---
title: STM32MP1 嵌入式 Linux 驱动开发指南
source: STM32MP1嵌入式Linux驱动开发指南V2.1.pdf
type: source
tags: [linux, driver, device-tree, stm32mp1, gpio, platform, interrupt, i2c, spi, uart, pwm, lcd, input, usb, can, wifi, 4g, adc, dac, iio, regmap]
created: 2026-05-24
---

# STM32MP1 嵌入式 Linux 驱动开发指南

正点原子出品，基于 STM32MP157 开发板，共 1549 页、59 章。涵盖从 Ubuntu 环境搭建到完整 Linux 驱动开发的全流程。本文档按三大篇逐章提取关键知识点。

---

## 第一篇：Ubuntu 系统入门篇（第 1-2 章）

### 第一章 Ubuntu 系统安装

- **VMware 安装**：下载 VMware Workstation Pro，创建虚拟机时选择 Ubuntu 64 位，分配至少 2 核 CPU + 4GB 内存 + 40GB 硬盘
- **Ubuntu 安装**：使用 Ubuntu 18.04/20.04 LTS 镜像，分区方案为 ext4 + swap
- **VMware Tools 安装**：实现主机与虚拟机之间的文件拖拽、剪贴板共享、自适应分辨率

### 第二章 Ubuntu 系统操作

- **基本操作**：系统设置、关机重启、网络配置（NAT/桥接模式）
- **终端操作**：常用命令（ls, cd, cp, mv, rm, mkdir, chmod, chown）
- **Shell 编程**：Shell 脚本语法、变量、条件判断、循环、函数
- **APT 包管理**：`apt-get install/update/remove`，软件源配置
- **文本编辑器**：Gedit 和 Vi/Vim 的使用，Vim 的三种模式（命令/输入/底行模式）
- **Linux 文件系统**：目录结构（/bin, /etc, /home, /usr, /var 等）、文件权限（rwx）、用户管理
- **进程管理**：`ps`, `top`, `kill`, `&`, `nohup`, `jobs`, `fg`, `bg`

---

## 第二篇：系统移植篇（第 3-19 章）

### 第三章 Linux C 编程基础

- **Hello World**：编写、编译、运行 C 程序的基本流程
- **GCC 编译器**：`gcc` 命令选项（-o, -c, -I, -L, -l, -Wall, -O2）
- **Makefile 基础**：规则格式 `target: prerequisites`，自动变量（$@, $<, $^），模式规则（%.o: %.c），伪目标（.PHONY），条件判断，函数（wildcard, patsubst, foreach）

### 第四章 开发环境搭建

- **文件互传**：Ubuntu 与 Windows 之间的文件共享（Samba/FTP/SSH）
- **NFS 和 SSH 服务**：NFS 用于网络文件系统挂载，SSH 用于远程登录
- **交叉编译工具链**：安装 `arm-linux-gnueabihf-gcc`，验证版本 `arm-linux-gnueabihf-gcc -v`
- **VSCode 安装**：安装 Remote-SSH、C/C++、Cortex-Debug 等插件
- **CH340 驱动**：USB 转串口驱动安装，用于串口调试
- **MobaXterm**：SSH 终端工具，支持文件传输、多标签、X11 转发
- **ST 官方工具**：STM32CubeMX（引脚配置/时钟树/设备树生成）、STM32CubeIDE（集成开发环境）、STM32CubeProgrammer（烧录工具）
- **USB DFU 和 STLink 驱动**：Windows 和 Ubuntu 下的烧录工具驱动安装

### 第五章 STM32MP1 启动详解

- **启动模式**：STM32MP1 支持多种启动模式（USB/SD/eMMC/NAND），通过 BOOT 引脚选择
- **启动流程**：ROM -> TF-A (BL2) -> U-Boot (BL33) -> Linux Kernel
- **Flash 设备简介**：NAND Flash、eMMC、SD 卡的特性对比
- **启动镜像格式**：STM32MP1 使用 FIP (Firmware Image Package) 格式打包启动镜像

### 第六章 TF-A 使用

- **TF-A 简介**：Trusted Firmware-A，ARM 官方安全固件，负责安全启动链
- **源码获取**：从 ST 官方 GitHub 仓库获取 TF-A 源码并打补丁
- **编译烧录**：使用 `make` 编译 TF-A，通过 STM32CubeProgrammer 烧录到 eMMC/SD
- **stm32wrapper4dbg**：调试工具，用于在开发阶段快速烧录 TF-A

### 第七章 TF-A 初探

