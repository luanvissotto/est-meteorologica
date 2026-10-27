from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class Estacao(Base):
    __tablename__ = "estacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, default="", nullable=False)
    bairro: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    cidade: Mapped[str] = mapped_column(String(120), default="São Paulo", nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude_m: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    chave_api: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)

    leituras = relationship("Leitura", back_populates="estacao", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="estacao", cascade="all, delete-orphan")


class Leitura(Base):
    __tablename__ = "leituras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    estacao_id: Mapped[int] = mapped_column(ForeignKey("estacoes.id"), nullable=False, index=True)
    temperatura: Mapped[float] = mapped_column(Float, nullable=False)
    umidade: Mapped[float] = mapped_column(Float, nullable=False)
    pressao: Mapped[float] = mapped_column(Float, nullable=False)
    qualidade_ar: Mapped[float] = mapped_column(Float, nullable=False)
    indice_qualidade_ar: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    classificacao_ar: Mapped[str] = mapped_column(String(40), default="desconhecido", nullable=False)
    luminosidade: Mapped[float] = mapped_column(Float, nullable=False)
    pluviometria: Mapped[float] = mapped_column(Float, nullable=False)
    valida: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    flags_validacao: Mapped[str] = mapped_column(Text, default="", nullable=False)
    origem: Mapped[str] = mapped_column(String(40), default="http", nullable=False)
    coletada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc, index=True)

    estacao = relationship("Estacao", back_populates="leituras")
    alertas = relationship("Alerta", back_populates="leitura")


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    estacao_id: Mapped[int] = mapped_column(ForeignKey("estacoes.id"), nullable=False, index=True)
    leitura_id: Mapped[int] = mapped_column(ForeignKey("leituras.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(80), nullable=False)
    severidade: Mapped[str] = mapped_column(String(20), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    limiar: Mapped[float] = mapped_column(Float, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc, index=True)

    estacao = relationship("Estacao", back_populates="alertas")
    leitura = relationship("Leitura", back_populates="alertas")
