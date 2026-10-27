import json
import threading
from typing import Optional

from app.config import get_settings
from app.database import SessionLocal
from app.schemas import LeituraCreate
from app.services.leituras import ErroNegocio, registrar_leitura


def processar_mensagem_mqtt(topico: str, payload_bruto: str) -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        dados = json.loads(payload_bruto)
        chave_api = dados.get("chave_api")
        payload = LeituraCreate(
            estacao_id=dados.get("estacao_id"),
            temperatura=float(dados["temperatura"]),
            umidade=float(dados["umidade"]),
            pressao=float(dados["pressao"]),
            qualidade_ar=float(dados["qualidade_ar"]),
            luminosidade=float(dados["luminosidade"]),
            pluviometria=float(dados["pluviometria"]),
            origem=dados.get("origem", "mqtt"),
        )
        registrar_leitura(db, payload, chave_api, origem_padrao="mqtt")
        print(f"[MQTT] Leitura recebida em {topico}")
    except (KeyError, ValueError, json.JSONDecodeError) as erro:
        print(f"[MQTT] Payload inválido no tópico {topico}: {erro}")
    except ErroNegocio as erro:
        print(f"[MQTT] Rejeitado: {erro.mensagem}")
    except Exception as erro:
        print(f"[MQTT] Erro inesperado: {erro}")
    finally:
        db.close()
        del settings


def iniciar_cliente_mqtt() -> Optional[threading.Thread]:
    settings = get_settings()
    if not settings.mqtt_enabled:
        return None

    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print("[MQTT] Biblioteca paho-mqtt não instalada.")
        return None

    def ao_conectar(cliente, _userdata, _flags, codigo_retorno, _properties=None):
        if codigo_retorno == 0:
            cliente.subscribe(settings.mqtt_topic)
            print(f"[MQTT] Conectado e inscrito em {settings.mqtt_topic}")
        else:
            print(f"[MQTT] Falha na conexão: código {codigo_retorno}")

    def ao_receber(_cliente, _userdata, mensagem):
        processar_mensagem_mqtt(mensagem.topic, mensagem.payload.decode("utf-8"))

    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if settings.mqtt_username:
        cliente.username_pw_set(settings.mqtt_username, settings.mqtt_password)
    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber

    def executar():
        try:
            cliente.connect(settings.mqtt_broker, settings.mqtt_port, 60)
            cliente.loop_forever()
        except Exception as erro:
            print(f"[MQTT] Cliente encerrado: {erro}")

    thread = threading.Thread(target=executar, daemon=True, name="mqtt-ingest")
    thread.start()
    return thread
