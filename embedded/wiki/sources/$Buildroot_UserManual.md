---
title: Buildroot 用户手册中文版
source: Buildroot用户手册中文版(正点原子翻译)_V1.0.pdf
type: source
tags: [buildroot, build-system, embedded-linux, rootfs, cross-compile]
created: 2026-05-24
---

# Buildroot 用户手册中文版

本文档是正点原子翻译的 Buildroot 官方用户手册中文版（基于 Buildroot 2020.02.6），系统性地介绍了 Buildroot 构建系统的使用方法、工作原理和开发指南。

---

## 第一部分 入门

### 1 关于 Buildroot

Buildroot 是一个通过交叉编译来简化和自动化构建嵌入式 Linux 系统的工具。它可以生成：
- 交叉编译工具链
- 根文件系统（rootfs）
- Linux 内核镜像
- bootloader 引导加载程序

Buildroot 可独立使用这些功能的任意组合（例如仅用现有工具链构建根文件系统）。支持 PowerPC、MIPS、ARM 等多种处理器架构，采用类似 Linux 内核的 menuconfig/gconfig/xconfig 配置界面，构建基本系统约需 15-30 分钟。

### 2 系统要求

Buildroot 设计为在 Linux 系统上运行。

**2.1 强制软件包**（必须在宿主机上安装）：
- 构建工具：which, sed, make (>=3.81), binutils, gcc (>=4.8), g++ (>=4.8), bash, patch, gzip, bzip2, perl (>=5.8.7), tar, cpio, unzip, rsync, file, bc
- 源码获取工具：wget

**2.2 可选软件包**：
- 推荐：Python 2.7+
- 配置界面依赖：ncurses5 (menuconfig), qt5 (xconfig), glib2/gtk2/glade2 (gconfig)
- 源码获取工具：bazaar, cvs, git, mercurial, rsync, scp, subversion
- Java 相关：javac, jar
- 文档生成：asciidoc (>=8.6.3), w3m, python-argparse, dblatex (仅 PDF)
- 图表生成：graphviz, python-matplotlib

### 3 获取 Buildroot

- 每 3 个月发布一次（2/5/8/11 月），版本号格式 YYYY.MM
- 源码包：http://buildroot.org/downloads/
- 支持通过 Vagrantfile 快速设置开发环境
- 可使用每日快照或克隆 Git 仓库跟踪开发

### 4 Buildroot 快速入门

**核心原则**：以普通用户身份构建所有内容，不需要 root 权限。

**配置界面**：
- `make menuconfig` — 基于 curses 的传统配置
- `make nconfig` — 基于 curses 的新版配置
- `make xconfig` — 基于 Qt 的配置
- `make gconfig` — 基于 GTK 的配置

配置完成后生成 `.config` 文件，被顶层 Makefile 读取。

**构建命令**：`make`（默认不支持顶级并行构建）

**构建步骤**：
1. 下载源文件
2. 配置、构建和安装交叉编译工具链（或导入外部工具链）
3. 配置、构建和安装选定的目标软件包
4. 构建内核镜像（如果选择）
5. 构建引导加载程序镜像（如果选择）
6. 以选定格式创建根文件系统

**输出目录结构**（`output/`）：
- `images/` — 所有镜像（内核、bootloader、根文件系统）
- `build/` — 所有组件的构建目录
- `host/` — 宿主机工具和目标工具链 sysroot
- `staging/` — 指向 host/ 中目标工具链 sysroot 的符号链接
- `target/` — 几乎完整的根文件系统（不含 /dev 设备文件，不可直接用于目标）

### 5 社区资源

- **Mailing List**：主要交流方式，需订阅才能发帖
- **IRC**：Freenode 上的 #buildroot 频道
- **Bug Tracker**：通过邮件列表或 bugtracker 报告
- **Wiki**：托管于 eLinux wiki
- **Patchwork**：基于 Web 的补丁跟踪系统（http://patchwork.buildroot.org）

---

## 第二部分 用户指南

### 6 Buildroot 配置

配置工具支持搜索功能：
- menuconfig 中按 "/" 调用搜索
- xconfig 中按 Ctrl+F 调用搜索

**6.1 交叉编译工具链**

工具链由编译器（gcc）、二进制工具（binutils）和 C 标准库组成。Buildroot 提供两种方案：

**6.1.1 内部工具链后端**（"Buildroot toolchain"）：
- Buildroot 自行构建交叉编译工具链
- 支持 C 库：uClibc-ng、glibc、musl
- 可配置：Linux 内核头文件版本、GCC/binutils/C库版本
- uClibc 特有选项：RPC 支持、宽字符、语言环境、C++、线程
- 可通过 `make uclibc-menuconfig` 深度定制 uClibc
- 优点：与 Buildroot 良好集成，只编译必要的
- 缺点：make clean 后需重新构建工具链

**6.1.2 外部工具链后端**（"External toolchain"）：
- 使用现有预构建的交叉编译工具链
- 集成 Linaro、CodeSourcery 等知名工具链
- 三种使用方式：
  1. 选择预定义配置文件，自动下载安装
  2. 选择预定义配置文件，指定本地路径
  3. 使用完全自定义工具链（"Custom toolchain"）
- 支持 crosstool-NG 和 Buildroot 本身生成的工具链
- 不支持 OpenEmbedded/Yocto 工具链或发行版工具链
- 优点：避免工具链构建时间
- 缺点：工具链 bug 难以修复

