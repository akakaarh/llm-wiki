---
type: source
title: ARMv7-M Architecture Reference Manual
doc_number: DDI0403E
date: 2010
source: raw/assets/DDI0403E_e_armv7m_arm.pdf
tags: [arm, armv7-m, cortex-m, architecture, reference]
---

# ARMv7-M Architecture Reference Manual (DDI0403E)

## 基本信息

- **文档编号**: DDI0403E
- **版本**: E (2010+)
- **格式**: PDF提取文本，约48,000行
- **架构**: ARMv7-M ( microcontroller profile)

## 架构概述

ARMv7-M是ARM架构的微控制器配置文件，专为高度确定性、中断低延迟、优化代码密度而设计。仅支持[[ARM 指令集体系|Thumb-2指令集]]（16位和32位Thumb指令混合），不支持ARM模式。详见 [[Cortex-A 与 Cortex-M 对比]]。

### 与ARMv7-A/R的核心区别

| 特性 | ARMv7-M | ARMv7-A/R |
|------|---------|-----------|
| 指令集 | 仅Thumb-2 | ARM + Thumb |
| 特权模型 | Privileged (可选User) | PL0/PL1/PL2 |
| MMU | 无([[MPU — 内存保护单元（Cortex-M）|MPU]]) | 完整[[MMU 与虚拟内存|MMU]] |
| 中断控制器 | [[NVIC]](集成) | GIC(独立) |
| 分页 | 固定4GB线性空间 | 虚拟内存支持 |

---

## Part A - Application Level Architecture

### Chapter A1: Introduction

**A1.1 Armv7架构与配置文件**

Armv7定义了三类配置文件：
- **Armv7-A**: 应用配置文件，支持ARM和Thumb指令集，需要虚拟地址支持的内存管理模型
- **Armv7-R**: 实时配置文件，支持ARM和Thumb指令集，物理地址-only支持
- **Armv7-M**: 微控制器配置文件，仅支持Thumb指令集，注重尺寸和确定性操作

**A1.2 Armv7-M架构特点**
- 行业领先功率/性能/面积约束
- 高度确定性：单周期或低周期执行，最小中断延迟
- 优秀C/C++目标：异常处理函数是标准C/C++函数
- 深度嵌入式系统设计：低引脚数设备

**A1.3 架构扩展**

两个可选扩展：
1. **DSP扩展** (Armv7E-M): 添加DSP指令，包括饱和和unsigned SIMD指令
2. **浮点扩展** (FPv4-SP / FPv5):
   - FPv4-SP: 单精度实现，VFPv4-D16
   - FPv5: 添加双精度支持和额外指令

---

### Chapter A2: Application Level Programmers' Model

**A2.1 应用级程序员模型概述**

- 应用在Thread模式执行，可特权或非特权
- SVC指令生成Supervisor Call异常，在Handler模式处理
- 所有异常在Handler模式以特权代码执行

**A2.2 数据类型与算术**

支持的数据类型：
- **字节**: 8位
- **半字**: 16位
- **字**: 32位

寄存器操作：
- 32位指针
- 有符号/无符号32位整数
- 有符号/无符号16位、8位整数（零扩展或符号扩展）
- 64位整数（两寄存器）

移位和旋转操作：
- LSL (逻辑左移)
- LSR (逻辑右移)
- ASR (算术右移)
- ROR (旋转右移)
- RRX (带扩展旋转右移1位)

饱和算术：
- SignedSatQ(), UnsignedSatQ() - 返回饱和标志
- SignedSat(), UnsignedSat() - 仅返回饱和结果

**A2.3 寄存器与执行状态**

核心寄存器（R0-R15）：
| 寄存器 | 别名 | 说明 |
|--------|------|------|
| R0-R12 | - | 通用寄存器 |
| SP | R13 | 栈指针 |
| LR | R14 | 链接寄存器，保存返回地址 |
| PC | R15 | 程序计数器 |

**APSR (Application Program Status Register)**:
```
31  30  29  28  27  26              19  16   15            0
 NZCV Q     Reserved           GE[3:0]  Reserved
```

- **N (bit[31])**: 负数标志
- **Z (bit[30])**: 零标志
- **C (bit[29])**: 进位标志
- **V (bit[28])**: 溢出标志
- **Q (bit[27])**: 饱和标志 (DSP扩展)
- **GE[3:0] (bits[19:16])**: DSP扩展的Greater-Than标志

