
import time
from machine import I2C, Pin
from ina219_sensor import INA219_ADDR, INA219Reader

# Conforme sua montagem: SDA = GPIO21, SCL = GPIO22
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

dispositivos = i2c.scan()
print("Enderecos I2C encontrados:", [hex(d) for d in dispositivos])

if INA219_ADDR not in dispositivos:
    raise RuntimeError("INA219 nao encontrado. Confira 3V3, GND, GPIO21 (SDA) e GPIO22 (SCL).")

sensor = INA219Reader(i2c)

# Para testar rapido, use 10 * 1000 (10s). Depois deixe 6 * 60 * 1000 (6 min = 360.000 ms).
INTERVALO_MS = 10 * 1000
ultima_leitura = time.ticks_ms() - INTERVALO_MS

while True:
    agora = time.ticks_ms()
    if time.ticks_diff(agora, ultima_leitura) >= INTERVALO_MS:
        ultima_leitura = agora

        tensao_v = sensor.ler_tensao_v()
        corrente_ma = sensor.ler_corrente_ma()

        print("Tensao: {:.3f} V | Corrente: {:.2f} mA".format(tensao_v, corrente_ma))

    time.sleep_ms(200)
