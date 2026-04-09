# main.py - Aplicacao MQTT no microcontrolador
# Execute este arquivo pelo Thonny (Run > Run current script)

import network
from umqtt.simple import MQTTClient
import machine
from machine import Pin
import dht
import time
import json
from machine import Pin
import time


# ==== CONFIGURACOES - ALTERE AQUI ====
SSID = "Visitantes"           # <-- Wi-Fi: nome da rede
SENHA = ""         # <-- Wi-Fi: senha
BROKER = "test.mosquitto.org"
PORTA = 1883
CLIENT_ID = "caua-da-massa2"           # Use seu RA para evitar conflito

TOPICO_PUBLICAR = "pucpr/micro/dados"   # Micro publica aqui
TOPICO_ASSINAR = "pucpr/pc/comandos"    # Micro recebe daqui

TOPICO2_PUBLICAR = "pucpr/micro2/dados"   # Micro publica aqui
TOPICO2_ASSINAR = "pucpr/pc2/comandos"    # Micro recebe daqui

sensor = dht.DHT11(Pin(23))
trig = Pin(28, Pin.OUT)
echo = Pin(32, Pin.IN)
button = Pin(14, Pin.IN, Pin.PULL_UP)
led1 = Pin(15, Pin.machine.Pin.OUT)
buzzer = Pin(17, Pin.OUT)

# LED integrado (ajuste o pino conforme sua placa)
# ESP32: pino 2 | Pico W: pino "LED" | ESP8266: pino 2
led = machine.Pin(2, machine.Pin.OUT)
led_estado = False

# ---- Conexao Wi-Fi ----
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(SSID, SENHA)
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1)
            tentativas += 1
            print(f" Tentativa {tentativas}/20...")
    if wlan.isconnected():
        print(f"Wi-Fi conectado! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("ERRO: Nao foi possivel conectar ao Wi-Fi")
        return False

# ---- Callback de mensagens recebidas ----
def callback_mensagem(topico, mensagem):
    global led_estado
    topico = topico.decode("utf-8")
    payload = mensagem.decode("utf-8")
    print(f"[MICRO] Recebido em '{topico}': {payload}")
    
    try:
        dados = json.loads(payload)
        comando = dados.get("comando", "")
        if comando == "led_on":
            led.value(1)
            led_estado = True
            print("[MICRO] LED ligado!")
            publicar_estado()
        elif comando == "led_off":
            led.value(0)
            led_estado = False
            print("[MICRO] LED desligado!")
            publicar_estado()
        elif comando == "status":
            publicar_dados_sensor()
        else:
            print(f"[MICRO] Comando desconhecido: {comando}")
    except Exception as e:
        print(f"[MICRO] Erro ao processar: {e}")

# ---- Funcoes de publicacao ----
def publicar_estado():
    estado = "ligado" if led_estado else "desligado"
    msg = json.dumps({"led": estado})
    client.publish(TOPICO_PUBLICAR, msg)
    print(f"[MICRO] Publicado: {msg}")
    
def medir_distancia():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    while echo.value() == 0:
        pulse_start = time.ticks_us()
    while echo.value() == 1:
        pulse_end = time.ticks_us()

    pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    distancia = (pulse_duration / 2) * 0.0343
    return distancia


def publicar_dados_button_hcsr04():
    if button.value() == 1:
        dados = {
            "distancia": medir_distancia()
        }
        led1.value(1)
        buzzer.value(1)
        comando = {
            "led":     
        }
        msg = json.dumps(dados)
        client.publish(TOPICO_PUBLICAR2, msg) #MUDAR
        print(f"[MICRO] Dados publicados: {msg}")
    led1.value(0)
    buzzer.value(0)
def publicar_dados_sensor():

    dados = {
        "temperatura": sensor.temperature(),
        "umidade": sensor.humidity(),
        "led": "ligado" if led_estado else "desligado"
    }
    msg = json.dumps(dados)
    client.publish(TOPICO_PUBLICAR, msg)
    print(f"[MICRO] Dados publicados: {msg}")

# ---- Conexao e loop principal ----
if not conectar_wifi():
    print("Abortando: sem Wi-Fi.")
    raise SystemExit

print("[MICRO] Conectando ao broker MQTT...")
client = MQTTClient(CLIENT_ID, BROKER, port=PORTA)
client.set_callback(callback_mensagem)
client.connect()
print(f"[MICRO] Conectado a {BROKER}")sensor.measure()
            publicar_dados_sensor()
            

client.subscribe(TOPICO_ASSINAR)
print(f"[MICRO] Inscrito em: {TOPICO_ASSINAR}")
print("[MICRO] Aguardando comandos...\n")

# Loop principal
contador = 0
try:
    while True:
        # Verifica novas mensagens (nao-bloqueante)
        client.check_msg()
        publicar_dados_button_hcsr04() # pra ficar verificando se ele ta apertando o botao (dentro da funcao) pra postar
        
        # A cada 30 segundos, publica dados automaticamente
        contador += 1
        if contador >= 30:
            sensor.measure()
            publicar_dados_sensor()
            contador = 0
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[MICRO] Interrompido pelo usuario.")
finally:
    client.disconnect()
    print("[MICRO] Desconectado do broker.")