**6.1.3 使用 Buildroot 构建外部工具链**：
- 配置步骤：选择目标架构、保留默认工具链类型、Init system 选 None、禁用 BusyBox 和 tar
- 运行 `make sdk` 生成 SDK 压缩包
- 输出文件名格式：`arm-buildroot-linux-uclibcgnueabi_sdk-buildroot.tar.gz`
- 在其他项目中使用：Toolchain type 设为 External，选择 Custom toolchain，设置 Toolchain URL

**6.1.3.1 外部工具链包装器**：
- 环境变量 `BR2_DEBUG_WRAPPER`：0=无调试，1=跟踪所有参数，2=每行一个参数

**6.2 /dev 管理**

在 "System configuration" -> "/dev management" 下提供四种方式：

1. **Static using device table**：传统方式，设备文件持久存储，不能自动创建/删除。默认设备表：`system/device_table_dev.txt`。可通过 `BR2_ROOTFS_STATIC_DEVICE_TABLE` 自定义。

2. **Dynamic using devtmpfs only**：内核虚拟文件系统（2.6.32+），自动创建/删除设备文件。需启用 `CONFIG_DEVTMPFS` 和 `CONFIG_DEVTMPFS_MOUNT`。

3. **Dynamic using devtmpfs+mdev**：在 devtmpfs 基础上添加 mdev（BusyBox 组件），可配置 `/etc/mdev.conf` 实现自动加载内核模块、推送固件等。是 udev 的轻量级实现。

4. **Dynamic using devtmpfs+eudev**：在 devtmpfs 基础上添加 eudev 守护程序，比 mdev 更重量级但更灵活。eudev 是 udev 的独立版本。

推荐：从 "devtmpfs only" 开始，需要固件时用 "devtmpfs+mdev"。

**6.3 初始化系统**

在 "System configuration" -> "Init system" 下提供三种选择：

1. **BusyBox**（默认）：基本 init 程序，读取 `/etc/inittab`，启动 `/etc/init.d/rcS` 和 getty。适合大多数嵌入式系统。

2. **systemV**：传统 sysvinit，位于 `package/sysvinit`，语法与 BusyBox inittab 略有不同。

3. **systemd**：新一代 init 系统，支持并行处理、socket/D-Bus 激活、按需启动守护程序、cgroup 进程跟踪等。适合复杂嵌入式系统，但依赖较大（dbus、udev 等）。

### 7 其他组件的配置

修改前需先在 Buildroot 中启用相应软件包：

- **BusyBox**：`BR2_PACKAGE_BUSYBOX_CONFIG` 指定配置文件，`make busybox-menuconfig` 编辑
- **uClibc**：`BR2_UCLIBC_CONFIG` 指定配置文件，`make uclibc-menuconfig` 编辑
- **Linux kernel**：`BR2_LINUX_KERNEL_USE_CUSTOM_CONFIG` 或 `BR2_LINUX_KERNEL_USE_DEFCONFIG`，`make linux-menuconfig` 编辑
- **Barebox**：`BR2_TARGET_BAREBOX_USE_CUSTOM_CONFIG`/`BR2_TARGET_BAREBOX_USE_DEFCONFIG`，`make barebox-menuconfig`
- **U-Boot**（>=2015.04）：`BR2_TARGET_UBOOT_USE_CUSTOM_CONFIG`/`BR2_TARGET_UBOOT_USE_DEFCONFIG`，`make uboot-menuconfig`

### 8 Buildroot 的一般用法

**8.1 make 技巧**：
- `make V=1 <target>` — 显示所有执行的命令
- `make list-defconfigs` — 显示带 defconfig 的板级列表
- `make help` — 显示所有可用目标
- `make clean` — 删除所有构建产物
- `make distclean` — 删除所有构建产物及配置
- `make manual` — 生成手册（需额外工具）
- `make -s printvars VARS='VAR1 VAR2'` — 转储内部 make 变量（支持 QUOTED_VARS、RAW_VARS）

**8.2 了解何时需要完全重新构建**：
- 更改目标架构配置 → 需要完全重建
- 更改工具链配置 → 通常需要完全重建
- 新增软件包 → 不一定需要完全重建（但依赖库变更时可能需要）
- 删除软件包 → 需要完全重建才能移除
- 更改软件包子选项 → 通常只需重建该软件包
- 更改根文件系统 skeleton → 需要完全重建
- 更改 overlay/post-build/post-image 脚本 → 不需要完全重建
- 完全重建命令：`make clean all`

**8.3 了解如何重建软件包**：
- `make <package>-dirclean` — 删除构建目录，从头重建
- `make <package>-rebuild` — 从 build 步骤重启（仅重新编译和安装）
- `make <package>-reconfigure` — 从 configure 步骤重启
- Buildroot 通过 stamp 文件（`.stamp_<step-name>`）跟踪构建步骤

**8.4 离线构建**：`make source` 下载所有源码，之后可断开网络

**8.5 目录树外构建**：
- `make O=/tmp/build` 或 `cd /tmp/build; make O=$PWD -C path/to/buildroot`
- O 路径相对于 Buildroot 主目录
- 输出目录中会生成 Makefile 包装器

**8.6 环境变量**：
- `HOSTCXX`/`HOSTCC` — 宿主机编译器
- `UCLIBC_CONFIG_FILE`/`BUSYBOX_CONFIG_FILE` — 配置文件路径
- `BR2_CCACHE_DIR` — ccache 缓存目录
- `BR2_DL_DIR` — 下载目录
- `BR2_GRAPH_OUT` — 图表输出格式（pdf/png）
- `BR2_GRAPH_DEPS_OPTS`/`BR2_GRAPH_SIZE_OPTS` — 图表选项

**8.7 有效处理文件系统镜像**：使用稀疏文件（sparse file）节省存储空间，tar -S 和 cp --sparse=always

