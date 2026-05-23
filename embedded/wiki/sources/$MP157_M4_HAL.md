---
type: source
tags: [stm32mp157, m4, hal, bare-metal, cortex-m4]
---

# STM32MP1 M4 裸机 HAL 库开发指南

> 来源：正点原子 STM32MP1 M4裸机HAL库开发指南V1.2.2
> 总页数：923页，共34章
> 适用硬件：正点原子 STM32MP157 开发板（STM32MP157DAA3）

---

## 全文章节结构概览

| 章 | 标题 | 核心内容 |
|----|------|----------|
| 1 | 本书学习方法 | 学习顺序、参考资料、代码规范、40个例程清单 |
| 2 | STM32MP1简介 | 芯片家族、A7+M4架构、与STM32F4区别、选型 |
| 3 | 开发环境搭建 | MDK安装、ST-LINK驱动、CH340驱动 |
| 4 | STM32初体验 | MDK编译例程、ST-LINK下载调试、DAP仿真器 |
| 5 | STM32基础知识入门 | C语言复习（位操作/宏/结构体/指针）、存储系统/寄存器映射 |
| 6 | 新建MDK工程 | 从零建工程、分散加载文件、编译调试 |
| 7 | Cortex-M4内核简介 | 处理器模式、通用寄存器、FPU、堆栈、SVC/PendSV |
| 8 | STM32Cube固件包 | 固件包目录结构、CMSIS关键文件、启动文件分析 |
| 9 | 认识HAL库 | HAL库定义、与STD/LL库区别、文件结构、回调机制 |
| 10 | STM32CubeMX简介 | 安装、图形化配置、生成MDK工程 |
| 11 | 汇编LED灯实验 | GPIO寄存器、ARM汇编指令、汇编点灯 |
| 12 | C语言LED灯实验 | C语言控制GPIO、启动文件修改 |
| 13 | 结构体实现外设定义实验 | 用结构体封装寄存器访问 |
| 14 | 新建HAL库版本MDK工程 | HAL库工程框架搭建、魔术棒设置 |
| 15 | HAL库跑马灯实验 | GPIO HAL API详解 |
| 16 | 蜂鸣器实验 | GPIO输出控制 |
| 17 | 按键输入实验 | GPIO输入检测、上下拉配置 |
| 18 | 系统时钟配置实验 | 时钟树、PLL配置、RCC HAL API |
| 19 | 外部中断实验 | NVIC、EXTI配置、中断优先级 |
| 20 | 串口通信实验 | USART原理、UART HAL API、中断收发 |
| 21 | Systick高精度延时实验 | SysTick寄存器、HAL_Delay原理、us级延时 |
| 22 | 窗口门狗(WWDG)实验 | WWDG原理、寄存器、HAL API |
| 23 | 基本定时器实验 | TIM6/TIM7、定时中断 |
| 24 | 通用定时器实验 | 中断、PWM输出、输入捕获、脉冲计数 |
| 25 | 高级定时器实验 | 指定PWM个数、输出比较、互补死区、PWM输入 |
| 26 | OLED实验 | 字模制作、SSD1306驱动、SPI通信 |
| 27 | 硬件随机数实验 | RNG外设、HAL API |
| 28 | DMA实验 | 双口DMA、DMAMUX、DMA HAL API |
| 29 | ADC实验 | 单通道/多通道/DMA读取/过采样 |
| 30 | DAC实验 | DAC输出、三角波、正弦波(DMA) |
| 31 | I2C光照&接近传感器实验 | I2C协议、硬件I2C、软件I2C、AP3216C |
| 32 | DS18B20数字温度传感器实验 | 单总线协议、时序 |
| 33 | DHT11数字温湿度传感器实验 | 单总线、数据格式 |
| 34 | A7和M4联合调试 | Remoteproc框架、固件加载 |

---

## 第一章 本书学习方法

- **学习顺序**：循序渐进，从基础到入门到提高，分基础篇/入门篇/提高篇三部分
- **参考资料**：
  - 《STM32MP157参考手册》（ST官方，英文）
  - 《STM32MP157A&D数据手册》
  - 《The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors》
  - 《Cortex-M3权威指南》中文版（宋岩译）
  - 可借助《STM32H7x3参考手册(中文版)》辅助学习（STM32MP1外设与STM32H7几乎一致）
- **编写规范**：每章分4部分——外设功能介绍、硬件设计、程序设计、下载验证
- **代码规范**：doxgen注释风格、4空格TAB、全局变量g_前缀、指针p_前缀
- **例程清单**：共40个HAL库版本例程，从汇编LED到A7+M4联合调试

---

## 第二章 STM32MP1简介

### 2.1 初识STM32MP1

- **STM32MP1系列三条产品线**：
  - STM32MP151：单核A7(650/800MHz) + 单核M4(209MHz)，无GPU
  - STM32MP153：双核A7(650/800MHz) + 单核M4(209MHz)，无GPU
  - STM32MP157：双核A7(650/800MHz) + 单核M4(209MHz)，有3D GPU
- **正点原子开发板**使用STM32MP157DAA3（STM32MP157最强型号）
- **多核异构架构**：Cortex-A7运行Linux，Cortex-M4运行裸机/RTOS，实现实时控制
- **STM32MP1可看作STM32H7的换核版**，基础外设几乎一致

