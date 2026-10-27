import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Alerta, Estacao, Leitura
from app.validators import classificar_qualidade_ar, gerar_alertas_climaticos, validar_leitura


ESTACOES_INICIAIS = [
    {
        "nome": "Praça da Sé",
        "descricao": "Estação central para monitoramento do microclima do centro histórico.",
        "bairro": "Sé",
        "cidade": "São Paulo",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "altitude_m": 760.0,
        "chave_api": "estacao-se-demo-key-001",
    },
    {
        "nome": "Parque Ibirapuera",
        "descricao": "Monitoramento de área verde e qualidade do ar para lazer urbano.",
        "bairro": "Moema",
        "cidade": "São Paulo",
        "latitude": -23.5874,
        "longitude": -46.6576,
        "altitude_m": 750.0,
        "chave_api": "estacao-ibirapuera-demo-key-002",
    },
    {
        "nome": "Avenida Paulista",
        "descricao": "Estação de corredor viário com alta densidade de tráfego.",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "latitude": -23.5614,
        "longitude": -46.6558,
        "altitude_m": 800.0,
        "chave_api": "estacao-paulista-demo-key-003",
    },
    {
        "nome": "Pinheiros",
        "descricao": "Monitoramento de fundo de vale e umidade relativa.",
        "bairro": "Pinheiros",
        "cidade": "São Paulo",
        "latitude": -23.5675,
        "longitude": -46.7019,
        "altitude_m": 730.0,
        "chave_api": "estacao-pinheiros-demo-key-004",
    },
]


def gerar_chave_api() -> str:
    return secrets.token_hex(16)


def popular_banco(db: Session) -> None:
    if db.query(Estacao).count() > 0:
        return

    estacoes = []
    for dados in ESTACOES_INICIAIS:
        estacao = Estacao(**dados, ativa=True)
        db.add(estacao)
        estacoes.append(estacao)
    db.flush()

    agora = datetime.now(timezone.utc)
    for indice, estacao in enumerate(estacoes):
        for horas in range(24, -1, -1):
            instante = agora - timedelta(hours=horas, minutes=indice * 3)
            temperatura = 22.5 + indice * 0.8 + (24 - horas) * 0.12
            umidade = 62.0 - indice * 2 + (horas % 5)
            pressao = 1014.0 - indice * 0.6
            qualidade_ar = 90.0 + indice * 35 + (horas % 7) * 4
            luminosidade = max(5.0, 85.0 - abs(12 - ((agora.hour - horas) % 24)) * 6)
            pluviometria = 2.4 if horas in {3, 4, 18} and indice == 3 else 0.1 * (indice == 3)

            resultado = validar_leitura(
                temperatura,
                umidade,
                pressao,
                qualidade_ar,
                luminosidade,
                pluviometria,
            )
            iqa, classificacao = classificar_qualidade_ar(qualidade_ar)
            leitura = Leitura(
                estacao_id=estacao.id,
                temperatura=round(temperatura, 2),
                umidade=round(umidade, 2),
                pressao=round(pressao, 2),
                qualidade_ar=round(qualidade_ar, 2),
                indice_qualidade_ar=iqa,
                classificacao_ar=classificacao,
                luminosidade=round(luminosidade, 2),
                pluviometria=round(pluviometria, 2),
                valida=resultado.valida,
                flags_validacao=",".join(resultado.flags),
                origem="seed",
                coletada_em=instante,
            )
            db.add(leitura)
            db.flush()

            if horas == 0:
                for alerta_dados in gerar_alertas_climaticos(
                    leitura.temperatura,
                    leitura.umidade,
                    leitura.pressao,
                    leitura.qualidade_ar,
                    leitura.pluviometria,
                    leitura.indice_qualidade_ar,
                ):
                    db.add(
                        Alerta(
                            estacao_id=estacao.id,
                            leitura_id=leitura.id,
                            tipo=alerta_dados["tipo"],
                            severidade=alerta_dados["severidade"],
                            mensagem=alerta_dados["mensagem"],
                            valor=alerta_dados["valor"],
                            limiar=alerta_dados["limiar"],
                            ativo=True,
                        )
                    )

    db.commit()
