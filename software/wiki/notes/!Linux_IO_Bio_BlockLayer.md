---
type: note
tags: [linux, storage, block-layer, bio, kernel, io]
---

# Linux 存储 I/O 路径：bio 与 Block Layer

> 学习日期：2026-04-24
> 阶段：阶段 1 - bio 在 block 层的生命周期

---

## 核心概念

### bio 是什么

bio 是 Linux 块 I/O 子系统的核心数据结构，代表**一次块 I/O 请求**。

```c
struct bio {
    struct bio_vec    *bi_io_vec;   // 内存页数组，每项是 (page, offset, len)
    sector_t          bi_sector;    // 起始扇区号（块设备视角）
    unsigned short    bi_idx;       // 当前已处理的 bio_vec 索引
    unsigned short    bi_vcnt;      // bio_vec 数组长度
    // ... 其他字段
}
```

关键特性：
- **page 级别**：每个 bio_vec 描述一个内存页的连续读写
- **块设备视角**：bi_sector 是磁盘物理扇区号
- **短生命周期**：一次 I/O 完成后 bio 被释放

---

## 从用户 read() 到 bio 的完整路径

```
用户 read(fd, buf, 4096)
    ↓
vfs_read()
    ↓
ext4_file_read_iter()        ← 文件系统层
    ↓
// 关键步骤：block mapping 查找
//    - 查文件 extent/block mapping 表
//    - 找出物理块号
//    - 判断是否连续（决定合并还是拆分）
    ↓
submit_bio()                 ← 进入 block 层
```

### 文件系统如何拆块

1. ext4 根据文件逻辑块号（LBA）查 extent mapping 表
2. 找出请求对应的物理块号
3. 拆分成 bio：
   - 连续物理块 → 合并成 1 个 bio
   - 不连续块 → 拆成多个 bio
4. 调用 `submit_bio()` 提交

> **核心结论：拆块执行者是文件系统，不是 block 层。**
> block 层收到 bio 后不会再拆分，只会转换（bio → request）或合并。

---

## bio → request 的转换（下一节内容）

（待学习）

---

## 待填补缺口

- [x] bio 的本质和结构
- [x] 文件系统如何拆块生成 bio
- [ ] bio → request 转换（block 内部机制）
- [ ] completion 后数据回拷路径

---

## 代码关键路径（已验证）

**ext4_file_read_iter() — 读取入口（`fs/ext4/file.c`）**

```c
static ssize_t ext4_file_read_iter(struct kiocb *iocb, struct iov_iter *to)
{
    if (IS_DAX(inode))
        return ext4_dax_read_iter(iocb, to);       // DAX 路径
    if (iocb->ki_flags & IOCB_DIRECT)
        return ext4_dio_read_iter(iocb, to);       // Direct I/O 路径
    return generic_file_read_iter(iocb, to);        //  buffered I/O 路径 ← most common
}
```

**两条 I/O 路径的区别：**

| 路径 | 函数 | 说明 |
|------|------|------|
| buffered I/O | `generic_file_read_iter()` | 先查 page cache，miss 时走 direct I/O |
| Direct I/O | `ext4_dio_read_iter()` → `iomap_dio_rw()` | 跳过 page cache，直达 block 层 |
| DAX | `ext4_dax_read_iter()` | 直接访问 persistent memory |

**buffered I/O 路径（cache miss 时）：**

```
generic_file_read_iter()
  └→ filemap_read()
       └→ ext4_direct_IO()           // 实际调用 iomap
            └→ iomap_dio_rw()       // iomap 子系统
                 └→ submit_bio()     // ← bio 在这里进入 block 层
```

**文件 block mapping 查找（生成 bio 的前置步骤）：**

```
ext4_direct_IO()
  └→ iomap_dio_rw()
       └→ iomap_apply()             // 应用 iomap 映射
            └→ ext4_dio_get_block()  // 查 extent mapping
                 └→ ext4_map_blocks() // 查文件物理块号
```

`ext4_map_blocks()` 是查 extent 表的核心函数，返回：
- `m_lblk`：逻辑块号
- `m_pblk`：物理块号
- `m_len`：连续块数量

