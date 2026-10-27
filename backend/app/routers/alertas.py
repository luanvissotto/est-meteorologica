from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Alerta
from app.schemas import AlertaResposta

router = APIRouter(prefix="/api/v1/alertas", tags=["Alertas"])


@router.get("", response_model=List[AlertaResposta])
def listar_alertas(
    apenas_ativos: bool = Query(default=True),
    estacao_id: Optional[int] = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    try:
        consulta = db.query(Alerta).options(joinedload(Alerta.estacao))
        if apenas_ativos:
            consulta = consulta.filter(Alerta.ativo.is_(True))
        if estacao_id is not None:
            consulta = consulta.filter(Alerta.estacao_id == estacao_id)
        registros = consulta.order_by(desc(Alerta.criado_em)).limit(limite).all()
        resposta = []
        for alerta in registros:
            item = AlertaResposta.model_validate(alerta)
            item.estacao_nome = alerta.estacao.nome if alerta.estacao else None
            resposta.append(item)
        return resposta
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao listar alertas: {erro}") from erro
