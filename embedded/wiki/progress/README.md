# 嵌入式系统学习进度

> 更新时间由 Claude Code 每次"记录"操作时自动更新
> 新 session 开始时，读取此文件恢复进度

---

## 总体路线

```
基础理论 → ARM架构 → Cortex-M深入 → 外设驱动 → RTOS → Cortex-A/Linux BSP
 (阶段1)    (阶段2)     (阶段3)       (阶段4)    (阶段5)    (阶段6)
```

| 阶段 | 名称 | 节数 | 难度 | 范围 |
|------|------|------|------|------|
| 1 | 嵌入式基础 | 4节 | ★★☆ | 广而浅 |
| 2 | ARM 架构基础 | 4节 | ★★★ | 中（已有页面支撑） |
| 3 | Cortex-M 架构深入 | 4节 | ★★★★ | 深 |
| 4 | Cortex-M 外设与驱动 | 4节 | ★★★☆ | 偏实践 |
| 5 | RTOS 理论 | 3节 | ★★★★ | 聚焦 |
| 6 | Cortex-A 架构与 Linux BSP | 4节 | ★★★★★ | 非常广 |

**与 software vault 的关系：**
- `embedded/` = 硬件架构 + 平台知识（ARM 处理器、外设、RTOS、启动流程、设备树）
- `software/` = Linux 内核深入（block 层、存储 I/O、内核子系统）
- 阶段6 是两者的交汇点：BSP 工程师既需要 Cortex-A 硬件知识（本 vault），也需要 Linux 内核知识（software vault）

---

## 当前阶段

**阶段 1：嵌入式基础**
状态：已完成

**阶段 2：ARM 架构基础**
状态：已完成

---

## 阶段详情

### 阶段 1：嵌入式基础（嵌入式基础理论）

**目标：** 建立嵌入式开发的前置知识栈 -- 数制编码、数字逻辑、嵌入式C、计算机体系结构基础。

#### 1.1 数制与编码
- 二进制/八进制/十六进制转换
- 补码表示（有符号整数）
- 定点数与浮点数（IEEE 754 概念）
- BCD、ASCII、UTF-8 编码
- **wiki 输出：** `#NumberSystems_Encoding.md`

#### 1.2 数字逻辑基础
- 布尔代数与逻辑门（AND/OR/NOT/XOR/NAND/NOR）
- 触发器（D触发器、JK触发器）
- 寄存器、多路选择器、解码器
- 组合逻辑 vs 时序逻辑
- **wiki 输出：** `#DigitalLogic_Basics.md`

#### 1.3 嵌入式C语言
- 位操作（置位/清位/翻转/掩码）
- volatile 关键字（防止编译器优化）
- 结构体对齐与打包（__attribute__((packed))）
- 内存映射I/O（*(volatile uint32_t *)0x40021000）
- 指针算术与类型转换
- 大小端在C中的表现
- **wiki 输出：** `#EmbeddedC_BitManipulation.md`, `#Endianness.md`

#### 1.4 计算机体系结构基础
- CPU流水线概念（取指/译码/执行/访存/写回）
- 总线架构（AHB高速总线/APB外设总线）
- 存储层次（寄存器 → Cache → SRAM → DRAM → Flash）
- 哈佛结构 vs 冯诺依曼结构
- DMA概念（直接内存访问，CPU不参与数据搬运）
- **wiki 输出：** `#ComputerArchitecture_Basics.md`

**已有页面：** 无（本阶段为前置知识）

---

### 阶段 2：ARM 架构基础

**目标：** 理解ARM架构家族全貌、指令集体系、处理器模式，建立Cortex-A与Cortex-M的整体认知框架。

#### 2.1 ARM 架构总览
- ARMv7 三大配置文件（A/R/M）
- ARMv8 演进（AArch32/AArch64）
- 架构版本号与授权模式
- ARM 生态（IP授权 → 芯片厂商 → 终端产品）
- **wiki 输出：** `#ARM_ArchitectureOverview.md` ✅

#### 2.2 指令集体系
- ARM（32-bit）：定长指令、条件执行
- Thumb（16-bit）：代码密度高
- Thumb-2（16/32-bit混合）：Cortex-M唯一指令集
- NEON（128-bit SIMD）：多媒体加速
- 指令格式分类（Branch/Data Processing/Load-Store/Multiply）
- 寄存器模型（R0-R15, SP/LR/PC）
- **已有页面：** `#ARM_InstructionSets.md`（直接使用）