**8.8 绘制软件包之间的依赖关系图**：
- `make graph-depends` — 整个系统依赖关系图
- `make <pkg>-graph-depends` — 单个软件包依赖关系图
- 需安装 graphviz
- 选项：`--depth N`、`--stop-on PKG`、`--exclude PKG`、`--transitive`/`--no-transitive`

**8.9 绘制构建持续时间图**：`make graph-build`（需 python-matplotlib 和 python-numpy）

**8.10 绘制软件包对文件系统大小贡献图**：
- `make graph-size`（需 python-matplotlib）
- 生成饼图和 CSV 文件
- `utils/size-stats-compare` 比较两次构建的大小差异

**8.11 顶级并行构建**（实验性）：
- 启用 `BR2_PER_PACKAGE_DIRECTORIES`
- 使用 `make -jN` 启动构建
- 使用 per-package directories 机制隔离依赖

**8.12 与 Eclipse 集成**：简化应用程序的编译、远程执行和远程调试

**8.13 高级用法**：

**8.13.1 在外部使用生成的工具链**：
- 添加 `output/host/bin` 到 PATH
- `make sdk` 导出 SDK 压缩包
- `make prepare-sdk` 准备 SDK 但不生成压缩包

**8.13.2 使用 gdb**：
- 内部工具链：启用 `BR2_PACKAGE_HOST_GDB`、`BR2_PACKAGE_GDB`、`BR2_PACKAGE_GDB_SERVER`
- 外部工具链：启用 `BR2_TOOLCHAIN_EXTERNAL_GDB_SERVER_COPY`
- 目标运行：`gdbserver:2345 foo`
- 宿主机连接：`(gdb) target remote <target ip>:2345`

**8.13.3 使用 ccache**：
- 在 "Build options" 中启用 "Enable compiler cache"
- 缓存位于 `$HOME/.buildroot-ccache`
- `make ccache-stats` 查看统计
- `BR2_CCACHE_USE_BASEDIR` 使用相对路径避免缓存未命中

**8.13.4 下载软件包的位置**：
- 默认存储在 `dl/` 目录
- 通过 `BR2_DL_DIR` 环境变量或 .config 设置共享下载目录

**8.13.5 软件包特定 make 目标**：

构建步骤（按顺序）：source → depends → extract → patch → configure → build → install-staging/install-target/install → host

其他目标：show-depends、show-recursive-depends、show-rdepends、show-recursive-rdepends、graph-depends、graph-rdepends、dirclean、reinstall、rebuild、reconfigure

**8.13.6 在开发期间使用 Buildroot**：
- `<pkg>_OVERRIDE_SRCDIR` 机制：在 `local.mk` 中指定源码路径
- Buildroot 使用 rsync 同步源码到 `output/build/<package>-custom/`
- 配合 `make <pkg>-rebuild all` 实现快速迭代开发
- `<pkg>_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS` 排除不需要的文件

### 9 特定项目的定制

**9.1 推荐的目录结构**：
```
board/<company>/<boardname>/
  ├── linux.config
  ├── busybox.config
  ├── post_build.sh
  ├── post_image.sh
  ├── rootfs_overlay/
  └── patches/
configs/<boardname>_defconfig
package/<company>/
  ├── Config.in
  ├── <company>.mk
  ├── package1/
  └── package2/
```

**9.1.1 实施分层定制**：支持多层定制（如 common + fooboard），通过空格分隔的条目列表实现，Buildroot 从左到右处理。

**9.2 将定制保留在 Buildroot 之外**（br2-external 机制）：
- 通过 `BR2_EXTERNAL` 环境变量指定路径
- 支持多个 br2-external 目录树（冒号分隔）
- 必需文件：`external.desc`、`external.mk`、`Config.in`
- `external.desc`：定义 name（必填）和 desc（可选）
- 自动生成变量 `BR2_EXTERNAL_$(NAME)_PATH` 和 `BR2_EXTERNAL_$(NAME)_DESC`
- `configs/` 目录存放 defconfig 文件
- `provides/` 目录定义替代实现（toolchains、jpeg、openssl）
- `linux/` 目录添加 Linux 内核扩展

**9.3 存储 Buildroot 配置**：`make savedefconfig` 保存精简配置

**9.4 存储其他组件配置**：BusyBox/Linux 内核等使用 defconfig 或完整 .config

**9.5 自定义生成的目标文件系统**：
- `BR2_ROOTFS_OVERLAY` — 添加或覆盖文件
- `BR2_ROOTFS_POST_BUILD_SCRIPT` — 修改或删除文件、运行命令
- `BR2_ROOTFS_DEVICE_TABLE` — 设置文件权限和所有权
- `BR2_ROOTFS_STATIC_DEVICE_TABLE` — 添加自定义设备节点

**9.6 添加自定义用户帐户**：`BR2_ROOTFS_USERS_TABLES`

**9.7 创建镜像后进行自定义**：`BR2_ROOTFS_POST_IMAGE_SCRIPT`

**9.8 添加特定项目的补丁**：`BR2_GLOBAL_PATCH_DIR`

**9.9 添加特定项目的软件包**：在 package/ 或 br2-external 中创建

**9.10 特定项目自定义配置快速指南**：汇总所有定制方法的快速参考

### 10 常见问题和故障排除

- **10.1 启动网络后引导程序挂起**：可能是 MAC 地址冲突
- **10.2 为什么目标上没有编译器**：Buildroot 不在目标上安装编译器，需交叉编译
- **10.3 为什么目标上没有开发文件**：需启用 "development files in target" 选项
- **10.4 为什么目标上没有文档**：需启用 "documentation" 选项
- **10.5 为什么配置菜单中有些软件包不可见**：检查依赖是否满足
- **10.6 为什么不将 target 目录用作 chroot**：缺少设备文件、权限不正确
- **10.7 为什么不生成二进制软件包**：Buildroot 设计哲学是生成完整镜像而非包管理
- **10.8 如何加快构建过程**：使用 ccache、外部工具链、目录树外构建、并行构建

