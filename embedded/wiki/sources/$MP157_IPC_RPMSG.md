---
title: STM32MP1 异核通信(基于 CubeIDE)
source: 【正点原子】STM32MP1异核通信(基于CubeIDE) V1.1.pdf
type: source
tags: [ipc, rpmsg, stm32mp1, dual-core, freertos, openamp, remoteproc, virtio]
created: 2026-05-24
---

# STM32MP1 异核通信(基于 CubeIDE)

正点原子出品，共 206 页，系统讲解 STM32MP157 Cortex-A7(Linux) 与 Cortex-M4(RTOS/裸机) 之间的异核通信实现。核心框架为 **OpenAMP**，通信基础为 **共享内存 + IPCC 中断通知**。

---

## 第一章 配置 OpenAMP

本章不讲原理，直接动手配置 M4 工程，为后续异核通信实验做准备。

### 1.1 配置 M4 工程

在 STM32CubeIDE 中创建工程 `RPMsg_TEST`，需配置三组关键外设：

**LED1 (PF3)：** DS0 被 A7 占用为心跳灯，M4 只能用 DS1(PF3)。配置为推挽输出、上拉模式，Pin Reserved 设为 Cortex-M4。

**USART3 (PD8/PD9)：** 分配给 M4 用于串口打印调试信息，工作模式为异步通信，默认参数。

**IPCC 和 HSEM：**
- IPCC（核间通信控制器）必须在 M4 侧开启，否则无法使能 OpenAMP。A7 侧默认已开启。
- HSEM（硬件信号量）默认开启，用于保证多核有序访问共享资源。

**OpenAMP 中间件：** 在 Middleware -> OPENAMP 处开启。默认配置参数：
- OpenAMP 版本：v2018.10（对应 STM32Cube 固件包 V1.2.0）
- 通信模式：远程通信模式（RPMSG_REMOTE）
- 共享内存起始地址：`0x10040000`（位于 SRAM3 中）
- 共享内存大小：`0x00008000`（32KB）
- Vring 缓冲区数量：16 个（RPMsg Buffer 默认 16 个）

### 1.2 导出 M4 工程

保存配置后生成工程，OpenAMP 库自动编译进工程。时钟可采用默认配置。选择生成独立 `.c/.h` 文件使代码结构清晰。

### 1.3 添加 LED1 代码

在 `main()` 的 `while(1)` 循环中添加 LED1 闪烁代码（PF3 翻转，500ms 延时），用于观察程序运行状态。初始化顺序：

```c
HAL_Init();
if(IS_ENGINEERING_BOOT_MODE()) { SystemClock_Config(); }
MX_IPCC_Init();
MX_OPENAMP_Init(RPMSG_REMOTE, NULL);
MX_GPIO_Init();
MX_USART3_UART_Init();
```

### 1.4 编译 M4 工程

编译生成 `RPMsg_TEST_CM4.elf`，即 M4 固件文件。

### 1.5 导出 MDK 工程

通过 STM32CubeMX 打开 `.ioc` 文件，选择 MDK-ARM V5.27 工具链导出。STM32CubeIDE 和 MDK 共享同一份源文件。

---

## 第二章 STM32MP157 资源分配

### 2.1 STM32MP157 资源介绍

STM32MP157DAA1 主要参数：
- 双核 Cortex-A7 (800MHz) + 单核 Cortex-M4 (209MHz)
- A7：32KB L1 I/D Cache + 256KB L2 Cache，支持 NEON、TrustZone
- M4：含 FPU 单元
- 内部 SRAM：708KB（RETRAM 64KB + SRAM1~4 共 384KB + 其他）
- 支持 LPDDR2/LPDDR3/DDR3/DDR3L，最大 1GB
- 3D GPU (OpenGL ES2.0)，RGB LCD 24bit，最高 1366x768@60fps
- 封装 LFBGA448，176 个 GPIO

两个 A7 内核中，一个用于安全模式（OP-TEE），一个用于非安全模式（Linux）。