- **设备安全启动验证**：Secure Boot 流程，签名验证机制
- **TF-A 架构**：BL1 -> BL2 -> BL31 (EL3 Runtime) -> BL33 (U-Boot)
- **ARMv7/ARMv8 权限等级**：EL0 (用户态) -> EL1 (内核态) -> EL2 (Hypervisor) -> EL3 (Secure Monitor)
- **STM32MP1 中的 TF-A**：BL2 负责 DDR 初始化和安全验证，BL31 为 Secure Monitor

### 第八章 TF-A 编译详解

- **编译流程**：`make PLAT=stm32mp1` 编译命令解析
- **编译产物**：tf-a-stm32mp157c-dk2.stm32、fip.bin 等

### 第九章 TF-A 移植

- **移植目的**：将 ST 官方 TF-A 移植到正点原子开发板
- **关键修改**：设备树文件修改（DDR 配置、时钟配置、电源配置）
- **编译验证**：编译并烧录到开发板验证启动

### 第十章 U-Boot 使用

- **U-Boot 简介**：通用 Bootloader，负责加载 Linux 内核
- **U-Boot 命令**：`printenv`, `setenv`, `saveenv`, `bootm`, `tftp`, `nfs`, `mmc`, `ext4load` 等
- **内存操作**：`md`, `mw`, `cp` 命令读写内存
- **EMMC/SD 操作**：`mmc info`, `mmc read/write`, `mmc part` 等
- **网络操作**：`ping`, `tftpboot`, `nfs` 命令
- **Boot 命令**：`boot`, `bootd`, `run` 命令的使用

### 第十一章 U-Boot 顶层 Makefile 详解

- **U-Boot 目录结构**：arch/, board/, cmd/, common/, drivers/, include/, lib/, tools/ 等
- **Makefile 流程**：
  - `make xxx_defconfig`：加载板级默认配置
  - `make`：编译 U-Boot
- **关键变量**：VERSION, PATCHLEVEL, SUBLEVEL, EXTRAVERSION
- **MAKEFLAGS**：传递给子 make 的标志
- **编译规则**：scripts/Makefile.build 递归编译子目录
- **Kbuild 系统**：obj-y, obj-m, obj- 变量控制编译

### 第十二章 U-Boot 启动流程详解

- **链接脚本**：u-boot.lds 定义入口地址和段布局
- **启动流程**：
  - `reset` -> `lowlevel_init` -> `_main` -> `board_init_f` -> `relocate_code` -> `board_init_r` -> `run_main_loop`
- **board_init_f**：初始化串口、定时器、环境变量等
- **relocate_code**：将 U-Boot 重定位到 DDR 高地址
- **board_init_r**：初始化外设（MMC、网络、USB 等）
- **cli_loop**：命令行循环，解析并执行命令
- **bootm 启动 Linux**：`do_bootm` -> `do_bootm_linux` -> 跳转到内核

### 第十三章 U-Boot 移植

- **移植步骤**：
  1. 添加板级默认配置文件（defconfig）
  2. 添加板级设备树
  3. 修改电源配置（PMIC）
  4. 修改 TF-A 相关配置
  5. 编译并测试
- **bootcmd 和 bootargs**：
  - `bootcmd`：U-Boot 自动执行的命令序列
  - `bootargs`：传递给 Linux 内核的启动参数（root=/dev/mmcblkXpY rootfstype=ext4 console=ttySTM0,115200）

### 第十四章 U-Boot 图形化配置及其原理

- **Kconfig 语法**：`config`, `menuconfig`, `choice`, `depends on`, `select`, `default`, `help`
- **menuconfig 使用**：`make menuconfig` 图形化配置界面
- **配置流程**：Kconfig -> .config -> include/generated/autoconf.h

### 第十五章 Linux 内核顶层 Makefile 详解

- **内核目录结构**：arch/, drivers/, fs/, include/, init/, kernel/, lib/, mm/, net/, scripts/
- **编译流程**：`make xxx_defconfig` -> `make` -> `make zImage` / `make dtbs`
- **Kbuild 系统**：与 U-Boot 类似的 obj-y/obj-m 编译系统
- **built-in.o**：每个目录生成的中间目标文件，最终链接为 vmlinux

### 第十六章 Linux 内核启动流程详解

- **链接脚本**：vmlinux.lds 定义内核入口
- **启动流程**：
  - `stext` -> `__mmap_switched` -> `start_kernel` -> `rest_init` -> `init` 进程
- **start_kernel**：初始化调度器、内存管理、中断、定时器、控制台等核心子系统
- **rest_init**：创建 kernel_init 和 kthreadd 内核线程

### 第十七章 Linux 内核移植

- **内核源码获取**：从 ST 官方 GitHub 获取 Linux 5.4.31 源码并打补丁
- **添加开发板配置**：
  1. 添加默认配置文件（defconfig）
  2. 添加设备树文件（DTS）
  3. 关闭内核模块验证（CONFIG_MODULE_SIG=n）
  4. 关闭内核 log 时间戳（CONFIG_PRINTK_TIME=n）
