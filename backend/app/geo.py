import math
from typing import Iterable, List

RAIO_TERRA_KM = 6371.0


def graus_para_radianos(graus: float) -> float:
    return graus * math.pi / 180.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = graus_para_radianos(lat1)
    phi2 = graus_para_radianos(lat2)
    delta_phi = graus_para_radianos(lat2 - lat1)
    delta_lambda = graus_para_radianos(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return RAIO_TERRA_KM * c


def vetor_deslocamento_km(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    dx = haversine_km(lat1, lon1, lat1, lon2)
    if lon2 < lon1:
        dx = -dx
    dy = haversine_km(lat1, lon1, lat2, lon1)
    if lat2 < lat1:
        dy = -dy
    modulo = math.sqrt(dx ** 2 + dy ** 2)
    return {"dx_km": round(dx, 4), "dy_km": round(dy, 4), "modulo_km": round(modulo, 4)}


def coordenadas_validas(latitude: float, longitude: float) -> bool:
    return -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0


def ordenar_por_proximidade(
    origem_lat: float,
    origem_lon: float,
    estacoes: Iterable[dict],
) -> List[dict]:
    resultado = []
    for estacao in estacoes:
        distancia = haversine_km(origem_lat, origem_lon, estacao["latitude"], estacao["longitude"])
        vetor = vetor_deslocamento_km(
            origem_lat,
            origem_lon,
            estacao["latitude"],
            estacao["longitude"],
        )
        item = dict(estacao)
        item["distancia_km"] = round(distancia, 3)
        item["vetor"] = vetor
        resultado.append(item)
    return sorted(resultado, key=lambda item: item["distancia_km"])
