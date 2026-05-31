---
type: question
tags: [m4, gpio, linux, conflict, stm32mp157, debug]
created: 2026-05-31
---

# M4 GPIO 与 Linux LED 驱动冲突

**现象：** M4 程序配置 GPIO 输出，但 LED 不亮或闪烁两下后被 Linux 抢回控制权。

**原因：** Linux 的 LED 子系统（`/sys/class/leds/`）会持续控制已注册的 GPIO 引脚。即使 `echo none > trigger`，某些情况下 Linux 仍会重新接管。

**修复：**
1. 使用未被 Linux LED 子系统注册的 GPIO（如 PC7 蜂鸣器）
2. 或在设备树中移除对应的 LED 节点

**关键教训：**
- PI0 (DS0) = 心跳灯，Linux 自动控制
- PF3 (DS1) = 用户 LED，Linux LED 子系统控制
- PC7 (BEEP) = 蜂鸣器，触发器默认 none，M4 可独占
