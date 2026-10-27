from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Estação Meteorológica Inteligente"
    app_env: str = "development"
    database_url: str = "sqlite:///./estacao_meteorologica.db"
    cors_origins: str = "*"
    mqtt_enabled: bool = False
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "cidades-inteligentes/estacoes/+/leituras"
    mqtt_username: str = ""
    mqtt_password: str = ""
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    seed_on_startup: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def cors_origin_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origem.strip() for origem in self.cors_origins.split(",") if origem.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