- **编译测试**：`make uImage dtbs` 编译内核和设备树
- **系统镜像打包**：使用 STM32CubeProgrammer 打包并烧录到 eMMC

### 第十八章 Busybox 根文件系统构建

- **根文件系统概念**：Linux 内核启动后挂载的第一个文件系统，包含 /bin, /etc, /lib, /dev 等目录
- **BusyBox 构建**：编译 BusyBox 生成最小根文件系统
- **构建步骤**：
  1. 编译 BusyBox（`make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-`）
  2. 创建 lib 目录并拷贝交叉编译工具链的库文件
  3. 创建 /etc/init.d/rcS 启动脚本
  4. 创建 /etc/fstab 文件系统挂载表
  5. 创建 /etc/inittab 初始化配置
- **NFS 挂载**：通过 bootargs 设置 `root=/dev/nfs nfsroot=xxx ip=xxx`
- **功能测试**：字符设备测试、网络测试、硬件设备测试

### 第十九章 Buildroot 根文件系统构建

- **Buildroot 简介**：自动化构建根文件系统的工具，支持交叉编译、包管理
- **Buildroot 配置**：`make menuconfig` 配置交叉编译工具链、目标架构、软件包
- **BusyBox 配置**：在 Buildroot 中配置 BusyBox 选项
- **服务配置**：VSFTPD (FTP)、SSH 服务的配置和使用
- **系统功能配置**：depmod 生成模块依赖、vsftpd 配置、sshd 配置、DNS 配置
- **写入 eMMC**：将构建好的根文件系统打包并烧录到 eMMC

---

## 第三篇：ARM Linux 驱动开发篇（第 20-59 章）

### 第二十章 字符设备驱动开发

- **字符设备概念**：按字节流读写的设备（LED、按键、IIC、SPI、LCD 等）
- **应用程序调用流程**：`open()` -> 库函数 -> 系统调用 -> 内核驱动 `open()` -> 硬件操作
- **核心数据结构**：
  - `struct file_operations`：文件操作集（open, read, write, release, ioctl 等）
  - `struct file`：文件对象，包含 private_data 等
  - `struct inode`：索引节点，包含设备号
- **驱动编写步骤**：
  1. `module_init()` / `module_exit()` 注册模块加载/卸载函数
  2. `register_chrdev()` 注册字符设备（主设备号）
  3. 实现 `file_operations` 中的各个操作函数
  4. 创建设备节点：手动 `mknod` 或自动创建（class_create + device_create）
- **设备号**：`MKDEV(major, minor)`, `MAJOR(dev)`, `MINOR(dev)`
- **Chrdevbase 实例**：虚拟字符设备驱动的完整实现，包括驱动代码和测试 APP

### 第二十一章 嵌入式 Linux LED 驱动实验（裸机风格）

- **地址映射**：
  - `ioremap()`：将物理地址映射为虚拟地址
  - `iounmap()`：解除映射
- **I/O 内存访问函数**：`readl()`, `writel()`, `readb()`, `writeb()`
- **LED 驱动实现**：直接操作 GPIO 寄存器（MODER, OTYPER, OSPEEDR, PUPDR, BSRR）控制 LED
- **测试 APP**：通过 `open()`, `write()`, `read()`, `close()` 系统调用控制 LED

### 第二十二章 新字符设备驱动实验

- **新注册方式**：`cdev_init()`, `cdev_add()`, `cdev_del()`
- **自动创建设备节点**：
  - `class_create()` 创建设备类
  - `device_create()` 创建设备节点
  - `device_destroy()` 和 `class_destroy()` 销毁
- **文件操作私有数据**：`file->private_data` 存储设备私有数据
- **LED 驱动重构**：使用新字符设备框架重新实现 LED 驱动

### 第二十三章 Linux 设备树

- **设备树概念**：Device Tree，用树形结构描述板级硬件信息（CPU、内存、外设等）
- **DTS/DTB/DTC**：
  - `.dts`：设备树源文件
  - `.dtsi`：设备树头文件（可被 .dts 包含）
  - `.dtb`：编译后的二进制设备树文件
  - `dtc`：设备树编译器
- **DTS 语法**：
  - 节点格式：`label: node-name@unit-address { ... };`
  - 属性格式：`property = value;`
  - 标准属性：`compatible`, `status`, `#address-cells`, `#size-cells`, `reg`, `ranges`
  - `compatible` 属性：用于设备和驱动的匹配，格式 `"manufacturer,model"`
  - `status` 属性：`"okay"`, `"disable"`, `"reserved"`