### 11 已知问题

当前版本存在以下已知问题和限制：

- **BR2_TARGET_LDFLAGS 中的 $ 符号问题**：如果选项包含 `$` 符号，则无法通过 `BR2_TARGET_LDFLAGS` 传递额外的链接器选项。例如，以下内容将被打断：`BR2_TARGET_LDFLAGS="-Wl,-rpath='$ORIGIN/../lib'"`
- **libffi 架构限制**：SuperH 2 和 ARC 体系架构不支持 libffi 软件包
- **prboom 编译器故障**：prboom 软件包使用 Sourcery CodeBench 2012.09 版本的 SuperH 4 编译器会触发编译器故障

### 12 法律声明和许可

**12.1 遵守开源许可证**：
- `make legal-info` 生成法律相关信息
- 输出位于 `output/legal-info/`
- 包含源码、许可证文本、版权声明等

**12.2 遵守 Buildroot 许可证**：Buildroot 本身使用 GPLv2+

**12.2.1 软件包补丁**：补丁继承原软件包的许可证

### 13 Buildroot 之外

**13.1 引导生成的镜像**：
- **13.1.1 NFS 引导**：通过网络挂载根文件系统
- **13.1.2 Live CD**：创建可引导的 Live CD

**13.2 Chroot**：使用 `make target-finalize` 后的 target 目录进行 chroot

---

## 第三部分 开发人员指南

### 14 Buildroot 如何工作

Buildroot 基本上是一组 Makefile 文件，可以使用正确的选项来对所需软件进行下载、配置和编译。它还包含各种软件包的补丁——主要是那些涉及交叉编译工具链（gcc、binutils 和 uClibc）的软件包。每个软件包基本上只有一个 Makefile 文件，它们以 `.mk` 扩展名命名。

**目录结构**：
- `toolchain/` — 包含与交叉编译工具链相关的所有软件的 Makefile 和相关文件：binutils、gcc、gdb、kernel-header 和 uClibc
- `arch/` — 包含 Buildroot 支持的所有处理器体系架构的定义
- `package/` — 包含所有用户空间工具和库的 Makefile 和相关文件，每个软件包都有一个子目录
- `linux/` — 包含 Linux 内核的 Makefile 和相关文件
- `boot/` — 包含 Buildroot 支持的 Bootloader 的 Makefile 和相关文件
- `system/` — 包含对系统集成的支持，例如目标文件系统框架 skeleton 和 init 系统的选择
- `fs/` — 包含与生成目标根文件系统镜像有关的软件的 Makefile 和相关文件

每个目录至少包含 2 个文件：
- `something.mk` — 用于下载、配置、编译和安装软件包 something 的 Makefile
- `Config.in` — 配置工具描述文件的一部分，描述与软件包有关的选项

**主 Makefile 执行步骤**（一旦配置完成）：
1. 创建所有输出目录：staging、target、build 等（默认在 `output/` 目录中，可以使用 `O=` 来指定另一个路径）
2. 生成工具链目标。当使用内部工具链时，这意味着将生成交叉编译工具链；当使用外部工具链时，这意味着将检查外部工具链的功能并将其导入到 Buildroot 环境
3. 生成 `TARGETS` 变量中列出的所有目标。该变量由所有单个组件的 Makefile 填充。生成这些目标将触发用户空间软件包（库、程序集）、内核、引导加载程序的编译以及根文件系统镜像的生成，具体取决于配置

### 15 编码风格

**15.1 Config.in 文件**：
- 缩进使用 Tab
- config 条目按字母顺序排列
- help 文本缩进一个 Tab 加一个空格

**15.2 .mk 文件**：
- 变量名使用大写和下划线
- 使用统一的包基础设施宏
- 依赖项按字母顺序排列

**15.3 documentation 文档**：使用 AsciiDoc 格式

**15.4 支持脚本**：位于 support/ 目录

### 16 添加对特定硬件板的支持

Buildroot 包含了一些公开可用的硬件板的基本配置，欢迎您为 Buildroot 添加对其他硬件板的支持。

**创建 defconfig 文件的步骤**：
1. 创建一个常规的 Buildroot 配置来为硬件建立一个基本系统：（内部）工具链、内核、引导加载程序、文件系统和一个简单的只有 BusyBox 的用户空间。不应选择特定的软件包：配置应尽可能少
2. 运行 `make savedefconfig`，这将在 Buildroot 根目录下生成一个最小的 defconfig 文件
3. 将此文件移动到 `configs/` 目录中，并将其重命名为 `<boardname>_defconfig`
4. 如果配置有些复杂，则最好手动将它重新格式化并分成几个部分，且在每部分前面添加对应的注释。典型部分是 Architecture、Toolchain options（通常只是 linux header 版本）、Firmware、Bootloader、Kernel 和 Filesystem

**版本控制要求**：
- 对于不同的组件，请始终使用固定的版本或 commit 哈希值，而不是 "latest" 版本
- 例如，设置 `BR2_LINUX_KERNEL_CUSTOM_VERSION=y` 和设置 `BR2_LINUX_KERNEL_CUSTOM_VERSION_VALUE` 为您所测试的内核版本
- 建议尽量使用 Linux 内核和 bootloader 的上游版本，并尽量使用内核和 bootloader 的默认配置

