---
title: ARM GIC 中断控制器
source: ARM Generic Interrupt Controller(ARM GIC控制器)V2.0.pdf
type: source
tags: [arm, gic, interrupt, gicd, gicc, sgi, ppi, spi]
created: 2026-05-24
---

# ARM Generic Interrupt Controller (GIC) Architecture Specification

> 来源：ARM IHI 0048B.b (ID072613)，Architecture version 2.0，2008-2013 ARM。共 214 页。

## 第1章 Introduction（概述）

### 1.1 GIC 架构概述

GIC（Generic Interrupt Controller，通用中断控制器）是 ARM 架构中负责中断管理的核心组件。它负责：
- 接收来自外设和其他来源的中断请求
- 对中断进行优先级仲裁
- 将最高优先级的中断分发给目标处理器核心
- 支持多核系统的中断路由

GIC 架构版本：
- **GICv1**：基础版本，支持安全扩展
- **GICv2**：本规范描述的版本，增加了虚拟化扩展支持
- **GICv3/v4**：后续版本（有单独规范），支持更多核心和 LPI

STM32MP157 中集成的是 GICv2 版本。

### 1.2 安全扩展支持（Security Extensions）

GIC 安全扩展与处理器的 TrustZone 配合工作：
- 中断分为**Group 0（安全中断）**和**Group 1（非安全中断）**
- Group 0 中断触发 FIQ，路由到安全世界处理
- Group 1 中断触发 IRQ，路由到非安全世界处理
- 安全软件（如安全监控器）可以访问所有中断配置
- 非安全软件只能访问 Group 1 中断的配置
- GICD_TYPER.SecurityExtn 位指示是否实现安全扩展

### 1.3 虚拟化支持（Virtualization）

GICv2 支持虚拟化扩展：
- 增加了**虚拟 CPU 接口（Virtual CPU Interface）**，供虚拟机使用
- 通过虚拟接口控制寄存器管理虚拟中断
- 支持虚拟中断注入：Hypervisor 通过 List Registers 将虚拟中断映射到物理中断
- 虚拟机中的操作系统通过虚拟 CPU 接口接收中断

### 1.4 术语

关键术语定义：
- **Pending**：中断已触发，等待处理
- **Active**：中断已被应答，正在处理中
- **Active and Pending**：中断正在处理，同时新的同类中断已触发
- **Enabled**：中断已被软件使能
- **Priority**：中断优先级，数值越小优先级越高

## 第2章 GIC Partitioning（GIC 分区）

### 2.1 GIC 分区概述

GIC 由三个主要部分组成：
1. **Distributor（分配器）**：全局中断配置和分发
2. **CPU Interface（CPU 接口）**：每个处理器核心的中断接口
3. **Virtual CPU Interface（虚拟 CPU 接口）**：GICv2 新增，供虚拟机使用

```
外设中断信号
    |
    v
+------------------+
|   Distributor    |  全局中断配置、优先级仲裁
|   (GICD_*)       |
+------------------+
    |     |     |
    v     v     v
  +---+ +---+ +---+
  |CIF| |CIF| |CIF|   CPU Interface（每核一个）
  | 0 | | 1 | | 2 |   (GICC_*)
  +---+ +---+ +---+
    |     |     |
    v     v     v
  Core0 Core1 Core2
```

### 2.2 Distributor（分配器）

Distributor 负责全局中断管理，主要功能：
- **中断配置**：使能/禁用每个中断，设置中断分组（Group 0/Group 1）
- **优先级设置**：为每个中断配置优先级
- **目标核心设置**：将 SPI 中断路由到指定核心
- **中断状态管理**：维护每个中断的 Pending/Active 状态
- **优先级仲裁**：从所有 Pending 中断中选择最高优先级

Distributor 通过 GICD_* 寄存器访问，这些寄存器是 memory-mapped 的。