### 2.2 内核外设分配

外设分配规则：
- **竖线"|"划分**：同一时刻只能单选（如 ADC 只能 A7 或 M4 独占）
- **斜线"/"划分**：可共享（如 GPIOA-K 可被 A7 和 M4 同时访问）

**M4 不可访问的外设：** DDR、RTC、STGEN、MDMA、GIC、IWDG、USB、DSI、GPU、FMC、ETH、LTDC

**M4 可访问的外设：** 大部分低速接口（UART、SPI、I2C、I2S）、GPIO、ADC、DAC、TIM、SAI、CAN FD、SDMMC3、PWR、RCC 等

**共享外设（关键）：**
- **IPCC**：A7 和 M4 共享，用于核间通信中断通知
- **HSEM**：A7(安全/非安全) 和 M4 共享，硬件信号量保护共享资源访问
- **GPIOA-K**：可共享
- **SRAM1~4、SYSRAM**：可共享

### 2.3 存储分配

**4GB 地址空间分为 13 块：**

| 存储块 | 功能 | 地址范围 |
|--------|------|----------|
| BOOT | BOOT ROM | 0x00000000~0x0FFFFFFF |
| SRAMs | SRAM 区域 | 0x10000000~0x1FFFFFFF |
| SYSRAM | SYSRAM | 0x20000000~0x2FFFFFFF |
| RAM aliases | SRAMs 别名区 | 0x30000000~0x3FFFFFFF |
| Peripherals 1 | 外设区域 1 | 0x40000000~0x4FFFFFFF |
| DDR | DDR 内存 | 0xC0000000~0xDFFFFFFF |

**SRAM 存储区域（核心）：**

| 存储块 | 地址范围 | 大小 |
|--------|----------|------|
| RETRAM | 0x00000000 | 64KB（M4 中断向量表，固定） |
| SRAM1 | 0x10000000~0x1001FFFF | 128KB |
| SRAM2 | 0x10020000~0x1003FFFF | 128KB |
| SRAM3 | 0x10040000~0x1004FFFF | 64KB |
| SRAM4 | 0x10050000~0x1005FFFF | 64KB |

**ST 参考设计中的分配方案：**
- RETRAM：M4 中断向量表
- SRAM1 (128KB)：M4 代码段
- SRAM2 (128KB)：M4 数据段
- SRAM3 (64KB)：**IPC 缓冲区（A7 和 M4 共享内存）**
- SRAM4 (64KB)：A7 的 DMA 缓冲区

**RAM aliases 原理：** 0x30000000~0x40000000 区域是 SRAMs 的"别名"，同一物理地址映射到两个虚拟地址区域——A7 通过 RAM aliases 访问，M4 通过 SRAMs 访问，本质是同一块物理内存。配置设备树时，RAM aliases 地址范围需与 SRAMs 对应。

---

## 第三章 异核通信框架

### 3.1 SMP 和 AMP 架构

**同构 vs 异构：**
- 同构：所有 CPU 架构相同（如双 Cortex-A9）
- 异构：CPU 架构不同（如 STM32MP157 的 A7+M4）

**SMP（对称多处理）：** 一个 OS 实例运行在多个同构 CPU 上，平等访问内存和外设。STM32MP157 的两个 A7 核运行同一个 Linux，构成 SMP 子系统。

**AMP（非对称多处理）：** 每个内核运行自己的 OS 或裸机，有独立和共享资源。STM32MP157 整体是 AMP 结构（A7 Linux + M4 RTOS）。AMP 需解决两个问题：
1. 生命周期管理（内核启动顺序）→ **RemoteProc**
2. 内核间通信 → **RPMsg**

### 3.2 IPCC 通信框架

**IPCC（Inter-Process Communication Controller）** 是硬件模块，提供信号交换机制，**不传输数据本身**（数据在共享内存中传输）。

