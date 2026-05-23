---
type: source
tags: [stm32mp157, getting-started, hardware, alientek]
---

# $ATK-DLMP157 快速上手指南

> 来源：正点原子 STM32MP157 快速体验 V1.8 + 开箱指南及维护 V1.1

---

## 第一部分：开箱指南及维护

### 1. 实物篇

#### 1.1 STM32MP157 开发板

- 采用核心板+底板搭配形式，核心板可单独购买，底板不能单独购买
- 在售核心板型号：STM32MP157-D，后续可能推出 STM32MP151、STM32MP157-A 及 MINI 版底板
- 核心板可从底板取下，一款底板可学习多款芯片
- 发货时配有亚克力板保护，起隔档灰尘、防金属误触短路作用
- 外观检查要点：检查元器件有无虚焊、脱落、错位，跳线帽是否缺少
- 注意：发货不配螺丝刀，需自行准备

#### 1.2 基本配件

- **电源适配器**：12V 直流，输入电压范围 DC6V-16V，建议使用正点原子配套适配器，不要使用别的适配器
- **杜邦线**：两条
- **USB Type-C 线**：两条，一条用于串口通信，一条用于烧写系统，支持正接反接

#### 1.3 其他套餐配件

**屏幕（RGB 接口）：**
- 4.3 寸 RGB 屏 800x480（推荐，适配出厂 Qt 界面）
- 4.3 寸 RGB 屏 480x272（可用但分辨率低，暂不推荐）
- 7 寸 RGB 屏 800x480
- 7 寸 RGB 屏 1024x600
- 10 寸 RGB 屏 1280x800
- 屏幕型号标记在屏幕背面，通过 M2/M1/M0 电阻焊接状态区分
- 不能使用 MCU 屏幕，使用其他品牌屏幕需注意线序

**ST-LINK 仿真器：**
- 用于学习 M4 内核（M4 没有 Flash，只能在线调试）
- JTAG 接口排针间距 2.0mm，需搭配 ST-LINK 转接板使用
- 推荐正点原子 ST-LINK 仿真器，其他仿真器不能完美适配

**TF 卡和读卡器：**
- 正点原子在售为闪迪 16G TF 卡（Micro SD 卡，非普通 SD 大卡）
- 需搭配读卡器或卡套使用，推荐 USB3.0 二合一读卡器
- 学习系统移植或 A7 裸机时会用到

**OV5640 摄像头模块：**
- 500 万像素，开发板已设计好接口，直接接入即可使用
- 出厂系统自带驱动

**4G 模组：**
- 型号：ME3630-C3B-MP01（不带 GPS）/ ME3630-C3C-MP01（带 GPS），均为全网通
- 出厂系统自带驱动和接口，直接接入模块和 SIM 卡后可测试

---

### 2. 启动篇

#### 2.1 软件设置

**安装串口终端软件 MobaXterm：**
- 安装包路径：开发板光盘 A-基础资料\3、软件\MobaXterm_Installer_v12.3.zip
- 解压后双击 MobaXterm_installer_12.3.msi 安装
- 安装完成后桌面生成 MobaXterm 图标
- 也可使用 SecureCRT、Putty 等其他串口终端软件

**安装 CH340 USB 串口驱动：**
- 驱动路径：开发板光盘 A-基础资料\3、软件\CH340 驱动(USB 串口驱动)_XP_WIN7 共用
- 双击 SETUP.EXE，点击安装即可

#### 2.2 硬件连接

1. **屏幕连接**：
   - FPC 排线连接屏幕与开发板，丝印"1"对"1"、"40"对"40"
   - 排座为夹子结构，用指甲轻挑黑色夹条中间打开，插入排线后扣下
   - 无数字丝印时参考小白点标记（表示丝印"1"）
   - 平时不要取下屏幕排线，防止金属片脱落或老化

2. **串口连接**：
   - 一条 USB Type-C 线连接开发板 USB_TTL 接口到电脑 USB 端口
   - MobaXterm 设置：串口类型，选择对应 COM 口，波特率 115200
   - 若识别多个 COM 口，可通过设备管理器查看，取下再插入 USB 线观察哪个 COM 口更新

3. **电源连接**：
   - 接上正点原子 12V 电源适配器
   - 即使 USB_TTL 已供电，接屏幕时仍需接电源适配器以保证供电稳定

#### 2.3 拨码开关

- 拨码开关有 3 个，开关拨到 ON 端表示 1，拨到数字端表示 0
- eMMC 启动模式：010（出厂系统烧录在 eMMC）
- 拨码开关具体含义在板子丝印上已标注

#### 2.4 启动开发板

- 接入电源后将开发板启动开关拨到 ON 模式
- 屏幕依次显示：正点原子 logo -> ST 官方 logo -> 初始化提示界面 -> Qt 桌面
- ST logo 后约有十秒黑屏（Qt 程序较大，系统服务多），请耐心等待
- 串口终端默认以 root 用户自动登录，无需密码
- 出厂文件系统由 Yocto 编译制作，启动时间较长

**HDMI 使用方法：**
- 用 HDMI 线连接开发板 HDMI 接口到显示器
- eMMC 启动后在 Uboot 倒计时结束前按数字键"2"选择 HDMI 设备树
- 板载 HDMI 最大支持 WXGA (1366x768) @60fps，出厂默认 1280x720 @60fps
- HDMI 与 RGB LCD 共用接口，理论上只能使用其中一种

---

### 3. 资料篇

#### 3.1 开发板资料目录

- 1、程序源码（出厂系统源码、Linux 驱动例程、M4 裸机/FreeRTOS 例程、ST 官方源码、BusyBox、Buildroot、模块驱动源码、Qt 综合例程）
- 2、开发板原理图
- 3、软件
- 4、参考资料
- 5、开发工具
- 6、硬件资料
- 7、STM32MP1 参考资料
- 8、系统镜像（教程系统镜像、出厂系统镜像、Weston 文件系统）

#### 3.2 教程资料