每个中断的配置包括：
- 使能/禁用（GICD_ISENABLER/GICD_ICENABLER）
- 优先级（GICD_IPRIORITYR）
- 目标核心（GICD_ITARGETSR）
- 触发方式（GICD_ICFGR）：电平触发或边沿触发
- 分组（GICD_IGROUPR）：Group 0 或 Group 1
- Pending 状态（GICD_ISPENDR/GICD_ICPENDR）
- Active 状态（GICD_ISACTIVER/GICD_ICACTIVER）

### 2.3 CPU Interface（CPU 接口）

每个处理器核心有一个独立的 CPU 接口，负责：
- **中断应答**：读取 GICC_IAR 获取最高优先级 Pending 中断的 ID
- **中断完成通知**：写入 GICC_EOIR 通知 GIC 中断处理完毕
- **优先级屏蔽**：通过 GICC_PMR 设置最低可响应优先级
- **抢占控制**：支持中断嵌套和优先级抢占

CPU 接口通过 GICC_* 寄存器访问。

## 第3章 Interrupt Handling and Prioritization（中断处理与优先级）

### 3.1 中断处理概述

GIC 管理的中断有四种状态：
- **Inactive**：中断未触发
- **Pending**：中断已触发，等待核心应答
- **Active**：中断已被核心应答，正在处理
- **Active and Pending**：中断正在处理，新的同类中断已到来

### 3.2 中断通用处理流程

中断处理的标准流程：

**1. 中断触发阶段**
- 外设拉高中断信号线
- GIC 将对应中断状态设为 Pending
- GICD_ISPENDRn 对应位置位

**2. 优先级仲裁阶段**
- Distributor 从所有已使能且 Pending 的中断中选择优先级最高的
- 将该中断与当前 Active 中断的优先级比较
- 如果 Pending 中断优先级更高，通过 nIRQ/nFIQ 通知目标核心

**3. 中断应答阶段**
- 核心进入中断处理模式（IRQ/FIQ handler）
- 软件读取 GICC_IAR 寄存器获取中断 ID
- 读取操作同时完成应答：中断状态从 Pending 变为 Active
- 对于 SGI，GICC_IAR 返回源核心 ID 和中断 ID

**4. 中断处理阶段**
- 软件根据中断 ID 执行相应的中断服务程序（ISR）
- 可以在 ISR 中清除外设的中断源

**5. 中断完成阶段**
- 软件写入 GICC_EOIR 寄存器，通知 GIC 中断处理完毕
- 写入值为中断 ID
- GIC 将中断状态从 Active 变为 Inactive
- 如果有同一中断再次 Pending，则转为 Pending 状态

### 3.3 中断优先级

**优先级字段**：
- 每个中断有一个 8 位优先级字段（GICD_IPRIORITYRn）
- 优先级值范围：0~255，**数值越小优先级越高**
- 实现时可能只使用高几位（如高 4 位），低几位为只读 0
- Cortex-A7 通常使用高 4 位（16 级优先级）

**优先级寄存器**：
- GICD_IPRIORITYRn：每个寄存器 32 位，包含 4 个中断的优先级（每个 8 位）
- 例如 GICD_IPRIORITYR0 包含中断 0~3 的优先级

**特殊优先级**：
- 优先级 0x00 通常保留给 SGI 的最低优先级
- 优先级 0xFF（最低）用于空闲/默认

### 3.4 中断分组对中断处理的影响

**Group 0 中断**：
- 触发 FIQ 信号
- 优先级仲裁时独立进行
- 在安全世界处理

**Group 1 中断**：
- 触发 IRQ 信号
- 优先级仲裁时独立进行
- 在非安全世界处理

**仲裁规则**：
- Group 0 和 Group 1 独立仲裁
- Group 0 优先级高于 Group 1（当两者同时 Pending 时，Group 0 先被处理）
- 通过 GICC_CTLR.FIQEn 位可配置 Group 1 中断使用 FIQ（虚拟化场景）

### 3.5 中断分组与优先级配置

GIC 支持安全扩展时的中断分组配置：

**GICD_IGROUPRn 寄存器**：
- 每位对应一个中断
- 0 = Group 0（安全，FIQ）
- 1 = Group 1（非安全，IRQ）

