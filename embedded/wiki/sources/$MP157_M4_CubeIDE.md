---
type: source
tags: [stm32mp157, m4, cubemx, cubide, bare-metal, cortex-m4]
---

# STM32MP1 M4 裸机 CubeIDE 开发指南

> 来源：正点原子 STM32MP1 M4裸机CubeIDE开发指南 V1.5.2
> 作者：正点原子 Linux 团队
> 版本：V1.5.2（2021.7.13）
> 页数：1100页

---

## 文档概述

本文档是正点原子 STM32MP157 开发板的 M4 内核裸机开发指南，基于 STM32CubeIDE 集成开发环境和 HAL 库进行开发。文档从零开始，循序渐进地介绍 STM32MP157 的 M4 内核开发，涵盖开发环境搭建、HAL 库使用、时钟系统、GPIO、UART、定时器、SPI、I2C、ADC/DAC、DMA 等外设的使用方法。

---

## 按文档章节结构逐一总结

### 第一章 本书学习方法（第21-28页）

本章介绍文档的学习方法和资源获取方式。

**关键内容：**
- **学习顺序**：建议先通读《STM32MP157 开发板硬件参考手册》，再从头循序渐进学习
- **参考资料**：
  - 《STM32MP157 参考手册》- ST 官方通用参考资料
  - 《STM32MP157A&D 数据手册》- 芯片引脚和电气特性
  - 《The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors, 3rd Edition》- Cortex-M4 架构详解
  - 《Cortex-M3 权威指南》中文版（宋岩 译）
  - 《STM32H7x3 参考手册(中文版)》- 可辅助学习 STM32MP1（外设类似）
- **编写规范**：每章分为 4 部分 - 外设功能介绍、硬件设计、程序设计、下载验证
- **代码规范**：
  - 函数/变量名使用小写字母
  - 注释使用 doxgen 风格 `/* */`
  - TAB 键用 4 个空格对齐
  - 全局变量用 `g_` 前缀，全局指针用 `p_` 前缀
- **例程列表**：共 25+ 个实验，从汇编 LED 灯到 DS18B20/DHT11 传感器

**学习资料获取：**
- ST 官网：www.st.com
- ST 中文社区：www.stmcu.org
- ST Wiki 平台：https://wiki.st.com
- 正点原子文档中心：www.openedv.com/docs/index.html
- 正点原子论坛：www.openedv.com

---

### 第二章 STM32MP1 简介（第29-45页）

本章介绍 STM32MP1 的基本概念、资源分配和选型方法。

**2.1 初识 STM32MP1**

- **STM32 家族**：2007 年 ST 发布首款 Cortex-M3 芯片 STM32F103，截至 2020 年累计出货超 45 亿颗
- **STM32MP1 系列**：2019 年发布，首款 Cortex-A7 内核的 MPU
  - STM32MP151：单核 A7 + M4，入门级
  - STM32MP153：双核 A7 + M4，中端级
  - STM32MP157：双核 A7 + M4 + 3D GPU，旗舰级

- **STM32MP157DAA1 资源表**：
  | 资源 | 参数 |
  |------|------|
  | Cortex-A7 | 800MHz × 2 |
  | Cortex-M4 | 209MHz × 1 |
  | 3D GPU | 1 个，支持 OpenGL ES2.0 |
  | SRAM | 708KB |
  | 封装 | LFBGA448 |
  | 通用 IO | 176 个 |
  | 16 位定时器 | 12 个 |
  | U(S)ART | 4+4=8 个 |
  | CAN FD | 2 个 |
  | SDIO | 3 个 |
  | 千兆网络 MAC | 1 个 |
  | SPI | 6 个 |
  | I2C | 6 个 |
  | USB OTG FS | 1 个 |
  | USB OTG HS | 2 个 |
  | RGB LCD | 1 个，24bit，最高 1366×768 60fps |

**2.1.4 A7 和 M4 内核资源分配**

STM32MP157 的外设资源分配模式：
- **单选**：外设只能分配给 A7 或 M4 其中一个
- **共享**：外设可以被 A7 和 M4 同时访问
- **M4 可用外设**：
  - ADC、DAC、DFSDM（单选）
  - SAI1-4、SPDIFRX（单选）
  - DMA1/DMA2、DMAMUX（单选/可共享）
  - GPIOA-GPIOK、GPIOZ（可共享）
  - TIM1-TIM17（单选）
  - WWDG（M4 专用）
  - I2C1-6（单选）
  - SPI1-6（单选）
  - USART1-8（单选）
  - FDCAN1-2（单选）
  - QUADSPI（单选）

- **M4 不可用外设**：
  - RTC（单独使用可用，与其他定时器中断共用会出问题）
  - IWDG1（A7 专用）
  - USB（A7 专用）
  - FMC（A7 专用）
  - ETH（A7 专用）
  - LTDC、GPU、DSI（A7 专用）

**2.2 M4 内核与 STM32F4 单片机区别**

| 对比项 | STM32MP157 M4 | STM32F429 |
|--------|---------------|-----------|
| 内核 | Cortex-M4 带 FPU | Cortex-M4 带 FPU |
| 主频 | 209MHz | 180MHz |
| 内部 RAM | 708KB（可用 384KB） | 256KB |
| 内部 Flash | 无 | 2MB |
| RTC | 不支持 | 支持 |
| USB | 不支持 | 支持 |
| FMC | 不支持 | 支持 |
| ETH | 不支持 | 支持 |

**关键差异：无内部 Flash**
- 代码只能下载到 MCU SRAM（0x10000000~0x1005FFFF，384KB）
- 掉电程序丢失，需要通过 A7 的 Linux 系统加载 bin 文件启动 M4
- 启动流程：A7 启动 Linux → 加载 M4 bin 文件到 SRAM → M4 启动

**2.3 STM32MP1 设计选型**

- **命名规则**：STM32MP157DAA1
  - STM32：家族
  - MP：MPU
  - 157：旗舰型号
  - D：800MHz，基本安全性
  - AA：LFBGA448 引脚
  - 1：-20℃~+105℃ 结温

