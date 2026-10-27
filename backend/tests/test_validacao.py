from app.geo import haversine_km, vetor_deslocamento_km
from app.stats import resumo_serie
from app.validators import classificar_qualidade_ar, gerar_alertas_climaticos, validar_leitura


def test_leitura_valida():
    resultado = validar_leitura(25.0, 60.0, 1013.0, 80.0, 70.0, 0.0)
    assert resultado.valida is True
    assert resultado.flags == []


def test_temperatura_fora_faixa():
    resultado = validar_leitura(95.0, 60.0, 1013.0, 80.0, 70.0, 0.0)
    assert resultado.valida is False
    assert "temperatura_fora_faixa" in resultado.flags


def test_salto_anormal():
    anterior = {
        "temperatura": 22.0,
        "umidade": 55.0,
        "pressao": 1013.0,
        "qualidade_ar": 80.0,
        "luminosidade": 50.0,
        "pluviometria": 0.0,
    }
    resultado = validar_leitura(45.0, 55.0, 1013.0, 80.0, 50.0, 0.0, anterior)
    assert "temperatura_salto_anormal" in resultado.flags


def test_classificacao_ar():
    indice, classe = classificar_qualidade_ar(40)
    assert indice == 25
    assert classe == "boa"


def test_alerta_chuva_intensa():
    alertas = gerar_alertas_climaticos(24.0, 80.0, 1010.0, 90.0, 30.0, 50)
    tipos = [item["tipo"] for item in alertas]
    assert "chuva_intensa" in tipos


def test_haversine_mesma_coordenada():
    assert haversine_km(-23.55, -46.63, -23.55, -46.63) == 0


def test_vetor_deslocamento():
    vetor = vetor_deslocamento_km(-23.55, -46.63, -23.56, -46.63)
    assert vetor["dx_km"] == 0
    assert vetor["dy_km"] < 0


def test_resumo_serie():
    resumo = resumo_serie([10, 20, 30])
    assert resumo["quantidade"] == 3
    assert resumo["media"] == 20.0
    assert resumo["minimo"] == 10.0
    assert resumo["maximo"] == 30.0