**执行状态**:
- Armv7-M仅执行Thumb指令
- EPSR.T位必须为1，0会导致INVSTATE UsageFault

**A2.4 异常、故障与中断**

异常类型：
- **Supervisor Calls (SVCall)**: 使用SVC指令
- **Faults**:
  - 指令执行错误
  - 数据内存访问错误
  - UsageFaults (未定义指令等)
  - DebugMonitor异常
- **中断**: 异步处理

内置系统组件：
- **SysTick**: 系统定时器及中断
- **PendSV**: 延迟Supervisor Call
- **NVIC**: 嵌套向量中断控制器
- **BKPT**: 调试事件指令

同步原语：
- SEV (Send Event)
- WFE (Wait For Event)
- WFI (Wait For Interrupt)

**A2.5 浮点扩展 (可选)**

FPv4-SP和FPv5两个版本：

**FPv4-SP FPU**:
- 32个单精度寄存器(S0-S31)或16个双精度寄存器(D0-D15)
- 单精度浮点算术
- 整数、单精度、半精度转换

**FPv5 FPU** (额外功能):
- 双精度浮点算术
- 额外指令: VSEL, VMAXNM, VMINNM, VCVTA/TN/TP/TM, VRINTA/N/P/M/Z/R

**FPSCR (Floating-point Status and Control Register)**:
```
31  30  29  28  27  26  25  24  23  22              7   4    0
 NZCV   AHP  FZ  DN  RMode    Reserved    IDC   Reserved  IXC UFC OFC DZC IOC
```

- **AHP (bit[26])**: 半精度控制 (0=IEEE, 1=替代格式)
- **DN (bit[25])**: 默认NaN模式
- **FZ (bit[24])**:  Flush-to-zero模式
- **RMode (bits[23:22])**: 舍入模式 (RN/RP/RM/RZ)
- **IOC/DZC/OFC/UFC/IXC/IDC**: 异常累计位

**A2.6 协处理器支持**

- CP0-CP7: IMPLEMENTATION DEFINED
- CP8-CP15: ARM保留
- CP10/CP11: 浮点扩展 (需通过CPACR启用)

---

### Chapter A3: Arm Architecture Memory Model

**A3.1 地址空间**

- 4GB (2^32) 字节地址空间
- 单一平坦地址模型
- 所有地址是物理地址 (PA)
- 地址计算使用无符号整数运算

**A3.2 对齐支持**

**始终生成对齐故障的访问**:
- 非半字对齐的LDREXH/STREXH
- 非字对齐的LDREX/STREX
- 非字对齐的LDRD, LDMIA, LDMDB, POP, LDC, VLDR, VLDM, VPOP
- 非字对齐的STRD, STMIA, STMDB, PUSH, STC, VSTR, VSTM, VPUSH

**支持非对齐访问（可配置）**:
- LDR/STR (字)
- LDRH/STRH (半字)
- TBH

**A3.3 字节序支持**

**小端 (Little-endian)**:
- 地址A的字节是字的最低有效字节

**大端 (Big-endian)**:
- 地址A的字节是字的最高有效字节

**Armv7-M特性**:
- 数据访问的字节序可配置（复位时静态决定）
- 指令获取始终是小端
- SCS访问始终是小端

字节序反转指令:
- REV: 反转32位字节序
- REV16: 反转两个半字
- REVSH: 反转半字并符号扩展

**A3.4 同步与信号量**

**独占访问指令**:
- LDREX, LDREXB, LDREXH (加载-独占)
- STREX, STREXB, STREXH (存储-独占)
- CLREX (清除-独占)

**本地监视器状态机**:
```
Open Access <--CLREX/StoreExcl(x)--> Exclusive Access
```

**独占监视器保证**:
- LDREX标记地址
- STREX检查标记并返回状态(0=成功, 1=失败)
- 标记大小是IMPLEMENTATION DEFINED (最小2位，最大11位)
- 推荐LDREX/STREX间隔<128字节

**A3.5 内存类型与属性**

三种内存类型：

| 类型 | 说明 | 特性 |
|------|------|------|
| **Normal** | 代码/数据存储 | 可缓存、可共享 |
| **Device** | 内存映射外设 | 有副作用、不可缓存 |
| **Strongly-ordered** | 严格排序内存 | 完全按程序顺序 |

**内存属性摘要**:
- **Shareable**: 可在多处理器间共享
- **Non-shareable**: 单处理器私有
- **Cacheability**: Non-cacheable / Write-Through / Write-Back