**通信结构：**
- A7 通过 GIC 接收中断，M4 通过 NVIC 接收中断
- 共享内存存储通信数据（SRAM3，非 IPCC 的一部分）
- Mailbox 框架封装在 IPCC 之上，负责转发通知

**6 个双向通道的 ST 默认分配：**

| 通道 | 模式 | 用途 | 框架 |
|------|------|------|------|
| 通道1 | 全双工 | M4→A7 的 RPMsg 传输 | RPMsg/OpenAMP |
| 通道2 | 全双工 | A7→M4 的 RPMsg 传输 | RPMsg/OpenAMP |
| 通道3 | 单工 | M4 关闭请求 | RemoteProc |
| 通道4~6 | 未使用 | - | - |

**IPCC 寄存器（8 个，分两组各 4 个）：**
- `IPCC_C1CR`/`IPCC_C2CR`：控制寄存器，使能 TX 空闲/RX 占用中断（TXFIE、RXOIE）
- `IPCC_C1MR`/`IPCC_C2MR`：屏蔽寄存器，控制每通道中断屏蔽（CHnFM、CHnOM）
- `IPCC_C1SCR`/`IPCC_C2SCR`：状态设置/清除寄存器（CHnS 设置占用、CHnC 清除）
- `IPCC_C1TOC2SR`/`IPCC_C2TOC1SR`：通道状态标志（CHnF=1 占用/0 空闲）

**IPCC 工作模式：**
- **单工发送/接收：** 发送方设置 CHnF=1 表示占用，接收方清除 CHnF=0 表示读取完成
- **半双工：** 支持请求-应答模式，通过 response pending 变量协调
- **全双工：** 两个单工通道组合，通道 1 和通道 2 各负责一个方向

**非阻塞信令机制：** IPCC 提供消息可用性中断和通道流控制，允许处理器以非阻塞方式交换信息。

### 3.3 OpenAMP 框架

OpenAMP 是针对 AMP 系统的标准开发框架，被 Xilinx、TI、NXP、ST、NORDIC 等厂商广泛使用。包含三个核心模块：

**Virtio（虚拟化模块）：**
- 提供虚拟化设备抽象，使得 RPMsg 可以在不同操作系统间移植
- 定义了 Vring（虚拟环）数据结构，用于在共享内存中高效传递消息
- Vring 包含 descriptors（描述符表）、available ring（可用环）和 used ring（已用环）

**RPMsg（远程处理器消息传递）：**
- 基于 Virtio 构建的消息传递框架
- 支持点对点通信，通过端点（endpoint）和通道（channel）实现
- 消息结构：rpmsg_hdr 包含 src（源地址）、dst（目标地址）、len（数据长度）、data（负载）
- 默认单次最大传输 512 字节（可配置增大到 1024B 或更多）

**RemoteProc（远程处理器）：**
- 管理远程处理器（M4）的生命周期：加载固件、启动、停止、恢复
- 通过资源表（resource table）描述 M4 的资源需求
- Linux 侧通过 sysfs 接口控制：`/sys/class/remoteproc/remoteproc0/state`

### 3.4 驱动文件介绍

**Linux 驱动编译配置：**
- 通过 `make menuconfig` 或修改 `fragment.cfg` 文件开启 OpenAMP 相关驱动
- 关键配置项：`CONFIG_RPMSG_CHAR`、`CONFIG_RPMSG_TTY`、`CONFIG_STM32_RPROC`

**Linux 驱动文件：**
- `remoteproc_core.c`：RemoteProc 核心框架
- `rpmsg_core.c`：RPMsg 核心框架
- `rpmsg_char.c`：RPMsg 字符设备驱动
- `rpmsg_tty.c`：RPMsg 虚拟串口驱动
- `stm32_rproc.c`：STM32 平台 RemoteProc 驱动

**M4 工程驱动文件（OpenAMP 库）：**
- `open-amp/`：OpenAMP 核心库
- `libmetal/`：硬件抽象层
- `virtual_driver/virt_uart.c`：虚拟串口驱动
- `rsc_table.c`：资源表定义

