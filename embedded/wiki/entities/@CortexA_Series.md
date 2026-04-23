---
type: entity
related_sources:
  - $CortexA_ProgrammersGuide.md
tags: [arm, cortex-a, processor-family]
---

# @Cortex-A 系列

## 概述

Cortex-A 是 ARM 的应用处理器系列，基于 ARMv7-A 架构（部分型号支持 ARMv8-A），面向智能手机、平板、嵌入式 Linux、车载等多种应用。

## 型号一览

| 型号 | 架构 | 特点 | 典型应用 |
|------|------|------|----------|
| Cortex-A5 | ARMv7-A | 入门级，低功耗，多核可选 | 入门手机、IoT |
| Cortex-A7 | ARMv7-A | 中端，全面支持特性，big.LITTLE 小核 | 中低端手机 |
| Cortex-A8 | ARMv7-A | 单核性能强，NEON mandatory | 早期智能手机 |
| Cortex-A9 | ARMv7-A | 出货量最大，支持多核（SMP） | 手机、平板、车载 |
| Cortex-A12 | ARMv7-A | 中端，A9 继任者 | 中端手机 |
| Cortex-A15 | ARMv7-A | 性能旗舰，big.LITTLE 大核 | 高端手机、服务器 |
| Cortex-A17 | ARMv7-A | A12 改进版，性能更强 | 中高端平板 |
| Cortex-A53 | ARMv8-A | 64-bit，A7 继任者，big.LITTLE 小核 | 主流手机 |
| Cortex-A57 | ARMv8-A | 64-bit，性能核 | 高端手机、服务器 |
| Cortex-A72 | ARMv8-A | 64-bit，A57 改进 | 高端手机、Chromebook |

## 共同特性

所有 Cortex-A 处理器均支持：
- ARM/Thumb/Thumb-2 指令集
- 硬件浮点（VFPv3）
- NEON SIMD（部分型号）
- MMU + TrustZone
- 多级 Cache
- 中断控制器（GIC）
- 多核（SMP，部分型号）

## big.LITTLE

Cortex-A7/A53 作为小核，Cortex-A15/A57/A72 作为大核，组合成异构多核系统，兼顾功耗和性能。

> 来源：$CortexA_ProgrammersGuide.md
