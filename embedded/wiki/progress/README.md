# 嵌入式系统学习进度

> 更新时间由 Claude Code 每次"记录"操作时自动更新
> 新 session 开始时，读取此文件恢复进度

---

## 双轨制说明

本项目采用**双轨制学习**，两个vault进度独立，一个对话框内切换：

| 关键词 | 操作 |
|--------|------|
| "继续嵌入式" | 读本文件，接着上次内容继续 |
| "切到软件" | 读 `software/wiki/progress/README.md`，接着上次内容继续 |
| "记录" | 更新当前vault进度文件 + git commit |
| "新话题" | 在当前vault里开新阶段/新专题 |

**规则：切换前必须先"记录"，否则新内容会丢失。**

---

## 开发板

**STM32MP157**（二手~400元）
- Cortex-A7（跑Linux）+ Cortex-M4（跑RTOS/裸机）
- 双核异构，一块板覆盖阶段2-8
- Bootlin课程直接覆盖此平台

---

## 总体路线

```
基础理论 → ARM架构 → Cortex-M深入 → 外设驱动 → RTOS → Linux设备驱动 → Cortex-A/BSP → 构建系统与安全
 (阶段1)    (阶段2)     (阶段3)       (阶段4)    (阶段5)    (阶段6)        (阶段7)        (阶段8)
```

| 阶段 | 名称 | 类型 | 实操环境 | 难度 |
|------|------|------|---------|------|
| 1 | 嵌入式基础 | 纯理论 | 无 | ★★☆ |
| 2 | ARM架构基础 + RISC-V概览 | 理论 | 无 | ★★★ |
| 3 | Cortex-M架构深入 + JTAG/SWD | 理论+实操 | M4裸机 | ★★★★ |
| 4 | Cortex-M外设与驱动 | 理论+实操 | M4外设 | ★★★☆ |
| 5 | RTOS + 核间通信 | 理论+实操 | FreeRTOS on M4 | ★★★★ |
| 6 | Linux设备驱动开发 | 理论+实操 | A7 Linux (WSL2+板上) | ★★★★★ |
| 7 | Cortex-A架构与Linux BSP | 理论+实操 | U-Boot/内核bring-up | ★★★★★ |
| 8 | 构建系统与安全 | 理论+实操 | Yocto/Buildroot | ★★★★ |

**与 software vault 的关系：**
- `embedded/` = 硬件架构 + 平台知识 + 设备驱动 + BSP + 构建系统
- `software/` = Linux 内核机制（block层、存储I/O、内存管理等），可独立扩展新专题
- 阶段6 是两者的交汇点：驱动开发需要Linux内核知识（software vault）+ 硬件架构知识（本vault）

---

## 当前阶段

**阶段 1：嵌入式基础**
状态：已完成

**阶段 2：ARM架构基础 + RISC-V概览**
状态：已完成

---

## 阶段详情

### 阶段 1：嵌入式基础（已完成）

**目标：** 建立嵌入式开发的前置知识栈

#### 1.1 数制与编码
- 二进制/八进制/十六进制转换、补码、IEEE 754、BCD/ASCII/UTF-8
- **wiki 输出：** `#NumberSystems_Encoding.md` ✅

#### 1.2 数字逻辑基础
- 布尔代数、逻辑门、触发器、组合逻辑与时序逻辑
- **wiki 输出：** `#DigitalLogic_Basics.md` ✅

#### 1.3 嵌入式C语言
- 位操作、volatile、结构体对齐、MMIO、指针算术、大小端
- **wiki 输出：** `#EmbeddedC_BitManipulation.md` ✅, `#Endianness.md` ✅

#### 1.4 计算机体系结构基础
- CPU流水线、AHB/APB总线、存储层次、DMA概念
- **wiki 输出：** `#ComputerArchitecture_Basics.md` ✅

---

### 阶段 2：ARM架构基础 + RISC-V概览

**目标：** 理解ARM架构家族全貌、指令集体系、处理器模式，建立Cortex-A与Cortex-M的整体认知框架。