- **节点引用与修改**：`&label` 引用节点，`/delete-node/` 删除节点，`/delete-property/` 删除属性
- **特殊节点**：`aliases`（别名）、`chosen`（启动参数）
- **OF 函数**：
  - 查找节点：`of_find_node_by_name()`, `of_find_node_by_path()`, `of_find_compatible_node()`
  - 查找父/子节点：`of_get_parent()`, `of_get_next_child()`
  - 读取属性值：`of_property_read_string()`, `of_property_read_u32()`, `of_property_read_u32_array()`
  - 获取 GPIO：`of_get_named_gpio()`

### 第二十四章 设备树下的 LED 驱动实验

- **设备树修改**：在 DTS 中添加 LED 节点，定义 `compatible`, `reg`（GPIO 寄存器地址）等属性
- **驱动实现**：通过 OF 函数从设备树获取 GPIO 信息，使用 `ioremap` 映射寄存器，操作 GPIO 控制 LED
- **测试流程**：编译设备树 -> 加载驱动 -> 运行测试 APP

### 第二十五章 pinctrl 和 gpio 子系统实验

- **pinctrl 子系统**：
  - 作用：管理引脚的复用功能、电气属性（上下拉、速度、驱动能力等）
  - STM32MP1 pinctrl 驱动：`drivers/pinctrl/stm32/pinctrl-stm32.c`
  - 设备树中 pinctrl 节点：定义引脚的默认状态（default）和睡眠状态（sleep）
  - pinctrl 属性：`pinctrl-names`, `pinctrl-0`, `pinctrl-1`
- **gpio 子系统**：
  - 作用：提供统一的 GPIO 操作 API，避免直接操作寄存器
  - 核心 API：
    - `gpio_request()`：申请 GPIO
    - `gpio_free()`：释放 GPIO
    - `gpio_direction_input()` / `gpio_direction_output()`：设置 GPIO 方向
    - `gpio_get_value()` / `gpio_set_value()`：读写 GPIO 值
  - 设备树 GPIO 属性：`gpios = <&gpioi 0 GPIO_ACTIVE_HIGH>;`
  - OF 函数：`of_get_named_gpio()` 从设备树获取 GPIO 编号

### 第二十六章 Linux 蜂鸣器驱动实验

- **蜂鸣器原理**：有源蜂鸣器（内置振荡电路，给电平即响）和无源蜂鸣器（需要 PWM 驱动）
- **驱动实现**：通过 pinctrl + gpio 子系统控制 GPIO 驱动蜂鸣器
- **测试 APP**：通过 write 系统调用控制蜂鸣器开/关

### 第二十七章 Linux 并发与竞争

- **并发概念**：多个执行单元同时访问共享资源
- **原子操作**：
  - 整型原子操作：`atomic_t`, `atomic_read()`, `atomic_set()`, `atomic_add()`, `atomic_sub()`, `atomic_inc()`, `atomic_dec()`
  - 位原子操作：`set_bit()`, `clear_bit()`, `change_bit()`, `test_bit()`
- **自旋锁**：`spinlock_t`, `spin_lock_init()`, `spin_lock()`, `spin_unlock()`
  - 适用于短时间持有、不能睡眠的场景
- **信号量**：`semaphore`, `sema_init()`, `down()`, `up()`
  - 可以睡眠，适用于长时间持有的场景
- **互斥体**：`mutex`, `mutex_init()`, `mutex_lock()`, `mutex_unlock()`
  - 推荐使用，比信号量更高效

### 第二十八章 Linux 并发与竞争实验

- **原子操作实验**：使用 `atomic_t` 保护 LED 驱动的打开/关闭状态
- **自旋锁实验**：使用 `spinlock_t` 保护共享数据
- **信号量实验**：使用 `semaphore` 实现资源互斥访问
- **互斥体实验**：使用 `mutex` 实现资源互斥访问

### 第二十九章 Linux 按键驱动实验

- **按键原理**：GPIO 输入模式，检测高低电平变化
- **驱动实现**：配置 GPIO 为输入模式，通过 `gpio_get_value()` 读取按键状态
- **测试 APP**：轮询方式读取按键状态

### 第三十章 Linux 内核定时器实验

- **内核时间概念**：节拍率（HZ）、jiffies 计数器
- **内核定时器**：
  - `struct timer_list`：定时器结构体
  - `timer_setup()`：初始化定时器
  - `add_timer()`：启动定时器
  - `mod_timer()`：修改定时器超时时间
  - `del_timer()` / `del_timer_sync()`：删除定时器
- **定时器实现**：周期性定时器实现 LED 闪烁

### 第三十一章 Linux 中断实验

- **中断 API**：
  - `request_irq()`：申请中断
  - `free_irq()`：释放中断
  - `enable_irq()` / `disable_irq()`：使能/禁用中断
