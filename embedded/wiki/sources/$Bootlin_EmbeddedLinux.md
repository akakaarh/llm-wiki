---
title: Bootlin Embedded Linux 系统开发培训
source: Bootlin Embedded Linux system development training slides (552 pages, CC-BY-SA 3.0)
type: source
tags: [bootlin, embedded-linux, training, kernel, buildroot, yocto, cross-compile, u-boot, device-tree, rootfs]
created: 2026-05-24
---

# Bootlin Embedded Linux 系统开发培训

Bootlin（前身为 Free Electrons）是法国的嵌入式 Linux 工程服务公司，自 2004 年运营以来在 Linux 内核贡献排名全球前 30，提交超过 9000 个内核补丁和 6000 个 Buildroot 补丁。本课程是其旗舰培训，共 552 页幻灯片，涵盖从交叉编译到系统集成的完整嵌入式 Linux 开发流程。

**课程信息：**
- 时长：线下 5 天/40 小时，在线 7 个半天/28 小时
- 许可证：Creative Commons BY-SA 3.0，所有材料免费开放
- 实操平台：STM32MP157 Discovery、BeagleBone Black、BeaglePlay、NXP i.MX93 FRDM
- 幻灯片地址：https://bootlin.com/doc/training/embedded-linux/embedded-linux-slides.pdf

**配套课程：**
- Linux 内核与驱动开发培训（5 天）：https://bootlin.com/training/kernel/
- Buildroot 系统开发培训（3 天）
- Yocto/OpenEmbedded 系统开发培训（3 天）

---

## 1 嵌入式 Linux 概述（p18-40）

### 1.1 什么是嵌入式 Linux

嵌入式 Linux 是在嵌入式系统中使用 Linux 内核和各种开源组件。Linux 自 2000 年起在嵌入式领域日益流行，2012 年随 Raspberry Pi、BeagleBone Black 进入低成本硬件市场。

### 1.2 使用 Linux 和开源的优势

- **质量**：基于高质量基础组件（内核、编译器、C 库）
- **低成本**：无按版税，开发工具免费
- **完全控制**：自主决定何时更新组件，无供应商锁定
- **安全性**：可追溯所有组件源码，独立进行漏洞评估
- **社区支持**：获得社区良好支持
- **组件复用**：支持大量功能、协议和硬件，专注产品附加值

### 1.3 嵌入式硬件基础

**处理器架构：**
- x86/x86-64：工业和多媒体嵌入式
- ARM：数百种 SoC，覆盖所有产品类型
- RISC-V：新兴免费指令集架构
- PowerPC、MIPS、Microblaze（Xilinx）、Nios II（Altera）
- Linux 支持 MMU 和 no-MMU 架构（no-MMU 有限制），不支持 8/16 位微控制器

**RAM 和存储：**
- 最低 8 MB RAM 可运行基本 Linux，实际系统通常需至少 32 MB
- 最低 4 MB 存储，支持 SD/MMC/eMMC/USB/SATA 等块存储
- 支持 NAND/NOR Flash 原始闪存存储，需专用文件系统

**通信总线支持：**
- I2C、SPI、1-wire、SDIO、PCI、USB、CAN
- 网络：以太网、WiFi、蓝牙、CAN、IPv4/IPv6、TCP/UDP、防火墙、高级路由

**硬件平台类型：**
- 评估平台（SoC 厂商提供，外设齐全但昂贵）
- SoM（System on Module，仅 CPU/RAM/Flash，通过连接器扩展外设）
- 社区开发平台（BeagleBone、Raspberry Pi 等，低成本就绪）
- 定制平台（基于评估板或开发平台的原理图设计）

**选型标准：** SoC 是否被 Linux 官方主线支持是关键差异，主线支持意味着更好的质量、新版本和 LTS 支持。

### 1.4 嵌入式 Linux 系统架构