#### 2.1 ARM 架构总览 ✓
- ARMv7 三大配置文件（A/R/M）
- ARMv8 演进（AArch32/AArch64）
- 架构版本号与授权模式
- ARM 生态（IP授权 → 芯片厂商 → 终端产品）
- **wiki 输出：** `#ARM_ArchitectureOverview.md`

#### 2.2 指令集体系 ✓
- ARM（32-bit）、Thumb（16-bit）、Thumb-2（16/32-bit混合）、NEON（128-bit SIMD）
- 指令格式分类、寄存器模型（R0-R15, SP/LR/PC）
- 已有页面：`#ARM_InstructionSets.md`

#### 2.3 Cortex-A 程序员模型 ✓
- 7种处理器模式、CPSR标志位、模式切换、Banked寄存器
- MMU与虚拟内存（两级页表、VA→PA转换、TLB）
- 已有页面：`#CortexA_ProcessorModes.md`, `#MMU_VirtualMemory.md`

#### 2.4 Cortex-M 与 Cortex-A 对比 ✓
- NVIC vs GIC（确定性12周期 vs 多核灵活路由）
- MPU vs MMU（8区域无虚拟地址 vs 页表翻译进程隔离）
- 选型决策树（实时→M、Linux→A、都要→双核异构）
- 已有页面：`@CortexM_Series.md`, `@CortexA_Series.md`, `#NVIC.md`, `#MPU_CortexM.md`, `!CortexA_vs_CortexM.md`

#### 2.5 RISC-V 架构概览 ✓
- 开源免费、模块化ISA（RV32I基础47条 + 可选扩展M/F/D/C/A/V）
- 3级特权（U/S/M）、硬件简化软件补
- Linux mainline支持现状（RV64成熟，RV32完善中）
- **wiki 输出：** `#RISC-V_ArchitectureOverview.md`

**已有来源文档：** `$ARMv7M_RefManual.md`, `$CortexA_ProgrammersGuide.md`（参考）

---

### 阶段 3：Cortex-M架构深入 + JTAG/SWD

**目标：** 深入理解Cortex-M内部机制，掌握硬件调试基础。
**类型：** 理论+实操 | **环境：** M4裸机（STM32MP157）
**主要资料：** `$CortexM3M4_DefinitiveGuide.md`（架构/异常/调试/MPU）、`$MP157_M4_CubeIDE.md`（实操）、`$MP157_M4_HAL.md`（HAL库）

#### 3.1 异常模型
- 异常类型、优先级配置、异常入口行为、EXC_RETURN、浮点懒压栈
- **wiki 输出：** `#CortexM_ExceptionModel.md`
- **来源：** `$CortexM3M4_DefinitiveGuide.md` Ch7（异常与中断）

#### 3.2 内存映射与总线
- 4GB地址空间布局、SCS寄存器映射、Bit-banding、AHB-AP
- **wiki 输出：** `#CortexM_MemoryMap.md`, `#BitBanding.md`
- **来源：** `$CortexM3M4_DefinitiveGuide.md` Ch6（内存系统，含 Bit-band 公式）

#### 3.3 系统控制与配置
- SCB关键寄存器、SysTick定时器、电源管理、时钟树基础
- **wiki 输出：** `#CortexM_SystemControl.md`
- **来源：** `$CortexM3M4_DefinitiveGuide.md` Ch9（低功耗与系统控制）、`$MP157_M4_CubeIDE.md` Ch9（时钟配置）、`$MP157_M4_HAL.md` Ch18/21（时钟/SysTick）

#### 3.4 启动流程与链接
- Reset Handler执行序列、向量表结构、MSP/PSP双栈指针、链接脚本、启动文件解析
- **wiki 输出：** `#CortexM_Startup.md`
- **来源：** `$CortexM3M4_DefinitiveGuide.md` Ch4（复位序列）、`$MP157_M4_HAL.md` Ch8（启动文件分析、分散加载文件）

