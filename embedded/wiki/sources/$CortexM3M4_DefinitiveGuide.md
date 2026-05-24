---
title: ARM Cortex-M3/M4 处理器权威指南（关键章节）
source: ARM Cortex-M3和Cortex-M4处理器权威指南(第三版).pdf
type: source
tags: [arm, cortex-m3, cortex-m4, nvic, mpu, debug, low-power, exception]
created: 2026-05-24
---

# ARM Cortex-M3/M4 处理器权威指南 — 来源摘要

> **本摘要仅覆盖与嵌入式学习路线阶段3相关的关键章节。**
> 原书共24章+9个附录（1055页），本摘要覆盖以下6个核心主题：
> - Chapter 4: Architecture（架构）
> - Chapter 6: Memory System（内存系统）
> - Chapter 7: Exceptions and Interrupts（异常与中断）
> - Chapter 9: Low Power and System Control Features（低功耗与系统控制）
> - Chapter 11: Memory Protection Unit (MPU)（内存保护单元）
> - Chapter 14: Debug and Trace Features（调试与追踪）

---

## 1. 处理器架构概述

### 1.1 架构版本

Cortex-M3 和 Cortex-M4 基于 **ARMv7-M** 架构。Cortex-M4 扩展了额外指令（如 SIMD/DSP），扩展版本称为 **ARMv7E-M**。

### 1.2 操作模式与状态

**操作状态（Operation States）：**
- **Thumb 状态**：执行 Thumb 指令时处于此状态。Cortex-M 不支持 ARM 指令集。
- **Debug 状态**：处理器被调试器暂停时进入此状态。

**操作模式（Operation Modes）：**
- **Thread 模式**：执行普通应用代码。可以是特权级或非特权级，由 CONTROL 寄存器控制。
- **Handler 模式**：执行异常处理器（如 ISR）。始终处于特权级。

**访问级别：**
- **特权级（Privileged）**：可访问所有资源，包括 NVIC 寄存器。
- **非特权级（Unprivileged）**：部分内存区域不可访问，部分操作受限。

默认启动状态：**特权级 Thread 模式 + Thumb 状态**。

### 1.3 内存映射

4GB 地址空间划分为以下区域：

| 区域 | 地址范围 | 用途 |
|------|----------|------|
| CODE | 0x00000000 - 0x1FFFFFFF (512MB) | 程序代码，包含默认向量表 |
| SRAM | 0x20000000 - 0x3FFFFFFF (512MB) | 数据存储（如 SRAM），前 1MB 支持 bit-band |
| Peripherals | 0x40000000 - 0x5FFFFFFF (512MB) | 外设寄存器，前 1MB 支持 bit-band |
| External RAM | 0x60000000 - 0x9FFFFFFF (1GB) | 外部 RAM |
| External Device | 0xA0000000 - 0xDFFFFFFF (1GB) | 外部设备 |
| PPB | 0xE0000000 - 0xE00FFFFF | 私有外设总线（NVIC、调试组件等） |
| SCS | 0xE000E000 - 0xE000EFFF | 系统控制空间（NVIC、SysTick、MPU、SCB） |

### 1.4 Bit-Band 操作

支持对单个比特进行原子读写操作。两个 bit-band 区域：
- **SRAM bit-band**：0x20000000-0x200FFFFF -> 别名 0x22000000-0x23FFFFFC
- **Peripheral bit-band**：0x40000000-0x400FFFFF -> 别名 0x42000000-0x43FFFFFC

**地址计算公式**：
```
bit_band_alias = (region_base & 0xF0000000) + 0x02000000 + ((region_base & 0xFFFFF) << 5) + (bit_number << 2)
```

**核心优势**：操作是原子的（READ-MODIFY-WRITE 在硬件级别完成），可避免中断或多任务环境下的竞态条件。

### 1.5 复位序列

复位后处理器自动执行：
1. 从地址 0x00000000 读取第一个字 -> 设置 MSP（主堆栈指针）
2. 从地址 0x00000004 读取第二个字 -> 设置 PC（复位向量）

三种复位类型：
- **Power-on Reset**：复位所有（包括调试组件）
- **System Reset**：复位处理器和外设，不复位调试组件
- **Processor Reset**：仅复位处理器

---

## 2. 编程模型

### 2.1 寄存器组（Register Bank）

16 个 32 位寄存器：

