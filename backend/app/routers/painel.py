from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PainelResumo
from app.services.leituras import resumo_painel

router = APIRouter(prefix="/api/v1/painel", tags=["Painel"])


@router.get("/resumo", response_model=PainelResumo)
def obter_resumo(db: Session = Depends(get_db)):
    try:
        return resumo_painel(db)
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao montar o painel: {erro}") from erro