### 2.2 M4内核与STM32F4单片机区别

- **开发工具相同**：MDK、IAR、STM32CubeIDE，ST-LINK/JLink调试
- **存储差异**：M4内核无内部Flash，程序加载到SRAM运行（掉电丢失），需A7端Linux加载.bin文件
- **资源共享**：A7+M4共享外设资源，部分资源仅A7可访问（ST已做划分）

### 2.3 STM32MP1设计选型

- STM32MP1系列、命名规则、选型指南、设计注意事项

---

## 第三章 开发环境搭建

- **MDK安装**：Keil MDK5安装
- **仿真器驱动**：ST-LINK驱动安装
- **ST-LINK固件更新**
- **CH340 USB虚拟串口驱动**：用于串口调试

---

## 第四章 STM32初体验

- **MDK5编译例程**：打开工程、编译、查看编译结果
- **ST-LINK下载与调试**：工程调试设置、仿真调试、断点/单步
- **MDK5使用技巧**：文本美化、语法检测、代码提示、编辑技巧
- **DAP仿真器**：CMSIS-DAP连接、MDK配置
- **无线调试器**：无线调试配置

---

## 第五章 STM32基础知识入门

### 5.1 C语言基础复习
- **位操作**：与、或、异或、取反、左移、右移
- **define宏定义**：常量定义、带参宏
- **ifdef条件编译**：头文件保护、功能开关
- **extern变量声明**：跨文件共享变量
- **typedef类型别名**：简化结构体/指针类型
- **结构体**：声明定义、成员访问、内存对齐
- **关键字**：volatile（防编译器优化）、const（只读修饰）、static（作用域限制）
- **指针**：指针变量、指针运算、函数指针

### 5.2 STM32MP157存储系统
- **寄存器基础知识**：寄存器是外设的控制/状态/数据接口
- **总线结构**：AHB、APB总线层次
- **存储器映射**：4GB地址空间分配
- **寄存器地址**：基地址+偏移量
- **寄存器映射**：用C语言结构体映射寄存器组

---

## 第六章 新建MDK工程

- **新建工程**：选择芯片型号、配置工程选项
- **新建程序文件**：添加.c/.h文件
- **分散加载文件(.sct)**：定义代码和数据的内存布局
- **编译和调试**：编译、下载、在线调试
- **清理工程**：删除中间文件

---

## 第七章 Cortex-M4内核简介

- **Cortex-M3/M4处理器**：ARMv7-M架构，Thumb-2指令集
- **通用寄存器**：R0-R12、SP(R13)、LR(R14)、PC(R15)、xPSR
- **操作模式**：线程模式(Thread)和处理模式(Handler)
- **特权级别**：特权级和用户级
- **FPU单元**：单精度浮点运算、FPU寄存器(S0-S31)、Lazy Stacking优化
- **堆栈**：MSP(主堆栈)和PSP(进程堆栈)双堆栈机制
- **SVC和PendSV异常**：SVC用于系统服务调用，PendSV用于上下文切换（RTOS核心）

---

## 第八章 STM32Cube固件包

### 8.1 获取固件包
- ST官网搜索STM32CubeMP1下载
- 固件包版本：STM32Cube_FW_MP1_V1.2.0

### 8.2 固件包目录结构

| 文件夹 | 内容 |
|--------|------|
| Drivers/BSP | 板级支持包（触摸屏、LCD、SRAM等驱动） |
| Drivers/CMSIS | CMSIS标准文件（启动文件、内核文件、外设头文件） |
| Drivers/STM32MP1xx_HAL_Driver | HAL库源码（Src+Inc） |
| Middlewares/Third_Party/FreeRTOS | FreeRTOS实时系统支持包 |
| Middlewares/Third_Party/OpenAMP | 非对称多处理框架（RPMsg、VirtIO、Remoteproc） |
| Projects | 官方Demo板示例工程（Applications/Demonstrations/Examples/Templates） |
| Utilities | 资源管理器配置（共享内存、ETZPC设备表） |

### 8.3 CMSIS关键文件

| 文件 | 作用 |
|------|------|
| stm32mp1xx.h | 顶层头文件，包含芯片型号判断和外设头文件 |
| stm32mp157dxx_cm4.h | M4内核专用：寄存器结构体定义、基地址宏、中断号 |
| stm32mp157dxx_ca7.h | A7内核专用头文件 |
| system_stm32mp1xx.c | 系统初始化（SystemCoreClock变量、SystemInit函数） |
| startup_stm32mp15xx.s | M4启动文件：堆栈初始化、中断向量表、Reset_Handler |
| stm32mp15xx_m4.sct | MDK分散加载文件（链接脚本），定义SRAM中的代码/数据布局 |

**启动文件分析**：
- 定义栈大小(Stack_Size EQU 0x400)和堆大小(Heap_Size EQU 0x200)
- 中断向量表：从0x00000000开始，前16个是系统异常，后240个是外部中断
- Reset_Handler：调用SystemInit，然后跳转到main

