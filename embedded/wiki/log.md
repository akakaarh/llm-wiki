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

## [2026-05-17] upgrade | 学习路线升级：6阶段→8阶段

- **行业调研**：调研2025-2026 BSP工程师技能需求，发现Linux设备驱动、Yocto/Buildroot、Zephyr RTOS、Secure Boot/OTA为关键缺口
- **路线扩展**：6阶段→8阶段，新增阶段6（Linux设备驱动开发）和阶段8（构建系统与安全）
- **现代化改造**：阶段5加入Zephyr RTOS和A7↔M4核间通信；阶段2加入RISC-V架构概览
- **开发板确认**：STM32MP157（Cortex-A7+M4双核异构），一块板覆盖阶段2-8
- **实操计划**：阶段3-8各含详细实操练习（共30+个hands-on实验）
- **双轨制设计**：embedded和software两个vault进度独立，关键词切换（"继续嵌入式"/"切到软件"/"记录"），一个对话框内推进
- **权威资源**：Bootlin课程（免费PDF+YouTube）、Elixir内核源码浏览器、Yocto 6.0文档
- 更新 `wiki/progress/README.md`、`CLAUDE.md`、父级 `CLAUDE.md`、`software/CLAUDE.md`

## [2026-05-23] ingest | 正点原子 STM32MP157 快速上手指南

- 来源：`E:\资料\STM32MP157\【正点原子】STM32MP157开发板（A盘）-基础资料\10\STM32MP157快速体验V1.8.pdf` + `10\STM32MP157开箱指南及维护V1.1.pdf`
- 新建 $ 摘要：$ATK_DLMP157_GettingStarted.md（1120行，覆盖开箱、硬件资源、串口设置、系统烧写、30个功能测试、交叉编译）
- 更新 index.md

## [2026-05-24] ingest | STM32MP1 M4 裸机开发指南（CubeIDE + HAL 库）

- 来源：`09\STM32MP1 M4裸机CubeIDE开发指南 V1.5.2.pdf`（1100页）+ `09\STM32MP1 M4裸机HAL库开发指南V1.2.2.pdf`（923页）
- 新建 $ 摘要：$MP157_M4_CubeIDE.md（27章，环境搭建、GPIO/UART/Timer/SPI/I2C/ADC/DMA 外设实验）
- 新建 $ 摘要：$MP157_M4_HAL.md（34章，HAL/LL 库架构、外设 API、回调机制）
- 更新 index.md

## [2026-05-24] ingest | STM32MP1 嵌入式 Linux 驱动开发指南

- 来源：`09\STM32MP1嵌入式Linux驱动开发指南V2.0.pdf`（1549页，55+章）
- 新建 $ 摘要：$MP157_Linux_Driver_Guide.md（三篇：Ubuntu入门、系统移植TF-A/U-Boot/内核、ARM Linux驱动开发全外设实验）
- 更新 index.md

## [2026-05-24] ingest | Buildroot 用户手册中文版

- 来源：`10\Buildroot用户手册中文版(正点原子翻译)_V1.0.pdf`
- 新建 $ 摘要：$Buildroot_UserManual.md（26章，入门、配置、使用、定制、软件包开发、调试、贡献）
- 更新 index.md

## [2026-05-24] ingest | STM32MP1 异核通信指南（RPMSG + OpenAMP）

- 来源：`09\STM32MP1异核通信(基于CubeIDE) V1.1.pdf`（206页）
- 新建 $ 摘要：$MP157_IPC_RPMSG.md（7章，OpenAMP配置、资源分配、IPCC框架、RemoteProc驱动、RPMSG通信、虚拟串口、低功耗唤醒）
- 更新 index.md
