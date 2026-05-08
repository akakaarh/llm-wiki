#!/usr/bin/env python3
"""
Wiki Graph — 扫描 [[wikilinks]]，生成知识图谱。

用法:
    python scripts/graph.py <vault_path> [--format mermaid|json|both] [--output <file>]

输出:
    - Mermaid: 可直接贴到 Markdown 渲染
    - JSON: 节点+边的图谱数据，供 Obsidian 或其他工具使用
"""

import argparse
import json
import re
import sys
from pathlib import Path


def find_md_files(wiki_dir: Path) -> list[Path]:
    """找到 wiki 目录下所有 .md 文件。"""
    results = []
    for p in sorted(wiki_dir.rglob("*.md")):
        rel = p.relative_to(wiki_dir)
        parts = rel.parts
        if parts[0] in ("progress",):
            continue
        if p.name in ("index.md", "log.md"):
            continue
        results.append(p)
    return results


def get_page_title(filepath: Path) -> str:
    """从 .md 文件中提取标题。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return filepath.stem
    for line in content.splitlines():
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            title = m.group(1).strip()
            title = re.sub(r"^[#$@!?&]+", "", title).strip()
            return title
    return filepath.stem


def get_page_type(filepath: Path) -> str:
    """从 frontmatter 提取 type。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return "unknown"
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            fm = content[3:end]
            m = re.search(r"^type:\s*(\w+)", fm, re.MULTILINE)
            if m:
                return m.group(1)
    # 从文件名前缀推断
    stem = filepath.stem
    if stem.startswith("$"):
        return "source"
    if stem.startswith("#"):
        return "concept"
    if stem.startswith("@"):
        return "entity"
    if stem.startswith("!"):
        return "synthesis"
    if stem.startswith("?"):
        return "question"
    return "note"


def extract_wikilinks(content: str) -> list[str]:
    """提取 [[wikilinks]] 目标。"""
    links = []
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content):
        links.append(m.group(1).strip())
    return links


def build_graph(vault_path: Path) -> dict:
    """构建图谱数据。"""
    wiki_dir = vault_path / "wiki"
    files = find_md_files(wiki_dir)

    # 构建 name → file 映射
    name_map: dict[str, Path] = {}
    for f in files:
        title = get_page_title(f)
        name_map[title] = f
        stem = re.sub(r"^[#$@!?&]+", "", f.stem).strip()
        if stem and stem not in name_map:
            name_map[stem] = f

    # 节点
    nodes = []
    file_to_id: dict[Path, str] = {}
    for i, f in enumerate(files):
        title = get_page_title(f)
        page_type = get_page_type(f)
        node_id = f"n{i}"
        file_to_id[f] = node_id
        nodes.append({
            "id": node_id,
            "title": title,
            "type": page_type,
            "path": str(f.relative_to(vault_path)),
        })

    # 边
    edges = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        links = extract_wikilinks(content)
        source_id = file_to_id.get(f)
        if not source_id:
            continue
        for link in links:
            target_file = name_map.get(link)
            if target_file and target_file in file_to_id:
                target_id = file_to_id[target_file]
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "label": link,
                })

    return {"nodes": nodes, "edges": edges}


def to_mermaid(graph: dict) -> str:
    """转换为 Mermaid 图。"""
    lines = ["graph LR"]

    # 节点样式
    type_styles = {
        "source": ":::source",
        "concept": ":::concept",
        "entity": ":::entity",
        "synthesis": ":::synthesis",
        "question": ":::question",
        "note": ":::note",
    }

    for node in graph["nodes"]:
        nid = node["id"]
        title = node["title"].replace('"', "'")
        style = type_styles.get(node["type"], "")
        lines.append(f'    {nid}["{title}"]{style}')

    # 边
    for edge in graph["edges"]:
        lines.append(f"    {edge['source']} --> {edge['target']}")

    # 样式定义
    lines.extend([
        "",
        "    classDef source fill:#e1f5fe,stroke:#0288d1,color:#000",
        "    classDef concept fill:#f3e5f5,stroke:#7b1fa2,color:#000",
        "    classDef entity fill:#e8f5e9,stroke:#388e3c,color:#000",
        "    classDef synthesis fill:#fff3e0,stroke:#ef6c00,color:#000",
        "    classDef question fill:#fce4ec,stroke:#c62828,color:#000",
        "    classDef note fill:#f5f5f5,stroke:#616161,color:#000",
    ])

    return "\n".join(lines)


def to_json(graph: dict) -> str:
    """转换为 JSON。"""
    return json.dumps(graph, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Wiki Graph — 知识图谱生成")
    parser.add_argument("vault", help="vault 路径（如 embedded 或 software）")
    parser.add_argument("--format", choices=["mermaid", "json", "both"], default="both", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    vault_path = Path(args.vault).resolve()
    if not vault_path.is_dir():
        print(f"错误：{vault_path} 不是目录", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(vault_path)

    if not graph["nodes"]:
        print("没有找到任何页面。", file=sys.stderr)
        sys.exit(0)

    outputs = {}
    if args.format in ("mermaid", "both"):
        outputs["mermaid"] = to_mermaid(graph)
    if args.format in ("json", "both"):
        outputs["json"] = to_json(graph)

    if args.output:
        out_path = Path(args.output)
        if args.format == "both":
            # 写两个文件
            base = out_path.stem
            parent = out_path.parent
            (parent / f"{base}.mmd").write_text(outputs["mermaid"], encoding="utf-8")
            (parent / f"{base}.json").write_text(outputs["json"], encoding="utf-8")
            print(f"已写入 {parent / f'{base}.mmd'} 和 {parent / f'{base}.json'}")
        else:
            out_path.write_text(list(outputs.values())[0], encoding="utf-8")
            print(f"已写入 {out_path}")
    else:
        for fmt, content in outputs.items():
            print(f"\n{'='*50}")
            print(f"格式: {fmt}")
            print(f"{'='*50}")
            print(content)


if __name__ == "__main__":
    main()