#### 3.5 JTAG/SWD调试基础（新增）
- JTAG/SWD协议概念
- OpenOCD + ST-Link环境搭建
- GDB远程调试（断点、单步、寄存器查看）
- **wiki 输出：** `#JTAG_SWD_Debugging.md`
- **⚠️ 资料缺口：** 现有资料仅覆盖 CubeIDE 图形化调试（`$MP157_M4_CubeIDE.md` Ch4.3），OpenOCD+GDB 命令行调试需补充

**实操练习（STM32MP157 M4核心）：**

| 练习 | 内容 | 验证标准 |
|------|------|---------|
| 3-P1 | 搭建开发环境：arm-none-eabi-gcc + STM32CubeMP1 SDK + OpenOCD | `arm-none-eabi-gcc --version` 正常输出 |
| 3-P2 | 第一个M4裸机程序：编译main.c，通过remoteproc加载到M4运行 | 串口/LED有输出 |
| 3-P3 | JTAG调试：OpenOCD+ST-Link连接M4，GDB设断点、单步、查看寄存器 | `info registers` 看到R0-R15/CPSR |
| 3-P4 | 异常触发实验：主动触发HardFault，GDB中观察入栈帧 | 能看到异常压栈的8个寄存器值 |
| 3-P5 | SysTick实验：配置SysTick中断，LED每秒闪烁 | LED精确1秒周期闪烁 |

---

### 阶段 4：Cortex-M外设与驱动

**目标：** 理解常见外设接口原理和寄存器级驱动模型。
**类型：** 理论+实操 | **环境：** M4外设（STM32MP157）
**主要资料：** `$MP157_M4_CubeIDE.md`（27章外设实验）、`$MP157_M4_HAL.md`（34章HAL库API）、`$STM32MP157_ReferenceManual.md`（寄存器详解）

#### 4.1 GPIO 与外部中断
- GPIO寄存器、输入/输出模式、EXTI、EXTI→NVIC连接路径
- **wiki 输出：** `#GPIO_ExternalInterrupts.md`
- **来源：** `$MP157_M4_CubeIDE.md` Ch10-13（GPIO输出/输入/EXTI）、`$MP157_M4_HAL.md` Ch11-19（汇编LED到EXTI）、`$STM32MP157_ReferenceManual.md` GPIO/EXTI 章节

#### 4.2 通信协议
- UART：帧格式、波特率计算、硬件流控、FIFO
- SPI：主从模式、4种CPOL/CPHA、全双工、片选管理
- I2C：7-bit/10-bit地址、ACK/NACK、时钟拉伸、多主仲裁
- **wiki 输出：** `#UART_Protocol.md`, `#SPI_Protocol.md`, `#I2C_Protocol.md`
- **来源：** `$MP157_M4_CubeIDE.md` Ch14/22-23（UART/I2C/SPI）、`$MP157_M4_HAL.md` Ch20/31（UART/I2C）、`$STM32MP157_ReferenceManual.md` USART 章节

#### 4.3 定时器与PWM
- 基本定时器、输入捕获、输出比较、PWM生成、看门狗
- **wiki 输出：** `#Timer_PWM.md`
- **来源：** `$MP157_M4_CubeIDE.md` Ch16-18（基本/通用/高级定时器）、`$MP157_M4_HAL.md` Ch22-25（WWDG/定时器/PWM/互补死区）

#### 4.4 DMA与ADC
- DMA通道/数据流、传输模式、循环模式、ADC基础
- **wiki 输出：** `#DMA_Controller.md`, `#ADC_Basics.md`, `@STM32_Peripherals.md`
- **来源：** `$MP157_M4_CubeIDE.md` Ch19-21（ADC/DAC/DMA）、`$MP157_M4_HAL.md` Ch28-30（DMA/ADC/DAC）、`$STM32MP157_ReferenceManual.md` DMA 章节
- **额外内容：** HAL指南还覆盖 DAC（三角波/正弦波生成）、OLED显示（SSD1306）、DS18B20/DHT11 传感器，可作为选做实验

**实操练习（STM32MP157 M4核心）：**

