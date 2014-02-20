/**
 * Copyright (C) 2013-2014 Ivan Kravets <me@ikravets.com>
 * See LICENSE for details.
 */

#include "platform_tools.h"

void UARTInit(const uint16_t speed)
{
#ifdef ARDUINO
    Serial.begin(speed);
#endif
}

void UARTTransmitByte(uint8_t _byte)
{
#ifdef ARDUINO
    Serial.write(_byte);
#endif
}

int16_t UARTReceiveByte()
{
#ifdef ARDUINO
    return Serial.read();
#endif
}

void UARTPrintln(const char *data)
{
#ifdef ARDUINO
    Serial.println(data);
#endif
}

uint32_t getTimeMillis()
{
#ifdef ARDUINO
    return millis();
#endif
}

void configurePinMode(uint8_t pinNum, uint8_t value)
{
#ifdef ARDUINO
    return pinMode(pinNum, value);
#endif
}

uint8_t readDigitalPin(uint8_t pinNum)
{
#ifdef ARDUINO
    return digitalRead(pinNum);
#endif
}

void writeDigitalPin(uint8_t pinNum, uint8_t value)
{
#ifdef ARDUINO
    return digitalWrite(pinNum, value);
#endif
}
