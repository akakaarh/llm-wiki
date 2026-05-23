# Index

> 此文件由 LLM 自动维护，不要手动编辑。

## 学习进度

- [README.md](progress/README.md) — 嵌入式系统学习路线与进度追踪（6阶段24节）

## 学习笔记

暂无内容。

## 来源摘要 ($)

- [$CortexA_ProgrammersGuide.md](sources/$CortexA_ProgrammersGuide.md) — ARM Cortex-A 系列程序员指南 DEN0013D，涵盖处理器模式、指令集、Cache、MMU、TrustZone、NEON
- [$ARMv7M_RefManual.md](sources/$ARMv7M_RefManual.md) — ARMv7-M 架构参考手册 DDI0403E，覆盖 Cortex-M1/M3/M4/M7，NVIC、MPU、异常模型
- [$ATK_DLMP157_GettingStarted.md](sources/$ATK_DLMP157_GettingStarted.md) — 正点原子 STM32MP157 快速上手：开箱、硬件资源、串口设置、系统烧写、30个功能测试
- [$MP157_M4_CubeIDE.md](sources/$MP157_M4_CubeIDE.md) — M4 裸机 CubeIDE 开发指南：27章，环境搭建、GPIO/UART/Timer/SPI/I2C/ADC/DMA 外设实验
- [$MP157_M4_HAL.md](sources/$MP157_M4_HAL.md) — M4 裸机 HAL 库开发指南：34章，HAL/LL 库架构、外设 API、回调机制

## 实体 (@)

- [@CortexA_Series.md](entities/@CortexA_Series.md) — Cortex-A 全系列型号汇总（A5~A72，big.LITTLE 异构）
- [@CortexM_Series.md](entities/@CortexM_Series.md) — Cortex-M 全系列型号对比（M0/M3/M4/M7/M33 等），与 Cortex-A 核心区别

## 概念 (#)

- [#NumberSystems_Encoding.md](concepts/#NumberSystems_Encoding.md) — 数制转换（二/八/十六进制）、补码、IEEE 754 浮点数、ASCII/BCD/UTF-8 编码
- [#DigitalLogic_Basics.md](concepts/#DigitalLogic_Basics.md) — 布尔代数、逻辑门、触发器（D/JK/T）、组合逻辑与时序逻辑、计数器
- [#EmbeddedC_BitManipulation.md](concepts/#EmbeddedC_BitManipulation.md) — 位操作、volatile、MMIO、结构体对齐、中断安全编码
- [#Endianness.md](concepts/#Endianness.md) — 大小端字节序、ARM 字节序支持、网络字节序转换
- [#ComputerArchitecture_Basics.md](concepts/#ComputerArchitecture_Basics.md) — CPU流水线、AHB/APB总线、存储层次、哈佛/冯诺依曼结构、DMA
- [#CortexA_ProcessorModes.md](concepts/#CortexA_ProcessorModes.md) — 处理器模式（USR/FIQ/IRQ/SVC/ABT/UND/SYS）、CPSR 标志位
- [#ARM_InstructionSets.md](concepts/#ARM_InstructionSets.md) — ARM/Thumb/Thumb-2/NEON 指令集体系
- [#MMU_VirtualMemory.md](concepts/#MMU_VirtualMemory.md) — MMU 页表结构、VA→PA 转换、内存类型与访问权限
- [#NVIC.md](concepts/#NVIC.md) — 嵌套向量中断控制器，Cortex-M 中断机制，与 GIC 对比
- [#MPU_CortexM.md](concepts/#MPU_CortexM.md) — MPU 内存保护单元，Cortex-M 区域保护，与 MMU 对比

## 综合 (!)

- [!CortexA_vs_CortexM.md](synthesis/!CortexA_vs_CortexM.md) — Cortex-A 与 Cortex-M 全面对比：架构、功耗、选型、应用场景

## Q&A (?)

暂无内容。

---

最后更新：2026-05-23
