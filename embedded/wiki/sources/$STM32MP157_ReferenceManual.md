---
title: STM32MP157 参考手册（关键章节）
source: STM32MP157参考手册.pdf
type: source
tags: [stm32mp157, rcc, gpio, usart, exti, dma, pwr, syscfg, reference-manual]
created: 2026-05-24
---

# STM32MP157 参考手册（关键章节摘要）

> **文档标识**: RM0436 Rev 4, 2020年2月
> **芯片**: STM32MP157 (Cortex-A7 + Cortex-M4 双核异构)
> **总页数**: 4018页
> **本摘要仅覆盖以下关键章节**，不包含完整手册内容。

---

## 1. 时钟树（RCC，第10章，p501-879）

### 1.1 RCC 概述

RCC 负责整个芯片的时钟和复位管理。主要特征：

- AHB-Lite 总线接口，支持 TrustZone
- **4个独立 PLL**（PLL1-PLL4），支持整数/分数模式、扩频功能
- **2个外部振荡器**：HSE（8-48 MHz）、LSE（32.768 kHz）
- **3个内部振荡器**：HSI（~64 MHz）、CSI（~4 MHz）、LSI（~32 kHz）
- 智能时钟门控降低功耗
- 2个中断线：时钟安全系统专用 + 通用

### 1.2 时钟路径架构

```
PLL1 → MPU 时钟 (mpuss_ck)
PLL2 → AXI子系统 + DDR + GPU (axiss_ck)
PLL3 → MCU子系统 + 外设内核时钟 (mcuss_ck)
PLL4 → 外设内核时钟
```

**4条主要时钟路径**：
- MPU 时钟路径
- AXI子系统时钟路径（含DDR接口）
- MCU 及其总线矩阵时钟路径
- 外设内核时钟路径

### 1.3 关键 PLL 寄存器

| 寄存器 | 功能 |
|--------|------|
| `RCC_PLL1CR` | PLL1 控制（使能、就绪标志） |
| `RCC_PLL1CFGR1` | PLL1 配置1（DIVM、DIVN 分频系数） |
| `RCC_PLL1CFGR2` | PLL1 配置2（DIVP、DIVQ、DIVR 分频系数） |
| `RCC_PLL1FRACR` | PLL1 分数分频 |
| `RCC_PLL2CR/CFGR1/CFGR2/FRACR` | PLL2 同结构 |
| `RCC_PLL3CR/CFGR1/CFGR2/FRACR` | PLL3 同结构 |
| `RCC_PLL4CR/CFGR1/CFGR2/FRACR` | PLL4 同结构 |

**PLL 配置步骤**：
1. 选择参考时钟源：`RCC_RCK12SELR`（PLL1/2）、`RCC_RCK3SELR`（PLL3）、`RCC_RCK4SELR`（PLL4）
2. 设置 DIVM 分频器：`RCC_PLLxCFGR1` 的 DIVMx[5:0]
3. 设置 VCO 倍频系数：`RCC_PLLxCFGR1` 的 DIVNx[8:0]
4. 设置输出分频：`RCC_PLLxCFGR2` 的 DIVPx[6:0]、DIVQx[6:0]、DIVRx[6:0]
5. 使能 PLL：`RCC_PLLxCR` 的 PLLON 位
6. 等待就绪：`RCC_PLLxCR` 的 PLLRDY 位

### 1.4 时钟分频器寄存器

| 寄存器 | 功能 |
|--------|------|
| `RCC_MPCKSELR` | MPU 时钟源选择 |
| `RCC_MPCKDIVR` | MPU 时钟分频 |
| `RCC_ASSCKSELR` | AXI子系统时钟源选择 |
| `RCC_AXIDIVR` | AXI 时钟分频 |
| `RCC_MSSCKSELR` | MCU子系统时钟源选择 |
| `RCC_MCUDIVR` | MCU 时钟分频 |
| `RCC_APB1DIVR` | APB1 分频 |
| `RCC_APB2DIVR` | APB2 分频 |
| `RCC_APB3DIVR` | APB3 分频 |
| `RCC_APB4DIVR` | APB4 分频 |
| `RCC_APB5DIVR` | APB5 分频 |
| `RCC_RTCDIVR` | RTC 时钟分频 |