- **选型原则**：由高到低、由大到小
- **原理图设计**：最小系统 + IO 分配
  - 最小系统：主控 + DDR + 存储器 + 电源方案
  - IO 分配：先分配特定外设 IO，再分配通用 IO，最后微调

---

### 第三章 开发环境搭建（第46-62页）

本章介绍 STM32CubeIDE 的安装和开发工具准备。

**3.1 STM32Cube 生态简介**

STM32Cube 生态系统包括：
- **STM32CubeMX**：图形化配置工具，配置引脚、时钟树、中间件，生成初始化代码
- **STM32CubeIDE**：集成开发环境，集成了 TrueSTUDIO 和 STM32CubeMX
- **STM32CubeProgrammer**：代码烧写工具，支持 SWD/JTAG/UART/USB
- **STM32CubeMonitor**：实时诊断工具，读取程序变量

**3.2 常用开发工具准备**

| 工具类型 | 推荐工具 | 说明 |
|----------|----------|------|
| IDE | STM32CubeIDE 1.4.0 | 免费，跨平台，集成 CubeMX |
| 仿真器 | STLINK V2 / DAP / JLINK | STLINK 最便宜，DAP 开源 |
| 串口助手 | XCOM | 正点原子开发，稳定功能多 |

**3.3 STM32CubeIDE 安装步骤**

1. **安装 Java 环境**：需要 V1.7 及以上版本，推荐 V1.8.0_271 64 位
   - 下载地址：www.java.com
   - 验证命令：`java -version`

2. **安装 STM32CubeIDE**：
   - 版本：1.4.0（集成 CubeMX V6.0.0）
   - 安装路径不能有中文
   - 双击 `st-stm32cubeide_1.4.0_7511_20200720_0928_x86_64.exe` 安装
   - 支持 Windows/Linux/macOS（64 位）

**3.4 CH340 USB 虚拟串口驱动安装**
- 用于开发板串口调试
- 驱动路径：开发板光盘 A-基础资料\5、开发工具\1、软件\CH340 驱动

---

### 第四章 STM32CubeIDE 的使用（第63-170页）

本章详细介绍 STM32CubeIDE 的工程创建、配置、编译和调试方法。

**4.1 STM32CubeIDE 第一个工程**

**4.1.1 创建工程**
1. 打开 STM32CubeIDE，选择 File → New → STM32 Project
2. 在芯片选择界面搜索 STM32MP157DAA1
3. 配置工程名称和路径
4. 选择目标芯片后点击 Finish

**4.1.2 配置工程**
- **Pinout & Configuration**：配置引脚复用功能
- **Clock Configuration**：配置时钟树
- **Project Manager**：配置工程设置
  - 勾选 "Generate peripheral initialization as a pair of .c/.h files per peripheral"
  - 使能 Full Assert（调试阶段）

**4.1.3 生成初始化代码**
- 按 Ctrl+S 保存 .ioc 文件，自动生成初始化代码
- 生成的代码结构：
  ```
  工程名_CM4/
  ├── Core/
  │   ├── Inc/          # 头文件
  │   └── Src/          # 源文件
  │       ├── main.c
  │       ├── gpio.c
  │       └── ...
  ├── BSP/              # 用户驱动代码
  └── Drivers/          # HAL 库文件
  ```

**4.2 工程配置技巧**

**4.2.1 添加头文件路径**
- 方法一：右键工程 → Properties → C/C++ General → Paths and Symbols → Includes → Add
- 方法二：直接在代码中使用相对路径 `#include "../../UART/UART.h"`

**4.2.2 添加源文件**
- 方法一：在工程中直接新建文件
- 方法二：导入已有文件（Import → General → File System）
- 方法三：拖拽文件到工程中（选择 Copy files 或 Link to files）

**4.2.3 编译生成 BIN/HEX 文件**
- 右键工程 → Properties → C/C++ Build → Settings → MCU Post build outputs
- 勾选 "Convert to binary file(-O binary)" 和 "Convert to Intel Hex file(-O ihex)"

**4.2.4 Debug 模式和 Release 模式**
- Debug 模式：包含调试信息，不做优化，可设置断点
- Release 模式：进行优化，代码更小，不能单步调试
- 切换方法：Project → Build Configurations → Set Active

**4.3 调试配置**

**4.3.1 STLINK 调试配置**
1. 连接 STLINK 到开发板的 SWD 接口
2. 右键工程 → Debug As → Debug Configurations
3. 选择 STM32 C/C++ Application
4. 配置 Debugger 选项：
   - Debug probe：ST-LINK (ST-LINK GDB server)
   - Interface：SWD
   - Frequency：建议 4000kHz

**4.3.2 DAP 调试配置**
1. 连接 DAP 到开发板的 SWD 接口
2. 配置 Debug probe：CMSIS-DAP (OpenOCD)
3. 其他配置与 STLINK 类似

**4.4 在线调试技巧**
- **断点设置**：双击代码行号左侧
- **单步执行**：F6（Step Over）、F5（Step Into）
- **查看变量**：选中变量，右键 → Watch Expression
- **查看寄存器**：Window → Show View → Registers
- **查看内存**：Window → Show View → Memory

---

### 第五章 C 语言基础及 STM32MP157 存储系统（第171-186页）

本章复习 C 语言基础知识，并介绍 STM32MP157 的存储系统。

**5.1 C 语言基础复习**
- **位操作**：与、或、异或、取反、左移、右移
- **define 宏定义**：`#define LED0_GPIO_Port GPIOI`
- **ifdef 条件编译**：`#ifdef __cplusplus ... #endif`
- **extern 变量声明**：声明在其他文件中定义的变量
- **typedef 类型别名**：`typedef unsigned int uint32_t`
- **结构体**：`typedef struct { ... } GPIO_InitTypeDef;`
- **关键字**：static、const、volatile
- **指针**：指针的定义和使用

**5.2 STM32MP157 存储系统**

**5.2.1 寄存器地址映射**
- 外设基地址：0x40000000
- GPIO 基地址：0x50002000（GPIOA）
- 每个 GPIO 端口偏移：0x400

