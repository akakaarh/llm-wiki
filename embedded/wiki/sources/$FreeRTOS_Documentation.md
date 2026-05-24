---
title: FreeRTOS 内核官方文档
source: FreeRTOS Official Documentation (freertos.org) + FreeRTOS Kernel Source
type: source
tags: [freertos, rtos, embedded, stm32, scheduler, task, queue, semaphore, mutex, timer]
created: 2026-05-24
---

# FreeRTOS 内核官方文档 — 来源摘要

> **来源：** FreeRTOS 官方文档 (freertos.org) + FreeRTOS Kernel 源码仓库 (github.com/freertos/freertos-kernel)
> **覆盖范围：** 内核特性概览、任务管理、调度机制、同步与通信原语、内存管理、软件定时器、配置体系
> **用途：** 嵌入式学习路线阶段5（RTOS + 核间通信）的核心参考

---

## 1. FreeRTOS 概述

FreeRTOS 是一个开源的实时操作系统（RTOS）内核，专为微控制器和小型嵌入式设备设计。其核心特点：

- **极小内存占用**：最小配置仅需 6-10KB ROM、几百字节 RAM
- **抢占式/协作式调度**：支持两种调度策略，可配置
- **C 语言实现**：可移植性强，已有 40+ 官方移植平台
- **MIT 许可证**：免费用于商业产品
- **支持 SMP 多核**：v10.5+ 引入对称多处理支持

FreeRTOS 内核提供以下核心组件：

| 组件 | 说明 |
|------|------|
| 任务管理 | 创建、删除、挂起、恢复任务；优先级调度 |
| 队列 | 任务间、任务与 ISR 间的消息传递 |
| 信号量 | 二进制信号量、计数信号量、互斥量（含优先级继承） |
| 软件定时器 | 周期/单次定时器，由守护任务执行回调 |
| 事件组 | 多标志位同步，支持 AND/OR 等待 |
| 任务通知 | 轻量级信号机制，比信号量更高效 |
| 流/消息缓冲区 | v10+ 新增，字节流/离散消息传递 |
| 内存管理 | 5 种堆实现方案（heap_1 ~ heap_5） |

---

## 2. 任务管理

### 2.1 任务状态

FreeRTOS 任务有四种基本状态：

| 状态 | 说明 |
|------|------|
| **Running（运行）** | 任务正在使用 CPU，任意时刻只有一个任务处于此状态 |
| **Ready（就绪）** | 任务可运行但优先级不够高或同优先级时间片已用完 |
| **Blocked（阻塞）** | 任务在等待事件（延时到期、队列数据、信号量等），不消耗 CPU |
| **Suspended（挂起）** | 任务被显式挂起，不会被调度器调度，必须显式恢复 |

状态转换关系：
```
                 vTaskSuspend()              vTaskResume()
  任意状态 ──────────────────> Suspended ──────────────────> Blocked/Ready
       │                                                        │
       │  事件发生（延时到期/队列/信号量）                         │
       │ <─────────────────                                     │
       │                                                        │
  Blocked ──────> Ready <────── 被抢占 ────── Running
       ↑            │                        │
       │            │  被调度器选中           │ vTaskDelay() / xQueueReceive() 等
       │            └────────────────────>   │
       │                                     │
       └─────────────────────────────────────┘
```

### 2.2 任务创建

**动态分配方式：**
```c
BaseType_t xTaskCreate(
    TaskFunction_t pxTaskCode,    // 任务函数指针
    const char * const pcName,    // 任务名称（调试用）
    const configSTACK_DEPTH_TYPE usStackDepth,  // 栈大小（单位：字）
    void * const pvParameters,    // 传入参数
    UBaseType_t uxPriority,       // 优先级
    TaskHandle_t * const pxCreatedTask  // 任务句柄（可选输出）
);
// 返回：pdPASS 或 errCOULD_NOT_ALLOCATE_REQUIRED_MEMORY
```

