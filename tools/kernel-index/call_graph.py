"""Kernel Code Index - Call graph builder via source-level function body analysis."""

import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

_DIR = Path(__file__).parent
DB_PATH = _DIR / "kernel_index.db"
KERNEL_SRC = _DIR.parent.parent.parent / "projects" / "kernel-code-index" / "kernel-src"

# Regex: identifier followed by '(' — catches function calls
CALL_RE = re.compile(r"\b([a-z_][a-z_0-9]*)\s*\(")


def load_function_index(conn):
    """Build lookup structures for known function names.

    Returns:
        name_to_ids: {name: [symbol_id, ...]}
        name_set: set of unique function names
    """
    rows = conn.execute(
        "SELECT id, name FROM symbols WHERE kind = 'function'"
    ).fetchall()
    name_to_ids = defaultdict(list)
    for sid, name in rows:
        name_to_ids[name].append(sid)
    return dict(name_to_ids), set(name_to_ids.keys())


def get_functions_by_file(conn):
    """Group functions by file_id, sorted by line number.

    Returns:
        {file_id: [(symbol_id, name, line, rel_path), ...]}
    """
    rows = conn.execute("""
        SELECT s.id, s.name, s.line, f.id, f.path
        FROM symbols s
        JOIN files f ON s.file_id = f.id
        WHERE s.kind = 'function'
        ORDER BY f.id, s.line
    """).fetchall()

    by_file = defaultdict(list)
    for sid, name, line, fid, fpath in rows:
        by_file[fid].append((sid, name, line, fpath))
    return dict(by_file)


def strip_comments_and_strings(text):
    """Remove C comments and string/char literals, preserving line structure."""
    result = []
    i = 0
    n = len(text)
    in_line_comment = False
    in_block_comment = False
    in_string = False
    in_char = False

    while i < n:
        ch = text[i]

        if not in_block_comment and not in_string and not in_char:
            if ch == '/' and i + 1 < n and text[i + 1] == '/':
                in_line_comment = True
                result.append(' ')
                result.append(' ')
                i += 2
                continue

        if not in_line_comment and not in_string and not in_char:
            if ch == '/' and i + 1 < n and text[i + 1] == '*':
                in_block_comment = True
                result.append(' ')
                result.append(' ')
                i += 2
                continue

        if in_block_comment:
            if ch == '*' and i + 1 < n and text[i + 1] == '/':
                in_block_comment = False
                result.append(' ')
                result.append(' ')
                i += 2
                continue
            result.append('\n' if ch == '\n' else ' ')
            i += 1
            continue

        if in_line_comment:
            if ch == '\n':
                in_line_comment = False
                result.append('\n')
            else:
                result.append(' ')
            i += 1
            continue

        if not in_char:
            if ch == '"' and not in_string:
                in_string = True
                result.append(' ')
                i += 1
                continue
            if in_string:
                if ch == '\\':
                    result.append('  ')
                    i += 2
                    continue
                if ch == '"':
                    in_string = False
                    result.append(' ')
                    i += 1
                    continue
                result.append('\n' if ch == '\n' else ' ')
                i += 1
                continue

        if not in_string:
            if ch == "'" and not in_char:
                in_char = True
                result.append(' ')
                i += 1
                continue
            if in_char:
                if ch == '\\':
                    result.append('  ')
                    i += 2
                    continue
                if ch == "'":
                    in_char = False
                    result.append(' ')
                    i += 1
                    continue
                result.append('\n' if ch == '\n' else ' ')
                i += 1
                continue

        result.append(ch)
        i += 1

    return "".join(result)


def extract_function_body(lines, start_line_idx):
    """Extract function body text and per-line absolute line numbers."""
    brace_start = None
    for offset in range(15):
        idx = start_line_idx + offset
        if idx >= len(lines):
            break
        line = lines[idx]
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue
        pos = line.find('{')
        if pos != -1:
            brace_start = (idx, pos)
            break

    if brace_start is None:
        return None, None

    depth = 0
    body_chars = []
    body_line_map = []
    in_block_comment = False
    in_string = False
    in_char = False

    row, col = brace_start
    started = False

    while row < len(lines):
        line = lines[row]
        col_start = col if not started else 0
        i = col_start

        while i < len(line):
            ch = line[i]

            if not in_block_comment and not in_string and not in_char:
                if ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    i = len(line)
                    continue

            if not in_string and not in_char:
                if ch == '/' and i + 1 < len(line) and line[i + 1] == '*':
                    in_block_comment = True
                    i += 2
                    continue

            if in_block_comment:
                if ch == '*' and i + 1 < len(line) and line[i + 1] == '/':
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue

            if not in_char and ch == '"' and not in_string:
                in_string = True
                i += 1
                continue
            if in_string:
                if ch == '\\':
                    i += 2
                    continue
                if ch == '"':
                    in_string = False
                i += 1
                continue

            if not in_string and ch == "'" and not in_char:
                in_char = True
                i += 1
                continue
            if in_char:
                if ch == '\\':
                    i += 2
                    continue
                if ch == "'":
                    in_char = False
                i += 1
                continue

            if ch == '{':
                depth += 1
                if not started:
                    started = True
            elif ch == '}':
                depth -= 1
                if started and depth == 0:
                    body_chars.append(ch)
                    body_line_map.append(row + 1)
                    return "".join(body_chars), body_line_map

            if started:
                body_chars.append(ch)
                body_line_map.append(row + 1)

            i += 1

        if started:
            body_chars.append('\n')
            body_line_map.append(row + 1)

        row += 1
        col = 0

    return None, None


