🇧🇷 Português | 🇺🇸 English

- [Português](#português)
- [English](#english)

<div align="center">

<img src="Image/Planta.png" alt="Planta Baixa" width="420" style="border-radius:12px;opacity:.85"/>

# 📡 Indoor Positioning System — Wi-Fi Fingerprinting

**Localização indoor em tempo real usando ESP32 + MQTT + Python**

[![ESP32](https://img.shields.io/badge/ESP32-PlatformIO-E55A2B?logo=espressif&logoColor=white)](https://platformio.org)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-6B00B6)](https://www.hivemq.com)
[![License](https://img.shields.io/badge/license-MIT-22c55e)](LICENSE)

</div>

---

## Como funciona

O sistema estima a posição de um ESP32 dentro de um ambiente comparando o scan Wi-Fi atual com **assinaturas previamente calibradas** em cada cômodo — técnica chamada de *Wi-Fi Fingerprinting*. O ESP32 apenas coleta e transmite; todo o cálculo fica no Python local.

```
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

```
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
│   ├── gerador_de_coordenadas.py  # App Tkinter para mapear a planta
│   ├── coordenadas.example.json   # Exemplo de coordenadas (referência)
│   └── requirements.txt
│
├── HTML/
│   ├── indexv1.html               # Interface simples (legado)
│   └── indexv2.html               # Dashboard sci-fi (versão atual)
│
├── Image/
│   └── Planta.png                 # Planta baixa do ambiente
│
├── index.html                     # Seletor de versão da interface
├── .gitignore
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

## Tópicos MQTT

| Tópico | Publicador | Conteúdo |
|--------|-----------|---------|
| `ufsc/engenharia/radar/calibracao` | ESP32 | JSON de calibração *(retained)* |
| `ufsc/engenharia/radar/dados_brutos` | ESP32 | `{"AABBCCDDEEFF": -65, ...}` |
| `ufsc/engenharia/radar/localizacao_final` | Python | `{"local", "x", "y", "confianca"}` |

Broker público: `broker.hivemq.com:1883` (TCP) · `:8884` (WSS — browser)

> ⚠️ Para ambientes de produção, suba um broker local (ex: [Mosquitto](https://mosquitto.org)) para não expor os MACs das suas redes na internet.

---

## Dependências

| Componente | Biblioteca |
|-----------|-----------|
| `calibracao.cpp` | LittleFS (built-in ESP-IDF) |
| `main.cpp` | PubSubClient, LittleFS |
| `backendIPSwifi.py` | paho-mqtt |
| `gerador_de_coordenadas.py` | Pillow, tkinter (built-in) |
| `indexv2.html` | Paho MQTT JS (CDN), Google Fonts (CDN) |

---

## Autor

Desenvolvido por **[Kauan Souto Goede](https://github.com/Kauan-Souto-Goede)** — UFSC Engenharia.

Contribuições, *issues* e *pull requests* são bem-vindos!