---

## 第四章 RemoteProc 相关驱动简析

### 4.1 资源表

资源表（resource table）是 M4 固件中描述资源需求的数据结构，放在特定的链接段 `.resource_table` 中，由 Linux 侧 RemoteProc 驱动解析。

**资源表结构体 `resource_table`：**
```c
struct resource_table {
    uint32_t ver;        // 版本号，固定为 1
    uint32_t num;        // 资源条目数量
    uint32_t reserved[2]; // 保留
    uint32_t offset[num]; // 各资源条目的偏移量
};
```

**常见资源类型：**
- `RSC_CARVEOUT`：内存预留（carveout），请求 Linux 分配特定地址的内存
- `RSC_DEVMEM`：设备内存映射
- `RSC_TRACE`：跟踪缓冲区，用于 M4 的 printf 输出
- `RSC_VDEV`：虚拟设备（virtio 设备），描述 RPMsg 通信所需的 Vring 配置

**Vring 配置关键参数：**
- `num_buffers`：每个 Vring 的缓冲区数量（默认 16）
- `notifyid`：对应的 IPCC 通道号
- `da`（device address）：设备地址
- `pa`（physical address）：物理地址
- `align`：对齐要求

### 4.2 存储和系统资源分配

**存储分配（链接脚本控制）：**
- RETRAM：M4 向量表（固定 0x00000000）
- SRAM1：M4 代码段（ST 参考默认）
- SRAM2：M4 数据段
- SRAM3：IPC 缓冲区（共享内存），包含资源表和 Vring
- SRAM4：A7 DMA 缓冲区

**系统资源分配（设备树控制）：**
- `mcuram`：MCU SRAM 区域，分配给 M4
- `vdev0vring0`/`vdev0vring1`：Vring 缓冲区
- `vdev0buffer`：RPMsg 数据缓冲区
- `m4_system_resources`：M4 系统资源节点

### 4.3 Linux 下 RemoteProc 相关 API

**rproc 结构体 `struct rproc`：** Linux 内核中表示远程处理器实例的核心结构，包含名称、固件名、状态、设备等字段。

**关键 API 函数：**

| 函数 | 功能 |
|------|------|
| `rproc_alloc()` | 分配并初始化 rproc 实例 |
| `rproc_free()` | 释放 rproc 实例 |
| `rproc_add()` | 注册远程处理器到内核 |
| `rproc_del()` | 注销远程处理器 |
| `rproc_boot()` | 启动远程处理器（加载固件并运行） |
| `rproc_shutdown()` | 关闭远程处理器 |
| `rproc_get()` | 获取 rproc 引用 |
| `rproc_put()` | 释放 rproc 引用 |

**rproc 设备树节点：** 在设备树中定义 `m4` 节点，配置 compatible、mboxes（IPCC 通道）、memory-region（共享内存区域）等属性。

### 4.4 链接脚本

**链接脚本地址分配：** M4 工程的链接脚本（`.ld` 文件）定义了内存区域和段的分配。

**关键内存区域定义：**
```
RETRAM (xrw) : ORIGIN = 0x00000000, LENGTH = 64K
SRAM1  (xrw) : ORIGIN = 0x10000000, LENGTH = 128K
SRAM2  (xrw) : ORIGIN = 0x10020000, LENGTH = 128K
SRAM3  (xrw) : ORIGIN = 0x10040000, LENGTH = 64K
SRAM4  (xrw) : ORIGIN = 0x10050000, LENGTH = 64K
```

**重新划分存储区域：** 如果需要调整 SRAM 分配（如给 M4 更多代码空间），需要同时修改：
1. M4 工程的链接脚本
2. Linux 设备树中的内存区域定义
3. 确保共享内存地址在 A7 设备树和 M4 链接脚本中一致

### 4.5 RemoteProc 的使用

**加载和运行固件流程：**

