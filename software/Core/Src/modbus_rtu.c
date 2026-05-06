#include "modbus_rtu.h"
#include "usart.h"   // HAL UART 接口

// 帧间隔时间（3.5T，1T = 1/baudrate * 11bit）
static uint32_t calc_frame_gap_ms(uint32_t baudrate)
{
    // 3.5T = 3.5 * 11 / baudrate * 1000 ms
    return (uint32_t)((35000UL * 11) / baudrate);
}

// 波特率对应的超时时间（经验值）
static uint32_t calc_timeout_ms(uint32_t baudrate)
{
    // 读单个寄存器：约 50ms + 传输时间
    return 100;
}

// ============ 初始化 ============
void ModbusRTU_Init(ModbusRTU_HandleTypeDef *hmodbus, uint8_t slave_addr, uint32_t baudrate)
{
    hmodbus->slave_addr   = slave_addr;
    hmodbus->baudrate     = baudrate;
    hmodbus->timeout_ms   = calc_timeout_ms(baudrate);
    hmodbus->frame_gap_ms = calc_frame_gap_ms(baudrate);
    hmodbus->tx_len       = 0;
    hmodbus->rx_len       = 0;
}

// ============ CRC16 ============
uint16_t ModbusRTU_CalcCRC16(const uint8_t *data, uint16_t len)
{
    uint16_t crc = 0xFFFF;
    while (len--) {
        crc ^= *data++;
        for (uint8_t i = 0; i < 8; i++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

static void modbus_send_frame(ModbusRTU_HandleTypeDef *hmodbus, uint16_t tx_len)
{
    hmodbus->tx_len = tx_len;
    // 阻塞式发送，TXE 中断 / DMA 在外层驱动
    HAL_UART_Transmit(&huart1, hmodbus->tx_buf, tx_len, hmodbus->timeout_ms);
}

// ============ 发送：读保持寄存器 (0x03) ============
ModbusErr ModbusRTU_SendReadHoldingRegisters(ModbusRTU_HandleTypeDef *hmodbus,
                                              uint16_t start_addr, uint16_t count)
{
    uint8_t *buf = hmodbus->tx_buf;
    buf[0] = hmodbus->slave_addr;
    buf[1] = MODBUS_FUNC_READ_HOLDING;
    buf[2] = (uint8_t)(start_addr >> 8);
    buf[3] = (uint8_t)(start_addr & 0xFF);
    buf[4] = (uint8_t)(count >> 8);
    buf[5] = (uint8_t)(count & 0xFF);

    uint16_t crc = ModbusRTU_CalcCRC16(buf, 6);
    buf[6] = (uint8_t)(crc & 0xFF);
    buf[7] = (uint8_t)(crc >> 8);

    modbus_send_frame(hmodbus, 8);
    return MODBUS_OK;
}

// ============ 发送：写单个寄存器 (0x06) ============
ModbusErr ModbusRTU_SendWriteSingleRegister(ModbusRTU_HandleTypeDef *hmodbus,
                                             uint16_t reg_addr, uint16_t value)
{
    uint8_t *buf = hmodbus->tx_buf;
    buf[0] = hmodbus->slave_addr;
    buf[1] = MODBUS_FUNC_WRITE_SINGLE_REG;
    buf[2] = (uint8_t)(reg_addr >> 8);
    buf[3] = (uint8_t)(reg_addr & 0xFF);
    buf[4] = (uint8_t)(value >> 8);
    buf[5] = (uint8_t)(value & 0xFF);

    uint16_t crc = ModbusRTU_CalcCRC16(buf, 6);
    buf[6] = (uint8_t)(crc & 0xFF);
    buf[7] = (uint8_t)(crc >> 8);

    modbus_send_frame(hmodbus, 8);
    return MODBUS_OK;
}

// ============ 发送：写多个寄存器 (0x10) ============
ModbusErr ModbusRTU_SendWriteMultipleRegisters(ModbusRTU_HandleTypeDef *hmodbus,
                                                uint16_t start_addr, uint16_t count,
                                                const uint16_t *data)
{
    uint8_t *buf = hmodbus->tx_buf;
    buf[0] = hmodbus->slave_addr;
    buf[1] = MODBUS_FUNC_WRITE_MULTI_REGS;
    buf[2] = (uint8_t)(start_addr >> 8);
    buf[3] = (uint8_t)(start_addr & 0xFF);
    buf[4] = (uint8_t)(count >> 8);
    buf[5] = (uint8_t)(count & 0xFF);
    buf[6] = (uint8_t)(count * 2);   // 字节计数

    for (uint16_t i = 0; i < count; i++) {
        buf[7 + i * 2]     = (uint8_t)(data[i] >> 8);
        buf[8 + i * 2]     = (uint8_t)(data[i] & 0xFF);
    }

    uint16_t crc = ModbusRTU_CalcCRC16(buf, 7 + count * 2);
    buf[7 + count * 2]     = (uint8_t)(crc & 0xFF);
    buf[8 + count * 2]     = (uint8_t)(crc >> 8);

    modbus_send_frame(hmodbus, 9 + count * 2);
    return MODBUS_OK;
}