- STM32MP157 开箱指南及维护
- STM32MP1 嵌入式 Linux 驱动开发指南
- STM32MP157 开发板硬件参考手册
- STM32MP157 快速体验
- 嵌入式 Linux C 代码规范化
- STM32MP1 M4 裸机 CubeIDE 开发手册
- STM32MP157 文件传输及更新固件手册
- STM32MP1 M4 裸机 HAL 库开发手册

#### 3.3 视频资料

- 原子哥平台：https://www.yuanzige.com/
- 正点原子 B 站：https://space.bilibili.com/394620890

---

### 4. 售后篇

#### 4.1 实物硬件问题

**屏幕显示不正常排查顺序：**
1. 检查排线连接是否正确、核心板是否松动
2. 检查是否使用 12V 电源适配器供电
3. 检查拨码开关是否正确、拨动到位，可重新插拔核心板
4. 检查核心板运行的程序是否有屏幕驱动
5. 烧录出厂系统测试屏幕是否正常显示
6. 仍无法解决则联系淘宝售后或 QQ 群/论坛反馈

**开发板无法启动排查顺序：**
1. 确认硬件连接，是否使用原子电源适配器供电
2. 检查 ON/OFF 开关是否打开，拨码开关是否正确到位
3. 检查核心板电源灯和底板电源灯是否亮起
4. 检查拨码开关是否正确，eMMC/TF 卡中是否有正确系统
5. 仍无法解决则联系淘宝售后或 QQ 群/论坛反馈

**售后返修条款：**
- 收货 15 天内：产品问题负责一切费用包换保修
- 15 天至 1 个月：产品问题负责来回运费维修
- 1 至 3 个月：产品本身问题负责发过去的运费维修
- 3 个月以后：买家承担来回运费和芯片、液晶屏等费用，不收维修手续费

---

## 第二部分：快速体验

### 第一章 ATK-STM32MP157 硬件资源简介

#### 1.1 底板资源简介

- 提供 STM32MP157 底板和 STM32MP157-Mini 底板两种资源图
- 详细硬件信息参考《【正点原子】STM32MP157 开发板硬件参考手册 V1.x.pdf》

#### 1.2 核心底板资源简介

- 核心板资源图见文档图示
- 详细硬件信息参考《【正点原子】STM32MP157 开发板硬件参考手册 V1.x.pdf》

---

### 第二章 ATK-STM32MP157 烧写系统

#### 2.1 STM32CubeProgrammer 简介

- 跨平台：支持 Windows、macOS、Linux，运行需要 Java 环境
- 多合一：支持 USB、ST-LINK、UART、OTA 多种烧写方式
- 版本：文档使用 en.stm32cubeprog_v2-5-0

#### 2.2 下载 STM32CubeProgrammer

- 从 ST 官网 https://www.st.com/ 下载（需注册 ST 帐号）
- 或使用光盘路径：开发板光盘 A-基础资料->5、开发工具->2、ST 官方开发工具
- 解压后三个文件：MacOS 安装文件、Windows exe 文件、Linux 安装程序

#### 2.3 Windows 下烧写固件到开发板

**2.3.1 安装 STM32CubeProgrammer：**

1. 安装 Java 环境：
   - 需要 Java 1.8.0_66 - 10.99.99 版本
   - 下载地址：https://java.com/zh-CN/download/ 或光盘路径 3、软件->Java 安装包->jre-8u261-windows-x64.exe
   - 安装时不要修改默认安装路径（很多软件依赖 Java 到 C 盘找路径）
   - 下载时不要点击"同意并免费下载"，应点击查看所有 Java 下载

2. 安装 STM32CubeProgrammer：
   - 双击 SetupSTM32CubeProgrammer-2.5.0.exe
   - 基本都是点击下一步，默认安装选项
   - 安装期间弹出驱动安装选择"始终安装此驱动程序软件"

3. 安装 DFU 驱动程序：
   - 拨码为 000（USB 模式），USB Type-C 连接 USB_OTG 接口到电脑 USB 3.0 接口
   - Windows 7：需先卸载 DfuSe 驱动，再双击 STM32Bootloader.bat 安装 STM32_Programmer 驱动
   - Windows 10：自动识别，无需额外操作
   - 设备管理器中应显示"具有 STM32_Programmer 驱动程序的 STM32 DFU 器件"

**2.3.2 Windows 使用 STM32CubePro 烧写固件到 eMMC：**

1. 硬件连接：
   - 拨码开关 000（USB 模式）
   - USB Type-C 连接底板 USB_OTG 到电脑 USB 3.0 接口（不要用 USB 2.0，烧写很慢）
   - 另一条 USB Type-C 连接底板 USB_TTL（可选，观察打印信息）
   - 开发板上电

2. 烧写步骤：
   - 打开 STM32CubeProgrammer，设备类型选择 USB
   - 点击刷新设备，出现 USB1 表明成功（不成功可按 RESET 按钮）
   - 打开 tsv 配置文件：flashlayout/atk_emmc-stm32mp157d-atk-qt.tsv
   - 浏览固件目录：8、系统镜像->2、出厂系统镜像->1、STM32CubeProg 烧录固件包
   - 点击 Download 开始烧写
   - USB 3.0 烧写约 5-6 分钟，USB 2.0 约 40-60 分钟
   - 可跳过文件系统烧写：将 tsv 文件最后一行的"p"修改为"PE"
   - 烧写完成，拨码到 010（eMMC 启动）

**2.3.3 烧写固件到 SD(TF)卡：**
- 方法同上，选择 atk_sdcard-stm32mp157d-atk-qt.tsv 配置文件
- 烧写完成后拨码到 101（SD 卡启动）

#### 2.4 Linux 下烧写固件到开发板

**2.4.1 Linux 安装 STM32CubeProgrammer：**

1. 安装 Java：
   ```bash
   sudo apt-get install openjdk-8-jre
   ```

2. 安装 STM32CubeProgrammer：
   ```bash
   chmod +x SetupSTM32CubeProgrammer-2.5.0.linux
   sudo ./SetupSTM32CubeProgrammer-2.5.0.linux
   ```

3. 配置环境变量（编辑 /etc/profile）：
   ```bash
   export PATH=$PATH:/usr/local/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/
   source /etc/profile
   ```