**A3.6 访问权限**

**数据访问控制**:
- 不可访问
- 仅特权访问
- 特权和非特权访问

**指令执行控制**:
- 不可执行 (XN)
- 仅特权执行
- 特权和非特权执行

**A3.7 内存访问顺序**

**内存屏障指令**:
1. **DMB** (Data Memory Barrier): 确保所有内存访问在屏障前观察到在屏障后的访问之前
2. **DSB** (Data Synchronization Barrier): 比DMB更严格，确保所有内存访问完成
3. **ISB** (Instruction Synchronization Barrier): 刷新流水线，确保上下文改变效果可见
4. **CSDB** (Consumption of Speculative Data Barrier): 阻止推测执行
5. **PSSBB/SSBB**: 阻止推测存储绕过

**内存顺序规则** (Figure A3-8):
- Normal访问: 可以重排
- Device Non-shareable: 有顺序限制
- Device Shareable: 必须按程序顺序
- Strongly-ordered: 必须严格按程序顺序

**A3.8 缓存与内存层次**

缓存特性：
- 基于空间局部性和时间局部性
- 缓存行是缓存分配的单元
- 支持可选缓存

缓存维护操作：
- Invalidate
- Clean
- Clean and Invalidate

---

### Chapter A4: The Armv7-M Instruction Set

**Thumb指令特点**:
- 16位或32位指令，2字节对齐
- 16位指令通常只能访问R0-R7 (低寄存器)
- 32位指令可访问所有寄存器

**A4.1 指令集概述**

分支指令:
| 指令 | 范围 | 说明 |
|------|------|------|
| B | +/-1MB | 分支 |
| CBNZ/CBZ | 0-126B | 比较并分支(零/非零) |
| BL | +/-16MB | 调用子程序 |
| BLX (register) | 任意 | 调用并切换指令集 |
| BX | 任意 | 分支并切换指令集 |
| TBB/TBH | 0-510B/0-131070B | 表分支 |

**A4.4 数据处理指令**

主要数据处理指令：
- ADC, ADD, ADR, AND, BIC, CMN, CMP, EOR, MOV, MVN, ORN, ORR, RSB, SBC, SUB, TEQ, TST

移位指令:
- LSL, LSR, ASR, ROR, RRX

乘法指令:
- MUL, MLA, MLS, UMULL, UMLAL, SMULL, SMLAL

饱和指令 (DSP扩展):
- SSAT, USAT

打包/解包指令:
- PKHTB, PKHBT, SXTB, SXTH, UXTB, UXTH

除法指令:
- SDIV, UDIV

**A4.7 状态寄存器访问指令**
- MRS (PSR到寄存器)
- MSR (寄存器到PSR)

**A4.8 加载/存储指令**
- LDR/STR (立即偏移、寄存器偏移)
- LDRB/STRB, LDRH/STRH
- LDRSB, LDRSH
- LDREX/STREX系列
- LDM/STM (多加载/存储)
- PUSH/POP

**A4.9 杂项指令**
- BKPT (断点)
- SVC (系统服务调用)
- SEV, WFE, WFI (同步原语)
- CLREX, ISB, DMB, DSB

**A4.12 协处理器指令**
- MCR, MRC, MCRR, MRRC (协处理器寄存器传输)

---

### Chapter A5: Thumb Instruction Set Encoding

**16位Thumb指令编码 (T1, T2)**:
- LSL, LSR, ASR, ADD, SUB, MOV, CMP, ADD, SUB, CMP, MOV (寄存器)
- AND, EOR, LSL, LSR, ASR, ROR, TST, SETEND (ARMv6-M+)
- CBZ, CBNZ, IT (Armv6-M+)

**32位Thumb-2指令编码 (T1, T2, T3, T4)**:
- 16位指令的扩展
- 额外的数据处理、加载/存储、分支指令

**指令选择规则**:
- 16位编码优先（代码密度优化）
- .W qualifier强制32位编码
- .N qualifier强制16位编码

---

### Chapter A6: Floating-point Instruction Set Encoding

浮点指令编码：
- VADD, VSUB, VMUL, VDIV
- VCMP, VCMPE
- VLDR, VSTR
- VLDM, VSTM, VPUSH, VPOP
- VMOV (寄存器间传输)
- VCVT (类型转换)
- VMAXNM, VMINNM
- VRINTA, VRINTN, VRINTP, VRINTM

---

### Chapter A7: Instruction Details

