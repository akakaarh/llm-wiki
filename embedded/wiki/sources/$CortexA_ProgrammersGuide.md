---
type: source
title: ARM Cortex-A Series Programmer's Guide
doc_number: DEN0013D
version: 4.0
date: 2012
source: raw/assets/arm_cortexa_series_armva_programmers_guideguide_den0013_0400_en.pdf
tags: [arm, cortex-a, processor, programmer-model, neon, mmu, trustzone]
---

# $ARM Cortex-A Series Programmer's Guide

## 基本信息

- **文档编号**：DEN0013D
- **版本**：4.0（2012）
- **格式**：PDF，约 5MB

## 内容摘要

ARM Cortex-A 系列是 ARMv7-A 架构的应用处理器系列，涵盖 Cortex-A5、Cortex-A7、Cortex-A8、Cortex-A9、Cortex-A12、Cortex-A15 等多款处理器。详见 [[Cortex-A 系列]]。

### 核心章节

1. **程序员模型** — 处理器模式（User/FIQ/IRQ/Supervisor/Abort/Undefined/System）、CPSR 标志位、备份寄存器（SPSR），详见 [[Cortex-A 处理器模式]]
2. **指令集** — ARM 指令集（32-bit）、Thumb 指令集（16/32-bit 混合）、Thumb-2、Branch/LDM/STM/PUSH/POP
3. **NEON SIMD** — 128-bit SIMD 引擎，用于多媒体加速
4. **Cache 架构** — I-Cache / D-Cache、Cache 一致性
5. **[[MMU 与虚拟内存|MMU]]** — 虚拟地址到物理地址转换、页表结构
6. **TrustZone** — 安全世界/正常世界切换，AMBA 分隔
7. **LPAE** — 大物理地址扩展，支持超过 4GB 内存
8. **Multicore** — 多核处理器支持（SCU 总线）
9. **电源管理** — WFI/WFE 指令、动态电压频率调节
10. **调试** — ICE 调试接口、 breakpoints、watchpoints

## 适用场景

- 嵌入式 Linux 驱动开发
- 裸机（Bare-metal）程序设计
- Android HAL 层开发
- 底层系统软件（bootloader、kernel porting）
