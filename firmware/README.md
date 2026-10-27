# Firmware ESP32

Abra a pasta `estacao_meteorologica` no Arduino IDE ou no PlatformIO.

1. Instale as bibliotecas DHT sensor library, Adafruit BMP280, Adafruit Unified Sensor e PubSubClient.
2. Edite `config.h` com Wi-Fi, IP da API e chave da estação.
3. Grave o sketch no ESP32.

O JSON gerado é o mesmo esperado por `POST /api/v1/leituras`.