**5.2.2 存储器映像**
- MCU SRAM：0x10000000 ~ 0x1005FFFF（384KB）
- APB 外设：0x40000000 ~ 0x5FFFFFFF
- AHB 外设：0x50000000 ~ 0x5FFFFFFF

**5.2.3 寄存器映像**
- GPIO_TypeDef 结构体封装了 GPIO 相关寄存器
- 通过操作结构体成员即可操作寄存器

---

### 第六章 STM32Cube 固件库（第187-240页）

本章介绍 STM32CubeMP1 固件库的目录结构和使用方法。

**6.1 获取 STM32Cube 固件库**
- 下载地址：ST 官网 → STM32CubeMP1
- 版本：STM32Cube_FW_MP1_V1.2.0

**6.2 STM32CubeMP1 固件库目录结构**

```
STM32Cube_FW_MP1_V1.2.0/
├── Drivers/
│   ├── BSP/                    # 板级支持包
│   ├── CMSIS/                  # ARM CMSIS 库
│   └── STM32MP1xx_HAL_Driver/  # HAL 库
│       ├── Inc/                # 头文件
│       └── Src/                # 源文件
├── Middlewares/                # 中间件（FreeRTOS、USB、FatFs 等）
├── Projects/                   # 官方例程
│   ├── STM32MP157C-EV1/        # 官方评估板例程
│   └── STM32MP157C-DK2/        # 官方发现套件例程
└── Utilities/                  # 工具软件
```

**6.3 HAL 库文件结构**
- `stm32mp1xx_hal.c/h`：HAL 库主文件
- `stm32mp1xx_hal_conf.h`：HAL 库配置文件
- `stm32mp1xx_hal_gpio.c/h`：GPIO 外设驱动
- `stm32mp1xx_hal_uart.c/h`：UART 外设驱动
- `stm32mp1xx_hal_tim.c/h`：定时器外设驱动
- ...

---

### 第七章 HAL 库基础知识（第241-270页）

本章介绍 HAL 库的基本结构和使用方法。

**7.1 HAL 库简介**
- HAL 库是 ST 官方提供的硬件抽象层库
- 提供统一的 API 接口，便于代码移植
- 支持 STM32 全系列芯片

**7.2 HAL 库文件结构**
- `stm32mp1xx_hal.c`：HAL 库初始化和系统配置
- `stm32mp1xx_hal_conf.h`：HAL 库配置文件，控制启用哪些外设模块
- `stm32mp1xx_hal_gpio.c`：GPIO 外设驱动
- `stm32mp1xx_hal_rcc.c`：时钟配置驱动
- `stm32mp1xx_hal_cortex.c`：Cortex-M4 内核配置

**7.3 如何使用 HAL 库**
1. 包含头文件：`#include "stm32mp1xx_hal.h"`
2. 初始化 HAL 库：`HAL_Init()`
3. 配置系统时钟：`SystemClock_Config()`
4. 初始化外设：`MX_GPIO_Init()` 等
5. 编写应用逻辑

**7.4 HAL 库重要文件分析**

**7.4.1 stm32mp1xx_hal_conf.h**
- 启用/禁用外设模块：`#define HAL_GPIO_MODULE_ENABLED`
- 配置 HSE/HSI 时钟频率
- 配置中断优先级位数
- 启用断言：`#define USE_FULL_ASSERT`

**7.4.2 stm32mp1xx_hal.c**
- `HAL_Init()`：初始化 HAL 库，配置 SysTick 中断
- `HAL_DeInit()`：反初始化 HAL 库
- `HAL_GetTick()`：获取系统滴答计数器值
- `HAL_Delay()`：毫秒级延时函数

---

### 第八章 STM32CubeIDE 工程模板（第271-338页）

本章介绍如何创建 STM32CubeIDE 工程模板。

**8.1 STM32CubeIDE 工程模板**
- 创建一个通用的工程模板，方便后续实验使用
- 包含系统初始化、延时函数、串口调试等基础功能

**8.2 CA7 工程文件分析**
- CA7 工程用于 A7 内核的 Linux 设备树配置
- 本教程主要关注 CM4 工程

**8.3 CM4 工程文件分析**

**工程目录结构：**
```
工程名_CM4/
├── Binaries/                   # 编译生成的二进制文件
├── Common/                     # 公共文件
├── Core/
│   ├── Inc/                    # 头文件
│   │   ├── main.h
│   │   ├── gpio.h
│   │   └── ...
│   └── Src/                    # 源文件
│       ├── main.c
│       ├── gpio.c
│       ├── stm32mp1xx_it.c     # 中断处理函数
│       └── stm32mp1xx_hal_msp.c # HAL MSP 初始化
├── Drivers/
│   ├── CMSIS/                  # ARM CMSIS 库
│   └── STM32MP1xx_HAL_Driver/  # HAL 库
└── Startup/                    # 启动文件
    └── startup_stm32mp157daxx_cm4.s
```

**关键文件说明：**
- `main.c`：主程序入口
- `stm32mp1xx_it.c`：中断服务函数
- `stm32mp1xx_hal_msp.c`：MSP（MCU Support Package）初始化
- `startup_stm32mp157daxx_cm4.s`：启动文件，定义中断向量表

---

### 第九章 系统时钟配置实验（第339-372页）

本章介绍 STM32MP157 的时钟系统配置方法。

**9.1 STM32MP157 时钟系统简介**
- **HSE**：外部高速时钟，8MHz（正点原子开发板）
- **HSI**：内部高速时钟，64MHz
- **LSE**：外部低速时钟，32.768kHz
- **LSI**：内部低速时钟，32kHz
- **PLL**：锁相环，用于倍频

**9.2 时钟树配置**
- M4 内核时钟源：HSI 或 HSE
- 系统时钟最大 209MHz
- AHB/APB 总线时钟配置

**9.3 时钟配置函数**
- `SystemClock_Config()`：系统时钟配置函数
- `HAL_RCC_OscConfig()`：振荡器配置
- `HAL_RCC_ClockConfig()`：系统时钟配置
- `HAL_RCCEx_PeriphCLKConfig()`：外设时钟配置

**9.4 系统时钟配置实验**

