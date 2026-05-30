# ============================================================
# STM32MP157 M4 裸机工程 Makefile
# ============================================================

# ============================================================
# 第一部分：工具链定义
# ============================================================
# PREFIX 是工具链的公共前缀，后面拼上 gcc、objcopy 等就是完整命令
# arm-none-eabi-gcc = ARM架构 + 无操作系统 + 嵌入式ABI + GCC编译器
PREFIX = arm-none-eabi-

# CC = C语言编译器，把 .c 编译成 .o
CC     = $(PREFIX)gcc

# AS = 汇编器，把 .s 编译成 .o
# -x assembler-with-cpp 表示先走C预处理器（处理#define等），再汇编
AS     = $(PREFIX)gcc -x assembler-with-cpp

# OBJCOPY = 格式转换工具，把 .elf 转成 .bin（平面二进制）
OBJCOPY = $(PREFIX)objcopy

# OBJDUMP = 反汇编工具，把 .elf 反汇编成可读的汇编代码
OBJDUMP = $(PREFIX)objdump

# SIZE = 显示 .elf 各段大小（text/data/bss）
SIZE   = $(PREFIX)size

# ============================================================
# 第二部分：芯片型号定义
# ============================================================
# -mcpu=cortex-m4       告诉编译器：目标CPU是Cortex-M4
# -mfpu=fpv4-sp-d16     告诉编译器：有硬件浮点单元（FPU），单精度
# -mfloat-abi=hard      告诉编译器：浮点运算用硬件指令（不是软件模拟）
# -mthumb               告诉编译器：生成Thumb指令（16/32位混合，省空间）
CPU     = -mcpu=cortex-m4
FPU     = -mfpu=fpv4-sp-d16
FLOAT   = -mfloat-abi=hard
MCU     = $(CPU) -mthumb $(FPU) $(FLOAT)

# ============================================================
# 第三部分：目标文件名
# ============================================================
# 最终输出的文件叫 first-m4.elf 和 first-m4.bin
TARGET = first-m4

# ============================================================
# 第四部分：源文件列表
# ============================================================
# 这里列出所有要编译的 .c 和 .s 文件
# 加新文件时在这里加，比如：C_SOURCES += src/uart.c
C_SOURCES  = src/main.c src/system_stm32mp1xx.c
ASM_SOURCES = src/startup.s

# ============================================================
# 第五部分：头文件搜索路径
# ============================================================
# -Isrc 表示在 src/ 目录下找 #include 的头文件
# 后面用 HAL 库时要加 SDK 路径，比如：
# -I$(SDK)/Drivers/CMSIS/Include
C_INCLUDES = -Isrc

# ============================================================
# 第六部分：链接脚本
# ============================================================
# 链接脚本告诉链接器：代码放哪里，数据放哪里
LDSCRIPT = stm32mp157_m4.ld

# ============================================================
# 第七部分：编译/汇编/链接选项
# ============================================================
# CFLAGS = C编译选项
#   $(MCU)           芯片型号
#   $(C_INCLUDES)    头文件路径
#   -Wall            显示所有警告
#   -ffreestanding   裸机环境（不假设存在标准库）
#   -nostdlib        不链接标准库
#   -Os              优化体积（O = optimize, s = size）
CFLAGS  = $(MCU) $(C_INCLUDES) -Wall -ffreestanding -nostdlib -Os

# ASFLAGS = 汇编选项，和 CFLAGS 类似
ASFLAGS = $(MCU) -Wall -ffreestanding -nostdlib

# LDFLAGS = 链接选项
#   $(MCU)           芯片型号
#   -T $(LDSCRIPT)   使用指定的链接脚本
#   -nostdlib        不链接标准库
#   -Wl,--gc-sections 删除没用的代码段（garbage collect）
LDFLAGS = $(MCU) -T $(LDSCRIPT) -nostdlib -Wl,--gc-sections

# ============================================================
# 第八部分：构建目录
# ============================================================
# 所有编译产物放到 build/ 目录下
BUILD_DIR = build

# ============================================================
# 自动计算目标文件
# ============================================================
# OBJECTS 是所有 .o 文件的列表
# $(C_SOURCES:.c=.o) 把所有 .c 替换成 .o
# $(notdir ...)       去掉路径，只留文件名
# $(addprefix build/, ...) 加上 build/ 前缀
# 最终结果：build/main.o build/system_stm32mp1xx.o build/startup.o
OBJECTS  = $(addprefix $(BUILD_DIR)/, $(notdir $(C_SOURCES:.c=.o)))
OBJECTS += $(addprefix $(BUILD_DIR)/, $(notdir $(ASM_SOURCES:.s=.o)))

# vpath 告诉 Makefile 去哪里找源文件
# 因为 .o 文件在 build/，但源文件在 src/，需要告诉它去 src/ 找
vpath %.c $(sort $(dir $(C_SOURCES)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))

# ============================================================
# 默认目标：make 不带参数时执行这个
# ============================================================
# all 依赖于 .elf 和 .bin 文件
# Make 会自动去找怎么生成这两个文件（下面的规则）
# 最后用 SIZE 显示 .elf 的大小
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).bin
	$(SIZE) $(BUILD_DIR)/$(TARGET).elf

# ============================================================
# 链接规则：所有 .o → .elf
# ============================================================
# $(BUILD_DIR)/$(TARGET).elf 依赖于 $(OBJECTS)（所有 .o 文件）
# $@ = 目标文件（build/first-m4.elf）
# $^ = 所有依赖（build/main.o build/system_stm32mp1xx.o build/startup.o）
$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
	@mkdir -p $(BUILD_DIR)         # @ 表示不打印这行命令本身
	$(CC) $(LDFLAGS) -o $@ $^      # 链接：gcc + 链接选项 + 输出 + 输入
	@echo "链接完成: $@"

# ============================================================
# 生成 .bin 文件
# ============================================================
# .bin 依赖于 .elf（先有 .elf 才能转 .bin）
# $< = 第一个依赖（build/first-m4.elf）
# $@ = 目标文件（build/first-m4.bin）
# -O binary 输出格式是平面二进制
$(BUILD_DIR)/$(TARGET).bin: $(BUILD_DIR)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $@
	@echo "生成 bin: $@"

# ============================================================
# 编译规则：.c → .o
# ============================================================
# %.c 匹配任意 .c 文件
# -c 表示只编译不链接（生成 .o 而不是可执行文件）
$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@    # 编译：gcc + 选项 + 输入 -o 输出
	@echo "编译: $<"

# ============================================================
# 汇编规则：.s → .o
# ============================================================
# 和上面类似，只是用汇编器 AS
$(BUILD_DIR)/%.o: %.s
	@mkdir -p $(BUILD_DIR)
	$(AS) $(ASFLAGS) -c $< -o $@
	@echo "汇编: $<"

# ============================================================
# 清理规则
# ============================================================
# make clean 删除整个 build 目录
clean:
	rm -rf $(BUILD_DIR)
	@echo "已清理"

# ============================================================
# 反汇编规则（调试用）
# ============================================================
# make disasm 生成可读的汇编文件
disasm: $(BUILD_DIR)/$(TARGET).elf
	$(OBJDUMP) -d $< > $(BUILD_DIR)/$(TARGET).dis
	@echo "反汇编: $(BUILD_DIR)/$(TARGET).dis"

# ============================================================
# .PHONY 声明伪目标
# ============================================================
# all、clean、disasm 不是真正的文件名
# 声明为 PHONY 后，make 不会去检查有没有叫这些名字的文件
# 每次都执行
.PHONY: all clean disasm