### 1.5 外设内核时钟选择寄存器

每个外设有独立的内核时钟选择寄存器，格式为 `RCC_<外设>CKSELR`：

| 寄存器 | 外设 |
|--------|------|
| `RCC_UART1CKSELR` | USART1 |
| `RCC_UART24CKSELR` | UART2/4 |
| `RCC_UART35CKSELR` | UART3/5 |
| `RCC_UART6CKSELR` | USART6 |
| `RCC_UART78CKSELR` | UART7/8 |
| `RCC_I2C12CKSELR` | I2C1/2 |
| `RCC_SPI2S1CKSELR` | SPI/I2S1 |
| `RCC_SPI2S23CKSELR` | SPI/I2S2/3 |
| `RCC_ETHCKSELR` | Ethernet |
| `RCC_USBCKSELR` | USB |
| `RCC_SDMMC12CKSELR` | SDMMC1/2 |

### 1.6 外设时钟使能寄存器

分两组：**MPU使能** 和 **MCU使能**，使用 Set/Clear 寄存器对：

- `RCC_MP_APBxENSETR` / `RCC_MP_APBxENCLRR`（MPU 访问）
- `RCC_MC_APBxENSETR` / `RCC_MC_APBxENCLRR`（MCU 访问）
- `RCC_MP_AHBxENSETR` / `RCC_MP_AHBxENCLRR`（MPU 访问）
- `RCC_MC_AHBxENSETR` / `RCC_MC_AHBxENCLRR`（MCU 访问）

**低功耗模式下时钟使能**（Sleep clock enable）：
- `RCC_MP_APBxLPENSETR` / `RCC_MP_APBxLPENCLRR`

### 1.7 复位寄存器

- `RCC_APBxRSTSETR` / `RCC_APBxRSTCLRR`：APB 外设复位
- `RCC_AHBxRSTSETR` / `RCC_AHBxRSTCLRR`：AHB 外设复位
- `RCC_MP_GRSTCSETR`：全局复位控制（MPSYSRST、MCURST、MPUP0RST、MPUP1RST）

### 1.8 时钟安全系统（CSS）

- HSE CSS：检测 HSE 故障，可触发系统复位（hcss_rst）
- LSE CSS：检测 LSE 故障
- 中断寄存器：`RCC_MP_CIER`、`RCC_MP_CIFR`

---

## 2. GPIO（第13章，p1061-1087）

### 2.1 GPIO 概述

每个 GPIO 端口有以下寄存器（每个32位）：

| 寄存器 | 功能 |
|--------|------|
| `GPIOx_MODER` | 模式选择（输入/输出/复用/模拟） |
| `GPIOx_OTYPER` | 输出类型（推挽/开漏） |
| `GPIOx_OSPEEDR` | 输出速度 |
| `GPIOx_PUPDR` | 上拉/下拉选择 |
| `GPIOx_IDR` | 输入数据（只读） |
| `GPIOx_ODR` | 输出数据（读写） |
| `GPIOx_BSRR` | 位设置/复位（原子操作） |
| `GPIOx_LCKR` | 配置锁定 |
| `GPIOx_AFRL` | 复用功能低8位（pin 0-7） |
| `GPIOx_AFRH` | 复用功能高8位（pin 8-15） |

### 2.2 模式配置（GPIOx_MODER）

每2位控制一个引脚：
- `00`：输入模式
- `01`：通用输出模式
- `10`：复用功能模式
- `11`：模拟模式

### 2.3 输出配置

**输出类型（GPIOx_OTYPER）**：
- `0`：推挽输出
- `1`：开漏输出

**输出速度（GPIOx_OSPEEDR）**，每2位：
- `00`：低速
- `01`：中速
- `10`：高速
- `11`：极高速

### 2.4 上拉/下拉（GPIOx_PUPDR）

每2位：
- `00`：无上拉/下拉
- `01`：上拉
- `10`：下拉
- `11`：保留

### 2.5 复用功能选择

