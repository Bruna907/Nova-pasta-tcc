import time

class INA219:
    def __init__(self, i2c, addr=0x40):
        self.i2c = i2c
        self.addr = addr
        # Calibração padrão (32V, 2A) com resistor shunt de 0.1 ohm
        self._write_register(0x05, 4096)
        # Configuração: 32V range, ganho 320mV, ADC 12-bit, modo contínuo
        self._write_register(0x00, 0x399F)

    def _write_register(self, reg, value):
        data = bytearray([(value >> 8) & 0xFF, value & 0xFF])
        self.i2c.writeto_mem(self.addr, reg, data)

    def _read_register(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        value = (data[0] << 8) | data[1]
        if value > 32767:
            value -= 65536
        return value

    def tensao_bus(self):
        # Retorna a tensão em Volts (V)
        raw = self.i2c.readfrom_mem(self.addr, 0x02, 2)
        value = ((raw[0] << 8) | raw[1]) >> 3
        return value * 0.004

    def tensao_shunt(self):
        # Retorna a queda de tensão no resistor shunt em mV
        return self._read_register(0x01) * 0.01

    def corrente_ma(self):
        # Retorna a corrente em miliamperes (mA)
        return self._read_register(0x04) * 0.1

    #Fim