| 寄存器 | 名称 | 说明 |
|--------|------|------|
| R0-R7 | Low Registers | 通用寄存器，16 位和 32 位指令均可访问 |
| R8-R12 | High Registers | 通用寄存器，主要由 32 位指令访问 |
| R13 | SP (Stack Pointer) | 堆栈指针，物理上有两个：MSP 和 PSP |
| R14 | LR (Link Register) | 链接寄存器，保存函数调用返回地址 |
| R15 | PC (Program Counter) | 程序计数器，读取返回当前指令地址+4 |

**双堆栈指针：**
- **MSP（Main Stack Pointer）**：默认堆栈指针，复位后使用，Handler 模式始终使用 MSP
- **PSP（Process Stack Pointer）**：仅在 Thread 模式可用，通常用于嵌入式 OS 的任务栈

选择由 CONTROL 寄存器的 SPSEL 位控制。

### 2.2 特殊寄存器

**程序状态寄存器（PSR）** 由三部分组成，可合并访问（xPSR）：

| 寄存器 | 位域 | 说明 |
|--------|------|------|
| APSR | N (bit 31) | 负数标志 |
| APSR | Z (bit 30) | 零标志 |
| APSR | C (bit 29) | 进位/借位标志 |
| APSR | V (bit 28) | 溢出标志 |
| APSR | Q (bit 27) | 饱和标志（粘滞） |
| APSR | GE[3:0] | 大于等于标志（仅 Cortex-M4） |
| IPSR | [4:0] | 当前异常编号（只读） |
| EPSR | T (bit 24) | Thumb 状态（始终为 1） |
| EPSR | ICI/IT | 中断可继续指令 / IF-THEN 状态 |

**中断屏蔽寄存器（仅特权级可访问）：**

| 寄存器 | 位宽 | 功能 |
|--------|------|------|
| PRIMASK | 1 bit | 置 1 屏蔽所有异常（NMI 和 HardFault 除外），等效于将优先级提升到 0 |
| FAULTMASK | 1 bit | 置 1 屏蔽所有异常（NMI 除外），等效于将优先级提升到 -1，异常返回时自动清零 |
| BASEPRI | 3-8 bit | 屏蔽指定优先级及以下的异常，写 0 禁用 |

**CMSIS-Core 访问函数：**
```c
__get_PRIMASK() / __set_PRIMASK(x)
__get_FAULTMASK() / __set_FAULTMASK(x)
__get_BASEPRI() / __set_BASEPRI(x)
__disable_irq()  // 设置 PRIMASK
__enable_irq()   // 清除 PRIMASK
```

**汇编访问：**
```asm
MRS r0, PRIMASK      ; 读取
MSR PRIMASK, r0      ; 写入
CPSIE i              ; 清除 PRIMASK（使能中断）
CPSID i              ; 设置 PRIMASK（禁止中断）
```

### 2.3 CONTROL 寄存器

| 位 | 名称 | 说明 |
|----|------|------|
| 0 | nPRIV | 0 = Thread 模式特权级（默认），1 = Thread 模式非特权级 |
| 1 | SPSEL | 0 = Thread 模式使用 MSP（默认），1 = Thread 模式使用 PSP |
| 2 | FPCA | 浮点上下文活跃（仅 Cortex-M4 FPU），执行浮点指令时自动置位 |

**常见组合：**

| nPRIV | SPSEL | 用途 |
|-------|-------|------|
| 0 | 0 | 简单应用，全程使用 MSP |
| 0 | 1 | 有 OS，当前任务特权级，使用 PSP |
| 1 | 1 | 有 OS，当前任务非特权级，使用 PSP |

**CMSIS-Core 访问：**
```c
__get_CONTROL() / __set_CONTROL(x)
```

### 2.4 堆栈模型

- **Full-descending 堆栈**：SP 先递减再存储（PUSH），先读取再递增（POP）
- PUSH/POP 始终 32 位对齐，SP 最低 2 位始终为 0
- 复位后 MSP 初始值从向量表地址 0x00000000 读取

---

## 3. 异常和中断

### 3.1 异常类型总览