**静态分配方式：**
```c
TaskHandle_t xTaskCreateStatic(
    TaskFunction_t pxTaskCode,
    const char * const pcName,
    uint32_t ulStackDepth,
    void * const pvParameters,
    UBaseType_t uxPriority,
    StackType_t * const puxStackBuffer,   // 预分配的栈缓冲区
    StaticTask_t * const pxTaskBuffer      // 预分配的 TCB 缓冲区
);
// 返回：任务句柄，失败返回 NULL
```

**任务函数原型：**
```c
void vTaskFunction( void * pvParameters )
{
    // 初始化代码（只执行一次）

    for( ;; )
    {
        // 任务主循环（永远不返回）
        vTaskDelay( pdMS_TO_TICKS( 100 ) );
    }
}
```

### 2.3 任务删除

```c
void vTaskDelete( TaskHandle_t xTaskToDelete );
// 传入 NULL 删除自身；传入句柄删除指定任务
// 注意：被删除任务的内存由空闲任务释放
```

### 2.4 任务挂起与恢复

```c
void vTaskSuspend( TaskHandle_t xTaskToSuspend );
void vTaskResume( TaskHandle_t xTaskToResume );

// 从中断中恢复任务
BaseType_t xTaskResumeFromISR( TaskHandle_t xTaskToResume );
// 返回：pdTRUE 表示需要上下文切换
```

### 2.5 任务延时

```c
// 相对延时：从调用时刻开始延时指定 tick 数
void vTaskDelay( TickType_t xTicksToDelay );

// 绝对延时：周期性精确延时（避免漂移）
void vTaskDelayUntil( TickType_t * const pxPreviousWakeTime,
                      TickType_t xTimeIncrement );

// 毫秒转 tick 宏
pdMS_TO_TICKS( xTimeInMs )
```

### 2.6 任务优先级

```c
void vTaskPrioritySet( TaskHandle_t xTask, UBaseType_t uxNewPriority );
UBaseType_t uxTaskPriorityGet( TaskHandle_t xTask );

// 获取/设置当前运行任务优先级
UBaseType_t uxTaskPriorityGetFromISR( TaskHandle_t xTask );
```

---

## 3. 调度机制

### 3.1 抢占式调度

当 `configUSE_PREEMPTION = 1`（默认）时，调度器始终运行最高优先级的就绪任务。高优先级任务就绪时会立即抢占低优先级任务。

### 3.2 协作式调度

当 `configUSE_PREEMPTION = 0` 时，任务只有主动让出 CPU（调用 `taskYIELD()` 或阻塞 API）时才会发生切换。

### 3.3 时间片轮转

当 `configUSE_TIME_SLICING = 1`（默认）时，同优先级的多个就绪任务以时间片轮转方式共享 CPU。每个 tick 中断切换一次。

### 3.4 调度器控制

```c
void vTaskStartScheduler();    // 启动调度器（通常在 main() 中调用，不返回）
void vTaskEndScheduler();      // 停止调度器（通常仅用于测试）
void vTaskSuspendAll();        // 挂起调度器（不关中断，ISR 仍可执行）
BaseType_t xTaskResumeAll();   // 恢复调度器

// 主动让出 CPU（同优先级轮转）
void taskYIELD();
```

### 3.5 Tick 机制

FreeRTOS 使用硬件定时器产生周期性 tick 中断来驱动调度。tick 频率由 `configTICK_RATE_HZ` 配置（通常 100~1000 Hz）。

**tick 中断处理流程：**
1. 递增 tick 计数器 `xTickCount`
2. 检查是否有阻塞任务的延时到期，将其移入就绪列表
3. 如果 `configUSE_PREEMPTION = 1`，检查是否有更高优先级任务就绪，触发 PendSV 上下文切换

**Tickless Idle 模式：**
- 通过 `configUSE_TICKLESS_IDLE = 1` 启用
- 当所有任务都阻塞时，停止 tick 中断，让处理器进入低功耗模式
- 在下一个任务唤醒时间点之前提前醒来恢复 tick