- `GPIOx_AFRL[3:0]` x 8：pin 0-7 的复用功能选择（AF0-AF15）
- `GPIOx_AFRH[3:0]` x 8：pin 8-15 的复用功能选择（AF0-AF15）
- 复位后默认 AF0，具体映射见器件 datasheet

### 2.6 原子位操作（GPIOx_BSRR）

- 低16位 BS(i)：写1设置对应 ODR 位
- 高16位 BR(i)：写1复位对应 ODR 位
- 写0无效果
- 同时设置和复位时，设置优先

### 2.7 配置锁定（GPIOx_LCKR）

特殊写序列锁定 GPIO 配置（MODER、OTYPER、OSPEEDR、PUPDR、AFRL、AFRH），锁定后直到下次复位才能修改。

### 2.8 GPIO 配置流程

1. 使能 GPIO 端口时钟（通过 RCC）
2. 设置 `GPIOx_MODER` 选择模式
3. 如果是输出：设置 `GPIOx_OTYPER`、`GPIOx_OSPEEDR`
4. 设置 `GPIOx_PUPDR` 选择上拉/下拉
5. 如果是复用功能：设置 `GPIOx_AFRL`/`GPIOx_AFRH`
6. 如果是模拟模式：直接设置 MODER=11

---

## 3. USART/UART（第53章，p2602-2692）

### 3.1 USART 概述

STM32MP157 提供：
- **USART1/2/3/6**：全功能（同步、Smartcard、IrDA、LIN）
- **UART4/5/7/8**：异步功能

主要特征：
- 全双工异步通信
- NRZ 标准格式
- 可配置过采样（16或8）
- 可编程波特率（分数发生器）
- 两个内部 FIFO（发送/接收，各16字节）
- 双时钟域（usart_pclk + usart_ker_ck）
- 自动波特率检测
- 数据字长：7、8或9位
- 停止位：1或2位
- DMA 支持

### 3.2 关键寄存器

| 寄存器 | 功能 |
|--------|------|
| `USART_CR1` | 控制寄存器1（使能、字长、奇偶校验、FIFO使能） |
| `USART_CR2` | 控制寄存器2（停止位、时钟极性） |
| `USART_CR3` | 控制寄存器3（DMA使能、硬件流控、过采样） |
| `USART_BRR` | 波特率寄存器 |
| `USART_PRESC` | 预分频寄存器 |
| `USART_ISR` | 中断和状态寄存器 |
| `USART_ICR` | 中断标志清除寄存器 |
| `USART_RDR` | 接收数据寄存器 |
| `USART_TDR` | 发送数据寄存器 |
| `USART_RQR` | 请求寄存器 |
| `USART_RTOR` | 接收超时寄存器 |
| `USART_GTPR` | 保护时间和预分频寄存器 |

### 3.3 USART_CR1 关键位域

- `UE`：USART 使能
- `UESM`：低功耗模式下 USART 使能
- `RE`：接收器使能
- `TE`：发送器使能
- `IDLEIE`：IDLE 中断使能
- `RXNEIE`：RXNE 中断使能
- `TCIE`：发送完成中断使能
- `TXEIE`：TXE 中断使能
- `PEIE`：奇偶校验错误中断使能
- `PS`：奇偶校验选择
- `PCE`：奇偶校验控制使能
- `M[1:0]`：字长（00=8位，01=9位，10=7位）
- `OVER8`：过采样模式
- `FIFOEN`：FIFO 模式使能

### 3.4 USART_CR3 关键位域

- `DMAT`：DMA 发送使能
- `DMAR`：DMA 接收使能
- `RTSE`：RTS 使能
- `CTSE`：CTS 使能
- `ONEBIT`：过采样方法（3位采样或单采样）
- `OVRDIS`：过载检测禁止

### 3.5 波特率计算

```
Baud = usart_ker_ck / (8 * (2 - OVER8) * USART_BRR)
```

其中 `usart_ker_ck` 由 `RCC_UARTxCKSELR` 选择的时钟源决定。

### 3.6 USART 中断源