| 异常编号 | 类型 | 优先级 | 说明 |
|----------|------|--------|------|
| 1 | Reset | -3（最高） | 复位 |
| 2 | NMI | -2 | 不可屏蔽中断 |
| 3 | HardFault | -1 | 所有未使能的 fault 汇总 |
| 4 | MemManage | 可编程 | MPU 违规或从不可执行区域取指 |
| 5 | BusFault | 可编程 | 总线错误响应 |
| 6 | UsageFault | 可编程 | 无效指令或非法状态转换 |
| 11 | SVC | 可编程 | Supervisor Call，OS 系统调用 |
| 12 | Debug Monitor | 可编程 | 软件调试事件 |
| 14 | PendSV | 可编程 | 可挂起的系统调用，用于 OS 上下文切换 |
| 15 | SysTick | 可编程 | 系统滴答定时器 |
| 16-255 | IRQ #0-#239 | 可编程 | 外部中断（实际数量由芯片设计决定） |

### 3.2 NVIC（嵌套向量中断控制器）

**核心特性：**
- 支持最多 240 个 IRQ 输入
- 每个中断可独立使能/禁止
- 支持脉冲触发和电平触发中断
- 自动嵌套中断支持（高优先级可抢占低优先级）
- 向量化异常入口（硬件自动从向量表获取处理程序地址）
- 中断延迟仅 12 个时钟周期

**NVIC 寄存器（位于 SCS 0xE000E000）：**

| 地址 | 寄存器 | CMSIS 符号 | 功能 |
|------|--------|------------|------|
| 0xE000E100-E11C | ISER[0-7] | NVIC->ISER[n] | 中断使能置位（写 1 使能，写 0 无效） |
| 0xE000E180-E19C | ICER[0-7] | NVIC->ICER[n] | 中断使能清除（写 1 禁止，写 0 无效） |
| 0xE000E200-E21C | ISPR[0-7] | NVIC->ISPR[n] | 中断挂起置位 |
| 0xE000E280-E29C | ICPR[0-7] | NVIC->ICPR[n] | 中断挂起清除 |
| 0xE000E300-E31C | IABR[0-7] | NVIC->IABR[n] | 中断活跃状态（只读） |
| 0xE000E400-E4EF | IP[0-239] | NVIC->IP[n] | 中断优先级（8 位宽） |
| 0xE000EF00 | STIR | NVIC->STIR | 软件触发中断（写入中断编号） |

**CMSIS-Core 常用函数：**
```c
NVIC_EnableIRQ(IRQn)           // 使能中断
NVIC_DisableIRQ(IRQn)          // 禁止中断
NVIC_SetPendingIRQ(IRQn)       // 设置挂起
NVIC_ClearPendingIRQ(IRQn)     // 清除挂起
NVIC_SetPriority(IRQn, prio)   // 设置优先级
NVIC_GetPriority(IRQn)         // 获取优先级
NVIC_SetPriorityGrouping(grp)  // 设置优先级分组
```

### 3.3 优先级机制

**优先级寄存器宽度**：3-8 位（由芯片设计者决定，大多数为 3 位或 4 位）

- 未实现的低位始终读为 0，写入忽略
- 数值越小优先级越高
- 复位后所有中断优先级为 0（最高可编程优先级）

**优先级分组（Priority Grouping）**：

8 位优先级寄存器分为两部分：**组优先级（Group/Pre-empt）** + **子优先级（Sub-priority）**

通过 SCB->AIRCR 的 PRIGROUP 字段配置：

| PRIGROUP | 组优先级位 | 子优先级位 | 最大抢占级数 |
|----------|-----------|-----------|-------------|
| 0 (默认) | [7:1] | [0] | 128 |
| 1 | [7:2] | [1:0] | 64 |
| 2 | [7:3] | [2:0] | 32 |
| 3 | [7:4] | [3:0] | 16 |
| 4 | [7:5] | [4:0] | 8 |
| 5 | [7:6] | [5:0] | 4 |
| 6 | [7] | [6:0] | 2 |
| 7 | 无 | [7:0] | 0（无抢占） |

**仲裁规则**：
1. 组优先级高者优先
2. 组优先级相同时，子优先级高者优先
3. 都相同时，异常编号小者优先

### 3.4 向量表与向量表重定位

**向量表结构：**

| 地址 | 内容 |
|------|------|
| 0x00000000 | MSP 初始值 |
| 0x00000004 | Reset 向量 |
| 0x00000008 | NMI 向量 |
| 0x0000000C | HardFault 向量 |
| ... | ... |
| 0x00000040 | IRQ #0 向量 |
| 0x00000044 | IRQ #1 向量 |

每个向量的 LSB 必须置 1（表示 Thumb 状态）。

**向量表偏移寄存器（VTOR）**：地址 0xE000ED08

