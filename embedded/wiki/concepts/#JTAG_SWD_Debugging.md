---
tags: [debug, swd, jtag, dap, openocd, gdb, cortex-m]
type: concept
---

# JTAG/SWD 调试基础

## 调试接口协议

Cortex-M4 支持两种调试接口：

| 协议 | 引脚 | 特点 |
|------|------|------|
| JTAG | TCK, TDI, TMS, TDO (4pin) + nTRST (可选) | IEEE 1149.1 标准，支持菊花链 |
| SWD | SWCLK, SWDIO (2pin) | ARM 专有，引脚更少，支持奇偶校验 |

两种协议共享引脚：TCK = SWCLK, TMS = SWDIO。可通过特殊位模式动态切换。

**SWD 是 Cortex-M 调试的首选**——只需 2 根信号线（+ GND），够用且省引脚。

## CoreSight 调试架构

调试连接层次：

```
调试主机(PC) → USB → 调试适配器(DAP/ST-LINK) → SWD/JTAG → SWJ-DP (Debug Port)
  → 内部调试总线 → AHB-AP (Access Port) → 处理器内部总线
```

| 组件 | 全称 | 作用 |
|------|------|------|
| SWJ-DP | Serial Wire JTAG Debug Port | 支持 SWD 和 JTAG 的调试端口 |
| AHB-AP | AHB Access Port | 将调试命令转换为内存访问 |
| FPB | Flash Patch and Breakpoint | 断点和 Flash 补丁（最多 8 个硬件断点） |
| DWT | Data Watchpoint and Trace | 数据观察点和追踪 |
| ITM | Instrumentation Trace Macrocell | 软件追踪（printf 等） |
| ROM Table | — | 调试组件地址查找表 |

## 断点类型

| 类型 | 数量 | 原理 |
|------|------|------|
| 硬件断点（FPB） | 最多 8 个（6 个指令地址 + 2 个字面量地址） | Flash Patch and Breakpoint 单元 |
| 软件断点（BKPT） | 无限 | BKPT 指令（编码 0xBExx） |

Flash 中只能用硬件断点（不能改 Flash 内容插入 BKPT 指令）。RAM 中两者都可以用。

## 调试模式

- **Halt 模式**：处理器暂停执行，调试器可读写寄存器/内存。由 C_DEBUGEN 位使能。
- **Debug Monitor 异常**：处理器在 DebugMonitor 异常中运行调试代码，可设置优先级。

唤醒条件：中断请求（需满足优先级条件）、调试请求、复位。

## 关键调试寄存器

| 地址 | 名称 | 作用 |
|------|------|------|
| 0xE000EDF0 | DHCSR | 调试暂停控制和状态 |
| 0xE000EDFC | DEMCR | 调试异常和监控控制 |

## 调试器类型

| 调试器 | 价格 | 特点 |
|-------|------|------|
| ST-LINK V2 | ~15-30 元 | STM32 官方推荐 |
| CMSIS-DAP | ~15-20 元 | 开源，通用性好 |
| J-Link | ~50-200 元 | 速度快，功能最强 |

## OpenOCD + GDB 调试环境

### OpenOCD 配置文件（CMSIS-DAP HID 后端）

```cfg
# dap.cfg
adapter driver cmsis-dap
cmsis_dap_backend hid
transport select swd
adapter speed 4000
source [find target/stm32mp15x.cfg]
```

**注意**：Windows 10/11 下 CMSIS-DAP 通常使用 HID 后端（不需要安装驱动）。如果之前用 Zadig 安装了 libusb-win32 驱动，需要卸载恢复 Windows 默认 HID 驱动，否则 OpenOCD 会报 "unable to find a matching CMSIS-DAP device"。

### 启动 OpenOCD

```bash
openocd -f dap.cfg
# 成功输出：
# Info : CMSIS-DAP: SWD supported
# Info : CMSIS-DAP: Interface ready
# Info : Listening on port 3333 for gdb connections
```

### GDB 连接

```bash
arm-none-eabi-gdb your_program.elf
(gdb) target remote localhost:3333
(gdb) monitor reset halt
(gdb) load
(gdb) break main
(gdb) continue
```

### 常见 OpenOCD 错误

| 错误 | 原因 | 解决 |
|------|------|------|
| "unable to find a matching CMSIS-DAP device" | 驱动问题 | 卸载 Zadig 安装的驱动，恢复 Windows 默认 HID 驱动 |
| "Error connecting DP: cannot read IDR" | 物理连接问题 | 检查接线、供电、接触 |
| "Error: init mode failed" | 目标芯片无响应 | 确认板子已上电，SWD 接线正确 |

## STM32MP157 开发板 JTAG 接口

### 引脚定义（10pin，2.0mm 间距）

```
┌──────────────────────────┐
│ Pin 1: VCC3.3   Pin 2: VDD │
│ Pin 3: NJTRST   Pin 4: GND │
│ Pin 5: JTDO     Pin 6: JTDI │
│ Pin 7: JTMS     Pin 8: GND │
│ Pin 9: JTCK     Pin 10: GND│
└──────────────────────────┘
```

SWD 只需连接：JTMS(SWDIO)、JTCK(SWCLK)、GND（可选 VCC3.3 作参考电压）。

### 转接问题

开发板 JTAG 插座是 **2.0mm 间距**，调试器通常附带 **2.54mm 间距**排线。需要 2.0mm 转 2.54mm 转接板才能连接。

### M4 固件加载方式

M4 没有 Flash，必须在线调试或通过 Linux remoteproc 加载：

```bash
# 通过 A7 Linux 加载 M4 固件
cp firmware.elf /lib/firmware/
echo firmware.elf > /sys/class/remoteproc/remoteproc0/firmware
echo start > /sys/class/remoteproc/remoteproc0/state
```

USB_TTL 串口（uart4/ttySTM0，115200）可观察 M4 输出，不需要调试器。

## 参考来源

- `$CortexM3M4_DefinitiveGuide.md` Ch14（调试与追踪特性）
- `$MP157_M4_CubeIDE.md` Ch4.3（CubeIDE 调试配置）
- `$ATK_DLMP157_GettingStarted.md`（开发板 JTAG 接口、ST-LINK 要求）
- 实际经验：CMSIS-DAP HID 后端配置、Windows 驱动排查