4. 安装 Oracle JRE（ST 工具运行在 Oracle JRE 上，非 Open-JRE）：
   ```bash
   sudo tar xf jre-8u261-linux-x64.tar.gz -C /usr/lib/jvm/
   sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/jre1.8.0_261/bin/java 1000
   sudo update-alternatives --config java  # 选择手动安装的 JRE
   ```

5. 安装 libusb：
   ```bash
   sudo apt-get install libusb-1.0.0-dev
   ```

6. 拷贝 udev 规则：
   ```bash
   sudo cp /usr/local/STMicroelectronics/STM32Cube/STM32CubeProgrammer/Drivers/rules/*.* /etc/udev/rules.d/
   ```

7. 虚拟机设置 USB 兼容 USB 3.0

**2.4.1.1 Linux 烧写固件到 eMMC：**
- 操作步骤与 Windows 类似，选择 atk_emmc-stm32mp157d-atk-qt.tsv
- 烧写完成，拨码到 010（eMMC 启动）

**2.4.2 制作 TF(SD)卡系统启动卡：**

1. 拷贝 sdcard_update 文件夹到 Ubuntu
2. 使用读卡器插入 TF 卡，连接到 Ubuntu 虚拟机
3. 使用 fdisk 确认 TF 卡设备节点（如 /dev/sdb，注意不要选到 /dev/sda 硬盘）
4. 执行烧录脚本（会格式化整张 TF 卡）：
   ```bash
   chmod +x sdcard_update.sh
   sudo ./sdcard_update.sh /dev/sdb
   ```
5. 烧写约 3 分钟，完成后插到底板卡槽，拨码至 101 启动

**2.4.3 使用 TF(SD)卡启动烧写固件到 eMMC：**

1. 从 TF 卡启动系统（拨码 010，注意这里拨码应为 101 从 TF 卡启动）
2. 使用 scp 拷贝 emmc_update 文件夹到开发板：
   ```bash
   scp -r emmc_update/ root@192.168.1.149:/home/root
   ```
3. 在开发板上执行烧写：
   ```bash
   chmod +x emmc_update.sh
   ./emmc_update.sh /dev/mmcblk2
   ```

---

### 第三章 ATK-STM32MP157 开发板使用前准备

#### 3.1 上电前注意事项

- 必须插上电源适配器，仅 USB_TTL 供电可能导致 LCD/HDMI 无法显示、触摸失灵、4G 模块不工作
- 底板下放保护膜，不要放杂物台上，防止金属异物短路
- 注意防水、防潮、防尘

#### 3.2 串口软件安装

- CH340 USB 串口驱动：光盘路径 3、软件->CH340 驱动(USB 串口驱动)_XP_WIN7 共用->SETUP.EXE
- MobaXterm 终端：光盘路径 3、软件->MobaXterm_Installer_v12.3.zip

#### 3.3 拨码开关设置及登录开发板

| 启动模式 | 拨码值 | 说明 |
|---------|--------|------|
| MCU (Cortex M4) | 100 | |
| SD Card 启动 | 101 | |
| NOR 启动 | 101 | ATK-STM32MP157 无 NOR FLASH |
| eMMC 启动 | 010 | 出厂默认 |
| NAND 启动 | 011 | 不售 NAND FLASH 类型核心板 |
| USB/UART 模式 | 110/000 | |

- USB_TTL 为调试串口，波特率 115200
- MobaXterm 串口设置：串口类型，选择 COM 口，波特率 115200
- 串口终端默认以 root 用户自动登录，无需密码
- 出厂文件系统由 Yocto 编译，启动时间较长，Qt 界面启动还需几秒

---

### 第四章 ATK-STM32MP157 功能测试

#### 4.1 LED 测试、蜂鸣器测试

| 管脚名称 | PI0 | PF3 | PC7 |
|---------|-----|-----|-----|
| 功能 | LED0（心跳灯） | LED1（用户 LED） | BEEP（蜂鸣器） |

设备树路径：arch/arm/boot/dts/stm32mp157d-atk.dtsi

测试命令：
```bash
cat /sys/class/leds/sys-led/trigger           # 查看 LED0 触发方式
echo none > /sys/class/leds/sys-led/trigger    # 改变触发模式
echo 1 > /sys/class/leds/sys-led/brightness    # 点亮 LED0
echo 0 > /sys/class/leds/sys-led/brightness    # 熄灭 LED0
echo 1 > /sys/class/leds/beep/brightness       # 打开蜂鸣器
echo 0 > /sys/class/leds/beep/brightness       # 关闭蜂鸣器
echo heartbeat > /sys/class/leds/beep/trigger  # 蜂鸣器心跳模式
```

#### 4.2 按键测试

| 管脚名称 | PG3 | PH7 |
|---------|-----|-----|
| 功能 | KEY0 | KEY1 |

设备树路径：arch/arm/boot/dts/stm32mp157d-atk.dtsi

测试命令：
```bash
lsinput                    # 查看输入事件设备
od -x /dev/input/event1    # 查看按键输入信息（event1 为按键，event0 为触摸屏）
hexdump /dev/input/event1  # 另一种查看方式
```

#### 4.3 LCD 测试

正点原子 RGB 屏幕类型：

| 屏幕尺寸 | 触摸芯片 | 屏幕 ID |
|---------|---------|---------|
| 4.3 寸 (480x272) | gt9xx | 0x00 |
| 4.3 寸 (800x480) | gt9xx/gt1151 | 0x04 |
| 7 寸 (800x480) | ft5x06/cst340 | 0x01 |
| 7 寸 (1024x600) | ft5x06/cst340 | 0x02 |
| 10 寸 (1280x800) | gt9xx | 0x03 |

触摸驱动路径：drivers/input/touchscreen/

**触摸测试：**
```bash
systemctl stop atk-qtapp-start.service  # 停止 Qt 桌面服务
export TSLIB_CONSOLEDEVICE=none         # 设置终端控制台为 NULL
ts_test                                 # 单点触摸测试
ts_test_mt                              # 多点触摸测试
```

**背光测试：**
```bash
cat /sys/class/backlight/panel-backlight/max_brightness   # 查看最大亮度等级（8级，0~7）
cat /sys/class/backlight/panel-backlight/brightness       # 查看当前亮度等级
echo 4 > /sys/class/backlight/panel-backlight/brightness  # 修改亮度等级
```