| 位域 | 说明 |
|------|------|
| [31:7] | TBLOFF：向量表偏移值（必须对齐到向量表大小扩展到 2 的幂） |

```c
SCB->VTOR = 0x20000000;  // 将向量表重定位到 SRAM 起始地址
```

### 3.5 SCB 关键寄存器

**中断控制和状态寄存器（ICSR）**：地址 0xE000ED04

| 位 | 名称 | 说明 |
|----|------|------|
| 31 | NMIPENDSET | 写 1 挂起 NMI |
| 28 | PENDSVSET | 写 1 挂起 PendSV |
| 27 | PENDSVCLR | 写 1 清除 PendSV 挂起 |
| 26 | PENDSTSET | 写 1 挂起 SysTick |
| 25 | PENDSTCLR | 写 1 清除 SysTick 挂起 |
| 9:0 | VECTACTIVE | 当前正在执行的 ISR 编号 |

**应用中断和复位控制寄存器（AIRCR）**：地址 0xE000ED0C

| 位 | 名称 | 说明 |
|----|------|------|
| 31:16 | VECTKEY | 写入时必须为 0x05FA，否则写入被忽略 |
| 15 | ENDIANNESS | 数据端序（只读，0=小端，1=大端） |
| 10:8 | PRIGROUP | 优先级分组 |
| 2 | SYSRESETREQ | 写 1 请求系统复位 |
| 1 | VECTCLRACTIVE | 清除所有异常活跃状态（调试用） |
| 0 | VECTRESET | 复位处理器（不含调试逻辑，调试用） |

**系统处理程序优先级寄存器（SHP[0-11]）**：地址 0xE000ED18-0xE000ED23

| 地址 | 名称 | 对应异常 |
|------|------|----------|
| 0xE000ED18 | SHP[0] | MemManage 优先级 |
| 0xE000ED19 | SHP[1] | BusFault 优先级 |
| 0xE000ED1A | SHP[2] | UsageFault 优先级 |
| 0xE000ED1F | SHP[7] | SVC 优先级 |
| 0xE000ED20 | SHP[8] | Debug Monitor 优先级 |
| 0xE000ED22 | SHP[10] | PendSV 优先级 |
| 0xE000ED23 | SHP[11] | SysTick 优先级 |

**系统处理程序控制和状态寄存器（SHCSR）**：地址 0xE000ED24

| 位 | 名称 | 说明 |
|----|------|------|
| 18 | USGFAULTENA | UsageFault 处理程序使能 |
| 17 | BUSFAULTENA | BusFault 处理程序使能 |
| 16 | MEMFAULTENA | MemManage 处理程序使能 |

使能 fault 处理程序示例：
```c
SCB->SHCSR |= (1 << 17);  // 使能 BusFault
```

### 3.6 中断配置流程

```c
// 1. 设置优先级（可选）
NVIC_SetPriority(IRQn, priority);

// 2. 在外设中使能中断
Peripheral->CR |= INTERRUPT_ENABLE_BIT;

// 3. 在 NVIC 中使能中断
NVIC_EnableIRQ(IRQn);
```

---

## 4. 低功耗特性

### 4.1 睡眠模式

Cortex-M3/M4 支持两种睡眠模式：

| 模式 | 进入指令 | 说明 |
|------|----------|------|
| Sleep | WFI / WFE | 停止处理器时钟，外设时钟可选停止 |
| Deep Sleep | WFI / WFE + SLEEPDEEP=1 | 更深层次的省电，可关闭更多时钟/电源 |

**系统控制寄存器（SCR）**：地址 0xE000ED10

| 位 | 名称 | 说明 |
|----|------|------|
| 4 | SEVONPEND | 置 1 时，新挂起的中断（无论是否使能）可从 WFE 唤醒 |
| 2 | SLEEPDEEP | 置 1 选择 Deep Sleep 模式 |
| 1 | SLEEPONEXIT | 置 1 时，从异常处理程序返回 Thread 模式时自动进入睡眠 |

### 4.2 WFI 与 WFE

| 指令 | CMSIS 函数 | 唤醒条件 |
|------|-----------|----------|
| WFI | `__WFI()` | 中断请求（需满足优先级条件）、调试请求、复位 |
| WFE | `__WFE()` | 中断请求、事件输入（RXEV）、SEV 指令、调试请求、复位 |

**WFI 唤醒条件**：中断必须使能且优先级高于当前级别（考虑 PRIMASK/BASEPRI）。

