from dataclasses import dataclass
from typing import List, Optional


LIMITE_TEMPERATURA = {"min": -20.0, "max": 60.0, "salto": 12.0}
LIMITE_UMIDADE = {"min": 0.0, "max": 100.0, "salto": 40.0}
LIMITE_PRESSAO = {"min": 870.0, "max": 1080.0, "salto": 25.0}
LIMITE_QUALIDADE_AR = {"min": 0.0, "max": 1500.0, "salto": 400.0}
LIMITE_LUMINOSIDADE = {"min": 0.0, "max": 100.0, "salto": 80.0}
LIMITE_PLUVIOMETRIA = {"min": 0.0, "max": 250.0, "salto": 80.0}


@dataclass
class ResultadoValidacao:
    valida: bool
    flags: List[str]


def valor_dentro_faixa(valor: float, minimo: float, maximo: float) -> bool:
    return minimo <= valor <= maximo


def salto_anormal(atual: float, anterior: Optional[float], salto_maximo: float) -> bool:
    if anterior is None:
        return False
    return abs(atual - anterior) > salto_maximo


def classificar_qualidade_ar(ppm: float) -> tuple[int, str]:
    if ppm < 50:
        return 25, "boa"
    if ppm < 100:
        return 50, "moderada"
    if ppm < 200:
        return 100, "ruim_para_sensiveis"
    if ppm < 350:
        return 150, "insalubre"
    if ppm < 500:
        return 200, "muito_insalubre"
    return 300, "perigosa"


def validar_leitura(
    temperatura: float,
    umidade: float,
    pressao: float,
    qualidade_ar: float,
    luminosidade: float,
    pluviometria: float,
    anterior: Optional[dict] = None,
) -> ResultadoValidacao:
    flags: List[str] = []

    if not valor_dentro_faixa(temperatura, LIMITE_TEMPERATURA["min"], LIMITE_TEMPERATURA["max"]):
        flags.append("temperatura_fora_faixa")
    if not valor_dentro_faixa(umidade, LIMITE_UMIDADE["min"], LIMITE_UMIDADE["max"]):
        flags.append("umidade_fora_faixa")
    if not valor_dentro_faixa(pressao, LIMITE_PRESSAO["min"], LIMITE_PRESSAO["max"]):
        flags.append("pressao_fora_faixa")
    if not valor_dentro_faixa(qualidade_ar, LIMITE_QUALIDADE_AR["min"], LIMITE_QUALIDADE_AR["max"]):
        flags.append("qualidade_ar_fora_faixa")
    if not valor_dentro_faixa(luminosidade, LIMITE_LUMINOSIDADE["min"], LIMITE_LUMINOSIDADE["max"]):
        flags.append("luminosidade_fora_faixa")
    if not valor_dentro_faixa(pluviometria, LIMITE_PLUVIOMETRIA["min"], LIMITE_PLUVIOMETRIA["max"]):
        flags.append("pluviometria_fora_faixa")

    temp_anterior = anterior.get("temperatura") if anterior else None
    umid_anterior = anterior.get("umidade") if anterior else None
    press_anterior = anterior.get("pressao") if anterior else None
    ar_anterior = anterior.get("qualidade_ar") if anterior else None
    lum_anterior = anterior.get("luminosidade") if anterior else None
    chuva_anterior = anterior.get("pluviometria") if anterior else None

    if salto_anormal(temperatura, temp_anterior, LIMITE_TEMPERATURA["salto"]):
        flags.append("temperatura_salto_anormal")
    if salto_anormal(umidade, umid_anterior, LIMITE_UMIDADE["salto"]):
        flags.append("umidade_salto_anormal")
    if salto_anormal(pressao, press_anterior, LIMITE_PRESSAO["salto"]):
        flags.append("pressao_salto_anormal")
    if salto_anormal(qualidade_ar, ar_anterior, LIMITE_QUALIDADE_AR["salto"]):
        flags.append("qualidade_ar_salto_anormal")
    if salto_anormal(luminosidade, lum_anterior, LIMITE_LUMINOSIDADE["salto"]):
        flags.append("luminosidade_salto_anormal")
    if salto_anormal(pluviometria, chuva_anterior, LIMITE_PLUVIOMETRIA["salto"]):
        flags.append("pluviometria_salto_anormal")

    umidade_incompativel = umidade > 95 and temperatura > 45
    if umidade_incompativel:
        flags.append("combinacao_fisicamente_improvavel")

    return ResultadoValidacao(valida=len(flags) == 0, flags=flags)