这就是文件系统把用户请求拆成 bio 的地方。

**参考代码文件：**
- `fs/ext4/file.c` — ext4_file_read_iter
- `mm/filemap.c` — generic_file_read_iter, filemap_read
- `fs/iomap/direct-io.c` — iomap_dio_rw
- `fs/ext4/inode.c` — ext4_direct_IO, ext4_map_blocks

---

## blk_mq_submit_bio 全流程（阶段 1-第 2 节）

### 入口：submit_bio

```c
void submit_bio(struct bio *bio)
{
    // bio 携带：
    //   bio->bi_sector     起始扇区号
    //   bio->bi_io_vec     内存页数组
    //   bio->bi_iter       迭代器（偏移/剩余大小）
    //   bio->bi_end_io     完成回调（NULL 表示同步）
    __submit_bio_noacct_mq(bio);
}
```

### blk_mq_submit_bio 三步

```c
void blk_mq_submit_bio(struct bio *bio)
{
    // Step 1: 拿 tag（硬件队列资源号）
    hctx = blk_mq_get_tag(bio);
    
    // Step 2: 分配 request，把 bio 塞进去
    rq = blk_mq_alloc_request(hctx, bio->bi_opf, ...);
    
    // Step 3: 插入派发队列
    blk_mq_insert_request(rq, ...);
}
```

### tag 机制

**tag = 硬件队列中 pending request 的序号/id（取餐号）。**

- NVMe 支持 out-of-order 完成：先提交的请求可能后完成
- tag 是资源令牌，让 completion 正确路由到对应 end_io 回调
- tag 范围：0 ~ queue_depth-1
- rqs[tag] 数组是反向索引：硬件返回 tag → 直接查表得 request

```c
// lib/sbitmap_queue.c
int sbitmap_queue_get(struct sbitmap_queue *sbq, ...)
{
    tag = find_first_zero_bit(sbq->word, sbq->depth);
    if (tag < sbq->depth) {
        clear_bit(tag, sbq->word);  // 原子占用
        return tag;
    }
    // 队列满：睡在 wait_event，等 tag 归还
    wait_event(sbq->wq, ...);
}
```

**卡在 blk_mq_get_tag 的原因：所有 tag 都被占用（queue_depth 耗尽），新请求只能等前面的完成归还 tag。**

### bio_to_request（零拷贝引用）

```c
static void blk_mq_rq_ctx_init(..., struct bio *bio)
{
    // 值拷贝
    rq->__sector = bio->bi_sector;
    rq->nr_phys_segments = bio_segments(bio);
    rq->__data_len = bio->bi_iter.bi_size;
    
    // 零拷贝：bio 指针直接赋值，不复制 bio 本身
    rq->bio = bio;
    
    rq->cmd_type = REQ_TYPE_FS;
}
```

**零拷贝 = 只传指针，不复制数据。bio 和 request 共享底层页缓冲区和元数据。**

### struct request 结构

```c
struct request {
    // I/O 描述（从 bio 拷贝的值）
    sector_t    __sector;           // 起始扇区号
    unsigned int __data_len;         // 数据长度
    unsigned short nr_phys_segments; // 物理段数
    
    // bio 引用（零拷贝）
    struct bio *bio;
    
    // 硬件上下文
    unsigned int tag;               // tag 号
    struct blk_mq_hw_ctx *q;        // 硬件队列
    
    // 命令类型
    unsigned char cmd_type;         // REQ_TYPE_FS / ...
    
    // 回调
    rq_end_io_fn *end_io;          // 完成回调
    
    // 链表节点
    struct list_head queuelist;     // dispatch 队列链表
    
    // 驱动私有数据（紧跟在 request 后面）
    // [struct request][struct blk_mq_tag_data][驱动私有数据]
};
```

### blk_mq_insert_request 两条路径

```c
void blk_mq_insert_request(struct request *rq, bool run, ...)
{
    if (run) {
        // 路径A：进入 dispatch 链表，等待软中断处理
        blk_mq_put_rq_on_plane(rq, mq_poll);
        //    └→ list_add_tail(&rq->queuelist, &hctx->dispatch);
    } else {
        // 路径B：直接派发到硬件
        blk_mq_try_issue_list_directly(rq);
        //    └→ nvme_sq_wpair() → 写 doorbell 触发 DMA
    }
}
```

