# 嵌入式 BSP 工作流系统 — 搭建与使用手册

> 三个独立项目通过 MCP 协议组合成 AI 驱动的嵌入式调试 + 学习闭环系统。
> 本手册帮助你基于源码搭建自己的系统，并告诉 AI Agent 如何使用它。

---

## 目录

- [第一部分：系统概览](#第一部分系统概览)
- [第二部分：环境准备](#第二部分环境准备)
- [第三部分：搭建 kernel-code-index](#第三部分搭建-kernel-code-index)
- [第四部分：搭建 gdb-ai-bridge](#第四部分搭建-gdb-ai-bridge)
- [第五部分：搭建 Wiki 知识库](#第五部分搭建-wiki-知识库)
- [第六部分：串联三个项目](#第六部分串联三个项目)
- [第七部分：AI Agent 使用手册](#第七部分ai-agent-使用手册)
- [第八部分：附录](#第八部分附录)

---

## 第一部分：系统概览

### 架构

```
┌───────────────────────────────────────────────────────────┐
│                   Claude Code (AI 层)                      │
│            统一入口，通过 MCP 协议连接三个子系统             │
└─────────┬─────────────────┬─────────────────┬─────────────┘
          │                 │                 │
    MCP: 9 tools      MCP: 5 tools     qmd 语义搜索
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ kernel-code-    │ │  gdb-ai-bridge  │ │     Wiki        │
│ index           │ │                 │ │                 │
│ 内核代码索引     │ │ GDB-AI 桥接     │ │ 知识库           │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 三个项目的职责

| 项目 | 职责 | 核心技术 | 状态 |
|------|------|----------|------|
| **kernel-code-index** | 内核代码符号索引，让 AI 理解代码结构 | ctags + SQLite + FastMCP | 完成（4阶段） |
| **gdb-ai-bridge** | GDB 调试与 AI 分析的桥梁 | GDB Python API + FastMCP | 完成（4阶段，187测试） |
| **Wiki** | 结构化知识沉淀与语义搜索 | Obsidian + qmd | 进行中 |

### 数据流

```
kernel-source ──(ctags)──▶ kernel_index.db ──(SQLite)──▶ enricher.py ──▶ analyzer.py ──▶ AI
                                │
                                ├──(export_symbols.py)──▶ symbol-docs/*.md ──(qmd)──▶ 语义搜索
                                │
                                └──(mcp_server.py)──▶ 9个MCP工具 ──▶ Claude Code

GDB session ──(collector.py)──▶ JSON ──(parser.py)──▶ OopsInfo ──(enricher.py)──▶ EnrichedContext
                                                                        │
                                                                        ├─ kernel_index.db (符号+调用链)
                                                                        └─ qmd wiki (知识库)

Wiki ──(qmd indexing)──▶ 向量搜索 ◄── mcp_server.py search 工具
                         向量搜索 ◄── enricher.py _search_wiki()
```

### 共享契约：SQLite 数据库

三个项目通过 `kernel_index.db` 共享数据，schema 如下：

```sql
-- 文件表
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,        -- 源文件路径
    subsystem TEXT,                    -- 子系统名，如 "drivers/gpio"
    line_count INTEGER
);

-- 符号表
CREATE TABLE symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                -- 符号名
    kind TEXT NOT NULL,                -- function, macro, struct, enum, variable, typedef
    file_id INTEGER NOT NULL,
    line INTEGER NOT NULL,             -- 行号
    pattern TEXT,                      -- ctags 正则模式
    typeref TEXT,                      -- 返回类型 / 类型引用
    signature TEXT,                    -- 函数参数签名
    is_static INTEGER DEFAULT 0,      -- 是否 static
    FOREIGN KEY (file_id) REFERENCES files(id)
);

-- 调用关系表
CREATE TABLE call_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id INTEGER NOT NULL,        -- 调用者 symbol.id
    callee_id INTEGER NOT NULL,        -- 被调用者 symbol.id
    call_site_file_id INTEGER NOT NULL,
    call_site_line INTEGER NOT NULL,
    FOREIGN KEY (caller_id) REFERENCES symbols(id),
    FOREIGN KEY (callee_id) REFERENCES symbols(id),
    FOREIGN KEY (call_site_file_id) REFERENCES files(id)
);

-- 索引
CREATE INDEX idx_symbols_name ON symbols(name);
CREATE INDEX idx_symbols_kind ON symbols(kind);
CREATE INDEX idx_symbols_file ON symbols(file_id);
CREATE INDEX idx_call_caller ON call_relations(caller_id);
CREATE INDEX idx_call_callee ON call_relations(callee_id);
```

---

## 第二部分：环境准备

### 必需依赖

| 依赖 | 最低版本 | 用途 |
|------|----------|------|
| Python | 3.10+ | 索引管道、MCP server、GDB 扩展 |
| Node.js | 18+ | 安装 qmd 搜索引擎 |
| Git | 2.30+ | 获取内核源码（sparse checkout） |
| universal-ctags | 6.0+ | 符号提取（项目自带 Windows 版） |
| GDB (with Python) | 10+ | GDB 扩展加载（arm-none-eabi-gdb-py3 或 gdb-multiarch） |

### 可选依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| qmd | 语义搜索（BM25 + 向量检索） | `npm install -g @tobilu/qmd` |
| Claude Code | AI 交互入口 | 按 Anthropic 文档安装 |
| pyserial | Phase 4 串口监控 | `pip install pyserial` |
| OpenOCD / J-Link | 硬件调试服务器 | 按芯片厂商文档安装 |

### Python 包

```bash
pip install mcp          # MCP server 框架（kernel-code-index 和 gdb-ai-bridge 都需要）
pip install pydantic     # MCP 工具字段定义（通常随 mcp 自动安装）
pip install pyserial     # 可选，Phase 4 串口监控
```

### 平台说明

| 平台 | 注意事项 |
|------|----------|
| Windows | 项目自带 ctags（`tools/ctags_bin/`）；qmd 需要 Git Bash 的 `sh.exe` 在 PATH 中 |
| Linux | 需自行安装 `universal-ctags`（`sudo apt install universal-ctags`） |
| macOS | `brew install universal-ctags` |

---

## 第三部分：搭建 kernel-code-index

### 3.1 获取项目

```bash
git clone https://github.com/akakaarh/kernel-code-index.git
cd kernel-code-index
pip install mcp
```

### 3.2 获取内核源码

使用 sparse checkout 只下载需要的子系统，避免下载整个内核（>2GB）：

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git kernel-src

cd kernel-src
git sparse-checkout set drivers/gpio include/linux/gpio
cd ..
```

#### 常用子系统 sparse-checkout 路径

| 子系统 | sparse-checkout 路径 |
|--------|---------------------|
| GPIO | `drivers/gpio include/linux/gpio` |
| SPI | `drivers/spi include/linux/spi` |
| I2C | `drivers/i2c include/linux/i2c*` |
| MMC | `drivers/mmc include/linux/mmc` |
| 网络 | `drivers/net include/linux/netdevice.h include/net` |
| 文件系统 | `fs/ext4 include/linux/ext4*` |
| 内存管理 | `mm include/linux/mm.h include/linux/slab.h` |

### 3.3 修改索引配置

编辑 `indexer.py`，修改子系统路径：

```python
SUBSYSTEM = "drivers/gpio"  # 改为你的子系统
```

### 3.4 运行索引

```bash
python indexer.py
```

索引完成后生成 `kernel_index.db`。

### 3.5 验证索引

```bash
python query.py stats                    # 查看统计信息
python query.py find gpio_chip           # 搜索符号
python query.py functions drivers/gpio/gpiolib.c  # 列出文件函数
python query.py callers gpiochip_add     # 查看调用者
python query.py callees gpiochip_add     # 查看被调用者
```

### 3.6 配置 Claude Code MCP

编辑 `.mcp.json`，将 `cwd` 改为你的项目绝对路径：

**Windows：**
```json
{
  "mcpServers": {
    "kernel-index": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:/Users/YourName/projects/kernel-code-index"
    }
  }
}
```

**Linux/macOS：**
```json
{
  "mcpServers": {
    "kernel-index": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/home/youruser/projects/kernel-code-index"
    }
  }
}
```

配置完成后，Claude Code 中即可使用 `find_symbol`、`call_graph` 等 9 个工具。

### 3.7 配置语义搜索（可选）

```bash
# 1. 安装 qmd
npm install -g @tobilu/qmd

# 2. 导出符号文档
python export_symbols.py

# 3. 创建 qmd collection
qmd add kernel-symbols symbol-docs/

# 4. 测试搜索
qmd query "gpio interrupt handling" -c kernel-symbols
```

### 3.8 添加更多子系统

```bash
# 1. 更新 sparse-checkout
cd kernel-src
git sparse-checkout add drivers/spi include/linux/spi
cd ..

# 2. 在 Claude Code 中使用 MCP 工具
# reindex_subsystem("drivers/spi")

# 或通过脚本
python indexer.py --subsystem drivers/spi
```

### 3.9 设计原理

**为什么用 ctags 而不是 clangd？**
- ctags 零配置、速度快、覆盖面广（函数/结构体/宏/枚举/typedef）
- clangd 需要 `compile_commands.json`，内核构建系统生成这个文件很麻烦
- ctags 不足：无法提取类型信息和调用关系 → 由 `call_graph.py` 补充

**调用图构建算法（call_graph.py）：**
1. 用状态机剥离 C 注释和字符串字面量
2. 从 ctags 报告的行号向前扫描找到函数体的 `{`
3. 用大括号深度追踪找到匹配的 `}`
4. 在清理后的函数体上用正则 `\b([a-z_][a-z_0-9]*)\s*\(` 提取函数调用
5. 与数据库中已知函数名交叉验证，写入 `call_relations` 表

**SQLite 而不是 JSON/向量数据库？**
- 无需额外服务，单文件部署
- SQL 查询灵活（JOIN、聚合、递归 CTE）
- WAL 模式支持并发读
- 1.7MB 数据库覆盖 212 个源文件，查询延迟 < 1ms

### 3.10 常见问题

**Q: ctags 找不到？**
Windows 用户：项目自带 ctags（`tools/ctags_bin/`），无需额外安装。
Linux 用户：`sudo apt install universal-ctags`，然后修改 `indexer.py` 中的 `CTAGS_BIN` 路径。

**Q: 索引很慢？**
GPIO 子系统（212 文件）约 10 秒。`drivers/net` 等大子系统可能需要几分钟。

**Q: 能索引整个内核吗？**
不建议。整个内核数百万行，数据库会很大且查询缓慢。按子系统分别索引。

**Q: 如何更新索引？**
重新运行 `python indexer.py` 重建数据库，或使用 `reindex_subsystem` MCP 工具增量添加。

---

## 第四部分：搭建 gdb-ai-bridge

### 4.1 获取项目

```bash
git clone https://github.com/akakaarh/gdb-ai-bridge.git
cd gdb-ai-bridge
```

### 4.2 配置 MCP

编辑 `.mcp.json`：

```json
{
  "mcpServers": {
    "gdb-ai-bridge": {
      "command": "python",
      "args": ["E:/projects/gdb-ai-bridge/mcp_server.py"]
    }
  }
}
```

### 4.3 设置环境变量

`enricher.py` 需要找到 `kernel_index.db`。设置环境变量：

```bash
# Windows (Git Bash)
export KERNEL_INDEX_DB="E:/projects/kernel-code-index/kernel_index.db"

# Linux
export KERNEL_INDEX_DB="/home/youruser/projects/kernel-code-index/kernel_index.db"
```

如果不设置，enricher 会按以下顺序查找：
1. 当前目录的 `kernel_index.db`
2. `../kernel-code-index/kernel_index.db`
3. `~/.kernel-index/kernel_index.db`

### 4.4 GDB 中加载扩展

```
(gdb) source E:/projects/gdb-ai-bridge/gdb_bridge/gdb_bridge.py
```

或添加到 `.gdbinit`：
```bash
source /path/to/gdb-ai-bridge/gdb_bridge/gdb_bridge.py
```

### 4.5 验证

```
(gdb) ai info
# 显示配置信息和采集器状态

(gdb) ai config arch arm target baremetal
# 配置架构和目标类型

(gdb) ai collect
# 手动采集当前上下文（Layer 0 + Layer 1）
```

### 4.6 离线分析（不需要 GDB）

```bash
# 分析 oops 日志文件
python analyzer.py crash_log.txt

# 分析 GDB bridge JSON 输出
python analyzer.py crash_dump.json

# 指定 kernel-index 数据库路径
python analyzer.py crash_log.txt --db /path/to/kernel_index.db

# 输出到文件
python analyzer.py crash_log.txt -o analysis.txt
```

### 4.7 GDB 命令参考

| 命令 | 说明 |
|------|------|
| `ai info` | 显示配置和状态 |
| `ai config arch <arch> target <target>` | 配置架构（arm/arm64）和目标类型（baremetal/linux） |
| `ai collect` | 手动采集 Layer 0 + Layer 1 |
| `ai collect --full` | 包含 Layer 2（大内存 dump） |
| `ai dump <file>` | 采集并保存到 JSON 文件 |
| `ai report <file>` | 在 GDB 中显示结构化崩溃报告 |
| `ai auto on` | 开启崩溃自动采集 |
| `ai auto off` | 关闭崩溃自动采集 |
| `ai auto status` | 查看自动采集状态 |
| `ai serve [port]` | 启动 HTTP API（默认 8765） |
| `ai exec <cmd>` | 执行任意 GDB 命令 |

### 4.8 分层采集器设计

| 层级 | 采集内容 | 耗时 | 触发条件 |
|------|----------|------|----------|
| Layer 0 | 寄存器 + 故障寄存器（CFSR/HFSR）+ 崩溃解码 | < 1ms | 始终安全 |
| Layer 1 | 异常帧 + 栈回溯 + 局部变量 | < 10ms | 需要 SP 有效 |
| Layer 2 | 大内存 dump | 用户触发 | 用户显式请求 |

每个采集方法都用 try/except 包裹，部分失败产生部分结果（带错误标注），不会崩溃。

### 4.9 设计原理

**适配器模式（arch × target 正交组合）：**

```
架构适配器 (ArchAdapter)        目标适配器 (TargetAdapter)
├── arm.py  (Cortex-M)          ├── baremetal.py (裸机)
│   SCB/CFSR/HFSR 解码          │   帧链遍历、局部变量
│   异常帧提取                   │
└── arm64.py (AArch64)          └── linux.py (Linux 内核)
    X0-X30, SP, PSTATE              bt 解析、kallsyms
```

添加 RISC-V 支持：只需创建 `arch/riscv.py` 实现 `ArchAdapter` 接口。

**白名单安全机制（debug_loop/safety.py）：**
- 只允许读操作：info, print, x/, backtrace, step, next, continue, break, finish
- 禁止写操作：set, call, write
- 最大 50 轮迭代
- 停滞检测（3 轮无进展）
- 振荡检测（重复操作序列）

**MMIO 安全：**
- 可配置安全内存区域，避免读有副作用的外设寄存器
- 可从 ELF LOAD 段自动解析安全区域

### 4.10 扩展指南

**添加新架构（如 RISC-V）：**

1. 创建 `gdb_bridge/arch/riscv.py`
2. 实现 `ArchAdapter` 接口：
   - `get_registers()` → 返回寄存器字典
   - `decode_fault()` → 解码故障原因
   - `get_exception_frame()` → 提取异常帧
3. 在 `gdb_bridge.py` 的 `_get_adapter()` 中注册

**添加新目标类型：**

1. 创建 `gdb_bridge/target/new_target.py`
2. 实现 `TargetAdapter` 接口：
   - `get_stack_trace()` → 返回栈回溯
   - `get_local_variables()` → 返回局部变量
   - `get_os_info()` → 返回 OS 信息

---

## 第五部分：搭建 Wiki 知识库

### 5.1 初始化仓库

```bash
mkdir -p /path/to/wiki
cd /path/to/wiki
git init
```

### 5.2 目录结构

```
wiki-root/
├── CLAUDE.md              # AI 行为指令
├── .mcp.json              # qmd MCP 配置
├── scripts/
│   ├── lint.py            # 健康检查工具
│   └── graph.py           # 知识图谱生成
├── embedded/              # Vault 1: 嵌入式
│   ├── CLAUDE.md          # Vault 专属指令
│   ├── raw/               # 原始文档（PDF 等，只读）
│   │   └── assets/
│   └── wiki/
│       ├── index.md       # 自动生成的索引
│       ├── log.md         # 操作日志
│       ├── dashboard.md   # Obsidian Dataview 面板
│       ├── sources/       # $ 前缀：源文档摘要
│       ├── concepts/      # # 前缀：概念页
│       ├── entities/      # @ 前缀：实体页
│       ├── synthesis/     # ! 前缀：综合对比
│       ├── questions/     # ? 前缀：Q&A
│       ├── notes/         # 学习笔记
│       └── progress/      # 学习进度
└── software/              # Vault 2: 软件/内核
    └── (同上结构)
```

### 5.3 页面命名规范

| 前缀 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `$` | 来源摘要 | 忠于原文，不跳章节 | `$ARMv7M_RefManual.md` |
| `#` | 概念 | 提炼通用原理，与具体文档解耦 | `#NVIC.md` |
| `@` | 实体 | 具体芯片/外设/工具 | `@CortexM_Series.md` |
| `!` | 综合 | 跨文档对比分析 | `!CortexA_vs_CortexM.md` |
| `?` | Q&A | 调试经验，极简三行 | `?HardFault-NULL.md` |

### 5.4 安装 qmd

```bash
npm install -g @tobilu/qmd
```

### 5.5 配置 MCP

编辑 `.mcp.json`：

```json
{
  "mcpServers": {
    "qmd": {
      "type": "stdio",
      "command": "node",
      "args": [
        "C:/Users/YourName/AppData/Roaming/npm/node_modules/@tobilu/qmd/dist/index.js",
        "mcp"
      ]
    }
  }
}
```

Linux 路径：
```json
{
  "args": ["/home/youruser/.npm-global/lib/node_modules/@tobilu/qmd/dist/index.js", "mcp"]
}
```

### 5.6 创建 qmd collection

```bash
# 嵌入式知识库
qmd add embedded /path/to/wiki/embedded/wiki/

# 软件知识库
qmd add software /path/to/wiki/software/wiki/

# 内核符号（来自 kernel-code-index）
qmd add kernel-symbols /path/to/kernel-code-index/symbol-docs/
```

### 5.7 配置 CLAUDE.md

复制模板并按需修改。关键配置项：

```markdown
# LLM Wiki — 父级协调层

## Vaults
- `embedded/` — 嵌入式知识库
- `software/` — 软件知识库

## 通用原则
1. Wiki 是知识的持久化积累
2. Raw sources 不可修改
3. LLM 负责所有 wiki 页面的创建、维护
4. 好的 Query 答案应存回 wiki
5. 定期 Lint 保持 wiki 健康

## 本地知识库
回答任何问题前，必须先用 qmd query 检索本地 Wiki。
```

每个 Vault 的 `CLAUDE.md` 定义：
- 学习路线和进度追踪
- 页面分类和命名规范
- 自动沉淀规则
- Ingest / Query / Lint 工作流

### 5.8 自动沉淀规则

| 触发场景 | 产出 | 路径 |
|----------|------|------|
| 解决了 bug | Q&A（现象/原因/修复） | `questions/?<简述>.md` |
| 讲解新概念 | 概念页 | `concepts/#<概念名>.md` |
| 对比分析 | 综合页 | `synthesis/!<主题>.md` |
| 学习推进 | 更新进度 | `progress/README.md` |
| 新芯片/工具 | 实体页 | `entities/@<名称>.md` |

Q&A 极简模板：
```yaml
---
type: question
tags: [debug, <标签>]
created: <日期>
---
# <问题简述>
**现象：** ...
**原因：** ...
**修复：** ...
```

### 5.9 工具脚本

**lint.py — 健康检查：**
```bash
python scripts/lint.py embedded          # 检查
python scripts/lint.py embedded --fix    # 自动修复
```

检查项：断链 wikilinks、孤立页面、缺失 frontmatter、过期 index。

**graph.py — 知识图谱：**
```bash
python scripts/graph.py embedded --format mermaid   # Mermaid 图
python scripts/graph.py embedded --format json      # JSON 数据
```

### 5.10 设计原理

**为什么用 Obsidian + wikilinks？**
- `[[wikilinks]]` 是最轻量的文档间引用方式
- Obsidian 提供图谱视图、Dataview 查询等开箱即用功能
- 纯 markdown 文件，git 友好，无 vendor lock-in

**为什么用 qmd 而不是全文搜索？**
- BM25（关键词精确匹配）+ 向量（语义理解）混合检索
- 本地运行，无需云服务
- 支持多 collection 联合查询
- 结果可按相关性分数过滤

**双轨制学习：**
- embedded 和 software 两个 vault 独立追踪进度
- 同一对话内通过关键词切换
- 切换前必须先"记录"，防止内容丢失

---

## 第六部分：串联三个项目

### 6.1 环境变量统一

```bash
# 指向 kernel-code-index 的数据库
export KERNEL_INDEX_DB="/path/to/kernel-code-index/kernel_index.db"
```

`enricher.py`（gdb-ai-bridge）和 `mcp_server.py`（kernel-code-index）都读这个数据库。

### 6.2 qmd collection 交叉

kernel-code-index 的 `search` 工具同时查询两个 collection：
- `kernel-symbols` — 内核代码符号（来自 export_symbols.py）
- `wiki` — Wiki 知识库

gdb-ai-bridge 的 `enricher.py` 也通过 `qmd search` 查询 wiki collection。

确保三个 collection 都已创建：
```bash
qmd list                    # 查看所有 collection
# 应该看到：embedded, software, kernel-symbols
```

### 6.3 完整验证流程

```
1. 粘贴一段 oops 日志到 Claude Code
   ↓
2. analyze-crash skill 自动触发
   ↓
3. mcp__gdb-ai-bridge__parse_oops(text) → 结构化 OopsInfo
   ↓
4. enricher.py 查 kernel_index.db → 符号定义 + 调用链
   ↓
5. enricher.py 查 qmd wiki → 相关概念和历史 Q&A
   ↓
6. analyzer.py 组装完整 prompt
   ↓
7. AI 输出结构化分析（原因/位置/调用路径/调试步骤/修复方向）
   ↓
8. 调试结果自动沉淀到 wiki questions/
```

### 6.4 快速验证命令

```bash
# 验证 kernel-code-index MCP
# 在 Claude Code 中：mcp__kernel-index__index_stats()

# 验证 gdb-ai-bridge MCP
# 在 Claude Code 中：mcp__gdb-ai-bridge__parse_oops(text="test")

# 验证 qmd 搜索
qmd query "GPIO interrupt" -c kernel-symbols -c wiki

# 验证离线分析
python /path/to/gdb-ai-bridge/analyzer.py /path/to/crash_log.txt
```

---

## 第七部分：AI Agent 使用手册

本部分告诉 AI Agent（如 Claude Code）如何使用这套系统。

### 7.1 可用 MCP 工具总览

#### kernel-code-index（9 个工具）

| 工具 | 参数 | 用途 |
|------|------|------|
| `find_symbol` | `name: str`, `exact: bool = False` | 按名称搜索符号（子串或精确匹配） |
| `list_functions` | `file: str` | 列出文件中的所有函数 |
| `search_by_kind` | `kind: str`, `subsystem: str = ""` | 按类型列出符号（function/struct/macro/enum） |
| `file_symbols` | `file: str` | 文件的完整符号概览（按类型分组） |
| `index_stats` | 无 | 数据库统计信息（文件数、符号数、按子系统分布） |
| `reindex_subsystem` | `subsystem: str` | 动态索引新的内核子系统 |
| `call_graph` | `name: str`, `direction: str = "both"`, `depth: int = 1` | 函数的调用者/被调用者树（支持多级展开） |
| `call_chain` | `source: str`, `target: str`, `max_depth: int = 5` | 两个函数之间的 BFS 最短调用路径 |
| `search` | `query: str`, `top_n: int = 5`, `rerank: bool = False` | 语义搜索（同时查 kernel-symbols + wiki） |

#### gdb-ai-bridge（5 个工具）

| 工具 | 参数 | 用途 |
|------|------|------|
| `parse_oops` | `text: str` | 解析 oops 日志为结构化 JSON |
| `analyze_crash` | `text: str`, `target_type: str = "generic"` | 完整分析流程（解析 + 富化 + prompt） |
| `list_actions` | 无 | 列出 12 种调试动作 |
| `translate_action` | `action: str`, `params: dict` | 将动作翻译为 GDB 命令 |
| `get_system_prompt` | `target_type: str` | 获取指定目标类型的系统 prompt |

#### qmd（Wiki 搜索）

| 工具 | 参数 | 用途 |
|------|------|------|
| `query` | `searches: list`, `collections: list`, `limit: int`, `intent: str` | 混合搜索（lex + vec + hyde） |
| `get` | `file: str` | 按路径获取单篇文档 |
| `multi_get` | `pattern: str` | 批量获取文档（glob 模式） |
| `status` | 无 | 查看索引状态 |

### 7.2 场景分类使用指南

#### 场景 A：理解内核代码

**问题示例：** "GPIO 子系统的 probe 流程是什么？"

```
步骤 1: search("gpio probe flow", collections=["kernel-symbols", "wiki"])
步骤 2: find_symbol("gpiochip_add") → 获取定义位置
步骤 3: call_graph("gpiochip_add", direction="callers", depth=2) → 查看调用链
步骤 4: file_symbols("drivers/gpio/gpiolib.c") → 了解文件结构
步骤 5: call_chain("gpiod_to_irq", "gpiochip_add") → 两个函数间的调用路径
```

**问题示例：** "这个结构体有哪些成员？"

```
步骤 1: find_symbol("gpio_chip", exact=True) → 找到定义位置
步骤 2: file_symbols("include/linux/gpio/driver.h") → 查看所有符号
```

#### 场景 B：崩溃分析

**问题示例：** 用户粘贴了一段 kernel oops 日志

```
步骤 1: parse_oops(text) → 结构化崩溃信息
步骤 2: find_symbol(crash_function) → 查看函数定义
步骤 3: call_graph(crash_function, direction="callers") → 谁调用了它
步骤 4: search("crash_function 相关知识", collections=["wiki"]) → 历史经验
步骤 5: 综合分析，输出 5 点结论：
        - 崩溃原因
        - 崩溃位置
        - 调用路径分析
        - 调试步骤
        - 可能的修复方向
```

**Skill 触发：** 当用户粘贴包含 "Unable to handle"、"Kernel panic"、"HardFault" 等关键词的文本时，自动触发 `analyze-crash` skill。

#### 场景 C：知识库查询

**问题示例：** "NVIC 是什么？"

```
步骤 1: query([{type:"vec", query:"NVIC 中断控制器"}], collections=["wiki"])
步骤 2: get("concepts/#NVIC.md") → 读取概念页
步骤 3: 如果 wiki 没有，再用 WebSearch 补充
```

**问题示例：** "之前调试过 SPI Flash 读 JEDEC ID 全 FF 的问题吗？"

```
步骤 1: query([{type:"lex", query:"SPI JEDEC ID FF"}], collections=["wiki"])
步骤 2: get("questions/?SPI-NOR-Flash-读JEDEC-ID全FF.md") → 读取 Q&A
```

#### 场景 D：调试控制

```
步骤 1: list_actions() → 查看可用动作
步骤 2: translate_action("read_register", {"register": "PC"}) → 翻译为 GDB 命令
步骤 3: get_system_prompt("baremetal") → 获取分析 prompt
```

### 7.3 关键配置速查

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `KERNEL_INDEX_DB` | kernel_index.db 路径 | `E:/projects/kernel-code-index/kernel_index.db` |
| qmd collection `kernel-symbols` | 内核符号文档 | `kernel-code-index/symbol-docs/` |
| qmd collection `wiki` | Wiki 知识库 | `Wiki/embedded/wiki/` + `Wiki/software/wiki/` |
| qmd collection `embedded` | 嵌入式 vault | `Wiki/embedded/wiki/` |
| qmd collection `software` | 软件 vault | `Wiki/software/wiki/` |

### 7.4 CLAUDE.md 行为指令摘要

**kernel-code-index CLAUDE.md 要点：**
- 目标：构建内核代码符号索引，让 AI 理解代码结构
- 4 个阶段全部完成
- 竞品调研结论：内核专用方案是空白地带

**gdb-ai-bridge CLAUDE.md 要点：**
- 项目已完成，187 个测试
- 支持 ARM32/ARM64，不限于 STM32MP157
- 架构适配器模式可扩展

**Wiki CLAUDE.md 要点：**
- 回答任何问题前，必须先用 `qmd query` 检索本地 Wiki
- 本地知识库优先级高于训练数据和网页搜索
- 教学模式：交互式问答，一次一个概念，确认后再继续
- 自动沉淀：bug → Q&A，新概念 → concepts，对比 → synthesis

---

## 第八部分：附录

### A. SQLite Schema 完整参考

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    subsystem TEXT,
    line_count INTEGER
);

CREATE TABLE symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    file_id INTEGER NOT NULL,
    line INTEGER NOT NULL,
    pattern TEXT,
    typeref TEXT,
    signature TEXT,
    is_static INTEGER DEFAULT 0,
    FOREIGN KEY (file_id) REFERENCES files(id)
);

CREATE TABLE call_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id INTEGER NOT NULL,
    callee_id INTEGER NOT NULL,
    call_site_file_id INTEGER NOT NULL,
    call_site_line INTEGER NOT NULL,
    FOREIGN KEY (caller_id) REFERENCES symbols(id),
    FOREIGN KEY (callee_id) REFERENCES symbols(id),
    FOREIGN KEY (call_site_file_id) REFERENCES files(id)
);

CREATE INDEX idx_symbols_name ON symbols(name);
CREATE INDEX idx_symbols_kind ON symbols(kind);
CREATE INDEX idx_symbols_file ON symbols(file_id);
CREATE INDEX idx_files_path ON files(path);
CREATE INDEX idx_files_subsystem ON files(subsystem);
CREATE INDEX idx_call_caller ON call_relations(caller_id);
CREATE INDEX idx_call_callee ON call_relations(callee_id);
```

### B. 常用子系统 sparse-checkout 路径速查

| 子系统 | 路径 |
|--------|------|
| GPIO | `drivers/gpio include/linux/gpio` |
| SPI | `drivers/spi include/linux/spi` |
| I2C | `drivers/i2c include/linux/i2c*` |
| MMC | `drivers/mmc include/linux/mmc` |
| USB | `drivers/usb include/linux/usb*` |
| 网络 | `drivers/net include/linux/netdevice.h include/net` |
| 文件系统 | `fs/ext4 include/linux/ext4*` |
| 内存管理 | `mm include/linux/mm.h include/linux/slab.h` |
| 中断 | `kernel/irq include/linux/irq.h` |
| 时钟 | `drivers/clk include/linux/clk*` |
| DMA | `drivers/dma include/linux/dma*` |
| PWM | `drivers/pwm include/linux/pwm.h` |

### C. FAQ

**Q: 三个项目必须全部搭建吗？**
不是。可以独立使用：
- 只要 kernel-code-index → 代码理解能力
- 只要 gdb-ai-bridge → 离线崩溃分析（不依赖 MCP）
- 只要 Wiki → 知识管理和语义搜索
- 三者串联 → 完整的调试 + 学习闭环

**Q: 不用 Claude Code 能用吗？**
kernel-code-index 和 gdb-ai-bridge 都有 CLI 接口（query.py 和 analyzer.py），不依赖 Claude Code。MCP 只是额外的 AI 集成层。

**Q: 如何扩展到其他芯片？**
gdb-ai-bridge 使用适配器模式，添加新架构只需：
1. 创建 `gdb_bridge/arch/<arch>.py` 实现 `ArchAdapter`
2. 在 `gdb_bridge.py` 中注册
3. 提供对应的 OpenOCD 配置文件

**Q: qmd 搜索结果不准怎么办？**
- 调整 `minScore` 过滤低相关性结果
- 使用 `intent` 参数提供上下文消歧
- 混合使用 `lex`（精确关键词）+ `vec`（语义理解）

### D. 扩展开发路线图

| 方向 | 说明 | 状态 |
|------|------|------|
| Kconfig 依赖图 | 解析 Kconfig → Makefile → 源文件依赖链 | 规划中 |
| clangd 集成 | 用 compile_commands.json 做更精确的类型分析 | 规划中 |
| 设备树映射 | dts 节点 ↔ 驱动 probe 函数的映射 | 规划中 |
| 子系统边界识别 | 自动识别 mm/、fs/、net/、drivers/ 等子系统 | 规划中 |
| RISC-V 支持 | gdb-ai-bridge 添加 RISC-V 架构适配器 | 规划中 |
| 增量索引 | 只重建变更文件的索引 | 规划中 |

---

> 手册版本：2026-05-31
> 源码仓库：
> - kernel-code-index: https://github.com/akakaarh/kernel-code-index
> - gdb-ai-bridge: https://github.com/akakaarh/gdb-ai-bridge