#### 2.3 Cortex-A 程序员模型
- 7种处理器模式（USR/FIQ/IRQ/SVC/ABT/UND/SYS）
- CPSR 标志位（N/Z/C/V/I/F/T/M[4:0]）
- 模式切换（异常进入/SVC调用/ERET返回）
- Banked 寄存器
- MMU 与虚拟内存（两级页表、VA→PA转换、内存类型、访问权限）
- **已有页面：** `#CortexA_ProcessorModes.md`, `#MMU_VirtualMemory.md`（直接使用）

#### 2.4 Cortex-M 与 Cortex-A 对比
- Cortex-M 全系列型号对比（M0~M55，架构/特性/主频）
- Cortex-A 全系列型号一览（A5~A72，big.LITTLE）
- NVIC vs GIC 中断控制器对比
- MPU vs MMU 内存保护对比
- 功耗、成本、开发体验全方位对比
- 选型决策树
- **已有页面：** `@CortexM_Series.md`, `@CortexA_Series.md`, `#NVIC.md`, `#MPU_CortexM.md`, `!CortexA_vs_CortexM.md`（直接使用）

**已有来源文档：** `$ARMv7M_RefManual.md`, `$CortexA_ProgrammersGuide.md`（参考）

---

### 阶段 3：Cortex-M 架构深入

**目标：** 深入理解Cortex-M内部机制 -- 异常模型、内存映射、系统控制、启动流程。

#### 3.1 异常模型
- 异常类型（Reset/NMI/HardFault/MemManage/BusFault/UsageFault/SVCall/PendSV/SysTick）
- 优先级配置（PRIGROUP、抢占优先级/子优先级）
- 异常入口行为（硬件自动压栈：xPSR/PC/LR/R12/R0-R3）
- 异常出口与EXC_RETURN值（0xFFFFFFF1/F9/FD）
- 浮点上下文懒压栈（Lazy Stacking）
- **wiki 输出：** `#CortexM_ExceptionModel.md`
- **已有页面引用：** `#NVIC.md`（在3.1中扩展异常模型知识）
- **来源：** `$ARMv7M_RefManual.md` Part B

#### 3.2 内存映射与总线
- 4GB 地址空间布局（Code 512MB / SRAM 512MB / Peripheral 512MB / SCS 1MB）
- 系统控制空间（SCS）寄存器映射
- Bit-banding（位带别名区，原子位操作）
- AHB-AP 调试访问端口
- **wiki 输出：** `#CortexM_MemoryMap.md`, `#BitBanding.md`
- **来源：** `$ARMv7M_RefManual.md` B3章

#### 3.3 系统控制与配置
- SCB（系统控制块）关键寄存器（AIRCR/CCR/SCR/ICSR）
- SysTick 定时器（24-bit递减计数器，用于RTOS tick）
- 电源管理（WFI/WFE/Sleep-on-Exit/Low-Power Mode）
- 时钟树基础（HSE/HSI/PLL/AHB/APB分频）
- **wiki 输出：** `#CortexM_SystemControl.md`
- **来源：** `$ARMv7M_RefManual.md` B3章

#### 3.4 启动流程与链接
- Reset Handler 执行序列
- 向量表结构（SP初始值 + Reset_Handler + 各异常入口）
- MSP/PSP 双栈指针机制
- 链接脚本基础（.text/.data/.bss/堆栈布局）
- 启动文件（startup_stm32fxxx.s）解析
- **wiki 输出：** `#CortexM_Startup.md`

---

### 阶段 4：Cortex-M 外设与驱动

**目标：** 理解常见外设接口原理和寄存器级驱动模型（纯理论，不需要实际硬件）。

#### 4.1 GPIO 与外部中断
- GPIO 寄存器（MODER/ODR/IDR/BSRR/AFR）
- 输入模式（浮空/上拉/下拉/模拟）
- 输出模式（推挽/开漏）
- EXTI（外部中断/事件控制器）：边沿触发、中断与事件区别
- EXTI → NVIC 连接路径
- **wiki 输出：** `#GPIO_ExternalInterrupts.md`
- **已有页面引用：** `#NVIC.md`, `#MPU_CortexM.md`

#### 4.2 通信协议
- **UART**：帧格式（起始位/数据位/校验位/停止位）、波特率计算、硬件流控（RTS/CTS）、FIFO
- **SPI**：主从模式、4种CPOL/CPHA模式、全双工、片选管理、多从机拓扑
- **I2C**：7-bit/10-bit地址、ACK/NACK、时钟拉伸、多主仲裁、重复起始条件
- 协议对比与选型
- **wiki 输出：** `#UART_Protocol.md`, `#SPI_Protocol.md`, `#I2C_Protocol.md`