#### 4.4 串口测试

| 串口类型 | 对应串口 | 设备名 |
|---------|---------|--------|
| com2(DB9 公头)/RS485 | usart3 | ttySTM1 |
| com1(DB9 母头) | uart5 | ttySTM2 |
| USB_TTL | uart4 | ttySTM0（调试串口） |

**DB9 公头(com2)测试：**
- 需要跳线帽切换 DB9 公头 com2 的 tx/rx 连接到 usart3 的 rx/tx
- 使用 USB 转 RS232 母头线连接开发板 com2
- 配置串口：`stty -F /dev/ttySTM1 ispeed 115200 ospeed 115200 cs8`
- 接收数据：`cat /dev/ttySTM1`

**DB9 母头(com1)测试：**
- 需要跳线帽切换 DB9 母头 com1 的 tx/rx 连接到 uart5 的 rx/tx
- 使用 USB 转 RS232 公头线连接开发板 com1
- 配置串口：`stty -F /dev/ttySTM2 ispeed 115200 ospeed 115200 cs8`

**RS485 串口测试：**
- 跳线帽切换连接 RS485 到 usart3
- RS485 的 A 连接转换器 A，B 连接 B

#### 4.5 USB 测试

**USB HOST 测试：**
- FAT32 格式 U 盘插入 USB_CN1/CN2/CN3 接口
- 自动挂载到 /run/media/sda1
- 读速度测试：`hdparm -t /dev/sda1`
- 写速度测试：`time dd if=/dev/zero of=/run/media/sda1/test bs=1024k count=100 conv=fdatasync`

**USB OTG 测试（OTG 网络）：**
- USB Type-C 连接 USB_OTG 到电脑
- 系统启动后生成 usb0 网络节点
- 在 Ubuntu 虚拟机中将 USB 设备连接到虚拟机
- 开发板与 Ubuntu 构成局域网，可进行网络通信

**USB 鼠标测试：**
- 出厂系统启动后插上鼠标，LCD/HDMI 屏幕会显示鼠标指针

#### 4.6 网络测试

- 核心板搭载千兆网络芯片，自适应 10/100/1000M
- 查看 IP：`ifconfig`
- 测试连通性：`ping www.baidu.com`
- 千兆网络测试：需千兆网线、千兆路由器/交换机、千兆网卡
- iperf3 测试：
  - Ubuntu 服务器：`iperf3 -s`
  - 开发板客户端：`iperf3 -c 192.168.1.11 -i 1`
  - 千兆网络 Bitrate 约 800 Mbits/sec

#### 4.7 CAN 测试

底板有一路 CAN，支持 CAN FD。主要特性：
- CAN FD 为 CAN 协议升级版，物理层未改变
- 数据比特率最高 5Mbps，理论最低 40kbps
- CANH 接仪器 CANH，CANL 接仪器 CANL

**CAN 测试：**
```bash
ip link set can0 up type can bitrate 500000                           # 设置波特率 500kbps
cansend can0 123#01.02.03.04.05.06.07.08                              # 发送数据
candump -ta can0                                                       # 接收数据（-t 打印时间，a ASCII 输出）
```

**CAN FD 测试：**
```bash
ifconfig can0 down                                                     # 先关闭 CAN
ip link set can0 up type can bitrate 1000000 dbitrate 5000000 fd on   # 设置 CAN FD 速率
cansend can0 123##300.11.22.33.44...                                   # 发送 CAN FD 数据（##3 为标志）
```

可用 CAN FD 速率配置（三选一）：
- bitrate 1000000 / dbitrate 5000000
- bitrate 200000 / dbitrate 1000000
- bitrate 100000 / dbitrate 500000

#### 4.8 RTC 时钟测试

- 底板 RTC 芯片：PCF8563（外部 RTC）
- 需检查 RTC 纽扣电池是否有电（正常约 3.3V）
- Linux 系统有两个时钟：system time（软件时钟）和 hardware clock（硬件时钟）

```bash
date                                    # 查看系统时钟
date -s "2020-9-9 10:00:00"            # 设置系统时钟
hwclock -w                              # 将系统时钟写入硬件时钟
hwclock                                 # 查看硬件时钟
```

#### 4.9 AP3216C 测试（仅 STM32MP157，Mini 不支持）

- 三合一环境传感器：环境光强度(ALS)、接近距离(PS)、红外线强度(IR)
- I2C5 接口，I2C 地址 0x1e
- 元器件位置：底板 U6 处（TF 卡旁边）
- 驱动路径：drivers/char/ap3216c.c

```bash
cat /sys/class/misc/ap3216c/als    # 读取环境光强度
cat /sys/class/misc/ap3216c/ps     # 读取接近距离
cat /sys/class/misc/ap3216c/ir     # 读取红外线强度
```

#### 4.10 ICM20608 测试（仅 STM32MP157，Mini 不支持）

- 6 轴 MEMS 传感器：3 轴加速度 + 3 轴陀螺仪
- SPI1 接口，SPI 最大频率 8MHz
- 驱动路径：drivers/char/icm2060c.c

```bash
modprobe icm20608                    # 安装驱动（如果未自动加载）
icm20608App /dev/icm20608            # 获取六轴传感器数据
```

#### 4.11 音频测试（仅 STM32MP157，Mini 不支持）

- 音频编解码芯片：CS42L51
- 板载麦克风可录音，底板背面接 2 欧 8 瓦喇叭
- 耳机旁有跳线帽切换耳机 MIC 输入和底板 MIC 输入（MIC-PHONE 为耳机，MIC-BOARD 为底板）

**播放音频：**
```bash
amixer -c STM32MP1DK cset name='PCM Playback Switch' 'on','on'
amixer -c STM32MP1DK cset name='PCM Playback Volume' '85','85'
amixer -c STM32MP1DK cset name='Analog Playback Volume' '204','204'
amixer -c STM32MP1DK cset name='PCM channel mixer' 'L R'
aplay /usr/share/sounds/alsa/Front_Right.wav
```

