# 📍 Indoor Positioning System (IPS) via Wi-Fi Fingerprinting

Um sistema completo de Posicionamento em Ambientes Internos (Indoor Positioning System) focado em rastreamento através de sinais Wi-Fi (RSSI e MAC Address). 

Este projeto resolve o problema de localização em ambientes fechados (onde o GPS não é efetivo) utilizando a técnica de *Fingerprinting*. O sistema é modular, dividido em firmware de coleta, um servidor backend para cálculos matemáticos, uma interface web de monitoramento em tempo real e uma ferramenta auxiliar para mapeamento do ambiente.

---

## 🧠 Como o sistema funciona (Arquitetura)

O fluxo de dados do projeto ocorre em tempo real, utilizando **MQTT** como protocolo central de comunicação entre as partes. A arquitetura é dividida em quatro pilares fundamentais:

### 1. O Hardware (ESP32 - PlatformIO / C++)
O microcontrolador atua como o "sensor" do ambiente. O firmware foi dividido em duas etapas para garantir a precisão do sistema:
* **Modo de Calibração (Fingerprint):** Antes de o sistema rodar oficialmente, este código varre o ambiente coletando a força do sinal (RSSI) e o MAC Address dos roteadores/beacons próximos em pontos conhecidos. Ele salva esses "mapas de sinal" na memória interna do ESP (SPIFFS/LittleFS) e também os envia via MQTT para que o backend conheça o ambiente.
* **Modo Principal (Tracking):** É o código de operação contínua. Ele lê o RSSI do momento e transmite esses dados brutos via MQTT para o servidor processar.

### 2. O Servidor Backend (Python)
É o "cérebro" do sistema que roda no computador local. 
* Ele se inscreve nos tópicos MQTT para receber os dados brutos de MAC Address e RSSI enviados pelo ESP32.
* Com base nos dados de calibração (*fingerprints*) registrados anteriormente, o script Python executa os cálculos de trilateração/probabilidade para estimar a posição exata do dispositivo.
* Após calcular o ponto geográfico relativo, ele publica as coordenadas (X, Y) processadas em um novo tópico MQTT focado no Frontend.

### 3. A Interface Web (HTML / CSS / JS)
É a "parte bonita" do projeto. 
* Um site estático que se conecta ao broker MQTT via WebSockets.
* Ele consome as coordenadas calculadas pelo backend e renderiza um marcador se movendo em tempo real sobre a planta baixa do ambiente.

### 4. O Mapeador de Planta Baixa (Ferramenta Auxiliar em Python)
Como os ambientes variam, criei uma aplicação desktop com interface gráfica (usando `Tkinter` e `Pillow`).
* O usuário carrega a imagem da sua própria planta baixa, clica nos cômodos para definir onde as coisas estão fisicamente e o programa gera automaticamente um arquivo `coordenadas.json`.
* Esse JSON é lido pela interface web para que ela saiba exatamente onde desenhar os elementos de forma proporcional.

---

## 🚀 Como reproduzir o projeto (Getting Started)

Siga a ordem abaixo para configurar o ecossistema completo na sua máquina.

### Pré-requisitos
* Um microcontrolador **ESP32**.
* [VS Code](https://code.visualstudio.com/) com a extensão **PlatformIO**.
* **Python 3.x** instalado.
* Um Broker MQTT configurado (local como Mosquitto, ou em nuvem como HiveMQ/CloudMQTT).

### Passo 1: Mapear o Ambiente
1. Navegue até a pasta da ferramenta auxiliar.
2. Instale a dependência de imagem: `pip install Pillow`
3. Rode o programa: `python gerador_de_coordenadas.py`
4. Carregue a foto da sua planta baixa, clique nos locais mapeados e clique em **Salvar coordenadas.json**.
5. Mova este arquivo `.json` gerado para a raiz da pasta do seu Frontend Web.

### Passo 2: Calibrar o ESP32 (Fingerprinting)
1. Abra a pasta do projeto do ESP32 no VS Code (PlatformIO).
2. Configure as credenciais de Wi-Fi e do seu Broker MQTT no arquivo de configuração do firmware.
3. Faça o upload do **Código de Calibração** para o ESP32.
4. Posicione o ESP32 nos cômodos físicos correspondentes ao seu mapa e deixe-o coletar as amostras de sinal. Ele salvará os dados internamente e publicará no broker.

### Passo 3: Iniciar o Backend
1. Navegue até a pasta do servidor Python.
2. Instale a biblioteca do MQTT: `pip install paho-mqtt` (e outras que você utilize para cálculo, como `numpy` ou `scipy`).
3. Execute o servidor: `python backend_server.py`.
4. Mantenha o terminal aberto. Ele ficará aguardando os dados do ESP32.

### Passo 4: Rodar o Tracker e Monitorar
1. Faça o upload do **Código Principal** (Tracker) para o ESP32 através do PlatformIO. Agora ele começará a varrer o ambiente e mandar os dados em tempo real.
2. Abra a interface Web (o arquivo `.html` principal) no seu navegador. Se estiver usando o VS Code, utilize a extensão *Live Server* para evitar bloqueios de CORS ao ler o `.json`.
3. Pronto! Veja a localização sendo atualizada na interface conforme o ESP32 se move pelo ambiente.

---

## 👨‍💻 Autor
Desenvolvido por [Kauan Souto Goede](https://github.com/Kauan-Souto-Goede).

Contribuições, *issues* e *pull requests* são bem-vindos!
