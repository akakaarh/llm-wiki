---
type: entity
related_sources:
  - $ARMv7M_RefManual.md
  - $CortexA_ProgrammersGuide.md
tags: [arm, cortex-m, microcontroller, processor-family]
---

# @Cortex-M 系列

## 概述

Cortex-M 是 ARM 的微控制器处理器系列，基于 ARMv7-M 架构（32-bit Thumb-2 only），面向单片机/微控制器市场。与 Cortex-A 的应用处理器路线平行，但设计目标完全不同。

## 型号对比

| 型号 | 架构 | FPU | DSP | MPU | I-Cache | D-Cache | TCM | 典型主频 |
|------|------|-----|-----|-----|---------|---------|-----|----------|
| Cortex-M0 | ARMv6-M | 无 | 无 | 无 | 无 | 无 | 无 | ~50 MHz |
| Cortex-M0+ | ARMv6-M | 无 | 无 | 可选 | 无 | 无 | 可选 | ~100 MHz |
| Cortex-M1 | ARMv7-M | 无 | 无 | 无 | 无 | 无 | 无 | FPGA 软核 |
| Cortex-M3 | ARMv7-M | 无 | 无 | 可选 | 无 | 无 | 无 | ~150 MHz |
| Cortex-M4 | ARMv7-M | 可选 | 有 | 可选 | 无 | 无 | 可选 | ~200 MHz |
| Cortex-M7 | ARMv7-M | 可选 | 有 | 有 | 可选 | 可选 | 可选 | ~400+ MHz |
| Cortex-M23 | ARMv8-M Baseline | 可选 | 无 | 可选 | 无 | 无 | 可选 | ~100 MHz |
| Cortex-M33 | ARMv8-M Mainline | 可选 | 可选 | 可选 | 无 | 无 | 可选 | ~200 MHz |
| Cortex-M55 | ARMv8.1-M | 可选 | Helium | 有 | 可选 | 可选 | 可选 | ~400 MHz |

## 与 Cortex-A 的核心区别

- **无 MMU** — 无虚拟内存，不能跑完整 OS（Linux/Android）
- **Thumb-2 only** — 无 ARM 模式，代码密度高
- **NVIC 集成** — 中断控制器直接集成在核心内，不像 A 系列用独立 GIC
- **低功耗** — 设计目标就是低功耗微控制器场景
- **确定性** — 中断延迟确定，无 cache miss 不确定因素

## 典型应用

| 型号 | 应用场景 |
|------|----------|
| Cortex-M0/M0+ | 简单传感器、IoT 端点、成本敏感场景 |
| Cortex-M3 | 工业 PLC、汽车电子、消费电子主控 |
| Cortex-M4 | 电机控制、音频处理、传感融合 |
| Cortex-M7 | 高性能音频、智能家居、汽车 ADAS |

## 厂商生态

- **ST** — STM32 全系列基于 Cortex-M3/M4/M7
- **NXP** — LPC 系列（LPC13xxx/17xxx/43xxx 基于 Cortex-M3/M4）
- **TI** — Tiva C 系列（TM4C，基于 Cortex-M4）
- **Nordic** — nRF52/nRF53 基于 Cortex-M4
- **Infineon** — XMC4000 基于 Cortex-M4
- **GD32** — 兆易创新，兼容 STM32 生态，基于 Cortex-M3/M4

> 来源：$ARMv7M_RefManual.md
