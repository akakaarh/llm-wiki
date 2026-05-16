# Log

> 时间线日志。格式：`## [YYYY-MM-DD] <type> | <description>`

## [2026-04-22] init | Wiki 框架初始化

- 创建 Vault 结构
- 定义页面分类和命名规范
- 制定 Ingest/Query/Lint 工作流

## [2026-04-22] ingest | ARM Cortex-A Series Programmer's Guide

- 来源：raw/assets/arm_cortexa_series_armva_programmers_guideguide_den0013_0400_en.pdf
- 新建 $ 摘要：$CortexA_ProgrammersGuide.md
- 新建 @ 实体：@CortexA_Series.md
- 新建 # 概念：#CortexA_ProcessorModes.md、#ARM_InstructionSets.md、#MMU_VirtualMemory.md
- 更新 index.md

## [2026-04-22] ingest | ARMv7-M Architecture Reference Manual

- 来源：raw/assets/DDI0403E_e_armv7m_arm.pdf
- 新建 $ 摘要：$ARMv7M_RefManual.md
- 新建 @ 实体：@CortexM_Series.md（Cortex-M 全系列对比）
- 新建 # 概念：#NVIC.md、#MPU_CortexM.md
- 新建 ! 综合：!CortexA_vs_CortexM.md（ARMv7-A vs ARMv7-M 全方位对比）
- 更新 index.md

## [2026-05-08] init | 创建嵌入式学习路线

- 新建 `wiki/progress/README.md`：完整 6 阶段学习路线（嵌入式基础 → ARM架构 → Cortex-M深入 → 外设驱动 → RTOS → Cortex-A/Linux BSP）
- 新建 `wiki/notes/` 目录
- 更新 `CLAUDE.md`：添加 progress/notes 分类 + 学习流程工作流
- 更新 `index.md`：添加学习进度和学习笔记分类
- 整合已有 13 个 wiki 页面到学习路线中
- 预计新增 31 个 wiki 页面

## [2026-05-09] learning | 阶段1 嵌入式基础 — 全部完成

- 新建 `#NumberSystems_Encoding.md`：数制转换、补码、IEEE 754、ASCII/BCD/UTF-8
- 新建 `#DigitalLogic_Basics.md`：布尔代数、逻辑门、触发器、组合逻辑与时序逻辑
- 新建 `#EmbeddedC_BitManipulation.md`：位操作、volatile、MMIO、结构体对齐、中断安全编码
- 新建 `#Endianness.md`：大小端字节序、ARM 字节序支持
- 新建 `#ComputerArchitecture_Basics.md`：CPU流水线、AHB/APB总线、存储层次、DMA
- 更新 `index.md` 和 `progress/README.md`

## [2026-05-16] learning | 阶段2 ARM架构基础 — 全部完成

- 新建 `#ARM_ArchitectureOverview.md`：ARMv7 三大配置（A/R/M）、ARMv8 演进、架构版本命名、授权模式、生态链
- 2.2~2.4 使用已有页面：`#ARM_InstructionSets.md`、`#CortexA_ProcessorModes.md`、`#MMU_VirtualMemory.md`、`@CortexM_Series.md`、`@CortexA_Series.md`、`#NVIC.md`、`#MPU_CortexM.md`、`!CortexA_vs_CortexM.md`
- 更新 `index.md` 和 `progress/README.md`
