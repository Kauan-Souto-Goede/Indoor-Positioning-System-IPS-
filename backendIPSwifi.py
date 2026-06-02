import paho.mqtt.client as mqtt
import json
import math
import sys
import os

# ─── Configurações MQTT ────────────────────────────────────────────────────────
MQTT_BROKER             = "broker.hivemq.com"
MQTT_PORT               = 1883
TOPICO_CALIBRACAO       = "ufsc/engenharia/radar/calibracao"    # ← recebe do ESP32
TOPICO_ENTRADA          = "ufsc/engenharia/radar/dados_brutos"
TOPICO_SAIDA            = "ufsc/engenharia/radar/localizacao_final"

# ─── Caminhos dos arquivos ─────────────────────────────────────────────────────
ARQUIVO_CALIBRACAO  = "calibracao.json"
ARQUIVO_COORDENADAS = "coordenadas.json"

# ─── Estado global ─────────────────────────────────────────────────────────────
# O mapa é construído assim que a calibração chegar; enquanto isso,
# dados brutos recebidos ficam em fila para serem processados depois.
estado = {
    "mapa":          None,   # None = calibração ainda não recebida
    "fila_brutos":   [],     # pacotes recebidos antes da calibração chegar
}

# ─── Carregamento e mesclagem dos mapas ───────────────────────────────────────
def montar_mapa(dados_calibracao: dict) -> dict | None:
    """
    Combina o JSON de calibração com coordenadas.json e retorna o mapa pronto.
    Retorna None se coordenadas.json não existir.
    """
    if not os.path.exists(ARQUIVO_COORDENADAS):
        print(f"[AVISO] '{ARQUIVO_COORDENADAS}' não encontrado.")
        print(f"         Crie o arquivo com as coordenadas de cada cômodo para")
        print(f"         habilitar o posicionamento com coordenadas x/y.")
        print(f"         Usando apenas nome do cômodo (sem x/y) por enquanto.\n")
        # Monta mapa sem coordenadas (só nome do cômodo)
        assinaturas = dados_calibracao.get("assinaturas", {})
        return {
            comodo: {"x": 0, "y": 0, "assinaturas": redes}
            for comodo, redes in assinaturas.items()
        }

    with open(ARQUIVO_COORDENADAS, "r", encoding="utf-8") as f:
        dados_coords = json.load(f)

    assinaturas = dados_calibracao.get("assinaturas", {})
    mapa = {}
    alertas = []

    for comodo, redes in assinaturas.items():
        if comodo not in dados_coords:
            alertas.append(comodo)
            continue
        mapa[comodo] = {
            "x":           dados_coords[comodo]["x"],
            "y":           dados_coords[comodo]["y"],
            "assinaturas": redes,
        }

    print(f"[OK] Mapa montado: {len(mapa)} cômodo(s) prontos.")
    if alertas:
        print(f"[AVISO] {len(alertas)} cômodo(s) sem coordenadas (ignorados):")
        for c in alertas:
            print(f"        → \"{c}\"")

    return mapa if mapa else None

# ─── Algoritmo de posicionamento ──────────────────────────────────────────────
def processar_localizacao(redes_atuais: dict, mapa: dict) -> dict:
    menor_distancia = float("inf")
    local_estimado  = "Desconhecido"
    coords          = {"x": 0, "y": 0}

    for comodo, dados in mapa.items():
        soma_quadrados = 0
        for mac, rssi_calibrado in dados["assinaturas"].items():
            rssi_atual = redes_atuais.get(mac, -100)
            soma_quadrados += math.pow(rssi_atual - rssi_calibrado, 2)

        distancia = math.sqrt(soma_quadrados)

        if distancia < menor_distancia:
            menor_distancia = distancia
            local_estimado  = comodo
            coords          = {"x": dados["x"], "y": dados["y"]}

    return {
        "local":     local_estimado,
        "x":         coords["x"],
        "y":         coords["y"],
        "confianca": round(menor_distancia, 2),
    }

# ─── Callbacks MQTT ───────────────────────────────────────────────────────────
def ao_conectar(client, userdata, flags, rc):
    print(f"[OK] Conectado ao broker HiveMQ (cod: {rc})")
    # Assina os dois tópicos
    client.subscribe(TOPICO_CALIBRACAO)
    client.subscribe(TOPICO_ENTRADA)
    print(f"     Aguardando calibração em : {TOPICO_CALIBRACAO}")
    print(f"     Dados brutos esperados em: {TOPICO_ENTRADA}")
    print(f"     Publicando resultado em  : {TOPICO_SAIDA}\n")

def ao_receber_mensagem(client, userdata, msg):
    topico = msg.topic

    # ── Recebeu JSON de calibração ────────────────────────────────────────────
    if topico == TOPICO_CALIBRACAO:
        try:
            dados_calibracao = json.loads(msg.payload.decode("utf-8"))

            # Salva em disco para referência / reuso offline
            with open(ARQUIVO_CALIBRACAO, "w", encoding="utf-8") as f:
                json.dump(dados_calibracao, f, indent=2, ensure_ascii=False)
            print(f"[Cal] calibracao.json salvo ({len(msg.payload)} bytes).")

            # Monta o mapa de sinais
            mapa = montar_mapa(dados_calibracao)
            if mapa is None:
                print("[Cal] Mapa vazio — verifique coordenadas.json.")
                return

            estado["mapa"] = mapa

            # Processa pacotes que chegaram antes da calibração
            if estado["fila_brutos"]:
                print(f"[Cal] Processando {len(estado['fila_brutos'])} pacote(s) em fila...")
                for redes in estado["fila_brutos"]:
                    _publicar_resultado(client, redes)
                estado["fila_brutos"].clear()

        except Exception as e:
            print(f"[ERRO] Falha ao processar calibração: {e}")
        return

    # ── Recebeu dados brutos de scan ──────────────────────────────────────────
    if topico == TOPICO_ENTRADA:
        try:
            redes_recebidas = json.loads(msg.payload.decode("utf-8"))

            if estado["mapa"] is None:
                # Calibração ainda não chegou: guarda na fila
                estado["fila_brutos"].append(redes_recebidas)
                print(f"[Fila] Calibração pendente — pacote guardado "
                      f"({len(estado['fila_brutos'])} na fila).")
                return

            _publicar_resultado(client, redes_recebidas)

        except json.JSONDecodeError:
            print(f"[ERRO] Payload inválido: {msg.payload}")
        except Exception as e:
            print(f"[ERRO] Falha no cálculo: {e}")

def _publicar_resultado(client, redes: dict):
    resultado = processar_localizacao(redes, estado["mapa"])
    print(f"[POSIÇÃO] {resultado['local']:30s}  "
          f"x={resultado['x']:4}  y={resultado['y']:4}  "
          f"dist={resultado['confianca']}")
    client.publish(TOPICO_SAIDA, json.dumps(resultado))

# ─── Entrada ──────────────────────────────────────────────────────────────────
print("=" * 50)
print("   MOTOR DE POSICIONAMENTO INDOOR")
print("=" * 50)
print(f"\nSe '{ARQUIVO_CALIBRACAO}' já existir localmente, ele será")
print(f"substituído pela versão enviada pelo ESP32 no boot.\n")

client = mqtt.Client(client_id="Motor_Local_Radar")
client.on_connect = ao_conectar
client.on_message = ao_receber_mensagem

print(f"Conectando a {MQTT_BROKER}:{MQTT_PORT}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