**WFE 特殊机制**：
- 处器内部有一个单比特事件寄存器
- 如果事件寄存器已置位，WFE 仅清除该寄存器而不进入睡眠
- 事件寄存器可由：异常入口/出口、SEV 指令、RXEV 信号、调试事件设置

### 4.3 Sleep-On-Exit

设置 SCR.SLEEPONEXIT = 1 后，处理器从最后一个异常处理程序返回 Thread 模式时自动进入睡眠。适用于中断驱动型应用，避免不必要的 Thread 模式执行。

### 4.4 SysTick 定时器

24 位倒计数定时器，内置于处理器中，地址 0xE000E010-0xE000E01C。

| 寄存器 | 地址 | 说明 |
|--------|------|------|
| SysTick->CTRL | 0xE000E010 | 控制和状态寄存器 |
| SysTick->LOAD | 0xE000E014 | 重载值（24 位） |
| SysTick->VAL | 0xE000E018 | 当前值（写任意值清零） |
| SysTick->CALIB | 0xE000E01C | 校准值（只读） |

**CTRL 寄存器位域：**
- bit 16: COUNTFLAG（计数到 0 时置 1，读后清零）
- bit 2: CLKSOURCE（0=外部时钟，1=处理器时钟）
- bit 1: TICKINT（置 1 使能 SysTick 异常）
- bit 0: ENABLE（置 1 使能定时器）

### 4.5 低功耗设计要点

1. **降低活跃功耗**：选择合适时钟频率、关闭未使用时钟、从 SRAM 执行代码
2. **减少活跃周期**：利用睡眠模式、中断驱动设计
3. **降低睡眠功耗**：使用 Deep Sleep、关闭 Flash、利用电源门控

---

## 5. 调试特性

### 5.1 调试接口

| 协议 | 引脚 | 说明 |
|------|------|------|
| JTAG | TCK, TDI, TMS, TDO (4pin) + nTRST (可选) | IEEE 1149.1 标准，支持菊花链 |
| Serial Wire (SWD) | SWCLK, SWDIO (2pin) | ARM 专有协议，引脚更少，支持奇偶校验 |

两种协议共享引脚：TCK = SWCLK, TMS = SWDIO。可通过特殊位模式动态切换。

### 5.2 调试模式

| 模式 | 说明 | 特点 |
|------|------|------|
| Halt 模式 | 处理器完全停止 | SysTick 停止、支持单步、可通过 DHCSR.C_DEBUGEN 启用 |
| Debug Monitor 模式 | 执行 Debug Monitor 异常处理程序 | SysTick 继续运行、高优先级中断仍可执行、需要通信外设 |

**Debug Halting Control and Status Register (DHCSR)**：地址 0xE000EDF0
- C_DEBUGEN (bit 0): 使能 Halt 模式调试（仅调试器可写）
- C_HALT (bit 1): 手动暂停处理器

**Debug Exception and Monitor Control Register (DEMCR)**：地址 0xE000EDFC
- VC_CORERESET: 复位时向量捕获
- VC_HARDERR: HardFault 时向量捕获
- MON_EN: Debug Monitor 使能

### 5.3 断点与观察点

| 类型 | 数量 | 说明 |
|------|------|------|
| 硬件断点（FPB） | 最多 8 个（6 个指令地址 + 2 个字面量地址） | Flash Patch and Breakpoint 单元 |
| 软件断点（BKPT） | 无限 | BKPT 指令（编码 0xBExx） |
| 硬件观察点（DWT） | 最多 4 个 | Data Watchpoint and Trace 单元 |

### 5.4 CoreSight 调试架构

**调试连接层次：**
```
调试主机(PC) -> USB -> 调试适配器 -> SWD/JTAG -> SWJ-DP (Debug Port)
  -> 内部调试总线 -> AHB-AP (Access Port) -> 处理器内部总线
```

**关键组件：**

| 组件 | 说明 |
|------|------|
| SWJ-DP | Serial Wire JTAG Debug Port，支持 SWD 和 JTAG |
| AHB-AP | AHB Access Port，将调试命令转换为内存访问 |
| FPB | Flash Patch and Breakpoint，断点和 Flash 补丁 |
| DWT | Data Watchpoint and Trace，观察点、数据追踪、性能分析 |
| ITM | Instrumentation Trace Macrocell，软件追踪（printf 等） |
| ETM | Embedded Trace Macrocell，指令追踪（可选） |
| TPIU | Trace Port Interface Unit，追踪数据输出 |
| ROM Table | 调试组件地址查找表 |

