from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.mqtt_ingest import iniciar_cliente_mqtt
from app.routers import alertas, estacoes, leituras, painel
from app.seed import popular_banco

settings = get_settings()


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.seed_on_startup:
        db = SessionLocal()
        try:
            popular_banco(db)
        finally:
            db.close()
    iniciar_cliente_mqtt()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "API pública da Estação Meteorológica Inteligente para Cidades Inteligentes. "
        "Recebe dados do ESP32 via HTTP ou MQTT, valida leituras, gera alertas e "
        "alimenta o dashboard cidadão."
    ),
    version="1.0.0",
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(estacoes.router)
app.include_router(leituras.router)
app.include_router(alertas.router)
app.include_router(painel.router)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/api/v1/saude")
def saude():
    return {
        "status": "ok",
        "servico": settings.app_name,
        "ambiente": settings.app_env,
        "mqtt": settings.mqtt_enabled,
    }


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def pagina_inicial():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/mapa")
    def pagina_mapa():
        return FileResponse(FRONTEND_DIR / "mapa.html")

    @app.get("/historico")
    def pagina_historico():
        return FileResponse(FRONTEND_DIR / "historico.html")

    @app.get("/alertas")
    def pagina_alertas():
        return FileResponse(FRONTEND_DIR / "alertas.html")

    @app.get("/sobre")
    def pagina_sobre():
        return FileResponse(FRONTEND_DIR / "sobre.html")