**板级目录结构**：
- 创建目录 `board/<manufacturer>` 和子目录 `board/<manufacturer>/<boardname>`
- 在这些目录中存储补丁程序和配置，并从 Buildroot 主配置中引用它们
- 可选择使用 br2-external 机制将板级配置保留在 Buildroot 源码树之外

### 17 向 Buildroot 添加新软件包

**17.1 软件包目录**：位于 `package/<package-name>/`

**17.2 配置文件**：

**17.2.1 Config.in 文件**：定义软件包在 menuconfig 中的条目
- `config BR2_PACKAGE_FOO` — 包名
- `bool "foo"` — 显示名称
- `default y` — 默认值
- `depends on` — 依赖条件（反向依赖）
- `select` — 自动选择依赖（正向依赖）
- `help` — 帮助文本

**17.2.2 Config.in.host 文件**：定义宿主机软件包

**17.2.3 选择 depends on 或 select**：
- `depends on`：当依赖不满足时隐藏选项
- `select`：自动强制启用依赖
- `comment`：显示提示信息但不可选择

**17.2.4 对目标和工具链选项的依赖**：如 `depends on BR2_USE_WCHAR`

**17.2.5 对 Linux 内核的依赖**：`depends on BR2_LINUX_KERNEL`

**17.2.6 对 udev 的依赖**：`depends on BR2_ROOTFS_DEVICE_CREATION_DYNAMIC_EUDEV`

**17.2.7 对 virtual 软件包的依赖**：选择特定 provider

**17.3 .mk 文件**：定义软件包的构建逻辑

**17.4 .hash 文件**：存储源码的哈希值用于校验

**17.5 具有特定构建系统的软件包的基础结构**（generic-package）：

**17.5.1 tutorial**：基本步骤
- 定义 `FOO_VERSION`、`FOO_SITE`、`FOO_LICENSE` 等
- 可选：`FOO_DEPENDENCIES`、`FOO_CONF_OPTS`、`FOO_INSTALL_TARGET_OPTS`

**17.5.2 reference**：完整的变量参考
- 下载相关：`FOO_SITE`、`FOO_SITE_METHOD`（git/svn/wget/hg等）、`FOO_SOURCE`
- 版本相关：`FOO_VERSION`、`FOO_DL_VERSION`
- 许可证相关：`FOO_LICENSE`、`FOO_LICENSE_FILES`
- 依赖相关：`FOO_DEPENDENCIES`、`FOO_BUILD_DEPENDENCIES`
- 配置相关：`FOO_CONFIGURE_CMDS`、`FOO_CONF_OPTS`
- 编译相关：`FOO_BUILD_CMDS`、`FOO_BUILD_OPTS`
- 安装相关：`FOO_INSTALL_TARGET_CMDS`、`FOO_INSTALL_STAGING_CMDS`、`FOO_INSTALL_HOST_CMDS`
- 其他：`FOO_POST_INSTALL_TARGET_HOOKS`、`FOO_ALLOW_EMPTY_DEPENDENCIES`

**17.6 基于 autotools 的软件包**：继承 generic-package，自动处理 ./configure/make/make install

17.6.1 tutorial 示例：
```makefile
LIBFOO_VERSION = 1.0
LIBFOO_SOURCE = LIBFOO-$(LIBFOO_VERSION).tar.gz
LIBFOO_SITE = http://www.foosoftware.org/download
LIBFOO_INSTALL_STAGING = YES
LIBFOO_INSTALL_TARGET = NO
LIBFOO_CONF_OPTS = --disable-shared
LIBFOO_DEPENDENCIES = libglib2 host-pkgconf

$(eval $(autotools-package))
```

17.6.2 autotools 特有变量：
- `LIBFOO_SUBDIR` — 指定包含软件包配置脚本的子目录名称
- `LIBFOO_CONF_ENV` — 指定传递给配置脚本的其他环境变量
- `LIBFOO_CONF_OPTS` — 指定传递给配置脚本的其他配置选项
- `LIBFOO_MAKE` — 指定备用 make 命令，不支持并行构建时设置为 `$(MAKE1)`
- `LIBFOO_MAKE_ENV` — 指定在构建步骤中传递给 make 命令的其他环境变量
- `LIBFOO_MAKE_OPTS` — 指定在构建步骤中传递给 make 命令的其他变量
- `LIBFOO_AUTORECONF` — 是否自动重新配置软件包（YES/NO），默认 NO
- `LIBFOO_AUTORECONF_ENV` — 传递给 autoreconf 程序的其他环境变量
- `LIBFOO_AUTORECONF_OPTS` — 传递给 autoreconf 程序的其他配置选项
- `LIBFOO_GETTEXTIZE` — 是否对该软件包进行 gettext 化（YES/NO），仅在 AUTORECONF=YES 时有效
- `LIBFOO_LIBTOOL_PATCH` — 是否应用可修复 libtool 交叉编译问题的 Buildroot 补丁程序（YES/NO），默认 YES
- `LIBFOO_INSTALL_STAGING_OPTS` — 安装到 staging 目录的 make 选项，默认 `DESTDIR=$(STAGING_DIR) install`
- `LIBFOO_INSTALL_TARGET_OPTS` — 安装到 target 目录的 make 选项，默认 `DESTDIR=$(TARGET_DIR) install`

**17.7 基于 CMake 的软件包**：继承 generic-package，使用 cmake 构建系统

17.7.1 tutorial 示例：
```makefile
LIBFOO_VERSION = 1.0
LIBFOO_SOURCE = LIBFOO-$(LIBFOO_VERSION).tar.gz
LIBFOO_SITE = http://www.foosoftware.org/download
LIBFOO_INSTALL_STAGING = YES
LIBFOO_INSTALL_TARGET = NO
LIBFOO_CONF_OPTS = -DBUILD_DEMOS=ON
LIBFOO_DEPENDENCIES = libglib2 host-pkgconf

$(eval $(cmake-package))
```

