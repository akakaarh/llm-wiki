---
title: Yocto/OpenEmbedded 构建系统（ST STM32MP1 专题）
source:
  - https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html
  - https://wiki.st.com/stm32mpu/wiki/STM32MPU_Distribution_Package
  - https://wiki.st.com/stm32mpu/wiki/How_to_create_a_new_open_embedded_layer
type: source
tags: [yocto, bitbake, build-system, stm32mp1, openembedded, openstlinux, bsp]
created: 2026-05-24
---

# Yocto/OpenEmbedded 构建系统（ST STM32MP1 专题）

本文档综合 Yocto Project 官方快速入门指南（v6.0）和 ST 官方 Wiki 的 STM32MPU Distribution Package 文档，系统性地介绍 Yocto 构建体系以及 ST 为 STM32MP1 系列提供的 OpenSTLinux 发行版构建流程。

---

## 第一部分 Yocto Project 概述

### 1 什么是 Yocto Project

Yocto Project 是一个开源协作项目，提供模板、工具和方法，帮助开发者为嵌入式产品创建定制的 Linux 发行版，而无需受硬件架构限制。其核心参考发行版名为 **Poky**。

**核心组件**：
- **BitBake**：构建引擎，执行 shell 和 Python 任务，根据 recipe（`.bb`）、配置（`.conf`）和 class（`.bbclass`）文件中的元数据来构建镜像
- **OpenEmbedded (OE)**：提供核心元数据层（`openembedded-core`），是 Yocto 的底层构建框架
- **Layers（层）**：包含相关指令和配置集合的仓库，按功能隔离（BSP 层、发行版层、应用层等），便于模块化开发和复用。约定层名称以 `meta-` 开头
- **Recipes（配方）**：`.bb` 文件，描述如何获取、编译和安装一个软件包
- **Images（镜像）**：最终构建产物，包含 bootloader、内核、根文件系统的完整 Linux 系统

### 2 构建环境要求

**硬件要求**：
- 磁盘空间：至少 140 GB（更多空间可复用构建缓存提升性能）
- 内存：至少 32 GB（建议尽可能多的 RAM 和 CPU 核心）

**软件要求**：
- 受支持的 Linux 发行版（Ubuntu、Fedora、Debian、openSUSE、CentOS 等）
- Git >= 1.8.3.1
- tar >= 1.28
- Python >= 3.9.0
- gcc >= 10.1
- GNU make >= 4.0

**Ubuntu/Debian 主机所需软件包**：

```bash
sudo apt-get install build-essential chrpath cpio debianutils diffstat file gawk gcc \
  git iputils-ping libacl1 libcrypt-dev locales python3 python3-git python3-jinja2 \
  python3-pexpect python3-pip python3-subunit socat texinfo unzip wget xz-utils zstd
```

需要确保 `en_US.UTF-8` locale 已启用。

### 3 BitBake 构建流程

**基本构建步骤**（以 Yocto 官方 Poky 为例）：

```bash
# 1. 克隆 bitbake
git clone https://git.openembedded.org/bitbake

# 2. 初始化构建环境（交互式，选择配置/MACHINE/DISTRO）
./bitbake/bin/bitbake-setup init

# 3. 进入构建目录，初始化环境
source <setup-dir>/build/init-build-env

# 4. 查看当前配置片段
bitbake-config-build list-fragments

# 5. 构建镜像
bitbake core-image-sato

# 6. 使用 QEMU 模拟运行
runqemu snapshot
```

**关键配置变量**：
- `DISTRO`：发行版配置（如 `poky`、`openstlinux-weston`）
- `MACHINE`：目标机器（如 `qemux86-64`、`stm32mp1`）
- `IMAGE`：目标镜像（如 `core-image-sato`、`st-image-weston`）

### 4 添加 BSP 层

```bash
# 克隆 BSP 层（以 Raspberry Pi 为例）
git clone -b wrynose https://git.yoctoproject.org/meta-raspberrypi ../layers/meta-raspberrypi

# 添加层到构建配置
bitbake-layers add-layer ../layers/meta-raspberrypi

# 切换 MACHINE
bitbake-config-build enable-fragment machine/raspberrypi5
```

### 5 创建自定义层

```bash
# 使用 bitbake-layers 工具创建新层
bitbake-layers create-layer ../layers/meta-mylayer

# 添加到构建配置
bitbake-layers add-layer ../layers/meta-mylayer
```

创建后的层目录结构：
```
meta-mylayer/
  conf/
    layer.conf
  recipes-example/
    example/
      example.bb
  COPYING.MIT
  README
```