| 练习 | 内容 | 验证标准 |
|------|------|---------|
| 4-P1 | GPIO输出：直接写MODER/ODR/BSRR控制LED | 串口控制LED开/关 |
| 4-P2 | GPIO输入：读IDR获取按钮状态 | 按钮按下，LED响应 |
| 4-P3 | UART发送：初始化USART寄存器，发送字符串 | 串口终端看到"Hello from M4" |
| 4-P4 | UART接收+中断：收到字符后原样回显 | 串口输入字符，立刻回显 |
| 4-P5 | SPI通信：读取外部器件JEDEC ID | 正确读取厂商ID和设备ID |
| 4-P6 | Timer PWM：产生PWM控制LED亮度 | LED亮度平滑渐变 |
| 4-P7 | DMA传输：内存→UART发送，CPU不参与搬运 | 大量数据发送时CPU占用率低 |

---

### 阶段 5：RTOS + 核间通信

**目标：** 理解RTOS核心概念，体验异构SoC真实工作模式。
**类型：** 理论+实操 | **环境：** FreeRTOS on M4（STM32MP157）
**主要资料：** `$MP157_IPC_RPMSG.md`（异核通信7章）、`$MP157_M4_HAL.md` Ch34（A7+M4联合调试）

#### 5.1 RTOS 基础概念
- 任务状态模型、上下文切换、调度算法、Tick机制
- **wiki 输出：** `#RTOS_Fundamentals.md`
- **来源：** `$FreeRTOS_Documentation.md`（13节：任务管理/调度/队列/信号量/互斥量/事件组/任务通知/软件定时器/内存管理/配置体系/SMP多核）

#### 5.2 同步与通信
- 信号量、互斥锁、优先级继承、消息队列、事件标志组、死锁
- **wiki 输出：** `#RTOS_Synchronization.md`
- **⚠️ 资料缺口：** 同上，需外部资料补充

#### 5.3 内存管理与RTOS内部机制
- 内存分配、栈大小估算、MPU任务隔离、PendSV上下文切换
- **新增：** Zephyr RTOS（DT+Kconfig模型、与Linux技能迁移）
- **新增：** A7↔M4核间通信（RPMSG/共享内存）
- FreeRTOS / Zephyr / RT-Thread 对比
- **wiki 输出：** `#RTOS_MemoryManagement.md`, `#ContextSwitch_CortexM.md`, `!RTOS_Comparison.md`
- **核间通信部分资料充分：** `$MP157_IPC_RPMSG.md` 覆盖 OpenAMP/Virtio/RPMsg/RemoteProc 全栈、IPCC 寄存器、资源表、共享内存分配（SRAM3 0x10040000）、虚拟串口、低功耗唤醒

**实操练习（STM32MP157）：**

| 练习 | 内容 | 验证标准 |
|------|------|---------|
| 5-P1 | FreeRTOS移植到M4：两个任务交替闪烁不同LED | 两个LED独立闪烁 |
| 5-P2 | 信号量同步：Task1产生数据，Task2通过信号量获取处理 | 串口输出结果，无数据丢失 |
| 5-P3 | RPMSG通信：A7 Linux ↔ M4 FreeRTOS互发消息 | `cat /dev/ttyRPMSG0` 收到M4消息 |
| 5-P4 | 综合案例：M4采集数据，通过RPMSG发给A7处理 | Linux实时显示M4数据 |

---

### 阶段 6：Linux设备驱动开发（新增）

**目标：** 掌握Linux驱动开发核心技能。BSP工程师的核心产出是驱动代码。
**类型：** 理论+实操 | **环境：** A7 Linux（WSL2 + 板上）
**主要资料：** `$MP157_Linux_Driver_Guide.md`（59章，系统移植+全外设驱动）

#### 6.1 Linux设备模型
- platform_device / platform_driver
- 设备树匹配（of_match_table）
- 总线-设备-驱动模型、设备属性（sysfs、uevent）
- **wiki 输出：** `#Linux_DeviceModel.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch34-37（设备树基础/中断/Pinctrl/Clock/Regulator/GPIO子系统）

#### 6.2 字符设备驱动
- cdev注册、file_operations
- 用户空间↔内核空间数据交互、ioctl接口、并发控制
- **wiki 输出：** `#CharDevice_Driver.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch20-23（字符设备/LED/按键/中断驱动）