**GICC_BPR（Binary Point Register）**：
- 控制优先级比较时使用的位数
- 将优先级字段分为"组优先级"和"子优先级"
- 组优先级用于仲裁，子优先级用于同一组内的排序

**GICC_ABPR（Aliased Binary Point Register）**：
- Group 1 中断使用的别名 BPR
- 允许安全软件为非安全中断设置不同的优先级分组策略

### 3.6 安全扩展附加特性

- **中断优先级屏蔽**：GICC_PMR 设置最低可响应优先级，高于此阈值的中断才被响应
- **优先级下降**：当 Group 1 中断被应答时，核心自动切换到非安全状态
- **抢占控制**：GICC_PMR 在中断应答时自动更新为被应答中断的优先级

### 3.7 伪代码：中断处理和优先级

规范提供了详细的伪代码描述中断仲裁过程：
- `GICGetHighestPriorityPendingInterrupt()`：获取最高优先级 Pending 中断
- `GICPriorityMask()`：检查中断是否满足优先级屏蔽条件
- `GICCheckPriority()`：比较两个中断的优先级

### 3.8 虚拟化扩展对中断处理的影响

虚拟化场景下中断处理的变化：
- Hypervisor 通过 HCR 寄存器控制虚拟中断行为
- List Registers（GICH_LRn）用于虚拟中断注入
- 物理中断可映射为虚拟中断
- 虚拟机中的操作系统通过 GICC_IAR 虚拟接口应答虚拟中断

### 3.9 GIC 使用示例

**示例 1：基本中断配置流程**
```
1. 禁用所有中断
   写 0xFFFFFFFF 到 GICD_ICENABLER0~n

2. 配置中断分组
   写 GICD_IGROUPRn 设置每个中断的分组

3. 设置中断优先级
   写 GICD_IPRIORITYRn 设置每个中断的优先级

4. 设置中断目标核心
   写 GICD_ITARGETSRn 设置 SPI 的目标核心

5. 设置触发方式
   写 GICD_ICFGRn 设置电平/边沿触发

6. 使能中断
   写 GICD_ISENABLERn 使能需要的中断

7. 使能 Distributor
   写 GICD_CTLR 使能分配器

8. 使能 CPU Interface
   写 GICC_CTLR 使能 CPU 接口
   写 GICC_PMR 设置优先级屏蔽值（通常 0xFF 允许所有）
```

**示例 2：中断处理流程**
```
IRQ Handler:
1. 读 GICC_IAR -> 获取中断 ID
2. 屏障指令（DSB/ISB）
3. 执行中断服务程序
4. 写 GICC_EOIR -> 通知中断完成
5. 屏障指令（DSB/ISB）
6. 返回
```

## 第4章 Programmers' Model（编程模型）

### 4.1 编程模型概述

GIC 的编程模型通过两组寄存器实现：
- **GICD_*（Distributor 寄存器）**：全局中断配置，通常只有安全软件可完全访问
- **GICC_*（CPU Interface 寄存器）**：每核的中断处理，部分寄存器非安全世界可访问

寄存器基地址（STM32MP157 典型配置）：
- GICD 基地址：0xA0021000
- GICC 基地址：0xA0022000
- GICH 基地址：0xA0024000（虚拟接口控制）
- GICV 基地址：0xA0026000（虚拟 CPU 接口）

### 4.2 安全扩展对编程模型的影响

安全扩展实现时：
- GICD_TYPER.SecurityExtn = 1
- 安全软件可访问所有 GICD_* 和 GICC_* 寄存器
- 非安全软件只能访问部分 GICD_* 寄存器（Group 1 相关）和 GICC_* 寄存器
- 非安全软件读取安全中断配置时返回 0 或默认值

### 4.3 Distributor 寄存器描述

#### GICD_CTLR（Distributor Control Register）

地址偏移：0x000
- 位 [0] Enable：GIC 使能
  - 0 = 禁用，所有中断不被分发
  - 1 = 使能，中断正常分发
