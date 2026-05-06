# Software Wiki — Vault Schema

## 概述

软件开发知识库。当前主要聚焦 Linux 内核存储 I/O 学习路径（BSP 工程师深化方向）。

## Linux 存储 I/O 学习进度

进度文件：`wiki/progress/README.md`

**每次新 session 开始时，第一件事是读取 `wiki/progress/README.md` 恢复进度。**

## 目录

- `raw/` — 原始文档（Markdown、代码片段、文档）
- `wiki/` — LLM 生成内容

## wiki 页面分类

| 分类 | 说明 |
|------|------|
| `progress/` | 学习进度追踪（每次新 session 优先读） |
| `notes/` | 学习笔记 |
| `sources/` | 文档摘要 |
| `entities/` | 模块、类、函数、工具 |
| `concepts/` | 设计模式、架构范式、语言特性 |
| `synthesis/` | 跨文档对比、综合分析 |
| `questions/` | Q&A 成果 |

## 命名

- 学习笔记：`!<topic>.md`
- 原始资料摘要：`$<title>.md`
- 实体：`@<name>.md`
- 概念：`#<concept>.md`
- 综合：`!<topic>.md`
- Q&A：`?<question>.md`

## 工作流

### 学习流程

1. **新 session** → 读取 `wiki/progress/README.md` 恢复进度
2. 按当前阶段继续学习
3. 用户说"记录" → 更新进度文件 + git commit
4. 用户说"新话题" → 开启新阶段，更新 README

### Ingest

1. 读 `raw/` 中的新文档
2. 写 `$<title>.md` 来源摘要
3. 更新 `wiki/index.md`
4. 新建/更新相关 `entities/` 或 `concepts/` 页面
5. 追加 `wiki/log.md`

### Lint

每周末检查：矛盾、过时、orphan 页面、缺失交叉引用。

## 标签体系（示例）

```yaml
tags: [language, framework, architecture, pattern, api, tool, devops, linux, storage]
```