### 3.6 上下文切换（PendSV / SVC）

FreeRTOS 在 Cortex-M 上的上下文切换机制：

- **SVC（Supervisor Call）**：启动调度器时使用 `SVC` 指令触发第一个任务的上下文恢复
- **PendSV（Pendable Service Request）**：用于任务切换，设为最低优先级异常
  - 调度器需要切换任务时设置 PendSV 挂起位
  - PendSV 在所有其他中断处理完毕后才执行
  - 保存当前任务寄存器（R4-R11）到其栈，恢复下一个任务的寄存器
  - 切换 PSP（Process Stack Pointer）指向新任务的栈

**关键实现：**
```c
// port.c 中的实现
#define portYIELD()                     \
{                                       \
    portNVIC_INT_CTRL_REG = portNVIC_PENDSVSET_BIT; \
    __dsb( portSY_FULL_READ_WRITE );    \
    __isb( portSY_FULL_READ_WRITE );    \
}

// 从中断中请求上下文切换
#define portYIELD_FROM_ISR( x )         \
{                                       \
    if( x != pdFALSE )                  \
    {                                   \
        portNVIC_INT_CTRL_REG = portNVIC_PENDSVSET_BIT; \
    }                                   \
}
```

---

## 4. 队列（Queue）

队列是 FreeRTOS 任务间通信的主要机制，支持多生产者/多消费者。

### 4.1 队列创建

```c
QueueHandle_t xQueueCreate(
    UBaseType_t uxQueueLength,   // 队列能容纳的最大项数
    UBaseType_t uxItemSize       // 每个项的大小（字节）
);
// 返回：队列句柄，失败返回 NULL

// 静态分配版本
QueueHandle_t xQueueCreateStatic(
    UBaseType_t uxQueueLength,
    UBaseType_t uxItemSize,
    uint8_t * const pucQueueStorageBuffer,
    StaticQueue_t * const pxQueueBuffer
);
```

### 4.2 队列操作

```c
// 发送（任务中使用）
BaseType_t xQueueSend( QueueHandle_t xQueue, const void * const pvItemToQueue, TickType_t xTicksToWait );
BaseType_t xQueueSendToBack( QueueHandle_t xQueue, const void * const pvItemToQueue, TickType_t xTicksToWait );
BaseType_t xQueueSendToFront( QueueHandle_t xQueue, const void * const pvItemToQueue, TickType_t xTicksToWait );

// 发送（ISR 中使用）
BaseType_t xQueueSendFromISR( QueueHandle_t xQueue, const void * const pvItemToQueue, BaseType_t * const pxHigherPriorityTaskWoken );

// 接收
BaseType_t xQueueReceive( QueueHandle_t xQueue, void * const pvBuffer, TickType_t xTicksToWait );

// 查看（不移除）
BaseType_t xQueuePeek( QueueHandle_t xQueue, void * const pvBuffer, TickType_t xTicksToWait );

// 查询可用项数
UBaseType_t uxQueueMessagesWaiting( QueueHandle_t xQueue );

// 查询剩余空间
UBaseType_t uxQueueSpacesAvailable( QueueHandle_t xQueue );
```

**参数说明：**
- `xTicksToWait`：队列满/空时的等待时间，`portMAX_DELAY` 表示永久等待，`0` 表示不等待
- `pxHigherPriorityTaskWoken`：ISR 版本专用，若接收/发送导致更高优先级任务就绪，此值被设为 `pdTRUE`

### 4.3 队列使用模式

**值传递（小型数据）：** 将数据直接拷贝入队列，适合 uint32_t、小型结构体。
**引用传递（大型数据）：** 将指针拷贝入队列，避免大块数据复制。

---

## 5. 信号量与互斥量

FreeRTOS 的信号量基于队列实现，有三种类型。

### 5.1 二进制信号量

适用于任务与 ISR 之间的同步（"通知"模式）。创建时为空，ISR 给出（give），任务获取（take）。

