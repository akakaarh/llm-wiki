"""Kernel Code Index MCP Server.

Exposes Linux kernel symbol index as MCP tools for Claude Code.
"""

import sqlite3
from pathlib import Path
from mcp.server.fastmcp import FastMCP

_DIR = Path(__file__).parent
_DB_PATH = _DIR / "kernel_index.db"
_CTAGS_BIN = _DIR.parent / "ctags_bin" / "ctags.exe"
_KERNEL_SRC = _DIR.parent.parent / "kernel-src"

mcp = FastMCP(
    "kernel-index",
    instructions=(
        "Linux kernel C source code symbol index. "
        "Use these tools to look up C functions, structs, macros, enums, and variables "
        "from kernel source files — NOT for searching documentation or wiki notes. "
        "These tools return exact symbol locations (file path + line number), "
        "type signatures, and return types from kernel source code."
    ),
)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def find_symbol(name: str, exact: bool = False) -> str:
    """Find kernel C source code symbols by name. Searches the ctags index, NOT documentation.

    Args:
        name: Symbol name to search for (substring match by default).
        exact: If True, require exact name match.

    Returns:
        Matching symbols with their kind, location, type info.
    """
    conn = get_conn()
    if exact:
        rows = conn.execute(
            """SELECT s.name, s.kind, s.line, s.typeref, s.signature, s.is_static,
                      f.path
               FROM symbols s JOIN files f ON s.file_id = f.id
               WHERE s.name = ?
               ORDER BY s.kind, f.path""",
            (name,),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT s.name, s.kind, s.line, s.typeref, s.signature, s.is_static,
                      f.path
               FROM symbols s JOIN files f ON s.file_id = f.id
               WHERE s.name LIKE ?
               ORDER BY s.name, s.kind, f.path
               LIMIT 50""",
            (f"%{name}%",),
        ).fetchall()
    conn.close()

    if not rows:
        return f"No symbols found matching '{name}'"

    lines = []
    for r in rows:
        parts = [f"{r['name']} ({r['kind']})"]
        if r["typeref"]:
            parts.append(f"type={r['typeref']}")
        if r["signature"]:
            parts.append(f"sig={r['signature']}")
        parts.append(f"at {r['path']}:{r['line']}")
        if r["is_static"]:
            parts.append("[static]")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


@mcp.tool()
def list_functions(file: str) -> str:
    """List all C functions defined in a kernel source file. Shows return type, parameters, and line number.

    Args:
        file: File path or path fragment (e.g. "gpiolib.c", "drivers/gpio/gpio-").

    Returns:
        List of functions with return type, signature, and line number.
    """
    conn = get_conn()
    rows = conn.execute(
        """SELECT s.name, s.line, s.typeref, s.signature, s.is_static
           FROM symbols s JOIN files f ON s.file_id = f.id
           WHERE f.path LIKE ? AND s.kind = 'function'
           ORDER BY s.line""",
        (f"%{file}%",),
    ).fetchall()
    conn.close()

    if not rows:
        return f"No functions found in files matching '{file}'"

    lines = []
    for r in rows:
        ret = r["typeref"] or "void"
        static = "static " if r["is_static"] else ""
        sig = r["signature"] or "()"
        lines.append(f"L{r['line']:>5d}  {static}{ret} {r['name']}{sig}")
    return "\n".join(lines)


@mcp.tool()
def search_by_kind(kind: str, subsystem: str = "") -> str:
    """List kernel C symbols by type (function, struct, macro, enum, etc.). Searches the ctags index.

    Args:
        kind: Symbol kind - one of: function, macro, struct, enum, variable, member, typedef, union, enumerator.
        subsystem: Optional subsystem filter (e.g. "drivers/gpio").

    Returns:
        List of matching symbols with file and line number.
    """
    conn = get_conn()
    if subsystem:
        rows = conn.execute(
            """SELECT s.name, s.line, f.path
               FROM symbols s JOIN files f ON s.file_id = f.id
               WHERE s.kind = ? AND f.subsystem = ?
               ORDER BY s.name
               LIMIT 100""",
            (kind, subsystem),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT s.name, s.line, f.path
               FROM symbols s JOIN files f ON s.file_id = f.id
               WHERE s.kind = ?
               ORDER BY s.name
               LIMIT 100""",
            (kind,),
        ).fetchall()
    conn.close()

    if not rows:
        return f"No '{kind}' symbols found"

    lines = [f"{r['name']:40s} {r['path']}:{r['line']}" for r in rows]
    if len(lines) == 100:
        lines.append("... (truncated at 100 results)")
    return "\n".join(lines)