| 事件 | 标志位 | 使能位 | 清除方法 |
|------|--------|--------|----------|
| 发送数据寄存器空 | TXE | TXEIE | 写TDR |
| 发送FIFO未满 | TXFNF | TXFNFIE | FIFO满时清除 |
| 发送FIFO空 | TXFE | TXFEIE | FIFO有数据或TXFRQ |
| 发送完成 | TC | TCIE | 写TDR或TCCF |
| 接收数据寄存器非空 | RXNE | RXNEIE | 读RDR或RXFRQ |
| 接收FIFO非空 | RXFNE | RXFNEIE | FIFO空或RXFRQ |
| 过载错误 | ORE | - | ORECF |
| 空闲线检测 | IDLE | IDLEIE | IDLECF |
| 奇偶校验错误 | PE | PEIE | PECF |
| 噪声错误 | NE | - | NECF |
| 帧错误 | FE | - | FECF |
| 字符匹配 | CMF | CMIE | CMCF |
| 接收超时 | RTOF | RTOFIE | RTOCCF |

### 3.7 USART 配置步骤

1. 使能 USART 时钟（RCC 中设置 `RCC_UARTxCKSELR` 选择内核时钟源）
2. 使能 GPIO 时钟，配置 TX/RX 引脚为复用功能
3. 设置 `USART_CR1`：字长、奇偶校验、FIFO使能
4. 设置 `USART_CR2`：停止位
5. 设置 `USART_CR3`：硬件流控、DMA
6. 设置 `USART_BRR`：波特率
7. 设置 `USART_PRESC`：预分频（如需要）
8. 使能发送器/接收器：`USART_CR1` 的 TE、RE 位
9. 使能 USART：`USART_CR1` 的 UE 位

---

## 4. 中断控制器（EXTI + NVIC + GIC）

### 4.1 NVIC（第22章，p1260）- Cortex-M4 侧

- **150个可屏蔽中断通道**
- **16个可编程优先级**（4位优先级）
- 与 Cortex-M4 紧密耦合，低延迟中断处理
- SysTick 校准值寄存器不可用（频率不固定），需根据 `mcu_ck` 设置重载值

### 4.2 GIC（第23章，p1261-1311）- Cortex-A7 侧

**中断源分类**：
- **SGI**（软件生成中断）：ID0-ID15，通过 `GICD_SGIR` 生成
- **PPI**（私有外设中断）：ID16-ID31，每CPU独立
  - PPI0: nFIQ（未使用）
  - PPI1: 安全物理定时器（ID29）
  - PPI2: 非安全物理定时器（ID30）
  - PPI3: nIRQ（未使用）
  - PPI4: 虚拟定时器（ID27）
  - PPI5: Hypervisor 定时器（ID26）
  - PPI6: 虚拟维护中断（ID25）
- **SPI**（共享外设中断）：ID32-ID287，最多256个

**关键 GIC 寄存器**：

| 寄存器 | 功能 |
|--------|------|
| `GICD_CTLR` | 分发器控制（ENABLEGRP0/1） |
| `GICD_TYPER` | 中断控制器类型 |
| `GICD_ISENABLERx` | 中断使能设置 |
| `GICD_ICENABLERx` | 中断使能清除 |
| `GICD_ISPENDRx` | 中断挂起设置 |
| `GICD_ICPENDRx` | 中断挂起清除 |
| `GICD_IPRIORITYRx` | 中断优先级（每8位一个优先级，5位有效） |
| `GICD_ITARGETSRx` | 中断目标CPU |
| `GICD_IGROUPRx` | 中断分组（Group0/Group1） |

**GIC 配置步骤**：
1. 设置 `GICD_CTLR` 使能中断分发
2. 配置 `GICD_IGROUPRx` 设置中断分组
3. 设置 `GICD_IPRIORITYRx` 配置优先级
4. 设置 `GICD_ITARGETSRx` 指定目标CPU
5. 使能中断：`GICD_ISENABLERx`

### 4.3 EXTI（第24章，p1312-1354）

**EXTI 概述**：
- 76个输入事件
- 支持双CPU（MPU 和 MCU）
- 所有事件输入可唤醒系统
- 两类事件输入：
  - **可配置事件**（来自I/O或外设的脉冲）：可选触发边沿、有挂起状态位
  - **直接事件**（来自有标志位的外设）：固定上升沿触发、无EXTI挂起位

