import secrets
from sqlalchemy.orm import Session

from app.models import Estacao


ESTACOES_INICIAIS = [
    {
        "nome": "Estação Meteorológica ESP32",
        "descricao": "Estação física baseada no microcontrolador ESP32.",
        "bairro": "Local",
        "cidade": "Local",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "altitude_m": 760.0,
        "chave_api": "estacao-esp32-demo-key-001",
    },
]


def gerar_chave_api() -> str:
    return secrets.token_hex(16)


def popular_banco(db: Session) -> None:
    """Inicializa a base com apenas a estação ESP32 cadastrada, sem leituras falsas."""
    if db.query(Estacao).count() > 0:
        return

    for dados in ESTACOES_INICIAIS:
        estacao = Estacao(**dados, ativa=True)
        db.add(estacao)
    db.commit()