- 安全扩展时：位 [0] 控制 Group 0，位 [1] 控制 Group 1

#### GICD_TYPER（Interrupt Controller Type Register）

地址偏移：0x004，只读
- 位 [4:0] ITLinesNumber：中断线路数量减 1
  - 支持的中断数 = 32 * (ITLinesNumber + 1)
  - 例如 5 = 支持 192 个中断
- 位 [7:5] CPUNumber：CPU 接口数量减 1
- 位 [10:8] _划分的实现定义字段
- 位 [12] LSPI：锁定 SPI 的支持
- 位 [13] SecurityExtn：安全扩展实现标志
  - 0 = 未实现安全扩展
  - 1 = 实现安全扩展

#### GICD_IIDR（Implementer Identification Register）

地址偏移：0x008，只读
- 位 [11:0] Implementer：实现者 JEP106 代码
- 位 [19:12] Revision：修订版本
- 位 [31:20] ProductID：产品 ID

#### GICD_IGROUPRn（Interrupt Group Registers）

地址偏移：0x080 + 4*n（n = 0, 1, ...）
- 每位对应一个中断
- 0 = Group 0（安全，FIQ）
- 1 = Group 1（非安全，IRQ）
- 复位值：所有位为 0（Group 0）

#### GICD_ISENABLERn（Interrupt Set-Enable Registers）

地址偏移：0x100 + 4*n
- 写 1 使能对应中断，写 0 无影响
- 读取返回当前使能状态

#### GICD_ICENABLERn（Interrupt Clear-Enable Registers）

地址偏移：0x180 + 4*n
- 写 1 禁用对应中断，写 0 无影响
- 读取返回当前使能状态

#### GICD_ISPENDRn（Interrupt Set-Pending Registers）

地址偏移：0x200 + 4*n
- 写 1 将对应中断设为 Pending（软件触发）
- 用于 SGI 和测试

#### GICD_ICPENDRn（Interrupt Clear-Pending Registers）

地址偏移：0x280 + 4*n
- 写 1 清除对应中断的 Pending 状态

#### GICD_ISACTIVERn / GICD_ICACTIVERn

地址偏移：0x300 + 4*n / 0x380 + 4*n
- 设置/清除中断的 Active 状态
- 用于调试和状态保存/恢复

#### GICD_IPRIORITYRn（Interrupt Priority Registers）

地址偏移：0x400 + 4*n
- 每个寄存器包含 4 个中断的优先级（每个 8 位）
- 位 [7:0] 对应中断 n*4 的优先级
- 位 [15:8] 对应中断 n*4+1 的优先级
- 位 [23:16] 对应中断 n*4+2 的优先级
- 位 [31:24] 对应中断 n*4+3 的优先级
- 优先级值 0~255，数值越小优先级越高
- 复位值：所有优先级为 0（最高优先级）

#### GICD_ITARGETSRn（Interrupt Processor Targets Registers）

地址偏移：0x800 + 4*n
- 每个寄存器包含 4 个中断的目标核心（每个 8 位）
- 位 [7:0] 对应中断 n*4 的目标
- 每位对应一个核心：位 0 = CPU 0，位 1 = CPU 1，...
- 支持多播：多个位同时置位可将中断路由到多个核心
- 仅对 SPI 有效，SGI/PPI 为只读（固定为当前核心）

#### GICD_ICFGRn（Interrupt Configuration Registers）

地址偏移：0xC00 + 8*n
- 每个寄存器包含 16 个中断的配置（每个 2 位）
- 每 2 位配置一个中断的触发方式：
  - 0b00 = 电平触发（Level-sensitive）
  - 0b10 = 边沿触发（Edge-triggered）
- SGI 固定为边沿触发，只读

#### GICD_NSACRn（Non-Secure Access Control Registers）

地址偏移：0xE00 + 4*n
- 控制非安全软件对中断的访问权限
- 仅在安全扩展实现时有意义

#### GICD_SGIR（Software Generated Interrupt Register）

