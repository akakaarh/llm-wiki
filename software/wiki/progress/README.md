# Linux 存储 I/O 学习进度

> 更新时间由 Claude Code 每次"记录"操作时自动更新
> 新 session 开始时，读取此文件恢复进度

---

## 双轨制说明

本项目采用**双轨制学习**，与 `embedded/wiki/progress/README.md` 配合使用。

| 关键词 | 操作 |
|--------|------|
| "继续嵌入式" | 读 `embedded/wiki/progress/README.md`，接着上次内容继续 |
| "切到软件" | 读本文件，接着上次内容继续 |
| "记录" | 更新当前vault进度文件 + git commit |
| "新话题" | 在当前vault里开新阶段/新专题 |
| "新专题 XXX" | 在当前vault里创建新的独立学习专题 |

**规则：切换前必须先"记录"，否则新内容会丢失。**

本vault可独立扩展新专题（如MM、网络等），不受嵌入式路线约束。

---

## 当前阶段

**阶段 2：request 在 scheduler 的生命周期**
状态：已完成 — mq-deadline/BFQ/kyber/多队列架构全部完成

---

**阶段 3：I/O 路径全景图与回顾**
状态：已完成

---

**阶段 4：写路径**
状态：已完成

---

**阶段 5：回顾与巩固**
状态：已完成

---

**阶段 6：NVMe 驱动层**
状态：已完成

---

**阶段 7：综合复习**
状态：已完成

### 阶段 7 内容规划

**7-1：完整 I/O 路径串联**
- 从 read()/write() 到硬件完成的完整路径
- 关键决策点总结
- 各层职责和数据流

**7-2：关键概念自测**
- 阶段 1-6 核心概念测试
- 识别薄弱环节
- 针对性巩固

**7-3：查漏补缺**
- 补充遗漏的知识点
- 深入理解模糊概念
- 建立完整知识体系

---

**阶段 8：性能调优**
状态：已完成

> 理论学习完成，实操待 WSL Claude Code Agent 进行
> 详细内容见 `wiki/perf-tuning/README.md`

### 阶段 8 内容

**8-1：观测工具入门** ✓
- iostat：设备级监控
- blktrace：request 级生命周期
- ftrace：内核函数级追踪
- bpftrace：自定义探针

**8-2：性能分析方法论** ✓
- 自顶向下分析法（iostat → blktrace → ftrace/bpftrace）
- 常见问题模式（延迟高+util低=软件、延迟高+util高=硬件、吞吐低+util低=I/O模式）

**8-3：调优手段** ✓
- 调度器选择（HDD→mq-deadline/BFQ、NVMe→kyber/none）
- 内核参数（dirty_ratio 调大增吞吐/调小降延迟、nr_requests 控制队列深度）
- 应用层优化（Buffered vs DIO 选择、对齐、减少 fsync、I/O 模式优化）

---

**阶段 9：ext4 文件系统**
状态：已完成

### 阶段 9 内容

**9-1：ext4 基础** ✓
- 磁盘布局（superblock、block group、inode table）
- inode 结构与文件元数据
- 目录 = 文件名→inode编号映射

**9-2：Extent 机制** ✓
- extent = 起始物理块 + 连续块数（比逐个指针高效）
- extent tree（i_block 直接存 ≤4 个 extent，多了用树）
- ext4_map_blocks：文件系统到 block 层的衔接点
- inode 读取流程（确定块组→组内偏移→读磁盘→解析）

**9-3：Journal（日志）** ✓
- 三种模式：journal（全记录）、ordered（默认，先数据后元数据）、writeback（最快但不安全）
- journal 区 = 磁盘固定区域，写入绕过 page cache，顺序追加写入
- fsync 完整路径（刷数据→写元数据到日志→提交日志）
- ordered 模式断电安全性：旧文件完好，新写入丢失

**9-4：ext4 生成 bio** ✓
- iomap 框架：三层结构（ext4_map_blocks → struct iomap → iomap 生成 bio）
- ext4_iomap_begin()：ext4 与 iomap 的衔接回调
- Buffered read：page cache miss → readahead → iomap 生成 bio → submit_bio
- Buffered write：copy_from_user → 标 dirty → write() 返回 → writeback 触发 → iomap 生成 bio → submit_bio
- DIO：直接生成 bio 挂用户 page → submit_bio → 等 bio completion
- HOLE 处理：不发 bio，内存填零返回（安全保证）

### 阶段 3 内容规划

**3-1：回顾与自测**
- 阶段 1（bio 生命周期）回顾
- 阶段 2（request/scheduler）回顾
- 关键概念自测
- 识别薄弱环节

**3-2：Buffered I/O 全景图**
- 从 read() 到数据返回的完整路径
- page cache 的作用
- 各层职责和数据流