**录音：**
```bash
amixer -c STM32MP1DK cset name='PGA-ADC Mux Left' '3'
amixer -c STM32MP1DK cset name='PGA-ADC Mux Right' '3'
amixer -c STM32MP1DK cset name='Mic Boost Volume' '1','1'
arecord -r 44100 -f S16_LE -c 2 -d 10 -D hw:0,1 record.wav  # 录音 10 秒
aplay record.wav                                               # 播放录音
```

#### 4.12 DHT11 测试

- 温湿度一体化数字传感器，单总线通信
- 工作电压 3.3V-5.5V，测量范围湿度 20~90%RH、温度 0~50 度
- 模块插在 JP9 处（拨码开关旁边），有孔一面朝向开发板外侧
- 与 DS18B20 共用管脚（PF2），不能同时使用
- 驱动路径：drivers/char/dht11.c

```bash
rmmod ds18b20                      # 卸载 DS18B20 驱动
rmmod dht11                        # 卸载 DHT11 驱动
modprobe dht11                     # 安装 DHT11 驱动
cat /sys/class/misc/dht11/value    # 读取数据（前两位湿度，后两位温度）
```

#### 4.13 DS18B20 测试

- 数字温度传感器，一线总线，测量范围 -55~+125 度，精度 0.5 度
- 模块插在 JP9 处，半圆面对准底板丝印半圆脚，半圆朝向板外
- 与 DHT11 共用管脚（PF2），不能同时使用
- 驱动路径：drivers/char/ds18b20.c

```bash
rmmod dht11                        # 卸载 DHT11 驱动
rmmod ds18b20                      # 卸载 DS18B20 驱动
modprobe ds18b20                   # 安装 DS18B20 驱动
cat /sys/class/misc/ds18b20/value  # 读取数据（数值除以 10000 为实际温度）
```

#### 4.14 板载 SDIO WIFI 测试（仅 STM32MP157，Mini 不支持）

- WIFI 芯片：RTK-8723DS
- 检查天线是否拧好拧紧，必须插 12V 电源

**Station（上网）模式：**
```bash
ifconfig wlan0 up
iw wlan0 scan | grep SSID          # 扫描热点
vi /etc/wpa_supplicant.conf         # 编辑热点配置
```

配置文件内容：
```
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1
network={
    ssid="你的热点名称"
    psk="你的热点密码"
}
```

连接热点：
```bash
wpa_supplicant -Dnl80211 -c /etc/wpa_supplicant.conf -i wlan0 &
udhcpc -i wlan0                     # 获取 IP
ping www.baidu.com -I wlan0         # 测试连通性
```

快捷脚本连接：
```bash
cd /home/root/shell/wifi
source ./alientek_sdio_wifi_setup.sh -m station -i 热点名 -p 密码 -d wlan0
```

**SoftAP（热点）模式：**
```bash
source ./alientek_sdio_wifi_setup.sh -m softap -d wlan0
# 热点名称：alientek_softap，默认密码：12345678
```

**Bridge（桥接模式）：**
```bash
source ./alientek_sdio_wifi_setup.sh -m bridge -d wlan0 -e eth0
# 热点名称：alientek_bridge，密码：12345678
# 需要底板网口已插网线且能上网
```

#### 4.15 板载蓝牙测试（仅 STM32MP157，Mini 不支持）

- 蓝牙芯片：RTK-8723DS
- 固件路径：/lib/firmware/rtlbt/
- 初始化脚本：/home/root/shell/bluetooth/atk-bluetooth-init.sh

**蓝牙初始化：**
```bash
echo 90 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio90/direction
echo 0 > /sys/class/gpio/gpio90/value
sleep 1
echo 1 > /sys/class/gpio/gpio90/value
rtk_hciattach -n -s 115200 /dev/ttySTM3 rtk_h5 &
systemctl start bluetooth.service
```

或使用脚本：
```bash
cd /home/root/shell/bluetooth
./atk-bluetooth-init.sh
```

**蓝牙传输文件：**
```bash
hciconfig hci0 up
hciconfig hci0 piscan               # 开启蓝牙被扫描
hcitool scan                         # 扫描蓝牙设备
/usr/libexec/bluetooth/obexd -r /home/root -a -d &  # 开启 obexd 守护进程
obexctl                              # 进入交互命令行
connect XX:XX:XX:XX:XX:XX           # 连接手机蓝牙
send /path/to/file                   # 发送文件
```

**蓝牙音乐：**
```bash
hciconfig hci0 up
bluetoothctl                         # 进入蓝牙命令交互行
power on
agent on
scan on                              # 扫描
scan off                             # 找到后关闭扫描
pairable on
connect XX:XX:XX:XX:XX:XX           # 连接蓝牙
exit                                 # 退出后手机端配对确认
```

#### 4.16 4G 模块 ME3630-W 测试（仅 STM32MP157，Mini 可用 USB 转 PCIe 转接板）

- 支持移动、联通、电信 4G 卡
- 天线连接到 4G 模块 MAIN 接口
- WWAN LED 亮绿灯表示正常加载
- 生成 3 个 /dev/ttyUSB* 设备，AT 指令通过 /dev/ttyUSB2 通信
- 脚本路径：/home/root/shell/4G/

**pppd 拨号上网：**
```bash
mkdir /etc/ppp/
cd /home/root/shell/4G/
./ppp-on-10000 &    # 电信卡（10010 联通，10086 移动）
ping www.baidu.com -I ppp0
```

**ECM 上网：**
```bash
./disconnect           # 先断开 pppd
./ECM_DEMO -t up       # 开启 ECM 上网
udhcpc -i usb0         # 获取 IP
ping www.baidu.com -I usb0
```

ECM_DEMO 说明：
- ECM_DEMO 执行完退出，ECM_DEMO_AUTO 会自动断线重连
- `ECM_DEMO -t up -p /dev/ttyUSB1 -a 3gnet` 可指定 APN 和拨号端口

#### 4.17 TF(SD)卡 测试

- 从 eMMC 启动时 TF 卡设备节点为 /dev/mmcblk1
- 自动挂载到 /run/media/mmcblk1
- 需使用 FAT32 格式，不能使用 NTFS 格式

