---
type: concept
related_sources:
  - $ARMv7M_RefManual.md
tags: [arm, cortex-m, interrupt, nvic, mcu]
---

# #NVIC — 嵌套向量中断控制器

## 概述

NVIC（Nested Vectored Interrupt Controller）是 ARM Cortex-M 架构的核心组成部分，**直接集成在处理器内核中**，与 Cortex-A 系列的独立 GIC 形成鲜明对比。

## 核心特性

1. **硬件嵌套栈** — 中断发生时，NVIC 自动将 xPSR、PC、LR、R0-R3、R12 入栈（部分可配置），无需软件干预
2. **向量表** — 包含所有异常/中断处理函数的入口地址，支持重定位
3. **优先级** — 支持动态优先级配置（8/16/256 级，取决于具体芯片）
4. **尾链（Tail-Chaining）** — 低延迟中断连续处理，无需恢复再入栈

## 与 GIC 的区别

| 特性 | NVIC（Cortex-M） | GIC（A系列） |
|------|------------------|--------------|
| 位置 | 集成在 CPU 内核 | 独立 IP 核（ARM GIC-400/500） |
| 中断数 | 最多 32 个外设中断（可扩展） | 最多 1020 个 SPI |
| 配置复杂度 | 简单 | 复杂（多 Redistributor、security） |
| 软件模型 | 简单寄存器 | 多寄存器组 |

## 关键寄存器

| 寄存器 | 用途 |
|--------|------|
| ISER | 中断使能 |
| ICER | 中断禁用 |
| ISPR | 中断挂起 |
| ICPR | 中断清除挂起 |
| IPR | 中断优先级 |
| IABR | 中断激活标志（只读） |

## 中断处理流程

1. 外设发出中断请求（IRQ）
2. NVIC 检查该 IRQ 优先级与当前优先级
3. 若优先级更高，咬尾（tail-chain）或进入新中断
4. 自动栈帧保存（寄存器入栈）
5. 跳转到向量表中的 ISR 地址
6. ISR 执行完毕后，NVIC 自动出栈，ERET 到被中断代码

## 应用注意事项

- **优先级分组** — 芯片厂家决定分成几组（影响抢占行为）
- **EXTI** — 外设 GPIO 中断通常通过 EXTI（External Interrupt）连接到 NVIC
- **向量化** — Cortex-M 的中断是向量式的，相比老式 ARM（FIC/向量表轮询）效率高很多

> 来源：$ARMv7M_RefManual.md
