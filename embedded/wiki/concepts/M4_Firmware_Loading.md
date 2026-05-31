---
type: concept
tags: [m4, remoteproc, firmware, stm32mp157, elf]
created: 2026-05-31
---

# M4 固件加载流程（STM32MP157）

## 概述

STM32MP157 的 M4 内核没有 Flash，程序必须从 A7 端的 Linux 加载到 SRAM 运行。

## 加载方式

### 方式 1：remoteproc 框架（推荐）

```bash
# 1. 传输固件到开发板
scp first-m4.elf root@<ip>:/lib/firmware/rproc-m4-fw

# 2. 启动 M4
echo start > /sys/class/remoteproc/remoteproc0/state

# 3. 停止 M4
echo stop > /sys/class/remoteproc/remoteproc0/state

# 4. 查看状态
cat /sys/class/remoteproc/remoteproc0/state
```

**固件格式：** ELF 文件（.elf），remoteproc 会解析程序头，把各段放到正确地址。

**固件命名：** 必须命名为 `rproc-m4-fw`（与设备树中 firmware-name 匹配）。

### 方式 2：M4.sh 脚本（正点原子提供）

```bash
cd /home/root/shell/rpmsg/
./M4.sh start <firmware.elf>
./M4.sh stop
```

## 内存布局

| 区域 | 地址 | 用途 |
|------|------|------|
| 中断向量表 | 0x00000000 | 硬件要求，必须在此地址 |
| 代码段 (.text) | 0x10000000 | M4 SRAM，128KB |
| 数据段 (.data) | 0x10020000 | M4 SRAM，128KB |
| 共享内存 | 0x10040000 | A7↔M4 通信，32KB |

## 常见问题

### 固件加载失败
- 检查文件名是否为 `rproc-m4-fw`
- 检查 ELF 文件是否为 ARM Cortex-M4 格式
- 检查链接脚本的内存地址是否正确

### M4 程序不运行
- 用 OpenOCD 检查 PC 寄存器：`reg pc`
- 检查启动文件是否正确（startup.s）
- 检查 GPIO 基地址是否正确（查 SDK 头文件）

### GPIO 不响应
- 检查是否被 Linux LED 子系统控制
- 用 `devmem2` 从 Linux 读寄存器验证
- 使用未被 Linux 注册的 GPIO（如蜂鸣器 PC7）
