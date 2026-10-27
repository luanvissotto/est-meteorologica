from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.geo import coordenadas_validas, ordenar_por_proximidade
from app.models import Estacao
from app.schemas import EstacaoCreate, EstacaoProxima, EstacaoPublica, EstacaoResposta, LeituraResposta
from app.seed import gerar_chave_api
from app.services.leituras import ultima_leitura_estacao

router = APIRouter(prefix="/api/v1/estacoes", tags=["Estações"])


@router.get("", response_model=List[EstacaoPublica])
def listar_estacoes(apenas_ativas: bool = Query(default=True), db: Session = Depends(get_db)):
    try:
        consulta = db.query(Estacao)
        if apenas_ativas:
            consulta = consulta.filter(Estacao.ativa.is_(True))
        return consulta.order_by(Estacao.nome.asc()).all()
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao listar estações: {erro}") from erro


@router.get("/proximas", response_model=List[EstacaoProxima])
def estacoes_proximas(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db),
):
    try:
        if not coordenadas_validas(latitude, longitude):
            raise HTTPException(status_code=400, detail="Coordenadas inválidas.")
        estacoes = db.query(Estacao).filter(Estacao.ativa.is_(True)).all()
        payload = [
            {
                "id": estacao.id,
                "nome": estacao.nome,
                "descricao": estacao.descricao,
                "bairro": estacao.bairro,
                "cidade": estacao.cidade,
                "latitude": estacao.latitude,
                "longitude": estacao.longitude,
                "altitude_m": estacao.altitude_m,
                "ativa": estacao.ativa,
            }
            for estacao in estacoes
        ]
        ordenadas = ordenar_por_proximidade(latitude, longitude, payload)
        resposta = []
        for item in ordenadas:
            estacao_id = item["id"]
            ultima = ultima_leitura_estacao(db, estacao_id)
            item["ultima_leitura"] = LeituraResposta.model_validate(ultima) if ultima else None
            resposta.append(EstacaoProxima(**item))
        return resposta
    except HTTPException:
        raise
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular proximidade: {erro}") from erro


@router.get("/{estacao_id}", response_model=EstacaoPublica)
def obter_estacao(estacao_id: int, db: Session = Depends(get_db)):
    estacao = db.query(Estacao).filter(Estacao.id == estacao_id).first()
    if estacao is None:
        raise HTTPException(status_code=404, detail="Estação não encontrada.")
    return estacao


@router.post("", response_model=EstacaoResposta, status_code=201)
def criar_estacao(
    payload: EstacaoCreate,
    x_admin_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    try:
        if x_admin_token not in {"admin-demo", "cidades-inteligentes"}:
            raise HTTPException(
                status_code=401,
                detail="Informe o cabeçalho X-Admin-Token com o valor de demonstração 'admin-demo'.",
            )
        chave = payload.chave_api or gerar_chave_api()
        existente = db.query(Estacao).filter(Estacao.chave_api == chave).first()
        if existente:
            raise HTTPException(status_code=409, detail="Já existe uma estação com esta chave de API.")
        estacao = Estacao(
            nome=payload.nome,
            descricao=payload.descricao,
            bairro=payload.bairro,
            cidade=payload.cidade,
            latitude=payload.latitude,
            longitude=payload.longitude,
            altitude_m=payload.altitude_m,
            chave_api=chave,
            ativa=payload.ativa,
        )
        db.add(estacao)
        db.commit()
        db.refresh(estacao)
        return estacao
    except HTTPException:
        raise
    except Exception as erro:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar estação: {erro}") from erro