```bash
hdparm -t /dev/mmcblk1                                                                    # 读速度
time dd if=/dev/zero of=/run/media/mmcblk1p5/test bs=1024k count=50 conv=fdatasync        # 写速度
```

#### 4.18 OV5640 摄像头/USB 摄像头测试

**OV5640 摄像头：**
- 插到 CAMERA 接口，镜头朝向板子外侧，不支持热插拔
- 设备节点：/dev/video0
- 测试程序：`ov5640_camera /dev/video0`
- gstreamer 采集到 LCD：`gst-launch-1.0 -v v4l2src device=/dev/video0 ! "video/x-raw, format=(string)YUY2, width=(int)640, height=(int)480, framerate=(fraction)30/1" ! videoconvert ! fbdevsink`
- 录制视频：`gst-launch-1.0 -v v4l2src device=/dev/video0 ! "video/x-raw, format=(string)YUY2, width=(int)640,height=(int)480, framerate=(fraction)30/1" ! videoconvert ! avimux ! filesink location=test.avi`
- 拍照：`gst-launch-1.0 v4l2src num-buffers=1 device=/dev/video0 ! jpegenc ! filesink location=test.jpg`

**USB 摄像头：**
- 支持 UVC 协议的摄像头均可，支持热插拔
- 设备节点：/dev/video1（OV5640 已占用 video0 时）
- 测试方法同 OV5640，将 video0 改为 video1

#### 4.19 SPDIF 测试（仅 STM32MP157，Mini 不支持）

- SPDIF OUT 和 SPDIF IN 两个接口
- 需要 SPDIF 数据光纤测试

#### 4.20 ADC 测试

- ADC 采集电压绝对值最大 3.3V，超过可能损坏芯片
- JP2 处有一路 ADC 与一路 DAC
- STM32MP157D 支持两个 ADC 控制器，采样精度可配置 16/14/12/10/8 位
- Linux 中 ADC 属于 IIO 子系统，使用 16 位精度

```bash
cat /sys/bus/iio/devices/iio:device0/in_voltage19_raw    # 读取原始值
cat /sys/bus/iio/devices/iio:device0/in_voltage_offset   # 读取 offset
cat /sys/bus/iio/devices/iio:device0/in_voltage_scale    # 读取 scale
# 实际值 = (raw_value + offset_value) * scale
```

#### 4.21 DAC 测试

- 8 位或 12 位模式，两个输出通道
- JP2 处有一路 DAC，可通过跳线帽给 ADC1 作输入
- DAC 属于 IIO 子系统，使用 12 位精度

```bash
echo 0 > /sys/bus/iio/devices/iio:device1/out_voltage1_powerdown     # 开启 DAC 输出
cat /sys/bus/iio/devices/iio:device1/out_voltage1_scale              # 读取 scale
echo 1000 > /sys/bus/iio/devices/iio:device1/out_voltage1_raw        # 设置输出值（最大 4095）
# 输出电压 = 3.3 * (out_raw / (2^12 - 1))
```

#### 4.22 CPU 温度

```bash
cat /sys/class/hwmon/hwmon0/temp1_input    # 查看 CPU 温度
```

#### 4.23 CPU 主频

```bash
cpufreq-info                               # 查看 CPU 主频信息
# CPU0 和 CPU1 工作在 400MHz~800MHz，调频模式为 ondemand
```

#### 4.24 查看系统信息

```bash
uname -r                   # 内核版本号
cat /etc/hostname          # 系统主机名
cat /proc/cpuinfo          # CPU 相关信息
cat /proc/meminfo          # 内存相关信息
cat /etc/issue              # 系统登录欢迎信息
```

#### 4.25 HDMI 测试

- 板载 HDMI 芯片：Sil902x（HDMI 发送器）
- CPU 最大输出 LTDC 信号：WXGA (1366x768) @60fps
- 出厂默认 HDMI 分辨率：1280x720 @60fps
- HDMI 与 RGB LCD 共用接口，理论上只能使用其中一种
- Uboot 倒计时时按数字键"2"选择 HDMI 设备树

**永久修改 HDMI 启动：**
- eMMC 启动：编辑 /run/media/mmcblk2p2/mmc1_extlinux/stm32mp157d-atk_extlinux.conf
- TF 卡启动：编辑 /run/media/mmcblk1p2/mmc0_extlinux/stm32mp157d-atk_extlinux.conf
- 将 stm32mp157d-atk 修改为 stm32mp157d-atk-hdmi

#### 4.26 OpenGL 测试

- 退出 Qt 桌面后执行：`glmark2-es2-drm`
- 测试 OpenGL ES 2.0，反映 GPU 性能

#### 4.27 关机和重启

```bash
sync; poweroff               # 关机（建议直接关闭电源）
sync; reboot                 # 重启（或按复位按钮）
```

#### 4.28 查看出厂文件系统版本

```bash
cat /etc/version
```

#### 4.29 4G 模块 EC20 测试

- EC20 模块（推荐 EC20-CE 系列），需购买天线
- 正确插入 4G 卡和模块后 WWAN LED 亮绿灯
- 生成 4 个 /dev/ttyUSB* 设备，AT 指令通过 /dev/ttyUSB2 通信
- WWAN LED 指示灯：慢闪(200ms 高/1800ms 低)=找网，慢闪(1800ms 高/200ms 低)=待机，快闪(125ms 高/125ms 低)=数据传输，高电平=通话中

**ppp 拨号上网：**
```bash
cd /home/root/shell/4G/
./ppp-on-10086 &             # 移动卡（10000 电信，10010 联通）
ping www.baidu.com -I ppp0
```

**quectel-CM 拨号：**
```bash
./disconnect                  # 先断开 ppp
quectel-CM &                  # 后台运行（-s 指定 APN：移动 cmnet，联通 3gnet，电信 ctnet）
ping www.baidu.com -I eth1    # EC20 网络节点为 eth1
```

**GPS 测试：**
```bash
echo -e "AT+QGPS=1\r\n" > /dev/ttyUSB2      # 开启 GPS
cat /dev/ttyUSB1                               # 查看 GPS 原始数据（需到空旷地带）
echo -e "AT+QGPSEND\r\n" > /dev/ttyUSB2      # 关闭 GPS
```

