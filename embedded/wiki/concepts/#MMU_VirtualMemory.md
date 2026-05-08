---
type: concept
related_sources:
  - $CortexA_ProgrammersGuide.md
tags: [arm, mmu, virtual-memory, page-table, memory-management]
---

# #MMU 与虚拟内存

## 概述

MMU（Memory Management Unit）在 ARM Cortex-A 中负责虚拟地址（VA）到物理地址（PA）的转换，支持基于页表的内存保护。与 Cortex-M 的 [[MPU — 内存保护单元（Cortex-M）|MPU]] 形成对比。

## 页表结构（ARMv7-A）

采用两级或三级页表（取决于配置）：

| 级别 | 描述符数 | 每项大小 | 覆盖范围 |
|------|----------|----------|----------|
| L1 | 4096 | 4KB | 1MB Section / 2MB/16KB Supersection |
| L2 | 256 | 4KB | 4KB Page / 64KB Large Page |

### L1 页表基址

`TTBR0`（用户空间）和 `TTBR1`（内核空间）寄存器指向页表的基物理地址。

## 转换过程

1. MVA（Modified Virtual Address）由 VA 高位选择 TTBR0/TTBR1
2. L1 页表索引 MVA[31:20]，查 L1 Descriptor
3. 若为 L2 页表，则 L2 索引 MVA[19:12]，查 L2 Descriptor
4. 输出物理地址 = 页基址 + 页内偏移

## 内存类型

| 类型 | 属性 | 典型用途 |
|------|------|----------|
| Strongly Ordered | 无缓存，无写缓冲 | 外设寄存器 |
| Device | 无缓存，写缓冲 | 外设 |
| Normal | 可缓存 | DDR/代码/堆 |

## Cache 与 MMU

- **VA → PA 转换**由 MMU 完成
- Cache 存储的是 **PA-indexed, PA-tagged** 数据（Cortex-A 通常如此）
- 开启 MMU 前通常需要Invalidate 所有 Cache

## 访问权限（AP）

| AP | 特权 | 用户 | 描述 |
|----|------|------|------|
| 00 | 无 | 无 | 无访问 |
| 01 | 读/写 | 无 | 特权仅访问 |
| 10 | 读/写 | 读 | 读锁定 |
| 11 | 读/写 | 读/写 | 全访问 |

## 域（Domain）

16 个域，每个域有 AP bits 控制。可以实现粗粒度的进程隔离。

> 来源：$CortexA_ProgrammersGuide.md