#### 6.3 设备树实战
- DTS语法回顾、pinctrl/clock/regulator/GPIO子系统
- **wiki 输出：** `#DeviceTree_Practice.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch34-37（设备树语法+子系统实战）

#### 6.4 中断与DMA驱动
- request_irq / threaded_irq、上半部/下半部
- DMA API（dma_alloc_coherent、dma_map_sg）
- **wiki 输出：** `#Interrupt_Driver.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch23（中断驱动）、Ch22（并发与竞态）

#### 6.5 IIO子系统与实战
- IIO框架、ADC/传感器驱动模板、buffer与trigger
- 综合实战：从硬件spec到完整驱动
- **wiki 输出：** `#IIO_Framework.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch54（IIO子系统）
- **额外内容：** 资料还覆盖 PWM/INPUT/LCD/PCIe/USB/CAN/WiFi/4G 等 30+ 外设驱动，可按需扩展

**实操练习（STM32MP157 A7 Linux）：**

| 练习 | 内容 | 验证标准 |
|------|------|---------|
| 6-P1 | Hello World内核模块：编写、insmod加载、rmmod卸载 | `dmesg` 显示 "Hello from kernel" |
| 6-P2 | 字符设备驱动：cdev + read/write/ioctl | `echo` 写入成功，`cat` 读回 |
| 6-P3 | 设备树入门：DTS添加自定义节点 | `/proc/device-tree/` 下有对应目录 |
| 6-P4 | platform_driver实战：设备树匹配 + probe | dmesg显示 "probe called" |
| 6-P5 | GPIO LED驱动：设备树+GPIO描述符API+sysfs | `echo 1 > /sys/class/leds/my-led/brightness` LED亮 |
| 6-P6 | 中断驱动：设备树描述按钮+中断处理函数 | dmesg显示 "button pressed" |
| 6-P7 | 综合实战：完整platform driver（GPIO+中断+sysfs） | 全流程跑通 |

---

### 阶段 7：Cortex-A架构与Linux BSP

**目标：** 理解Cortex-A系统架构，掌握BSP开发完整流程。
**类型：** 理论+实操 | **环境：** U-Boot/内核bring-up（STM32MP157）
**主要资料：** `$CortexA7_TRM.md`（MMU/TLB/Cache/Generic Timer/PMU）、`$ARM_GIC_Controller.md`（GICv2完整寄存器）、`$MP157_Linux_Driver_Guide.md` Ch5-19（系统移植）、`$ATK_DLMP157_GettingStarted.md`（交叉编译）

#### 7.1 Cortex-A 系统架构
- 特权级模型（PL0/PL1/PL2）、GIC中断控制器、Cache架构、TrustZone基础
- **wiki 输出：** `#GIC_InterruptController.md`, `#Cache_Architecture.md`, `#TrustZone_Basics.md`
- **来源：** `$CortexA7_TRM.md`（L1/L2 Cache、Generic Timer、PMU）、`$ARM_GIC_Controller.md`（SGI/PPI/SPI、GICD/GICC 寄存器、优先级仲裁、虚拟化）、`$CortexA_ProgrammersGuide.md`（处理器模式、TrustZone）

#### 7.2 启动流程
- Boot ROM → ATF/TF-A → U-Boot → Linux内核 → init
- 内核镜像格式、DTB加载
- **wiki 输出：** `#SoC_BootProcess.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch5（启动详解）/ Ch6-9（TF-A）/ Ch10-13（U-Boot）

#### 7.3 设备树与硬件描述
- DTS/DTB语法、设备树层级结构、pinctrl/clock/regulator子系统
- 内核解析设备树（of_platform_populate）
- **wiki 输出：** `#DeviceTree_Syntax.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch34（设备树语法）、Ch14（U-Boot Kconfig/设备树）

