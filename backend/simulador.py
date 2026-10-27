"""Simula o ESP32 enviando leituras HTTP para a API."""

import argparse
import math
import random
import time
from datetime import datetime, timezone

import httpx

ESTACOES = [
    {"id": 1, "chave": "estacao-esp32-demo-key-001", "nome": "Estação Meteorológica ESP32"},
]


def gerar_leitura(estacao_id: int, tick: int) -> dict:
    hora = datetime.now().hour
    ciclo = math.sin((hora + tick / 10) / 24 * math.pi * 2)
    temperatura = 23.5 + ciclo * 6 + random.uniform(-0.4, 0.4)
    umidade = max(30.0, min(95.0, 68 - ciclo * 12 + random.uniform(-3, 3)))
    pressao = 1013.2 + random.uniform(-1.2, 1.2)
    qualidade_ar = 70 + abs(ciclo) * 25 + random.uniform(0, 15)
    luminosidade = max(2.0, min(100.0, 50 + ciclo * 45 + random.uniform(-4, 4)))
    pluviometria = max(0.0, random.choice([0.0, 0.0, 0.0, 0.2, 1.1, 8.0, 27.0]) if tick % 9 == 0 else 0.0)
    return {
        "estacao_id": estacao_id,
        "temperatura": round(temperatura, 2),
        "umidade": round(umidade, 2),
        "pressao": round(pressao, 2),
        "qualidade_ar": round(qualidade_ar, 2),
        "luminosidade": round(luminosidade, 2),
        "pluviometria": round(pluviometria, 2),
        "origem": "esp32",
        "coletada_em": datetime.now(timezone.utc).isoformat(),
    }


def executar(base_url: str, intervalo: float, ciclos: int) -> None:
    cliente = httpx.Client(timeout=10.0)
    tick = 0
    enviados = 0
    try:
        while ciclos == 0 or tick < ciclos:
            for estacao in ESTACOES:
                payload = gerar_leitura(estacao["id"], tick)
                try:
                    resposta = cliente.post(
                        f"{base_url}/api/v1/leituras",
                        json=payload,
                        headers={"X-API-Key": estacao["chave"]},
                    )
                    if resposta.status_code >= 400:
                        print(f"[{estacao['nome']}] erro {resposta.status_code}: {resposta.text}")
                    else:
                        dados = resposta.json()
                        print(
                            f"[{estacao['nome']}] T={dados['temperatura']}°C "
                            f"U={dados['umidade']}% válida={dados['valida']}"
                        )
                        enviados += 1
                except httpx.HTTPError as erro:
                    print(f"Falha de rede para {estacao['nome']}: {erro}")
            tick += 1
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("Simulador interrompido pelo usuário.")
    finally:
        cliente.close()
        print(f"Leituras enviadas: {enviados}")


def main():
    parser = argparse.ArgumentParser(description="Simulador da estação meteorológica ESP32.")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="URL base da API")
    parser.add_argument("--intervalo", type=float, default=5.0, help="Intervalo entre ciclos, em segundos")
    parser.add_argument("--ciclos", type=int, default=0, help="Quantidade de ciclos. 0 = infinito")
    args = parser.parse_args()
    print(f"Enviando leituras simuladas do ESP32 para {args.url}")
    executar(args.url, args.intervalo, args.ciclos)


if __name__ == "__main__":
    main()