- **中断处理函数**：`irqreturn_t (*irq_handler_t)(int irq, void *dev_id)`
- **中断标志**：`IRQF_SHARED`（共享中断）、`IRQF_TRIGGER_RISING`（上升沿触发）等
- **上半部与下半部**：
  - 上半部：中断处理函数，快速执行
  - 下半部：tasklet、工作队列、软中断
- **设备树中断信息**：`interrupt-parent`, `interrupts` 属性
- **获取中断号**：`irq_of_parse_and_map()`, `platform_get_irq()`

### 第三十二章 Linux 阻塞和非阻塞 IO 实验

- **阻塞 IO**：进程睡眠等待资源可用
  - `wait_event()` / `wait_event_interruptible()`：等待队列
  - `wake_up()` / `wake_up_interruptible()`：唤醒等待队列
- **非阻塞 IO**：立即返回，通过轮询或异步通知
- **poll 机制**：`poll()`, `select()`, `epoll()` 系统调用
  - `struct poll_table_struct`
  - `poll_wait()`：将等待队列加入 poll 表

### 第三十三章 异步通知实验

- **异步通知概念**：通过信号（SIGIO）通知应用程序数据就绪
- **实现步骤**：
  1. 应用程序注册信号处理函数 `signal(SIGIO, handler)`
  2. 应用程序设置文件所有者 `fcntl(fd, F_SETOWN, getpid())`
  3. 应用程序启用异步通知 `fcntl(fd, F_SETFL, FASYNC)`
  4. 驱动中 `kill_fasync()` 发送信号

### 第三十四章 platform 设备驱动实验

- **驱动分离与分层**：将设备信息和驱动逻辑分离，通过总线匹配
- **总线-设备-驱动模型**：
  - 总线（bus_type）：管理设备和驱动的匹配
  - 设备（device）：描述硬件信息
  - 驱动（device_driver）：实现驱动逻辑
- **platform 框架**：
  - `struct platform_device`：平台设备，描述硬件资源（内存、中断等）
  - `struct platform_driver`：平台驱动，实现 probe/remove 函数
  - 匹配方式：`name` 匹配、`id_table` 匹配、`of_match_table`（设备树）匹配
- **platform_driver 结构体**：
  ```c
  struct platform_driver {
      int (*probe)(struct platform_device *);
      int (*remove)(struct platform_device *);
      struct device_driver driver;
      const struct platform_device_id *id_table;
  };
  ```
- **资源获取**：`platform_get_resource()`, `platform_get_irq()`

### 第三十五章 设备树下的 platform 驱动编写

- **设备树下的 platform 驱动**：只需编写 `platform_driver`，设备信息从设备树获取
- **pinctrl-stm32.c 修改**：使 pinctrl 配置在 platform 框架下生效
- **设备树 GPIO 节点**：定义 pinctrl 和 GPIO 属性
- **probe 函数实现**：
  1. 获取设备树中的 GPIO 信息
  2. 申请 GPIO
  3. 设置 GPIO 方向
  4. 实现 file_operations
- **LED 驱动重构**：使用 platform 框架 + 设备树实现 LED 驱动

### 第三十六章 Linux 内置 LED 驱动实验

- **内核 LED 子系统**：`drivers/leds/leds-gpio.c`
- **gpio_led 驱动**：内核内置的 GPIO LED 驱动
- **设备树配置**：使用 `gpio-leds` 兼容性，定义 LED 节点
- **LED 触发器**：`default-on`, `heartbeat`, `timer` 等

### 第三十七章 Linux MISC 驱动实验

- **MISC 设备概念**：主设备号为 10 的杂项字符设备，简化字符设备驱动编写
- **miscdevice 结构体**：
  ```c
  struct miscdevice {
      int minor;              // 子设备号
      const char *name;       // 设备名字
      const struct file_operations *fops; // 设备操作集
  };
  ```
- **注册/注销**：`misc_register()`, `misc_deregister()`
- **蜂鸣器驱动**：使用 MISC 框架实现蜂鸣器驱动，嵌套在 platform 驱动中

### 第三十八章 Linux INPUT 子系统实验

- **INPUT 子系统**：统一处理输入设备（按键、触摸屏、鼠标、键盘等）
- **核心结构体**：
  - `struct input_dev`：输入设备
  - `struct input_event`：输入事件
- **驱动编写步骤**：
  1. `input_allocate_device()` 申请 input_dev
  2. 设置事件类型和事件码
  3. `input_register_device()` 注册
  4. `input_event()` 上报事件
  5. `input_unregister_device()` 注销
