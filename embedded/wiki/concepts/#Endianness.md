---
type: concept
tags: [endianness, byte-order, memory-layout, arm]
---

# 大小端（Endianness）

多字节数据在内存中的字节排列顺序。ARM 架构支持两种模式，嵌入式开发中必须理解大小端对寄存器访问、网络通信和文件格式的影响。

---

## 基本概念

### 大端（Big-Endian）

高位字节存储在低地址。

```
值 0x12345678 存储在地址 0x1000：

地址:  0x1000  0x1001  0x1002  0x1003
数据:  0x12    0x34    0x56    0x78
       ↑ 高位字节在前
```

人类阅读习惯是大端。网络协议（TCP/IP）使用大端（也叫网络字节序）。

### 小端（Little-Endian）

低位字节存储在低地址。

```
值 0x12345678 存储在地址 0x1000：

地址:  0x1000  0x1001  0x1002  0x1003
数据:  0x78    0x56    0x34    0x12
       ↑ 低位字节在前
```

ARM Cortex-M 默认使用小端。x86 也是小端。大多数嵌入式系统使用小端。

---

## 为什么大小端重要

### 1. 寄存器位域与字节序

```c
// 假设某寄存器地址 0x40000000，32-bit 值 0x0000_00FF
// 读取该地址的单字节：
uint8_t byte = *(volatile uint8_t *)0x40000000;
// 小端：byte = 0xFF（低字节在低地址）
// 大端：byte = 0x00（高字节在低地址）
```

### 2. 多字节寄存器访问

```c
// 16-bit 寄存器，值 0xABCD
volatile uint16_t *reg = (volatile uint16_t *)0x40000000;

// 用字节指针访问
uint8_t low  = ((volatile uint8_t *)0x40000000)[0];  // 小端: 0xCD
uint8_t high = ((volatile uint8_t *)0x40000000)[1];  // 小端: 0xAB
```

### 3. 网络通信

```c
// 网络协议用大端，ARM 用小端，需要转换
uint16_t port = 8080;           // 0x1F90
uint16_t net_port = htons(port); // 0x901F（大端表示）

// htons = Host TO Network Short
// htonl = Host TO Network Long (32-bit)
// ntohs = Network TO Host Short
// ntohl = Network TO Host Long
```

### 4. 文件格式

| 格式 | 字节序 | 说明 |
|------|--------|------|
| ELF | 与目标架构一致 | ELF 头中有 `e_ident[EI_DATA]` 标识 |
| BMP | 小端 | Windows 格式 |
| JPEG | 大端 | 网络格式 |
| PNG | 大端 | 网络格式 |
| FAT32 | 小端 | 存储格式 |

---

## ARM 的字节序支持

### Cortex-M

- 默认**小端**
- 部分 Cortex-M 核心支持大端配置（通过 AIRCR.ENDIANNESS 位），但实际产品几乎不用
- ARMv8-M（Cortex-M23/M33/M55）固定小端

### Cortex-A

- 支持大端和小端，通过 CP15 的 SCTLR.E 位切换
- Linux 内核可以编译为大端或小端模式
- Android 设备通常使用小端

### 混合字节序（Bi-Endian）

少数 ARM 核心支持运行时切换字节序，但实际开发中极少遇到。

---

## C 语言中的字节序处理

### 检测当前字节序

```c
int is_little_endian(void) {
    uint32_t val = 1;
    return *(uint8_t *)&val == 1;  // 低地址存的是低字节
}
```

### 字节序转换

```c
// 手动实现 htonl
uint32_t htonl(uint32_t host) {
    return ((host & 0xFF000000) >> 24) |
           ((host & 0x00FF0000) >> 8)  |
           ((host & 0x0000FF00) << 8)  |
           ((host & 0x000000FF) << 24);
}

// 使用编译器内置函数（GCC）
uint32_t val = __builtin_bswap32(0x12345678);  // 0x78563412
uint16_t val = __builtin_bswap16(0x1234);      // 0x3412
```

### 结构体与字节序

```c
// 网络协议头（大端）
struct __attribute__((packed)) ip_header {
    uint8_t  ver_ihl;
    uint8_t  tos;
    uint16_t total_length;  // 大端存储
    uint16_t id;            // 大端存储
    // ...
};

// 读取时需要转换
uint16_t len = ntohs(header->total_length);
```

---

## 调试技巧

### 内存查看

```
# GDB 查看内存（以字节显示）
(gdb) x/4bx 0x20000000
0x20000000: 0x78  0x56  0x34  0x12   ← 小端存储 0x12345678

# 以半字显示
(gdb) x/2hx 0x20000000
0x20000000: 0x5678  0x1234
```

### 常见错误

```c
// 错误：假设大端
uint32_t val = 0x12345678;
uint8_t *p = (uint8_t *)&val;
if (p[0] == 0x12) { /* 只在大端成立 */ }

// 正确：用位操作提取字节
uint8_t byte0 = val & 0xFF;          // 总是得到 0x78
uint8_t byte3 = (val >> 24) & 0xFF;  // 总是得到 0x12
```

---

> 来源：通用知识
> 另见：[[EmbeddedC_BitManipulation]], [[NumberSystems_Encoding]]
