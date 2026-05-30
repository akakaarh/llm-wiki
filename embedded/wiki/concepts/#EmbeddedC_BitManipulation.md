---
type: concept
tags: [c-language, bit-manipulation, volatile, mmio, struct-packing, embedded-c]
---

# 嵌入式C语言

嵌入式C语言与应用层C的核心差异在于：直接操作硬件。位操作、volatile、内存映射I/O、结构体对齐等特性是嵌入式开发的日常。

---

## 位操作（Bit Manipulation）

### 基本操作

| 操作 | C 表达式 | 说明 |
|------|----------|------|
| 置位 | `val \|= (1 << n)` | 第 n 位置 1 |
| 清位 | `val &= ~(1 << n)` | 第 n 位清 0 |
| 翻转 | `val ^= (1 << n)` | 第 n 位取反 |
| 读位 | `(val >> n) & 1` | 读取第 n 位值 |
| 掩码提取 | `val & 0xFF00` | 提取指定位段 |

### 位域赋值（先清后写）

寄存器中经常需要修改某个位域而不影响其他位：

```c
// 将 GPIOA->MODER 的 [5:4] 设置为 0b01（输出模式）
// 先清零目标位域，再写入新值
GPIOA->MODER &= ~(0x3 << 4);   // 清零 [5:4]
GPIOA->MODER |=  (0x1 << 4);   // 写入 01
```

**合并写法（推荐）：**
```c
#define SET_BITFIELD(reg, mask, pos, val) \
    ((reg) = ((reg) & ~((mask) << (pos))) | ((val) << (pos)))

SET_BITFIELD(GPIOA->MODER, 0x3, 4, 0x1);
```

### 多位域同时修改

```c
// 同时配置多个位域时，先构建完整值再一次性写入
uint32_t moder = GPIOA->MODER;
moder &= ~(0x3 << 4);   // 清 PA2
moder &= ~(0x3 << 6);   // 清 PA3
moder |=  (0x1 << 4);   // PA2 = 输出
moder |=  (0x1 << 6);   // PA3 = 输出
GPIOA->MODER = moder;    // 一次性写入
```

好处：减少对寄存器的读写次数，避免中间状态触发硬件动作。

---

## volatile 关键字

### 为什么需要 volatile

编译器优化会假设：如果一个变量在函数内没有被显式修改，它的值不会变。但对于硬件寄存器，值可能被外设随时改变。

```c
// 没有 volatile — 编译器可能优化成只读一次
uint32_t *status_reg = (uint32_t *)0x40021000;
while (*status_reg == 0) { }  // 编译器可能死循环

// 有 volatile — 每次都从内存读取
volatile uint32_t *status_reg = (volatile uint32_t *)0x40021000;
while (*status_reg == 0) { }  // 每次循环都重新读取
```

### volatile 的使用场景

| 场景 | 示例 |
|------|------|
| 硬件寄存器 | `*(volatile uint32_t *)0x40021000` |
| 中断修改的变量 | `volatile int flag;` 在 ISR 中置位，主循环中检查 |
| 多线程共享变量 | RTOS 中多任务共享的标志位 |
| DMA 缓冲区 | DMA 传输完成后，缓冲区内容已被硬件修改 |

### 常见错误

```c
// 错误：对 volatile 变量做复合赋值（可能读写多次）
volatile int counter;
counter++;  // 实际是：read counter, add 1, write counter
            // 如果 read 和 write 之间被中断，可能丢更新

// 正确：用临时变量
int temp = counter;
temp++;
counter = temp;
```

---

## 内存映射 I/O（MMIO）

### 原理

外设寄存器被映射到 CPU 的地址空间，访问寄存器就是访问特定内存地址。

```
0x4000_0000 ─┐
             │  APB1 外设（低速）
0x4000_7FFF ─┤
             │  APB2 外设（高速）
0x4001_3FFF ─┤
             │  AHB1 外设（GPIO、DMA等）
0x5006_0FFF ─┘
```

### C 语言实现