17.7.2 cmake 特有变量：
- `LIBFOO_SUBDIR` — 指定包含软件包主 CMakeLists.txt 文件的子目录名称
- `LIBFOO_CONF_ENV` — 指定传递给 CMake 的其他环境变量
- `LIBFOO_CONF_OPTS` — 指定传递给 CMake 的其他配置选项
- `LIBFOO_SUPPORTS_IN_SOURCE_BUILD` — 当软件包无法在源码目录树中构建时设置为 NO
- `LIBFOO_MAKE` — 指定备用 make 命令，不支持并行构建时设置为 `$(MAKE1)`
- `LIBFOO_MAKE_ENV` — 指定在构建步骤中传递给 make 命令的其他环境变量
- `LIBFOO_MAKE_OPTS` — 指定在构建步骤中传递给 make 命令的其他变量
- `LIBFOO_INSTALL_STAGING_OPTS` — 安装到 staging 目录的 make 选项，默认 `DESTDIR=$(STAGING_DIR) install`
- `LIBFOO_INSTALL_TARGET_OPTS` — 安装到 target 目录的 make 选项，默认 `DESTDIR=$(TARGET_DIR) install`

cmake-package 基础结构自动设置的常见 CMake 选项（通常无需手动设置）：
- `CMAKE_BUILD_TYPE` — 由 `BR2_ENABLE_DEBUG` 驱动
- `CMAKE_INSTALL_PREFIX` — 自动设置
- `BUILD_SHARED_LIBS` — 由 `BR2_STATIC_LIBS` 驱动
- `BUILD_DOC`、`BUILD_DOCS` — 已禁用
- `BUILD_EXAMPLE`、`BUILD_EXAMPLES` — 已禁用
- `BUILD_TEST`、`BUILD_TESTS`、`BUILD_TESTING` — 已禁用

**17.8 Python 软件包**：
- 支持 distutils 和 setuptools
- `utils/scanpypi` 工具从 PyPI 自动生成包
- 支持 CFFI 后端

**17.9 基于 LuaRocks 的软件包**

**17.10 Perl/CPAN 软件包**

**17.11 virtual 软件包**：定义可替换的 API 兼容实现（如不同的 JPEG 库）

**17.12 使用 kconfig 作为配置文件的软件包**

**17.13 基于 rebar 的软件包**（Erlang）

**17.14 基于 Waf 的软件包**

**17.15 基于 Meson 的软件包**

**17.16 集成基于 Cargo 的软件包**（Rust）

**17.17 Go 软件包**

**17.18 可构建内核模块的软件包**

**17.19 asciidoc 文档的基础结构**

**17.20 Linux 内核软件包特定的基础结构**：
- **17.20.1 linux 内核工具**：内核镜像类型、设备树、内核模块安装
- **17.20.2 linux 内核扩展**：通过 `linux/` 目录添加内核扩展

**17.21 各个构建步骤中可用的 Hook 钩子变量**：
- `POST_RSYNC hook`：rsync 后执行
- `Target-finalize hook`：目标文件系统最终化时执行

**17.22 Gettext 和其他软件包的集成与交互**

**17.23 提示和技巧**：
- 软件包名称、配置条目名称和 makefile 变量的对应关系
- 使用 `check-package` 检查编码风格
- 使用 `runtime-testing` 框架测试软件包
- 添加从 GitHub 获取的软件包

### 18 软件包应用补丁

**18.1 提供补丁**：
- **18.1.1 已下载的补丁**：在 `FOO_PATCH` 中指定
- **18.1.2 在 Buildroot 中的补丁**：放在 `package/<pkg>/` 目录下
- **18.1.3 全局补丁目录**：通过 `BR2_GLOBAL_PATCH_DIR` 指定

**18.2 如何应用补丁**：Buildroot 按顺序应用 `.patch` 文件

**18.3 软件包补丁的格式和许可**：需包含有效的 commit message 和 Signed-off-by

**18.4 集成在 Web 上找到的补丁**：需添加适当的 commit message

### 19 下载基础结构

**下载方法**（`FOO_SITE_METHOD`）：
- `wget` — 用于压缩包的常规 FTP/HTTP 下载，当 `FOO_SITE` 以 `http://`、`https://` 或 `ftp://` 开头时默认使用
- `scp` — 使用 scp 通过 SSH 方式下载压缩包，当 `FOO_SITE` 以 `scp://` 开头时默认使用，URL 格式为 `scp://[user@]host:filepath`
- `svn` — 用于从 Subversion 仓库下载
- `git` — 用于从 Git 仓库下载
- `hg` — 用于从 Mercurial 仓库下载
- `bazaar` — 用于从 Bazaar 仓库下载
- `cvs` — 用于从 CVS 仓库下载
- `file` — 用于本地文件系统路径

**关键变量**：
- `BR2_DL_DIR` — 设置下载目录，默认为 `dl/`
- `FOO_SITE` — 指定软件包源码的下载位置，支持 HTTP/FTP URL、Git/SVN 仓库 URL、本地文件系统路径
- `FOO_SITE_METHOD` — 显式指定下载方法（通常可由 URL 自动推断）
- `FOO_DL_OPTS` — 以空格分隔的传递给下载器的其他选项列表
- `FOO_EXTRA_DOWNLOADS` — 以空格分隔的 Buildroot 应下载的其他文件列表