地址偏移：0xF00，只写
- 位 [15:0] SGIINTID：SGI 中断 ID（0~15）
- 位 [23:16] CPUTargetList：目标核心列表（位掩码）
- 位 [25:24] TargetListFilter：
  - 0b00 = 发送到 CPUTargetList 指定的核心
  - b01 = 发送到除当前核心外的所有核心
  - 0b10 = 仅发送到当前核心
- 位 [26] NSATT：安全/非安全 SGI
  - 0 = 安全 Group 0 SGI
  - 1 = 非安全 Group 1 SGI

#### GICD_CPENDSGIRn / GICD_SPENDSGIRn

地址偏移：0xF10 + 4*n / 0xF20 + 4*n
- SGI Pending 状态的设置和清除
- 每个 SGI 的 Pending 状态按源核心分开记录（每个 SGI 16 位，每位对应一个源核心）

### 4.4 CPU Interface 寄存器描述

#### GICC_CTLR（CPU Interface Control Register）

地址偏移：0x000
- 位 [0] Enable：CPU 接口使能
  - 0 = 禁用，核心不接收中断
  - 1 = 使能，核心正常接收中断
- 位 [1] AckCtl（安全扩展时）：
  - 0 = 非安全软件读取 Group 0 的 GICC_IAR 返回 1022（假中断）
  - 1 = 非安全软件可应答 Group 0 中断
- 位 [2] FIQEn（安全扩展时）：
  - 0 = Group 1 中断使用 IRQ
  - 1 = Group 1 中断使用 FIQ（用于虚拟化）
- 位 [3] SBPR：
  - 0 = 使用 GICC_BPR 和 GICC_ABPR 分别控制
  - 1 = 使用 GICC_BPR 控制所有分组

#### GICC_PMR（Priority Mask Register）

地址偏移：0x004
- 位 [7:0] Priority：优先级屏蔽值
- 只有优先级值小于等于此值的中断才会被响应
- 0xFF = 允许所有优先级的中断
- 0x00 = 屏蔽所有中断
- 复位值：0x00（所有中断被屏蔽）

#### GICC_BPR（Binary Point Register）

地址偏移：0x008
- 位 [2:0] BinaryPoint：二进制点
- 控制优先级字段的分组：将 8 位优先级分为"组优先级"和"子优先级"
- 仲裁使用组优先级，子优先级用于同组内的排序
- 值 0 = 所有 8 位用于仲裁
- 值 7 = 仅最高 1 位用于仲裁

#### GICC_ABPR（Aliased Binary Point Register）

地址偏移：0x01C
- 仅在安全扩展实现时有意义
- Group 1 中断使用的别名 BPR
- 允许安全软件为非安全中断设置不同的优先级分组

#### GICC_IAR（Interrupt Acknowledge Register）

地址偏移：0x00C，只读
- 位 [9:0] InterruptID：中断 ID
  - 0~15：SGI（同时位 [12:10] 包含源核心 ID）
  - 16~31：PPI
  - 32~1019：SPI
  - 1022：假中断（Spurious interrupt）
  - 1023：无中断
- 读取此寄存器完成中断应答：
  - 将中断状态从 Pending 改为 Active
  - 清除对应的 Pending 位

#### GICC_EOIR（End of Interrupt Register）

地址偏移：0x010，只写
- 位 [9:0] EOIINTID：中断 ID
- 写入此寄存器通知 GIC 中断处理完毕
- 将中断状态从 Active 改为 Inactive
- 如果有同一中断 Pending，则转为 Pending

#### GICC_RPR（Running Priority Register）

地址偏移：0x014，只读
- 位 [7:0] Priority：当前正在处理的最高优先级中断的优先级
- 用于中断嵌套场景：新中断必须比当前优先级更高才能抢占

#### GICC_HPPIR（Highest Priority Pending Interrupt Register）

地址偏移：0x018，只读
- 位 [9:0] PENDINTID：最高优先级 Pending 中断的 ID
- 位 [12:10] CPUID：SGI 的源核心 ID

#### GICC_ABPR（Aliased Binary Point Register）

地址偏移：0x01C
- Group 1 中断的优先级分组控制