指令按字母顺序排列，每条指令包含：
- 语法格式
- 编码
- 伪代码描述
- 异常信息
- 备注

**重要指令速查**:

| Mnemonic | 功能 | 页码 |
|----------|------|------|
| ADC | 带进位加法 | A7-177 |
| ADD | 加法 | A7-177 |
| AND | 位与 | A7-179 |
| B | 分支 | A7-205 |
| BFC | 位段清除 | A7-208 |
| BFI | 位段插入 | A7-209 |
| BIC | 位清除 | A7-210 |
| BKPT | 断点 | A7-212 |
| BL | 分支带链接 | A7-213 |
| BLX | 分支带链接并切换 | A7-214 |
| BX | 分支并切换 | A7-215 |
| CBZ/CBNZ | 比较并分支 | A7-216 |
| CLREX | 清除独占 | A7-219 |
| CLZ | 计算前导零 | A7-220 |
| CMN | 比较取负 | A7-221 |
| CMP | 比较 | A7-222 |
| CPS | 改变处理器状态 | A7-223 |
| CPY | 复制 | A7-225 |
| DMB | 数据内存屏障 | A7-230 |
| DSB | 数据同步屏障 | A7-231 |
| EOR | 异或 | A7-232 |
| ISB | 指令同步屏障 | A7-235 |
| IT | If-Then | A7-236 |
| LDM | 多加载 | A7-241 |
| LDR | 加载字 | A7-247 |
| LDRB | 加载字节 | A7-254 |
| LDRD | 加载双字 | A7-257 |
| LDREX | 加载独占 | A7-261 |
| LDRH | 加载半字 | A7-264 |
| LDRSB | 加载符号字节 | A7-267 |
| LDRSH | 加载符号半字 | A7-269 |
| LSL | 逻辑左移 | A7-271 |
| LSR | 逻辑右移 | A7-273 |
| MLA | 乘加 | A7-275 |
| MLS | 乘减 | A7-276 |
| MOV | 移动 | A7-277 |
| MOVT | 移动顶部半字 | A7-281 |
| MRS | PSR到寄存器 | A7-283 |
| MSR | 寄存器到PSR | A7-285 |
| MUL | 乘法 | A7-287 |
| MVN | 移动取反 | A7-288 |
| NOP | 无操作 | A7-289 |
| ORN | 或非 | A7-290 |
| ORR | 或 | A7-291 |
| POP | 出栈 | A7-293 |
| PUSH | 入栈 | A7-295 |
| RBIT | 位反转 | A7-297 |
| REV | 字节反转字 | A7-298 |
| REV16 | 字节反转半字 | A7-299 |
| REVSH | 反转半字并符号扩展 | A7-300 |
| ROR | 旋转右移 | A7-301 |
| RRX | 带进位旋转右移 | A7-302 |
| SBC | 带借位减法 | A7-303 |
| SDIV | 有符号除法 | A7-304 |
| SEL | 选择字节 | A7-351 |
| SEV | 发送事件 | A7-352 |
| SMULL | 有符号长乘法 | A7-353 |
| SSAT | 有符号饱和 | A7-354 |
| STM | 多存储 | A7-356 |
| STR | 存储字 | A7-359 |
| STRB | 存储字节 | A7-362 |
| STRD | 存储双字 | A7-364 |
| STREX | 存储独占 | A7-394 |
| STRH | 存储半字 | A7-365 |
| SUB | 减法 | A7-368 |
| SVC | 超级调用 | A7-371 |
| SXTB | 符号扩展字节 | A7-372 |
| SXTH | 符号扩展半字 | A7-373 |
| TBB | 表分支字节 | A7-416 |
| TBH | 表分支半字 | A7-417 |
| TEQ | 测试等价 | A7-418 |
| TST | 测试 | A7-419 |
| UBFX | 无符号位段提取 | A7-420 |
| UDIV | 无符号除法 | A7-421 |
| UMLAL | 无符号长乘加 | A7-422 |
| UMULL | 无符号长乘法 | A7-423 |
| USAT | 无符号饱和 | A7-424 |
| UXTB | 零扩展字节 | A7-426 |
| UXTH | 零扩展半字 | A7-427 |
| VABS | 浮点绝对值 | A7-428 |
| VADD | 浮点加法 | A7-430 |
| VCMP | 浮点比较 | A7-431 |
| VCVT | 浮点转换 | A7-459 |
| VDIV | 浮点除法 | A7-436 |
| VFMA | 浮点乘加 | A7-437 |
| VFNMA | 浮点负乘加 | A7-438 |
| VFNMS | 浮点负乘减 | A7-439 |
| VLDM | 浮点多加载 | A7-440 |
| VLDR | 浮点加载 | A7-443 |
| VMAXNM | 浮点最大值 | A7-475 |
| VMINNM | 浮点最小值 | A7-476 |
| VMLA | 浮点乘加 | A7-447 |
| VMLS | 浮点乘减 | A7-448 |
| VMOV | 浮点移动 | A7-449 |
| VMRS | 浮点寄存器到PSR | A7-485 |
| VMSR | PSR到浮点寄存器 | A7-486 |
| VMUL | 浮点乘法 | A7-451 |
| VNEG | 浮点取负 | A7-452 |
| VNMLA | 浮点负乘加 | A7-453 |
| VNMLS | 浮点负乘减 | A7-454 |
| VNMUL | 浮点负乘 | A7-455 |
| VPOP | 浮点出栈 | A7-456 |
| VPUSH | 浮点入栈 | A7-457 |
| VRINTA | 浮点舍入到整数(away) | A7-493 |
| VRINTN | 浮点舍入到整数(nearest) | A7-493 |
| VRINTP | 浮点舍入到整数(+inf) | A7-493 |
| VRINTM | 浮点舍入到整数(-inf) | A7-493 |
| VRINTZ | 浮点舍入到整数(zero) | A7-496 |
| VRINTR | 浮点舍入到整数(与RNDR产生相同结果) | A7-496 |
| VSEL | 浮点选择 | A7-497 |
| VSTM | 浮点多存储 | A7-498 |
| VSTR | 浮点存储 | A7-501 |
| VSUB | 浮点减法 | A7-502 |
| VABS | 浮点绝对值 | A7-428 |