```
开发主机 (Host)                    嵌入式目标 (Target)
┌──────────────┐                 ┌──────────────┐
│ 应用程序      │                 │ 应用程序      │
│ 编译器/调试器  │                 │ C 库          │
│ 工具链        │                 │ Linux 内核    │
└──────────────┘                 │  设备驱动     │
    ↕ 串口/网络/JTAG              │  网络/文件系统  │
                                 │ Bootloader    │
                                 │  (启动后消失)  │
                                 └──────────────┘
```

**核心软件组件：**
1. **交叉编译工具链** — 在开发机运行，生成目标机代码
2. **Bootloader** — 硬件初始化，加载和执行内核
3. **Linux 内核** — 进程管理、内存管理、网络栈、设备驱动
4. **C 库** — C 函数库，内核与用户空间的接口
5. **库和应用程序** — 第三方或自研

**嵌入式 Linux 工作划分：**
- BSP 开发：包含 bootloader 和内核及目标硬件的设备驱动
- 系统集成：将 bootloader、内核、第三方库和应用集成到完整系统
- 应用开发：使用特定库开发 Linux 用户空间应用

---

## 2 开发环境（p41-47）

### 2.1 主机操作系统

强烈推荐使用 GNU/Linux 作为桌面开发系统。所有社区工具设计为在 Linux 上运行。如使用 Windows，可用 VirtualBox 虚拟机或 WSL2。推荐 Ubuntu 发行版。

### 2.2 串口通信工具

嵌入式开发必备工具，常用选项：
- **Picocom**（推荐，最简单）：`sudo apt install picocom`，运行 `picocom -b 115200 /dev/ttyUSB0`，退出 `[Ctrl][a] [Ctrl][x]`
- 其他：Minicom、Gtkterm、Putty、screen、tmux、tio

---

## 3 交叉编译工具链（p48-85）

### 3.1 工具链定义

交叉编译工具链在开发主机（通常 x86）上运行，但生成目标架构的二进制代码。原因：目标机存储/内存受限、速度慢、不宜安装全部开发工具。

**工具链组件：**
- **Binutils**：汇编器（as）、链接器（ld）、objdump、readelf 等二进制工具
- **GCC**：C/C++ 编译器（也支持其他语言）
- **C 库**：glibc（功能全、体积大）、uClibc-ng（小体积）、musl（干净设计、静态链接友好）
- **GDB**：调试器（可选，支持远程调试）

### 3.2 获取工具链

**预编译工具链（推荐入门）：**
- ARM 官方：`https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a`
- Bootlin 提供：`https://toolchains.bootlin.com/`（支持多种架构和 C 库组合，定期更新）
- 发行版包管理器：`sudo apt install gcc-arm-linux-gnueabi`（但版本可能较旧）

**自建工具链（推荐生产）：**
- Crosstool-NG：基于 kconfig 配置，类似内核配置系统
- 安装：`./configure --enable-local && make` 构建 ct-ng 可执行文件
- 配置：`./ct-ng list-samples` 列出示例，`./ct-ng <sample-name>` 加载示例配置
- 精调：`./ct-ng menuconfig` 或 `./ct-ng nconfig`
- 构建：`./ct-ng build`（自动下载依赖，按正确顺序构建所有组件）

**工具链关键目录：**
- `bin/`：交叉编译工具二进制文件（可加入 PATH）
- `<arch-tuple>/sysroot/lib`：目标架构的 C 库、GCC 运行时、C++ 标准库
- `<arch-tuple>/sysroot/usr/include`：C 库头文件和内核头文件

### 3.3 交叉编译注意事项

- 使用 `--host=` 指定目标机器类型（autotools）
- `CROSS_COMPILE` 变量指定工具链前缀
- sysroot 目录包含目标系统的头文件和库
- ccache 可加速重复编译（约 7 倍提速）

---

## 4 Bootloader 与固件（p86-197）

### 4.1 Bootloader 角色

