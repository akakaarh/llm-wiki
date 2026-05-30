---
type: question
tags: [debug, spi, pinctrl, nor-flash, device-tree]
created: 2026-05-30
---
# SPI NOR Flash 读 JEDEC ID 全 0xFF

**现象：** probe 阶段读 JEDEC ID 返回全 0xFF，但逻辑分析仪抓到的 SPI 波形（CLK、MOSI、MISO）完全正常。

**原因：** CS（片选）引脚未在设备树中配置 pinctrl。SoC 端的 SPI 控制器虽然在发时序，但 CS 引脚处于默认状态（未被复用为 SPI 功能），导致 Flash 实际上从未被选中，MISO 上的 0xFF 是总线空闲时的上拉电平。

**修复：** 设备树中 SPI 控制器节点添加 pinctrl 配置：
```dts
pinctrl-0 = <&spi1_pins_a>;
```