**分散加载文件(.sct)**：
- 定义M4代码加载到SRAM1/SRAM2/SRAM3区域
- 定义RW_IRAM1（可读写数据）和ARM_LIB_STACK/ARM_LIB_HEAP区域

---

## 第九章 认识HAL库

### 9.1 HAL库基础概念

- **API（应用程序编程接口）**：封装好的可调用功能函数
- **句柄（Handle）**：指针或索引，用于描述和访问资源
- **HAL（Hardware Abstraction Layer）**：硬件抽象层，将寄存器操作封装为API

### 9.2 HAL库与STD库、LL库的区别

| 库类型 | 特点 | 支持范围 |
|--------|------|----------|
| STD标准外设库 | 结构体封装寄存器，接近硬件，可移植性差 | 仅F0-F4/L1 |
| HAL库 | 软硬件分离，通用API，可移植性好 | 全STM32系列 |
| LL库(Low Layer) | 轻量级、高性能、面向专家，可独立或与HAL混合使用 | 与HAL捆绑 |

**STM32MP1目前仅支持HAL库。**

### 9.3 HAL库文件夹结构

```
STM32MP1xx_HAL_Driver/
├── Inc/                    # 头文件
│   ├── stm32mp1xx_hal*.h   # HAL库头文件
│   └── stm32mp1xx_ll_*.h   # LL库头文件
├── Src/                    # 源文件
│   ├── stm32mp1xx_hal*.c   # HAL库源文件
│   └── stm32mp1xx_ll_*.c   # LL库源文件
├── Release_Notes.html      # 版本更新说明
└── STM32MP157Cxx_CM4_User_Manual.chm  # HAL库用户手册
```

### 9.4 HAL库命名规则

**文件命名**：
- `stm32mp1xx_hal_ppp.c/h` — 外设通用驱动
- `stm32mp1xx_hal_ppp_ex.c/h` — 外设扩展功能
- `stm32mp1xx_ll_ppp.c/h` — LL库底层驱动

**函数命名**：
- `HAL_PPP_Init()` / `HAL_PPP_DeInit()` — 初始化/反初始化
- `HAL_PPP_Read()` / `HAL_PPP_Write()` — 读写操作
- `HAL_PPP_Transmit()` / `HAL_PPP_Receive()` — 发送/接收
- `HAL_PPP_Set()` / `HAL_PPP_Get()` — 控制函数
- `HAL_PPP_GetState()` / `HAL_PPP_GetError()` — 状态查询

**句柄命名**：`PPP_HandleTypeDef`（如`UART_HandleTypeDef`、`TIM_HandleTypeDef`）

**结构体命名**：`PPP_InitTypeDef`（如`UART_InitTypeDef`、`TIM_InitTypeDef`）

### 9.5 回调函数机制

HAL库大量使用回调函数（Callback），用户可重定义：

| 回调函数类型 | 示例 | 说明 |
|-------------|------|------|
| HAL_PPP_MspInit/DeInit | HAL_USART_MspInit() | 由HAL_PPP_Init()调用，配置GPIO/时钟/DMA/中断 |
| HAL_PPP_ProcessCpltCallback | HAL_USART_TxCpltCallback | 中断/DMA完成时调用 |
| HAL_PPP_ErrorCallback | HAL_USART_ErrorCallback | 错误处理 |

**回调注册机制**：在stm32mp1xx_hal_conf.h中设置`USE_HAL_PPP_REGISTER_CALLBACKS`为1U可启用函数指针注册方式。

### 9.6 HAL库重要文件

**stm32mp1xx_hal_conf.h**：
- 外设模块使能（`#define HAL_TIM_MODULE_ENABLED`）
- 回调函数注册选择（`USE_HAL_PPP_REGISTER_CALLBACKS`）
- 时钟配置：HSE=24MHz、HSI=64MHz、LSI=32KHz、LSE=32.768KHz

**stm32mp1xx_hal.c**：
- `HAL_Init()` — HAL库初始化（配置Flash预取、SysTick、NVIC优先级分组）
- `HAL_DeInit()` — 反初始化
- `HAL_InitTick()` — SysTick初始化
- `HAL_Delay()` — 毫秒延时
- `HAL_GetTick()` — 获取当前tick值

### 9.7 HAL库常用宏定义

| 宏 | 作用 |
|----|------|
| `__HAL_PPP_ENABLE_IT(__HANDLE__, __INTERRUPT__)` | 使能外设中断 |
| `__HAL_PPP_DISABLE_IT(...)` | 禁用外设中断 |
| `__HAL_PPP_GET_FLAG(...)` | 获取状态标记 |
| `__HAL_PPP_CLEAR_FLAG(...)` | 清除状态标记 |
| `__HAL_PPP_ENABLE(__HANDLE__)` | 使能外设 |
| `__HAL_PPP_DISABLE(__HANDLE__)` | 禁用外设 |

---

## 第十章 STM32CubeMX简介

- **作用**：图形化配置GPIO/时钟/外设，自动生成初始化代码
- **安装**：需先安装JAVA环境，再安装STM32CubeMX
- **使用流程**：
  1. 打开STM32CubeMX，下载关联固件包
  2. 选择芯片型号（STM32MP157Dxx）
  3. 配置HSE/LSE时钟源
  4. 配置时钟树（PLL、分频器）
  5. 配置GPIO功能引脚
  6. 生成MDK工程源码
  7. 添加用户程序

