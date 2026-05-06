# Linux 存储 I/O 学习进度

> 更新时间由 Claude Code 每次"记录"操作时自动更新
> 新 session 开始时，读取此文件恢复进度

---

## 当前阶段

**阶段 2：request 在 scheduler 的生命周期**
状态：进行中 — 第1节已完成，待继续

---

## 学习笔记

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

---

## 历史记录

| 日期 | 阶段 | 内容摘要 |
|------|------|----------|
| 2026-04-24 | 阶段1-第1节 | bio 结构、文件系统拆块生成 bio、ext4 读取路径（buffered/DIO/DAX）、ext4_map_blocks 查找物理块号 |
| 2026-04-28 | 阶段1-第2节 | blk_mq_submit_bio 全流程、tag 机制（硬件队列资源令牌）、bio_to_request 零拷贝引用、struct request 结构、blk_mq_insert_request 两条路径（dispatch 链表 vs 直接派发）、软中断设计理念（合并批处理、吞吐换延迟）、文件系统 vs block 层合并的本质区别（逻辑连续 vs 物理连续） |
| 2026-04-28 | 阶段1-第3节 | completion 路径：buffered I/O 在 filemap_read 内部 copy_page_to_iter、DIO 用 DMA 直达用户 buffer 不需要回拷、等待机制（wait queue 睡眠等 wake_up） |
| 2026-04-29 | 阶段2-第1节 | elevator scheduler（排序/合并/防饿死）、dispatch 流程（elevator 取最优 request 直接 pop 不扫描）、plug 机制（攒多个 bio 批量 unplug dispatch）、unplug 时机（进程 sleep、plug 满、时间到期）、per-task_struct plug 模型、request 派发到 NVMe 硬件（SQ/CQ/tag/CQE/doorbell）、硬中断完成路径、end_io 回调区分（buffered unlock_page vs DIO ki_complete） |
| 2026-05-06 | 回顾自测 | 系统回顾阶段1全部+阶段2第1节，纠正 tag 功能优先级（流控>路由）、确认 DIO 无 copy_to_user、明确学习策略：重架构轻函数链 |