---

## 第二部分 ST STM32MP1 OpenSTLinux 发行版

### 1 Distribution Package 内容

ST 的 Distribution Package 基于 **OpenEmbedded / Yocto Project** 构建框架，提供：

**Cortex-A 侧（Linux）**：
- **OpenSTLinux 发行版**：包含完整源码的 BSP（Linux 内核、U-Boot、TF-A、OP-TEE）和应用框架（Wayland-Weston、GStreamer、ALSA 等）
- 发行版基于 OpenEmbedded 构建

**Cortex-M 侧（裸机/RTOS）**：
- **STM32CubeMP1 Package**：包含 BSP、HAL、中间件和应用的完整源码
- 通过 `meta-st-stm32mp` 层中的 recipe 集成到 OpenSTLinux 发行版：
  - `recipes-extended/m4projects/m4projects-stm32mp1.bb` 或
  - `recipes-extended/stm32mp1-projects/m4projects-stm32mp1.bb`

**工具**：
- STM32CubeProgrammer：烧写工具

### 2 ST Yocto 层结构

ST 的 OpenSTLinux 发行版包含以下层结构：

```
Distribution-Package/
  OpenSTLinux distribution/
    layers/
      meta-openembedded/              # OE-Core 标准层集合
      meta-st/
        meta-st-openstlinux/          # ST 层：框架和镜像设置
        meta-st-stm32mp/              # ST 层：STM32MP BSP 描述
          recipes-bsp/
            alsa/                     # ALSA 控制配置
            ddr-firmware/             # DDR PHY 固件
            drivers/                  # Vivante GCNANO GPU 内核驱动
            fip-stm32mp/              # FIP 生成
            trusted-firmware-a/       # TF-A 配方
            u-boot/                   # U-Boot 配方
          recipes-extended/
            external-dt/              # 设备树文件
            linux-examples/           # Linux 示例
            stm32mp1-projects/        # Cortex-M4 固件示例
          recipes-graphics/
            gcnano-userland/          # Vivante OpenGL ES/EGL 库
          recipes-kernel/
            linux/                    # Linux 内核配方
            linux-firmware/           # Linux 固件
          recipes-security/
            optee/                    # OP-TEE 配方
          recipes-st/
            images/                   # bootfs 和 userfs 分区二进制
        meta-st-stm32mp-addons/       # STM32CubeMX 集成辅助层
        scripts/
          envsetup.sh                 # 环境初始化脚本
      openembedded-core/              # OE 核心元数据
```

### 3 安装 OpenSTLinux 发行版

ST 使用 Google 的 **repo** 工具管理多仓库清单。

**安装步骤**（以 v6.2.0 为例，基于 Yocto Scarthgap / Linux 6.6）：

```bash
# 进入安装目录
cd <working directory>/Distribution-Package

# 初始化 repo（使用 ST 的 manifest 仓库）
repo init -u https://github.com/STMicroelectronics/oe-manifest.git \
  -b refs/tags/openstlinux-6.6-yocto-scarthgap-mpu-v26.02.18

# 同步所有仓库
repo sync
```

安装后约 140 MB，编译后约 25 GB。

**注意**：Yocto 使用绝对目录路径命名中间文件，路径过长会导致构建失败。

### 4 初始化构建环境

```bash
DISTRO=openstlinux-weston MACHINE=<machine> source layers/meta-st/scripts/envsetup.sh
```

**ST 支持的关键变量值**：

| 变量 | 值 | 说明 |
|------|------|------|
| DISTRO | `openstlinux-weston` | 带 Wayland/Weston 的发行版 |
| MACHINE | `stm32mp1` | STM32MP15x 系列 |
| MACHINE | `stm32mp13` | STM32MP13x 系列 |
| IMAGE | `st-image-weston` | Weston 图形镜像 |

执行 `envsetup.sh` 后：
- 创建 `build-<distro>-<machine>/` 构建目录
- 生成 `conf/local.conf`（本地用户配置）
- 生成 `conf/bblayers.conf`（层配置）
- BSP 依赖受 SLA（软件许可协议）保护的包和固件，需接受 EULA

### 5 构建 OpenSTLinux 镜像

```bash
# 确保已运行 envsetup.sh
bitbake st-image-weston
```

构建产物位于 `build-<distro>-<machine>/tmp-glibc/deploy/images/<machine>/` 目录。

### 6 烧写与启动

