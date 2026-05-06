#ifndef MODBUS_RTU_H
#define MODBUS_RTU_H

#include <stdint.h>

// Modbus RTU 帧最大长度
#define MODBUS_RTU_MAX_FRAME_LEN 256

// Modbus 功能码
typedef enum {
    MODBUS_FUNC_READ_COILS         = 0x01,
    MODBUS_FUNC_READ_DISCRETE      = 0x02,
    MODBUS_FUNC_READ_HOLDING       = 0x03,
    MODBUS_FUNC_READ_INPUT         = 0x04,
    MODBUS_FUNC_WRITE_SINGLE_COIL = 0x05,
    MODBUS_FUNC_WRITE_SINGLE_REG   = 0x06,
    MODBUS_FUNC_WRITE_MULTI_COILS  = 0x0F,
    MODBUS_FUNC_WRITE_MULTI_REGS   = 0x10,
} ModbusFuncCode;

// Modbus RTU 句柄
typedef struct {
    uint8_t  slave_addr;           // 从机地址
    uint8_t  tx_buf[MODBUS_RTU_MAX_FRAME_LEN];
    uint8_t  rx_buf[MODBUS_RTU_MAX_FRAME_LEN];
    uint16_t tx_len;               // 发送长度
    uint16_t rx_len;               // 接收长度
    uint32_t baudrate;             // 波特率
    uint32_t timeout_ms;           // 响应超时 ms
    uint32_t frame_gap_ms;         // 帧间隔（3.5T）
} ModbusRTU_HandleTypeDef;

// 错误码
typedef enum {
    MODBUS_OK           = 0,
    MODBUS_ERR_CRC      = 1,
    MODBUS_ERR_TIMEOUT  = 2,
    MODBUS_ERR_FRAME    = 3,
    MODBUS_ERR_PARAM    = 4,
} ModbusErr;

// ============ 初始化 ============
void ModbusRTU_Init(ModbusRTU_HandleTypeDef *hmodbus, uint8_t slave_addr, uint32_t baudrate);

// ============ 发送接口 ============
ModbusErr ModbusRTU_SendReadHoldingRegisters(ModbusRTU_HandleTypeDef *hmodbus, uint16_t start_addr, uint16_t count);
ModbusErr ModbusRTU_SendWriteSingleRegister(ModbusRTU_HandleTypeDef *hmodbus, uint16_t reg_addr, uint16_t value);
ModbusErr ModbusRTU_SendWriteMultipleRegisters(ModbusRTU_HandleTypeDef *hmodbus, uint16_t start_addr, uint16_t count, const uint16_t *data);

// ============ CRC ============
uint16_t ModbusRTU_CalcCRC16(const uint8_t *data, uint16_t len);

#endif
