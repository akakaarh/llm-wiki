# Embedded Wiki — Vault Schema

## 概述

嵌入式开发知识库。原始文档包括芯片手册、RTOS 文档、通信协议规范、硬件调试笔记等。

## 学习进度

进度文件：`wiki/progress/README.md`

**每次新 session 开始时，第一件事是读取 `wiki/progress/README.md` 恢复进度。**

## 双轨制学习

本vault与 `software/` vault 采用双轨制，在同一个对话框内通过关键词切换：

| 关键词 | 操作 |
|--------|------|
| "继续嵌入式" | 读 `embedded/wiki/progress/README.md`，接着上次继续 |
| "切到软件" | 读 `software/wiki/progress/README.md`，接着上次继续 |
| "记录" | 更新当前vault进度文件 + git commit |
| "新话题" | 在当前vault里开新阶段/新专题 |
| "新专题 XXX" | 在当前vault里创建新的独立学习专题 |

**新session启动：** 读两个vault的进度文件，询问用户选择继续哪条线。

## 当前学习路线（8阶段）

| 阶段 | 名称 | 状态 |
|------|------|------|
| 1 | 嵌入式基础 | ✅ 已完成 |
| 2 | ARM架构基础 + RISC-V概览 | 未开始 |
| 3 | Cortex-M架构深入 + JTAG/SWD | 未开始 |
| 4 | Cortex-M外设与驱动 | 未开始 |
| 5 | RTOS + 核间通信 | 未开始 |
| 6 | Linux设备驱动开发 | 未开始 |
| 7 | Cortex-A架构与Linux BSP | 未开始 |
| 8 | 构建系统与安全 | 未开始 |

开发板：STM32MP157（阶段2-8使用）

## 目录

- `raw/` — 原始文档（PDF、Markdown、网页剪藏）
- `wiki/` — LLM 生成内容

## wiki 页面分类

| 分类 | 说明 |
|------|------|
| `progress/` | 学习进度追踪（每次新 session 优先读） |
| `notes/` | 学习笔记 |
| `entities/` | 硬件型号、驱动模块、调试工具 |
| `concepts/` | DMA、中断、状态机、总线协议 |
| `sources/` | 文档摘要 |
| `synthesis/` | 跨文档对比、综合分析 |
| `questions/` | Q&A 成果 |

## 命名

- 实体：`@<name>.md`
- 概念：`#<concept>.md`
- 来源：`$<title>.md`
- 综合：`!<topic>.md`
- Q&A：`?<question>.md`

## 自动产出规则

每次与用户交互涉及嵌入式知识时，**自动沉淀**，不需要用户主动要求：

| 触发场景 | 产出 | 路径 |
|----------|------|------|
| 解决了 bug / 调试问题 | Q&A 条目（现象/原因/修复三行） | `questions/?<简短描述>.md` |
| 讲解了新概念 | concepts 条目 | `concepts/#<概念名>.md` |
| 对比了两个东西 | synthesis 条目 | `synthesis/!<主题>.md` |
| 学习进度推进 | 更新进度文件 | `progress/README.md` |
| 用到了新的芯片/外设/工具 | entities 条目 | `entities/@<名称>.md` |

**Q&A 格式极简模板：**
```yaml
---
type: question
tags: [debug, driver, i2c]
created: 2026-05-30
---
# <问题简述>

**现象：** ...
**原因：** ...
**修复：** ...
```

**原则：宁可写三行，也不要不写。**

## 工作流

### Ingest

**原则：来源摘要（$）必须覆盖文档的所有主要章节，重要细节不遗漏。具体章节的具体内容不得以"略"或"见原文"方式跳过。**

1. 读 `raw/` 中的新文档
2. 写 `$<title>.md` 来源摘要，规则如下：
   - 按文档原有章节结构逐一总结，**不能跳章节**
   - 每个章节需写出：这一节讲了什么、有哪些关键定义/寄存器/特性
   - 关键细节（如具体寄存器名称、位域定义、异常号、地址映射表）必须包含
   - "略"或"详见原文"是不可接受的摘要写法
   - 重要的表格、列表内容应尽量保留
3. 更新 `wiki/index.md`
4. 新建/更新相关 `entities/` 或 `concepts/` 页面，规则：
   - 通用原理/概念 → `concepts/#<concept>.md`
   - 具体型号/工具/外设 → `entities/@<entity>.md`
   - 跨文档对比/综合分析 → `synthesis/!<topic>.md`
5. **交叉引用**：在页面正文中提到其他 wiki 页面时，使用 `[[页面名]]` 或 `[[页面名|显示文字]]` 添加 wikilink
6. 追加 `wiki/log.md`

### Query

1. 读 `index.md` 找相关页
2. 读取相关页面并合成答案
3. 好答案存为 `?` 页或对应分类页

### Lint

运行 `python scripts/lint.py <vault_path>` 检查健康状态，加 `--fix` 自动修复机械问题。

检查项：断链 wikilinks、孤立页面、缺失 frontmatter、过期 index。

### 学习流程

1. **新 session** → 读取 `wiki/progress/README.md` 恢复进度
2. 按当前阶段继续学习
3. 用户说"记录" → 更新进度文件 + git commit
4. 用户说"新话题" → 开启新阶段，更新 README

## 页面职责边界

| 类型 | 内容 | 例子 |
|------|------|------|
| `$` 来源摘要 | 文档的完整章节结构总结，关键细节不丢 | `$ARMv7M_RefManual.md` 含 D5.3 每节内容 |
| `#` 概念 | 从一个或多个来源提炼的通用原理，与具体文档解耦 | `#NVIC.md` 从 ARMv7-M/A 多份文档提炼中断通用模型 |
| `!` 综合 | 跨型号/架构/文档的对比分析 | `!CortexA_vs_CortexM.md` 对比两种系列 |

**原则：`$` 忠于原文，`#` 提炼原理，`!` 做横向对比。不允许用 `$` 代替 `#`，也不允许用 `#` 跳过 `$` 的细节。**

## 标签体系（示例）

```yaml
tags: [chip, rtos, protocol, driver, debug, concept, tool]
```