### 5.5 追踪接口

| 模式 | 引脚 | 带宽 | 说明 |
|------|------|------|------|
| SWV (Serial Wire Viewer) | SWO (1 pin) | ~2Mbit/s | 低引脚数，与 TDO 共享 |
| Trace Port | TRACECLK + TRACEDATA[0:3] (5 pin) | 高 | 支持指令追踪（需 ETM） |

**SWV 可输出的信息：**
- 异常事件
- 数据观察点事件
- 性能计数器
- 软件生成的追踪数据（ITM）
- 时间戳

---

## 6. MPU（内存保护单元）

### 6.1 概述

MPU 是可选组件，用于定义内存区域的访问权限和属性。

**核心功能：**
- 最多 8 个可编程区域，每个有独立的基地址、大小和属性
- 支持背景区域（Region -1）
- 违规访问触发 MemManage 或 HardFault 异常

**MPU 类型寄存器**：地址 0xE000ED90
- DREGION (bit [15:8]): 支持的区域数（0 = 无 MPU，8 = 有 MPU）

### 6.2 MPU 寄存器

| 地址 | 寄存器 | CMSIS 符号 | 功能 |
|------|--------|------------|------|
| 0xE000ED90 | TYPE | MPU->TYPE | MPU 类型信息 |
| 0xE000ED94 | CTRL | MPU->CTRL | 使能和背景区域控制 |
| 0xE000ED98 | RNR | MPU->RNR | 选择要配置的区域编号 |
| 0xE000ED9C | RBAR | MPU->RBAR | 区域基地址 |
| 0xE000EDA0 | RASR | MPU->RASR | 区域属性和大小 |

**MPU 控制寄存器（CTRL）**：

| 位 | 名称 | 说明 |
|----|------|------|
| 2 | PRIVDEFENA | 置 1 时，特权级访问可使用默认内存映射作为背景区域 |
| 1 | HFNMIENA | 置 1 时，HardFault/NMI 处理程序中 MPU 也生效 |
| 0 | ENABLE | MPU 使能 |

**MPU 区域基地址寄存器（RBAR）**：

| 位 | 名称 | 说明 |
|----|------|------|
| 31:N | ADDR | 区域基地址（N 取决于区域大小） |
| 4 | VALID | 置 1 时使用 REGION 字段而非 RNR |
| 3:0 | REGION | 区域编号覆盖 |

**MPU 区域属性和大小寄存器（RASR）**：

| 位 | 名称 | 说明 |
|----|------|------|
| 28 | XN | 置 1 禁止从该区域取指执行 |
| 26:24 | AP | 数据访问权限 |
| 21:19 | TEX | 类型扩展字段 |
| 18 | S | 可共享 |
| 17 | C | 可缓存 |
| 16 | B | 可缓冲 |
| 15:8 | SRD | 子区域禁用 |
| 5:1 | REGION SIZE | 区域大小编码 |
| 0 | ENABLE | 区域使能 |

**AP 字段编码：**

| AP 值 | 特权级访问 | 用户级访问 | 说明 |
|--------|-----------|-----------|------|
| 000 | 无 | 无 | 无访问 |
| 001 | 读/写 | 无 | 仅特权级 |
| 010 | 读/写 | 只读 | 用户级不可写 |
| 011 | 读/写 | 读/写 | 完全访问 |
| 101 | 只读 | 无 | 仅特权级只读 |
| 110 | 只读 | 只读 | 只读 |

**REGION SIZE 编码：**

| 编码 | 大小 | 编码 | 大小 |
|------|------|------|------|
| b00100 | 32 B | b10000 | 128 KB |
| b00101 | 64 B | b10001 | 256 KB |
| b00110 | 128 B | b10010 | 512 KB |
| b00111 | 256 B | b10011 | 1 MB |
| b01000 | 512 B | b10100 | 2 MB |
| b01001 | 1 KB | b10101 | 4 MB |
| b01010 | 2 KB | b10110 | 8 MB |
| b01011 | 4 KB | b10111 | 16 MB |
| b01100 | 8 KB | b11000 | 32 MB |
| b01101 | 16 KB | b11001 | 64 MB |
| b01110 | 32 KB | b11010 | 128 MB |
| b01111 | 64 KB | b11011 | 256 MB |

