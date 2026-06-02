# 📍 Indoor Positioning System (IPS) via Wi-Fi Fingerprinting

Um sistema completo de Posicionamento em Ambientes Internos (Indoor Positioning System) focado em rastreamento através de sinais Wi-Fi (RSSI e MAC Address). 

Este projeto resolve o problema de localização em ambientes fechados (onde o GPS não é efetivo) utilizando a técnica de *Fingerprinting*. O sistema é modular, dividido em firmware de coleta, um servidor backend local para cálculos matemáticos, uma interface web de monitoramento em tempo real e uma ferramenta auxiliar para mapeamento do ambiente.

---

## 🧠 Como o sistema funciona (Arquitetura)

O fluxo de dados do projeto ocorre em tempo real, utilizando **MQTT** como protocolo central de comunicação. A arquitetura é dividida em quatro pilares fundamentais:

### 1. O Hardware (ESP32 - PlatformIO / C++)
O microcontrolador atua como o "sensor" do ambiente. O firmware foi dividido em duas etapas para garantir a eficiência e organização do sistema:
* **Modo de Calibração (Fingerprint):** Antes de o sistema rodar oficialmente, este código varre o ambiente coletando a força do sinal (RSSI) e o MAC Address dos roteadores/beacons em pontos conhecidos. Ele processa e **salva esses dados apenas na memória interna** do ESP (SPIFFS/LittleFS).
* **Modo Principal (Tracking):** É o código de operação contínua. Logo ao ser iniciado, ele resgata a calibração final salva na memória e a envia via MQTT para o servidor. Em seguida, ele passa a ler continuamente o RSSI do momento e transmitir esses dados brutos para cálculo.

### 2. O Servidor Backend (Python)
É o "cérebro" do sistema que recebe os dados do ESP32 via MQTT, executa os cálculos de trilateração/probabilidade e publica as coordenadas (X, Y) calculadas para o frontend. 
* 🔒 **Foco em Privacidade:** O backend foi projetado para rodar **exclusivamente de forma local** (offline/fora da nuvem). Essa é uma medida de segurança rigorosa para evitar que os MAC Addresses da sua rede, de dispositivos vizinhos e de equipamentos ao redor fiquem expostos na internet.

### 3. A Interface Web (HTML / CSS / JS)
É a "parte bonita" do projeto. Um site estático (hospedado em HTTPS via GitHub Pages ou rodando localmente) que se conecta ao broker MQTT via WebSockets.
* **Upload Dinâmico da Planta Baixa:** Para utilizar a interface, é necessário ter uma imagem da sua planta baixa (PNG, JPG, etc.). Por flexibilidade, a imagem não fica presa no código-fonte; a própria interface permite que você faça o upload da imagem da planta e do arquivo de coordenadas no navegador toda vez que for utilizar a ferramenta.

### 4. O Mapeador de Planta Baixa (Ferramenta Auxiliar em Python)
Uma aplicação desktop com interface gráfica (usando `Tkinter` e `Pillow`) desenvolvida para gerar as coordenadas do seu ambiente. O usuário carrega a imagem da planta baixa, clica nos cômodos para definir as localizações físicas e o programa gera automaticamente o arquivo `coordenadas.json` consumido pelo site.

---

## 🚀 Como reproduzir o projeto (Getting Started)

Siga a ordem abaixo para configurar o ecossistema completo na sua máquina.

### Pré-requisitos
* Um microcontrolador **ESP32**.
* [VS Code](https://code.visualstudio.com/) com a extensão **PlatformIO**.
* **Python 3.x** instalado.
* Um Broker MQTT configurado na sua rede local (ex: Mosquitto).
* Uma imagem (foto/arquivo) da sua planta baixa.

### Passo 1: Mapear o Ambiente
1. Navegue até a pasta da ferramenta auxiliar.
2. Instale a dependência de imagem: `pip install Pillow`
3. Rode o programa: `python gerador_de_coordenadas.py`
4. Carregue a imagem da sua planta baixa, clique nos locais mapeados e clique em **Salvar coordenadas.json**. Você usará esse arquivo mais tarde.

### Passo 2: Calibrar o ESP32 (Fingerprinting)
1. Abra a pasta do firmware no VS Code (PlatformIO).
2. Configure as credenciais de Wi-Fi e do seu Broker MQTT local no arquivo de configuração do firmware.
3. Faça o upload do **Código de Calibração** para o ESP32.
4. Posicione o ESP32 nos cômodos físicos correspondentes ao seu mapa e deixe-o coletar as amostras de sinal. Ele salvará a calibração internamente na placa.

### Passo 3: Iniciar o Backend Seguro (Local)
1. Navegue até a pasta do servidor Python.
2. Instale a biblioteca do MQTT e dependências matemáticas: `pip install paho-mqtt numpy` (ajuste conforme as bibliotecas que estiver usando).
3. Execute o servidor: `python backend_server.py`.
4. Mantenha o terminal aberto. Ele rodará localmente, aguardando os dados do ESP32 para calcular as posições sem expor seus MACs na internet.

### Passo 4: Rodar o Tracker e Monitorar na Web
1. Faça o upload do **Código Principal** (Tracker) para o ESP32. Assim que ligar, ele enviará a calibração salva para o servidor local e começará o rastreamento em tempo real.
2. Acesse a interface Web (seu link HTTPS do GitHub Pages ou arquivo local via *Live Server*).
3. Faça o **upload da imagem da sua planta baixa** e do arquivo `coordenadas.json` diretamente na página web.
4. Pronto! Veja a localização sendo atualizada no mapa em tempo real conforme o ESP32 se move pelo ambiente.

---

## 👨‍💻 Autor
Desenvolvido por [Kauan Souto Goede](https://github.com/Kauan-Souto-Goede).

Contribuições, *issues* e *pull requests* são bem-vindos!