**界面窗口**：
- Pinout & Configuration：外设栏、引脚配置、System view
- Clock Configuration：时钟树配置
- Project Manager：工程选项、代码生成器、高级设置
- Tools：其他工具

---

## 第十一章 汇编LED灯实验

### GPIO简介

**STM32MP15的GPIO**：
- GPIOA~GPIOK，共11组，每组16个引脚
- 正点原子开发板引出144个GPIO（共184个）

**GPIO功能模式**（8种）：
- 输入浮空、输入上拉、输入下拉、模拟功能
- 开漏输出、推挽输出
- 开漏式复用功能、推挽式复用功能

**GPIO寄存器**：
| 寄存器 | 功能 |
|--------|------|
| MODER | 端口模式控制（输入/输出/复用/模拟） |
| OTYPER | 输出类型（推挽/开漏） |
| OSPEEDR | 输出速度等级 |
| PUPDR | 上拉/下拉配置 |
| IDR | 输入数据寄存器 |
| ODR | 输出数据寄存器 |
| BSRR | 置位/复位寄存器（原子操作） |
| BRR | 清除寄存器 |
| LCKR | 配置锁存寄存器 |
| AFR[2] | 复用功能选择（AFR[0]=AF0-AF7, AFR[1]=AF8-AF15） |

**使能GPIO时钟**：通过RCC_AHB4ENR寄存器使能对应GPIO端口时钟

### ARM汇编指令

| 指令 | 功能 |
|------|------|
| EQU | 定义常量 |
| CMP | 比较 |
| LDR | 从存储器加载数据到寄存器 |
| STR | 将寄存器数据存储到存储器 |
| MOV | 数据传输 |
| MRS/MSR | 读/写特殊寄存器 |
| PUSH/POP | 压栈/出栈 |
| B/BL/BX/BLX | 跳转指令 |

---

## 第十二章 C语言LED灯实验

- 用C语言操作GPIO寄存器控制LED
- 修改启动文件（startup_stm32mp15xx.s）添加C入口
- 定义GPIO寄存器结构体映射
- 编写main.h和main.c

---

## 第十三章 结构体实现外设定义实验

- 用结构体封装GPIO外设寄存器
- 通过结构体指针访问寄存器
- 实现LED控制的结构化代码

---

## 第十四章 新建HAL库版本MDK工程

- **文件夹结构**：Drivers、Middlewares、Output、Projects、User
- **工程分组**：按功能模块分组（USER、DRIVERS、CMSIS等）
- **MDK搜索路径**：添加HAL库和CMSIS的Include路径
- **魔术棒设置**：
  - 全局宏定义：`STM32MP157Dxx,USE_HAL_DRIVER`
  - 编译中间文件路径
  - 生成.hex文件
  - 分散加载文件(.sct)
  - 编译器版本选择

---

## 第十五章 HAL库跑马灯实验 — GPIO HAL API

### 关键API函数

**1. HAL_GPIO_Init**
```c
void HAL_GPIO_Init(GPIO_TypeDef *GPIOx, GPIO_InitTypeDef *GPIO_Init);
```
- GPIOx：GPIOA~GPIOK
- GPIO_Init结构体成员：
  - `Pin`：GPIO_PIN_0~GPIO_PIN_15，GPIO_PIN_All
  - `Mode`：GPIO_MODE_INPUT / GPIO_MODE_OUTPUT_PP / GPIO_MODE_OUTPUT_OD / GPIO_MODE_AF_PP / GPIO_MODE_AF_OD / GPIO_MODE_ANALOG / GPIO_MODE_IT_RISING等
  - `Pull`：GPIO_NOPULL / GPIO_PULLUP / GPIO_PULLDOWN
  - `Speed`：GPIO_SPEED_FREQ_LOW / MEDIUM / HIGH / VERY_HIGH
  - `Alternate`：GPIO_AF0_USART1~GPIO_AF15等

**2. HAL_GPIO_DeInit** — 反初始化GPIO

**3. HAL_GPIO_ReadPin**
```c
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);
```
- 返回：GPIO_PIN_SET 或 GPIO_PIN_RESET

**4. HAL_GPIO_WritePin**
```c
void HAL_GPIO_WritePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, GPIO_PinState PinState);
```
- 操作BSRR寄存器实现原子读写

**5. HAL_GPIO_TogglePin** — 翻转GPIO引脚状态

**6. HAL_GPIO_LockPin** — 锁定GPIO引脚配置

### 跑马灯实验设计
- LED0(PI0)和LED1(PF3)交替闪烁
- 使能GPIO时钟：`__HAL_RCC_GPIOI_CLK_ENABLE()` / `__HAL_RCC_GPIOF_CLK_ENABLE()`
- 配置为推挽输出模式，无上下拉，高速

---

## 第十六章 蜂鸣器实验

- 蜂鸣器通过GPIO控制（PB12）
- 配置为推挽输出
- 高电平响，低电平停

---

## 第十七章 按键输入实验

