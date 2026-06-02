# 🇧🇷 Português | 🇺🇸 English

* [Português](#-indoor-positioning-system--wi-fi-fingerprinting)
* [English](#-indoor-positioning-system--wi-fi-fingerprinting-english)

<div align="center">

<img src="Image/Planta.png" alt="Planta Baixa" width="420" style="border-radius:12px;opacity:.85"/>

# 📡 Indoor Positioning System — Wi-Fi Fingerprinting

**Localização indoor em tempo real usando ESP32 + MQTT + Python**

[![ESP32](https://img.shields.io/badge/ESP32-PlatformIO-E55A2B?logo=espressif\&logoColor=white)](https://platformio.org)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python\&logoColor=white)](https://python.org)
[![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-6B00B6)](https://www.hivemq.com)
[![License](https://img.shields.io/badge/license-MIT-22c55e)](LICENSE)

</div>

---

## Como funciona

O sistema estima a posição de um ESP32 dentro de um ambiente comparando o scan Wi-Fi atual com **assinaturas previamente calibradas** em cada cômodo — técnica chamada de *Wi-Fi Fingerprinting*. O ESP32 apenas coleta e transmite; todo o cálculo fica no Python local.

```text
┌─────────────────┐     LittleFS      ┌──────────────────────────┐
│  calibracao.cpp │ ──────────────── ▶│  Flash interna (ESP32)   │
└─────────────────┘   (uma vez)       └──────────┬───────────────┘
                                                  │ boot
                                                  ▼
┌─────────────────┐   MQTT retained   ┌──────────────────────────┐
│    main.cpp     │ ────────────────▶ │  calibracao  (tópico)    │
│   (radar loop)  │ ────────────────▶ │  dados_brutos (tópico)   │
└─────────────────┘   a cada 10s      └──────────┬───────────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────────┐
                                    │   backendIPSwifi.py (local) │
                                    │   distância euclidiana RSSI │
                                    └──────────┬──────────────────┘
                                               │ MQTT
                                               ▼
                                    ┌─────────────────────────────┐
                                    │   indexv2.html  (browser)   │
                                    │   ponto em tempo real ●     │
                                    └─────────────────────────────┘
```

### Algoritmo de posicionamento

Para cada scan recebido, o backend calcula a **distância euclidiana no espaço RSSI** entre o scan atual e cada assinatura calibrada:

$$d_{comodo} = \sqrt{\sum_{mac} (rssi_{atual} - rssi_{calibrado})^2}$$

O cômodo com **menor distância** é a localização estimada. Redes ausentes no scan recebem penalidade de −100 dBm.

---

## Estrutura do repositório

```text
Indoor-Positioning-System-IPS/
│
├── ESP32/                          # Projeto PlatformIO (dois ambientes)
│   ├── src/
│   │   ├── calibracao.cpp          # Firmware de calibração (gravar uma vez)
│   │   └── main.cpp                # Firmware de operação contínua (radar)
│   └── platformio.ini              # Dois envs: [calibracao] e [producao]
│
├── Backend Server/
│   ├── backendIPSwifi.py           # Motor de posicionamento MQTT
│   ├── gerador_de_coordenadas.py   # App Tkinter para mapear a planta
│   ├── coordenadas.example.json    # Exemplo de coordenadas (referência)
│   └── requirements.txt
│
├── HTML/
│   ├── indexv1.html                # Interface simples (legado)
│   └── indexv2.html                # Dashboard sci-fi (versão atual)
│
├── Image/
│   └── Planta.png                  # Planta baixa do ambiente
│
├── index.html                      # Seletor de versão da interface
├── LICENSE
└── README.md
```

---

## Utilização

1. Gere o mapa de coordenadas utilizando gerador_de_coordenadas.py.
2. Execute o firmware de calibração para coletar as assinaturas Wi-Fi do ambiente.
3. Grave o firmware principal no ESP32.
4. Execute backendIPSwifi.py.
5. Abra index.html e selecione a interface desejada.

---

## Tópicos MQTT

| Tópico                                    | Publicador | Conteúdo                           |
| ----------------------------------------- | ---------- | ---------------------------------- |
| `ufsc/engenharia/radar/calibracao`        | ESP32      | JSON de calibração *(retained)*    |
| `ufsc/engenharia/radar/dados_brutos`      | ESP32      | `{"AABBCCDDEEFF": -65, ...}`       |
| `ufsc/engenharia/radar/localizacao_final` | Python     | `{"local", "x", "y", "confianca"}` |

Broker público: `broker.hivemq.com:1883` (TCP) · `:8884` (WSS — browser)

> ⚠️ Para ambientes de produção, suba um broker local (ex: Mosquitto) para não expor os MACs das suas redes na internet.

---

## Dependências

| Componente                  | Biblioteca                             |
| --------------------------- | -------------------------------------- |
| `calibracao.cpp`            | LittleFS (built-in ESP-IDF)            |
| `main.cpp`                  | PubSubClient, LittleFS                 |
| `backendIPSwifi.py`         | paho-mqtt                              |
| `gerador_de_coordenadas.py` | Pillow, tkinter (built-in)             |
| `indexv2.html`              | Paho MQTT JS (CDN), Google Fonts (CDN) |

---

## Autor

Desenvolvido por **Kauan Souto Goede** — UFSC Engenharia.

Contribuições, *issues* e *pull requests* são bem-vindos!

---

# 📡 Indoor Positioning System — Wi-Fi Fingerprinting (English)

**Real-time indoor positioning using ESP32 + MQTT + Python**

[![ESP32](https://img.shields.io/badge/ESP32-PlatformIO-E55A2B?logo=espressif\&logoColor=white)](https://platformio.org)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python\&logoColor=white)](https://python.org)
[![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-6B00B6)](https://www.hivemq.com)
[![License](https://img.shields.io/badge/license-MIT-22c55e)](LICENSE)

</div>

---

## How it works

The system estimates the position of an ESP32 inside an environment by comparing the current Wi-Fi scan with **previously calibrated fingerprints** for each room — a technique known as *Wi-Fi Fingerprinting*. The ESP32 is responsible only for collecting and transmitting data, while all processing is performed locally in Python.

```text
┌─────────────────┐     LittleFS      ┌──────────────────────────┐
│ calibration.cpp │ ────────────────▶ │  ESP32 Internal Flash    │
└─────────────────┘    (one time)     └──────────┬───────────────┘
                                                  │ boot
                                                  ▼
┌─────────────────┐   MQTT retained   ┌──────────────────────────┐
│    main.cpp     │ ────────────────▶ │ calibration (topic)      │
│   (radar loop)  │ ────────────────▶ │ raw_data (topic)         │
└─────────────────┘   every 10s       └──────────┬───────────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────────┐
                                    │   backendIPSwifi.py (local) │
                                    │   RSSI Euclidean distance   │
                                    └──────────┬──────────────────┘
                                               │ MQTT
                                               ▼
                                    ┌─────────────────────────────┐
                                    │   indexv2.html (browser)    │
                                    │   real-time tracking ●      │
                                    └─────────────────────────────┘
```

### Positioning algorithm

For each received scan, the backend computes the **Euclidean distance in RSSI space** between the current scan and every calibrated fingerprint:

$$d_{room} = \sqrt{\sum_{mac} (rssi_{current} - rssi_{reference})^2}$$

The room with the **smallest distance** is selected as the estimated location. Missing networks receive a −100 dBm penalty.

---

## Repository structure

```text
Indoor-Positioning-System-IPS/
│
├── ESP32/
│   ├── src/
│   │   ├── calibration.cpp
│   │   └── main.cpp
│   └── platformio.ini
│
├── Backend Server/
│   ├── backendIPSwifi.py
│   ├── coordinate_generator.py
│   ├── coordinates.example.json
│   └── requirements.txt
│
├── HTML/
│   ├── indexv1.html
│   └── indexv2.html
│
├── Image/
│   └── Planta.png
│
├── index.html
├── LICENSE
└── README.md
```

---

## Usage

1. Generate the coordinate map using `gerador_de_coordenadas.py`.
2. Run the calibration firmware to collect Wi-Fi fingerprints.
3. Upload the main firmware to the ESP32.
4. Run `backendIPSwifi.py`.
5. Open `index.html` and select the desired interface.

---

## MQTT Topics

| Topic                                     | Publisher | Content                                |
| ----------------------------------------- | --------- | -------------------------------------- |
| `ufsc/engenharia/radar/calibracao`        | ESP32     | Calibration JSON *(retained)*          |
| `ufsc/engenharia/radar/dados_brutos`      | ESP32     | `{"AABBCCDDEEFF": -65, ...}`           |
| `ufsc/engenharia/radar/localizacao_final` | Python    | `{"location", "x", "y", "confidence"}` |

Public broker: `broker.hivemq.com:1883` (TCP) · `:8884` (WSS — browser)

> ⚠️ For production environments, consider using a local broker (e.g. Mosquitto) to avoid exposing Wi-Fi MAC addresses over the internet.

---

## Dependencies

| Component                   | Library                                |
| --------------------------- | -------------------------------------- |
| `calibration.cpp`           | LittleFS (built-in ESP-IDF)            |
| `main.cpp`                  | PubSubClient, LittleFS                 |
| `backendIPSwifi.py`         | paho-mqtt                              |
| `gerador_de_coordenadas.py` | Pillow, tkinter                        |
| `indexv2.html`              | Paho MQTT JS (CDN), Google Fonts (CDN) |

---

## Author

Developed by **Kauan Souto Goede** — UFSC Engineering.

Contributions, issues and pull requests are welcome!