**镜像站点支持**：
- `BR2_PRIMARY_SITE` — 指定主镜像站点 URL，Buildroot 会优先从该站点下载
- `BR2_BACKUP_SITE` — 指定备用镜像站点 URL，当主站点不可用时使用
- 支持本地文件系统镜像，可用于离线构建

### 20 调试 Buildroot

**基本调试方法**：
- `make V=1` — 显示所有执行的命令
- `make V=2` — 显示更多调试信息
- 检查 `output/build/<pkg>/.stamp_*` 文件了解构建进度
- 查看 `output/build/<pkg>/build.log` 获取构建日志

**构建步骤检测**（`BR2_INSTRUMENTATION_SCRIPTS`）：

定义 `BR2_INSTRUMENTATION_SCRIPTS` 变量，指定您想要在每个步骤之前和之后调用的一个或多个脚本（或其他可执行文件）的路径，以空格分隔。这些脚本按顺序调用，带有三个参数：
- `start` 或 `end`，表示步骤的开始或结束
- 即将开始或刚刚结束的步骤的名称
- 软件包的名称

使用方式：
```bash
make BR2_INSTRUMENTATION_SCRIPTS="/path/to/my/script1 /path/to/my/script2"
```

**可检测的步骤列表**：
- `extract` — 解压
- `patch` — 打补丁
- `configure` — 配置
- `build` — 编译
- `install-host` — 安装到 host 目录
- `install-target` — 安装到 target 目录
- `install-staging` — 安装到 staging 目录
- `install-image` — 安装到 binaries 目录

**脚本可访问的环境变量**：
- `BR2_CONFIG` — Buildroot .config 文件的路径
- `HOST_DIR`、`STAGING_DIR`、`TARGET_DIR` — 各输出目录路径
- `BUILD_DIR` — 软件包的提取和构建目录
- `BINARIES_DIR` — 所有二进制文件（镜像）的存储位置
- `BASE_DIR` — 基本输出目录

**构建时间分析**：
- `make graph-build` — 生成构建持续时间图（需 python-matplotlib 和 python-numpy）
- `BR2_GRAPH_OUT` — 图表输出格式（pdf/png）

### 21 为 Buildroot 做贡献

**21.1 复现、分析和修复错误**

**21.2 分析和修复自动构建失败**：http://autobuild.buildroot.net/

**21.3 审查和测试补丁**

**21.3.1 应用来自 Patchwork 的补丁**：`git-pw` 工具

**21.4 处理待办事项清单中的项目**

**21.5 提交补丁**：

**21.5.1 补丁格式**：
- 使用 `git format-patch` 生成
- 每个补丁一个逻辑变更
- commit message 格式：`<package>: <short description>`
- 必须包含 Signed-off-by

**21.5.2 准备补丁系列**：使用 `git send-email` 发送

**21.5.3 Cover letter**：描述补丁系列的整体目的

**21.5.4 补丁修订更改日志**：在 commit message 中记录修订历史

**21.6 报告 issues/bugs 或获取帮助**

**21.7 使用 run-tests 框架**：

Buildroot 包含一个运行时测试框架，称为 run-tests，它建立在 Python 脚本和 QEMU 运行时执行的基础上。该框架有两种类型的测试用例：一种用于构建时测试，另一种用于具有 QEMU 依赖性的运行时测试。

框架目标：
- 构建一个定义明确的配置
- 可选项，验证构建输出的某些属性
- 如果是运行时测试：在 QEMU 下启动，运行测试条件以验证功能是否正常运行

常用命令：
- `support/testing/run-tests -h` — 查看帮助和所有选项
- `support/testing/run-tests -l` — 列出所有测试用例
- 设置下载文件夹（`-d`）、输出文件夹（`-o`）、保留构建输出（`-k`）、JLEVEL 等

运行测试用例示例：
```bash
# 列出所有测试
support/testing/run-tests -l

# 运行单个测试并保留输出（需加 sudo）
sudo support/testing/run-tests -d dl -o output_folder -k tests.init.test_busybox.TestInitSystemBusyboxRw
```

**21.7.1 创建测试用例**：

熟悉如何创建测试用例的最好方法是查看 `support/testing/tests/fs/` 和 `support/testing/tests/init/` 的测试脚本。默认情况下，测试用例使用 br-arm-full-* uClibc-ng 工具链和 armv5/7 cpu 的预构建内核。

基本的测试用例定义涉及：
- 创建一个新的测试文件
- 定义唯一的测试类别
- 确定是否可以使用默认的 defconfig plus 测试选项
- 实现 `def test_run(self):` 函数，可选性启动模拟器并提供测试用例条件

额外步骤：
- 将自己添加到 DEVELOPERS 文件中以维护该测试用例
- 通过执行 `make .gitlab-ci.yml` 来更新 Gitlab CI yml

**21.7.2 调试测试用例**：

测试框架由 `support/testing/` 顶层中的 conf、infra 和 tests 文件夹组成。所有测试用例都位于 tests 文件夹下，由不同的文件夹组织，代表不同的测试类别。

调试步骤：
1. 使用 `-d`（dl 文件夹）、`-o`（输出文件夹）、`-k`（保留输出）参数运行测试
2. 成功构建后，output_folder 将包含一个 `<test name>` 文件夹，其中包含 Buildroot 构建组件、构建日志和运行时日志
3. 如果构建失败，控制台将显示失败阶段（setup/build/run），可检查 build/run 日志
4. 运行时日志的前几行会捕获 QEMU 启动命令，允许进行增量测试而无需重新运行 run-tests

调试技巧：
```bash
# 查看构建和运行日志
ls output_folder/TestInitSystemBusyboxRw/
# TestInitSystemBusyboxRw-build.log
# TestInitSystemBusyboxRw-run.log

# 可直接修改 output_folder 中的源码，重新运行标准 make 目标，然后重新测试
# 这比添加补丁文件、删除输出目录重新开始更快
```