@mcp.tool()
def file_symbols(file: str) -> str:
    """Get all C symbols defined in a kernel source file, grouped by kind.

    Args:
        file: File path or path fragment.

    Returns:
        Symbol summary and detailed listing for the file.
    """
    conn = get_conn()

    # Summary
    summary = conn.execute(
        """SELECT s.kind, COUNT(*) as cnt
           FROM symbols s JOIN files f ON s.file_id = f.id
           WHERE f.path LIKE ?
           GROUP BY s.kind ORDER BY cnt DESC""",
        (f"%{file}%",),
    ).fetchall()

    if not summary:
        return f"No symbols found in files matching '{file}'"

    # Detail
    symbols = conn.execute(
        """SELECT s.name, s.kind, s.line, s.typeref, s.signature
           FROM symbols s JOIN files f ON s.file_id = f.id
           WHERE f.path LIKE ?
           ORDER BY s.kind, s.line""",
        (f"%{file}%",),
    ).fetchall()
    conn.close()

    lines = ["=== Summary ==="]
    for r in summary:
        lines.append(f"  {r['kind']:15s} {r['cnt']:>5d}")
    lines.append(f"\n=== Symbols ({len(symbols)} total) ===")
    current_kind = None
    for r in symbols:
        if r["kind"] != current_kind:
            current_kind = r["kind"]
            lines.append(f"\n--- {current_kind} ---")
        detail = f"L{r['line']:>5d}  {r['name']}"
        if r["typeref"]:
            detail += f" : {r['typeref']}"
        if r["signature"]:
            detail += r["signature"]
        lines.append(detail)
    return "\n".join(lines)


@mcp.tool()
def index_stats() -> str:
    """Get statistics about the current kernel index database.

    Returns:
        Total counts of files and symbols, breakdown by kind and subsystem.
    """
    conn = get_conn()

    total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    total_symbols = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]

    lines = [
        f"Kernel Code Index Statistics",
        f"  Files:   {total_files}",
        f"  Symbols: {total_symbols}",
        "",
        "By kind:",
    ]
    for r in conn.execute(
        "SELECT kind, COUNT(*) as cnt FROM symbols GROUP BY kind ORDER BY cnt DESC"
    ):
        lines.append(f"  {r['kind']:15s} {r['cnt']:>6d}")

    lines.append("\nBy subsystem:")
    for r in conn.execute(
        "SELECT subsystem, COUNT(DISTINCT f.id) as files, COUNT(s.id) as symbols "
        "FROM files f LEFT JOIN symbols s ON s.file_id = f.id "
        "GROUP BY subsystem ORDER BY symbols DESC"
    ):
        lines.append(f"  {r['subsystem']:25s} {r['files']:>4d} files  {r['symbols']:>6d} symbols")

    conn.close()
    return "\n".join(lines)