def find_calls_in_body(body_text, line_numbers, name_set):
    """Find function calls in a cleaned body text."""
    cleaned = strip_comments_and_strings(body_text)

    calls = []
    seen = set()

    for m in CALL_RE.finditer(cleaned):
        callee = m.group(1)
        if callee not in name_set:
            continue
        pos = m.start()
        if pos < len(line_numbers):
            line_no = line_numbers[pos]
        else:
            line_no = 0
        key = (callee, line_no)
        if key not in seen:
            seen.add(key)
            calls.append((callee, line_no))

    return calls


def build_call_graph(conn, verbose=False):
    """Main entry: build call_relations from source analysis."""
    name_to_ids, name_set = load_function_index(conn)
    if verbose:
        print(f"[*] Loaded {len(name_to_ids)} functions ({len(name_set)} unique names)")

    functions_by_file = get_functions_by_file(conn)
    if verbose:
        print(f"[*] Functions spread across {len(functions_by_file)} files")

    file_paths = {}
    for fid in functions_by_file:
        rel_path = functions_by_file[fid][0][3]
        file_paths[fid] = rel_path

    total_relations = 0
    files_processed = 0

    for fid, func_list in sorted(functions_by_file.items()):
        rel_path = file_paths[fid]
        abs_path = KERNEL_SRC / rel_path

        if not abs_path.exists():
            if verbose:
                print(f"  [!] File not found: {abs_path}")
            continue

        try:
            source = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            if verbose:
                print(f"  [!] Cannot read {abs_path}: {e}")
            continue

        source_lines = source.splitlines()
        file_relations = []

        for caller_id, caller_name, func_line, _ in func_list:
            body_text, line_map = extract_function_body(source_lines, func_line - 1)
            if body_text is None:
                continue

            calls = find_calls_in_body(body_text, line_map, name_set)
            for callee_name, call_line in calls:
                callee_ids = name_to_ids.get(callee_name, [])
                for callee_id in callee_ids:
                    file_relations.append((caller_id, callee_id, fid, call_line))

        if file_relations:
            conn.executemany(
                "INSERT INTO call_relations (caller_id, callee_id, call_site_file_id, call_site_line) "
                "VALUES (?, ?, ?, ?)",
                file_relations,
            )
            total_relations += len(file_relations)

        files_processed += 1
        if verbose:
            short_name = Path(rel_path).name
            print(f"  [{files_processed}/{len(functions_by_file)}] {short_name}: {len(file_relations)} relations")

    conn.commit()
    return total_relations, files_processed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Kernel Call Graph Builder")
    parser.add_argument("--db", default=str(DB_PATH), help="SQLite database path")
    parser.add_argument("--clean", action="store_true", default=True,
                        help="Clear existing call_relations before building (default: True)")
    parser.add_argument("--no-clean", dest="clean", action="store_false",
                        help="Keep existing call_relations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Error: database not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    if args.clean:
        deleted = conn.execute("DELETE FROM call_relations").rowcount
        conn.commit()
        if deleted > 0:
            print(f"[*] Cleared {deleted} existing call relations")

    print("[*] Building call graph...")
    total_relations, files_processed = build_call_graph(conn, verbose=args.verbose)

    print(f"\n[===] Summary ===")
    print(f"  Files processed:   {files_processed}")

    stats = conn.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT caller_id) as callers,
            COUNT(DISTINCT callee_id) as callees
        FROM call_relations
    """).fetchone()
    print(f"  Call relations:    {stats[0]}")
    print(f"  Unique callers:    {stats[1]}")
    print(f"  Unique callees:    {stats[2]}")

    print(f"\n  Most called functions (top 10):")
    for row in conn.execute("""
        SELECT s.name, COUNT(DISTINCT cr.caller_id) as callers
        FROM call_relations cr
        JOIN symbols s ON cr.callee_id = s.id
        GROUP BY s.name
        ORDER BY callers DESC
        LIMIT 10
    """):
        print(f"    {row[0]:40s} {row[1]:>4d} callers")

    print(f"\n  Most calling functions (top 10):")
    for row in conn.execute("""
        SELECT s.name, COUNT(DISTINCT cr.callee_id) as callees
        FROM call_relations cr
        JOIN symbols s ON cr.caller_id = s.id
        GROUP BY cr.caller_id
        ORDER BY callees DESC
        LIMIT 10
    """):
        print(f"    {row[0]:40s} {row[1]:>4d} callees")

    conn.close()
    print(f"\n[+] Done.")


if __name__ == "__main__":
    main()