**关键 EXTI 寄存器**：

| 寄存器 | 功能 |
|--------|------|
| `EXTI_RTSR1/2/3` | 上升沿触发选择 |
| `EXTI_FTSR1/2/3` | 下降沿触发选择 |
| `EXTI_SWIER1/2/3` | 软件中断事件 |
| `EXTI_RPR1/2/3` | 上升沿挂起寄存器 |
| `EXTI_FPR1/2/3` | 下降沿挂起寄存器 |
| `EXTI_IMR1/2/3` | CPU1（MPU）中断屏蔽 |
| `EXTI_C2IMR1/2/3` | CPU2（MCU）中断屏蔽 |
| `EXTI_EMR1/2/3` | CPU1 事件屏蔽 |
| `EXTI_C2EMR1/2/3` | CPU2 事件屏蔽 |

**EXTI 配置流程**：
1. 选择触发边沿：设置 `EXTI_RTSR`（上升沿）和/或 `EXTI_FTSR`（下降沿）
2. 配置中断屏蔽：设置 `EXTI_IMR`（MPU）或 `EXTI_C2IMR`（MCU）
3. 配置事件屏蔽（如需事件）：设置 `EXTI_EMR` 或 `EXTI_C2EMR`
4. 配置 GPIO 引脚为输入模式（非模拟）
5. 在 NVIC/GIC 中使能对应中断

---

## 5. DMA（第18章，p1185-1222）

### 5.1 DMA 概述

- **DMA1 和 DMA2**，每个有 **8个流**（共16个流）
- 双 AHB 主总线架构（内存端口 + 外设端口）
- 每个流通过 DMAMUX 选择请求源（最多116个通道）
- 4字深度 FIFO（每流独立）
- 优先级：4级软件可编程 + 硬件仲裁

### 5.2 DMA 流寄存器

| 寄存器 | 功能 |
|--------|------|
| `DMA_SxCR` | 流控制寄存器 |
| `DMA_SxNDTR` | 数据数量寄存器 |
| `DMA_SxPAR` | 外设地址寄存器 |
| `DMA_SxM0AR` | 内存地址0寄存器 |
| `DMA_SxM1AR` | 内存地址1寄存器（双缓冲） |
| `DMA_SxFCR` | FIFO 控制寄存器 |
| `DMA_LISR` | 低位中断状态寄存器 |
| `DMA_HISR` | 高位中断状态寄存器 |
| `DMA_LIFCR` | 低位中断标志清除寄存器 |
| `DMA_HIFCR` | 高位中断标志清除寄存器 |

### 5.3 DMA_SxCR 关键位域

- `EN`：流使能
- `DIR[1:0]`：传输方向
  - `00`：外设→内存
  - `01`：内存→外设
  - `10`：内存→内存
- `CIRC`：循环模式
- `PINC`：外设地址递增
- `MINC`：内存地址递增
- `PSIZE[1:0]`：外设数据宽度（00=8位，01=16位，10=32位）
- `MSIZE[1:0]`：内存数据宽度
- `PL[1:0]`：优先级（00=低，01=中，10=高，11=极高）
- `DBM`：双缓冲模式
- `CT`：当前目标（双缓冲时）
- `PBURST[1:0]`：外设突发（00=单次，01=4拍，10=8拍，11=16拍）
- `MBURST[1:0]`：内存突发
- `TCIE`：传输完成中断使能
- `HTIE`：半传输中断使能
- `TEIE`：传输错误中断使能
- `DMEIE`：直接模式错误中断使能

### 5.4 DMA_SxFCR 关键位域

- `DMDIS`：直接模式禁止（0=直接模式，1=FIFO模式）
- `FTH[1:0]`：FIFO 阈值（00=1/4，01=1/2，10=3/4，11=满）

### 5.5 DMA 中断标志

每个流有5个事件标志：
- **TCIF**：传输完成
- **HTIF**：半传输完成
- **TEIF**：传输错误
- **DMEIF**：直接模式错误
- **FEIF**：FIFO 错误

### 5.6 DMA 配置步骤

