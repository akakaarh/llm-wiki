---
type: note
tags: [linux, storage, performance, tuning, ftrace, blktrace, bpftrace, iostat]
---

# Stage 8: 性能调优

> 理论学习和实操分开进行
> - 理论：主对话（Windows）
> - 实操：WSL Claude Code Agent

---

## 8-1 观测工具入门（理论已完成）

### iostat：设备级 I/O 监控

```bash
iostat -xdm 1
```

关键字段：

| 字段 | 含义 | 关注点 |
|------|------|--------|
| `r/s`, `w/s` | IOPS | 每秒读/写请求数 |
| `rMB/s`, `wMB/s` | 吞吐量 | 带宽 |
| `r_await`, `w_await` | 平均延迟（ms） | **最重要**，超预期说明有问题 |
| `rrqm/s`, `wrqm/s` | 合并率 | 高=好，调度器在有效合并 |
| `aqu-sz` | 平均队列深度 | 过高说明硬件跟不上 |
| `%util` | 设备繁忙度 | 接近 100%=饱和 |

判断方法：

```
延迟高 + %util 低    → 软件层问题（调度器、驱动）
延迟高 + %util 高    → 硬件瓶颈（盘太慢）
延迟低 + %util 高    → 正常，硬件在满负荷工作
合并率低             → I/O 模式随机，调度器优化空间小
```

合并率低不代表调度器有问题，而是请求本身在磁盘上不相邻（随机 I/O），无法合并。

---

### blktrace：request 级生命周期追踪

```bash
blktrace -d /dev/nvme0n1 -o trace
blkparse -i trace | less
```

关键事件：

| 事件 | 含义 | 位置 |
|------|------|------|
| Q | bio 进入 block 层 | submit_bio() |
| G | 分配 request | blk_mq_alloc_request() |
| I | request 插入队列 | blk_mq_insert_request() |
| D | request dispatch 到硬件 | blk_mq_dispatch_rq_list() |
| C | 完成 | blk_mq_end_request() |

时间线分析：

```
Q → G:  分配 request 耗时（通常很快）
G → I:  插入队列耗时
I → D:  调度器排队耗时（如果有延迟，说明调度器在等待/排序）
D → C:  硬件处理耗时（I/O 延迟的主要部分）
Q → C:  总耗时（就是 iostat 里看到的 await）
```

---

### ftrace：内核函数级追踪

ftrace 是内核自带的追踪框架。

```
/sys/kernel/debug/tracing/
├── current_tracer        # 当前追踪器
├── trace                 # 输出
├── set_graph_function    # 设置要追踪的函数
└── events/block/         # block 层事件
    ├── block_bio_queue     ≈ blktrace Q
    ├── block_rq_insert     ≈ blktrace I
    ├── block_rq_issue      ≈ blktrace D
    └── block_rq_complete   ≈ blktrace C
```

ftrace 独有能力——函数调用图：

```bash
echo ext4_map_blocks > /sys/kernel/debug/tracing/set_graph_function
echo function_graph > /sys/kernel/debug/tracing/current_tracer
cat /sys/kernel/debug/tracing/trace
```

输出：
```
ext4_map_blocks() {
  ext4_ext_map_blocks() {
    ext4_ext_find_extent() { ... }
    ext4_ext_insert_extent() { ... }
  }
}
```

blktrace 只看到 request 级别，ftrace 能深入函数调用层级。

---

### bpftrace：自定义探针

bpftrace 是 eBPF 的高级脚本接口，最大优势是灵活。

```bash
# 追踪 bio 提交
bpftrace -e 'tracepoint:block:block_bio_queue {
  printf("%s sector=%d size=%d\n", comm, args->sector, args->nr_sector);
}'
```

bpftrace vs ftrace：

| 特性 | ftrace | bpftrace |
|------|--------|----------|
| 灵活性 | 预定义事件 | 自定义探针 |
| 过滤能力 | 有限 | 强（可编程） |
| 统计能力 | 需要外部工具 | 内置聚合 |
| 学习曲线 | 低 | 中高 |

bpftrace 独有能力——聚合统计：

```bash
# I/O 延迟直方图
bpftrace -e 'tracepoint:block:block_rq_complete {
  @usec = hist(args->error);
}'
```

---

## 8-2 性能分析方法论（待学）

### 自顶向下分析法

```
iostat        → "延迟高了"
    ↓
blktrace      → "I→D 间隔大，调度器在排队"
    ↓
ftrace        → "ext4_map_blocks 里 find_extent 耗时"
    ↓
bpftrace      → "99% 请求 < 1ms，但 1% 超过 10ms"
```

### 常见性能问题模式

待补充

---

## 8-3 调优手段（待学）

- I/O 调度器选择和参数调优
- 内核参数（dirty_ratio、nr_requests 等）
- 应用层优化（DIO vs buffered 选择、I/O 模式优化）

---

## 实操任务清单（给 WSL Agent）

> 在 WSL 中执行，需要 root 权限

### 任务 1：iostat 观察

```bash
# 终端 1：监控
iostat -xdm 1

# 终端 2：制造 I/O
dd if=/dev/zero of=/tmp/testfile bs=1M count=1000
dd if=/dev/zero of=/tmp/testfile bs=4K count=100000
```

观察不同 block size 对 IOPS 和吞吐的影响。

### 任务 2：blktrace 验证 bio→request

```bash
# 采集
blktrace -d /dev/sda -o trace &
dd if=/dev/zero of=/tmp/testfile bs=1M count=10
kill %1

# 分析
blkparse -i trace | head -50
```

- 看 Q 和 G 事件的扇区号是否一致（零拷贝验证）
- 看是否有合并（多个 Q 对应一个 G）

### 任务 3：ftrace 追踪函数调用

```bash
cd /sys/kernel/debug/tracing
echo 1 > events/block/enable
echo 1 > tracing_on
dd if=/dev/zero of=/tmp/testfile bs=4K count=10
echo 0 > tracing_on
cat trace
```

### 任务 4：bpftrace 统计延迟

```bash
# I/O 延迟分布
bpftrace -e 'tracepoint:block:block_rq_complete {
  @latency = hist(args->error);
}'
```

---

## 理论与实操对照

| 理论概念 | 实操验证 |
|----------|----------|
| bio→request 零拷贝 | blktrace: Q 和 G 扇区号一致 |
| 调度器合并 | blktrace: 多个 Q 对应一个 G |
| 调度器排队 | blktrace: I→D 间隔 |
| 硬件延迟 | blktrace: D→C 间隔 |
| 函数调用链 | ftrace: function_graph |
| 延迟分布 | bpftrace: hist() 聚合 |