```c
// 方法1：直接指针（最底层）
#define GPIOA_MODER  (*(volatile uint32_t *)0x40020000)
#define GPIOA_ODR    (*(volatile uint32_t *)0x40020014)

GPIOA_MODER |= (1 << 10);  // PA5 输出模式
GPIOA_ODR   |= (1 << 5);   // PA5 置高

// 方法2：结构体映射（STM32 HAL 风格）
typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} GPIO_TypeDef;

#define GPIOA  ((GPIO_TypeDef *)0x40020000)

GPIOA->MODER |= (1 << 10);
GPIOA->ODR   |= (1 << 5);
```

### 结构体映射的注意事项

- 结构体成员顺序必须与寄存器地址一一对应
- 必须使用 `volatile` 修饰每个成员
- 需要 `__attribute__((packed))` 或确认编译器不会插入填充（通常寄存器都是4字节对齐，不需要 packed）

---

## 结构体对齐与打包

### 对齐规则

编译器会在结构体成员之间插入填充字节，使每个成员的地址是其大小的整数倍：

```c
struct misaligned {
    char  a;    // offset 0, size 1
    // 3 bytes padding
    int   b;    // offset 4, size 4
    char  c;    // offset 8, size 1
    // 3 bytes padding
};  // total: 12 bytes
```

### 打包结构体

嵌入式中，网络协议帧或存储格式需要精确的内存布局：

```c
struct __attribute__((packed)) packet {
    uint8_t  header;    // offset 0
    uint16_t length;    // offset 1（不填充！）
    uint8_t  payload[]; // offset 3
};
```

**注意：** packed 结构体中，非对齐访问可能导致：
- ARM Cortex-M：非对齐访问可能触发 HardFault（取决于 SCB->CCR.UNALIGN_TRP 位）
- 性能下降：即使不触发异常，非对齐访问也需要多次总线事务

---

## 指针与类型转换

### 函数指针 — 向量表

Cortex-M 的向量表本质上是函数指针数组：

```c
typedef void (*ISR_t)(void);

__attribute__((section(".isr_vector")))
const ISR_t vector_table[] = {
    (ISR_t)&_estack,       // SP 初始值
    Reset_Handler,         // Reset
    NMI_Handler,           // NMI
    HardFault_Handler,     // HardFault
    // ...
};
```

### void* 与硬件抽象

```c
// 通用外设驱动：基地址 + 偏移
void write_reg(void *base, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)((uint32_t)base + offset) = value;
}

write_reg((void *)0x40020000, 0x14, (1 << 5));  // GPIOA->ODR |= (1<<5)
```

### 常见陷阱

```c
// 陷阱1：指针类型影响读取宽度
uint32_t *p32 = (uint32_t *)0x20000000;
uint8_t  *p8  = (uint8_t  *)0x20000000;
*p32 = 0x12345678;  // 写入4字节
*p8;                // 读取1字节 = 0x78（小端）

// 陷阱2：const 放置位置
const uint32_t *p;      // 指向常量的指针（*p 不可改，p 可改）
uint32_t * const p;     // 常量指针（p 不可改，*p 可改）
const uint32_t * const p; // 两者都不可改
```

---

## 中断安全编码

### 共享变量保护

```c
volatile int shared_flag = 0;

// 主循环
while (1) {
    // 关中断保护临界区
    __disable_irq();
    if (shared_flag) {
        shared_flag = 0;
        __enable_irq();
        // 处理事件
    } else {
        __enable_irq();
        // 等待
    }
}

// 中断服务程序
void EXTI0_IRQHandler(void) {
    shared_flag = 1;
    // 清中断标志...
}
```

### 关中断的替代方案

- **原子操作**：Cortex-M 的 `LDREX`/`STREX` 指令实现无锁操作
- **编译器屏障**：`__asm__ volatile("" ::: "memory")` 防止编译器重排序
- **硬件屏障**：`__DSB()` / `__ISB()` 确保内存访问完成

---

> 来源：通用知识
> 另见：[[NumberSystems_Encoding]], [[Endianness]]
