# ESP32 IoT Control System

Sistema de comunicação, monitoramento e controle de dispositivos IoT baseado em **ESP32**, **MicroPython** e **MQTT**.

O projeto utiliza uma arquitetura orientada a eventos na qual o ESP32 coleta dados de sensores e controla atuadores, enquanto um computador atua como servidor central para receber os dados e enviar comandos remotamente através de um broker MQTT.

## 📌 Visão geral

A solução é composta por três elementos principais:

```text
┌─────────────────────┐
│       ESP32         │
│                     │
│  DHT11              │
│  HC-SR04            │
│  LED                │
│  Buzzer             │
└──────────┬──────────┘
           │
           │ MQTT
           ▼
┌─────────────────────┐
│    MQTT Broker      │
│                     │
│ test.mosquitto.org  │
└──────────┬──────────┘
           │
           │ MQTT
           ▼
┌─────────────────────┐
│   Servidor Python   │
│                     │
│ Monitoramento       │
│ Controle            │
│ Processamento       │
└─────────────────────┘
```

O ESP32 publica periodicamente informações dos sensores e dos atuadores. O servidor pode receber essas informações e enviar comandos para controlar o LED e o buzzer.

## ✨ Funcionalidades

### Monitoramento

* 🌡️ Leitura de temperatura através do **DHT11**
* 💧 Leitura de umidade através do **DHT11**
* 📏 Medição de distância através do **HC-SR04**
* 💡 Monitoramento do estado do LED
* 🔊 Monitoramento do estado do buzzer

### Controle

O servidor pode enviar comandos MQTT para o ESP32:

* `led_on` — liga o LED
* `led_off` — desliga o LED
* `buzzer_on` — liga o buzzer
* `buzzer_off` — desliga o buzzer
* `status` — solicita os dados atuais dos sensores

## 🛠️ Tecnologias utilizadas

| Tecnologia     | Utilização                        |
| -------------- | --------------------------------- |
| ESP32          | Microcontrolador                  |
| MicroPython    | Firmware do ESP32                 |
| Python         | Servidor de controle              |
| MQTT           | Comunicação entre os dispositivos |
| `umqtt.simple` | Cliente MQTT no ESP32             |
| Paho MQTT      | Cliente MQTT no servidor          |
| DHT11          | Temperatura e umidade             |
| HC-SR04        | Distância                         |

## 📂 Estrutura do projeto

```text
esp32-iot-control-system/
│
├── main.py
├── server.py
└── README.md
```

### `main.py`

Firmware executado no ESP32.

Responsável por:

* conectar o ESP32 à rede Wi-Fi;
* conectar ao broker MQTT;
* publicar dados dos sensores;
* receber comandos MQTT;
* controlar LED e buzzer;
* publicar o estado dos atuadores.

### `server.py`

Aplicação executada no computador.

Responsável por:

* conectar ao broker MQTT;
* receber dados enviados pelo ESP32;
* exibir as informações no terminal;
* enviar comandos de controle ao ESP32.

## 🔌 Hardware

O projeto utiliza os seguintes GPIOs:

| Componente      |    GPIO |
| --------------- | ------: |
| DHT11           | GPIO 23 |
| HC-SR04 Trigger | GPIO 26 |
| HC-SR04 Echo    | GPIO 32 |
| Buzzer          | GPIO 15 |
| LED             |  GPIO 2 |

> **Atenção:** o pino `Echo` do HC-SR04 pode operar em tensão superior ao nível lógico de 3,3 V do ESP32 dependendo do módulo utilizado. Utilize um divisor de tensão ou outro método apropriado de adaptação de nível quando necessário.

## 📡 Comunicação MQTT

O projeto utiliza atualmente:

```text
Broker: test.mosquitto.org
Porta: 1883
QoS: 1
```

### Tópicos

Os tópicos utilizados pelo sistema são:

```text
<prefixo>/sensor_dht/dados
<prefixo>/sensor_hcsr/dados
<prefixo>/led/dados
<prefixo>/buzzer/dados
<prefixo>/pc/comandos
```

O `PREFIXO` pode ser utilizado para separar diferentes dispositivos dentro do mesmo broker.

### Dados do DHT11

Exemplo de mensagem:

```json
{
  "temperatura": 25,
  "umidade": 60,
  "led": "desligado"
}
```

### Dados do HC-SR04

```json
{
  "distancia": 35.42
}
```

### Estado do LED

```json
{
  "led": "ligado"
}
```

### Estado do buzzer

```json
{
  "buzzer": "desligado"
}
```

### Comandos

Os comandos enviados ao ESP32 seguem o formato:

```json
{
  "comando": "led_on"
}
```

Exemplo para desligar o buzzer:

```json
{
  "comando": "buzzer_off"
}
```

## 🚀 Instalação

### 1. Clone o projeto

```bash
git clone https://github.com/vMigliorini/esp32-iot-control-system.git

cd esp32-iot-control-system
```

## ⚙️ Configuração do ESP32

O ESP32 deve possuir **MicroPython** instalado.

O firmware utiliza as seguintes bibliotecas:

```python
import network
from umqtt.simple import MQTTClient
import machine
from machine import Pin
import dht
from hcsr04 import HCSR04
```

Configure suas credenciais de Wi-Fi no `main.py`:

```python
SSID = "sua_rede_aqui"
SENHA = "sua_senha_aqui"
```

Também é possível configurar o broker MQTT:

```python
BROKER = "test.mosquitto.org"
PORTA = 1883
```

### Identificação do dispositivo

Para evitar colisões entre dispositivos utilizando o mesmo broker, recomenda-se configurar um prefixo único:

```python
PREFIXO = "esp32-001"
```

Por exemplo:

```text
esp32-001/sensor_dht/dados
esp32-001/sensor_hcsr/dados
esp32-001/led/dados
esp32-001/buzzer/dados
esp32-001/pc/comandos
```

Uma opção é gerar um UUID:

```bash
python -c "import uuid; print(uuid.uuid4())"
```

## 🖥️ Instalação do servidor

O servidor utiliza Python e a biblioteca **Paho MQTT**.

Instale a dependência:

```bash
pip install paho-mqtt
```

Execute:

```bash
python server.py
```

Ao iniciar, o servidor exibirá:

```text
--- COMANDOS DISPONIVEIS ---
 led_on
 led_off
 buzzer_on
 buzzer_off
 status
 sair
```

## 🎮 Controle do ESP32

Depois que o servidor estiver conectado ao broker, basta digitar um comando.

### Ligar LED

```text
led_on
```

### Desligar LED

```text
led_off
```

### Ligar buzzer

```text
buzzer_on
```

### Desligar buzzer

```text
buzzer_off
```

### Solicitar status

```text
status
```

### Encerrar servidor

```text
sair
```

## 🔄 Fluxo de funcionamento

### Inicialização

```text
ESP32
  │
  ├── Inicializa sensores
  │
  ├── Conecta ao Wi-Fi
  │
  ├── Conecta ao broker MQTT
  │
  └── Inscreve-se no tópico de comandos
```

### Monitoramento

```text
DHT11 ───────────────┐
                     │
HC-SR04 ─────────────┼──> ESP32 ──MQTT──> Broker ──> Servidor
                     │
LED/Buzzer ──────────┘
```

### Controle

```text
Servidor
    │
    │ MQTT
    ▼
Broker
    │
    │ comando
    ▼
ESP32
    │
    ├── LED
    │
    └── Buzzer
```

Após executar um comando, o ESP32 publica novamente o estado do atuador.

## 🔐 Segurança

> **Importante:** a configuração atual utiliza o broker público `test.mosquitto.org` através da porta `1883`, sem TLS.

Essa configuração é adequada para **testes e fins educacionais**, mas não deve ser utilizada em produção para dados ou dispositivos reais.

Para um ambiente de produção, recomenda-se:

* utilizar um broker MQTT próprio;
* habilitar TLS/SSL;
* utilizar autenticação;
* utilizar credenciais individuais por dispositivo;
* definir ACLs para os tópicos;
* utilizar IDs únicos para os dispositivos;
* evitar colocar credenciais diretamente no código-fonte.

## 🧪 Exemplo de utilização

Imagine um ESP32 instalado em um ambiente monitorado.

O dispositivo envia periodicamente:

```json
{
  "temperatura": 24,
  "umidade": 57,
  "led": "desligado"
}
```

E:

```json
{
  "distancia": 42.8
}
```

O servidor apresenta os dados no terminal.

Caso seja necessário acionar o LED, o operador pode enviar:

```text
led_on
```

O servidor publica:

```json
{
  "comando": "led_on"
}
```

O ESP32 recebe o comando, altera o GPIO do LED e publica:

```json
{
  "led": "ligado"
}
```

## 📚 Objetivos do projeto

Este projeto foi desenvolvido como uma implementação prática de conceitos de:

* Internet das Coisas (IoT);
* sistemas embarcados;
* comunicação MQTT;
* arquitetura orientada a eventos;
* comunicação máquina-a-máquina;
* monitoramento remoto;
* controle remoto de dispositivos;
* integração entre hardware e software.

## 🔮 Possíveis melhorias

Algumas evoluções que podem ser incorporadas ao projeto:

* [ ] Interface web para monitoramento
* [ ] Dashboard em tempo real
* [ ] Armazenamento histórico dos sensores
* [ ] Gráficos de temperatura e umidade
* [ ] Autenticação MQTT
* [ ] MQTT sobre TLS
* [ ] Broker MQTT próprio
* [ ] Suporte a múltiplos ESP32
* [ ] Identificação automática dos dispositivos
* [ ] Reconexão automática ao Wi-Fi
* [ ] Reconexão automática ao broker MQTT
* [ ] Sistema de logs
* [ ] Alertas baseados em temperatura/distância
* [ ] Docker para o servidor
* [ ] API REST para integração com outros sistemas

## 👨‍💻 Autor

Desenvolvido por **vMigliorini**.

## 📄 Licença

Consulte o repositório para informações sobre a licença do projeto.
