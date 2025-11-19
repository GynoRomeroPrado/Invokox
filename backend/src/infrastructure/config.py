"""
Application Configuration

Gestión centralizada de configuración usando Pydantic Settings.
"""

import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación.

    Lee variables de entorno con validación automática.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ==================================================================
    # APPLICATION
    # ==================================================================
    app_name: str = "Invokox Backend"
    app_version: str = "2.0.0"
    mode: Literal["standalone", "server"] = "standalone"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # ==================================================================
    # API
    # ==================================================================
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # ==================================================================
    # DATABASE
    # ==================================================================
    database_url: str = "sqlite:///./data/invokox.db"
    sql_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # SQL Server (para modo server)
    sql_server_host: str = "localhost"
    sql_server_port: str = "1433"
    sql_server_database: str = "invokox_db"
    sql_server_user: str = "sa"
    sql_server_password: str = "YourStrong!Passw0rd"
    sql_server_driver: str = "ODBC Driver 18 for SQL Server"

    # ==================================================================
    # REDIS
    # ==================================================================
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # ==================================================================
    # SECURITY
    # ==================================================================
    secret_key: str = "your-secret-key-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ==================================================================
    # OCR/AI
    # ==================================================================
    ocr_engine: Literal["paddleocr", "docling", "tesseract"] = "paddleocr"
    ocr_language: str = "es"
    use_gpu: bool = False
    model_path: str = "./models"

    # ==================================================================
    # FILE STORAGE
    # ==================================================================
    upload_dir: str = "./data/uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list[str] = ["pdf", "png", "jpg", "jpeg"]

    # ==================================================================
    # SYNC (para modo dual)
    # ==================================================================
    server_api_url: str = "https://api.company.local"
    sync_interval_minutes: int = 15
    sync_batch_size: int = 100

    # ==================================================================
    # LOGGING
    # ==================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_file: str = "./logs/app.log"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"

    # ==================================================================
    # COMPUTED PROPERTIES
    # ==================================================================

    @property
    def is_development(self) -> bool:
        """Verifica si está en modo desarrollo."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Verifica si está en modo producción."""
        return self.environment == "production"

    @property
    def is_standalone_mode(self) -> bool:
        """Verifica si está en modo standalone."""
        return self.mode == "standalone"

    @property
    def is_server_mode(self) -> bool:
        """Verifica si está en modo server."""
        return self.mode == "server"

    def get_cors_origins(self) -> list[str]:
        """
        Retorna lista de orígenes CORS.

        En producción, usar solo orígenes específicos.
        """
        if self.is_production:
            return self.cors_origins
        # En desarrollo, permitir localhost
        return self.cors_origins + [
            "http://localhost:*",
            "http://127.0.0.1:*"
        ]


# ==================================================================
# SINGLETON
# ==================================================================

_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Obtiene la instancia singleton de configuración.

    Esta función se puede usar como dependencia en FastAPI:
    ```python
    @app.get("/config")
    def get_config(settings: Settings = Depends(get_settings)):
        return {"mode": settings.mode}
    ```
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Para importación directa
settings = get_settings()