#### 4.30 异核通讯测试

- A7 通过虚拟串口发送数据给 M4 核，M4 控制蜂鸣器
- M4 固件路径：/lib/firmware/RPMsg_UART_CM4.elf
- 脚本路径：/home/root/shell/rpmsg/M4.sh

```bash
cd /home/root/shell/rpmsg/
./M4.sh start RPMsg_UART_CM4.elf    # 开启异核通讯，加载 M4 固件
cat /dev/ttyRPMSG0 &                 # 接收 M4 发来的数据
echo 'beep_on' > /dev/ttyRPMSG0      # 启动 M4 控制的蜂鸣器
echo 'beep_off' > /dev/ttyRPMSG0     # 关闭 M4 控制的蜂鸣器
./M4.sh stop                         # 关闭 M4 核
```

---

### 第五章 ATK-STM32MP157 文件系统简介

#### 5.1 文件系统目录简介

| 目录 | 功能 |
|------|------|
| /bin | 常用执行文件（mv、cp、date 等） |
| /dev | 设备与接口（一切皆文件） |
| /etc | 系统配置文件、启动脚本、服务文件 |
| /home | 默认用户主文件夹，默认存在 root 用户 |
| /lib | 系统函数库、内核模块 modules（驱动程序） |
| /proc | 虚拟文件系统（内核、进程、设备、网络状态） |
| /run | 系统运行时所需文件，重启后重新生成 |
| /sbin | 系统指令，只有 root 用户可执行 |
| /sys | 虚拟文件系统，记录核心系统硬件信息 |
| /tmp | 临时文件 |
| /usr | Linux 核心目录（共享文件、可执行文件等） |
| /var | 系统执行过程经常改变的文件 |
| /vendor | GPU 库文件 |
| /usr/local/ | 出厂 Qt 综合程序 |

#### 5.2 文件系统 Qt 版本

- Qt 5.12.9（LTS 长期支持版本，2021.07 更新后从 Qt5.14.2 降级为 Qt5.12.9）

#### 5.3 如何创建 systemd 自启动服务

```bash
vi /home/root/auto_run_script.sh    # 创建脚本（内容：#!/bin/bash echo "Hello World!" > /dev/ttySTM0）
chmod +x /home/root/auto_run_script.sh
cd /etc/systemd/system
vi auto_run_script.service           # 创建服务文件
```

服务文件内容：
```ini
[Unit]
Description=Run a Custom Script at Startup
After=default.target
[Service]
ExecStart=/home/root/auto_run_script.sh
[Install]
WantedBy=default.target
```

```bash
systemctl daemon-reload
systemctl enable auto_run_script.service
sync; reboot
```

#### 5.4 如何禁用 Qt 界面启动

Qt 显示方式：
- **linuxfb 插件**（默认）：使用 /dev/fb0 设备，纯软件渲染，不使用 GPU 加速
- **eglfs 插件**：使用硬件渲染，触摸屏流畅但鼠标点击卡顿

```bash
systemctl disable systemui     # 永久关闭 Qt 桌面
systemctl start systemui       # 启动 Qt 桌面
systemctl stop systemui        # 停止 Qt 桌面
systemctl enable systemui      # 使能 Qt 桌面
systemctl restart systemui     # 重启 Qt 桌面
```

Qt 服务文件路径：/etc/systemd/system/systemui.service
- linuxfb 方式：ExecStart=/opt/ui/systemui -platform linuxfb
- eglfs 方式：ExecStart=/opt/ui/systemui -platform eglfs

#### 5.5 如何不使用 systemd 服务自启动程序

- 编辑 /etc/profile 文件，在末尾添加自启动命令
- 注意：不同用户登录会重复执行此文件，存在 SSH 用户时建议用 systemd 方式
- Qt 程序启动格式：`/home/root/demo >/dev/null 2>&1 &`

#### 5.6 常用系统软件

| 软件 | 版本 | 功能 |
|------|------|------|
| Qt | 5.12.9 (LTS) | 图形开发库，支持 sqlite、Quick/QML、Qt3D、QWebkit、Qt5Multimedia、Qt5Bluetooth 等 |
| Nginx | 1.16.1 | 轻量级 web 服务器（默认禁用），支持推流 |
| FFmpeg | 4.2.2 | 音视频处理 |
| GStreamer | 1.16.2 | 媒体处理 |
| OpenCV4 | 4.1 | 图像处理 |
| Python3 | 3.8 | 运行 Python 程序 |

---

### 第六章 ATK-STM32MP157 交叉编译篇

三种交叉编译工具链：
1. en.SDK-x86_64-stm32mp1-openstlinux-5.4-dunfell-mp1-20-06-24.tar.xz：ST 官方交叉编译工具链
2. gcc-arm-9.2-2019.12-x86_64-arm-none-linux-gnueabihf.tar.xz：通用 ARM 交叉编译工具（ST 推荐，驱动开发指南教学用）
3. st-example-image-qtwayland-openstlinux-weston-stm32mp1-x86_64-toolchain-3.1-snapshot.sh：Yocto 定制编译工具链，用于编译 Qt 应用程序

#### 6.1 安装通用 ARM 交叉编译工具链

- 安装方法参考《STM32MP1 嵌入式 Linux 驱动开发指南》第 4 章
- 编译 TF-A 参考第 6 章
- 编译 U-Boot 参考第 10 章
- 编译内核参考第 17 章

**编译内核模块：**
```bash
make ARCH=arm CROSS_COMPILE=arm-none-linux-gnueabihf- modules -j32
mkdir tmp
make ARCH=arm INSTALL_MOD_PATH=./tmp modules_install
rm -rf tmp/lib/modules/5.4.31/source
rm -rf tmp/lib/modules/5.4.31/build
find ./tmp -name "*.ko" | xargs arm-none-linux-gnueabihf-strip --strip-debug --remove-section=.comment --remove-section=.note --preserve-dates
```

#### 6.2 安装含编译 Qt 应用程序的交叉编译工具链

```bash
chmod +x st-example-image-qtwayland-openstlinux-weston-stm32mp1-x86_64-toolchain-3.1-snapshot.sh
./st-example-image-qtwayland-openstlinux-weston-stm32mp1-x86_64-toolchain-3.1-snapshot.sh
# 安装到 /opt/st/ 目录下
```