- **按键检测原理**：读取GPIO输入电平，配合消抖处理
- **上下拉原则**：按键未按下时确保引脚有确定电平
- KEY0(PH3)、KEY1(PH2)、KEY2(PC13)
- 配置为输入模式，上拉/下拉根据硬件电路选择

---

## 第十八章 系统时钟配置实验

### 时钟源
- **HSE**：高速外部振荡器，24MHz（开发板晶振）
- **HSI**：高速内部振荡器，64MHz
- **CSI**：低功耗内部振荡器
- **LSE**：低速外部振荡器，32.768KHz
- **LSI**：低速内部振荡器，32KHz

### 时钟树关键节点
- **PLL1**：为MPU(Cortex-A7)提供时钟
- **PLL2**：为AXI总线和部分外设提供时钟
- **PLL3**：为MCU(Cortex-M4)提供时钟，MCU时钟=209MHz
- **PLL4**：为外设（UART、SPI、I2C等）提供时钟

### RCC HAL API

| 函数 | 功能 |
|------|------|
| `HAL_RCC_DeInit()` | RCC反初始化 |
| `HAL_RCC_OscConfig()` | 配置振荡器（HSE/HSI/PLL） |
| `HAL_RCC_ClockConfig()` | 配置系统时钟源和分频器 |
| `HAL_RCC_GetSystemCoreClockFreq()` | 获取系统核心时钟频率 |
| `HAL_RCCEx_PeriphCLKConfig()` | 配置外设时钟源 |

### 时钟配置示例
```c
RCC_OscInitTypeDef RCC_OscInitStruct = {0};
RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

// 配置HSE和PLL
RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
RCC_OscInitStruct.HSEState = RCC_HSE_ON;
RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
RCC_OscInitStruct.PLL.PLLM = 12;
RCC_OscInitStruct.PLL.PLLN = 288;
RCC_OscInitStruct.PLL.PLLP = 2;
RCC_OscInitStruct.PLL.PLLQ = 2;
RCC_OscInitStruct.PLL.PLLR = 2;
HAL_RCC_OscConfig(&RCC_OscInitStruct);

// 配置总线时钟分频
RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1;
RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_4);
```

---

## 第十九章 外部中断实验

### NVIC（嵌套向量中断控制器）
- 支持240个外部中断
- 可编程优先级（4位抢占优先级+4位子优先级）
- NVIC相关函数：
  - `HAL_NVIC_SetPriority(IRQn, PreemptPriority, SubPriority)` — 设置优先级
  - `HAL_NVIC_EnableIRQ(IRQn)` — 使能中断
  - `HAL_NVIC_DisableIRQ(IRQn)` — 禁用中断

### EXTI（外部中断/事件控制器）
- 每个GPIO端口可映射到EXTI线（通过SYSCFG寄存器）
- 支持上升沿/下降沿/双边沿触发
- 配置步骤：
  1. 使能GPIO时钟和SYSCFG时钟
  2. 配置GPIO为输入模式
  3. 配置EXTI线映射到对应GPIO端口
  4. 配置EXTI触发方式
  5. 使能NVIC中断
  6. 编写中断服务函数和回调函数

---

## 第二十章 串口通信实验

### 串口基础知识
- **通信方式**：串行/并行
- **传输方向**：单工/半双工/全双工
- **同步方式**：同步/异步
- **波特率**：每秒传输的二进制位数（bps）

### STM32MP157串口资源
- 支持USART和UART
- USART支持同步和异步模式，UART仅支持异步
- 串口时钟来自PLL4

### UART HAL API

**关键结构体**：

```c
// 初始化结构体
typedef struct {
  uint32_t BaudRate;          // 波特率（如115200）
  uint32_t WordLength;        // 数据位（8或9位）
  uint32_t StopBits;          // 停止位（0.5/1/1.5/2）
  uint32_t Parity;            // 校验（无/奇/偶）
  uint32_t Mode;              // 模式（收/发/收发）
  uint32_t HwFlowCtl;         // 硬件流控
  uint32_t OverSampling;      // 过采样（8倍/16倍）
  uint32_t OneBitSampling;    // 单样本/多样本
  uint32_t ClockPrescaler;    // 时钟预分频器
} UART_InitTypeDef;

// 句柄结构体
typedef struct __UART_HandleTypeDef {
  USART_TypeDef *Instance;            // 寄存器基地址
  UART_InitTypeDef Init;              // 通信参数
  uint8_t *pTxBuffPtr;                // 发送缓冲区指针
  uint16_t TxXferSize;                // 发送数据大小
  __IO uint16_t TxXferCount;          // 发送计数器
  uint8_t *pRxBuffPtr;                // 接收缓冲区指针
  uint16_t RxXferSize;                // 接收数据大小
  __IO uint16_t RxXferCount;          // 接收计数器
  DMA_HandleTypeDef *hdmatx;          // 发送DMA句柄
  DMA_HandleTypeDef *hdmarx;          // 接收DMA句柄
  __IO HAL_UART_StateTypeDef gState;  // 发送状态
  __IO HAL_UART_StateTypeDef RxState; // 接收状态
} UART_HandleTypeDef;
```

**关键API函数**：