**使用 HSE 配置系统时钟：**
```c
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /* 配置 HSE */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLL12SOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 100;
  RCC_OscInitStruct.PLL.PLLP = 2;
  RCC_OscInitStruct.PLL.PLLQ = 2;
  RCC_OscInitStruct.PLL.PLLR = 2;
  HAL_RCC_OscConfig(&RCC_OscInitStruct);

  /* 配置系统时钟 */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
  HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}
```

**9.5 HAL_Delay 延时函数**
- 基于 SysTick 定时器实现
- 精度：1ms
- 函数原型：`void HAL_Delay(uint32_t Delay)`

---

### 第十章 跑马灯实验（GPIO 输出）（第339-372页）

本章通过跑马灯实验介绍 GPIO 输出配置方法。

**10.1 STM32MP157 GPIO 简介**

**GPIO 功能模式（8种）：**
1. 输入浮空
2. 输入上拉
3. 输入下拉
4. 模拟输入
5. 具有上拉或下拉功能的开漏输出
6. 具有上拉或下拉功能的推挽输出
7. 具有上拉或下拉功能的开漏式复用功能
8. 具有上拉或下拉功能的推挽式复用功能

**GPIO 寄存器：**
| 寄存器 | 功能 | 复位值 |
|--------|------|--------|
| MODER | 模式控制寄存器 | 0xFFFFFFFF（模拟模式） |
| OTYPER | 输出类型寄存器 | 0x00000000（推挽） |
| OSPEEDR | 输出速度寄存器 | 0x00000000（低速） |
| PUPDR | 上拉下拉寄存器 | 0x00000000（无上下拉） |
| IDR | 输入数据寄存器 | 只读 |
| ODR | 输出数据寄存器 | 0x00000000 |
| BSRR | 置位/复位寄存器 | 只写，支持原子操作 |
| BRR | 清除寄存器 | 只写 |
| LCKR | 配置锁存寄存器 | 0x00000000 |
| AFRL/AFRH | 复用功能选择寄存器 | 0x00000000 |

**10.2 GPIO 相关 API 函数**

| 函数 | 功能 |
|------|------|
| `HAL_GPIO_Init()` | 初始化 GPIO 外设 |
| `HAL_GPIO_DeInit()` | 反初始化 GPIO 外设 |
| `HAL_GPIO_ReadPin()` | 读取引脚电平状态 |
| `HAL_GPIO_WritePin()` | 设置引脚输出电平 |
| `HAL_GPIO_TogglePin()` | 翻转引脚电平 |
| `HAL_GPIO_LockPin()` | 锁定引脚配置 |

**10.3 LED 灯简介**
- LED 工作电流：0~15mA
- 阳极接高电平，阴极接低电平点亮
- 正点原子开发板：LED0 接 PI0，LED1 接 PF3

**10.4 硬件设计**
- LED0：PI0（AHB4 总线）
- LED1：PF3（AHB4 总线）
- 输出低电平点亮，输出高电平熄灭

**10.5 软件设计**

**GPIO 配置步骤：**
1. 使能 GPIO 时钟：`__HAL_RCC_GPIOI_CLK_ENABLE()`
2. 配置 GPIO_InitStruct：
   - Pin：GPIO_PIN_0
   - Mode：GPIO_MODE_OUTPUT_PP（推挽输出）
   - Pull：GPIO_PULLUP（上拉）
   - Speed：GPIO_SPEED_FREQ_HIGH（高速）
3. 调用 `HAL_GPIO_Init()` 初始化

**关键代码：**
```c
// 初始化 GPIO
void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  __HAL_RCC_GPIOI_CLK_ENABLE();
  __HAL_RCC_GPIOF_CLK_ENABLE();

  GPIO_InitStruct.Pin = GPIO_PIN_0;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOI, &GPIO_InitStruct);
}

// 主循环控制 LED 闪烁
while (1)
{
  HAL_GPIO_TogglePin(GPIOI, GPIO_PIN_0);
  HAL_GPIO_TogglePin(GPIOF, GPIO_PIN_3);
  HAL_Delay(500);
}
```

---

### 第十一章 蜂鸣器实验（GPIO 输出）（第373-398页）

本章通过蜂鸣器实验进一步学习 GPIO 输出控制。

**11.1 蜂鸣器简介**
- 有源蜂鸣器：内部有振荡电路，通电即响
- 无源蜂鸣器：需要外部方波驱动

**11.2 硬件设计**
- 蜂鸣器接 PB5 引脚
- 输出高电平响，输出低电平不响

**11.3 软件设计**
- 配置 PB5 为推挽输出
- 使用 `HAL_GPIO_WritePin()` 控制蜂鸣器开关

---

### 第十二章 按键输入实验（GPIO 输入）（第399-435页）

本章通过按键输入实验介绍 GPIO 输入配置方法。

**12.1 按键输入简介**
- 按键按下：引脚接地，读取低电平
- 按键释放：引脚被上拉，读取高电平

**12.2 硬件设计**
- KEY0：PA0（上拉输入）
- KEY1：PC5（上拉输入）
- KEY2：PA15（上拉输入）
- WK_UP：PA0（下拉输入）

**12.3 软件设计**

**GPIO 输入配置：**
```c
GPIO_InitStruct.Pin = GPIO_PIN_0;
GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
GPIO_InitStruct.Pull = GPIO_PULLUP;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
```

**读取按键状态：**
```c
if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET)
{
  // 按键按下
  HAL_Delay(20); // 消抖
  if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET)
  {
    // 确认按键按下
  }
}
```

---

### 第十三章 外部中断实验（EXTI）（第436-502页）

本章介绍外部中断的配置和使用方法。

**13.1 EXTI 简介**
- EXTI 支持 23 个中断/事件线
- 支持上升沿、下降沿、双边沿触发
- 支持中断模式和事件模式

**13.2 EXTI 配置**
```c
GPIO_InitStruct.Pin = GPIO_PIN_0;
GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING; // 下降沿触发
GPIO_InitStruct.Pull = GPIO_PULLUP;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

// 使能中断
HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
HAL_NVIC_EnableIRQ(EXTI0_IRQn);
```

**13.3 中断服务函数**
```c
void EXTI0_IRQHandler(void)
{
  HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  if (GPIO_Pin == GPIO_PIN_0)
  {
    // 处理中断
  }
}
```