---

## Part B - System Level Architecture

### Chapter B1: System Level Programmers' Model

**B1.1 异常模型概述**

Armv7-M异常模型特点：
- 硬件压栈/出栈
- 向量表可重定位
- 低延迟中断入口

**异常类型与优先级**:
| 异常号 | 类型 | 说明 |
|--------|------|------|
| 1 | Reset | 复位 |
| 2 | NMI | 不可屏蔽中断 |
| 3 | HardFault | 硬故障 |
| 4 | MemManage | 内存管理故障 |
| 5 | BusFault | 总线故障 |
| 6 | UsageFault | 使用故障 |
| 7-10 | - | 保留 |
| 11 | SVCall | 超级调用 |
| 12-14 | - | 保留 |
| 15 | DebugMonitor | 调试监控 |
| 16+ | IRQ0-IRQn | 外设中断 |

**B1.3 系统寄存器**

**xPSR (Application/System Program Status Register)**:
- APSR (Application): N/Z/C/V/Q/GE
- IPSR (Interrupt): 异常号
- EPSR (Execution): T位 (Thumb状态)

**PRIMASK**: 屏蔽所有可配置优先级中断 (1=屏蔽)

**FAULTMASK**: 屏蔽HardFault (1=屏蔽)

**BASEPRI**: 按优先级屏蔽中断

**CONTROL**:
- bit[0]: 特权选择 (0=特权, 1=非特权)
- bit[1]: SP选择 (0=Main, 1=Process)

**B1.4 异常入口/出口行为**

异常入口：
1. 压栈 (R0-R3, R12, LR, PC, xPSR)
2. 读取向量
3. 更新SP
4. 加载PC
5. 更新LR

异常出口 (EXC_RETURN):
- 0xFFFFFFF1: 返回Handler模式，使用MSP
- 0xFFFFFFF9: 返回Thread模式，使用MSP
- 0xFFFFFFFD: 返回Thread模式，使用PSP

**B1.5 浮点上下文压栈**

如果浮点扩展存在且启用：
- 压栈时自动保存S0-S15, FPSCR
- 可选保存S16-S31 (Lazy stacking)

---

### Chapter B2: System Memory Model

**B2.1 系统内存模型**

内存模型通过伪代码定义：
- MemU[]: 未对齐内存访问
- MemA[]: 对齐内存访问
- Mem[]: 内存抽象

**B2.2 缓存和分支预测器维护操作**

内存映射缓存维护（IMPLEMENTATION DEFINED）：
- ICIALLU: 无效化指令缓存
- ICIMVAU: 按地址无效化
- BPIALLU: 无效化分支预测

---

### Chapter B3: System Address Map

