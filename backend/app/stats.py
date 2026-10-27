import math
from typing import Iterable, List, Optional


def media(valores: List[float]) -> Optional[float]:
    if not valores:
        return None
    return sum(valores) / len(valores)


def mediana(valores: List[float]) -> Optional[float]:
    if not valores:
        return None
    ordenados = sorted(valores)
    n = len(ordenados)
    meio = n // 2
    if n % 2 == 0:
        return (ordenados[meio - 1] + ordenados[meio]) / 2
    return ordenados[meio]


def desvio_padrao(valores: List[float]) -> Optional[float]:
    valor_medio = media(valores)
    if valor_medio is None or len(valores) < 2:
        return None
    variancia = sum((valor - valor_medio) ** 2 for valor in valores) / (len(valores) - 1)
    return math.sqrt(variancia)


def resumo_serie(valores: Iterable[float]) -> dict:
    lista = [float(valor) for valor in valores]
    return {
        "quantidade": len(lista),
        "minimo": min(lista) if lista else None,
        "maximo": max(lista) if lista else None,
        "media": round(media(lista), 3) if lista else None,
        "mediana": round(mediana(lista), 3) if lista else None,
        "desvio_padrao": round(desvio_padrao(lista), 3) if desvio_padrao(lista) is not None else None,
    }