- **事件类型**：`EV_KEY`（按键）、`EV_REL`（相对坐标）、`EV_ABS`（绝对坐标）
- **按键驱动**：使用 INPUT 子系统实现按键驱动
- **内核自带按键驱动**：`drivers/input/keyboard/gpio_keys.c`

### 第三十九章 Linux PWM 驱动实验

- **PWM 概念**：脉冲宽度调制，通过调整占空比控制电机速度、LCD 背光等
- **STM32MP1 PWM**：由定时器产生（TIM1-TIM14），每个定时器支持多通道 PWM
- **设备树 PWM 节点**：定时器节点、PWM 子节点
- **PWM 子系统**：
  - `struct pwm_device`：PWM 设备
  - `struct pwm_state`：PWM 状态（周期、占空比、使能）
  - `pwm_config()`：配置 PWM 周期和占空比
  - `pwm_enable()` / `pwm_disable()`：使能/禁用 PWM
- **PWM 背光驱动**：使用 PWM 控制 LCD 背光亮度

### 第四十章 Linux LCD 驱动实验

- **LCD 与 LTDC**：STM32MP1 的 LTDC（LCD-TFT Display Controller）接口
- **DRM 框架**：Direct Rendering Manager，Linux 内核的显示子系统
- **ST 官方 DRM 驱动**：
  - `drivers/gpu/drm/stm/`：STM32 DRM 驱动
  - `drivers/gpu/drm/panel/`：LCD 面板驱动
- **LCD 驱动配置**：
  1. 修改设备树 LTDC 节点
  2. 在 `panel-simple.c` 中添加 LCD 面板参数
  3. 配置 LCD 面板时序参数（hactive, vactive, hsync, vsync 等）
- **测试**：LCD 显示测试、终端控制台配置

### 第四十一章 Linux I2C 驱动实验

- **I2C 简介**：两线制（SCL/SDA）串行通信协议，支持多从机
- **STM32MP1 I2C**：支持标准模式（100KHz）和快速模式（400KHz）
- **Linux I2C 框架**：
  - `struct i2c_adapter`：I2C 适配器（主机）
  - `struct i2c_client`：I2C 从设备
  - `struct i2c_driver`：I2C 驱动
  - `struct i2c_algorithm`：I2C 传输算法
- **I2C 驱动编写**：
  1. 设备树添加 I2C 设备节点
  2. 实现 `i2c_driver`（probe/remove）
  3. 使用 `i2c_transfer()` 或 `i2c_smbus_read/write_byte_data()` 读写数据
- **AP3216C 驱动**：光距离传感器，I2C 接口，驱动实现包括初始化、数据读取

### 第四十二章 RGB 转 HDMI 实验

- **RGB 转 HDMI 原理**：使用转换芯片（SiI9022A）将 RGB 信号转换为 HDMI 信号
- **设备树配置**：添加 SiI9022A 节点，配置 I2C 地址和 GPIO
- **内核驱动**：使用内核自带的 `sii902x` 驱动

### 第四十三章 Linux RTC 驱动实验

- **Linux 内核 RTC 框架**：
  - `struct rtc_device`：RTC 设备
  - `struct rtc_class_ops`：RTC 操作集（read_time, set_time, read_alarm 等）
- **STM32MP1 内部 RTC**：32 位计数器，支持闹钟、唤醒功能
- **RTC 使用**：`hwclock` 命令查看/设置硬件时钟

### 第四十四章 外部 RTC 芯片 PCF8563 实验

- **PCF8563 简介**：I2C 接口的 RTC 芯片，低功耗
- **寄存器说明**：秒、分、时、日、月、年、星期等寄存器
- **驱动实现**：I2C 驱动框架实现 PCF8563 驱动
- **设备树配置**：在 I2C 节点下添加 PCF8563 子节点

### 第四十五章 Linux SPI 驱动实验

- **SPI 简介**：高速全双工同步串行通信，4 线（SCK, MOSI, MISO, CS）
- **STM32MP1 SPI**：支持主/从模式，最大频率 108MHz
- **Linux SPI 框架**：
  - `struct spi_controller`：SPI 控制器
  - `struct spi_device`：SPI 从设备
  - `struct spi_driver`：SPI 驱动
  - `struct spi_transfer`：SPI 传输描述
  - `struct spi_message`：SPI 消息（包含多个 transfer）
- **SPI 驱动编写**：
  1. 设备树添加 SPI 设备节点
  2. 实现 `spi_driver`（probe/remove）
  3. 使用 `spi_sync()` / `spi_async()` 读写数据
- **ICM-20608 驱动**：6 轴传感器（3 轴陀螺仪 + 3 轴加速度计），SPI 接口

### 第四十六章 Linux RS232/485/GPS 驱动实验

