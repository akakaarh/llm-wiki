"""Kernel Code Index - Symbol indexer using universal-ctags + SQLite."""

import json
import subprocess
import sqlite3
import sys
from pathlib import Path

_DIR = Path(__file__).parent
CTAGS_BIN = _DIR.parent / "ctags_bin" / "ctags.exe"
DB_PATH = _DIR / "kernel_index.db"
SCHEMA_PATH = _DIR / "schema.sql"
KERNEL_SRC = _DIR.parent.parent / "kernel-src"

CTAGS_FIELDS = "--fields=+nKsStpf"


def init_db(db_path: Path) -> sqlite3.Connection:
    """Create database and schema."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    return conn


def run_ctags(source_dir: Path) -> list[dict]:
    """Run ctags on directory and return parsed JSON tags."""
    cmd = [
        str(CTAGS_BIN),
        "--output-format=json",
        CTAGS_FIELDS,
        "--languages=c",
        "-R",
        "-f", "-",
        str(source_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"ctags stderr: {result.stderr[:500]}", file=sys.stderr)

    tags = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                tags.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return tags


def classify_kind(ctags_kind: str) -> str:
    """Normalize ctags kind to our categories."""
    return ctags_kind.lower() if ctags_kind else "unknown"


def is_static(tag: dict) -> bool:
    """Check if symbol is file-scoped (static)."""
    return tag.get("file", False)


def index_subsystem(conn: sqlite3.Connection, subsystem_dir: Path, subsystem_name: str):
    """Index a kernel subsystem directory."""
    print(f"[*] Running ctags on {subsystem_dir}...")
    tags = run_ctags(subsystem_dir)
    print(f"[*] Found {len(tags)} tags")

    # Collect unique files
    file_paths = set()
    for tag in tags:
        p = tag.get("path", "")
        if p:
            file_paths.add(p)

    # Insert files
    file_id_map = {}
    for fpath in sorted(file_paths):
        # Make path relative to kernel source root
        try:
            rel = Path(fpath).relative_to(KERNEL_SRC)
        except ValueError:
            rel = Path(fpath)
        rel_str = str(rel).replace("\\", "/")

        cur = conn.execute(
            "INSERT OR IGNORE INTO files (path, subsystem) VALUES (?, ?)",
            (rel_str, subsystem_name),
        )
        if cur.lastrowid:
            file_id_map[fpath] = cur.lastrowid
        else:
            row = conn.execute("SELECT id FROM files WHERE path = ?", (rel_str,)).fetchone()
            file_id_map[fpath] = row[0]

    # Insert symbols
    inserted = 0
    skipped = 0
    for tag in tags:
        name = tag.get("name", "")
        if not name:
            skipped += 1
            continue

        fpath = tag.get("path", "")
        file_id = file_id_map.get(fpath)
        if not file_id:
            skipped += 1
            continue

        try:
            conn.execute(
                """INSERT INTO symbols
                   (name, kind, file_id, line, pattern, typeref, signature, is_static)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    name,
                    classify_kind(tag.get("kind", "")),
                    file_id,
                    tag.get("line", 0),
                    tag.get("pattern", ""),
                    tag.get("typeref", ""),
                    tag.get("signature", ""),
                    1 if is_static(tag) else 0,
                ),
            )
            inserted += 1
        except sqlite3.Error as e:
            print(f"  Skip {name}: {e}", file=sys.stderr)
            skipped += 1

    conn.commit()
    print(f"[+] Indexed {inserted} symbols, skipped {skipped}")
    return inserted


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Kernel Code Indexer")
    parser.add_argument("--subsystem", default="drivers/gpio",
                        help="Subsystem path relative to kernel root")
    parser.add_argument("--db", default=str(DB_PATH),
                        help="SQLite database path")
    args = parser.parse_args()

    subsystem_dir = KERNEL_SRC / args.subsystem
    if not subsystem_dir.exists():
        print(f"Error: {subsystem_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    subsystem_name = args.subsystem.replace("\\", "/")
    db_path = Path(args.db)

    print(f"[*] Initializing database at {db_path}")
    conn = init_db(db_path)

    count = index_subsystem(conn, subsystem_dir, subsystem_name)

    # Summary
    total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    total_symbols = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    print(f"\n[===] Summary ===")
    print(f"  Files indexed: {total_files}")
    print(f"  Symbols indexed: {total_symbols}")

    # Breakdown by kind
    print(f"\n  By kind:")
    for row in conn.execute(
        "SELECT kind, COUNT(*) FROM symbols GROUP BY kind ORDER BY COUNT(*) DESC"
    ):
        print(f"    {row[0]:15s} {row[1]:>6d}")

    conn.close()
    print(f"\n[+] Done. Database: {db_path}")


if __name__ == "__main__":
    main()
