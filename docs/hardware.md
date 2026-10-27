# Hardware da estação meteorológica

## Lista de materiais

| Item | Função | Observação |
| --- | --- | --- |
| ESP32 DevKit V1 | Microcontrolador Wi-Fi | 3,3 V |
| DHT22 | Temperatura e umidade | GPIO 4, resistor 4,7 kΩ no DATA |
| BMP280 | Pressão atmosférica | I2C SDA 21, SCL 22 |
| MQ-135 | Qualidade do ar | ADC GPIO 34, pré-aquecimento |
| LDR + resistor 10 kΩ | Luminosidade | Divisor de tensão no GPIO 35 |
| Pluviômetro de báscula | Chuva | Interrupção GPIO 27 |
| LED | Status de envio | GPIO 2 |
| Fonte 5 V / 2 A | Alimentação | USB ou regulador |

## Ligações

- DHT22 DATA -> GPIO 4  
- BMP280 SDA -> GPIO 21  
- BMP280 SCL -> GPIO 22  
- MQ-135 AOUT -> GPIO 34  
- LDR -> GPIO 35  
- Ré reed do pluviômetro -> GPIO 27 e GND  
- LED ânodo -> GPIO 2 (já existe LED onboard em muitos kits)

## Álgebra de Boole no firmware

A leitura só é enviada como consistente se todas as faixas forem verdadeiras:

```
valida = (Tmin ≤ T ≤ Tmax) ∧ (Umin ≤ U ≤ Umax) ∧ (Pmin ≤ P ≤ Pmax)
       ∧ (Amin ≤ A ≤ Amax) ∧ (Lmin ≤ L ≤ Lmax) ∧ (Cmin ≤ C ≤ Cmax)
```

Se o DHT22 devolver `NaN`, o envio é abortado (circuito aberto ou cabo solto).

## Bibliotecas Arduino

- Adafruit BMP280 Library  
- DHT sensor library  
- Adafruit Unified Sensor  
- PubSubClient  

Configure `firmware/estacao_meteorologica/config.h` com o SSID, a senha, o IP do computador que executa a API e a chave da estação.