- **Linux UART 框架**：
  - `struct uart_driver`：串口驱动
  - `struct uart_port`：串口端口
  - `struct uart_ops`：串口操作集
- **STM32MP1 UART**：8 个串口（4 个 USART + 4 个 UART）
- **设备树配置**：配置串口引脚、波特率、流控等
- **RS232 驱动**：使用 USART3，标准 DB9 接口
- **RS485 驱动**：使用 USART3 + MAX485 芯片，半双工通信
- **GPS 驱动**：使用 UART5，NMEA 协议解析
- **minicom 工具**：串口调试终端工具

### 第四十七章 触摸屏驱动实验

- **多点触摸协议**：MT (Multi-Touch) 协议
  - Type A：适用于触摸点跟踪困难的设备
  - Type B：适用于触摸点跟踪容易的设备（推荐使用）
- **事件上报**：`ABS_MT_POSITION_X`, `ABS_MT_POSITION_Y`, `ABS_MT_TRACKING_ID`
- **FT5426 驱动**：7 寸屏触摸 IC，I2C 接口
  - 设备树配置：添加 FT5426 节点
  - 驱动实现：I2C 驱动框架 + INPUT 子系统
- **GT9147 驱动**：4.3 寸屏触摸 IC，I2C 接口
- **tslib 库**：触摸屏校准和测试库

### 第四十八章 Linux 音频驱动实验

- **ALSA 框架**：Advanced Linux Sound Architecture
  - `struct snd_card`：声卡
  - `struct snd_pcm`：PCM 设备
  - `struct snd_pcm_ops`：PCM 操作集
- **WM8960 驱动**：I2S 接口音频编解码器
- **设备树配置**：I2S 节点、音频编解码器节点、音频路由

### 第四十九章 Linux CAN 驱动实验

- **CAN 简介**：控制器局域网络，用于汽车、工业控制
- **STM32MP1 CAN**：支持 CAN 2.0A/B 协议
- **Linux CAN 框架**：SocketCAN
  - `struct can_frame`：CAN 帧
  - `socket(PF_CAN, SOCK_RAW, CAN_RAW)`：创建 CAN 套接字
- **CAN 驱动配置**：设备树配置、波特率设置
- **测试工具**：`cansend`, `candump`, `can-utils`

### 第五十章 Linux USB 驱动实验

- **USB 协议基础**：
  - USB 描述符：设备描述符、配置描述符、接口描述符、端点描述符
  - USB 传输类型：控制传输、批量传输、中断传输、同步传输
  - USB 数据包：令牌包、数据包、握手包
- **Linux USB 框架**：
  - `struct usb_device`：USB 设备
  - `struct usb_driver`：USB 驱动
  - `struct urb`：USB 请求块
- **USB 设备驱动**：编写 USB 设备驱动，实现 probe/disconnect
- **USB gadget 驱动**：将 STM32MP1 作为 USB 设备（如 U 盘、串口）

### 第五十一章 Linux 块设备驱动实验

- **块设备概念**：以块为单位读写的设备（硬盘、eMMC、SD 卡等）
- **Linux 块设备框架**：
  - `struct gendisk`：通用磁盘
  - `struct block_device_operations`：块设备操作集
  - `struct request_queue`：请求队列
  - `struct request`：请求
- **块设备驱动编写**：
  1. `alloc_disk()` 分配 gendisk
  2. 设置 gendisk 属性（major, first_minor, fops, queue）
  3. `add_disk()` 添加磁盘
- **RAM 模拟块设备**：使用内存模拟块设备

### 第五十二章 Linux 网络设备驱动实验

- **网络设备概念**：以太网卡、WiFi 等网络接口
- **Linux 网络框架**：
  - `struct net_device`：网络设备
  - `struct net_device_ops`：网络设备操作集（ndo_open, ndo_stop, ndo_start_xmit 等）
  - `struct sk_buff`：套接字缓冲区
- **网络设备驱动编写**：
  1. `alloc_etherdev()` 分配 net_device
  2. 设置 net_device_ops
  3. `register_netdev()` 注册
- **数据收发**：`dev_queue_xmit()` 发送，`netif_rx()` 接收
- **DM9000 网卡驱动**：以太网控制器驱动实现

### 第五十三章 Linux WiFi 驱动实验

- **WiFi 模块**：正点原子开发板使用 RTL8723BU WiFi 模块
- **驱动编译**：交叉编译 WiFi 驱动模块
- **wpa_supplicant**：WiFi 连接管理工具
- **WiFi 配置**：`wpa_passphrase`, `wpa_supplicant`, `dhclient`

### 第五十四章 Linux 4G 通信实验

