import secrets
from sqlalchemy.orm import Session

from app.models import Estacao


ESTACOES_INICIAIS = [
    {
        "nome": "Estação Meteorológica ESP32",
        "descricao": "Estação física baseada no microcontrolador ESP32.",
        "bairro": "Centro",
        "cidade": "São José do Rio Preto",
        "latitude": -20.8113,
        "longitude": -49.3758,
        "altitude_m": 489.0,
        "chave_api": "estacao-esp32-demo-key-001",
    },
]


def gerar_chave_api() -> str:
    return secrets.token_hex(16)


def popular_banco(db: Session) -> None:
    """Inicializa a base com a estação em São José do Rio Preto - SP."""
    if db.query(Estacao).count() > 0:
        estacao = db.query(Estacao).filter(Estacao.id == 1).first()
        if estacao and (abs(estacao.latitude - (-23.5505)) < 0.01):
            estacao.cidade = "São José do Rio Preto"
            estacao.bairro = "Centro"
            estacao.latitude = -20.8113
            estacao.longitude = -49.3758
            estacao.altitude_m = 489.0
            db.commit()
        return

    for dados in ESTACOES_INICIAIS:
        estacao = Estacao(**dados, ativa=True)
        db.add(estacao)
    db.commit()