| 函数 | 功能 |
|------|------|
| `HAL_UART_Init()` | 初始化UART |
| `HAL_UART_DeInit()` | 反初始化 |
| `HAL_UART_Transmit()` | 查询方式发送（阻塞） |
| `HAL_UART_Receive()` | 查询方式接收（阻塞） |
| `HAL_UART_Transmit_IT()` | 中断方式发送 |
| `HAL_UART_Receive_IT()` | 中断方式接收 |
| `HAL_UART_Transmit_DMA()` | DMA方式发送 |
| `HAL_UART_Receive_DMA()` | DMA方式接收 |
| `HAL_UART_IRQHandler()` | 中断处理函数 |
| `HAL_UART_TxCpltCallback()` | 发送完成回调 |
| `HAL_UART_RxCpltCallback()` | 接收完成回调 |

**中断收发流程**：
1. 调用`HAL_UART_Receive_IT()`启动中断接收
2. 数据到达触发USART中断
3. 中断服务函数调用`HAL_UART_IRQHandler()`
4. HAL库自动清除中断标志并调用`HAL_UART_RxCpltCallback()`
5. 在回调函数中处理数据并重新启动接收

**GPIO复用功能配置**：
- 通过`GPIO_InitTypeDef.Alternate`设置AF映射
- 如`GPIO_AF7_USART1`将引脚复用为USART1功能

---

## 第二十一章 Systick高精度延时实验

### SysTick简介
- 24位倒计数定时器，内嵌在Cortex-M4内核中
- 时钟源：系统时钟或系统时钟/8
- 寄存器：STK_CTRL、STK_LOAD、STK_VAL、STK_CALIB

### HAL库SysTick驱动
- `HAL_InitTick()` — 初始化SysTick
- `HAL_GetTickPrio()` — 获取SysTick中断优先级
- `HAL_SetTickFreq()` / `HAL_GetTickFreq()` — 设置/获取tick频率

### HAL_Delay函数分析
- SysTick分频值为1时：SystemCoreClock/1000得到1ms计数值
- SystemClock_Config执行前后HAL_Delay行为不同

### 高精度延时（无操作系统）
```c
void delay_us(uint32_t nus);  // 微秒延时
void delay_ms(uint16_t nms);  // 毫秒延时
```
- 使用SysTick寄存器直接操作实现us级延时

---

## 第二十二章 窗口门狗（WWDG）实验

- **WWDG特点**：在窗口期内必须喂狗，过早或过晚都会复位
- **框图**：7位递减计数器、预分频器、窗口值
- **寄存器**：WWDG_CR（控制）、WWDG_CFR（配置）、WWDG_SR（状态）
- **HAL API**：
  - `HAL_WWDG_Init()` — 初始化
  - `HAL_WWDG_Refresh()` — 喂狗
  - `HAL_WWDG_IRQHandler()` — 中断处理
  - `HAL_WWDG_EarlyWakeupCallback()` — 早期唤醒回调

---

## 第二十三章 基本定时器实验

- **TIM6/TIM7**：最简单的定时器，仅支持定时中断和DAC触发
- **框图**：时钟源→预分频器(PSC)→计数器(CNT)→自动重载(ARR)
- **寄存器**：CR1、DIER、SR、CNT、PSC、ARR、EGR
- **定时时间计算**：`Tout = ((arr+1)*(psc+1)) / Ft`（Ft=定时器时钟频率）
- **HAL API**：
  - `HAL_TIM_Base_Init()` — 初始化
  - `HAL_TIM_Base_Start_IT()` — 启动定时中断
  - `HAL_TIM_IRQHandler()` — 中断处理
  - `HAL_TIM_PeriodElapsedCallback()` — 溢出回调

---

## 第二十四章 通用定时器实验

### TIM2/TIM3/TIM4/TIM5
- 32位/16位计数器，支持向上/向下/中心对齐计数
- 支持输入捕获、输出比较、PWM输出、脉冲计数

### 24.2 通用定时器中断
- 配置流程：使能时钟→设置句柄参数→HAL_TIM_Base_Init()→设置NVIC→HAL_TIM_Base_Start_IT()

### 24.3 PWM输出实验
- **PWM原理**：通过比较CNT和CCR值控制输出电平
- **边沿对齐**：向上计数，CNT<CCR时有效电平
- **中心对齐**：上下计数，对称PWM波形
- **HAL API**：
  - `HAL_TIM_PWM_Init()` — PWM初始化
  - `HAL_TIM_PWM_ConfigChannel()` — 配置PWM通道
  - `HAL_TIM_PWM_Start()` — 启动PWM输出
  - 修改CCR值改变占空比：`__HAL_TIM_SET_COMPARE(&htim, TIM_CHANNEL_x, pulse)`

### 24.4 输入捕获实验
- **原理**：捕获外部信号的边沿时刻，测量脉宽/频率
- **HAL API**：
  - `HAL_TIM_IC_Init()` — 输入捕获初始化
  - `HAL_TIM_IC_ConfigChannel()` — 配置捕获通道
  - `HAL_TIM_IC_Start_IT()` — 启动中断捕获
  - `HAL_TIM_ReadCapturedValue()` — 读取捕获值

### 24.5 脉冲计数实验（外部时钟模式1）
- 配置从模式为外部时钟模式1
- 使用`HAL_TIM_SlaveConfigSynchronization()`配置从模式

