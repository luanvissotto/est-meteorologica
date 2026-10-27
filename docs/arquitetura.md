# Arquitetura do sistema

## Visão geral

O fluxo de dados começa no hardware embarcado, passa pela API e termina no dashboard público.

```
Sensores -> ESP32 -> HTTP POST / MQTT -> FastAPI -> SQLite/PostgreSQL -> Dashboard cidadão
```

## Camadas

1. **Firmware (ESP32)**  
   Coleta periódica, validação de faixas, JSON alinhado ao schema `LeituraCreate`.

2. **Backend (FastAPI + SQLAlchemy)**  
   Autenticação por `X-API-Key`, validação lógica, estatística descritiva, alertas e geolocalização.

3. **Persistência**  
   SQLite por padrão (`estacao_meteorologica.db`). PostgreSQL via `DATABASE_URL`.

4. **Frontend**  
   HTML5, Tailwind CSS via CDN, Chart.js e Leaflet. Atualização automática a cada poucos segundos.

## Contratos de dados

Payload enviado pelo ESP32 ou simulador:

```json
{
  "estacao_id": 1,
  "temperatura": 25.4,
  "umidade": 61.2,
  "pressao": 1013.25,
  "qualidade_ar": 118.0,
  "luminosidade": 73.5,
  "pluviometria": 0.25,
  "origem": "esp32"
}
```

Cabeçalho obrigatório: `X-API-Key`.

## Lógica matemática aplicada

- Faixas físicas (predicados booleanos) para cada grandeza.
- Filtro de salto anormal em relação à última amostra.
- Combinação `umidade > 95 AND temperatura > 45` marcada como fisicamente improvável.
- Alertas compostos, por exemplo calor extremo: `temperatura >= 35 AND umidade <= 40`.

## Geometria analítica

- Distância entre cidadão e estação: fórmula de Haversine sobre a esfera terrestre.
- Vetor de deslocamento local `(Δx, Δy)` em quilômetros, com módulo `sqrt(Δx² + Δy²)`.