使用 STM32CubeProgrammer 将构建产物烧写到目标存储设备（microSD 卡、eMMC 等）。烧写完成后，配置启动开关选择对应的启动源。

### 7 自定义开发

#### 7.1 创建自定义层

```bash
# 查看当前层列表和优先级
bitbake-layers show-layers

# 创建新层（指定优先级 7）
bitbake-layers create-layer --priority 7 ../layers/meta-st/meta-my-custo-layer

# 添加到构建配置
bitbake-layers add-layer ../layers/meta-st/meta-my-custo-layer/
```

**层优先级（priority）机制**：
- 决定 BitBake 应用规则的顺序
- 优先级数值越大，优先级越高
- 当两个层对同一配方有 `.bbappend` 文件时，低优先级层的规则先应用，高优先级层的规则后应用（可覆盖低优先级层）

#### 7.2 devtool 工具

`devtool` 是 OpenEmbedded 的配套开发工具，用于在发行版构建环境中开发、构建和测试代码：
- 添加新应用或库
- 修改现有应用
- 将开发成果集成回构建系统

#### 7.3 集成 Developer Package 的开发成果

ST 提供了从 Distribution Package 上下文进行交叉编译的方法，以及将开发成果集成到 Yocto 构建流程的指南：
- 添加客户应用程序：`How to add a customer application`
- 自定义 Linux 内核：`How to customize the Linux kernel`

### 8 创建自定义发行版

1. **自定义机器配置**：适配硬件修改（`How to create your own machine`）
2. **创建自定义发行版**：启用框架（Wayland、X11）和功能（ALSA、NFS、WiFi、蓝牙、IPv6 等）（`How to create your own distribution`）
3. **创建自定义镜像**：添加缺失的用户态工具（libdrm、evtest、iptables、i2c-tools 等）（`How to create your own image`）

### 9 生成自定义 Starter/Developer Package

```bash
# 启用归档功能（local.conf 中添加）
ST_ARCHIVER_ENABLE = "1"

# 构建镜像并生成归档
bitbake st-image-weston --runall=deploy_archives
```

构建产物：
- **Starter Package 镜像**：`build-<DISTRO>-<MACHINE>/tmp-glibc/deploy/images/<machine>/`
- **Developer Package 源码**：`build-<distro>-<machine>/tmp-glibc/deploy/sources/arm-ostl-linux-gnueabi/`
- **SDK**：通过 `How to create an SDK for OpenSTLinux distribution` 生成（仅支持 64 位主机）

---

## 第三部分 主要软件组件版本

以 STM32MPU Ecosystem v6.2.0 为例：

| 组件 | 版本 |
|------|------|
| Linux 内核 | v6.6-stm32mp-r3 (LTS v6.6.116) |
| U-Boot | v2023.10-stm32mp-r3 |
| TF-A | v2.10-stm32mp-r3 (LTS v2.10.24) |
| OP-TEE | v4.0.0-stm32mp-r3 |
| STM32CubeMP1 Package | v1.7.0 |
| OpenEmbedded | v5.0.15 (Scarthgap) |

---

## 第四部分 Secure Boot

ST Wiki 上的 OP-TEE Secure Boot 配置页面（`How_to_configure_the_OP-TEE_for_secure_boot`）在本次抓取时无法访问。Secure Boot 通常涉及：
- TF-A（Trusted Firmware-A）的安全启动链
- OP-TEE 作为安全操作系统
- FIP（Firmware Image Package）签名验证
- 详细的 STM32MP1 Secure Boot 配置可参考 ST 官方 Wiki 或 STM32MP1 参考手册中的安全章节

---

## 参考链接

| 资源 | URL |
|------|-----|
| Yocto Project 官方文档 | https://docs.yoctoproject.org/ |
| Yocto Quick Build | https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html |
| ST STM32MPU Distribution Package | https://wiki.st.com/stm32mpu/wiki/STM32MPU_Distribution_Package |
| ST 创建 OE 层 | https://wiki.st.com/stm32mpu/wiki/How_to_create_a_new_open_embedded_layer |
| ST OE devtool | https://wiki.st.com/stm32mpu/wiki/OpenEmbedded_-_devtool |
| ST BitBake 速查表 | https://wiki.st.com/stm32mpu/wiki/BitBake_cheat_sheet |
| ST OpenSTLinux 发行版 | https://wiki.st.com/stm32mpu/wiki/OpenSTLinux_distribution |
| ST oe-manifest 仓库 | https://github.com/STMicroelectronics/oe-manifest.git |
| Yocto Layer Index | https://layers.openembedded.org/ |