- **4G 模块**：ME3630 4G 模块，支持 ECM/PPP/RNDIS 等接口
- **ECM 模式**：以太网控制模型，将 4G 模块虚拟为网卡
- **PPP 模式**：点对点协议，通过串口建立网络连接
- **网络连接**：`ifconfig usb0 up`, `udhcpc -i usb0`

### 第五十五章 Regmap API 实验

- **Regmap 概念**：统一的寄存器访问抽象层，适用于 I2C、SPI、MMIO 等
- **regmap_config 结构体**：
  ```c
  struct regmap_config {
      reg_bits;       // 寄存器地址位数
      val_bits;       // 寄存器值位数
      max_register;   // 最大寄存器地址
  };
  ```
- **Regmap API**：
  - `regmap_init_i2c()` / `regmap_init_spi()`：初始化 regmap
  - `regmap_read()` / `regmap_write()`：读写寄存器
  - `regmap_update_bits()`：更新寄存器特定位
- **ICM-20608 重构**：使用 Regmap API 重写 ICM-20608 驱动

### 第五十六章 Linux IIO 子系统实验

- **IIO 概念**：Industrial I/O，用于 ADC、DAC、传感器等设备的统一框架
- **核心结构体**：
  - `struct iio_dev`：IIO 设备
  - `struct iio_info`：IIO 信息
  - `struct iio_chan_spec`：IIO 通道描述
- **IIO 驱动编写**：
  1. `iio_device_alloc()` 分配 IIO 设备
  2. 设置 IIO 信息和通道
  3. `iio_device_register()` 注册
- **ICM-20608 IIO 驱动**：使用 IIO 框架实现传感器驱动
- **IIO 读取工具**：`cat /sys/bus/iio/devices/iio:deviceX/in_accel_x_raw`

### 第五十七章 Linux ADC 驱动实验

- **STM32MP1 ADC**：16 位分辨率，支持多通道
- **IIO ADC 驱动**：使用 IIO 框架实现 ADC 驱动
- **设备树配置**：ADC 节点、通道配置
- **ADC 读取**：通过 IIO 接口读取 ADC 值

### 第五十八章 Linux DAC 驱动实验

- **STM32MP1 DAC**：12 位分辨率
- **IIO DAC 驱动**：使用 IIO 框架实现 DAC 驱动
- **DAC 输出**：通过 IIO 接口设置 DAC 输出值

### 第五十九章 Linux 硬件监测实验

- **硬件监测**：温度、电压、风扇转速等传感器监测
- **hwmon 框架**：`struct hwmon_channel_info`, `struct hwmon_ops`
- **温度传感器**：使用 IIO 框架读取温度值

---

## 关键概念总结

### 驱动开发框架层次

| 层次 | 说明 | 对应章节 |
|------|------|----------|
| 字符设备驱动 | 最基础的驱动框架 | 第 20-22 章 |
| platform 驱动 | 总线-设备-驱动模型 | 第 34-35 章 |
| I2C 驱动 | I2C 总线框架 | 第 41 章 |
| SPI 驱动 | SPI 总线框架 | 第 45 章 |
| INPUT 子系统 | 输入设备统一框架 | 第 38 章 |
| IIO 子系统 | 传感器/ADC/DAC 统一框架 | 第 56-58 章 |
| DRM 框架 | 显示子系统 | 第 40 章 |
| ALSA 框架 | 音频子系统 | 第 48 章 |

### 设备树关键属性

- `compatible`：设备和驱动匹配的关键，格式 `"manufacturer,model"`
- `reg`：寄存器地址和大小
- `status`：设备状态（okay/disable）
- `pinctrl-names` / `pinctrl-0`：引脚控制状态
- `interrupt-parent` / `interrupts`：中断配置
- `gpios`：GPIO 引脚配置

### 常用内核 API

- **内存映射**：`ioremap()`, `iounmap()`, `readl()`, `writel()`
- **GPIO**：`gpio_request()`, `gpio_direction_output()`, `gpio_set_value()`
- **中断**：`request_irq()`, `free_irq()`
- **定时器**：`timer_setup()`, `add_timer()`, `mod_timer()`
- **等待队列**：`wait_event()`, `wake_up()`
- **互斥**：`mutex_lock()`, `mutex_unlock()`
- **自旋锁**：`spin_lock()`, `spin_unlock()`

---

## 相关 wiki 页面

- #$MP157_Quick_Start — 开发板开箱与基础测试
- #$MP157_M4_CubeIDE_Guide — Cortex-M4 裸机开发
- #$MP157_M4_HAL_Guide — Cortex-M4 HAL 库开发
- [[#ComputerArchitecture_Basics|计算机体系结构基础]] — ARM 架构基础概念
- [[#EmbeddedC_BitManipulation|嵌入式 C 位操作]] — 寄存器位操作基础
