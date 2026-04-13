import network
from umqtt.simple import MQTTClient
import machine
from machine import Pin
import dht
from hcsr04 import HCSR04
import time
import json

SSID = "sua-rede"
SENHA = "sua-senha"
BROKER = "test.mosquitto.org"
PORTA = 1883
CLIENT_ID = "caua-da-massa2"
    

TOPICO_PUBLICAR = "pucpr/sensor_dht/dados"
TOPICO2_PUBLICAR = "pucpr/sensor_hcsr/dados"
TOPICO_ASSINAR = "pucpr/pc/comandos"

sensor = dht.DHT11(Pin(23))
sensor_hcsr = HCSR04(trigger_pin=26, echo_pin=32, echo_timeout_us=10000)
buzzer = Pin(15, Pin.OUT)
led = machine.Pin(2, Pin.OUT)

led_estado = False
buzzer_estado = False
publicado = True

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

def callback_mensagem(topico, mensagem):
    global led_estado
    global buzzer_estado
    global publicado
    topico = topico.decode("utf-8")
    payload = mensagem.decode("utf-8")
    print(f"[MICRO] Recebido em '{topico}': {payload}")
    
    try:
        dados = json.loads(payload)
        comando = dados.get("comando", "")
        status_entrega = dados.get("status", "")
        
        if status_entrega == "mensagem_rece_bida":
            publicado = True
            print("[MICRO] Dados entregues!")
            
        if comando == "led_on":
            led.value(1)
            led_estado = True
            print("[MICRO] LED ligado!")
            publicar_estado_led()
        elif comando == "led_off":
            led.value(0)
            led_estado = False
            print("[MICRO] LED desligado!")
            publicar_estado_led()
        elif comando == "buzzer_on":
            buzzer.value(1)
            buzzer_estado = True
            print("[MICRO] BUZZER ligado!")
            publicar_estado_buzzer()
        elif comando == "buzzer_off":
            buzzer.value(0)
            buzzer_estado = False
            print("[MICRO] BUZZER desligado!")
            publicar_estado_buzzer()
        elif comando == "status":
            publicar_dados_sensor()	
            publicar_dados_hcsr04()
            
        else:
            print(f"[MICRO] Comando desconhecido: {comando}")
    except Exception as e:
        print(f"[MICRO] Erro ao processar: {e}")

def publicar_estado_led():
    global publicado
    publicado = False
    estado = "ligado" if led_estado else "desligado"
    msg = json.dumps({"led": estado})
    client.publish(TOPICO_PUBLICAR, msg, qos=1)
    print(f"[MICRO] Publicado: {msg}")
    
def publicar_estado_buzzer():
    global publicado
    publicado = False
    estado = "ligado" if buzzer_estado else "desligado"
    msg = json.dumps({"buzzer": estado})
    client.publish(TOPICO_PUBLICAR, msg, qos=1)
    print(f"[MICRO] Publicado: {msg}")
    
def medir_distancia():
    distancia = sensor_hcsr.distance_cm() 
    return distancia

def publicar_dados_hcsr04():
    dados = {"distancia": medir_distancia()}
    msg = json.dumps(dados)
    client.publish(TOPICO2_PUBLICAR, msg, qos=1)
    print(f"[MICRO] Dados publicados: {msg}")
    
def publicar_dados_sensor():
    global publicado
    publicado = False
    sensor.measure()
    dados = {
        "temperatura": sensor.temperature(),
        "umidade": sensor.humidity(),
        "led": "ligado" if led_estado else "desligado"
    }
    msg = json.dumps(dados)
    client.publish(TOPICO_PUBLICAR, msg, qos=1)
    print(f"[MICRO] Dados publicados: {msg}")

if not conectar_wifi():
    print("Abortando: sem Wi-Fi.")
    raise SystemExit

print("[MICRO] Conectando ao broker MQTT...")
client = MQTTClient(CLIENT_ID, BROKER, port=PORTA)
client.set_callback(callback_mensagem)
client.connect()
print(f"[MICRO] Conectado a {BROKER}")

client.subscribe(TOPICO_ASSINAR, qos=1)
print(f"[MICRO] Inscrito em: {TOPICO_ASSINAR}")
print("[MICRO] Aguardando comandos...\n")

contador = 0
try:
    while True:
        client.check_msg()
        contador += 1
        if contador >= 30:
            publicar_dados_sensor()
            publicar_dados_hcsr04()
            contador = 0
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[MICRO] Interrompido pelo usuario.")
finally:
    client.disconnect()
    print("[MICRO] Desconectado do broker.")