1. 使能 DMA 时钟（RCC）
2. 设置 `DMA_SxPAR`：外设地址
3. 设置 `DMA_SxM0AR`：内存地址
4. 设置 `DMA_SxNDTR`：数据数量
5. 配置 `DMA_SxCR`：方向、数据宽度、优先级、递增模式、循环模式
6. 配置 `DMA_SxFCR`：FIFO 模式和阈值
7. 通过 DMAMUX 选择请求源
8. 使能中断（如需）：TCIE、HTIE、TEIE
9. 使能流：`DMA_SxCR` 的 EN 位

### 5.7 DMAMUX（第19章，p1223）

DMAMUX 将116个外设请求源映射到16个 DMA 流。每个流通过 `DMAMUX_CxCR` 寄存器的 `DMAREQ_ID[7:0]` 选择请求源。

---

## 6. 电源管理（PWR，第9章，p436-499）

### 6.1 PWR 概述

- 外部稳压器控制（PWR_ON、PWR_LP）
- 电源监控：POR/PDR、BOR、PVD、AVD
- VBAT 充电
- 多种低功耗模式

### 6.2 电源域

| 电源域 | 供电 | 说明 |
|--------|------|------|
| VDD | I/O、系统模拟 | 主电源 |
| VDDCORE | 数字核心 | 外部稳压器供电 |
| VBAT | 备份域 | 电池供电 |
| VDDA | ADC/DAC | 模拟电源 |
| VDD3V3_USBFS | USB FS I/O | 独立供电 |
| VDDQ_DDR | DDR PHY | 独立供电 |

### 6.3 低功耗模式

| 模式 | 描述 | 唤醒源 |
|------|------|--------|
| CSleep | CPU 时钟停止，外设时钟可控 | 任意中断 |
| CStop | CPU 子系统停止 | EXTI 唤醒 |
| CStandby | CPU 子系统待机 | EXTI 唤醒 |
| Stop | 全系统停止（VDDCORE 保持） | WKUP 引脚 |
| LP-Stop | 低功耗停止（稳压器低功耗） | WKUP 引脚 |
| LPLV-Stop | 低功耗低压停止 | WKUP 引脚 |
| Standby | 全系统待机（VDDCORE 断电） | WKUP 引脚/复位 |

### 6.4 关键 PWR 寄存器

| 寄存器 | 功能 |
|--------|------|
| `PWR_CR1` | 控制寄存器1（LPDS、LVDS、LPCFG） |
| `PWR_CSR1` | 控制状态寄存器1 |
| `PWR_CR2` | 控制寄存器2 |
| `PWR_CR3` | 控制寄存器3 |
| `PWR_MPUCR` | MPU 控制寄存器 |
| `PWR_MCUCR` | MCU 控制寄存器 |
| `PWR_WKUPCR` | 唤醒控制寄存器 |
| `PWR_WKUPFR` | 唤醒标志寄存器 |
| `PWR_MPUWKUPENR` | MPU 唤醒使能 |
| `PWR_MCUWKUPENR` | MCU 唤醒使能 |

### 6.5 WKUP 引脚

- 6个 WKUP 引脚（WKUP1-WKUP6）
- 可配置上升沿/下降沿触发
- 支持内部上拉

---

## 7. SYSCFG（第14章，p1088-1109）

### 7.1 SYSCFG 概述

系统配置控制器，主要管理：
- I/O 补偿单元
- Ethernet 时钟源选择
- I2C Fast Mode Plus 配置
- 高速低压 Pad 模式
- AXI 互联控制

### 7.2 I/O 补偿单元

当 I/O 输出缓冲速度配置在 50 MHz 及以上时，建议使用补偿单元进行压摆率控制。

**使能序列**：
1. 确保 CSI 振荡器已使能并就绪
2. 设置 `SYSCFG_CMPENSETR.MCU_EN` 或 `MPU_EN = 1`
3. 等待 `SYSCFG_CMPCR.READY = 1`
4. 设置 `SYSCFG_CMPCR.SW_CTRL = 0`