Bootloader 是处理器运行的首个可由开发者修改的代码，负责：
1. 基本硬件初始化
2. 从存储/网络加载操作系统内核
3. 可能的解压缩
4. 执行内核
5. 提供 shell/菜单用于诊断和配置

### 4.2 嵌入式启动流程

**典型两阶段启动：**
1. **ROM 代码**（处理器厂商固化，不可修改）：从 NAND/NOR/USB/SD/eMMC 加载第一阶段 bootloader 到内部 SRAM
2. **第一阶段 bootloader**（如 SPL/TPL）：在 SRAM 中运行，初始化 DDR 控制器
3. **第二阶段 bootloader**（如 U-Boot）：在 DDR 中运行，加载内核
4. **Linux 内核**：接管系统

**ROM 代码恢复机制：** 大多数 SoC 提供通过 UART/USB 刷写 bootloader 的恢复功能。
- STM32MP1：STM32 Cube Programmer
- NXP i.MX：uuu
- Microchip AT91/SAM：SAM-BA
- Allwinner：sunxi-fel
- 通用工具：Snagboot（https://github.com/bootlin/snagboot）

### 4.3 x86 启动方式

**Legacy BIOS 启动：**
- MBR（主引导记录）：第一扇区含 446 字节 bootloader 代码
- 分为 Stage 1（446 字节）和 Stage 2（从原始存储加载，支持文件系统）

**UEFI 启动：**
- 从 EFI 系统分区加载 EFI 二进制文件
- 分区格式为 FAT，文件路径 `/efi/boot/bootx64.efi`
- ACPI 表描述运行时不可动态发现的硬件

### 4.4 ARM 启动方式

**ARMv7/ARMv8 异常级别：**
- EL3（最高特权）：安全固件（Secure Monitor），仅安全世界
- EL2：虚拟化（Hypervisor）
- EL1：Linux 内核
- EL0：用户空间应用
- 两个世界：Normal World（Linux）和 Secure World（TrustZone）

**安全固件接口：**
- PSCI（Power State Coordination Interface）：CPU 开关机、空闲状态、平台重启
- SCMI（System Control and Management Interface）：电源域、时钟、传感器、性能
- TF-A（Trusted Firmware-A）：ARM 安全固件参考实现，运行在 EL3

**可信执行环境：**
- OP-TEE：最常见的开源 TEE 实现，被大多数芯片厂商支持
- 硬件分区隔离安全世界和普通世界

**RISC-V 启动：**
- M-mode（机器模式）、S-mode（内核）、U-mode（用户空间）
- SBI（Supervisor Binary Interface）：标准化固件接口
- OpenSBI：SBI 的参考开源实现

### 4.5 常用 Bootloader

**U-Boot（嵌入式事实标准）：**
- 支持 ARM、ARM64、RISC-V、PowerPC、MIPS 等所有嵌入式架构
- 支持 x86 UEFI 固件
- 几乎所有 SoC/SoM/板卡厂商的默认 bootloader
- 官网：https://www.denx.de/wiki/U-Boot

**Barebox：**
- 替代 U-Boot 的 bootloader，使用 kconfig 配置
- 更 Linux 风格的 shell 接口，更清洁的代码
- 但使用率低于 U-Boot，平台支持较少
- 官网：https://www.barebox.org/

**GRUB：** x86 平台事实标准，支持 Legacy BIOS 和 UEFI

**systemd-boot：** 简单的 UEFI 启动管理器，比 GRUB 简单

### 4.6 U-Boot 详解（p120-197）

**获取与配置：**
- 源码：ftp://ftp.denx.de/pub/u-boot/ 或 `git clone git://git.denx.de/u-boot.git`
- 配置：`make <board_name>_defconfig`（如 `make stm32mp15_basic_defconfig`）
- 精调：`make menuconfig`（kconfig 配置系统）

**编译：**
- 交叉编译：`export CROSS_COMPILE=arm-linux-`，`make`
- 生成文件：`u-boot.bin`（裸二进制）、`u-boot.img`（带头部，可被 U-Boot 加载）、`u-boot-spl`（第一阶段）