---

### 第十四章 串口通信实验（UART）（第436-502页）

本章介绍 UART 串口通信的配置和使用方法。

**14.1 串口通信简介**
- 异步串行通信协议
- 波特率、数据位、停止位、校验位
- 常用波特率：9600、115200

**14.2 STM32MP157 UART 资源**
- USART1-4：支持同步/异步模式
- UART5-8：仅支持异步模式
- M4 可用：USART2/3、UART4/5/7/8

**14.3 UART 寄存器**
- CR1：控制寄存器 1（使能发送/接收/中断）
- CR2：控制寄存器 2（停止位配置）
- CR3：控制寄存器 3（硬件流控制）
- BRR：波特率寄存器
- ISR：中断和状态寄存器
- TDR：发送数据寄存器
- RDR：接收数据寄存器

**14.4 UART HAL 库函数**
- `HAL_UART_Init()`：初始化 UART
- `HAL_UART_Transmit()`：发送数据（阻塞方式）
- `HAL_UART_Receive()`：接收数据（阻塞方式）
- `HAL_UART_Transmit_IT()`：发送数据（中断方式）
- `HAL_UART_Receive_IT()`：接收数据（中断方式）
- `HAL_UART_Transmit_DMA()`：发送数据（DMA 方式）
- `HAL_UART_Receive_DMA()`：接收数据（DMA 方式）

**14.5 串口实验配置**

**UART 配置步骤：**
1. 配置 GPIO 引脚为复用功能
2. 配置 UART 参数（波特率、数据位、停止位）
3. 使能 UART 中断（可选）
4. 实现中断回调函数

**关键代码：**
```c
UART_HandleTypeDef huart2;

void MX_USART2_UART_Init(void)
{
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  HAL_UART_Init(&huart2);
}

// 发送字符串
char *str = "Hello, STM32MP1!\r\n";
HAL_UART_Transmit(&huart2, (uint8_t *)str, strlen(str), 1000);

// 接收数据（中断方式）
uint8_t rx_data;
HAL_UART_Receive_IT(&huart2, &rx_data, 1);

// 接收完成回调函数
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  if (huart->Instance == USART2)
  {
    // 处理接收到的数据
    HAL_UART_Receive_IT(&huart2, &rx_data, 1);
  }
}
```

---

### 第十五章 窗口看门狗（WWDG）实验（第503-525页）

本章介绍窗口看门狗的配置和使用方法。

**15.1 WWDG 简介**
- 窗口看门狗用于检测程序运行异常
- 在窗口期内喂狗，否则复位
- 窗口期由上窗口值和下窗口值决定

**15.2 WWDG 寄存器**
- CR：控制寄存器（使能、计数器值）
- CFR：配置寄存器（窗口值、预分频器）
- SR：状态寄存器

**15.3 WWDG HAL 库函数**
- `HAL_WWDG_Init()`：初始化 WWDG
- `HAL_WWDG_Refresh()`：喂狗

**15.4 WWDG 实验配置**
```c
WWDG_HandleTypeDef hwwdg;

void MX_WWDG_Init(void)
{
  hwwdg.Instance = WWDG;
  hwwdg.Init.Prescaler = WWDG_PRESCALER_8;
  hwwdg.Init.Window = 80;
  hwwdg.Init.Counter = 127;
  hwwdg.Init.EWIMode = WWDG_EWI_ENABLE;
  HAL_WWDG_Init(&hwwdg);
}

// 喂狗
HAL_WWDG_Refresh(&hwwdg);
```

---

### 第十六章 基本定时器实验（第526-562页）

本章介绍基本定时器的配置和使用方法。

**16.1 基本定时器简介**
- TIM6 和 TIM7 为基本定时器
- 只有定时功能，没有输入捕获和输出比较
- 用于产生时基、触发 DAC 等

**16.2 基本定时器框图**
- 时钟源：APB1 总线时钟
- 预分频器：16 位，分频系数 1~65536
- 计数器：16 位，向上计数
- 自动重载寄存器：16 位

**16.3 基本定时器寄存器**
- CR1：控制寄存器 1
- CR2：控制寄存器 2
- DIER：DMA/中断使能寄存器
- SR：状态寄存器
- EGR：事件生成寄存器
- CNT：计数器
- PSC：预分频器
- ARR：自动重载寄存器

**16.4 基本定时器 HAL 库函数**
- `HAL_TIM_Base_Init()`：初始化定时器
- `HAL_TIM_Base_Start()`：启动定时器
- `HAL_TIM_Base_Start_IT()`：启动定时器中断
- `HAL_TIM_Base_Stop()`：停止定时器
- `HAL_TIM_Base_Stop_IT()`：停止定时器中断

**16.5 基本定时器中断实验**
```c
TIM_HandleTypeDef htim6;

void MX_TIM6_Init(void)
{
  htim6.Instance = TIM6;
  htim6.Init.Prescaler = 8399;  // 84MHz / 8400 = 10kHz
  htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim6.Init.Period = 9999;     // 10kHz / 10000 = 1Hz (1秒)
  htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  HAL_TIM_Base_Init(&htim6);
}

// 启动定时器中断
HAL_TIM_Base_Start_IT(&htim6);

// 定时器中断回调函数
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM6)
  {
    // 定时器溢出处理
  }
}
```

---

### 第十七章 通用定时器实验（第563-673页）

本章介绍通用定时器的中断、PWM 输出和输入捕获功能。

**17.1 通用定时器简介**
- TIM2/3/4/5 为通用定时器
- 支持定时、输入捕获、输出比较、PWM 等功能
- 16 位或 32 位计数器

**17.2 通用定时器中断实验**
- 配置方法与基本定时器类似
- 支持向上、向下、中央对齐计数模式

**17.3 通用定时器 PWM 输出实验**

**PWM 配置步骤：**
1. 配置定时器为 PWM 模式
2. 配置 GPIO 引脚为复用功能
3. 设置 PWM 频率和占空比
4. 启动 PWM 输出