```bash
# 1. 传输固件到开发板
scp RPMsg_TEST_CM4.elf root@<ip>:/lib/firmware/

# 2. 指定固件
echo RPMsg_TEST_CM4.elf > /sys/class/remoteproc/remoteproc0/firmware

# 3. 启动固件
echo start > /sys/class/remoteproc/remoteproc0/state

# 4. 查看状态
cat /sys/class/remoteproc/remoteproc0/state  # 应显示 running

# 5. 关闭固件
echo stop > /sys/class/remoteproc/remoteproc0/state
```

**debugfs 调试接口：**
- `/sys/kernel/debug/remoteproc/remoteproc0/name`：处理器名（m4）
- `/sys/kernel/debug/remoteproc/remoteproc0/resource_table`：资源表信息
- `/sys/kernel/debug/remoteproc/remoteproc0/carveout_memories`：内存分配
- `/sys/kernel/debug/remoteproc/remoteproc0/recovery`：恢复机制（enabled/disabled）

**开机自动运行：**
- 方法 1：在 `/etc/rc.local` 中添加加载脚本
- 方法 2：修改设备树 `m4_system_resources` 节点，设置 `auto-boot` 属性
- 方法 3：在 U-Boot 中加载 M4 固件（`rproc init`、`rproc load`、`rproc start`）

**U-Boot 启动 M4 固件：**
```bash
rproc init
rproc load 0 <firmware_addr> <size>
rproc start 0
```

---

## 第五章 基于 RPMSG 实现异核通信

### 5.1 Linux 下 RPMSG 相关驱动文件

RPMsg 是基于 Virtio 的消息传递框架，在 Linux 内核中已有完整实现。

**核心结构体：**
- `struct rpmsg_device`：RPMsg 设备，代表一个通信通道
- `struct rpmsg_endpoint`：RPMsg 端点，用于收发消息
- `struct rpmsg_hdr`：消息头，包含 src、dst、len、reserved 字段
- `struct rpmsg_channel_info`：通道信息（名称、源地址、目标地址）

**缓冲区管理：**
- Vring0：用于 A7→M4 方向
- Vring1：用于 M4→A7 方向
- 每个 Vring 有 16 个描述符（默认），每个描述符对应一个 RPMsg Buffer

**Linux 侧关键 API：**

| 函数 | 功能 |
|------|------|
| `rpmsg_create_ept()` | 创建 RPMsg 端点 |
| `rpmsg_destroy_ept()` | 销毁 RPMsg 端点 |
| `rpmsg_send()` | 发送消息（阻塞） |
| `rpmsg_trysend()` | 发送消息（非阻塞） |
| `rpmsg_sendto()` | 发送到指定地址 |
| `rpmsg_send_offchannel()` | 使用指定源地址发送 |

**用户空间接口：**
- `/dev/rpmsg0` 等字符设备（通过 `rpmsg_char` 驱动）
- `/dev/ttyRPMSG0` 虚拟串口设备（通过 `rpmsg_tty` 驱动）

### 5.2 OpenAMP 库中的 API（M4 侧）

**初始化 IPCC API：**
```c
void MX_IPCC_Init(void);
```

**初始化 OpenAMP API：**
```c
void MX_OPENAMP_Init(int RPMode, rpmsg_ns_bind_cb ns_bind_cb);
```
- `RPMode`：`RPMSG_REMOTE`（M4 作为远程处理器）
- `ns_bind_cb`：名称服务绑定回调，当 A7 创建通道时触发

**回调函数机制：**
- `rpmsg_ns_bind_cb`：名称服务绑定回调，A7 侧创建通道时通知 M4
- 端点回调函数：接收到消息时调用，原型为 `int (*cb)(struct rpmsg_endpoint *ept, void *data, size_t len, uint32_t src, void *priv)`

**创建 RPMsg 端点 API：**
```c
int OPENAMP_create_endpoint(struct rpmsg_endpoint *ept, const char *name,
                            uint32_t dest, rpmsg_ept_cb cb,
                            rpmsg_ns_unbind_cb unbind_cb);
```