| 路径 | 特点 | 适用场景 |
|------|------|----------|
| 路径A（run=true） | 入 dispatch 链表，等软中断，可能被合并 | 普通异步 I/O，文件系统正常读写 |
| 路径B（run=false） | 直接写硬件队列，零软中断开销 | 同步 I/O、direct I/O、已知立即可执行 |

### 软中断设计理念

**核心思想：把"紧急响应"和"耗时处理"分开。**

```
硬件完成 → 硬中断触发 → 标记"有 I/O 完成了" → 硬中断返回
                                              ↓
                                    稍后（软中断上下文）处理
                                              ↓
                                    批量处理 dispatch 队列
                                              ↓
                                    调用 driver 回调
```

**三个设计理念：**

1. **合并（Merging）**：elevator 把相邻扇区的 request 合并，减少硬件 DMA 次数
2. **批处理**：软中断一次处理多个 request，避免多次硬中断开销
3. **延迟执行**：让 I/O 请求在软中断批量合并、优化后统一执行

**以吞吐换延迟**：牺牲少量延迟，换取更高整体吞吐。

---

## completion 后数据回拷路径（阶段 1-第 3 节）

### buffered I/O completion 路径

```
用户 read()（同步阻塞）
  ↓
generic_file_read_iter() → filemap_read()
  ├→ submit_bio() 发起异步 I/O
  └→ 进程进入 wait queue 睡眠
  
硬中断完成 → blk_mq_end_request()
  └→ unlock_page(page) → wake_up()
                    ↓
              filemap_read() 继续
                    ↓
              copy_page_to_iter() ← 在这里 copy_to_user
```

**关键：copy_to_user() 发生在 filemap_read() 内部，进程上下文，不是中断 handler。**

### Direct I/O completion 路径

```
generic_file_read_iter() → ext4_direct_IO() → iomap_dio_rw()
  ↓
submit_bio() 发起异步 I/O
  ↓
iomap_dio_rw() 立刻返回，进程进入 wait
  ↓
硬中断完成 → nvme_pci_complete_rq()
  ↓
end_io 回调：iomap_dio_complete_work()
  └→ iocb->ki_complete(iocb, ret)
       ↓
  唤醒用户进程，read() 返回
```

**DIO 不需要 copy_to_user**：数据直接 DMA 到用户 buffer（由 iov_iter 指定）。

### 两条路径的本质区别

| | buffered I/O | Direct I/O |
|---|---|---|
| 数据位置 | page cache | 用户 buffer |
| copy_to_user | 在 filemap_read()，进程上下文 | 不需要，DMA 直达 |
| 等待方式 | 进程睡在 wait queue | 进程睡在 iocb |
| 回调链 | unlock_page → wake_up | end_io → ki_complete |

### 等待机制统一理解

两种 I/O 都是同步阻塞 read，进程主动 sleep 等 wake_up。
- buffered：page unlock 触发 wake_up
- DIO：end_io 回调触发 ki_complete → wake_up

区别只是谁触发 wake_up（interrupt vs end_io 回调）。

---

## 文件系统 vs block 层合并的本质区别

**文件系统视角：逻辑块拆分**

```
ext4_map_blocks() 查 extent 表：
  fileA 逻辑块 0-3 → 物理块 1000-1007
  fileB 逻辑块 0-3 → 物理块 1008-1015
```

**block 层视角：物理扇区合并**

```
dispatch 链表里：
  bio [sector 1000, len 4096]  ← 来自 fileA
  bio [sector 1008, len 4096]  ← 来自 fileB
  
  ↓ elevator 合并（物理相邻）
  request [sector 1000, len 8192]
```

**核心区别：文件系统只看自己的 extent 表，不感知全局磁盘状态。block 层看到磁盘全局视图，能做跨文件/跨进程的物理合并。**

---

## 待填补缺口

- [x] bio 的本质和结构
- [x] 文件系统如何拆块生成 bio
- [x] bio → request 转换（block 内部机制）
- [x] completion 后数据回拷路径