**环境变量：**
- 存储在持久存储（Flash/eMMC/SD）的专用区域
- `printenv` 查看，`setenv` 设置，`saveenv` 保存
- 特殊变量：`bootcmd`（自动启动命令）、`bootargs`（传递给内核的命令行参数）

**U-Boot 命令：**
- 存储操作：`mmc read/write/info`、`nand read/write/erase`、`ext4load`
- 网络操作：`tftp`、`nfs`、`ping`
- 内存操作：`md`（显示）、`mw`（写入）、`cp`（复制）
- 启动命令：`bootm`（从内存启动映像）、`bootz`（启动 zImage）、`booti`（启动 Image/ARM64）

**TFTP 网络传输：**
- 开发主机安装 TFTP 服务器：`sudo apt install tftpd-hpa`
- 文件放入 `/srv/tftp` 目录
- U-Boot 中：配置 `ipaddr`、`serverip`、`ethaddr`，使用 `tftp <address> <filename>` 加载

**脚本自动化：**
- 环境变量可包含脚本，用 `;` 链接命令，用 `if command ; then ... ; else ... ; fi` 测试
- `run` 命令执行环境变量中存储的脚本

**设备树传递：**
- U-Boot 加载设备树 blob（DTB）到内存
- `bootm` 命令接受内核地址和 DTB 地址：`bootm <kernel_addr> - <dtb_addr>`
- 或将 DTB 地址存入 `fdt_addr` 环境变量

---

## 5 Linux 内核（p198-269）

### 5.1 内核角色

Linux 内核是系统的核心，负责：
- 进程管理（调度、上下文切换）
- 内存管理（虚拟内存、MMU 配置）
- 文件系统支持
- 网络协议栈
- 设备驱动
- 提供系统调用接口给用户空间

### 5.2 获取内核源码

- 官方：`https://www.kernel.org/`
- Git 仓库：`git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git`
- 稳定版本：`git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git`
- 版本命名：`<major>.<minor>.<patch>`（如 6.1.52），偶数 minor 为稳定版

### 5.3 内核配置

**配置系统（kconfig）：**
- `make menuconfig` — 基于 ncurses 的菜单界面
- `make nconfig` — 新版 ncurses 界面
- `make xconfig` — 基于 Qt 的图形界面
- `make gconfig` — 基于 GTK 的图形界面

**配置选项类型：**
- bool（y/n）：编译进内核或不编译
- tristate（y/m/n）：编译进内核、编译为模块或不编译
- string/hex/int：字符串、十六进制值、整数

**预定义配置：**
- `make defconfig`：架构默认配置
- `make <board>_defconfig`：特定板卡配置
- `make allnoconfig`：最小配置
- `make allyesconfig`：尽可能多的配置

### 5.4 内核编译

- 设置交叉编译：`export CROSS_COMPILE=arm-linux-`，`export ARCH=arm`
- 并行编译：`make -j$(nproc)`（推荐使用全部 CPU 核心）
- ccache 加速：`export CROSS_COMPILE="ccache arm-linux-"`（约 7 倍提速）
- 不要以 root 用户编译

**编译结果：**
- `arch/<arch>/boot/Image`：未压缩内核镜像
- `arch/<arch>/boot/zImage`（ARM）或 `bzImage`（x86）：压缩内核镜像
- `vmlinux`：ELF 格式的内核（调试用）
- `*.dtb`：设备树 blob 文件
- `*.ko`：内核模块文件

### 5.5 内核安装

- 将 zImage/Image 复制到目标存储（SD 卡、eMMC、TFTP 目录等）
- 将 DTB 文件放在内核可访问的位置
- 模块安装：`make modules_install INSTALL_MOD_PATH=<rootfs_path>`

### 5.6 内核启动参数