**4GB地址空间布局**:
```
0x0000_0000 - 0x1FFF_FFFF: 代码区 (512MB) - 起始地址空间
0x2000_0000 - 0x3FFF_FFFF: SRAM区 (512MB)
0x4000_0000 - 0x5FFF_FFFF: 外设区 (512MB)
0x6000_0000 - 0x9FFF_FFFF: 外部SRAM (1GB)
0xA000_0000 - 0xDFFF_FFFF: 外部设备 (1GB)
0xE000_0000 - 0xE00F_FFFF: 系统控制空间 (SCS) (1MB)
0xE010_0000 - 0xFFFF_FFFF: 保留
```

**B3.3 SCS (System Control Space) 地址映射**:
```
0xE000_E008 - 0xE000_E00F: SysTick
0xE000_E010 - 0xE000_E0FF: NVIC
0xE000_ED00 - 0xE000_ED8F: SCB
0xE000_ED90 - 0xE000_EDEF: MPU
0xE000_EF00 - 0xE000_EF3F: FPU (如果存在)
0xE000_EDF0 - 0xE000_EEFF: Debug
```

**B3.4 关键系统寄存器**

**ICSR (Interrupt Control and State Register)**:
- VECTACTIVE: 当前活跃异常
- VECTPENDING: 待处理最高优先级异常
- ISRPENDING: 中断待处理标志
- PENDSVSET/PENDSVCLR: PendSV控制
- RETTOBASE: 返回基础检查

**AIRCR (Application Interrupt and Reset Control Register)**:
- VECTRESET: 系统复位
- VECTCLRACTIVE: 清除活跃标志
- ENDIANNESS: 字节序 (0=LE, 1=BE)
- PRIGROUP: 中断优先级分组

**CCR (Configuration and Control Register)**:
- UNALIGN_TRP: 非对齐访问陷阱
- DIV_0_TRP: 除零陷阱
- USERSETMPR: 用户设置主栈指针
- NONBASETHRD: 线程模式非基础

**B3.5 NVIC (Nested Vectored Interrupt Controller)**

特性：
- 最多240个中断
- 16个优先级
- 硬件优先级掩码
- 向量表重定位
- 外部中断支持

关键寄存器：
- NVIC_ISER: 中断设置启用
- NVIC_ICER: 中断清除启用
- NVIC_ISPR: 中断设置待处理
- NVIC_ICPR: 中断清除待处理
- NVIC_IPR0-IPR59: 中断优先级

**B3.6 MPU (Memory Protection Unit)** (可选)

**MPU特性**:
- 最多8或16个保护区域
- 子区域禁用
- XN (Execute Never) 位
- 特权/用户访问控制
- 缓存属性支持

**MPU寄存器**:
- MPU_TYPE: 类型 (区域数)
- MPU_CTRL: 控制 (启用MPU, 默认区域属性)
- MPU_RNR: 区域号
- MPU_RBAR: 区域基地址
- MPU_RASR: 区域属性和大小

**MPU_RASR位定义**:
```
31  29  28   24  23  22  21  19  18  16  15   8   5    1   0
 XN  AP   RESERVED  SRD  B   C   S  RESERVED  SIZE  ENABLE
```

- **XN (bit[28])**: Execute Never
- **AP (bits[26:24])**: 访问权限
- **SRD (bits[15:8])**: 子区域禁用
- **B/C/S**: 缓存属性
- **SIZE**: 区域大小 (2^(SIZE+1))

---

### Chapter B4: The CPUID Scheme

CPUID寄存器用于识别处理器架构和特性。

**MIDR (Main ID Register)**:
```
31  24  20  16  4    0
Implementer  Variant  Architecture  PartNO  Revision
```

**CTR (Cache Type Register)**: 缓存类型信息

**TCMTR (TCM Type Register)**: TCM类型

**MPUIR (MPU Type Register)**: MPU区域数

**PAUTH_..** (Armv8-M): 指针认证相关

**ID_..** (众多): 架构特性寄存器

**FPIDR, FPEXC**: 浮点实现标识

---

### Chapter B5: System Instruction Details

**CPSIE I/F**: 启用/禁用中断
**MRS/MSR**: PSR访问
**WFI/WFE/SEV**: 等待指令

**CLREX**: 清除独占监视器

**布防/解蔽指令**:
- RFE (返回from exception) - Armv7-R
- SRS (存储返回状态) - Armv7-R

---

## Part C - Debug Architecture

