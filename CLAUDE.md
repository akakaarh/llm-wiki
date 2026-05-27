# LLM Wiki — 父级协调层

这是多知识库的协调入口。

## Vaults

- `embedded/` — 嵌入式知识库 Vault（当前焦点：8阶段BSP学习路线）
- `software/` — 软件知识库 Vault（Linux内核机制，可独立扩展新专题）

## 双轨制学习

两个vault在同一对话框内通过关键词切换，进度文件各自独立：

| 关键词 | 操作 |
|--------|------|
| "继续嵌入式" | 读 `embedded/wiki/progress/README.md`，接着上次继续 |
| "切到软件" | 读 `software/wiki/progress/README.md`，接着上次继续 |
| "记录" | 更新当前vault进度文件 + git commit |
| "新话题" | 在当前vault里开新阶段/新专题 |
| "新专题 XXX" | 在当前vault里创建新的独立学习专题 |

**新session启动流程：**
1. 读 `embedded/wiki/progress/README.md`
2. 读 `software/wiki/progress/README.md`
3. 询问用户："今天继续嵌入式还是软件？"

**规则：切换前必须先"记录"，否则新内容会丢失。**

## 当前工作 Vault

无偏好。用户在对话中指定。

## 开发板

STM32MP157（Cortex-A7 + Cortex-M4 双核异构），用于嵌入式vault阶段2-8的实操教学。

## 通用原则

1. Wiki 是知识的持久化积累，不是每次问答从头推导
2. Raw sources 不可修改
3. LLM 负责所有 wiki 页面的创建、维护、交叉引用
4. 好的 Query 答案应存回 wiki
5. 定期 Lint 保持 wiki 健康

## 环境上下文

本项目运行在 **Windows 10 + Git Bash (MINGW64)** 环境下。排查问题时，务必先用 `uname -a` 和 `pwd` 确认当前环境是 WSL、Git Bash 还是 MINGW64，再建议命令。永远不要假设环境。

## 本地知识库

**回答任何问题前，必须先用 `qmd query` 检索本地 Wiki。** 本地知识库是专门为用户整理的权威来源，优先级高于训练数据和网页搜索。

检索流程：
1. `qmd query "<问题关键词>" -c embedded -c software` — 语义搜索本地 wiki
2. 如果命中相关页面，基于 wiki 内容回答
3. 如果未命中或信息不足，再用网页搜索或 Context7 补充
4. 新获取的有价值知识应沉淀回 wiki

禁止跳过本地检索直接从记忆/训练数据回答。

## 教学模式

当被要求教学或制定学习计划时，使用 **交互式问答风格**——一次教一个概念，问理解问题，等确认后再继续。永远不要一次倒出整页/整篇内容。永远不要在确认当前内容被理解之前跳到下一个主题。如果学习阶段有子部分（如 8-1 ftrace、8-2 bpftrace），必须完全完成每个子部分再进入下一个。

## 排查方法

排查工具/API 错误时，先调查实际配置和端点要求，再建议用户联系客服或检查余额。配置文件、API 格式要求和 URL 模式应作为首要检查项。

详见各 Vault 的 CLAUDE.md