#### 7.4 BSP 开发工作流
- BSP包组成、设备驱动模型、内核移植步骤
- 交叉编译工具链、调试手段（ftrace/eBPF）
- **wiki 输出：** `#BSP_Development.md`
- **来源：** `$MP157_Linux_Driver_Guide.md` Ch15-17（内核Makefile/启动流程/内核移植）、`$ATK_DLMP157_GettingStarted.md` Ch6（交叉编译工具链）
- **⚠️ 资料缺口：** ftrace/eBPF 调试手段需从其他资料补充

**实操练习（STM32MP157）：**

| 练习 | 内容 | 验证标准 |
|------|------|---------|
| 7-P1 | 交叉编译环境搭建 | `arm-linux-gnueabihf-gcc --version` 正常 |
| 7-P2 | 编译Linux内核（STM32MP157 defconfig） | `arch/arm/boot/` 有zImage和dtb |
| 7-P3 | U-Boot编译与启动 | 串口看到U-Boot banner和"Starting kernel..." |
| 7-P4 | 内核bring-up：自编译内核启动 | `uname -a` 显示自编译版本 |
| 7-P5 | 串口调试：排查console无输出/rootfs挂载失败 | 能独立修复启动失败 |
| 7-P6 | ftrace实战：跟踪驱动probe函数调用链 | trace文件显示完整调用图 |

---

### 阶段 8：构建系统与安全（新增）

**目标：** 掌握Yocto/Buildroot构建系统和Secure Boot/OTA。
**类型：** 理论+实操 | **环境：** Yocto/Buildroot（WSL2 + STM32MP157）
**主要资料：** `$Buildroot_UserManual.md`（26章）、`$MP157_Linux_Driver_Guide.md` Ch19（Buildroot构建）

#### 8.1 Yocto Project
- BitBake基础、layer概念、recipe编写
- BSP layer开发、定制image、SDK生成
- **wiki 输出：** `#Yocto_BitBake.md`
- **来源：** `$Yocto_STM32MP1.md`（Yocto 概述 + ST OpenSTLinux 发行版构建 + BSP layer 开发）、`$Bootlin_EmbeddedLinux.md`（Buildroot vs Yocto 对比）

#### 8.2 Buildroot
- 配置系统（menuconfig）、自定义board定义
- 与Yocto对比选型
- **wiki 输出：** `#Buildroot.md`
- **来源：** `$Buildroot_UserManual.md`（26章完整覆盖：入门/配置/使用/定制/软件包开发/调试/贡献）、`$MP157_Linux_Driver_Guide.md` Ch19（Buildroot 根文件系统构建实战）

#### 8.3 Secure Boot与OTA
- ARM TrustZone与Secure Boot链
- Verified Boot（U-Boot FIT image签名）
- OTA框架（SWUpdate/Mender/RAUC）
- **wiki 输出：** `#SecureBoot_OTA.md`
- **⚠️ 资料缺口：** 现有资料不覆盖 Secure Boot/OTA。`$MP157_Linux_Driver_Guide.md` Ch7 提到 TF-A 安全启动验证机制，但无完整 Secure Boot 链教程。需从 ST Wiki 或 Bootlin 课程补充

**实操练习（STM32MP157）：**

| 练习 | 内容 | 验证标准 |
|------|------|---------|
| 8-P1 | Yocto环境搭建：安装依赖、下载poky、配置machine | `bitbake -e` 无报错 |
| 8-P2 | 构建最小镜像：bitbake core-image-minimal | 镜像构建成功，板上启动登录 |
| 8-P3 | 自定义Yocto recipe：编译自己的驱动模块集成到镜像 | 模块随镜像烧录，insmod正常加载 |
| 8-P4 | Buildroot构建：为STM32MP157构建镜像 | 镜像启动成功，能对比两者差异 |
| 8-P5 | Secure Boot签名：U-Boot FIT image签名 | 篡改镜像启动失败，正确签名正常启动 |

---

## 已有页面映射

