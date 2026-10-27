# Estação Meteorológica Inteligente para Cidades Inteligentes

Sistema completo de monitoramento ambiental urbano: firmware ESP32, API FastAPI, banco relacional e dashboard público para cidadãos.

## Estrutura do repositório

```text
testesm/
├── README.md
├── docs/
│   ├── arquitetura.md
│   ├── hardware.md
│   ├── requisitos.md
│   └── relatorio-tecnico.md
├── backend/
│   ├── app/
│   ├── tests/
│   ├── simulador.py
│   └── requirements.txt
├── frontend/
└── firmware/estacao_meteorologica/
```

## Como executar o backend e o dashboard

No Windows (PowerShell), a partir da pasta `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abra:

- Painel: http://127.0.0.1:8000/
- Mapa: http://127.0.0.1:8000/mapa
- Documentação da API: http://127.0.0.1:8000/docs

Na primeira inicialização o banco SQLite é criado com quatro estações de demonstração.

## Simular o ESP32 sem hardware

Em outro terminal, com o ambiente virtual ativado:

```powershell
python simulador.py --url http://127.0.0.1:8000 --intervalo 5
```

## Envio real pelo ESP32

`POST /api/v1/leituras` com cabeçalho `X-API-Key`.

Chaves de demonstração:

| Estação | Chave |
| --- | --- |
| Praça da Sé | `estacao-se-demo-key-001` |
| Parque Ibirapuera | `estacao-ibirapuera-demo-key-002` |
| Avenida Paulista | `estacao-paulista-demo-key-003` |
| Pinheiros | `estacao-pinheiros-demo-key-004` |

Cadastro de nova estação: `POST /api/v1/estacoes` com cabeçalho `X-Admin-Token: admin-demo`.

## MQTT (opcional)

Defina no `.env`:

```text
MQTT_ENABLED=true
MQTT_BROKER=localhost
MQTT_TOPIC=cidades-inteligentes/estacoes/+/leituras
```

O firmware publica o mesmo JSON no tópico configurado em `config.h`.

## Testes

```powershell
python -m pytest -q
```

## PostgreSQL

```text
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/estacao
```

Instale o driver `psycopg2-binary` se for usar PostgreSQL.