**关键代码：**
```c
TIM_HandleTypeDef htim3;
TIM_OC_InitTypeDef sConfigOC = {0};

void MX_TIM3_Init(void)
{
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 83;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 999;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_PWM_Init(&htim3);

  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 500;  // 50% 占空比
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1);
}

// 启动 PWM 输出
HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);

// 动态修改占空比
__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 750);
```

**17.4 通用定时器输入捕获实验**

**输入捕获配置步骤：**
1. 配置定时器为输入捕获模式
2. 配置 GPIO 引脚为复用功能
3. 使能捕获中断
4. 在中断中读取捕获值

**关键代码：**
```c
TIM_HandleTypeDef htim5;

void MX_TIM5_Init(void)
{
  htim5.Instance = TIM5;
  htim5.Init.Prescaler = 83;
  htim5.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim5.Init.Period = 0xFFFFFFFF;
  htim5.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_IC_Init(&htim5);
}

// 启动输入捕获
HAL_TIM_IC_Start_IT(&htim5, TIM_CHANNEL_1);

// 输入捕获回调函数
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM5)
  {
    uint32_t capture_value = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
  }
}
```

---

### 第十八章 高级定时器实验（第674-780页）

本章介绍高级定时器的输出比较、互补输出和 PWM 输入功能。

**18.1 高级定时器简介**
- TIM1 和 TIM8 为高级定时器
- 支持互补输出、死区插入、刹车功能
- 适用于电机控制、电源转换等应用

**18.2 高级定时器输出指定个数 PWM 实验**
- 使用定时器的重复计数器功能
- 输出指定数量的 PWM 脉冲后自动停止

**18.3 高级定时器输出比较模式实验**
- 输出比较模式用于产生精确的定时事件
- 支持冻结、匹配、翻转、强制等模式

**18.4 高级定时器互补输出带死区控制实验**
- 用于电机控制的 H 桥驱动
- 死区时间防止上下桥臂直通

**18.5 高级定时器 PWM 输入模式实验**
- 用于测量外部 PWM 信号的频率和占空比
- 使用两个通道分别捕获上升沿和下降沿

---

### 第十九章 ADC 实验（第781-900页）

本章介绍 ADC（模数转换器）的配置和使用方法。

**19.1 ADC 简介**
- 12 位逐次逼近型 ADC
- 支持单通道、多通道、扫描模式
- 支持 DMA 传输
- 支持过采样（最高 26 位分辨率）

**19.2 ADC 寄存器**
- CR：控制寄存器
- CFGR：配置寄存器
- SMPR1/2：采样时间寄存器
- LTR/HTR：看门狗阈值寄存器
- SQR1-4：规则序列寄存器
- DR：数据寄存器

**19.3 ADC HAL 库函数**
- `HAL_ADC_Init()`：初始化 ADC
- `HAL_ADC_ConfigChannel()`：配置 ADC 通道
- `HAL_ADC_Start()`：启动 ADC 转换
- `HAL_ADC_PollForConversion()`：等待转换完成
- `HAL_ADC_GetValue()`：获取转换结果
- `HAL_ADC_Start_DMA()`：启动 DMA 方式 ADC

**19.4 单通道 ADC 采集实验**
```c
ADC_HandleTypeDef hadc1;

void MX_ADC1_Init(void)
{
  hadc1.Instance = ADC1;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  HAL_ADC_Init(&hadc1);
}

// 读取 ADC 值
HAL_ADC_Start(&hadc1);
HAL_ADC_PollForConversion(&hadc1, 100);
uint32_t adc_value = HAL_ADC_GetValue(&hadc1);
float voltage = adc_value * 3.3 / 4096;
```

---

### 第二十章 DAC 实验（第901-950页）

本章介绍 DAC（数模转换器）的配置和使用方法。

**20.1 DAC 简介**
- 12 位 DAC
- 支持 8 位或 12 位模式
- 支持 DMA 传输
- 支持三角波和噪声波生成

**20.2 DAC 寄存器**
- CR：控制寄存器
- SWTRIGR：软件触发寄存器
- DHR12R1/DHR12L1：12 位右/左对齐数据保持寄存器
- DOR1：数据输出寄存器

**20.3 DAC HAL 库函数**
- `HAL_DAC_Init()`：初始化 DAC
- `HAL_DAC_ConfigChannel()`：配置 DAC 通道
- `HAL_DAC_Start()`：启动 DAC
- `HAL_DAC_SetValue()`：设置 DAC 输出值

**20.4 DAC 输出实验**
```c
DAC_HandleTypeDef hdac;

void MX_DAC_Init(void)
{
  hdac.Instance = DAC;
  HAL_DAC_Init(&hdac);
}

// 输出指定电压
HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 2048);
HAL_DAC_Start(&hdac, DAC_CHANNEL_1);
```

---

### 第二十一章 DMA 实验（第951-995页）

本章介绍 DMA（直接存储器访问）的配置和使用方法。

**21.1 DMA 简介**
- DMA 用于外设和存储器之间的数据传输
- 无需 CPU 干预，提高数据传输效率
- 支持多种传输模式和优先级配置

**21.2 DMA 控制器**
- DMA1：8 个通道
- DMA2：8 个通道
- DMAMUX：DMA 请求复用器

**21.3 DMA HAL 库函数**
- `HAL_DMA_Init()`：初始化 DMA
- `HAL_DMA_Start()`：启动 DMA 传输
- `HAL_DMA_Abort()`：中止 DMA 传输

**21.4 DMA 传输实验**
```c
DMA_HandleTypeDef hdma_usart2_tx;

void MX_DMA_Init(void)
{
  __HAL_RCC_DMA1_CLK_ENABLE();

  hdma_usart2_tx.Instance = DMA1_Stream6;
  hdma_usart2_tx.Init.Channel = DMA_CHANNEL_4;
  hdma_usart2_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
  hdma_usart2_tx.Init.PeriphInc = DMA_PINC_DISABLE;
  hdma_usart2_tx.Init.MemInc = DMA_MINC_ENABLE;
  hdma_usart2_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
  hdma_usart2_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
  hdma_usart2_tx.Init.Mode = DMA_NORMAL;
  hdma_usart2_tx.Init.Priority = DMA_PRIORITY_LOW;
  HAL_DMA_Init(&hdma_usart2_tx);

  __HAL_LINKDMA(&huart2, hdmatx, hdma_usart2_tx);
}
```