| 已有页面 | 归入阶段 | 说明 |
|----------|----------|------|
| `$CortexA_ProgrammersGuide.md` | 阶段2（主）、阶段7（参考） | Cortex-A架构主要来源 |
| `$ARMv7M_RefManual.md` | 阶段2（参考）、阶段3（主） | Cortex-M架构主要来源 |
| `@CortexA_Series.md` | 阶段2、阶段7 | Cortex-A型号总览 |
| `@CortexM_Series.md` | 阶段2、阶段5 | Cortex-M型号对比 |
| `#ARM_InstructionSets.md` | 阶段2.2 | 指令集体系 |
| `#CortexA_ProcessorModes.md` | 阶段2.3、阶段7.1 | 处理器模式 |
| `#MMU_VirtualMemory.md` | 阶段2.3、阶段7.1 | 虚拟内存 |
| `#NVIC.md` | 阶段2.4、阶段3.1、阶段5.3 | 中断控制器 |
| `#MPU_CortexM.md` | 阶段2.4、阶段4.1、阶段5.3 | 内存保护 |
| `!CortexA_vs_CortexM.md` | 阶段2.4 | 全面对比 |

---

## 预计新增页面汇总

| 阶段 | 新增页面数 | 页面列表 |
|------|-----------|----------|
| 阶段1 | 5 | `#NumberSystems_Encoding.md`, `#DigitalLogic_Basics.md`, `#EmbeddedC_BitManipulation.md`, `#ComputerArchitecture_Basics.md`, `#Endianness.md` ✅ |
| 阶段2 | 2 | `#ARM_ArchitectureOverview.md`, `#RISC-V_ArchitectureOverview.md` |
| 阶段3 | 6 | `#CortexM_ExceptionModel.md`, `#CortexM_MemoryMap.md`, `#CortexM_SystemControl.md`, `#CortexM_Startup.md`, `#BitBanding.md`, `#JTAG_SWD_Debugging.md` |
| 阶段4 | 8 | `#GPIO_ExternalInterrupts.md`, `#UART_Protocol.md`, `#SPI_Protocol.md`, `#I2C_Protocol.md`, `#Timer_PWM.md`, `#DMA_Controller.md`, `#ADC_Basics.md`, `@STM32_Peripherals.md` |
| 阶段5 | 5 | `#RTOS_Fundamentals.md`, `#RTOS_Synchronization.md`, `#RTOS_MemoryManagement.md`, `#ContextSwitch_CortexM.md`, `!RTOS_Comparison.md` |
| 阶段6 | 5 | `#Linux_DeviceModel.md`, `#CharDevice_Driver.md`, `#DeviceTree_Practice.md`, `#Interrupt_Driver.md`, `#IIO_Framework.md` |
| 阶段7 | 6 | `#GIC_InterruptController.md`, `#Cache_Architecture.md`, `#TrustZone_Basics.md`, `#SoC_BootProcess.md`, `#DeviceTree_Syntax.md`, `#BSP_Development.md` |
| 阶段8 | 3 | `#Yocto_BitBake.md`, `#Buildroot.md`, `#SecureBoot_OTA.md` |
| **合计** | **40** | |

---

## 历史记录