#### 4.3 定时器与PWM
- 基本定时器（预分频器 + 自动重载计数器）
- 输入捕获（测量脉冲宽度/频率）
- 输出比较（定时翻转/产生延迟）
- PWM 生成原理（占空比 = CCR/ARR）
- 看门狗定时器（IWDG独立看门狗 / WWDG窗口看门狗）
- **wiki 输出：** `#Timer_PWM.md`

#### 4.4 DMA与ADC
- DMA 通道/数据流概念
- 传输模式（外设→内存 / 内存→外设 / 内存→内存）
- 循环模式 vs 普通模式
- DMA 与外设配合（UART_RX + DMA示例）
- ADC 基础（分辨率、采样时间、通道多路复用、扫描模式）
- **wiki 输出：** `#DMA_Controller.md`, `#ADC_Basics.md`
- **wiki 输出：** `@STM32_Peripherals.md`（STM32外设寄存器概览，作为参考实体）

---

### 阶段 5：RTOS 理论

**目标：** 理解实时操作系统的核心概念、任务调度、同步机制，以及RTOS如何利用Cortex-M硬件特性。

#### 5.1 RTOS 基础概念
- 任务（Task）vs 线程（Thread）
- 任务状态模型（Ready / Running / Blocked / Suspended）
- 上下文切换机制（保存/恢复寄存器）
- 调度算法（时间片轮转、优先级抢占、协作式调度）
- Tick 机制（SysTick 驱动调度节拍）
- **wiki 输出：** `#RTOS_Fundamentals.md`

#### 5.2 同步与通信
- 信号量（二值信号量 / 计数信号量）
- 互斥锁（Mutex）与优先级反转问题
- 优先级继承协议（Priority Inheritance）
- 消息队列（任务间数据传递）
- 事件标志组（Event Groups）
- 死锁条件与预防
- **wiki 输出：** `#RTOS_Synchronization.md`

#### 5.3 内存管理与RTOS内部机制
- 固定大小内存块分配 vs 动态堆分配
- 每任务独立栈（栈大小估算）
- MPU 实现任务隔离（MPU区域分配策略）
- PendSV 实现上下文切换（延迟异常，最低优先级）
- FreeRTOS / RT-Thread / Zephyr 特性对比
- RTOS 移植到 Cortex-M 的关键步骤
- **wiki 输出：** `#RTOS_MemoryManagement.md`, `#ContextSwitch_CortexM.md`, `!RTOS_Comparison.md`
- **已有页面引用：** `#NVIC.md`（PendSV/SysTick优先级配置）, `#MPU_CortexM.md`（任务隔离）, `@CortexM_Series.md`（MPU支持情况）

---

### 阶段 6：Cortex-A 架构与 Linux BSP

**目标：** 理解Cortex-A系统架构，掌握BSP开发特有的核心知识。Linux内核深入内容（block层、存储子系统）已在 software vault 学习，此处聚焦硬件架构和BSP工作流。

#### 6.1 Cortex-A 系统架构
- 特权级模型（PL0用户态 / PL1内核态 / PL2 Hypervisor）
- GIC 中断控制器架构（Distributor / Redistributor / CPU Interface）
  - 中断类型（SGI/PPI/SPI）
  - 多核中断路由
- Cache 架构（L1 I-Cache/D-Cache、L2统一Cache）
  - 写直达（Write-Through）vs 写回（Write-Back）
  - Cache一致性（MESI协议概念）
- TrustZone 基础（Secure World / Normal World / Monitor Mode / SMC调用）
- **wiki 输出：** `#GIC_InterruptController.md`, `#Cache_Architecture.md`, `#TrustZone_Basics.md`
- **已有页面引用：** `#CortexA_ProcessorModes.md`（扩展PL0/PL1/PL2）, `#MMU_VirtualMemory.md`（Cache与MMU关系）, `$CortexA_ProgrammersGuide.md`

#### 6.2 启动流程
- SoC 启动ROM（Boot ROM，芯片固化代码）
- ARM Trusted Firmware（ATF/TF-A）启动阶段
  - BL1：安全初始化，加载BL2
  - BL2：平台初始化，加载BL31/BL33
  - BL31：EL3 Runtime（安全监控）
  - BL33：Non-Secure启动（U-Boot/Linux）
- U-Boot 基础（环境变量、bootcmd、加载内核）
- 内核镜像格式（zImage / Image / uImage）
- DTB（设备树二进制）加载
- **wiki 输出：** `#SoC_BootProcess.md`