**3-3：Direct I/O 全景图**
- 从 read() 到数据返回的完整路径
- 跳过 page cache 的路径
- DMA 直达用户 buffer

**3-4：I/O 路径对比与总结**
- buffered vs DIO 完整对比
- 关键决策点总结
- 性能特性对比

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

**需要多回顾的概念（2026-05-13 自测）：**
- buffered I/O vs DIO 的 completion 路径差异（容易混淆提交路径和完成路径）

**需要多回顾的概念（2026-05-14 自测）：**
- bio/request 生成层级：bio 由文件系统生成，request 由 block 层从 bio 转换（容易误以为 bio 生成 request）
- mq-deadline 4 队列：读/写 × 扇区排序/deadline 排序（容易忘记组合关系）
- DIO 数据写入机制：DMA 直接写入用户 page，ki_complete 只是唤醒进程的回调（容易误以为 ki_complete 写入数据）
- 执行上下文：dispatch 在进程上下文（容易误以为在中断上下文）

---

## 待填补缺口

- [x] bio → request 转换（block 内部机制，黑箱）
- [x] completion 后数据回拷路径（copy 发生在哪一层）
- [x] dispatch 单位确认（request，不是 bio）
- [x] mq-deadline 调度器原理
- [x] BFQ 调度器原理
- [x] kyber 调度器原理
- [x] 多队列架构细节（ctx/hctx 映射、tag、竞争解决）

---

## 历史记录

