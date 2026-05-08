---
type: concept
related_sources:
  - $ARMv7M_RefManual.md
tags: [arm, cortex-m, mpu, memory-protection, embedded]
---

# #MPU — 内存保护单元（Cortex-M）

## 概述

MPU（Memory Protection Unit）是 Cortex-M3/M4/M7 中的可选内存保护硬件，位于 CPU 与总线之间，对内存访问进行权限检查。相比 Cortex-A 的 [[MMU 与虚拟内存|MMU]]，MPU 更简单，不支持虚拟地址映射，仅支持基于物理地址的区域保护。

## 与 MMU 的对比

| 特性 | MPU（Cortex-M） | MMU（Cortex-A） |
|------|----------------|----------------|
| 地址映射 | 无（线性映射） | 支持页表虚拟地址映射 |
| 虚拟内存 | 不支持 | 支持 |
| 保护粒度 | 8/16 个固定区域 | 多级页表，4KB~16MB 粒度 |
| XN 位 | 支持（禁止执行） | 支持 |
| 子区域 | 支持（8 个子区域可独立禁用） | 不支持 |
| 典型用途 | 进程隔离、栈保护 | 完整 OS 虚拟内存 |

## 保护区域

Cortex-M MPU 支持 **8 个或 16 个**保护区域（取决于具体实现），每个区域可配置：

| 属性 | 说明 |
|------|------|
| 基地址 | 区域起始地址（需对齐到区域大小） |
| 大小 | 4KB ~ 4GB（2^n） |
| 使能位 | 区域是否生效 |
| Subregion | 将区域分为 8 个子区域，可独立禁用 |
| 访问权限 | 特权读/写、用户读/写、执行权限 |
| 类型 | Normal / Device / Strongly Ordered |

## 子区域（Subregion）

每个区域可分成 8 个 subregion，可独立启用/禁用。用途：

- **栈溢出检测**：将栈区域的上/下各留一个 subregion 不使能，访问时触发 MemManage Fault
- **hole 区域**：在连续大区域内创建不连续的"洞"

## 典型应用场景

1. **多任务系统** — 每个任务分配独立数据区域，防止越界访问
2. **RTOS 栈保护** — 为每个任务栈设置边界 subregion
3. **只读区域** — Flash 区域设为只读，防止意外修改
4. **外设保护** — 外设地址范围设为特权访问，用户代码禁止直接操作

## 配置流程

1. 禁用 MPU（设置 CTRL.ENABLE = 0）
2. 配置各区域的 BASE、ATTR、SIZE 寄存器
3. 设置 RNR 选择区域号
4. 启用 MPU（设置 CTRL.ENABLE = 1）
5. 设置 CTRL.PRIVDEFENA 决定默认内存属性

## 注意

Cortex-M0/M0+ **无 MPU**，只有 M3 及以上才可选支持。

> 来源：$ARMv7M_RefManual.md