#### 6.3 设备树与硬件描述
- DTS/DTB 语法（节点、属性、compatible字符串、reg、interrupts）
- 设备树层级结构（SoC级 → 板级 → 覆盖）
- pinctrl 子系统（引脚复用配置）
- clock 子系统（时钟树管理）
- regulator 子系统（电源管理）
- 内核如何解析设备树（of_platform_populate）
- **wiki 输出：** `#DeviceTree_Syntax.md`

#### 6.4 BSP 开发工作流
- BSP 包组成（bootloader配置、内核配置、设备树、驱动代码、根文件系统）
- 设备驱动模型（platform_device / platform_driver，设备树匹配）
- 内核移植步骤（选defconfig → 适配设备树 → 调试串口 → 驱动逐个bring-up）
- 交叉编译工具链（aarch64-linux-gnu-gcc / arm-linux-gnueabihf-gcc）
- 调试手段（JTAG/SWD、串口控制台、earlycon、ftrace）
- 常见BSP交付物
- **wiki 输出：** `#BSP_Development.md`
- **已有页面引用：** `@CortexA_Series.md`（SoC选型参考）, `$CortexA_ProgrammersGuide.md`（架构参考）

---

## 已有页面映射

| 已有页面 | 归入阶段 | 说明 |
|----------|----------|------|
| `$CortexA_ProgrammersGuide.md` | 阶段2（主）、阶段6（参考） | Cortex-A架构主要来源 |
| `$ARMv7M_RefManual.md` | 阶段2（参考）、阶段3（主） | Cortex-M架构主要来源 |
| `@CortexA_Series.md` | 阶段2、阶段6 | Cortex-A型号总览 |
| `@CortexM_Series.md` | 阶段2、阶段5 | Cortex-M型号对比 |
| `#ARM_InstructionSets.md` | 阶段2.2 | 指令集体系 |
| `#CortexA_ProcessorModes.md` | 阶段2.3、阶段6.1 | 处理器模式（阶段6扩展PL0/PL1/PL2） |
| `#MMU_VirtualMemory.md` | 阶段2.3、阶段6.1 | 虚拟内存（阶段6扩展Cache关系） |
| `#NVIC.md` | 阶段2.4、阶段3.1、阶段5.3 | 中断控制器（阶段3扩展异常模型，阶段5扩展RTOS中断管理） |
| `#MPU_CortexM.md` | 阶段2.4、阶段4.1、阶段5.3 | 内存保护（阶段4引用外设保护，阶段5扩展任务隔离） |
| `!CortexA_vs_CortexM.md` | 阶段2.4 | 全面对比 |

---

## 学习笔记

（随学习进度记录）

---

## 待填补缺口

（随学习进度更新）

---

## 历史记录

| 日期 | 阶段 | 内容摘要 |
|------|------|----------|
| 2026-05-08 | 初始化 | 创建学习路线，6阶段24节，整合已有13个wiki页面 |
| 2026-05-09 | 阶段1完成 | 嵌入式基础4节全部完成，新增5个wiki页面 |
| 2026-05-16 | 阶段2完成 | ARM架构基础4节完成，新增#ARM_ArchitectureOverview.md，其余已有页面直接使用 |

---

## 预计新增页面汇总

| 阶段 | 新增页面数 | 页面列表 |
|------|-----------|----------|
| 阶段1 | 5 | `#NumberSystems_Encoding.md`, `#DigitalLogic_Basics.md`, `#EmbeddedC_BitManipulation.md`, `#ComputerArchitecture_Basics.md`, `#Endianness.md` |
| 阶段2 | 1 | `#ARM_ArchitectureOverview.md` |
| 阶段3 | 5 | `#CortexM_ExceptionModel.md`, `#CortexM_MemoryMap.md`, `#CortexM_SystemControl.md`, `#CortexM_Startup.md`, `#BitBanding.md` |
| 阶段4 | 8 | `#GPIO_ExternalInterrupts.md`, `#UART_Protocol.md`, `#SPI_Protocol.md`, `#I2C_Protocol.md`, `#Timer_PWM.md`, `#DMA_Controller.md`, `#ADC_Basics.md`, `@STM32_Peripherals.md` |
| 阶段5 | 5 | `#RTOS_Fundamentals.md`, `#RTOS_Synchronization.md`, `#RTOS_MemoryManagement.md`, `#ContextSwitch_CortexM.md`, `!RTOS_Comparison.md` |
| 阶段6 | 7 | `#GIC_InterruptController.md`, `#Cache_Architecture.md`, `#TrustZone_Basics.md`, `#SoC_BootProcess.md`, `#DeviceTree_Syntax.md`, `#BSP_Development.md` |
| **合计** | **31** | |

---

最后更新：2026-05-16
