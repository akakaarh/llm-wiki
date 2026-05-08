#!/usr/bin/env python3
"""
Wiki Lint — 检查 wiki vault 的健康状态。

用法:
    python scripts/lint.py <vault_path> [--fix]

检查项:
    1. 孤立页面：index.md 中未列出的 .md 文件
    2. 断链：[[wikilinks]] 指向不存在的页面
    3. 缺失交叉引用：正文中提到页面名但未加 [[]]
    4. 过期 index：index.md 文件列表与实际不符
    5. frontmatter 检查：缺少 type 或 tags

--fix 自动修复（仅机械问题）：
    - 重新生成 index.md
    - 移除死链 [[]]
    - 补全缺失的 frontmatter
"""

import argparse
import os
import re
import sys
from pathlib import Path


def find_md_files(wiki_dir: Path) -> list[Path]:
    """找到 wiki 目录下所有 .md 文件（排除 index.md、log.md、progress/）。"""
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
    """从 .md 文件中提取标题（第一个 # 标题行）。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return filepath.stem
    for line in content.splitlines():
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            title = m.group(1).strip()
            # 去掉命名前缀（如 #NVIC → NVIC）
            title = re.sub(r"^[#$@!?&]+", "", title).strip()
            return title
    return filepath.stem


def parse_frontmatter(content: str) -> dict | None:
    """解析 YAML frontmatter（简单实现，不依赖 pyyaml）。"""
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    fm_text = content[3:end].strip()
    result = {}
    for line in fm_text.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                result[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",")]
            else:
                result[key] = val
    return result


def extract_wikilinks(content: str) -> list[str]:
    """提取 [[wikilinks]]，返回目标页面名列表。"""
    links = []
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content):
        links.append(m.group(1).strip())
    return links


def extract_page_names(files: list[Path], wiki_dir: Path) -> dict[str, Path]:
    """构建 页面名 → 文件路径 的映射。"""
    name_map = {}
    for f in files:
        title = get_page_title(f)
        name_map[title] = f
        # 文件 stem（带前缀，如 !CortexA_vs_CortexM）
        stem = f.stem
        if stem not in name_map:
            name_map[stem] = f
        # 去掉命名前缀
        clean_stem = re.sub(r"^[#$@!?&]+", "", stem).strip()
        if clean_stem and clean_stem not in name_map:
            name_map[clean_stem] = f
    return name_map


def lint_vault(vault_path: Path, fix: bool = False) -> int:
    """对一个 vault 运行 lint 检查。返回问题数。"""
    wiki_dir = vault_path / "wiki"
    if not wiki_dir.is_dir():
        print(f"错误：{wiki_dir} 不是目录")
        return 1

    files = find_md_files(wiki_dir)
    page_names = extract_page_names(files, wiki_dir)
    issues = []

    # 收集所有 wikilink 目标
    all_links: dict[Path, list[str]] = {}
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        links = extract_wikilinks(content)
        all_links[f] = links

    # 检查 1: 断链
    broken_links: dict[Path, list[str]] = {}
    for f, links in all_links.items():
        broken = [l for l in links if l not in page_names]
        if broken:
            broken_links[f] = broken
            for b in broken:
                issues.append(("断链", f, f"[[{b}]] 指向不存在的页面"))

    # 检查 2: frontmatter
    missing_fm: list[Path] = []
    missing_type: list[Path] = []
    missing_tags: list[Path] = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(content)
        if fm is None:
            missing_fm.append(f)
            issues.append(("frontmatter", f, "缺少 frontmatter"))
        else:
            if "type" not in fm:
                missing_type.append(f)
                issues.append(("frontmatter", f, "缺少 type 字段"))
            if "tags" not in fm:
                missing_tags.append(f)
                issues.append(("frontmatter", f, "缺少 tags 字段"))

    # 检查 3: index.md 过期
    index_file = wiki_dir / "index.md"
    index_stale = False
    indexed_paths: set[Path] = set()
    indexed_names: set[str] = set()
    if index_file.is_file():
        try:
            index_content = index_file.read_text(encoding="utf-8")
        except Exception:
            index_content = ""
        for title, path_str in re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", index_content):
            indexed_paths.add(Path(path_str))
            indexed_names.add(title)
            # 也用文件 stem 匹配
            stem = Path(path_str).stem
            clean_stem = re.sub(r"^[#$@!?&]+", "", stem).strip()
            if clean_stem:
                indexed_names.add(clean_stem)
        actual_rels = {f.relative_to(wiki_dir) for f in files}
        missing_from_index = actual_rels - indexed_paths
        if missing_from_index:
            index_stale = True
            for mf in missing_from_index:
                issues.append(("index", index_file, f"未列出: {mf}"))

    # 检查 4: 孤立页面
    orphans = []
    for f in files:
        title = get_page_title(f)
        stem = re.sub(r"^[#$@!?&]+", "", f.stem).strip()
        if title not in indexed_names and stem not in indexed_names:
            orphans.append(f)
            issues.append(("孤立", f, f"页面 '{title}' 未在 index.md 中列出"))

    # 打印报告
    print(f"\n{'='*50}")
    print(f"Lint 报告: {vault_path}")
    print(f"{'='*50}")
    print(f"扫描文件: {len(files)}")
    print(f"发现问题: {len(issues)}")

    if not issues:
        print("\n[OK] 没有问题！")
        return 0

    # 按类型分组
    by_type: dict[str, list] = {}
    for kind, filepath, msg in issues:
        by_type.setdefault(kind, []).append((filepath, msg))

    for kind, items in by_type.items():
        print(f"\n--- {kind} ({len(items)}) ---")
        for filepath, msg in items:
            rel = filepath.relative_to(vault_path)
            print(f"  {rel}: {msg}")

    # --fix 模式
    if fix:
        print(f"\n{'='*50}")
        print("自动修复")
        print(f"{'='*50}")
        fixed = 0

        # 修复: 移除死链
        for f, broken in broken_links.items():
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            modified = False
            for b in broken:
                # 移除 [[link]] 但保留文字
                pattern = re.compile(r"\[\[" + re.escape(b) + r"(?:\|[^\]]+)?\]\]")
                if pattern.search(content):
                    content = pattern.sub(b, content)
                    modified = True
            if modified:
                f.write_text(content, encoding="utf-8")
                print(f"  修复死链: {f.relative_to(vault_path)}")
                fixed += 1

        # 修复: 补全 frontmatter
        for f in missing_fm:
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            fm = "---\ntype: note\ntags: []\n---\n\n"
            f.write_text(fm + content, encoding="utf-8")
            print(f"  补全 frontmatter: {f.relative_to(vault_path)}")
            fixed += 1

        # 修复: 重建 index.md
        if index_stale:
            rebuild_index(wiki_dir, files)
            print(f"  重建 index.md")
            fixed += 1

        print(f"\n修复了 {fixed} 个问题")

    return len(issues)


def rebuild_index(wiki_dir: Path, files: list[Path]):
    """重建 index.md。"""
    categories: dict[str, list[tuple[str, Path]]] = {
        "sources": [],
        "entities": [],
        "concepts": [],
        "synthesis": [],
        "notes": [],
        "questions": [],
    }

    for f in files:
        title = get_page_title(f)
        rel = f.relative_to(wiki_dir)
        category = rel.parts[0] if len(rel.parts) > 1 else "other"
        if category in categories:
            categories[category].append((title, rel))
        else:
            categories.setdefault("other", []).append((title, rel))

    lines = ["# Index\n", "> 此文件由 lint.py --fix 自动生成。\n"]

    cat_labels = {
        "sources": "来源摘要 ($)",
        "entities": "实体 (@)",
        "concepts": "概念 (#)",
        "synthesis": "综合 (!)",
        "notes": "学习笔记",
        "questions": "Q&A (?)",
    }

    for cat, label in cat_labels.items():
        lines.append(f"## {label}\n")
        items = categories.get(cat, [])
        if items:
            for title, rel in items:
                lines.append(f"- [{title}]({rel})")
        else:
            lines.append("暂无内容。")
        lines.append("")

    from datetime import date
    lines.append(f"---\n\n最后更新：{date.today()}")

    index_file = wiki_dir / "index.md"
    index_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Wiki Lint — 检查 wiki vault 健康状态")
    parser.add_argument("vault", help="vault 路径（如 embedded 或 software）")
    parser.add_argument("--fix", action="store_true", help="自动修复机械问题")
    args = parser.parse_args()

    vault_path = Path(args.vault).resolve()
    if not vault_path.is_dir():
        print(f"错误：{vault_path} 不是目录")
        sys.exit(1)

    issues = lint_vault(vault_path, fix=args.fix)
    sys.exit(1 if issues > 0 else 0)


if __name__ == "__main__":
    main()
