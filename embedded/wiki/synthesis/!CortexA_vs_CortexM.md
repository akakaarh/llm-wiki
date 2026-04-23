---
type: synthesis
related_sources:
  - $CortexA_ProgrammersGuide.md
  - $ARMv7M_RefManual.md
tags: [arm, cortex-a, cortex-m, comparison, embedded, application]
---

# !Cortex-A 与 Cortex-M 对比

## 选型总览

| 维度 | Cortex-A | Cortex-M |
|------|-----------|----------|
| 架构 | ARMv7-A / ARMv8-A | ARMv6-M / ARMv7-M / ARMv8-M |
| 定位 | 应用处理器 | 微控制器 |
| 典型主频 | 0.5GHz ~ 3GHz | 50MHz ~ 400MHz |
| 典型功耗 | 0.5W ~ 10W+ | 10μW ~ 500mW |
| 支持 OS | Linux/Android/iOS | RTOS / Bare-metal |
| 虚拟内存 | MMU | 无（MPU 可选） |
| 指令集 | ARM + Thumb + Thumb-2 | 仅 Thumb/Thumb-2 |
| 适用场景 | 手机/平板/PC/服务器 | 单片机/嵌入式/IoT/工业控制 |

## 详细对比

### 中断系统

- **Cortex-A** — 独立 GIC（Generic Interrupt Controller），支持 SPI/PPI/SGI，配置复杂，支持多核中断路由，安全状态（TrustZone）集成
- **Cortex-M** — NVIC 集成在内核，硬件嵌套，无需软件模拟，配置简单，向量化中断

### 内存管理

- **Cortex-A** — MMU 支持完整虚拟内存，页表 4KB ~ 2MB/16MB，地址空间 4GB（32-bit）或 48-bit（64-bit）
- **Cortex-M** — 无 MMU，固定 4GB 线性地址空间，MPU 可选（区域保护，无虚拟内存）

### 功耗与成本

- **Cortex-A** — 动态功耗 ~ C×V²×f，多核 big.LITTLE 调度，移动设备专用
- **Cortex-M** — 静态功耗极低（WFI/WFE 深度睡眠，微瓦级），内核直接集成 NVIC减少外部 IP

### 开发体验

| 方面 | Cortex-A | Cortex-M |
|------|----------|----------|
| 调试器 | J-Link（高级）/ OpenOCD | J-Link / ST-Link / OpenOCD |
| SDK | 芯片厂家 Linux BSP / Android HAL | CMSIS + 厂家 HAL / 裸机 |
| 启动流程 | Bootloader(U-Boot/LK) → Kernel → Rootfs | 简单：Reset_Handler → Main |
| 典型 RTOS | Linux / Android | FreeRTOS / RT-Thread / Zephyr |

## 生态代表性产品

| Cortex-A | Cortex-M |
|-----------|----------|
| Qualcomm Snapdragon | STM32F4 |
| Apple A-series | NRF52 |
| Samsung Exynos | LPC43 |
| NXP i.MX6/8 | TI Tiva C |
| Raspberry Pi (BCM2835+) | GD32F4 |

## 何时选谁

**选 Cortex-M**：工业传感器/执行器、电机控制、IoT 端点、简单通信协议（UART/I2C/SPI）、电池供电、成本敏感、确定性实时性要求高

**选 Cortex-A**：需要完整操作系统（Linux）、复杂通信协议栈（TCP/IP + TLS）、图形界面、多媒体处理、多任务隔离、需要丰富生态

> 来源：$CortexA_ProgrammersGuide.md + $ARMv7M_RefManual.md