**轮询 API：**
```c
void OPENAMP_check_for_message(void);
```
通过邮箱轮询检查 Vring Buffer 中是否有数据（A7 发来的消息）。

**发送消息 API：**
```c
int rpmsg_send(struct rpmsg_endpoint *ept, const void *data, int len);
int rpmsg_trysend(struct rpmsg_endpoint *ept, const void *data, int len);
int rpmsg_sendto(struct rpmsg_endpoint *ept, const void *data, int len, uint32_t dst);
```

### 5.3 单次接收的数据量

**默认限制：** 单次接收最大 512 字节，受 RPMsg Buffer 大小限制。

**增大接收数据量的方法：**
1. 修改 `rsc_table.c` 中 Vring 的 `RPMSG_BUFFER_SIZE` 宏定义
2. 修改 `openamp_conf.h` 中的配置
3. 重新编译 M4 工程和 OpenAMP 库
4. **注意：** 增大缓冲区会占用更多共享内存，需确保 SRAM3 空间足够

**单次接收 1024B 配置示例：**
- 修改 `RPMSG_BUFFER_SIZE` 为 1024
- 调整 Vring 描述符数量或共享内存大小

### 5.4 基于 RPMSG 的异核通信实验

**硬件设计：** 使用 USART3（PD8/PD9）连接 PC 串口调试，DS1（PF3）LED 指示。

**软件设计（M4 侧）：**
1. 在 `main()` 中初始化 OpenAMP
2. 注册名称服务回调 `rpmsg_ns_bind_cb`
3. 在回调中创建端点并注册接收回调
4. 在 `while(1)` 中调用 `OPENAMP_check_for_message()` 轮询消息
5. 收到消息后通过 `rpmsg_send()` 回复

**软件设计（A7 Linux 侧）：**
1. 加载 M4 固件（RemoteProc）
2. 通过 `/dev/rpmsg0` 字符设备或自定义驱动进行通信
3. 使用 `write()`/`read()` 系统调用收发数据

**实验验证：** A7 通过 RPMsg 发送消息给 M4，M4 收到后打印并回复，A7 收到回复后打印，形成双向通信闭环。

---

## 第六章 基于虚拟串口实现异核通信

### 6.1 虚拟串口概述

虚拟串口（Virtual UART）是基于 RPMsg 的上层应用，将 RPMsg 通道封装为串口设备。M4 侧使用 `VIRT_UART` API，A7 侧出现 `/dev/ttyRPMSG0` 设备节点，用户空间应用可以像操作普通串口一样使用它。

**优势：** 用户无需直接操作 RPMsg 底层 API，降低了开发复杂度。

### 6.2 Linux 下虚拟串口驱动分析

Linux 内核中的 `rpmsg_tty` 驱动将 RPMsg 通道注册为 TTY 设备：
- 设备节点：`/dev/ttyRPMSG0`
- 使用标准串口操作：`open()`、`read()`、`write()`、`close()`
- 波特率等参数由 RPMsg 通道特性决定，非实际物理波特率

### 6.3 OpenAMP 库中的 API（M4 侧虚拟串口）

**虚拟串口初始化 API：**
```c
VIRT_UART_StatusTypeDef VIRT_UART_Init(VIRT_UART_HandleTypeDef *huart);
```
内部调用 `OPENAMP_create_endpoint()`，通道名称为 `"rpmsg-tty-channel"`。

**虚拟串口回调 API：**
```c
static void VIRT_UART_read_cb(struct rpmsg_endpoint *ept, void *data,
                               size_t len, uint32_t src, void *priv);
```

**注册回调函数：**
```c
VIRT_UART_RegisterCallback(huart, VIRT_UART_RXCPLT_CB_ID, pCallback);
```

**虚拟串口发送 API：**
```c
VIRT_UART_StatusTypeDef VIRT_UART_Transmit(VIRT_UART_HandleTypeDef *huart,
                                            uint8_t *pData, uint16_t Size);
```
返回 0 表示成功，1 表示失败。

