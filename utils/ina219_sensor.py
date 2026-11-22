INA219_ADDR = 0x40
REG_CONFIG = 0x00
REG_BUS_VOLTAGE = 0x02
REG_CURRENT = 0x04
REG_CALIBRATION = 0x05

SHUNT_OHMS = 0.1  # Resistor R100 na placa do INA219


class INA219Reader:
    def __init__(self, i2c, addr=INA219_ADDR, shunt_ohms=SHUNT_OHMS):
        self.i2c = i2c
        self.addr = addr
        self.shunt_ohms = shunt_ohms
        self.current_lsb = 0.0001  # 100 uA por passo
        self._configurar()

    def _write_u16(self, reg, val):
        data = bytes([(val >> 8) & 0xFF, val & 0xFF])
        self.i2c.writeto_mem(self.addr, reg, data)

    def _read_s16(self, reg):
        raw = self.i2c.readfrom_mem(self.addr, reg, 2)
        val = (raw[0] << 8) | raw[1]
        if val & 0x8000:
            val -= 0x10000
        return val

    def _configurar(self):
        self._write_u16(REG_CONFIG, 0x399F)
        cal = int(0.04096 / (self.current_lsb * self.shunt_ohms))
        self._write_u16(REG_CALIBRATION, cal)

    def ler_tensao_v(self):
        raw = self.i2c.readfrom_mem(self.addr, REG_BUS_VOLTAGE, 2)
        bus_raw = (raw[0] << 8) | raw[1]
        return (bus_raw >> 3) * 0.004

    def ler_corrente_ma(self):
        raw_curr = self._read_s16(REG_CURRENT)
        return (raw_curr * self.current_lsb) * 1000.0