```c
SemaphoreHandle_t xSemaphoreCreateBinary();  // 创建时为空
SemaphoreHandle_t xBinarySemaphore;

// 使用
xBinarySemaphore = xSemaphoreCreateBinary();

// ISR 中给出
void vISR( void )
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR( xBinarySemaphore, &xHigherPriorityTaskWoken );
    portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
}

// 任务中获取
void vTask( void * pvParameters )
{
    for( ;; )
    {
        if( xSemaphoreTake( xBinarySemaphore, portMAX_DELAY ) == pdTRUE )
        {
            // 处理事件
        }
    }
}
```

### 5.2 计数信号量

适用于资源池管理和事件计数。

```c
SemaphoreHandle_t xSemaphoreCreateCounting(
    UBaseType_t uxMaxCount,      // 最大计数值
    UBaseType_t uxInitialCount   // 初始计数值
);

// 资源池示例：5 个连接槽
SemaphoreHandle_t xPool = xSemaphoreCreateCounting( 5, 5 );

// 事件计数示例：初始为 0，每次 ISR 递增
SemaphoreHandle_t xEvents = xSemaphoreCreateCounting( 10, 0 );
```

### 5.3 互斥量（Mutex）

适用于保护共享资源，支持**优先级继承**：当低优先级任务持有互斥量而高优先级任务等待时，低优先级任务临时提升到等待者的优先级，避免优先级反转。

```c
SemaphoreHandle_t xSemaphoreCreateMutex();        // 创建互斥量
SemaphoreHandle_t xSemaphoreCreateRecursiveMutex(); // 递归互斥量

// 递归互斥量：同一任务可多次获取，必须相同次数释放
xSemaphoreTakeRecursive( xMutex, xTicksToWait );
xSemaphoreGiveRecursive( xMutex );
```

**优先级继承机制：**
- 任务 A（低优先级）持有互斥量
- 任务 B（高优先级）尝试获取互斥量，被阻塞
- 内核自动将 A 的优先级提升到 B 的级别
- A 释放互斥量后，优先级恢复原值
- B 获取互斥量并继续执行

### 5.4 信号量通用操作

```c
BaseType_t xSemaphoreTake( SemaphoreHandle_t xSemaphore, TickType_t xTicksToWait );
BaseType_t xSemaphoreGive( SemaphoreHandle_t xSemaphore );

// ISR 中使用（仅限二进制和计数信号量）
BaseType_t xSemaphoreGiveFromISR( SemaphoreHandle_t xSemaphore, BaseType_t * const pxHigherPriorityTaskWoken );
```

---

## 6. 事件组（Event Group）

事件组提供多标志位同步，支持等待多个事件的 AND/OR 组合。

```c
EventGroupHandle_t xEventGroupCreate();

// 设置事件位
EventBits_t xEventGroupSetBits( EventGroupHandle_t xEventGroup, const EventBits_t uxBitsToSet );

// 等待事件位
EventBits_t xEventGroupWaitBits(
    EventGroupHandle_t xEventGroup,
    const EventBits_t uxBitsToWaitFor,     // 要等待的位
    const BaseType_t xClearOnExit,         // 退出时是否清除
    const BaseType_t xWaitForAllBits,      // TRUE=AND，FALSE=OR
    TickType_t xTicksToWait
);

// ISR 中设置
BaseType_t xEventGroupSetBitsFromISR( EventGroupHandle_t xEventGroup,
                                       const EventBits_t uxBitsToSet,
                                       BaseType_t * const pxHigherPriorityTaskWoken );

// 同步点（所有任务到达后才继续）
EventBits_t xEventGroupSync( EventGroupHandle_t xEventGroup,
                              const EventBits_t uxBitsToSet,
                              const EventBits_t uxBitsToWaitFor,
                              TickType_t xTicksToWait );
```