通过 bootloader 传递（U-Boot 的 `bootargs` 变量）：
- `console=ttySTM0,115200`：控制台串口和波特率
- `root=/dev/mmcblk0p2`：根文件系统设备
- `rootfstype=ext4`：根文件系统类型
- `init=/sbin/init`：init 程序路径
- `mem=256M`：限制可用内存

---

## 6 设备树（p270-309）

### 6.1 为什么需要设备树

传统方式将硬件描述硬编码在内核源码中（arch/arm/mach-*），导致大量重复代码。设备树（Device Tree）是一种数据结构，用于描述硬件拓扑，使内核代码与硬件描述分离。

### 6.2 设备树基础

**三种文件格式：**
- **DTS（Device Tree Source）**：人类可读的文本格式
- **DTB（Device Tree Blob）**：编译后的二进制格式，传递给内核
- **DTSI（Device Tree Source Include）**：可被 DTS 包含的片段

**设备树语法：**
```dts
/dts-v1/;
/ {
    model = "STMicroelectronics STM32MP157C-DK2 Board";
    compatible = "st,stm32mp157c-dk2", "st,stm32mp157";

    chosen {
        bootargs = "root=/dev/mmcblk0p4 rootwait";
    };

    memory@0xc0000000 {
        reg = <0xc0000000 0x20000000>;
    };

    soc {
        serial@40011000 {
            compatible = "st,stm32-usart";
            reg = <0x40011000 0x400>;
            status = "okay";
        };
    };
};
```

**节点结构：**
- 根节点 `/` 包含整个系统的描述
- 节点名格式：`<name>[@<unit-address>]`
- `compatible` 属性：用于匹配设备驱动（最重要的属性）
- `reg` 属性：设备寄存器地址和大小
- `status` 属性：`okay`（启用）、`disabled`（禁用）

### 6.3 设备树编译器（dtc）

- `dtc -I dts -O dtb -o output.dtb input.dts`：编译 DTS 到 DTB
- `dtc -I dtb -O dts -o output.dts input.dtb`：反编译 DTB 到 DTS
- 内核构建系统自动编译相关 DTB

### 6.4 设备树在启动中的传递

- DTB 可链接到 bootloader 二进制中
- 或从存储/网络加载到 RAM
- U-Boot 通过 `bootm <kernel_addr> - <dtb_addr>` 将 DTB 地址传递给内核
- ARM64 使用 DTS 描述硬件成为强制要求

### 6.5 设备树绑定（Bindings）

设备树绑定文档定义了各设备类型的节点和属性规范：
- 位于内核源码 `Documentation/devicetree/bindings/`
- 现在迁移到 YAML 格式：`Documentation/devicetree/bindings/*/`
- 为每个设备子系统定义了必需和可选属性

---

## 7 根文件系统（p260-340+）

### 7.1 根文件系统组成

根文件系统（rootfs）是 Linux 内核挂载的第一个文件系统，包含：
- **基本目录结构**：`/bin`、`/sbin`、`/lib`、`/etc`、`/usr`、`/var`、`/proc`、`/sys`、`/dev`、`/tmp`
- **init 程序**：内核启动的第一个用户空间进程（PID 1）
- **C 库**：glibc 或 musl 或 uClibc-ng
- **shell 和基本工具**：BusyBox 提供精简的 shell 和核心命令
- **配置文件**：`/etc/init.d/`、`/etc/fstab`、`/etc/passwd` 等
- **设备节点**：`/dev/` 下的字符设备和块设备

### 7.2 设备文件系统

- **devtmpfs**：内核自动创建设备节点的虚拟文件系统，挂载在 `/dev`
- **sysfs**：`/sys`，内核导出设备模型信息
- **procfs**：`/proc`，进程和内核信息
- **tmpfs**：`/tmp`、`/var`，基于 RAM 的临时文件系统

### 7.3 设备类型

- **字符设备**：串口、终端、声卡、视频设备等，以字节流访问
- **块设备**：硬盘、SD 卡、USB 存储等，以固定大小块访问
- 设备标识三元组：`类型（字符/块）`、`主设备号`（设备类别）、`次设备号`（具体设备实例）