这些运行时测试由 Buildroot Gitlab CI 基础结构定期执行（参见 `.gitlab.yml`）。

### 22 DEVELOPERS 文件和 get-developers

Buildroot 主目录中包含一个名为 `DEVELOPERS` 的文件，该文件列出了涉及 Buildroot 不同领域的开发人员。

**DEVELOPERS 文件的用途**：
- 通过分析补丁并将修改后的文件与相关的开发人员进行匹配，计算出应向其发送补丁的开发人员列表
- 查找哪些开发人员正在处理给定的体系架构或软件包，以便在此体系架构或软件包发生构建失败时可以通知他们（通过与 Buildroot 的 autobuild 基础结构交互）

**要求**：开发人员在向 Buildroot 添加新的软件包、新的板子或者新的功能时，应将自身注册到 DEVELOPERS 文件中，并在补丁中包含对 DEVELOPERS 文件的适当修改。

**`utils/get-developers` 工具用法**：
- `utils/get-developers <patch1> <patch2>...` — 传递一个或几个补丁作为命令行参数时，返回适当的 `git send-email` 命令
- `utils/get-developers -e <patch>` — 仅以适合 `git send-email --cc-cmd` 的格式打印电子邮件地址
- `utils/get-developers -a <arch>` — 返回负责给定体系架构的开发人员列表
- `utils/get-developers -p <package>` — 返回负责给定软件包的开发人员列表
- `utils/get-developers -c` — 查看 Buildroot 存储库中版本控制下的所有文件，列出未被任何开发人员处理的文件（用于帮助完成 DEVELOPERS 文件）
- `utils/get-developers`（不带参数）— 验证 DEVELOPERS 文件的完整性，并为不匹配的项目提示警告

### 23 发布工程

**23.1 发布**：

Buildroot 项目按季度发布，每月发布错误修复版本（bugfix releases）。每年的第一个版本是长期支持版本（LTS）。

- **季度发布版本**：2020.02、2020.05、2020.08、2020.11
- **错误修复版本**：2020.02.1、2020.02.2、…
- **LTS 版本**：2020.02、2021.02、…

**版本支持策略**：
- 发布版本受支持，直到下一个版本的第一个错误修复版本发布。例如，当 2020.08.1 发布时，2020.05.x 即为 EOL
- LTS 版本受支持，直到下一个 LTS 版本的第一个错误修复版本发布。例如，2020.02.x 版本受支持，直到 2021.02.1 版本发布

**23.2 开发周期**：

每个发布周期由以下阶段组成：
1. **开发阶段**（2 个月）：在 master 主分支上进行新功能开发
2. **稳定化阶段**（1 个月）：在发布之前进行，不会将任何新功能添加到 master 分支中，仅会修复错误

**RC（Release Candidate）流程**：
- 稳定化阶段从标记 `rc1` 开始
- 每周都会对另一个候选发布版本进行标记，直到发布为止
- 例如：2020.08-rc1、2020.08-rc2、…、2020.08

**next 分支机制**：
- 为了在稳定化阶段处理新功能和版本变更，可以为这些功能创建一个 `next` 分支
- 在当前版本发布后，`next` 分支会合并到 master 主分支中，并在那里继续下一个版本的开发周期

---

## 第四部分 附录

### 24 Makedev 语法文档

设备表文件格式（用于静态设备文件创建）：
```
# 格式：<name> <type> <mode> <uid> <gid> <major> <minor> <start> <inc> <count>
# 例：null    c    666  0     0     1       3
```

### 25 Makeusers 语法文档

用户表文件格式（用于创建自定义用户帐户）：
```
# 格式：<username> <uid> <group> <gid> <password> <home> <shell> <groups> <comment>
# 例：myuser -1 mygroup -1 =mypassword /home/myuser /bin/sh mygroup My User
```

### 26 从较早的 Buildroot 版本迁移

**26.1 迁移至 2016.11**：br2-external 目录树格式变更，需转换

**26.2 迁移至 2017.08**：部分配置选项名称变更

---

## 关键命令速查

| 命令 | 说明 |
|------|------|
| `make menuconfig` | 打开配置界面 |
| `make` | 构建整个系统 |
| `make clean` | 清理构建产物 |
| `make distclean` | 清理所有产物和配置 |
| `make savedefconfig` | 保存精简配置 |
| `make sdk` | 生成 SDK 压缩包 |
| `make source` | 仅下载源码（离线构建准备） |
| `make <pkg>` | 构建指定软件包 |
| `make <pkg>-dirclean` | 删除软件包构建目录 |
| `make <pkg>-rebuild` | 重新编译软件包 |
| `make <pkg>-reconfigure` | 重新配置并编译软件包 |
| `make graph-depends` | 生成依赖关系图 |
| `make graph-build` | 生成构建时间图 |
| `make graph-size` | 生成文件系统大小图 |
| `make legal-info` | 生成法律信息 |
| `make list-defconfigs` | 列出所有 defconfig |
| `make help` | 显示所有可用目标 |
| `make busybox-menuconfig` | 配置 BusyBox |
| `make linux-menuconfig` | 配置 Linux 内核 |
| `make uclibc-menuconfig` | 配置 uClibc |
| `make uboot-menuconfig` | 配置 U-Boot |

## 相关页面

- Buildroot 构建系统 — Buildroot 实操指南
- 交叉编译工具链 — 工具链原理与使用
- 根文件系统 — rootfs 结构与定制
- U-Boot 引导加载程序 — bootloader 配置与使用
- Linux 内核配置 — 内核编译与配置
