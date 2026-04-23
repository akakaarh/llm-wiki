---
type: concept
related_sources:
  - $CortexA_ProgrammersGuide.md
tags: [arm, instruction-set, thumb, neon, simd]
---

# #ARM 指令集体系

## 概述

ARM 架构定义了多套指令集，各有特点。Cortex-A 处理器支持全部这些指令集。

## 指令集类型

### ARM（32-bit）

- 定长 32-bit 指令
- 所有指令均可条件执行（condition field）
- 支持全部操作包括乘法、协处理器访问、Cache 管理
- 适用于高性能场景

### Thumb（16/32-bit）

- 16-bit 压缩指令，代码密度高
- 不支持部分 ARM 特性（如协处理器访问）
- 通过 BL/BLX 调用 Thumb 和 ARM 之间的互操作
- 适合存储受限场景

### Thumb-2

- Thumb 的扩展，引入 32-bit Thumb 指令
- 兼具代码密度和性能
- 大部分 Cortex-A 代码以 Thumb-2 编译

### Jazelle

- 支持 Java Bytecode 硬件加速（部分 Cortex-A 处理器）
- 已逐步被 ART 虚拟机取代

### NEON（SIMD）

- 128-bit SIMD 引擎
- 32x8-bit、16x16-bit、8x32-bit 等多种元素尺寸
- 用于多媒体：视频编解码、图像处理、信号处理
- 支持半精度浮点（FP16）
- 独立于 FPU（VFPv3）

## 指令格式分类

| 类型 | 示例指令 | 特点 |
|------|----------|------|
| Branch | B, BL, BX, BLX | 跳转，子程序调用 |
| Data Processing | ADD, SUB, MOV, CMP, AND | 算术/逻辑运算 |
| Load/Store | LDR, STR, LDM, STM | 内存访问 |
| Multiply | MUL, MLA, UMULL | 乘累加 |
| Status Transfer | MRS, MSR | CPSR/SPSR 访问 |
| Coprocessor | MCR, MRC, CDP | 协处理器操作 |

## 寄存器（USR 模式）

| 寄存器 | 别名 | 用途 |
|--------|------|------|
| r0-r12 | 通用 | 数据处理 |
| r13 | sp | 栈指针 |
| r14 | lr | 链接寄存器（子程序返回） |
| r15 | pc | 程序计数器 |

> 来源：$CortexA_ProgrammersGuide.md