#### GICC_IIDR（CPU Interface Identification Register）

地址偏移：0x0FC，只读
- 实现者标识信息

### 4.5 保存和恢复 GIC 状态

GIC 状态保存/恢复的要点：
- **保存状态**：在挂起/休眠前，保存所有 GICD_IGROUPRn、GICD_ISENABLERn、GICD_IPRIORITYRn、GICD_ITARGETSRn、GICD_ICFGRn 以及 GICC_CTLR、GICC_PMR 等
- **恢复状态**：在唤醒后，按正确顺序恢复寄存器：先恢复配置（分组、优先级、目标），再恢复使能，最后使能 Distributor 和 CPU Interface
- **Pending/Active 状态**：需要特殊处理，可能需要重新触发或清除
- 保存顺序建议：先禁用 GICD 和 GICC，再保存，最后恢复并使能

## 第5章 GIC Support for Virtualization（虚拟化支持）

### 5.1 虚拟化环境中的 GIC

在支持虚拟化的系统中，GIC 增加了虚拟中断处理能力：
- **物理中断**：由实际外设触发，由 Distributor 处理
- **虚拟中断**：由 Hypervisor 注入给虚拟机，通过虚拟 CPU 接口传递

### 5.2 管理 GIC 虚拟 CPU 接口

Hypervisor 通过以下步骤管理虚拟中断：
1. 接收物理中断（读 GICC_IAR）
2. 确定该中断应路由到哪个虚拟机
3. 通过 List Registers 将物理中断映射为虚拟中断
4. 虚拟机通过虚拟 CPU 接口接收和处理虚拟中断

### 5.3 虚拟接口控制寄存器（GICH_*）

#### GICH_HCR（Hypervisor Control Register）

地址偏移：0x000
- 位 [0] En：虚拟接口使能
- 位 [1] UIE：Underflow 中断使能
- 位 [2] LRENPIE：List Register Entry Not Present 中断使能
- 位 [3] NPIE：No Pending 中断使能
- 位 [4] VGrp0EIE：Virtual Group 0 中断使能
- 位 [5] VGrp1DIE：Virtual Group 1 禁用中断使能
- 位 [6] EOICount：EOI 计数器

#### GICH_VTR（Virtual Type Register）

地址偏移：0x004，只读
- 位 [5:0] ListRegs：实现的 List Register 数量减 1
- 位 [26:23] PREbits：优先级位数减 1

#### GICH_VMCR（Virtual Machine Control Register）

地址偏移：0x008
- 虚拟机的 GIC 控制状态的虚拟副本
- 包含虚拟 GICC_CTLR、GICC_PMR、GICC_BPR 等

#### GICH_MISR（Maintenance Interrupt Status Register）

地址偏移：0x010，只读
- 报告维护中断的原因

#### GICH_EISR0 / GICH_EISR1

地址偏移：0x020 / 0x024，只读
- End of Interrupt Status Register
- 报告哪些 List Register 条目需要 EOI 处理

#### GICH_ELRSR0 / GICH_ELRS1

地址偏移：0x030 / 0x034，只读
- Empty List Register Status Register
- 报告哪些 List Register 条目为空

#### GICH_APR（Active Priority Register）

地址偏移：0x0F0
- 虚拟中断的活动优先级记录

#### GICH_LRn（List Registers）

地址偏移：0x100 + 4*n
- 每个 List Register 对应一个虚拟中断槽位
- 位 [9:0] VirtualID：虚拟中断 ID
- 位 [15:10] 保留
- 位 [23:16] PhysicalID：物理中断 ID
- 位 [27:24] Priority：虚拟中断优先级
- 位 [29:28] State：中断状态（00=Inactive, 01=Pending, 10=Active, 11=Pending+Active）
- 位 [30] Group1：分组标志
- 位 [31] HW：硬件中断标志
  - 0 = 虚拟中断（软件注入）
  - 1 = 硬件中断映射（物理中断到虚拟中断）

### 5.4 虚拟 CPU 接口

