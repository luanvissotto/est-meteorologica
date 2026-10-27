from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.models import Alerta, Estacao, Leitura
from app.schemas import LeituraCreate
from app.stats import resumo_serie
from app.validators import classificar_qualidade_ar, gerar_alertas_climaticos, validar_leitura


class ErroNegocio(Exception):
    def __init__(self, mensagem: str, codigo: int = 400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo


def obter_estacao_por_chave(db: Session, chave_api: str) -> Estacao:
    estacao = db.query(Estacao).filter(Estacao.chave_api == chave_api).first()
    if estacao is None:
        raise ErroNegocio("Chave de API inválida.", 401)
    if not estacao.ativa:
        raise ErroNegocio("A estação está inativa e não pode enviar leituras.", 403)
    return estacao


def ultima_leitura_estacao(db: Session, estacao_id: int) -> Optional[Leitura]:
    return (
        db.query(Leitura)
        .filter(Leitura.estacao_id == estacao_id)
        .order_by(desc(Leitura.coletada_em))
        .first()
    )


def registrar_leitura(
    db: Session,
    payload: LeituraCreate,
    chave_api: Optional[str],
    origem_padrao: str = "http",
) -> Leitura:
    estacao: Optional[Estacao] = None
    if chave_api:
        estacao = obter_estacao_por_chave(db, chave_api)
        if payload.estacao_id and payload.estacao_id != estacao.id:
            raise ErroNegocio("O identificador da estação não corresponde à chave de API.", 403)
    elif payload.estacao_id:
        estacao = db.query(Estacao).filter(Estacao.id == payload.estacao_id).first()
        if estacao is None:
            raise ErroNegocio("Estação não encontrada.", 404)
        if not estacao.ativa:
            raise ErroNegocio("A estação está inativa e não pode enviar leituras.", 403)
    else:
        raise ErroNegocio("Informe a chave de API ou o identificador da estação.", 400)

    anterior = ultima_leitura_estacao(db, estacao.id)
    anterior_dict = None
    if anterior is not None:
        anterior_dict = {
            "temperatura": anterior.temperatura,
            "umidade": anterior.umidade,
            "pressao": anterior.pressao,
            "qualidade_ar": anterior.qualidade_ar,
            "luminosidade": anterior.luminosidade,
            "pluviometria": anterior.pluviometria,
        }

    resultado = validar_leitura(
        payload.temperatura,
        payload.umidade,
        payload.pressao,
        payload.qualidade_ar,
        payload.luminosidade,
        payload.pluviometria,
        anterior_dict,
    )
    iqa, classificacao = classificar_qualidade_ar(payload.qualidade_ar)
    instante = payload.coletada_em or datetime.now(timezone.utc)

    leitura = Leitura(
        estacao_id=estacao.id,
        temperatura=payload.temperatura,
        umidade=payload.umidade,
        pressao=payload.pressao,
        qualidade_ar=payload.qualidade_ar,
        indice_qualidade_ar=iqa,
        classificacao_ar=classificacao,
        luminosidade=payload.luminosidade,
        pluviometria=payload.pluviometria,
        valida=resultado.valida,
        flags_validacao=",".join(resultado.flags),
        origem=payload.origem or origem_padrao,
        coletada_em=instante,
    )
    db.add(leitura)
    db.flush()

    if resultado.valida:
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
    db.refresh(leitura)
    return leitura


def listar_leituras(
    db: Session,
    estacao_id: Optional[int] = None,
    apenas_validas: bool = False,
    limite: int = 200,
) -> list[Leitura]:
    consulta = db.query(Leitura).options(joinedload(Leitura.estacao))
    if estacao_id is not None:
        consulta = consulta.filter(Leitura.estacao_id == estacao_id)
    if apenas_validas:
        consulta = consulta.filter(Leitura.valida.is_(True))
    return consulta.order_by(desc(Leitura.coletada_em)).limit(limite).all()


def ultimas_por_estacao(db: Session) -> list[Leitura]:
    subconsulta = (
        db.query(Leitura.estacao_id, func.max(Leitura.id).label("max_id"))
        .group_by(Leitura.estacao_id)
        .subquery()
    )
    return (
        db.query(Leitura)
        .options(joinedload(Leitura.estacao))
        .join(subconsulta, Leitura.id == subconsulta.c.max_id)
        .all()
    )


def calcular_estatisticas(db: Session, estacao_id: Optional[int], periodo_horas: int) -> dict:
    inicio = datetime.now(timezone.utc) - timedelta(hours=periodo_horas)
    consulta = db.query(Leitura).filter(Leitura.valida.is_(True), Leitura.coletada_em >= inicio)
    if estacao_id is not None:
        consulta = consulta.filter(Leitura.estacao_id == estacao_id)
    leituras = consulta.all()
    return {
        "estacao_id": estacao_id,
        "periodo_horas": periodo_horas,
        "amostras_validas": len(leituras),
        "temperatura": resumo_serie(item.temperatura for item in leituras),
        "umidade": resumo_serie(item.umidade for item in leituras),
        "pressao": resumo_serie(item.pressao for item in leituras),
        "qualidade_ar": resumo_serie(item.qualidade_ar for item in leituras),
        "luminosidade": resumo_serie(item.luminosidade for item in leituras),
        "pluviometria": resumo_serie(item.pluviometria for item in leituras),
    }


def resumo_painel(db: Session) -> dict:
    agora = datetime.now(timezone.utc)
    inicio_24h = agora - timedelta(hours=24)
    total_estacoes = db.query(func.count(Estacao.id)).scalar() or 0
    estacoes_ativas = db.query(func.count(Estacao.id)).filter(Estacao.ativa.is_(True)).scalar() or 0
    total_leituras = db.query(func.count(Leitura.id)).scalar() or 0
    alertas_ativos = db.query(func.count(Alerta.id)).filter(Alerta.ativo.is_(True)).scalar() or 0
    ultima = db.query(func.max(Leitura.coletada_em)).scalar()
    medias = (
        db.query(
            func.avg(Leitura.temperatura),
            func.avg(Leitura.umidade),
            func.avg(Leitura.qualidade_ar),
            func.sum(Leitura.pluviometria),
        )
        .filter(Leitura.valida.is_(True), Leitura.coletada_em >= inicio_24h)
        .first()
    )
    return {
        "total_estacoes": total_estacoes,
        "estacoes_ativas": estacoes_ativas,
        "total_leituras": total_leituras,
        "alertas_ativos": alertas_ativos,
        "ultima_atualizacao": ultima,
        "media_temperatura": round(medias[0], 2) if medias and medias[0] is not None else None,
        "media_umidade": round(medias[1], 2) if medias and medias[1] is not None else None,
        "media_qualidade_ar": round(medias[2], 2) if medias and medias[2] is not None else None,
        "acumulado_chuva_24h": round(medias[3], 2) if medias and medias[3] is not None else None,
    }