### 7.4 文件系统类型

**块存储文件系统：**
- **ext4**：最常用 Linux 文件系统，支持日志
- **FAT/VFAT**：与 Windows 兼容，用于 SD 卡、EFI 分区
- **Btrfs**：高级文件系统，支持快照、压缩、校验
- **SquashFS**：只读压缩文件系统，适合只读根文件系统

**Flash 存储文件系统：**
- **JFFS2**：用于 NOR/NAND Flash 的日志文件系统
- **UBIFS**：用于 NAND Flash，UBI 层管理坏块
- **YAFFS2**：另一种 NAND Flash 文件系统

### 7.5 NFS 根文件系统

开发阶段常用，通过网络挂载根文件系统：
- 内核配置：`CONFIG_ROOT_NFS=y`
- 启动参数：`root=/dev/nfs nfsroot=<server_ip>:<path> ip=dhcp`
- 优势：无需反复刷写目标存储，方便开发调试

---

## 8 构建系统（p340-450）

### 8.1 为什么需要构建系统

手动构建嵌入式 Linux 系统涉及数百个包（工具链、bootloader、内核、库、应用程序），每个都有不同的构建方法和依赖。构建系统自动化这一过程。

### 8.2 Buildroot

**概述：**
- 简单、轻量级的嵌入式 Linux 构建系统
- 基于 Makefile 和 kconfig
- 构建完整系统约 15-30 分钟
- 生成：工具链（可选）、rootfs、内核镜像、bootloader（可选）

**基本使用：**
```bash
make menuconfig    # 配置
make               # 构建
make clean         # 清理构建产物
```

**配置选项：**
- Target Architecture：目标架构（ARM、ARM64、MIPS 等）
- Toolchain：选择内置或外部工具链
- System configuration：rootfs 选项、init 系统、主机名等
- Kernel：内核版本、配置文件、DTB
- Bootloader：U-Boot 版本、配置
- Target packages：选择要包含的软件包
- Filesystem images：输出格式（ext4、SquashFS、initramfs 等）

**输出目录（`output/`）：**
- `images/`：所有镜像文件
- `build/`：各组件构建目录
- `host/`：主机工具和 sysroot
- `target/`：近似完整的 rootfs（不含 /dev 设备文件）

**扩展机制：**
- 自定义包：创建 `package/<pkg>/<pkg>.mk` 和 `<pkg>.mk`
- 包覆盖：`BR2_ROOTFS_OVERLAY` 覆盖 rootfs 中的文件
- 后构建脚本：`BR2_ROOTFS_POST_BUILD_SCRIPT`
- 后镜像脚本：`BR2_ROOTFS_POST_IMAGE_SCRIPT`

**法律合规：** `make legal-info` 生成所有包的许可证清单。

### 8.3 Yocto Project / OpenEmbedded

**概述：**
- 更复杂但更强大的构建框架
- 基于 BitBake 任务调度器和 metadata（recipes/layers）
- 适合需要高度定制化和长期维护的商业产品
- 构建时间较长（数小时）

**核心概念：**
- **Recipe（.bb 文件）**：描述如何获取、编译、安装单个软件包
- **Layer**：相关 recipe 的集合，可独立维护
- **Machine**：目标硬件描述
- **Image**：最终 rootfs 镜像的 recipe
- **SDK**：交叉开发工具链

**基本工作流：**
```bash
source oe-init-build-env
bitbake core-image-minimal   # 构建最小镜像
bitbake <recipe>             # 构建特定 recipe
```

### 8.4 Buildroot vs Yocto 对比

| 特性 | Buildroot | Yocto |
|------|-----------|-------|
| 学习曲线 | 低 | 高 |
| 构建速度 | 快（~30分钟） | 慢（数小时） |
| 配置方式 | kconfig | BitBake + metadata |
| 包管理 | 无运行时包管理 | opkg/rpm/deb |
| 定制深度 | 中等 | 非常深 |
| 社区 | 活跃，Bootlin 共同维护 | 行业标准 |
| 适用场景 | 中小项目、原型开发 | 大型商业产品 |