### Chapter C1: Armv7-M Debug

**C1.1 调试架构概述**

两种调试模式：
1. **Halting Debug**: 处理器停止，完整调试访问
2. **Monitor Debug**: 异常处理期间调试

**C1.2 调试事件**

同步调试事件：
- 断点 (BKPT指令或FPB匹配)
- 向量捕获
- 单步

异步调试事件：
- 监视点 (数据匹配)
- 暂停请求
- 外部调试请求

**C1.3 断点单元 (FPB)**

FPB特性：
- 最多8个指令断点
- 指令字匹配 (LIT)
- 字比较器 (COMP)
- 链接字用于向量捕获

**C1.4 数据监视点与跟踪 (DWT)**

DWT特性：
- 最多4个监视点
- PC值包
- 数据地址包
- 数据值包
- 性能计数器

**C1.6 调试系统寄存器**

**DFSR (Debug Fault Status Register)**:
- EXTERNAL: 外部调试请求
- VCATCH: 向量捕获
- DWTTRAP: DWT陷阱
- BKPT: 断点
- HALTED: 暂停

**DHCSR (Debug Halting Control and Status Register)**:
```
31  16  15  14  13  12  11  10  9   8   6   5   4   3   2   1   0
DBGKEY  S_RESET_ST S_RETIRE_ST S_LOCKUP S_SLEEP S_HALT S_REGRDY  C_SNAPSTALL C_MASKINTS C_STEP C_HALT C_DEBUGEN
```

关键位：
- **C_DEBUGEN**: 启用调试
- **C_HALT**: 暂停请求
- **C_STEP**: 单步
- **C_MASKINTS**: 屏蔽中断

**DEMCR (Debug Exception and Monitor Control Register)**:
- VC_CORERESET: 核心复位向量捕获
- VC_MMERR: 内存管理错误向量捕获
- VC_CHKERR: 检查错误向量捕获
- VC_HARDERR: 硬错误向量捕获
- VC_SFTERR: 软件错误向量捕获
- VC_HALT: 暂停向量捕获
- MON_EN: 监控调试启用
- MON_STEP: 监控单步
- MON_PEND: 监控待处理

---

## Part D - Appendices

### Appendix D1: CoreSight Infrastructure IDs

CoreSight ID寄存器：
- PERIPHERALID0-4
- COMPONENTID0-3

格式遵循ARM debug接口规范。

---

### Appendix D2: Legacy Instruction Mnemonics

传统Thumb助记符支持：
- NOP (旧式)
- YIELD, WFE, WFI, SEV (提示指令)

---

### Appendix D3: Deprecated Features

deprecated特性：
- 小端BE-8格式 (Armv6-M)
- 某些CP15操作

---

### Appendix D4: Armv7-M DSP Extension

**DSP扩展指令** (Armv7E-M):

饱和算术：
- SSAT, USAT

SIMD操作：
- SADD8, SADDSUBX, SSUB8, etc.
- QADD8, QSUB8, etc.
- SHADD8, SHADD16, etc.

并行加减：
- SADD16, SADD8
- SSUB16, SSUB8

**ITM (Instrumentation Trace Macrocell)**:
- 软件跟踪
- 硬件源包
- 时间戳

**DWT包协议**:
- 同步包
- 硬件源包
- 时间戳包
- PC采样包

---

### Appendix D5: Armv7-R Differences

**D5.1 概述**

Armv7-M和Armv7-R的比较：
- Thumb-2技术是共同的
- 关键权衡：绝对性能 vs 中断延迟

**D5.2 字节序支持差异**

| 特性 | Armv7-M | Armv7-R |
|------|---------|---------|
| 指令获取字节序 | 仅小端 | 大端/小端可配置 |
| 数据字节序 | 复位静态配置 | 动态控制 (xPSR.EE) |

**D5.3 Application Level Support (关键)**

Armv7-M可视为Armv7-R的子集：

**共同支持**:
- 相同的标志和通用寄存器
- 所有Armv7-M应用级指令
- SDIV/UDIV硬件除法
- 可选浮点扩展

**Armv7-R额外支持**:
- SIMD指令和饱和算术 (Armv7-M DSP扩展才有)
- ARM和Thumb指令集 + 互操作
- 双字LDREX/STREX + SWP (deprecated)
- 高级SIMD (NEON) - Armv7-M不支持

**Load Multiple行为差异**:
- Armv7-R: 始终可重启
- Armv7-M: 支持基于xPSR.ICI位的继续模型

