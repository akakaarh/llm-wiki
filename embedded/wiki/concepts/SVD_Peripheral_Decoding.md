---
title: SVD 外设寄存器解码
type: concept
tags: [svd, debug, peripheral, register, cmsis, stm32]
related: ["#JTAG_SWD_Debugging.md", "#NVIC.md", "#MPU_CortexM.md"]
---

# SVD 外设寄存器解码

## 什么是 SVD

SVD (System View Description) 是 ARM CMSIS 标准定义的 XML 格式文件，描述了微控制器所有外设的寄存器映射。每个芯片厂商提供自己芯片的 SVD 文件。

SVD 文件包含：
- 外设名称和基地址（如 I2C1 基地址 0x40005400）
- 每个寄存器的名称、偏移、大小、访问权限
- 每个位域的名称、位置、宽度、描述

```xml
<peripheral>
  <name>I2C1</name>
  <baseAddress>0x40005400</baseAddress>
  <register>
    <name>SR1</name>
    <addressOffset>0x14</addressOffset>
    <fields>
      <field><name>BERR</name><bitOffset>0</bitOffset><bitWidth>1</bitWidth></field>
      <field><name>TXE</name><bitOffset>7</bitOffset><bitWidth>1</bitWidth></field>
    </fields>
  </register>
</peripheral>
```

## 为什么需要 SVD

调试驱动问题时，直接读内存地址是无意义的：

```
(gdb) x/x 0x40005414
0x40005414: 0x00000082    ← 看不懂
```

用 SVD 解码后：

```
I2C1->SR1 (0x40005414) = 0x00000082
  [7] TXE  = 1  (TX data register empty)
  [1] BERR = 1  (Bus error)           ← 一目了然
```

## 在 gdb-ai-bridge 中使用

### 加载 SVD 文件

```gdb
# 方式 1：启动时设置环境变量
SVD_FILE=/path/to/STM32MP157x.svd arm-none-eabi-gdb-py3 firmware.elf

# 方式 2：GDB 内配置（推荐）
(gdb) ai config svd /path/to/STM32MP157x.svd
```

### 解码寄存器

```gdb
# 解码单个寄存器
(gdb) ai decode 0x40005414
I2C1->SR1 (0x40005414) = 0x00000082
  [7] TXE = 1
  [1] BERR = 1

# 解码连续 N 个寄存器
(gdb) ai decode 0x40005400 5

# 查看 SVD 状态
(gdb) ai info
```

### 自动解码

`ai collect` 采集崩溃上下文时，如果加载了 SVD 文件，会自动解码 SCB 故障寄存器（CFSR、HFSR、MMFAR、BFAR）。

## SVD 文件下载

### ST 官方（STM32 系列）

ST 的 STM32CubeMX 安装目录下有所有 STM32 芯片的 SVD 文件：

```
STM32CubeMX安装目录/STM32CubeMX/repository/cmsis/stm32mp157.svd
```

或者从 Keil Pack 中提取（.pack 文件是 ZIP 格式）：

```bash
unzip Keil.STM32MP1xx_DFP.1.3.0.pack "SVD/*.svd"
```

### cmsis-svd GitHub 仓库

ARM 官方维护的 SVD 文件集合：

https://github.com/posborne/cmsis-svd

包含所有主流厂商（ST、NXP、TI、Nordic、Microchip 等）的 SVD 文件。

### 各厂商来源

| 厂商 | SVD 来源 |
|------|----------|
| ST (STM32) | STM32CubeMX / Keil Pack / cmsis-svd |
| NXP | MCUXpresso SDK / cmsis-svd |
| Nordic (nRF) | nRF Connect SDK / cmsis-svd |
| TI (CC/SimpleLink) | CCS / cmsis-svd |
| Microchip (SAM/PIC) | MPLAB X / cmsis-svd |

## STM32MP157 常用外设

| 外设 | 基地址 | 说明 |
|------|--------|------|
| GPIOA | 0x50002000 | GPIO 端口 A |
| GPIOB | 0x50003000 | GPIO 端口 B |
| I2C1 | 0x40005400 | I2C 控制器 1 |
| I2C4 | 0x5C002000 | I2C 控制器 4 |
| SPI1 | 0x40013000 | SPI 控制器 1 |
| USART2 | 0x40004400 | USART 2 |
| TIM2 | 0x40000000 | 定时器 2 |
| DMA1 | 0x48000000 | DMA 控制器 1 |
| EXTI | 0x5000D000 | 外部中断 |
| SCB | 0xE000ED00 | 系统控制块（Cortex-M4） |

## SVD 格式要点

### derivedFrom（外设继承）

多个相同外设（如 GPIOA、GPIOB）共享寄存器定义：

```xml
<peripheral derivedFrom="GPIOA">
  <name>GPIOB</name>
  <baseAddress>0x50003000</baseAddress>
</peripheral>
```

### dim 数组（寄存器数组）

重复寄存器用 dim 展开：

```xml
<register>
  <name>CCR%s</name>
  <dim>4</dim>
  <dimIncrement>0x4</dimIncrement>
  <dimIndex>1,2,3,4</dimIndex>
</register>
```

展开为 CCR1、CCR2、CCR3、CCR4。

### 枚举值（enumeratedValues）

某些位域有预定义的枚举值：

```xml
<field>
  <name>MODE</name>
  <enumeratedValues>
    <enumeratedValue><name>Input</name><value>0</value></enumeratedValue>
    <enumeratedValue><name>Output</name><value>1</value></enumeratedValue>
  </enumeratedValues>
</field>
```

当前 gdb-ai-bridge 的 SVD 解析器不支持枚举值解码（显示原始数值），未来可扩展。

## 调试场景示例

### I2C 通信失败

```gdb
(gdb) ai decode 0x40005414
I2C1->SR1 (0x40005414) = 0x00000004
  [2] AF = 1  (Acknowledge failure)    ← 从机没有应答
```

### HardFault 诊断

```gdb
(gdb) ai decode 0xE000ED28
SCB->CFSR (0xE000ED28) = 0x00000082
  [9] DIVBYZERO = 0
  [7] MMARVALID = 0
  [1] IBUSERR = 1  (Instruction bus error)  ← 指令总线错误
```

### GPIO 配置检查

```gdb
(gdb) ai decode 0x50002000 8
GPIOA->MODER (0x50002000) = 0xABFFF...
GPIOA->OTYPER (0x50002004) = 0x00000000
...
```