### 6.4 M4 工程下虚拟串口驱动分析

`virt_uart.c` 文件中的 `VIRT_UART_Init()` 函数创建 RPMsg 端点，通道名 `"rpmsg-tty-channel"`，注册接收回调 `VIRT_UART_read_cb`。当 A7 侧打开 `/dev/ttyRPMSG0` 并写入数据时，M4 侧的回调函数被触发。

### 6.5 基于异核通信实现灯光控制实验

**实验目标：** A7 通过虚拟串口发送指令控制 M4 侧的 LED 开关。

**M4 侧软件设计：**
1. 初始化 VIRT_UART
2. 注册接收回调
3. 在回调中解析 A7 发来的指令（如 `"LED_ON"` / `"LED_OFF"`）
4. 根据指令控制 PF3 引脚（LED1）

**A7 侧操作：**
```bash
echo "LED_ON" > /dev/ttyRPMSG0   # 开灯
echo "LED_OFF" > /dev/ttyRPMSG0  # 关灯
```

### 6.6 M4 单次接收 1024B 的数据

修改 OpenAMP 缓冲区大小为 1024B，需修改 `RPMSG_BUFFER_SIZE` 并重新编译。

### 6.7 基于异核通信实现阈值报警实验

**实验目标：** M4 采集传感器数据（如温度），当超过阈值时通过虚拟串口通知 A7，A7 收到报警信息后进行处理（如记录日志、触发报警）。

**M4 侧设计：**
1. 定时采集传感器数据
2. 判断是否超过阈值
3. 超过阈值时通过 `VIRT_UART_Transmit()` 发送报警消息

**A7 侧设计：**
1. 读取 `/dev/ttyRPMSG0` 接收报警消息
2. 解析并处理报警（如显示、记录、发送通知）

---

## 第七章 系统的休眠和唤醒

> **注意**：原文 PDF 第七章标注为"待更新"，以下内容基于 STM32MP157 参考手册（RM0436）PWR 章节和异核通信框架整理。

### 7.1 STM32MP157 低功耗模式概述

STM32MP157 的 PWR 模块提供多种低功耗模式，适用于 Cortex-A7 和 Cortex-M4 双核异构系统的电源管理：

| 模式 | CPU 状态 | RAM 状态 | 唤醒源 | 典型功耗 |
|------|----------|----------|--------|----------|
| **CRun**（正常运行） | A7+M4 运行 | 保持 | - | 最高 |
| **CSleep**（Cortex 睡眠） | A7 WFI，M4 可运行 | 保持 | 任意中断 | 中等 |
| **CStop**（Cortex 停止） | A7+CStop，M4 可 CRun | 保持（可配置保持域） | WKUP 引脚/LPUART/RTC/IPCC | 低 |
| **CStandby**（Cortex 待机） | A7 待机，M4 可运行 | 部分保持（仅 RETRAM） | WKUP 張脚/RTC/IPCC | 极低 |
| **DStop**（域停止） | 所有 CPU 停止 | 保持（RETENTION 域） | WKUP 引脚/LPUART/RTC | 很低 |
| **DStandby**（域待机） | 所有 CPU 待机 | 仅 RETRAM 保持 | WKUP 引脚/RTC | 最低 |

### 7.2 PWR 模块关键寄存器

**PWR_CR1（电源控制寄存器 1）**：
- `LPDS`（bit 0）：低功耗深睡眠模式选择
- `FPDS`（bit 9）：Flash 掉电停止模式
- `DBP`（bit 8）：禁用备份域写保护
- `LPCFG`（bit 13）：低功耗配置

**PWR_MPUCR（MPU 控制寄存器）**：
- `PDDS`（bit 0）：Power Down Deep Sleep 选择
- `CWUF`（bit 8）：清除唤醒标志
- `SBF`（bit 9）：待机标志
- `SBF_MPU`（bit 10）：MPU 待机标志

