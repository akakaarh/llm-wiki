# Linux 存储 I/O 学习进度

> 更新时间由 Claude Code 每次"记录"操作时自动更新
> 新 session 开始时，读取此文件恢复进度

---

## 当前阶段

**阶段 2：request 在 scheduler 的生命周期**
状态：进行中 — 第2节 mq-deadline 已完成，待继续 BFQ

---

## 学习笔记

### 2026-05-10 mq-deadline 调度器

**设计目标：**
- 防饿死：每个请求都有 deadline，超时后优先处理
- 读写分离：读请求对延迟敏感，单独队列优先处理

**数据结构（4个队列）：**
```c
struct deadline_data {
    struct rb_root sort_list[2][2];    // [读/写][扇区排序/deadline排序]
    struct list_head fifo_list[2][2];  // [读/写][FIFO链表]
    struct request *next_rq[2];        // [读/写] 下一个扇区顺序请求
    int fifo_batch;                    // 批量处理数量
    int writes_starved;                // 写饥饿计数
};
```

**dispatch 优先级：**
1. 读 FIFO 有超时？→ 取出（防饿死）
2. 写 FIFO 有超时？→ 取出
3. 读 next_rq（扇区顺序，减少寻道）
4. 写 next_rq

**关键参数：**
| 参数 | 读 | 写 | 说明 |
|------|----|----|------|
| deadline | 500ms | 5000ms | 读对延迟敏感 |
| 优先级 | 高 | 低 | 读影响用户体验 |

**防饿死机制：**
- 连续 2 次 dispatch 都跳过写队列 → writes_starved >= 2
- 下次 dispatch 优先检查写队列
- 即使读队列有请求，也先处理写

**bio 与 request 关系确认：**
- dispatch 单位是 request，不是 bio
- bio 是文件系统提交给 block 层的"原料"
- block 层通过 bio_to_request 零拷贝转换为 request
- 调度器操作 request，硬件驱动处理 request

**核心结论：从 block 层开始，所有操作都以 request 为单位。**

---

### 2026-05-06 回顾与自测

对阶段1全部3节和阶段2第1节做了系统回顾和口头自测：

**掌握扎实的部分：**
- bio → request 的零拷贝关系
- 分层结构（文件系统 / block 层 / 硬件驱动）的职责边界
- buffered I/O vs DIO 的 completion 路径差异
- 执行上下文切换点（sleep / wake_up）
- plug 批量提交机制

**需要纠正的理解：**
- tag 的首要功能是**流控**（资源令牌），完成路由是第二功能，之前混为一谈
- DIO 完全不做 copy_to_user，DMA 直达用户 buffer

**学习策略确认：**
- 不需要死记函数调用链，理解架构和设计动机即可
- 实际 debug 靠 ftrace / bpftrace，不靠记忆

---

## 待填补缺口

- [x] bio → request 转换（block 内部机制，黑箱）
- [x] completion 后数据回拷路径（copy 发生在哪一层）
- [x] dispatch 单位确认（request，不是 bio）
- [ ] BFQ 调度器原理
- [ ] kyber 调度器原理
- [ ] 多队列架构细节（software queue / hardware queue 映射）

---

## 历史记录

| 日期 | 阶段 | 内容摘要 |
|------|------|----------|
| 2026-04-24 | 阶段1-第1节 | bio 结构、文件系统拆块生成 bio、ext4 读取路径（buffered/DIO/DAX）、ext4_map_blocks 查找物理块号 |
| 2026-04-28 | 阶段1-第2节 | blk_mq_submit_bio 全流程、tag 机制（硬件队列资源令牌）、bio_to_request 零拷贝引用、struct request 结构、blk_mq_insert_request 两条路径（dispatch 链表 vs 直接派发）、软中断设计理念（合并批处理、吞吐换延迟）、文件系统 vs block 层合并的本质区别（逻辑连续 vs 物理连续） |
| 2026-04-28 | 阶段1-第3节 | completion 路径：buffered I/O 在 filemap_read 内部 copy_page_to_iter、DIO 用 DMA 直达用户 buffer 不需要回拷、等待机制（wait queue 睡眠等 wake_up） |
| 2026-04-29 | 阶段2-第1节 | elevator scheduler（排序/合并/防饿死）、dispatch 流程（elevator 取最优 request 直接 pop 不扫描）、plug 机制（攒多个 bio 批量 unplug dispatch）、unplug 时机（进程 sleep、plug 满、时间到期）、per-task_struct plug 模型、request 派发到 NVMe 硬件（SQ/CQ/tag/CQE/doorbell）、硬中断完成路径、end_io 回调区分（buffered unlock_page vs DIO ki_complete） |
| 2026-05-06 | 回顾自测 | 系统回顾阶段1全部+阶段2第1节，纠正 tag 功能优先级（流控>路由）、确认 DIO 无 copy_to_user、明确学习策略：重架构轻函数链 |
| 2026-05-10 | 阶段2-第2节 | mq-deadline 调度器：设计目标（防饿死+读写分离）、4个队列结构（2×2：读/写 × 扇区排序/deadline排序）、红黑树+链表数据结构、dispatch 优先级（读FIFO超时→写FIFO超时→读next_rq→写next_rq）、关键参数（read_expire=500ms/write_expire=5000ms/fifo_batch=16/writes_starved=2）、防饿死机制（连续被抢占N次后提升优先级）、bio与request关系确认（dispatch单位是request，bio是文件系统提交的"原料"，block层转换为request后调度） |