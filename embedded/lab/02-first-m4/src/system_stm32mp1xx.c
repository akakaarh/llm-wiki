/**
 * 最简系统初始化（M4 裸机用）
 * 后面用 HAL 库时再替换为 SDK 的完整版本
 */

#include <stdint.h>

/* 系统时钟频率（M4 默认 209MHz，暂不配置） */
uint32_t SystemCoreClock = 64000000U;

/**
 * @brief  系统初始化
 *         启动文件的 Reset_Handler 会调用此函数
 *         目前只做最基本的设置
 */
void SystemInit(void)
{
    /* FPU 使能（Cortex-M4 有硬件浮点单元） */
    /* SCB->CPACR: 设置 CP10 和 CP11 为完全访问 */
    *((volatile uint32_t *)0xE000ED88U) |= ((3U << 20) | (3U << 22));

    /* 暂不配置时钟，使用默认值 */
}

/**
 * @brief  更新系统时钟变量
 *         目前为空实现
 */
void SystemCoreClockUpdate(void)
{
    /* 暂不实现 */
}