**PWR_CR3（电源控制寄存器 3）**：
- `EWUP`（bits 0-5）：使能 WKUP 引脚
- `EWUP_A7`（bits 8-13）：使能 A7 域 WKUP 引脚
- `EWUP_M4`（bits 16-21）：使能 M4 域 WKUP 引脚

### 7.3 M4 唤醒 A7 的具体流程

在异核通信场景中，M4 可以在 A7 处于低功耗状态时唤醒整个系统：

**唤醒机制**：
1. **IPCC 中断唤醒**：M4 通过 IPCC（Inter-Processor Communication Controller）向 A7 发送中断通知，A7 的 IPCC 中断可以将 A7 从 CStop/CStandby 模式唤醒
2. **WKUP 引脚唤醒**：M4 可以配置外部唤醒引脚，当 A7 进入低功耗模式后，通过外部事件唤醒
3. **RTC 闹钟唤醒**：M4 可以设置 RTC 闹钟，在指定时间唤醒 A7

**典型唤醒流程**：
```c
// A7 侧：进入 CStop 模式前的准备
// 1. 配置唤醒源（如 IPCC 中断、WKUP 引脚）
// 2. 设置 PWR_CR3 的 EWUP 位使能唤醒引脚
// 3. 执行 WFI 指令进入 CStop

// M4 侧：唤醒 A7
// 1. 通过 IPCC 发送核间中断
// 2. A7 的 IPCC 中断处理程序被触发
// 3. A7 从 CStop 模式恢复，重新初始化时钟和外设
```

**HAL 库 API**：
- `HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI)` — 进入 Sleep 模式
- `HAL_PWR_EnterSTOPMode(PWR_MAINREGULATOR_ON, PWR_STOPENTRY_WFI)` — 进入 Stop 模式
- `HAL_PWR_EnterSTANDBYMode()` — 进入 Standby 模式
- `HAL_PWR_DisableWakeUpPin(PWR_WAKEUP_PIN1)` — 禁用唤醒引脚
- `HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1)` — 使能唤醒引脚

### 7.4 异核通信中的电源管理考虑

**M4 独立运行场景**：
- 当 A7 进入 CStandby 模式时，M4 可以继续运行（在 M4 域中）
- M4 可以独立处理传感器数据、外设控制等任务
- 当需要 A7 处理时，M4 通过 IPCC 中断唤醒 A7

**共享资源保护**：
- 在进入低功耗模式前，必须确保共享内存中的数据已正确保存
- 使用 HSEM（硬件信号量）协调双核对共享资源的访问
- 在唤醒后，需要重新初始化 OpenAMP/RPMsg 通道

**唤醒后恢复**：
- A7 从低功耗模式唤醒后，需要重新初始化时钟树
- OpenAMP 通道可能需要重新建立连接
- 共享内存区域的内容在 CStop 模式下保持，在 DStandby 模式下可能丢失（取决于 RETRAM 配置）

---

## 关键概念速查

| 概念 | 说明 |
|------|------|
| OpenAMP | 非对称多处理系统开发框架，包含 Virtio、RPMsg、RemoteProc |
| RPMsg | 远程处理器消息传递，基于 Virtio 的点对点通信框架 |
| RemoteProc | 远程处理器生命周期管理（加载/启动/停止固件） |
| Virtio | 虚拟化设备抽象层，定义 Vring 数据结构 |
| IPCC | 核间通信控制器，提供中断通知机制（不传输数据） |
| HSEM | 硬件信号量，保护共享资源访问 |
| Vring | 虚拟环，共享内存中的消息队列结构 |
| 资源表 | M4 固件中描述资源需求的数据结构 |
| 共享内存 | SRAM3 (0x10040000~0x10047FFF)，A7 和 M4 通过 RAM aliases/SRAMs 访问同一物理地址 |
| Mailbox | 邮箱框架，封装 IPCC，负责转发中断通知 |
