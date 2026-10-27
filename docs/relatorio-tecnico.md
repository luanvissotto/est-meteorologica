# Relatório técnico — Estação Meteorológica Inteligente

## 1. Introdução

Este projeto implementa uma estação meteorológica urbana com ESP32, API Python e dashboard público, alinhado ao plano de ensino de Projeto e Desenvolvimento II.

## 2. Metodologia

O desenvolvimento segue sprints com entregas de hardware, firmware, backend e visualização. O repositório já contém as quatro fatias integradas e um simulador para demonstração sem protoboard.

## 3. Implementação

- Firmware em C++ (Arduino) com leitura periódica e JSON idêntico ao schema da API.
- Backend FastAPI com SQLAlchemy 2, validação, estatística e geolocalização.
- Frontend estático servido pela própria API.
- Banco SQLite inicializado com quatro estações na cidade de São Paulo.

## 4. Testes

Execute no diretório `backend`:

```
python -m pytest -q
```

Os testes cobrem faixas inválidas, salto anormal, classificação do ar, Haversine e estatística descritiva.

## 5. Conclusão

O sistema demonstra o ciclo completo sensor-nuvem-cidadão e pode ser expandido com mais estações, broker MQTT em produção e PostgreSQL municipal.