@mcp.tool()
def reindex_subsystem(subsystem: str) -> str:
    """Re-index a kernel subsystem's C source code via ctags. Use to add new subsystems.

    Args:
        subsystem: Subsystem path relative to kernel root (e.g. "drivers/spi", "mm", "fs/ext4").

    Returns:
        Summary of indexed symbols.
    """
    import subprocess, json, sys

    kernel_src = _KERNEL_SRC
    subsystem_dir = kernel_src / subsystem
    if not subsystem_dir.exists():
        return f"Error: {subsystem_dir} does not exist. You may need to update sparse-checkout first."

    ctags_bin = _CTAGS_BIN
    cmd = [
        str(ctags_bin), "--output-format=json",
        "--fields=+nKsStpf", "--languages=c",
        "-R", "-f", "-", str(subsystem_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    tags = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                tags.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    conn = get_conn()
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Insert files
    file_paths = set()
    for tag in tags:
        p = tag.get("path", "")
        if p:
            file_paths.add(p)

    file_id_map = {}
    for fpath in sorted(file_paths):
        try:
            rel = Path(fpath).relative_to(kernel_src)
        except ValueError:
            rel = Path(fpath)
        rel_str = str(rel).replace("\\", "/")
        cur = conn.execute(
            "INSERT OR IGNORE INTO files (path, subsystem) VALUES (?, ?)",
            (rel_str, subsystem),
        )
        if cur.lastrowid:
            file_id_map[fpath] = cur.lastrowid
        else:
            row = conn.execute("SELECT id FROM files WHERE path = ?", (rel_str,)).fetchone()
            file_id_map[fpath] = row[0]

    # Insert symbols
    inserted = 0
    for tag in tags:
        name = tag.get("name", "")
        if not name:
            continue
        fpath = tag.get("path", "")
        file_id = file_id_map.get(fpath)
        if not file_id:
            continue
        try:
            conn.execute(
                """INSERT INTO symbols
                   (name, kind, file_id, line, pattern, typeref, signature, is_static)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    name,
                    tag.get("kind", "").lower(),
                    file_id,
                    tag.get("line", 0),
                    tag.get("pattern", ""),
                    tag.get("typeref", ""),
                    tag.get("signature", ""),
                    1 if tag.get("file", False) else 0,
                ),
            )
            inserted += 1
        except sqlite3.Error:
            continue

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    conn.close()

    return f"Indexed {inserted} symbols from {subsystem}. Total symbols in database: {total}"


@mcp.tool()
def call_graph(name: str, direction: str = "both", depth: int = 1) -> str:
    """Find callers and/or callees of a function in the kernel call graph.

    Args:
        name: Function name (exact match).
        direction: "callers" (who calls this), "callees" (what this calls), or "both".
        depth: How many levels to expand (default 1 = direct only). Use 2-3 to see
               deeper call chains without overwhelming detail. Nodes with more children
               are marked with [...] so you know where to dig deeper.

    Returns:
        Call graph tree with file locations and line numbers.
    """
    conn = get_conn()

    # Preload adjacency for efficiency
    if direction in ("callees", "both"):
        cal_rows = conn.execute("""
            SELECT caller.name, callee.name, f.path, cr.call_site_line
            FROM call_relations cr
            JOIN symbols caller ON cr.caller_id = caller.id
            JOIN symbols callee ON cr.callee_id = callee.id
            JOIN files f ON cr.call_site_file_id = f.id
        """).fetchall()
        callee_adj = {}  # caller -> [(callee, path, line), ...]
        for r in cal_rows:
            callee_adj.setdefault(r[0], []).append((r[1], r[2], r[3]))

    if direction in ("callers", "both"):
        call_rows = conn.execute("""
            SELECT caller.name, callee.name, f.path, cr.call_site_line
            FROM call_relations cr
            JOIN symbols caller ON cr.caller_id = caller.id
            JOIN symbols callee ON cr.callee_id = callee.id
            JOIN files f ON cr.call_site_file_id = f.id
        """).fetchall()
        caller_adj = {}  # callee -> [(caller, path, line), ...]
        for r in call_rows:
            caller_adj.setdefault(r[1], []).append((r[0], r[2], r[3]))

    conn.close()

    def format_tree(root, adj, label, current_depth, visited):
        """Recursively build a tree string."""
        lines = []
        entries = adj.get(root, [])
        if not entries:
            if current_depth == 1:
                lines.append(f"{label} of {root}: (none)")
            return lines

        # Deduplicate: group by name, keep first occurrence's path/line
        seen = {}
        for callee_name, path, line in entries:
            if callee_name not in seen:
                seen[callee_name] = (path, line)
        unique = sorted(seen.items())

        if current_depth == 1:
            has_more = any(name not in visited and adj.get(name) for name, _ in unique)
            suffix = " (use depth=2 to expand)" if has_more and depth == 1 else ""
            lines.append(f"{label} of {root} ({len(unique)} found){suffix}:")

        for child_name, (path, line) in unique:
            short_path = path.split("/")[-1] if "/" in path else path
            is_cycle = child_name in visited
            has_children = child_name in adj and adj[child_name]

            if current_depth >= depth:
                # At max depth: show node, mark if expandable
                if has_children and not is_cycle:
                    child_count = len(set(n for n, _, _ in adj.get(child_name, [])))
                    lines.append(f"{'  ' * current_depth}{child_name} at {short_path}:{line} [...{child_count} more]")
                else:
                    lines.append(f"{'  ' * current_depth}{child_name} at {short_path}:{line}")
            else:
                # Recurse
                if is_cycle:
                    lines.append(f"{'  ' * current_depth}{child_name} at {short_path}:{line} (cycle)")
                elif has_children:
                    lines.append(f"{'  ' * current_depth}{child_name} at {short_path}:{line}:")
                    visited.add(child_name)
                    sub = format_tree(child_name, adj, label, current_depth + 1, visited)
                    lines.extend(sub)
                    visited.discard(child_name)
                else:
                    lines.append(f"{'  ' * current_depth}{child_name} at {short_path}:{line} (leaf)")

        return lines

    parts = []

    if direction in ("callers", "both"):
        if name in caller_adj:
            parts.extend(format_tree(name, caller_adj, "Callers", 1, {name}))
        else:
            parts.append(f"No callers found for {name}")

    if direction in ("callees", "both"):
        if name in callee_adj:
            parts.extend(format_tree(name, callee_adj, "Callees", 1, {name}))
        else:
            parts.append(f"No callees found for {name}")

    return "\n".join(parts) if parts else f"Function '{name}' not found in call graph"


@mcp.tool()
def call_chain(source: str, target: str, max_depth: int = 5) -> str:
    """Find a call path between two functions using BFS on the call graph.

    Args:
        source: Starting function name.
        target: Target function name.
        max_depth: Maximum call depth to search (default 5).

    Returns:
        The call chain from source to target, or report that no path was found.
    """
    from collections import deque

    conn = get_conn()

    rows = conn.execute("""
        SELECT caller.name, callee.name
        FROM call_relations cr
        JOIN symbols caller ON cr.caller_id = caller.id
        JOIN symbols callee ON cr.callee_id = callee.id
    """).fetchall()
    conn.close()

    adj = {}
    for caller_name, callee_name in rows:
        adj.setdefault(caller_name, set()).add(callee_name)

    queue = deque([(source, [source])])
    visited = {source}

    while queue:
        current, path = queue.popleft()
        if len(path) > max_depth + 1:
            continue
        for neighbor in adj.get(current, []):
            if neighbor == target:
                return " -> ".join(path + [neighbor])
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return f"No call path found from {source} to {target} within depth {max_depth}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