### 6.3 内存属性（TEX/S/C/B）

| TEX | C | B | 内存类型 | 可共享性 |
|-----|---|---|----------|----------|
| 000 | 0 | 0 | 强序（Strongly Ordered） | 可共享 |
| 000 | 0 | 1 | 共享设备（Shared Device） | 可共享 |
| 000 | 1 | 0 | 写透（Write Through） | 由 S 位决定 |
| 000 | 1 | 1 | 写回（Write Back） | 由 S 位决定 |
| 001 | 0 | 0 | 非缓存（Non-cacheable） | 由 S 位决定 |
| 001 | 1 | 1 | 写回，读写分配 | 由 S 位决定 |
| 010 | 0 | 0 | 非共享设备（Non-shared Device） | 不共享 |

**常用配置：**

| 用途 | TEX | S | C | B |
|------|-----|---|---|---|
| Flash/ROM | 000 | 0 | 1 | 0 |
| 内部 SRAM | 000 | 1 | 1 | 0 |
| 外部 RAM | 000 | 1 | 1 | 1 |
| 外设 | 000 | 1 | 0 | 1 |

### 6.4 MPU 配置流程

```c
// 1. 禁用 MPU（配置期间）
MPU->CTRL = 0;

// 2. 选择区域
MPU->RNR = 0;  // 区域 0

// 3. 设置基地址
MPU->RBAR = 0x20000000;

// 4. 设置属性和大小
MPU->RASR = (1 << 0)    // ENABLE
          | (0b01011 << 1)  // 4KB 区域
          | (0b011 << 24)   // AP = 完全访问
          | (0b000 << 19)   // TEX
          | (1 << 18)       // S = 可共享
          | (1 << 17)       // C = 可缓存
          | (0 << 16);      // B = 非缓冲

// 5. 使能 MPU
MPU->CTRL = (1 << 0)     // ENABLE
          | (1 << 2);     // PRIVDEFENA（特权级使用背景区域）

// 6. 内存屏障
__DSB();
__ISB();
```

### 6.5 子区域禁用（SRD）

RASR 的 SRD 字段（bit [15:8]）将区域分为 8 个等分子区域，每个子区域可独立禁用。
- 子区域大小 = 区域大小 / 8
- 区域大小必须大于 128 字节才能使用子区域
- 禁用的子区域如与其他区域重叠，使用其他区域的规则；否则触发 MemManage fault

### 6.6 区域重叠规则

当一个地址落入多个已编程区域时，使用**编号最高**的区域的设置。
例如：地址同时在 Region 1 和 Region 4 中 -> 使用 Region 4 的设置。

---

## 附录：关键寄存器地址速查

| 地址 | 寄存器 | 说明 |
|------|--------|------|
| 0xE000E000 | NVIC 基地址 | 中断控制器 |
| 0xE000E004 | ICTR | 中断控制器类型 |
| 0xE000E010-0x1C | SysTick | 系统滴答定时器 |
| 0xE000ED00 | SCB->CPUID | 处理器 ID |
| 0xE000ED04 | SCB->ICSR | 中断控制和状态 |
| 0xE000ED08 | SCB->VTOR | 向量表偏移 |
| 0xE000ED0C | SCB->AIRCR | 应用中断和复位控制 |
| 0xE000ED10 | SCB->SCR | 系统控制（睡眠模式） |
| 0xE000ED14 | SCB->CCR | 配置控制 |
| 0xE000ED18-0x23 | SCB->SHP[0-11] | 系统异常优先级 |
| 0xE000ED24 | SCB->SHCSR | 系统处理程序控制和状态 |
| 0xE000ED88 | SCB->CPACR | 协处理器访问控制（FPU 使能） |
| 0xE000ED90-0xB8 | MPU | 内存保护单元寄存器 |
| 0xE000EDF0 | DHCSR | 调试暂停控制和状态 |
| 0xE000EDFC | DEMCR | 调试异常和监控控制 |

---

## 关联 wiki 页面

- [[#EmbeddedC_BitManipulation]] — 位操作基础（与 bit-band 操作相关）
- [[#NumberSystems_Encoding]] — 数的表示与编码（与 PSR 标志位相关）
- [[#ComputerArchitecture_Basics]] — 计算机体系结构基础（与内存映射相关）
- [[#DigitalLogic_Basics]] — 数字逻辑基础（与 NVIC 硬件相关）
- [[#Endianness]] — 字节序（与内存端序配置相关）