**典型用法 — 多模块初始化同步：**
```c
#define BIT_NETWORK    ( 1 << 0 )
#define BIT_STORAGE    ( 1 << 1 )
#define BIT_SENSOR     ( 1 << 2 )
#define ALL_READY      ( BIT_NETWORK | BIT_STORAGE | BIT_SENSOR )

// 各模块初始化完成后设置对应位
// 主任务等待所有模块就绪
xEventGroupWaitBits( xEventGroup, ALL_READY, pdTRUE, pdTRUE, portMAX_DELAY );
```

---

## 7. 任务通知（Task Notification）

任务通知是 FreeRTOS v10+ 引入的轻量级同步机制，比信号量更高效（直接写入任务 TCB，不经过队列）。

每个任务有一个 32 位通知值，可作为事件标志、计数器或直接传递数据。

```c
// 发送通知
BaseType_t xTaskNotify( TaskHandle_t xTaskToNotify, uint32_t ulValue, eNotifyAction eAction );
BaseType_t xTaskNotifyFromISR( TaskHandle_t xTaskToNotify, uint32_t ulValue,
                                eNotifyAction eAction, BaseType_t * const pxHigherPriorityTaskWoken );

// 等待通知
BaseType_t xTaskNotifyWait( uint32_t ulBitsToClearOnEntry,    // 入口时清除的位
                             uint32_t ulBitsToClearOnExit,     // 出口时清除的位
                             uint32_t * pulNotificationValue,  // 接收通知值
                             TickType_t xTicksToWait );

// 简化版本（纯信号，无值传递）
BaseType_t xTaskNotifyGive( TaskHandle_t xTaskToNotify );
uint32_t ulTaskNotifyTake( BaseType_t xClearCountOnExit, TickType_t xTicksToWait );

// 获取当前任务句柄
TaskHandle_t xTaskGetCurrentTaskHandle();
```

**eNotifyAction 枚举：**

| 值 | 说明 |
|----|------|
| `eNoAction` | 仅唤醒任务，不更新通知值 |
| `eSetBits` | 按位或操作（类似事件组） |
| `eIncrement` | 递增通知值（类似计数信号量） |
| `eSetValueWithOverwrite` | 覆盖写入通知值 |
| `eSetValueWithoutOverwrite` | 仅在无未处理通知时写入 |

**任务通知的局限：**
- 每个任务只有一个通知值（32 位）
- 不支持多消费者（只能通知特定任务）
- 等待通知时不能同时等待多个源（可用位标志模拟）

---

## 8. 软件定时器

软件定时器由 FreeRTOS 的定时器守护任务（Timer Daemon Task）执行，不依赖硬件定时器。

### 8.1 定时器创建与控制

```c
TimerHandle_t xTimerCreate(
    const char * const pcTimerName,          // 定时器名称
    const TickType_t xTimerPeriodInTicks,    // 周期（tick 数）
    const UBaseType_t uxAutoReload,          // pdTRUE=自动重载，pdFALSE=单次
    void * const pvTimerID,                  // 定时器 ID（可在回调中获取）
    TimerCallbackFunction_t pxCallbackFunction  // 回调函数
);

// 回调函数原型
void vTimerCallback( TimerHandle_t xTimer );

// 控制操作
BaseType_t xTimerStart( TimerHandle_t xTimer, TickType_t xTicksToWait );
BaseType_t xTimerStop( TimerHandle_t xTimer, TickType_t xTicksToWait );
BaseType_t xTimerReset( TimerHandle_t xTimer, TickType_t xTicksToWait );
BaseType_t xTimerChangePeriod( TimerHandle_t xTimer, TickType_t xNewPeriod, TickType_t xTicksToWait );

// 从定时器获取/设置 ID
void *pvTimerGetTimerID( TimerHandle_t xTimer );
void vTimerSetTimerID( TimerHandle_t xTimer, void *pvNewID );
```

### 8.2 定时器配置

```c
// FreeRTOSConfig.h 中
#define configUSE_TIMERS                1
#define configTIMER_TASK_PRIORITY       ( configMAX_PRIORITIES - 1 )  // 通常最高优先级
#define configTIMER_QUEUE_LENGTH        10    // 命令队列长度
#define configTIMER_TASK_STACK_DEPTH    ( configMINIMAL_STACK_SIZE * 2 )
```

