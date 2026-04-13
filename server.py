
import paho.mqtt.client as mqtt
import time
import json

BROKER = "test.mosquitto.org"
PORTA = 1883
PREFIXO = "" #gere um UUID: python -c "import uuid; print(uuid.uuid4())"
TOPICO_PUBLICAR = f"{PREFIXO}/pc/comandos" 
TOPICO_ASSINAR = f"{PREFIXO}/+/dados" 
CLIENT_ID = "pc-pucpr-001"

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("[PC] Conectado ao broker MQTT!")
        client.subscribe(TOPICO_ASSINAR, qos=1)
    else:
        print(f"[PC] Falha na conexao, codigo: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"\n[PC] Mensagem recebida em '{msg.topic}': {payload}")
    
    try:
        dados = json.loads(payload)
        if "temperatura" in dados:
            print(f" -> Temperatura: {dados['temperatura']} C")
        if "umidade" in dados:
            print(f" -> Umidade: {dados['umidade']} %")
        if "distancia" in dados:
            print(f" -> Distância: {dados['distancia']:.2f} cm")
        if "led" in dados:
            print(f" -> Estado do LED: {dados['led']}")
        if "buzzer" in dados:
            print(f" -> Estado do BUZZER: {dados['buzzer']}")
    except json.JSONDecodeError:
        print(f" -> Dado em texto puro: {payload}")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"[PC] Desconectado do broker (rc={reason_code})")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print(f"[PC] Conectando a {BROKER}:{PORTA}...")
    client.connect(BROKER, PORTA, 60)
    client.loop_start()

    print("\n--- COMANDOS DISPONIVEIS ---")
    print(" led_on")
    print(" led_off")
    print(" buzzer_on")
    print(" buzzer_off")
    print(" status")
    print(" sair\n")

    try:
        while True:
            comando = input("[PC] Digite um comando: ").strip()
            if comando.lower() == "sair":
                break
            
            if comando:
                mensagem = json.dumps({"comando": comando})
                client.publish(TOPICO_PUBLICAR, mensagem, qos=1)
                print(f"[PC] Publicado: {mensagem}")
                
    except KeyboardInterrupt:
        print("\n[PC] Interrompido pelo usuario.")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[PC] Encerrado.")

if __name__ == "__main__":
    main()