| 日期 | 阶段 | 内容摘要 |
|------|------|----------|
| 2026-05-08 | 初始化 | 创建学习路线，6阶段24节，整合已有13个wiki页面 |
| 2026-05-09 | 阶段1完成 | 嵌入式基础5个概念页面全部完成 |
| 2026-05-17 | 路线升级 | 6阶段→8阶段，新增Linux设备驱动(阶段6)和构建系统与安全(阶段8)；加入STM32MP157开发板实操计划；加入RISC-V概览和Zephyr RTOS；引入双轨制学习（embedded+software单一对话框切换） |
| 2026-05-18 | 阶段2-2.1~2.3 | ARM架构总览（版本号/Profile/授权模式/生态）、指令集体系（ARM/Thumb-2/Interworking/寄存器模型/NEON）、Cortex-A程序员模型（7种模式/Banked寄存器/特权级/SWI系统调用/MMU两级页表/TLB） |
| 2026-05-18 | 阶段2-2.4~2.5 | Cortex-M与A对比（NVIC确定性vs GIC多核、MPU简单vs MMU完整、选型决策树）、RISC-V概览（开源免费/模块化ISA/3级特权/Linux支持） |
| 2026-05-24 | 路线审视 | 基于9个来源摘要审视学习路线：阶段3/4/6资料充分，阶段5缺FreeRTOS原理，阶段7缺ftrace/eBPF，阶段8仅Buildroot有资料（缺Yocto/SecureBoot/OTA）；qmd索引更新至29文件291向量；各阶段补充资料来源标注 |
| 2026-05-24 | 补充资料 | 下载并沉淀3份补充资料：FreeRTOS官方文档（13节，覆盖阶段5缺口）、Yocto/ST指南（覆盖阶段8 Yocto缺口）、Bootlin嵌入式Linux培训（552页，覆盖阶段7-8多项缺口）；PDF原件16个迁移到raw/assets/；qmd索引更新至32文件347向量 |

---

## 资料覆盖度总览（2026-05-24 审视）

基于 9 个来源摘要与学习路线的对比分析。

### 各阶段覆盖情况

| 阶段 | 覆盖度 | 主要来源 | 缺口 |
|------|--------|---------|------|
| 3 | ★★★★☆ | `$CortexM3M4_DefinitiveGuide.md`, `$MP157_M4_CubeIDE.md`, `$MP157_M4_HAL.md` | OpenOCD+GDB 命令行调试 |
| 4 | ★★★★★ | `$MP157_M4_CubeIDE.md`, `$MP157_M4_HAL.md`, `$STM32MP157_ReferenceManual.md` | 无 |
| 5 | ★★★★☆ | `$MP157_IPC_RPMSG.md`（核间通信）、`$FreeRTOS_Documentation.md`（FreeRTOS 原理） | 无 |
| 6 | ★★★★★ | `$MP157_Linux_Driver_Guide.md`（59章） | 无 |
| 7 | ★★★★☆ | `$CortexA7_TRM.md`, `$ARM_GIC_Controller.md`, `$MP157_Linux_Driver_Guide.md` | ftrace/eBPF 调试 |
| 8 | ★★★★☆ | `$Buildroot_UserManual.md`、`$Yocto_STM32MP1.md`、`$Bootlin_EmbeddedLinux.md` | Secure Boot/OTA（仅概要） |

### 资料中的额外内容（未纳入学习计划）

| 来源 | 额外内容 | 建议 |
|------|---------|------|
| `$MP157_M4_CubeIDE.md` | OLED 显示（SSD1306）、AP3216C 光照传感器、DS18B20/DHT11 温湿度传感器、RNG 硬件随机数 | 可作为阶段 4 选做实验 |
| `$MP157_M4_HAL.md` | DAC 波形生成、高级定时器互补输出/死区控制、A7+M4 联合调试（Remoteproc） | DAC/高级定时器可选做；联合调试归入阶段 5 |
| `$ATK_DLMP157_GettingStarted.md` | WiFi Station/SoftAP/Bridge、蓝牙（文件传输/音乐）、4G 模块（pppd/ECM）、CAN FD、OV5640 摄像头、HDMI、OpenGL ES2.0 | 可作为阶段 6 驱动实战的补充素材 |
| `$MP157_IPC_RPMSG.md` | 低功耗模式（6种）、M4 唤醒 A7 流程、IPCC 寄存器详解 | 可扩展为阶段 5 的低功耗专题 |

### 待补充资料

| 缺口 | 建议来源 |
|------|---------|
| Secure Boot/OTA | ST Wiki（STM32MP1 Secure Boot）、SWUpdate/Mender 文档 |
| OpenOCD+GDB | OpenOCD 官方文档 + ARM CoreSight 调试架构 |
| ftrace/eBPF | Linux 内核文档 Documentation/trace/ |

---

最后更新：2026-05-24