---

## 第二十五章 高级定时器实验

### TIM1/TIM8
- 16位计数器，支持互补输出、死区插入、重复计数器

### 25.2 输出指定个数PWM
- 利用重复计数器(RCR)和更新中断实现
- RCR=N时，N+1次溢出产生一次更新事件

### 25.3 输出比较模式
- 与PWM模式的区别：OC模式在CNT==CCR时翻转/置位/清除输出
- HAL API：`HAL_TIM_OC_Init()`、`HAL_TIM_OC_ConfigChannel()`、`HAL_TIM_OC_Start()`

### 25.4 互补输出带死区控制
- **互补输出**：CHx和CHxN输出互补信号，用于H桥驱动
- **死区时间**：防止上下桥臂同时导通
- **HAL API**：
  - `HAL_TIMEx_ConfigBreakDeadTime()` — 配置死区
  - `HAL_TIMEx_PWMN_Start()` — 启动互补PWM

### 25.5 PWM输入模式
- 自动测量PWM信号的频率和占空比
- 使用从模式自动复位计数器

---

## 第二十六章 OLED实验

- **字符编码**：ASCII、GB2312
- **字模制作**：像素→点阵→十六进制数据
- **SSD1306驱动**：128x64 OLED，支持8080并口和4线SPI
- **显存管理**：GDDRAM存储显示数据
- **命令集**：设置列地址、页地址、对比度、显示开关等
- **实验内容**：显示字符/数字、显示图片、显示动图、显示汉字

---

## 第二十七章 硬件随机数实验

- **RNG外设**：基于模拟噪声源的真随机数发生器
- **HAL API**：
  - `HAL_RNG_Init()` — 初始化
  - `HAL_RNG_GenerateRandomNumber()` — 生成32位随机数
- **寄存器**：RNG_CR（控制）、RNG_SR（状态）、RNG_DR（数据）

---

## 第二十八章 DMA实验

### DMA简介
- **双口DMA**：DMA1(8个流)和DMA2(8个流)
- **MDMA**：用于更高带宽传输
- **DMAMUX**：DMA请求复用器，将外设请求映射到DMA流

### DMA HAL API

**DMA_HandleTypeDef句柄**：包含Instance、Init、回调函数指针、状态信息

**DMA_InitTypeDef结构体**：
- `Request`：DMA请求源（通过DMAMUX选择外设）
- `Direction`：传输方向（外设→存储器/存储器→外设/存储器→存储器）
- `PeriphInc` / `MemInc`：外设/存储器地址是否递增
- `PeriphDataAlignment` / `MemDataAlignment`：数据宽度（8/16/32位）
- `Mode`：普通模式/循环模式
- `Priority`：优先级（低/中/高/非常高）
- `FIFOMode`：FIFO模式开关
- `MemBurst` / `PeriphBurst`：突发模式

**关键函数**：
| 函数 | 功能 |
|------|------|
| `HAL_DMA_Init()` | DMA初始化 |
| `HAL_UART_Transmit_DMA()` | 串口DMA发送 |
| `HAL_UART_Receive_DMA()` | 串口DMA接收 |
| `HAL_DMA_Start_IT()` | 中断方式启动DMA |
| `HAL_DMA_Start()` | 启动DMA |
| `HAL_UART_DMAStop()` | 停止DMA传输 |

**回调函数**：
- `XferCpltCallback` — 传输完成
- `XferHalfCpltCallback` — 半传输完成
- `XferErrorCallback` — 传输错误

---

## 第二十九章 ADC实验

### ADC特性
- 16位分辨率（支持过采样到26位）
- 最大时钟36MHz
- 支持单通道/多通道、单次/连续/扫描模式
- 支持DMA传输

### ADC HAL API

**ADC_HandleTypeDef句柄**：包含Instance、Init、DMA_Handle、State

**ADC_InitTypeDef结构体**：
- `ClockPrescaler`：预分频系数（1/2/4/6/8/.../256）
- `Resolution`：分辨率（16/12/10/8位）
- `ScanConvMode`：扫描模式开关
- `ContinuousConvMode`：连续转换开关
- `NbrOfConversion`：转换通道数（1~16）
- `ExternalTrigConv`：外部触发源
- `OversamplingMode`：过采样模式开关

**关键函数**：
| 函数 | 功能 |
|------|------|
| `HAL_ADC_Init()` | ADC初始化 |
| `HAL_ADCEx_Calibration_Start()` | ADC校准（必须在使用前执行） |
| `HAL_ADC_ConfigChannel()` | 配置ADC通道 |
| `HAL_ADC_Start()` | 启动ADC转换 |
| `HAL_ADC_PollForConversion()` | 等待转换完成 |
| `HAL_ADC_GetValue()` | 获取转换结果 |
| `HAL_ADC_Start_DMA()` | DMA方式启动ADC |

**实验内容**：
1. 单通道ADC采集（轮询方式）
2. 单通道ADC采集（DMA读取）
3. 多通道ADC采集（DMA读取，扫描模式+不连续转换）
4. 单通道ADC过采样（26位分辨率）

---

## 第三十章 DAC实验

