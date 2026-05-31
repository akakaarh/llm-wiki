---
type: note
title: gpiod_to_irq 完整调用链分析
tags: [gpio, irq, irqdomain, gpiolib, interrupt]
---

## 概述

`gpiod_to_irq()` 是 Linux GPIO 子系统中将 GPIO 描述符映射到 Linux IRQ 号的核心函数。完整路径涉及初始化阶段的 irqdomain 注册和运行时的 IRQ 号查询两部分。

## 初始化路径（驱动 probe 阶段）

GPIO 驱动通过 `gpiochip_add()` → `gpiochip_add_irqchip()` 建立 GPIO 与 IRQ 的映射基础设施。

### 关键函数

| 函数 | 位置 | 职责 |
|------|------|------|
| gpiochip_add_irqchip | gpiolib.c:2183 | 入口，为 gpio_chip 注册 irqchip 基础设施 |
| gpiochip_simple_create_domain | gpiolib.c:2003 | 创建简单的 irq_domain（大多数驱动使用） |
| gpiochip_hierarchy_create_domain | gpiolib.c:2219 | 创建层级 irq_domain（级联 GPIO 控制器使用） |
| gpiochip_set_irq_hooks | gpiolib.c:2103 | 设置 irq_chip 的 startup/shutdown/type 回调 |
| gpiochip_irq_map | gpiolib.c:1932 | irq_domain 的 map 回调，建立 hwirq→virq 映射 |
| gpiochip_irqchip_irq_valid | gpiolib.c:2028 | 检查 GPIO 线的 IRQ 是否有效 |
| acpi_gpiochip_request_interrupts | gpiolib.c:2252 | 注册 ACPI GPIO 中断（如适用） |

### 初始化调用链

```
gpiochip_add()
  └─ gpiochip_add_irqchip()                    [gpiolib.c:2183]
       ├─ gpiochip_hierarchy_is_hierarchical()
       │    └─ gpiochip_hierarchy_create_domain()   [gpiolib.c:2219]
       │         ├─ gpiochip_hierarchy_setup_domain_ops()
       │         └─ gpiochip_set_hierarchical_irqchip()
       ├─ gpiochip_simple_create_domain()           [gpiolib.c:2003]
       │    └─ irq_domain_create_simple()            [kernel/irq/]
       │         └─ 建立 irq_domain，ops.map = gpiochip_irq_map
       ├─ gpiochip_set_irq_hooks()                  [gpiolib.c:2103]
       │    └─ 设置 gc->irqchip 的 startup/shutdown/set_type
       ├─ gpiochip_irqchip_add_allocated_domain()   [gpiolib.c:2248]
       └─ acpi_gpiochip_request_interrupts()        [gpiolib.c:2252]
            └─ acpi_gpiochip_request_irqs()          [gpiolib-acpi-core.c:486]
```

## 运行时路径（gpiod_to_irq 调用）

### 关键函数

| 函数 | 位置 | 职责 |
|------|------|------|
| gpiod_to_irq | gpiolib.c:4127 | 主入口，GPIO 描述符→IRQ 号 |
| validate_desc | gpiolib.c:4134 | 验证 gpio_desc 有效性 |
| gpiod_hwgpio | gpiolib.c:4145 | 从 desc 获取硬件 GPIO 编号 |
| gc->to_irq | (各驱动自定义) | 可选的自定义 to_irq 回调 |
| gpiochip_to_irq | gpiolib.c:2016 | 默认 GPIO→IRQ 映射实现 |
| gpiochip_line_is_valid | gpiolib.c:1594 | 检查 GPIO 线是否有效 |
| irq_find_mapping | kernel/irq/ | 在 irq_domain 中查找 hwirq→virq 映射 |
| irq_create_mapping | kernel/irq/ | 创建 hwirq→virq 映射（如不存在） |

### 运行时调用链

```
用户驱动: gpiod_to_irq(desc)                      [gpiolib.c:4127]
  ├─ validate_desc(desc)                           [gpiolib.c:4134]
  │    └─ 验证 desc 非空且已请求
  ├─ gpiod_hwgpio(desc)                            [gpiolib.c:4145]
  │    └─ 返回硬件 GPIO 编号（desc_to_gpio 的变体）
  ├─ gc = desc->gdev->chip                         // 获取 gpio_chip
  ├─ [可选] gc->to_irq(gc, hwgpio)                // 驱动自定义映射
  │    └─ 某些 SoC 驱动实现自定义映射逻辑
  └─ [默认] gpiochip_to_irq(gc, hwgpio)           [gpiolib.c:2016]
       ├─ gpiochip_irqchip_irq_valid(gc, hwgpio)   [gpiolib.c:2028]
       │    └─ gpiochip_line_is_valid(gc, hwgpio)   [gpiolib.c:1594]
       ├─ irq_find_mapping(gc->irqdomain, hwgpio)  [kernel/irq/]
       │    └─ 在 irqdomain 中查找已有映射
       └─ [若未找到] irq_create_mapping(gc->irqdomain, hwgpio)
            └─ 创建新的 hwirq→virq 映射并返回 virq
```

## 主要调用者

| 调用者 | 文件 | 场景 |
|--------|------|------|
| lineevent_create | gpiolib-cdev.c:2076 | 字符设备 ioctl GPIO 事件 |
| edge_detector_setup | gpiolib-cdev.c:1035 | GPIO 线边缘检测 |
| debounce_setup | gpiolib-cdev.c:919 | GPIO 消抖设置 |
| gpio_sysfs_request_irq | gpiolib-sysfs.c:223 | sysfs 接口请求中断 |
| acpi_gpiochip_alloc_event | gpiolib-acpi-core.c:398 | ACPI GPIO 事件分配 |
| gpio_fwd_to_irq | gpio-aggregator.c:438 | GPIO 聚合器转发 IRQ |
| lineevent_create | gpiolib-cdev.c:2076 | 用户空间 GPIO 事件监听 |

## 核心数据结构关系

```
gpio_desc
  └─ gdev (gpio_device)
       └─ chip (gpio_chip)
            ├─ to_irq        → [可选] 驱动自定义回调
            ├─ irqdomain     → irq_domain
            │    ├─ ops.map   = gpiochip_irq_map
            │    └─ host_data = gpio_chip
            └─ irqchip       → irq_chip
                 ├─ irq_startup
                 ├─ irq_shutdown
                 ├─ irq_set_type
                 ├─ irq_mask
                 └─ irq_unmask
```

## 要点

- `gpiod_to_irq()` 本身不注册中断，只做 GPIO→IRQ 号的映射查询
- 真正的中断注册由 `devm_request_irq()` / `request_irq()` 完成，使用 `gpiod_to_irq()` 返回的 IRQ 号
- 大多数现代 GPIO 驱动使用 irqdomain 框架，通过 `gpiochip_add_irqchip()` 统一注册
- `gc->to_irq` 回调是老式接口，现代驱动应优先使用 irqdomain
- irqdomain 的 `map` 回调 (`gpiochip_irq_map`) 在首次映射时被调用，完成 hwirq→virq 的绑定
