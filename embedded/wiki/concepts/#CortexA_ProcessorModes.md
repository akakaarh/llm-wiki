---
type: concept
related_sources:
  - $CortexA_ProgrammersGuide.md
tags: [arm, processor-mode, cpsr, registers]
---

# #Cortex-A 处理器模式

## 概述

ARM Cortex-A 处理器支持 7 种特权模式，定义在 ARMv7-A 架构中。每种模式有独立的寄存器 banked 副本。与 [[NVIC|Cortex-M 的 NVIC 中断模型]] 不同，Cortex-A 使用独立的 GIC 处理中断。详见 [[Cortex-A 系列]]。

## 模式列表

| 模式 | 缩写 | 用途 | Banked 寄存器 |
|------|------|------|--------------|
| User | USR | 普通应用程序 | - |
| FIQ | FIQ | 快速中断 | r8-r14, SPSR |
| IRQ | IRQ | 普通中断 | r13-r14, SPSR |
| Supervisor | SVC | 系统调用/bootloader | r13-r14, SPSR |
| Abort | ABT | 内存访问错误 | r13-r14, SPSR |
| Undefined | UND | 未定义指令 | r13-r14, SPSR |
| System | SYS | 特权用户模式 | r13-r14 |

## CPSR 标志位

CPSR（Current Program Status Register）包含：

- **N** — 负数
- **Z** — 零
- **C** — 进位/借位
- **V** — 溢出
- **I** — IRQ 禁止（1=禁止）
- **F** — FIQ 禁止（1=禁止）
- **T** — Thumb 状态（1=Thumb）
- **M[4:0]** — 模式位

## 模式切换

- **异常进入**：自动切换到对应异常模式，备份 CPSR 到 SPSR
- **SVC 调用**：触发 SVC 异常进入 SVC 模式
- **ERET 返回**：从 SPSR 恢复 CPSR 并返回用户态

## 关键行为

- FIQ 有独立的 r8-r12 寄存器，FIQ 处理不需要保存这些寄存器
- 只有 System 模式和 User 模式共享寄存器 bank
- 模式切换不等于进程切换（由操作系统控制）

> 来源：$CortexA_ProgrammersGuide.md