虚拟 CPU 接口是虚拟机中操作系统看到的 GIC 接口，其寄存器与 GICC_* 寄存器对齐（地址偏移相同），但功能是虚拟的：
- 虚拟 GICC_IAR：返回虚拟中断 ID
- 虚拟 GICC_EOIR：通知虚拟中断完成

### 5.5 虚拟 CPU 接口寄存器

虚拟 CPU 接口寄存器（GICV_*）与物理 GICC_* 寄存器一一对应：
- GICV_CTLR、GICV_PMR、GICV_BPR、GICV_IAR、GICV_EOIR、GICV_RPR、GICV_HPPIR
- 虚拟机操作系统访问这些寄存器时，GIC 返回虚拟中断信息

## 附录：寄存器快速参考

### Distributor 寄存器（GICD_*）

| 寄存器 | 偏移 | 读写 | 描述 |
|--------|------|------|------|
| GICD_CTLR | 0x000 | RW | 分配器控制 |
| GICD_TYPER | 0x004 | RO | 类型信息 |
| GICD_IIDR | 0x008 | RO | 实现者 ID |
| GICD_IGROUPRn | 0x080+4n | RW | 中断分组 |
| GICD_ISENABLERn | 0x100+4n | RW | 中断使能置位 |
| GICD_ICENABLERn | 0x180+4n | RW | 中断使能清除 |
| GICD_ISPENDRn | 0x200+4n | RW | 中断 Pending 置位 |
| GICD_ICPENDRn | 0x280+4n | RW | 中断 Pending 清除 |
| GICD_ISACTIVERn | 0x300+4n | RW | 中断 Active 置位 |
| GICD_ICACTIVERn | 0x380+4n | RW | 中断 Active 清除 |
| GICD_IPRIORITYRn | 0x400+4n | RW | 中断优先级 |
| GICD_ITARGETSRn | 0x800+4n | RW | 中断目标核心 |
| GICD_ICFGRn | 0xC00+8n | RW | 中断触发配置 |
| GICD_NSACRn | 0xE00+4n | RW | 非安全访问控制 |
| GICD_SGIR | 0xF00 | WO | 软件中断触发 |
| GICD_CPENDSGIRn | 0xF10+4n | RW | SGI Pending 清除 |
| GICD_SPENDSGIRn | 0xF20+4n | RW | SGI Pending 置位 |

### CPU Interface 寄存器（GICC_*）

| 寄存器 | 偏移 | 读写 | 描述 |
|--------|------|------|------|
| GICC_CTLR | 0x000 | RW | CPU 接口控制 |
| GICC_PMR | 0x004 | RW | 优先级屏蔽 |
| GICC_BPR | 0x008 | RW | 二进制点 |
| GICC_IAR | 0x00C | RO | 中断应答 |
| GICC_EOIR | 0x010 | WO | 中断完成 |
| GICC_RPR | 0x014 | RO | 运行优先级 |
| GICC_HPPIR | 0x018 | RO | 最高优先级 Pending |
| GICC_ABPR | 0x01C | RW | 别名二进制点 |
| GICC_IIDR | 0x0FC | RO | CPU 接口 ID |

### 虚拟接口控制寄存器（GICH_*）

| 寄存器 | 偏移 | 读写 | 描述 |
|--------|------|------|------|
| GICH_HCR | 0x000 | RW | Hypervisor 控制 |
| GICH_VTR | 0x004 | RO | 虚拟类型 |
| GICH_VMCR | 0x008 | RW | 虚拟机控制 |
| GICH_MISR | 0x010 | RO | 维护中断状态 |
| GICH_EISR0 | 0x020 | RO | EOI 状态 0 |
| GICH_EISR1 | 0x024 | RO | EOI 状态 1 |
| GICH_ELRSR0 | 0x030 | RO | 空列表状态 0 |
| GICH_ELRSR1 | 0x034 | RO | 空列表状态 1 |
| GICH_APR | 0x0F0 | RW | 活动优先级 |
| GICH_LRn | 0x100+4n | RW | 列表寄存器 |