---

### 第二十二章 I2C 实验（第996-1048页）

本章介绍 I2C 总线的配置和使用方法。

**22.1 I2C 简介**
- I2C 是一种两线式串行通信协议
- 支持多主多从架构
- 标准模式：100kHz，快速模式：400kHz

**22.2 I2C 寄存器**
- CR1：控制寄存器 1
- CR2：控制寄存器 2
- OAR1/OAR2：自身地址寄存器
- TIMINGR：时序寄存器
- TXDR：发送数据寄存器
- RXDR：接收数据寄存器

**22.3 I2C HAL 库函数**
- `HAL_I2C_Init()`：初始化 I2C
- `HAL_I2C_Master_Transmit()`：主模式发送
- `HAL_I2C_Master_Receive()`：主模式接收
- `HAL_I2C_Mem_Write()`：写存储器
- `HAL_I2C_Mem_Read()`：读存储器

**22.4 I2C 实验配置**
```c
I2C_HandleTypeDef hi2c1;

void MX_I2C1_Init(void)
{
  hi2c1.Instance = I2C1;
  hi2c1.Init.Timing = 0x10909CEC;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  HAL_I2C_Init(&hi2c1);
}

// 写数据
uint8_t data[] = {0x01, 0x02};
HAL_I2C_Mem_Write(&hi2c1, 0xA0, 0x00, I2C_MEMADD_SIZE_8BIT, data, 2, 1000);

// 读数据
uint8_t rx_data[2];
HAL_I2C_Mem_Read(&hi2c1, 0xA0, 0x00, I2C_MEMADD_SIZE_8BIT, rx_data, 2, 1000);
```

---

### 第二十三章 SPI 实验（第1049-1090页）

本章介绍 SPI 总线的配置和使用方法。

**23.1 SPI 简介**
- SPI 是一种高速同步串行通信协议
- 支持全双工通信
- 4 线制：SCK、MOSI、MISO、CS

**23.2 SPI 寄存器**
- CR1：控制寄存器 1
- CR2：控制寄存器 2
- CFG1/CFG2：配置寄存器
- TXDR：发送数据寄存器
- RXDR：接收数据寄存器

**23.3 SPI HAL 库函数**
- `HAL_SPI_Init()`：初始化 SPI
- `HAL_SPI_Transmit()`：发送数据
- `HAL_SPI_Receive()`：接收数据
- `HAL_SPI_TransmitReceive()`：全双工收发

**23.4 SPI 实验配置**
```c
SPI_HandleTypeDef hspi1;

void MX_SPI1_Init(void)
{
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_HIGH;
  hspi1.Init.CLKPhase = SPI_PHASE_2EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT;
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_256;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  HAL_SPI_Init(&hspi1);
}

// 发送数据
uint8_t tx_data[] = {0x01, 0x02};
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET); // CS 拉低
HAL_SPI_Transmit(&hspi1, tx_data, 2, 1000);
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);   // CS 拉高

// 接收数据
uint8_t rx_data[2];
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
HAL_SPI_Receive(&hspi1, rx_data, 2, 1000);
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
```

---

### 第二十四章 OLED 显示实验（第1091-1150页）

本章介绍 OLED 显示屏的驱动方法。

**24.1 OLED 简介**
- 0.96 寸 OLED 显示屏
- 分辨率：128×64
- 接口：SPI 或 I2C

**24.2 OLED 驱动**
- 初始化序列
- 显示字符、字符串、数字
- 显示图片

---

### 第二十五章 I2C 光照&接近传感器实验（第1151-1200页）

本章介绍 I2C 接口的光照和接近传感器驱动。

**25.1 传感器简介**
- AP3216C：光照+接近+红外三合一传感器
- I2C 接口，地址 0x1E

**25.2 传感器驱动**
- 初始化传感器
- 读取光照强度
- 读取接近检测值

---

### 第二十六章 DS18B20 数字温度传感器实验（第1201-1250页）

本章介绍单总线协议和 DS18B20 温度传感器驱动。

**26.1 单总线简介**
- 单总线（One-Wire）通信协议
- 只需一根数据线即可通信
- 支持多设备挂载

**26.2 DS18B20 简介**
- 数字温度传感器
- 测量范围：-55℃ ~ +125℃
- 精度：±0.5℃
- 分辨率：9~12 位可调

**26.3 DS18B20 驱动**
- 初始化时序
- 读取温度命令
- 温度转换

---

### 第二十七章 DHT11 数字温湿度传感器实验（第1251-1300页）

本章介绍 DHT11 温湿度传感器驱动。

**27.1 DHT11 简介**
- 数字温湿度传感器
- 温度范围：0~50℃
- 湿度范围：20~90%RH
- 单总线通信

**27.2 DHT11 驱动**
- 初始化时序
- 读取 40 位数据
- 校验和验证

---

## 关键配置步骤

### 环境搭建

**1. 安装 Java 环境**
```bash
# 下载 Java V1.8.0_271 64位
# 安装后验证
java -version
```

**2. 安装 STM32CubeIDE 1.4.0**
- 下载地址：ST 官网
- 安装路径不能有中文
- 集成 CubeMX V6.0.0

**3. 安装 CH340 驱动**
- 用于串口调试
- 路径：开发板光盘 A-基础资料\5、开发工具\1、软件\CH340 驱动

### 工程创建

**1. 创建新工程**
- File → New → STM32 Project
- 搜索 STM32MP157DAA1
- 配置工程名称和路径

**2. 配置引脚**
- 在 Pinout & Configuration 界面配置引脚复用
- 右键引脚 → Pin Reserved → Cortex-M4（重要！）

**3. 配置时钟**
- 在 Clock Configuration 界面配置时钟树
- 默认使用 HSI（64MHz）

**4. 生成代码**
- Ctrl+S 保存 .ioc 文件
- 自动生成初始化代码

### 编译烧录

**1. 编译配置**
- 右键工程 → Properties → C/C++ Build → Settings
- 勾选 Generate binary file 和 Intel Hex file

