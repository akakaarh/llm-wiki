# LLM Wiki

个人知识库，由 Claude Code 辅助维护。基于 Obsidian，所有页面为纯 Markdown。

## 结构

- `embedded/` — 嵌入式知识库（ARM 架构、Cortex-M/A 系列）
- `software/` — 软件知识库（Linux 内核存储 I/O 学习路径）
- `scripts/` — Wiki 工具脚本

## 工作方式

- 每个 Vault 有独立的 `CLAUDE.md` 定义 schema 和工作流
- 页面通过 `[[wikilinks]]` 互相引用，Obsidian 图谱可可视化
- 学习进度追踪在各 vault 的 `wiki/progress/README.md`
- LLM 负责页面创建、维护、交叉引用
- Raw sources 只读，不可修改

## 页面命名约定

| 前缀 | 类型 | 示例 |
|------|------|------|
| `$` | 来源摘要 | `$ARMv7M_RefManual.md` |
| `#` | 概念 | `#NVIC.md` |
| `@` | 实体 | `@CortexM_Series.md` |
| `!` | 综合/笔记 | `!CortexA_vs_CortexM.md` |
| `?` | Q&A | `?<question>.md` |

## 工具

```bash
# Lint 检查（断链、孤立页面、缺失 frontmatter、过期 index）
python scripts/lint.py embedded
python scripts/lint.py software

# 自动修复机械问题
python scripts/lint.py embedded --fix

# 知识图谱生成
python scripts/graph.py embedded --format mermaid
python scripts/graph.py embedded --format json
```

## 当前进度

### 软件：Linux 存储 I/O

- **上次：** 阶段 5 完成（回顾与巩固）
- **下次：** 阶段 6-1 NVMe 队列机制

### 嵌入式

- 学习路线图已建立（6 阶段 24 课），阶段 1 未开始