def gerar_alertas_climaticos(
    temperatura: float,
    umidade: float,
    pressao: float,
    qualidade_ar: float,
    pluviometria: float,
    indice_qualidade_ar: int,
) -> List[dict]:
    alertas: List[dict] = []

    calor_extremo = temperatura >= 35 and umidade <= 40
    if calor_extremo:
        alertas.append(
            {
                "tipo": "calor_extremo",
                "severidade": "alta",
                "mensagem": "Risco de estresse térmico: temperatura elevada combinada com umidade baixa.",
                "valor": temperatura,
                "limiar": 35.0,
            }
        )
    elif temperatura >= 32:
        alertas.append(
            {
                "tipo": "onda_de_calor",
                "severidade": "media",
                "mensagem": "Temperatura acima do conforto térmico urbano.",
                "valor": temperatura,
                "limiar": 32.0,
            }
        )

    if temperatura <= 8:
        alertas.append(
            {
                "tipo": "frio_intenso",
                "severidade": "media",
                "mensagem": "Queda acentuada de temperatura detectada.",
                "valor": temperatura,
                "limiar": 8.0,
            }
        )

    if umidade >= 90 and pluviometria >= 5:
        alertas.append(
            {
                "tipo": "tempo_instavel",
                "severidade": "media",
                "mensagem": "Umidade muito alta com precipitação em curso.",
                "valor": umidade,
                "limiar": 90.0,
            }
        )

    if pluviometria >= 25:
        alertas.append(
            {
                "tipo": "chuva_intensa",
                "severidade": "alta",
                "mensagem": "Precipitação intensa: atenção a alagamentos urbanos.",
                "valor": pluviometria,
                "limiar": 25.0,
            }
        )
    elif pluviometria >= 10:
        alertas.append(
            {
                "tipo": "chuva_moderada",
                "severidade": "baixa",
                "mensagem": "Chuva moderada registrada na estação.",
                "valor": pluviometria,
                "limiar": 10.0,
            }
        )

    if pressao <= 990:
        alertas.append(
            {
                "tipo": "baixa_pressao",
                "severidade": "media",
                "mensagem": "Pressão atmosférica baixa, possível instabilidade climática.",
                "valor": pressao,
                "limiar": 990.0,
            }
        )

    if indice_qualidade_ar >= 200 or qualidade_ar >= 500:
        alertas.append(
            {
                "tipo": "qualidade_ar_perigosa",
                "severidade": "critica",
                "mensagem": "Qualidade do ar perigosa. Evite atividades ao ar livre.",
                "valor": qualidade_ar,
                "limiar": 500.0,
            }
        )
    elif indice_qualidade_ar >= 150 or qualidade_ar >= 350:
        alertas.append(
            {
                "tipo": "qualidade_ar_ruim",
                "severidade": "alta",
                "mensagem": "Qualidade do ar insalubre para a população em geral.",
                "valor": qualidade_ar,
                "limiar": 350.0,
            }
        )
    elif indice_qualidade_ar >= 100 or qualidade_ar >= 200:
        alertas.append(
            {
                "tipo": "qualidade_ar_atencao",
                "severidade": "media",
                "mensagem": "Qualidade do ar ruim para grupos sensíveis.",
                "valor": qualidade_ar,
                "limiar": 200.0,
            }
        )

    return alertas
