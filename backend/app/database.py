from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

url_banco = settings.database_url
# Compatibilidade com provedores de nuvem (Render, Railway, Heroku) que fornecem postgres://
if url_banco.startswith("postgres://"):
    url_banco = url_banco.replace("postgres://", "postgresql+psycopg2://", 1)
elif url_banco.startswith("postgresql://") and "+psycopg2" not in url_banco:
    url_banco = url_banco.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}
if url_banco.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    url_banco,
    connect_args=connect_args,
    pool_pre_ping=True,
)

if url_banco.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def definir_pragma_sqlite(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