| 日期 | 阶段 | 内容摘要 |
|------|------|----------|
| 2026-04-24 | 阶段1-第1节 | bio 结构、文件系统拆块生成 bio、ext4 读取路径（buffered/DIO/DAX）、ext4_map_blocks 查找物理块号 |
| 2026-04-28 | 阶段1-第2节 | blk_mq_submit_bio 全流程、tag 机制（硬件队列资源令牌）、bio_to_request 零拷贝引用、struct request 结构、blk_mq_insert_request 两条路径（dispatch 链表 vs 直接派发）、软中断设计理念（合并批处理、吞吐换延迟）、文件系统 vs block 层合并的本质区别（逻辑连续 vs 物理连续） |
| 2026-04-28 | 阶段1-第3节 | completion 路径：buffered I/O 在 filemap_read 内部 copy_page_to_iter、DIO 用 DMA 直达用户 buffer 不需要回拷、等待机制（wait queue 睡眠等 wake_up） |
| 2026-04-29 | 阶段2-第1节 | elevator scheduler（排序/合并/防饿死）、dispatch 流程（elevator 取最优 request 直接 pop 不扫描）、plug 机制（攒多个 bio 批量 unplug dispatch）、unplug 时机（进程 sleep、plug 满、时间到期）、per-task_struct plug 模型、request 派发到 NVMe 硬件（SQ/CQ/tag/CQE/doorbell）、硬中断完成路径、end_io 回调区分（buffered unlock_page vs DIO ki_complete） |
| 2026-05-06 | 回顾自测 | 系统回顾阶段1全部+阶段2第1节，纠正 tag 功能优先级（流控>路由）、确认 DIO 无 copy_to_user、明确学习策略：重架构轻函数链 |
| 2026-05-10 | 阶段2-第2节 | mq-deadline 调度器：4个队列结构、dispatch 优先级、防饿死机制、bio与request关系确认 |
| 2026-05-11 | 阶段2-第3节 | BFQ 调度器：按进程公平分配带宽、budget 预算机制、虚拟时间调度、weight 权重与带宽分配 |
| 2026-05-11 | 阶段2-第4节 | kyber 调度器：令牌桶限流、低延迟优先、NVMe/UFS/eMMC 接口协议与颗粒类型 |
| 2026-05-13 | 阶段2-第5节 | 多队列架构：blk-mq 理念、ctx（软件队列/收件箱）与 hctx（硬件队列/工作台）映射关系、tag 作为硬件资源钥匙、hctx 数量受硬件限制、竞争解决（原子操作+自旋锁） |
| 2026-05-13 | 阶段3-第1节 | 回顾自测：8 个核心概念测试，薄弱环节是 buffered vs DIO completion 路径（容易混淆提交路径和完成路径），需要多回顾 |
| 2026-05-13 | 阶段3-第2节 | Buffered I/O 全景图：VFS→文件系统→page cache→bio→Block层→硬件→完成→copy_to_user |
| 2026-05-13 | 阶段3-第3节 | DIO 全景图：VFS→文件系统→bio(指向用户page)→Block层→硬件→DMA直达用户buffer→ki_complete |
| 2026-05-13 | 阶段3-第4节 | I/O 路径对比：Buffered vs DIO 完整对比、关键决策点、性能特性、适用场景 |
| 2026-05-14 | 阶段4-第1节 | Buffered Write 路径：write() → page cache → 标记 dirty → 返回，数据持久化由 writeback 异步完成 |
| 2026-05-14 | 阶段4-第2节 | Writeback 机制：触发时机（定时器/阈值/fsync/内存不足）、两个阈值（后台10%/前台20%）、刷盘流程 |
| 2026-05-14 | 阶段4-第3节 | DIO 写路径：write() → 生成bio(指向用户page) → block层 → 硬件 → 等完成 → 返回，数据立即持久化 |
| 2026-05-14 | 阶段4-第4节 | 写路径对比：Buffered vs DIO Write、page cache 按需分配、用户page/内核page/用户buffer 概念辨析 |
| 2026-05-14 | 阶段5-第1节 | 知识图谱梳理 + 自测：8 个核心概念测试，薄弱环节是 bio/request 生成层级（bio 文件系统生成，request block 层生成）、mq-deadline 4 队列（读/写 × 扇区排序/deadline 排序） |
| 2026-05-14 | 阶段5-第2节 | 薄弱环节巩固：bio/request 生成层级已纠正，mq-deadline 4 队列已巩固（读/写 × 扇区排序/deadline 排序组合） |
| 2026-05-14 | 阶段5-第3节 | 综合测试：8 个综合问题，薄弱环节是 DIO 数据写入机制（DMA 直接写入用户 page，ki_complete 只是回调）、执行上下文细节（dispatch 在进程上下文） |
| 2026-05-15 | 阶段6-第1节 | NVMe 队列机制：SQ/CQ 结构、doorbell 机制、command_id 对应 tag |
| 2026-05-15 | 阶段6-第2节 | NVMe 中断处理：MSI-X 中断、nvme_irq() 读取 CQ、通过 command_id 找 request |
| 2026-05-15 | 阶段6-第3节 | NVMe 错误处理：CQ 状态字段、可重试/不可重试错误、超时处理 |
| 2026-05-15 | 阶段6-第4节 | NVMe 完整 I/O 路径：读写操作全流程、NVMe/UFS/SCSI 协议对比 |
| 2026-05-16 | 阶段7-第1节 | 完整 I/O 路径串联：读写路径全景、关键决策点总结（VFS→文件系统→block层→调度器→硬件→完成回调→进程上下文） |
| 2026-05-16 | 阶段7-第2节 | 核心概念自测：8 个概念测试全过（bio/request 生成关系、tag 流控、mq-deadline 4 队列组合、DIO 零拷贝、dispatch 进程上下文、buffered write dirty page、BFQ 虚拟时间、kyber 令牌桶） |
| 2026-05-16 | 阶段7-第3节 | 查漏补缺：writeback 机制补全（触发时机、两个阈值、刷盘流程） |
| 2026-05-16 | 阶段8-第1节 | 观测工具入门：iostat 关键字段与判断方法、blktrace 事件时间线、ftrace 函数调用图、bpftrace 自定义探针与聚合统计。理论实操分离，实操在 WSL 进行 |
| 2026-05-17 | 阶段8-第2节 | 性能分析方法论：自顶向下分析法（iostat→blktrace→ftrace/bpftrace）、4种常见问题模式（延迟高+util低=软件瓶颈、延迟高+util高=硬件瓶颈、吞吐低+util低=随机I/O、吞吐不稳定=干扰/限流） |
| 2026-05-17 | 阶段8-第3节 | 调优手段：调度器选择（HDD→mq-deadline/BFQ、NVMe→kyber/none）、内核参数（dirty_ratio/nr_requests）、应用层优化（Buffered vs DIO 选择、对齐、减少fsync、I/O模式优化） |
| 2026-05-17 | 阶段9-第1节 | ext4基础：磁盘布局（块组结构）、inode（文件元数据，不含文件名和内容）、目录（文件名→inode映射）、Superblock（全局元信息，部分块组有备份） |
| 2026-05-17 | 阶段9-第2节 | Extent机制：extent=起始块+长度（比逐个指针高效）、extent tree（i_block直接存≤4个）、ext4_map_blocks（文件系统→block层衔接点）、inode读取完整流程 |
| 2026-05-17 | 阶段9-第3节 | Journal日志：三种模式（journal全记录/ordered默认/writeback）、journal区=磁盘固定区域绕过page cache顺序写入、fsync完整路径、ordered断电安全性（旧文件完好新写入丢失） |
| 2026-05-18 | 阶段9-第4节 | ext4生成bio：iomap框架三层结构（ext4_map_blocks→struct iomap→bio）、ext4_iomap_begin衔接回调、buffered read（readahead阶段同步生成bio）、buffered write（writeback异步生成bio）、DIO（直接挂用户page同步等待completion）、HOLE填零安全保证 |