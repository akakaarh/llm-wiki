# LLM Wiki 知识库设计

## 概述

基于 Andrej Karpathy 的 LLM Wiki 模式，搭建一个通用、可扩展的个人知识库框架。核心思路：LLM 增量构建并维护一个持久化的 Wiki，作为用户与原始文档之间的中间层，实现知识的积累和复用，而非每次问答从头推导。

## 目录结构

```
E:\Wiki\
├── CLAUDE.md              # 父级 schema（多库协调层）

├── embedded/              # Vault 1（嵌入式知识库示例）
│   ├── CLAUDE.md          # Vault schema（LLM 的工作手册）
│   ├── .obsidian/          # Obsidian 配置
│   ├── metadata.yaml       # Vault 元信息
│   ├── raw/                # 原始文档（不可变源）
│   │   └── assets/         # 附件（截图、PDF 等）
│   └── wiki/               # LLM 生成内容
│       ├── index.md         # 内容索引
│       ├── log.md           # 操作日志
│       ├── entities/        # 实体页
│       ├── concepts/        # 概念页
│       ├── sources/          # 来源摘要
│       ├── synthesis/        # 综合分析
│       └── questions/        # Q&A 成果

└── software/              # Vault 2（软件知识库，空脚手架）
    ├── CLAUDE.md
    ├── .obsidian/
    ├── metadata.yaml
    ├── raw/
    │   └── assets/
    └── wiki/
        ├── index.md
        ├── log.md
        ├── entities/
        ├── concepts/
        ├── sources/
        ├── synthesis/
        └── questions/
```

## 层级职责

| 层级 | 角色 |
|------|------|
| Raw Sources | 原始文档库（网页剪藏、PDF、Markdown），不可修改，作为信任源 |
| Wiki | LLM 生成的 Markdown 文件，完全由 LLM 维护 |
| Schema | CLAUDE.md，规定 LLM 的工作流程和规范 |

## 页面分类与命名

### 分类

- **entities/** — 实体：具体的人事物（硬件型号、函数、工具）
- **concepts/** — 概念：原理、模式、方法论
- **sources/** — 来源摘要：每份原始文档的提炼
- **synthesis/** — 综合分析：跨文档总结、对比
- **questions/** — Q&A 成果：来自 Query 的好答案

### 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 实体 | `@<name>.md` | `@STM32F4.md`、`@FreeRTOS.md` |
| 概念 | `#<concept>.md` | `#DMA.md`、`#状态机.md` |
| 来源摘要 | `$<title>.md` | `$STM32RefManual_CH3.md` |
| 综合/对比 | `!<topic>.md` | `!RTOS对比.md` |
| Q&A | `?<question>.md` | `?中断与异常的区别.md` |

## 工作流程

### Ingest（摄入新文档）

1. 用户将文档放入 `raw/`
2. LLM 读取文档，提炼关键信息
3. 写 `$<title>.md` 来源摘要页
4. 更新 `index.md`，新增条目
5. 更新相关 entities/concepts（新建或修订）
6. 追加 `log.md` 记录

### Query（提问）

1. LLM 读取 `index.md` 定位相关页面
2. 读取相关 wiki 页面
3. 合成答案并注明来源
4. 如答案有保存价值，写入 `questions/` 或相应分类

### Lint（健康检查）

定期（每周/每月）检查：
- 矛盾页面
- 过时被新来源替代的内容
- 无 inbound 链接的 orphan 页面
- 有提及但未建页的概念
- 缺失交叉引用

## 工具链

- **Obsidian** — Wiki 浏览与编辑
- **Obsidian Web Clipper** — 网页转 Markdown
- **qmd** — 本地搜索（BM25+向量混合搜索，MCP 工具可用）
- **Marp** — 生成幻灯片
- **Dataview** — YAML frontmatter 动态查询
- **Git** — 版本历史与多设备同步

## 后续扩展

当确定具体知识库类型（嵌入式/纯软/其他）后，在对应 Vault 的 CLAUDE.md 中补充：
- 具体的分类标签体系
- 常用的 source 标注模板
- 特定领域的 Lint 检查规则