**浮点差异**:
- Armv7-R: 双精度操作，更复杂架构
- Armv7-M: 仅单精度(FPv4-SP)或有限双精度(FPv5)
- Armv7-M无浮点子架构概念

**D5.4 System Level Support**

**关键差异**:

| 特性 | Armv7-M | Armv7-R |
|------|---------|---------|
| 寄存器banking | 仅SP | 完整banking |
| 异常模型 | 低延迟，自动压栈 | 传统模式，软件控制 |
| 系统控制 | 内存映射寄存器 | CP15协处理器 |
| 调试控制 | CP14 | CP14 |
| PMSAv7 | 可选 | 必需 |
| 缓存 | 内存映射系统缓存 | 紧耦合缓存支持 |
| 中断控制器 | NVIC集成 | GIC (独立) |

**D5.5 Debug Support**

- 两者都支持Halting和Monitor调试
- 断点和监视点机制不同
- Armv7-M调试侵入性更小
- Armv7-M提供额外的软件/硬件事件生成跟踪能力

---

### Appendix D6: Pseudocode Definition

**数据类型**:
- Bitstrings: bits(N)
- Integers: unbounded正/负
- Booleans: TRUE/FALSE
- Reals: unbounded实数
- Enumerations: 符号常量集
- Lists: 有序元素集
- Arrays: 索引集合

**关键操作符**:
- 移位: LSL, LSR, ASR, ROR, RRX
- 算数: +, -, *, /, MOD
- 位操作: AND, OR, EOR, NOT
- 比较: ==, !=, <, >, <=, >=

**关键函数**:
- UInt(), SInt(): 位串到整数转换
- BitString(): 整数到位串转换
- ConditionPassed(): 条件执行检查
- Align(), Round(): 对齐和舍入

---

### Appendix D7-D8: 保留用于其他信息

(D7为空，D8未在此文档中定义)

---

## 重要附录速查

### 异常入口压栈顺序 (Armv7-M)

```
地址递减写入:
xPSR
PC (返回地址)
LR (R14)
R12
R3
R2
R1
R0
```

### EXC_RETURN 值

| 值 | 说明 |
|----|------|
| 0xFFFFFFF1 | 返回Handler模式，使用MSP |
| 0xFFFFFFF9 | 返回Thread模式，使用MSP |
| 0xFFFFFFFD | 返回Thread模式，使用PSP |
| 0xFFFFFFE1 | (Armv8-M) 返回Handler，使用SP |
| 0xFFFFFFE9 | (Armv8-M) 返回Thread，使用MSP |
| 0xFFFFFFED | (Armv8-M) 返回Thread，使用PSP |

### 关键系统地址

| 地址 | 寄存器 | 说明 |
|------|--------|------|
| 0xE000ED00 | SCB | 系统控制块 |
| 0xE000ED08 | ICSR | 中断控制与状态 |
| 0xE000ED0C | AIRCR | 应用中断/复位控制 |
| 0xE000ED10 | SCR | 系统控制 |
| 0xE000ED14 | CCR | 配置与控制 |
| 0xE000ED20 | SMPR | 系统处理器优先级掩码 |
| 0xE000ED24 | PRIGROUP | 中断优先级分组 |
| 0xE000ED80 | MPU_TYPE | MPU类型 |
| 0xE000ED90 | MPU_CTRL | MPU控制 |
| 0xE000ED94 | MPU_RNR | MPU区域号 |
| 0xE000ED98 | MPU_RBAR | MPU区域基地址 |
| 0xE000ED9C | MPU_RASR | MPU区域属性和大小 |
| 0xE000EF00 | FPCCR | 浮点上下文控制 |
| 0xE000EF04 | FPCAR | 浮点上下文地址 |
| 0xE000EF08 | FPDSCR | 浮点默认状态控制 |
| 0xE000EF0C | VMED | 主导出异常 |
| 0xE000EDFO | DFSR | 调试故障状态 |
| 0xE000EDF4 | DHCSR | 调试暂停控制和状态 |
| 0xE000EDF8 | DCRSR | 调试核心寄存器选择 |
| 0xE000EDFC | DCRDR | 调试核心数据 |
| 0xE000EFE0 | DEMCR | 调试异常和监控控制 |

---

## 文档信息

- **Copyright**: ARM Limited, 2006-2008, 2010, 2014, 2017, 2018, 2021
- **非保密文档**
- **文档ID**: ID021621