### 8.3 定时器工作机制

软件定时器不直接运行在中断中，而是通过定时器守护任务处理：
1. `xTimerStart()` 等 API 实际是向定时器命令队列发送命令
2. 守护任务从队列取出命令，管理定时器列表
3. tick 中断检查是否有定时器到期
4. 到期时，守护任务执行回调函数

**注意：** 定时器回调在守护任务上下文中执行，不应使用阻塞 API（会导致守护任务阻塞）。

---

## 9. 内存管理

FreeRTOS 提供 5 种堆实现方案，在 `portable/MemMang/` 目录下：

| 方案 | 文件 | 特点 | 适用场景 |
|------|------|------|----------|
| **heap_1** | `heap_1.c` | 只分配不释放，极简单 | 不需要动态删除任务/队列的系统 |
| **heap_2** | `heap_2.c` | 可分配释放，不合并碎片 | 大小固定分配的系统 |
| **heap_3** | `heap_3.c` | 包装标准库 malloc/free | 堆由编译器/OS 管理的系统 |
| **heap_4** | `heap_4.c` | 可分配释放，合并相邻空闲块 | 通用嵌入式系统（最常用） |
| **heap_5** | `heap_5.c` | 同 heap_4，支持非连续堆区域 | 内存分布不连续的系统 |

### 9.1 核心 API

```c
void *pvPortMalloc( size_t xWantedSize );   // 分配内存
void vPortFree( void *pv );                 // 释放内存
size_t xPortGetFreeHeapSize( void );        // 获取当前空闲堆大小
size_t xPortGetMinimumEverFreeHeapSize( void ); // 获取历史最小空闲堆大小

// v10+ 新增
void *pvPortCalloc( size_t xNum, size_t xSize ); // 分配并清零
```

### 9.2 堆配置

```c
// FreeRTOSConfig.h 中
#define configSUPPORT_DYNAMIC_ALLOCATION    1   // 启用动态分配
#define configSUPPORT_STATIC_ALLOCATION     1   // 启用静态分配
#define configTOTAL_HEAP_SIZE               ( 10 * 1024 )  // 堆大小 10KB

// heap_4/heap_5 新增选项
#define configHEAP_CLEAR_MEMORY_ON_FREE     1   // 释放时清零内存
```

### 9.3 静态分配 vs 动态分配

| 特性 | 动态分配 | 静态分配 |
|------|----------|----------|
| 内存来源 | FreeRTOS 堆 | 用户预分配 |
| 分配失败可能性 | 有 | 无 |
| 碎片问题 | heap_4/5 合并缓解 | 无 |
| 确定性 | 较低 | 高 |
| MISRA 合规 | 需额外审查 | 推荐方式 |

---

## 10. FreeRTOSConfig.h 配置体系

FreeRTOS 通过 `FreeRTOSConfig.h` 头文件进行内核定制，每个移植都需要此文件。

### 10.1 硬件配置

```c
#define configCPU_CLOCK_HZ              ( 72000000UL )    // CPU 频率
#define configTICK_RATE_HZ              ( 1000 )          // Tick 频率（1ms/tick）
```

### 10.2 调度配置

```c
#define configUSE_PREEMPTION            1      // 1=抢占式，0=协作式
#define configUSE_TIME_SLICING          1      // 同优先级时间片轮转
#define configMAX_PRIORITIES            ( 5 )  // 优先级数量
#define configUSE_IDLE_HOOK             0      // 空闲任务钩子
#define configUSE_TICK_HOOK             0      // Tick 中断钩子
```

### 10.3 内存配置

```c
#define configSUPPORT_DYNAMIC_ALLOCATION    1
#define configSUPPORT_STATIC_ALLOCATION     1
#define configTOTAL_HEAP_SIZE               ( 10 * 1024 )
#define configMINIMAL_STACK_SIZE            ( 128 )  // 空闲任务栈大小（字）
```

