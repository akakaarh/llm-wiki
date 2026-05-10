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

### 软件：Linux 存储 I/O 学习路径

**当前：阶段 2 — request 在 scheduler 的生命周期**

| 节 | 内容 | 状态 |
|----|------|------|
| 阶段 1-1 | bio 结构、ext4 读取路径、ext4_map_blocks | ✅ |
| 阶段 1-2 | blk_mq_submit_bio、tag 机制、bio_to_request、合并机制 | ✅ |
| 阶段 1-3 | completion 路径、buffered vs DIO 回拷差异 | ✅ |
| 阶段 2-1 | elevator scheduler、dispatch、plug 机制、NVMe 硬件派发 | ✅ |
| 阶段 2-2 | mq-deadline 调度器（4 队列、防饿死、读写分离） | ✅ |
| 阶段 2-3 | BFQ 调度器（按进程公平分配带宽） | ⏳ 下一步 |
| 阶段 2-4 | kyber 调度器（令牌桶限流） | ⏳ |
| 阶段 2-5 | 多队列架构（software queue / hardware queue 映射） | ⏳ |

**已掌握核心概念：**
- bio → request 零拷贝转换
- 分层架构职责（文件系统 / block 层 / 硬件驱动）
- buffered vs DIO completion 路径差异
- mq-deadline 调度器原理（4 队列、dispatch 优先级、防饿死机制）
- dispatch 单位是 request，不是 bio

**学习策略：** 重架构轻函数链，debug 靠 ftrace / bpftrace

### 嵌入式

学习路线图已建立（6 阶段 24 课），阶段 1 未开始