### DAC特性
- 12位DAC，支持8位/12位数据格式
- 支持外部触发和DMA请求
- 输出引脚：DAC_OUT1(PA4)、DAC_OUT2(PA5)

### DAC HAL API
| 函数 | 功能 |
|------|------|
| `HAL_DAC_Init()` | DAC初始化 |
| `HAL_DAC_ConfigChannel()` | 配置DAC通道 |
| `HAL_DAC_Start()` | 启动DAC输出 |
| `HAL_DAC_SetValue()` | 设置DAC输出值 |
| `HAL_DAC_GetValue()` | 获取当前DAC值 |
| `HAL_DAC_Start_DMA()` | DMA方式启动DAC |

**实验内容**：
1. DAC输出固定电压
2. DAC输出三角波（硬件自动递增/递减）
3. DAC输出正弦波（DMA方式，定时器触发）

---

## 第三十一章 I2C光照&接近传感器实验

### I2C协议
- 两线制：SCL（时钟）+ SDA（数据）
- 支持多主多从，7位/10位地址
- 时序：起始条件→地址+读写位→数据→应答→停止条件

### STM32MP157 I2C
- 支持主/从模式
- 支持SMBus协议
- 内置噪声滤波器

### I2C HAL API
| 函数 | 功能 |
|------|------|
| `HAL_I2C_Master_Transmit()` | 主机发送 |
| `HAL_I2C_Master_Receive()` | 主机接收 |
| `HAL_I2C_Mem_Write()` | 写设备寄存器 |
| `HAL_I2C_Mem_Read()` | 读设备寄存器 |
| `HAL_I2C_Slave_Transmit()` | 从机发送 |
| `HAL_I2C_Slave_Receive()` | 从机接收 |

### AP3216C传感器
- 集成光照传感器(ALS)、接近传感器(PS)、红外LED
- I2C地址：0x1E
- 支持硬件I2C和软件I2C两种驱动方式

---

## 第三十二章 DS18B20数字温度传感器实验

- **单总线协议**：仅需一根数据线
- **通信时序**：初始化→ROM指令→RAM指令
- **温度转换**：12位分辨率，精度0.0625度
- 通过精确延时实现单总线时序

---

## 第三十三章 DHT11数字温湿度传感器实验

- **单总线结构**：一根数据线
- **数据格式**：40bit = 8bit湿度整数 + 8bit湿度小数 + 8bit温度整数 + 8bit温度小数 + 8bit校验
- **时序**：主机拉低18ms→拉高20-40us→DHT11响应→数据传输

---

## 第三十四章 A7和M4联合调试

### Remoteproc框架
- **作用**：允许A7主处理器控制M4协处理器的生命周期（加载、启动、停止）
- **组件**：
  - remoteproc：通用远程处理框架，加载.axf固件、解析资源表、控制启动/关闭
  - stm32_rproc：M4平台驱动，注册回调、处理平台资源、邮箱通知
  - RPMsg：远程处理器消息传递，通过共享内存通信
  - VirtIO：虚拟化模块

### 固件加载流程
1. 启动Linux系统（A7端）
2. 将M4固件(.axf文件)传输到开发板的`/lib/firmware`目录
3. 通过sysfs接口加载和控制：
   ```bash
   # 启动M4
   echo start > /sys/class/remoteproc/remoteproc0/state
   # 停止M4
   echo stop > /sys/class/remoteproc/remoteproc0/state
   ```

### 工程模式vs量产模式
- **工程模式（Engineering Mode）**：ST-LINK在线仿真，程序下载到SRAM运行，掉电丢失
- **量产模式（Production Mode）**：A7端Linux加载M4固件，适合核间通信和产品部署

---

## HAL 库架构总结

### 三层架构
```
用户应用层
    ↓
HAL库API层（硬件抽象）
    ↓
CMSIS层（内核访问）
    ↓
硬件寄存器
```

### HAL库 vs LL库
| 特性 | HAL库 | LL库 |
|------|-------|------|
| 抽象层次 | 高，隐藏寄存器细节 | 低，接近寄存器操作 |
| 可移植性 | 好，跨STM32系列通用 | 差，与芯片相关 |
| 执行效率 | 中等 | 高 |
| 代码体积 | 较大 | 小 |
| 适用场景 | 快速开发、项目移植 | 性能关键代码 |
| STM32MP1支持 | 支持 | 部分支持 |

### 回调机制
HAL库通过回调函数实现事件驱动编程：
1. `HAL_PPP_Init()`内部调用`HAL_PPP_MspInit()`（用户重定义，配置GPIO/时钟/DMA）
2. 中断/DMA完成时调用`HAL_PPP_ProcessCpltCallback()`（用户重定义，处理数据）
3. 错误发生时调用`HAL_PPP_ErrorCallback()`（用户重定义，错误处理）

### 典型外设使用流程
```
1. 使能外设时钟
2. 配置GPIO复用功能
3. 定义PPP_HandleTypeDef句柄
4. 填充PPP_InitTypeDef结构体
5. 调用HAL_PPP_Init()
6. 配置NVIC中断优先级
7. 调用HAL_PPP_Start_IT()或HAL_PPP_Transmit_DMA()
8. 实现中断服务函数（调用HAL_PPP_IRQHandler）
9. 重定义回调函数处理事件
```