### 10.4 功能开关

```c
#define configUSE_MUTEXES               1
#define configUSE_RECURSIVE_MUTEXES     1
#define configUSE_COUNTING_SEMAPHORES   1
#define configUSE_TIMERS                1
#define configUSE_EVENT_GROUPS          1
#define configUSE_STREAM_BUFFERS        1
#define configUSE_TASK_NOTIFICATIONS    1
#define configUSE_QUEUE_SETS            0
```

### 10.5 调试配置

```c
#define configCHECK_FOR_STACK_OVERFLOW  2     // 栈溢出检测（1=仅检查末尾，2=也检查模式字）
#define configUSE_MALLOC_FAILED_HOOK    1     // 堆分配失败钩子
#define configASSERT( x )               if( !( x ) ) { taskDISABLE_INTERRUPTS(); for( ;; ); }
```

### 10.6 API 裁剪

```c
// 将不需要的 API 设为 0 可减少代码体积
#define INCLUDE_vTaskPrioritySet        1
#define INCLUDE_uxTaskPriorityGet       1
#define INCLUDE_vTaskDelete             1
#define INCLUDE_vTaskSuspend            1
#define INCLUDE_vTaskDelayUntil         1
#define INCLUDE_vTaskDelay              1
```

---

## 11. STM32MP157 上的 FreeRTOS（正点原子例程）

本地路径：`E:\资料\STM32MP157\【正点原子】STM32MP157开发板（A盘）-基础资料\01、程序源码\04、M4 FreeRTOS驱动例程\`

正点原子提供了 STM32MP157 M4 核的 FreeRTOS 驱动例程（V1.0），以 zip 包形式提供。这些例程基于 STM32CubeIDE + HAL 库，展示了在 Cortex-M4 上运行 FreeRTOS 的典型用法。

---

## 12. SMP 多核支持（v10.5+）

FreeRTOS v10.5+ 引入了对称多处理（SMP）支持，允许在同一芯片的多个核心上运行 FreeRTOS。

### 12.1 SMP 启动流程

**主核流程：**
1. 执行核心特定和共享初始化（设置栈指针、清零 .bss 等）
2. 跳转到 `main()`，创建用户任务，可选地将任务绑定到特定核心
3. 调用 `vTaskStartScheduler()` -> `xPortStartScheduler()`
4. 配置主核 tick 定时器，设置 `ucPrimaryCoreInitDoneFlag` 通知从核
5. 等待所有从核报告就绪
6. 调用 `vPortRestoreContext()` 调度第一个任务

**从核流程：**
1. 执行核心特定初始化
2. 等待主核信号（`ucPrimaryCoreInitDoneFlag = 1`）
3. 更新向量表到 FreeRTOS 向量表
4. 初始化 GIC redistributor，使能 SGI
5. 发出 `SVC` 指令（portSVC_START_FIRST_TASK）启动调度

### 12.2 核间通知

SMP 系统必须实现 `vInterruptCore(uint8_t ucCoreID)` 函数，用于通知其他核心进行上下文切换。典型实现为写入 doorbell 寄存器或处理器间信号寄存器。

---

## 13. 与本 Wiki 的交叉引用

- [[#NVIC]] — FreeRTOS 的中断管理依赖 Cortex-M 的 NVIC，优先级配置必须与 FreeRTOS 的 `configMAX_SYSCALL_INTERRUPT_PRIORITY` 协调
- #ARMv7M_RefManual — PendSV 和 SVC 异常的硬件细节见 ARMv7-M 架构参考手册
- #CortexM3M4_DefinitiveGuide — 上下文切换涉及的寄存器（R4-R11、PSP、xPSR）详见 Cortex-M3/M4 权威指南
- #MP157_IPC_RPMSG — STM32MP157 异核通信中 M4 侧运行 FreeRTOS 的配置
- #MP157_M4_HAL — STM32MP157 M4 HAL 库与 FreeRTOS 的集成