**编译 Qt 应用程序：**
```bash
# 使能工具链（每次切换终端需执行）
source /opt/st/stm32mp1/3.1-snapshot/environment-setup-cortexa7t2hf-neon-vfpv4-ostl-linux-gnueabi
qmake xx.pro              # 或直接 qmake（自动找 xx.pro）
make -j 16
```

**编译出厂 Qt 综合例程：**
- 源码路径：1、程序源码->9、Qt 综合例程源码->systemui.tar.gz
- 解压后执行 `./build.sh`
- 编译成功后将 ui 文件夹替换到开发板 /opt/ 下

#### 6.3 出厂 Linux 源码编译

**编译 TF-A：**
```bash
mkdir mp157/tf-a -p
tar -axvf tf-a-stm32mp-2.2.r1-gxxxxxxx-vx.x.tar.bz2 -C mp157/tf-a/
cd mp157/tf-a/tf-a-stm32mp-2.2.r1/
./build.sh
# 生成 build/trusted/stm32mp157d-atk-trusted.stm32
```

**编译 U-Boot：**
```bash
mkdir mp157/uboot -p
tar -axvf u-boot-stm32mp-2020.01-gxxxxxxx-vxx.tar.bz2 -C mp157/uboot/
cd mp157/uboot/
./build.sh
# 生成 u-boot.stm32
```

**编译内核：**
```bash
mkdir mp157/kernel
tar -axvf linux-5.4.31-gxxxxxxx-vxx.tar.bz2 -C mp157/kernel/
cd mp157/kernel/
./build.sh
# 生成 tmp 目录下的 dtb 文件、uImage、modules.tar.bz2
```

---

## 关键操作步骤

### 硬件接线

1. **屏幕连接**：FPC 排线丝印"1"对"1"、"40"对"40"，排座夹子打开插入排线后扣下
2. **串口连接**：USB Type-C 线连接底板 USB_TTL 接口到电脑
3. **电源连接**：12V 电源适配器连接底板电源接口
4. **拨码设置**：eMMC 启动为 010，SD 卡启动为 101，USB 模式为 000

### 串口连接

- 工具：MobaXterm（或 SecureCRT、Putty）
- 驱动：CH340 USB 串口驱动
- 设置：串口类型，选择 COM 口，波特率 115200
- 登录：默认 root 用户自动登录，无需密码

### 系统启动

1. 拨码到 010（eMMC 启动）
2. 插上 12V 电源适配器
3. 启动开关拨到 ON
4. 等待 Qt 桌面启动（约 30 秒至 1 分钟）
5. 串口终端自动登录

### 烧写系统

1. 拨码到 000（USB 模式）
2. USB Type-C 连接 USB_OTG 到电脑 USB 3.0 接口
3. 打开 STM32CubeProgrammer，选择 USB 设备
4. 加载 tsv 配置文件和固件目录
5. 点击 Download 烧写（约 5-6 分钟）
6. 烧写完成，拨码到 010 启动

---

## 硬件资源概览

### 核心资源

- **SoC**：STM32MP157D，双核 Cortex-A7 + Cortex-M4
- **内存**：DDR3L
- **存储**：eMMC（核心板上）
- **GPU**：支持 OpenGL ES 2.0
- **网络**：千兆以太网（核心板搭载千兆网络芯片，自适应 10/100/1000M）

### 底板接口

- **显示**：RGB LCD 接口、HDMI 接口（Sil902x 芯片，最大 WXGA 1366x768 @60fps）
- **串口**：USB_TTL (uart4/ttySTM0)、DB9 公头 com2 (usart3/ttySTM1)、DB9 母头 com1 (uart5/ttySTM2)、RS485（与 com2 共用 usart3，跳线帽切换）
- **USB**：USB_OTG（USB 2.0）、USB_CN1/CN2/CN3（USB HOST）
- **存储**：TF 卡槽
- **网络**：千兆网口
- **4G**：4G 模块接口（支持 ME3630-W、EC20）
- **摄像头**：OV5640 摄像头接口
- **音频**：CS42L51 编解码芯片、板载麦克风、底板喇叭（2 欧 8 瓦）、耳机座
- **数字音频**：SPDIF OUT、SPDIF IN 接口
- **CAN**：一路 CAN/CAN FD 接口
- **模拟**：ADC/DAC 接口（JP2 处）
- **传感器**：AP3216C（I2C5，环境光/接近/红外）、ICM20608（SPI1，6 轴 MEMS）
- **温湿度**：JP9 处接口（DHT11/DS18B20，共用 PF2 管脚）
- **RTC**：PCF8563 芯片（外部 RTC，纽扣电池供电）
- **蓝牙**：RTK-8723DS 芯片（与 WIFI 共用）
- **WIFI**：RTK-8723DS SDIO WIFI（板载天线）
- **调试**：JTAG 接口（2.0mm 间距，需 ST-LINK 转接板）
- **电源**：DC 6-16V 输入，12V 电源适配器

### GPIO 引脚分配

| 功能 | 引脚 |
|------|------|
| LED0（心跳灯） | PI0 |
| LED1（用户 LED） | PF3 |
| BEEP（蜂鸣器） | PC7 |
| KEY0 | PG3 |
| KEY1 | PH7 |
| DHT11/DS18B20 | PF2 |
| 触摸屏 I2C | I2C2 |
| 触摸屏中断 | PI1 |
| 触摸屏复位 | PH15 |
| AP3216C | I2C5 (0x1e) |
| ICM20608 | SPI1 (CS: PZ3) |
| 蓝牙串口 | /dev/ttySTM3 |
| 蓝牙复位 | GPIO90 |

---

## 正点原子联系方式

- 公司名称：广州市星翼电子科技有限公司
- 在线教学平台：www.yuanzige.com
- 论坛：http://www.openedv.com/forum.php
- 淘宝店铺：https://openedv.taobao.com
- 官方网站：www.alientek.com
- B 站视频：https://space.bilibili.com/394620890
- 电话：020-38271790
- 传真：020-36773971
