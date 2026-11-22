import time
import network
from machine import I2C, Pin
from ina219_sensor import INA219_ADDR, INA219Reader

# Configuracao de Wi-Fi (use rede 2,4 GHz) e fuso horario (Brasil -03:00 = -10800 s)
WIFI_SSID = "SEU_WIFI"
WIFI_SENHA = "SUA_SENHA"
FUSO_HORARIO_SEG = -3 * 3600


def conectar_wifi(ssid, senha, timeout_s=15):
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.active(False)
        time.sleep_ms(200)
        wlan.active(True)
        time.sleep_ms(200)

        if wlan.isconnected():
            return True

        print("Conectando ao Wi-Fi...")
        wlan.connect(ssid, senha)
        inicio = time.time()
        while not wlan.isconnected():
            if time.time() - inicio > timeout_s:
                print("Aviso: nao conectou ao Wi-Fi no tempo limite.")
                return False
            time.sleep(0.5)

        print("Wi-Fi conectado! IP:", wlan.ifconfig()[0])
        return True
    except OSError as e:
        print("Aviso: erro interno no Wi-Fi:", e)
        return False


def sincronizar_hora_ntp(tentativas=3):
    import ntptime

    servidores = ("a.st1.ntp.br", "b.st1.ntp.br", "pool.ntp.org", "time.google.com")
    for _ in range(tentativas):
        for host in servidores:
            try:
                ntptime.host = host
                ntptime.settime()
                print("Hora sincronizada via NTP ({}).".format(host))
                return True
            except Exception:
                time.sleep_ms(500)

    print("Aviso: nao foi possivel sincronizar NTP (mantendo relogio local).")
    return False


def formatar_data_hora():
    t = time.localtime(time.time() + FUSO_HORARIO_SEG)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )


if conectar_wifi(WIFI_SSID, WIFI_SENHA):
    sincronizar_hora_ntp()

# Conforme sua montagem: SDA = GPIO21, SCL = GPIO22, GND comum[cite: 1]
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=50000)

dispositivos = i2c.scan()
print("Enderecos I2C encontrados:", [hex(d) for d in dispositivos])

if INA219_ADDR not in dispositivos:
    raise RuntimeError("INA219 nao encontrado. Confira 3V3, GND, GPIO21 (SDA) e GPIO22 (SCL).")[cite: 1]

sensor = INA219Reader(i2c)

# --- CONFIGURACAO DE INTERVALOS (em milissegundos) ---
# Ativo: 5 segundos = 5.000 ms
INTERVALO_MS = 5 * 1000

# Para usar 1 hora (3.600.000 ms), comente a linha de 5 segundos acima
# e descomente a linha abaixo:
# INTERVALO_MS = 60 * 60 * 1000  # 1 hora = 3.600.000 ms

# Referencia de 6 minutos (360.000 ms):
# INTERVALO_MS = 6 * 60 * 1000  # 6 minutos = 360.000 ms

ultima_leitura = time.ticks_ms() - INTERVALO_MS

while True:
    agora = time.ticks_ms()
    if time.ticks_diff(agora, ultima_leitura) >= INTERVALO_MS:
        ultima_leitura = agora

        data_hora = formatar_data_hora()
        tensao_v = sensor.ler_tensao_v()
        corrente_ma = sensor.ler_corrente_ma()
        potencia_w = sensor.ler_potencia_w(tensao_v, corrente_ma)
        potencia_mw = potencia_w * 1000.0

        print(
            "[{}] Tensao: {:.3f} V | Corrente: {:.2f} mA | Potencia: {:.3f} W ({:.1f} mW)".format(
                data_hora, tensao_v, corrente_ma, potencia_w, potencia_mw
            )
        )

    time.sleep_ms(200)
