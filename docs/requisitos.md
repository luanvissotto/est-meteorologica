# Requisitos do projeto integrador

## Requisitos funcionais

1. Coletar temperatura, umidade, pressão, qualidade do ar, luminosidade e pluviometria.
2. Transmitir os dados por Wi-Fi usando HTTP e, opcionalmente, MQTT.
3. Armazenar histórico em banco relacional.
4. Rejeitar ou marcar leituras corrompidas.
5. Calcular estatísticas (mínimo, máximo, média, mediana e desvio padrão).
6. Exibir dashboard público com gráficos, mapa e alertas.
7. Informar a estação mais próxima do cidadão.

## Requisitos não funcionais

- Interface responsiva e com contraste adequado.
- CORS liberado para o frontend e para o ESP32.
- Tempo de atualização do painel inferior a 10 segundos.
- Código organizado por responsabilidades.

## Histórias de usuário

- Como cidadão, quero ver a temperatura e a qualidade do ar da minha região para decidir se pratico atividade ao ar livre.
- Como gestor urbano, quero alertas de chuva intensa para antecipar risco de alagamento.
- Como equipe técnica, quero uma chave por estação para evitar dados anônimos ou adulterados.
