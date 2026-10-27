# Estação Meteorológica Inteligente com ESP32

Sistema de monitoramento ambiental em tempo real: firmware ESP32, API FastAPI, banco relacional e dashboard público para acompanhamento das leituras dos sensores.

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

No Windows (PowerShell), a partir da pasta `est-meteorologica/backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abra no navegador:

- Painel principal: http://127.0.0.1:8000/
- Mapa: http://127.0.0.1:8000/mapa
- Histórico: http://127.0.0.1:8000/historico
- Alertas: http://127.0.0.1:8000/alertas
- Documentação interativa da API: http://127.0.0.1:8000/docs

> **Nota:** As estações de demonstração e dados simulados de outros locais foram removidos. O sistema inicia limpo, aguardando a conexão e os dados reais enviados pelo microcontrolador ESP32.

## Envio real pelo ESP32

O ESP32 envia as leituras via requisição HTTP:

- **Endpoint:** `POST /api/v1/leituras`
- **Cabeçalho:** `X-API-Key: estacao-esp32-demo-key-001` (ou a chave configurada em `config.h`)

Configuração no arquivo `firmware/estacao_meteorologica/config.h`:

```c
#define WIFI_SSID "SUA_REDE_WIFI"
#define WIFI_SENHA "SUA_SENHA_WIFI"
#define API_HOST "IP_DO_SEU_COMPUTADOR"
#define API_PORTA 8000
#define API_CAMINHO "/api/v1/leituras"
#define API_CHAVE "estacao-esp32-demo-key-001"
#define ESTACAO_ID 1
```

## Simulação do ESP32 (sem o hardware físico)

Caso queira testar o sistema sem a placa física, utilize o simulador que emula exatamente os dados da estação ESP32:

```powershell
python simulador.py --url http://127.0.0.1:8000 --intervalo 5
```

## MQTT (opcional)

Defina no `.env`:

```text
MQTT_ENABLED=true
MQTT_BROKER=localhost
MQTT_TOPIC=cidades-inteligentes/estacoes/+/leituras
```

O firmware publica o mesmo payload JSON no tópico configurado em `config.h`.

## Testes automatizados

```powershell
python -m pytest -q
```