---

## 9 应用开发与调试（p400-450）

### 9.1 交叉编译应用

**构建系统识别：**
- **手写 Makefile**：直接指定 `CC=arm-linux-gcc`
- **Autotools**：`./configure --host=arm-linux --prefix=/usr`，然后 `make && make install DESTDIR=<path>`
- **CMake**：`cmake -DCMAKE_TOOLCHAIN_FILE=<toolchain-file> ..`
- **Meson**：使用交叉编译文件

**Autotools 四步流程：**
1. `autoreconf`（如需要，生成 configure 脚本）
2. `./configure --host=arm-linux`（配置交叉编译）
3. `make`（编译）
4. `make install DESTDIR=<sysroot>`（安装到目标 sysroot）

### 9.2 调试

**GDB 远程调试：**
- 目标机运行 `gdbserver`：`gdbserver :1234 ./application`
- 主机 GDB 连接：`arm-linux-gdb ./application`，`(gdb) target remote <target_ip>:1234`
- 或通过串口：`target remote /dev/ttyUSB0`

**strace 系统调用追踪：**
- `strace ./application` 追踪所有系统调用
- `strace -e trace=open,read,write` 追踪特定系统调用
- 可附加到已运行进程：`strace -p <pid>`

**性能分析：**
- `perf`：Linux 内核性能分析工具
- `valgrind`：内存泄漏和错误检测
- `top`/`htop`：CPU 和内存使用监控

---

## 10 开源许可证（p460-470+）

### 10.1 主要许可证

**GPL（GNU General Public License）：**
- 强 copyleft：衍生作品必须以相同许可证发布
- 仅在分发时触发义务
- Linux 内核、U-Boot、BusyBox 使用 GPLv2
- GPLv3 增加反 Tivoization 条款（消费设备必须允许用户运行修改版本）

**LGPL（Lesser GPL）：**
- 弱 copyleft：链接 LGPL 库的程序可保持专有
- glibc、uClibc 使用 LGPL
- 静态链接时需提供目标文件以便重新链接

**宽松许可证（Permissive）：**
- MIT、BSD（2-clause/3-clause）、Apache 2.0
- 允许代码被专有软件使用
- 仅需保留版权声明

### 10.2 合规实践

- 使用前确认许可证与项目约束匹配
- 保持修改与原版分离
- 维护完整的自由软件包清单和版本
- Buildroot：`make legal-info`
- 在向客户交付产品前确保合规

---

## 11 相关培训课程

Bootlin 还提供以下免费开放材料的培训课程：
- **Linux 内核与驱动开发**（5 天）：内核架构、设备驱动 API、设备模型、中断处理、内存管理、调试技术
- **Buildroot 系统开发**（3 天）
- **Yocto/OpenEmbedded 系统开发**（3 天）
- **嵌入式 Linux 音频**（2 天）
- **实时 Linux（PREEMPT_RT）**（2 天）
- **Linux 调试、追踪与性能分析**（3 天）
- **嵌入式 Linux 安全**（2 天）
- **嵌入式 Linux 网络**（3 天）
- **Linux 图形栈**（3 天）

所有课程材料：https://bootlin.com/training/

---

## 与本 Wiki 的关联

- 交叉编译工具链概念与 `$Buildroot_UserManual.md` 中的工具链章节互补
- 设备树内容可建立 `#DeviceTree.md` 概念页
- U-Boot 启动流程与 STM32MP157 启动序列直接相关（参见 `$STM32MP157_ReferenceManual.md`）
- 根文件系统构建方法与 `$Buildroot_UserManual.md` 中的 rootfs 章节对应
- 内核编译和配置是阶段 6-7 学习路线的核心技能
