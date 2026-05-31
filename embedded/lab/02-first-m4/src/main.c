/**
 * M4 裸机程序：蜂鸣器闪烁
 * 功能：控制 PC7 (BEEP) 闪烁
 * 方式：直接操作寄存器，不使用 HAL 库
 *
 * PC7 = 蜂鸣器，Linux 触发器为 none，M4 可以独占控制。
 */

/* STM32MP157 外设基地址 */
#define RCC_BASE        0x50000000UL
#define GPIOC_BASE      0x50004000UL

/* RCC 寄存器 */
#define RCC_MP_AHB4ENSETR   (*(volatile unsigned int *)(RCC_BASE + 0xA28))

/* GPIOC 寄存器 */
#define GPIOC_MODER     (*(volatile unsigned int *)(GPIOC_BASE + 0x00))
#define GPIOC_OTYPER    (*(volatile unsigned int *)(GPIOC_BASE + 0x04))
#define GPIOC_OSPEEDR   (*(volatile unsigned int *)(GPIOC_BASE + 0x08))
#define GPIOC_PUPDR     (*(volatile unsigned int *)(GPIOC_BASE + 0x0C))
#define GPIOC_ODR       (*(volatile unsigned int *)(GPIOC_BASE + 0x14))

/* GPIOC 时钟使能位（bit 2） */
#define RCC_GPIOC_EN    (1UL << 2)

/* 简单延时 */
static void delay(volatile unsigned int count)
{
    while (count--)
    {
        __asm__("nop");
    }
}

int main(void)
{
    /* 第 1 步：使能 GPIOC 时钟 */
    RCC_MP_AHB4ENSETR = RCC_GPIOC_EN;

    /* 第 2 步：配置 PC7 为输出模式
     * PC7 = pin 7，所以看 bit[15:14]
     * 01 = 通用输出模式 */
    GPIOC_MODER &= ~(3UL << 14);
    GPIOC_MODER |=  (1UL << 14);

    /* 第 3 步：推挽输出 */
    GPIOC_OTYPER &= ~(1UL << 7);

    /* 第 4 步：高速 */
    GPIOC_OSPEEDR |= (3UL << 14);

    /* 第 5 步：无上下拉 */
    GPIOC_PUPDR &= ~(3UL << 14);

    /* 第 6 步：蜂鸣器闪烁主循环 */
    while (1)
    {
        GPIOC_ODR |=  (1UL << 7);  /* PC7 高电平，蜂鸣器响 */
        delay(5000000);

        GPIOC_ODR &= ~(1UL << 7);  /* PC7 低电平，蜂鸣器停 */
        delay(5000000);
    }

    return 0;
}