**禁止序列**（保持当前补偿值）：
1. 复制 `SYSCFG_CMPCR.APSRC[3:0]`/`ANSRC[3:0]` 到 `RAPSRC`/`RANSRC`
2. 设置 `SYSCFG_CMPCR.SW_CTRL = 1`
3. 设置 `SYSCFG_CMPENCLRR.MCU_EN` 和 `MPU_EN = 1`

### 7.3 关键 SYSCFG 寄存器

| 寄存器 | 偏移 | 功能 |
|--------|------|------|
| `SYSCFG_BOOTR` | 0x000 | BOOT 引脚状态和控制 |
| `SYSCFG_PMCSETR` | 0x004 | 外设模式配置设置 |
| `SYSCFG_PMCCLRR` | 0x044 | 外设模式配置清除 |
| `SYSCFG_IOCTRLSETR` | 0x018 | I/O 控制设置 |
| `SYSCFG_IOCTRLCLRR` | 0x058 | I/O 控制清除 |
| `SYSCFG_ICNR` | 0x01C | 互联控制 |
| `SYSCFG_CMPCR` | 0x020 | 补偿单元控制 |
| `SYSCFG_CMPENSETR` | 0x024 | 补偿使能设置 |
| `SYSCFG_CMPENCLRR` | 0x028 | 补偿使能清除 |

### 7.4 SYSCFG_PMCSETR 关键位域

- `ETH_SEL[2:0]`（bits 23:21）：Ethernet PHY 接口选择
  - `000`：GMII 或 MII
  - `001`：RGMII
  - `100`：RMII
- `ETH_SELMII`（bit 20）：MII/GMII 选择
- `ETH_REF_CLK_SEL`（bit 17）：RMII 50MHz 时钟选择
- `ETH_CLK_SEL`（bit 16）：125MHz 时钟选择
- `I2Cx_FMP`（bits 5:0）：I2C Fast Mode Plus 使能

### 7.5 SYSCFG_IOCTRLSETR 关键位域

- `HSLVEN_SPI`（bit 4）：SPI 高速低压 Pad 模式
- `HSLVEN_SDMMC`（bit 3）：SDMMC 高速低压 Pad 模式
- `HSLVEN_ETH`（bit 2）：ETH 高速低压 Pad 模式
- `HSLVEN_QUADSPI`（bit 1）：QUADSPI 高速低压 Pad 模式
- `HSLVEN_TRACE`（bit 0）：TRACE 高速低压 Pad 模式

> **警告**：VDD > 2.7V 时使能高速模式可能损坏芯片。

---

## 附录：寄存器访问约定

- **rw**：读写
- **r**：只读
- **w**：只写
- **rc_w1**：读清除（写1清除）
- **rs**：读设置（写1设置）
- **t**：写1触发（自动清除）

## 附录：常用外设时钟使能位置

| 外设 | 总线 | MPU使能寄存器 | MCU使能寄存器 |
|------|------|---------------|---------------|
| GPIOA-K | AHB4 | `RCC_MP_AHB4ENSETR` | `RCC_MC_AHB4ENSETR` |
| USART1 | APB5 | `RCC_MP_APB5ENSETR` | `RCC_MC_APB5ENSETR` |
| USART2-3 | APB1 | `RCC_MP_APB1ENSETR` | `RCC_MC_APB1ENSETR` |
| UART4-5 | APB1 | `RCC_MP_APB1ENSETR` | `RCC_MC_APB1ENSETR` |
| USART6 | APB2 | `RCC_MP_APB2ENSETR` | `RCC_MC_APB2ENSETR` |
| UART7-8 | APB1 | `RCC_MP_APB1ENSETR` | `RCC_MC_APB1ENSETR` |
| DMA1/DMA2 | AHB2 | `RCC_MP_AHB2ENSETR` | `RCC_MC_AHB2ENSETR` |
| SYSCFG | APB3 | `RCC_MP_APB3ENSETR` | `RCC_MC_APB3ENSETR` |
| EXTI | APB3 | `RCC_MP_APB3ENSETR` | `RCC_MC_APB3ENSETR` |
| PWR | APB3 | `RCC_MP_APB3ENSETR` | `RCC_MC_APB3ENSETR` |
