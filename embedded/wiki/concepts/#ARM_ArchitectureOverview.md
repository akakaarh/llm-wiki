---
type: concept
related_sources:
  - $CortexA_ProgrammersGuide.md
  - $ARMv7M_RefManual.md
tags: [arm, architecture, armv7, armv8, ecosystem]
---

# #ARM 架构总览

## 概述

ARM（Advanced RISC Machines）是一种 RISC 指令集架构，由 ARM Holdings 设计并通过 IP 授权模式推广。ARM 不直接制造芯片，而是授权给芯片厂商（如 ST、NXP、TI、Samsung、Qualcomm）进行 SoC 设计和生产。

## ARMv7 三大配置文件

ARMv7 架构定义了三个配置文件（Profile），面向不同应用场景：

| 配置文件 | 全称 | 目标场景 | 关键特性 |
|----------|------|----------|----------|
| **A（Application）** | ARMv7-A | 高性能应用处理器 | MMU、多模式、NEON、TrustZone |
| **R（Real-time）** | ARMv7-R | 实时系统 | MPU、低延迟中断、确定性行为 |
| **M（Microcontroller）** | ARMv7-M | 微控制器 | Thumb-2 only、NVIC、低功耗 |

### A Profile（ARMv7-A）

- 面向：手机、平板、服务器、网络设备
- 运行 Linux/Android 等全功能 OS
- 支持 [[CortexA_ProcessorModes|7种处理器模式]]
- [[MMU_VirtualMemory|MMU 虚拟内存]] 支持
- NEON SIMD 和 VFP 浮点扩展
- TrustZone 安全扩展
- 典型核心：Cortex-A5 ~ [[CortexA_Series|Cortex-A72]]

### R Profile（ARMv7-R）

- 面向：汽车电子、硬盘控制器、基带处理器
- 硬实时要求，确定性中断延迟
- 使用 MPU（非 MMU）
- 支持 ARM 和 Thumb 指令集
- 典型核心：Cortex-R4/R5/R7/R8

### M Profile（ARMv7-M）

- 面向：微控制器、IoT、传感器节点
- 仅支持 Thumb-2 指令集
- [[NVIC|NVIC 中断控制器]]，低延迟异常处理
- [[MPU_CortexM|MPU]] 可选
- 极低功耗（μW 级）
- 典型核心：[[CortexM_Series|Cortex-M0/M3/M4/M7]]

## ARMv8 演进

ARMv8 是 ARM 架构的重大升级，引入 64 位支持：

### ARMv8-A

- 引入 **AArch64**：64 位执行状态
- 保留 **AArch32**：向后兼容 ARMv7-A
- 两种执行状态可在同一核心切换（EL3 Monitor 控制）
- 通用寄存器从 16 个扩展到 31 个（X0-X30）
- 异常级别模型：EL0（用户态）~ EL3（安全监控）

| 执行状态 | 位宽 | 寄存器 | 指令集 |
|----------|------|--------|--------|
| AArch32 | 32-bit | R0-R15 | ARM / Thumb-2 |
| AArch64 | 64-bit | X0-X30, SP, PC | A64 |

### ARMv8-M

- Cortex-M 系列的 64 位就绪架构
- 引入 TrustZone for ARMv8-M（安全/非安全状态切换）
- 引入 ARMv8.1-M（MVE Helium 向量扩展）
- 典型核心：Cortex-M33/M55/M85

### ARMv8-R

- 实时配置的 64 位支持
- 典型核心：Cortex-R52/R82

## 架构版本命名

ARM 架构版本使用 `ARMv<x>` 格式，与具体处理器核心（`Cortex-<x>`）区分：

```
ARMv7-A  →  Cortex-A5, A7, A9, A15, A17
ARMv7-M  →  Cortex-M0, M3, M4, M7
ARMv8-A  →  Cortex-A53, A57, A72, A76
ARMv8-M  →  Cortex-M33, M55, M85
```

版本号的补充标识：
- **ARMv7-A**：基础版本
- **ARMv7ve**：虚拟化扩展（Virtualization Extensions）
- **ARMv7-A Security Extensions**：TrustZone
- **ARMv8.1-A**：原子操作、大系统扩展
- **ARMv8.2-A**：半精度浮点、SVE 向量扩展
- **ARMv8.4-A**：增强虚拟化、内存标签

## ARM 授权模式

ARM 采用三级授权模式：

| 授权层级 | 说明 | 例子 |
|----------|------|------|
| **架构授权** | 获得指令集授权，可自行设计核心 | Apple（A/M系列）、Qualcomm（Kryo/Oryon）、Samsung（Mongoose） |
| **核心授权** | 获得 ARM 设计的核心（硬核/软核） | ST（Cortex-M4）、NXP（Cortex-A53）、TI（Cortex-A15） |
| **物理 IP 授权** | 获得工艺相关的物理设计 | 台积电、三星（用于代工） |

## ARM 生态链

```
ARM Holdings (IP 设计)
    ↓ 授权
芯片厂商 (SoC 集成)
    ├── ST → STM32 系列 (Cortex-M)
    ├── NXP → i.MX / LPC 系列 (Cortex-A/M)
    ├── TI → AM335x / Sitara (Cortex-A)
    ├── Samsung → Exynos (Cortex-A + 自研核心)
    ├── Qualcomm → Snapdragon (Cortex-A + Kryo/Oryon)
    └── Apple → A/M 系列 (自研核心)
    ↓ 生产
终端产品
    ├── 手机/平板 (Cortex-A, Android/iOS)
    ├── IoT/可穿戴 (Cortex-M, FreeRTOS/Zephyr)
    ├── 汽车电子 (Cortex-R/M, AUTOSAR)
    └── 服务器/PC (Cortex-A, Linux)
```

## 与其他架构对比

| 特性 | ARM | x86 | RISC-V |
|------|-----|-----|--------|
| 指令集 | RISC | CISC | RISC |
| 授权模式 | IP 授权 | Intel/AMD 独占 | 开源 |
| 功耗 | 低 | 高 | 低 |
| 生态 | 成熟（移动端主导） | 成熟（PC/服务器主导） | 发展中 |
| 64 位 | ARMv8 (2011) | AMD64 (2003) | RV64 |

## 与本 Wiki 其他页面的关系

- [[ARM_InstructionSets|ARM 指令集体系]]：各配置文件支持的指令集细节
- [[CortexA_ProcessorModes|Cortex-A 处理器模式]]：ARMv7-A 的特权模式
- [[NVIC|NVIC 中断控制器]]：ARMv7-M 的中断机制
- [[MMU_VirtualMemory|MMU 虚拟内存]]：ARMv7-A 的内存管理
- [[CortexA_vs_CortexM|Cortex-A vs Cortex-M 对比]]：两种配置的全方位对比

> 参考：$CortexA_ProgrammersGuide.md, $ARMv7M_RefManual.md
