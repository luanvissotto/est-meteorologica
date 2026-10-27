from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class EstacaoBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=120)
    descricao: str = ""
    bairro: str = ""
    cidade: str = "São Paulo"
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    ativa: bool = True

    @field_validator("latitude")
    @classmethod
    def validar_latitude(cls, valor: float) -> float:
        if valor < -90 or valor > 90:
            raise ValueError("Latitude deve estar entre -90 e 90.")
        return valor

    @field_validator("longitude")
    @classmethod
    def validar_longitude(cls, valor: float) -> float:
        if valor < -180 or valor > 180:
            raise ValueError("Longitude deve estar entre -180 e 180.")
        return valor


class EstacaoCreate(EstacaoBase):
    chave_api: Optional[str] = Field(default=None, min_length=8, max_length=64)


class EstacaoResposta(EstacaoBase):
    id: int
    criada_em: datetime

    model_config = {"from_attributes": True}


class EstacaoPublica(BaseModel):
    id: int
    nome: str
    descricao: str
    bairro: str
    cidade: str
    latitude: float
    longitude: float
    altitude_m: float
    ativa: bool

    model_config = {"from_attributes": True}


class LeituraCreate(BaseModel):
    estacao_id: Optional[int] = None
    temperatura: float
    umidade: float
    pressao: float
    qualidade_ar: float
    luminosidade: float
    pluviometria: float
    origem: str = "http"
    coletada_em: Optional[datetime] = None


class LeituraResposta(BaseModel):
    id: int
    estacao_id: int
    temperatura: float
    umidade: float
    pressao: float
    qualidade_ar: float
    indice_qualidade_ar: int
    classificacao_ar: str
    luminosidade: float
    pluviometria: float
    valida: bool
    flags_validacao: str
    origem: str
    coletada_em: datetime

    model_config = {"from_attributes": True}


class AlertaResposta(BaseModel):
    id: int
    estacao_id: int
    leitura_id: Optional[int]
    tipo: str
    severidade: str
    mensagem: str
    valor: float
    limiar: float
    ativo: bool
    criado_em: datetime
    estacao_nome: Optional[str] = None

    model_config = {"from_attributes": True}


class EstatisticaCampo(BaseModel):
    quantidade: int
    minimo: Optional[float]
    maximo: Optional[float]
    media: Optional[float]
    mediana: Optional[float]
    desvio_padrao: Optional[float]


class EstatisticasResposta(BaseModel):
    estacao_id: Optional[int]
    periodo_horas: int
    amostras_validas: int
    temperatura: EstatisticaCampo
    umidade: EstatisticaCampo
    pressao: EstatisticaCampo
    qualidade_ar: EstatisticaCampo
    luminosidade: EstatisticaCampo
    pluviometria: EstatisticaCampo


class LeituraComEstacao(LeituraResposta):
    estacao: EstacaoPublica


class PainelResumo(BaseModel):
    total_estacoes: int
    estacoes_ativas: int
    total_leituras: int
    alertas_ativos: int
    ultima_atualizacao: Optional[datetime]
    media_temperatura: Optional[float]
    media_umidade: Optional[float]
    media_qualidade_ar: Optional[float]
    acumulado_chuva_24h: Optional[float]


class EstacaoProxima(EstacaoPublica):
    distancia_km: float
    vetor: dict
    ultima_leitura: Optional[LeituraResposta] = None
