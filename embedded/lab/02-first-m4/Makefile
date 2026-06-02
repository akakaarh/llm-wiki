# STM32MP157 M4 裸机工程 Makefile

PREFIX  = arm-none-eabi-
CC      = $(PREFIX)gcc
AS      = $(PREFIX)gcc -x assembler-with-cpp
OBJCOPY = $(PREFIX)objcopy
OBJDUMP = $(PREFIX)objdump
SIZE    = $(PREFIX)size

# 芯片参数
CPU   = -mcpu=cortex-m4
FPU   = -mfpu=fpv4-sp-d16
FLOAT = -mfloat-abi=hard
MCU   = $(CPU) -mthumb $(FPU) $(FLOAT)

TARGET = first-m4

# 源文件
C_SOURCES   = src/main.c src/system_stm32mp1xx.c
ASM_SOURCES = src/startup.s
C_INCLUDES  = -Isrc
LDSCRIPT    = stm32mp157_m4.ld

# 编译/链接选项
CFLAGS  = $(MCU) $(C_INCLUDES) -Wall -ffreestanding -nostdlib -Os
ASFLAGS = $(MCU) -Wall -ffreestanding -nostdlib
LDFLAGS = $(MCU) -T $(LDSCRIPT) -nostdlib -Wl,--gc-sections

BUILD_DIR = build

# 自动计算 .o 文件列表
OBJECTS  = $(addprefix $(BUILD_DIR)/, $(notdir $(C_SOURCES:.c=.o)))
OBJECTS += $(addprefix $(BUILD_DIR)/, $(notdir $(ASM_SOURCES:.s=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))

# 默认目标
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).bin
	$(SIZE) $(BUILD_DIR)/$(TARGET).elf

# 链接：所有 .o → .elf
$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(LDFLAGS) -o $@ $^

# 生成 .bin
$(BUILD_DIR)/$(TARGET).bin: $(BUILD_DIR)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $@

# 编译：.c → .o
$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# 汇编：.s → .o
$(BUILD_DIR)/%.o: %.s
	@mkdir -p $(BUILD_DIR)
	$(AS) $(ASFLAGS) -c $< -o $@

# 清理
clean:
	rm -rf $(BUILD_DIR)

# 反汇编（调试用）
disasm: $(BUILD_DIR)/$(TARGET).elf
	$(OBJDUMP) -d $< > $(BUILD_DIR)/$(TARGET).dis

.PHONY: all clean disasm
