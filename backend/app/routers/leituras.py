from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EstatisticasResposta, LeituraCreate, LeituraResposta
from app.services.leituras import (
    ErroNegocio,
    calcular_estatisticas,
    listar_leituras,
    registrar_leitura,
    ultimas_por_estacao,
)

router = APIRouter(prefix="/api/v1/leituras", tags=["Leituras"])


@router.post("", response_model=LeituraResposta, status_code=201)
def receber_leitura(
    payload: LeituraCreate,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    try:
        return registrar_leitura(db, payload, x_api_key)
    except ErroNegocio as erro:
        raise HTTPException(status_code=erro.codigo, detail=erro.mensagem) from erro
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=f"Dados de sensor inválidos: {erro}") from erro
    except Exception as erro:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao registrar leitura: {erro}") from erro


@router.get("", response_model=List[LeituraResposta])
def obter_leituras(
    estacao_id: Optional[int] = Query(default=None),
    apenas_validas: bool = Query(default=True),
    limite: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    try:
        return listar_leituras(db, estacao_id, apenas_validas, limite)
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar leituras: {erro}") from erro


@router.get("/ultimas", response_model=List[LeituraResposta])
def obter_ultimas(db: Session = Depends(get_db)):
    try:
        return ultimas_por_estacao(db)
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar últimas leituras: {erro}") from erro


@router.get("/estatisticas", response_model=EstatisticasResposta)
def obter_estatisticas(
    estacao_id: Optional[int] = Query(default=None),
    periodo_horas: int = Query(default=24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    try:
        return calcular_estatisticas(db, estacao_id, periodo_horas)
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular estatísticas: {erro}") from erro