**2. 编译工程**
- 点击锤子图标编译
- 或按 Ctrl+B

**3. 调试配置**
- 右键工程 → Debug As → Debug Configurations
- 选择 ST-LINK 或 DAP
- 配置 SWD 接口

**4. 下载调试**
- 点击 Debug 按钮
- 程序下载到 MCU SRAM
- 支持断点、单步调试

---

## 外设实验总结

### GPIO 配置

**推挽输出配置：**
```c
GPIO_InitTypeDef GPIO_InitStruct = {0};
__HAL_RCC_GPIOI_CLK_ENABLE();

GPIO_InitStruct.Pin = GPIO_PIN_0;
GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
GPIO_InitStruct.Pull = GPIO_PULLUP;
GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
HAL_GPIO_Init(GPIOI, &GPIO_InitStruct);
```

**输入配置：**
```c
GPIO_InitStruct.Pin = GPIO_PIN_0;
GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
GPIO_InitStruct.Pull = GPIO_PULLUP;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
```

**外部中断配置：**
```c
GPIO_InitStruct.Pin = GPIO_PIN_0;
GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
GPIO_InitStruct.Pull = GPIO_PULLUP;
HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
HAL_NVIC_EnableIRQ(EXTI0_IRQn);
```

### UART 配置

**UART 初始化：**
```c
UART_HandleTypeDef huart2;

huart2.Instance = USART2;
huart2.Init.BaudRate = 115200;
huart2.Init.WordLength = UART_WORDLENGTH_8B;
huart2.Init.StopBits = UART_STOPBITS_1;
huart2.Init.Parity = UART_PARITY_NONE;
huart2.Init.Mode = UART_MODE_TX_RX;
HAL_UART_Init(&huart2);
```

**串口收发：**
```c
// 发送
HAL_UART_Transmit(&huart2, (uint8_t *)"Hello", 5, 1000);

// 接收（中断方式）
uint8_t rx_data;
HAL_UART_Receive_IT(&huart2, &rx_data, 1);
```

### Timer 配置

**基本定时器中断：**
```c
TIM_HandleTypeDef htim6;

htim6.Instance = TIM6;
htim6.Init.Prescaler = 8399;
htim6.Init.Period = 9999;
HAL_TIM_Base_Init(&htim6);
HAL_TIM_Base_Start_IT(&htim6);
```

**PWM 输出：**
```c
TIM_HandleTypeDef htim3;
TIM_OC_InitTypeDef sConfigOC = {0};

htim3.Instance = TIM3;
htim3.Init.Prescaler = 83;
htim3.Init.Period = 999;
HAL_TIM_PWM_Init(&htim3);

sConfigOC.OCMode = TIM_OCMODE_PWM1;
sConfigOC.Pulse = 500;
HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1);
HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
```

### SPI 配置

**SPI 初始化：**
```c
SPI_HandleTypeDef hspi1;

hspi1.Instance = SPI1;
hspi1.Init.Mode = SPI_MODE_MASTER;
hspi1.Init.Direction = SPI_DIRECTION_2LINES;
hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
hspi1.Init.CLKPolarity = SPI_POLARITY_HIGH;
hspi1.Init.CLKPhase = SPI_PHASE_2EDGE;
hspi1.Init.NSS = SPI_NSS_SOFT;
HAL_SPI_Init(&hspi1);
```

**SPI 收发：**
```c
uint8_t tx_data[] = {0x01, 0x02};
uint8_t rx_data[2];

HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
HAL_SPI_TransmitReceive(&hspi1, tx_data, rx_data, 2, 1000);
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
```

### I2C 配置

**I2C 初始化：**
```c
I2C_HandleTypeDef hi2c1;

hi2c1.Instance = I2C1;
hi2c1.Init.Timing = 0x10909CEC;
hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
HAL_I2C_Init(&hi2c1);
```

**I2C 读写：**
```c
uint8_t data[] = {0x01, 0x02};
HAL_I2C_Mem_Write(&hi2c1, 0xA0, 0x00, I2C_MEMADD_SIZE_8BIT, data, 2, 1000);

uint8_t rx_data[2];
HAL_I2C_Mem_Read(&hi2c1, 0xA0, 0x00, I2C_MEMADD_SIZE_8BIT, rx_data, 2, 1000);
```

### ADC 配置

**ADC 初始化：**
```c
ADC_HandleTypeDef hadc1;

hadc1.Instance = ADC1;
hadc1.Init.Resolution = ADC_RESOLUTION_12B;
hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
hadc1.Init.ContinuousConvMode = DISABLE;
HAL_ADC_Init(&hadc1);
```

**ADC 读取：**
```c
HAL_ADC_Start(&hadc1);
HAL_ADC_PollForConversion(&hadc1, 100);
uint32_t adc_value = HAL_ADC_GetValue(&hadc1);
float voltage = adc_value * 3.3 / 4096;
```

### DMA 配置

**DMA 初始化：**
```c
DMA_HandleTypeDef hdma_usart2_tx;

hdma_usart2_tx.Instance = DMA1_Stream6;
hdma_usart2_tx.Init.Channel = DMA_CHANNEL_4;
hdma_usart2_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
hdma_usart2_tx.Init.PeriphInc = DMA_PINC_DISABLE;
hdma_usart2_tx.Init.MemInc = DMA_MINC_ENABLE;
HAL_DMA_Init(&hdma_usart2_tx);
```

---

## 重要注意事项

1. **引脚保留**：配置引脚后必须设置 Pin Reserved → Cortex-M4，否则不会生成初始化代码
2. **时钟使能**：操作外设前必须先使能对应时钟
3. **M4 可用外设**：严格按表 2.1.4.1 的资源分配使用 M4 外设
4. **SRAM 限制**：M4 可用 RAM 只有 384KB（0x10000000~0x1005FFFF）
5. **无内部 Flash**：程序掉电丢失，需要 A7 加载 bin 文件启动 M4
6. **调试模式**：调试阶段使用 Debug 模式，发布时切换到 Release 模式
7. **断言启用**：开发阶段启用 USE_FULL_ASSERT，发布时关闭
