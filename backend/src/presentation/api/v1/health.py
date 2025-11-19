"""
Health Check Endpoints

Endpoints para verificar el estado de la aplicación y sus dependencias.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session
from datetime import datetime
from typing import Dict, Any

from src.infrastructure.config import get_settings, Settings
from src.infrastructure.database.config import (
    get_session_dependency,
    check_db_connection,
    get_db_info
)

router = APIRouter()


@router.get("/health")
async def health_check(
    session: Session = Depends(get_session_dependency),
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    Health check endpoint.

    Verifica el estado de:
    - API (responde)
    - Database (conexión)
    - Configuración básica

    Returns:
        dict con status y detalles de cada componente
    """
    # Verificar database
    db_healthy = check_db_connection()
    db_info = get_db_info()

    # TODO: Verificar Redis cuando se implemente Celery
    redis_healthy = None  # await check_redis_connection()

    # Status general
    overall_status = "healthy" if db_healthy else "unhealthy"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "mode": settings.mode,
        "environment": settings.environment,
        "components": {
            "api": {
                "status": "healthy",
                "message": "API is responding"
            },
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "type": "sqlite" if db_info["is_sqlite"] else "sqlserver",
                "url": db_info["database_url"]
            },
            "redis": {
                "status": "unknown",
                "message": "Not implemented yet"
            }
        }
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe para Kubernetes.

    Verifica si la aplicación está lista para recibir tráfico.
    """
    db_ready = check_db_connection()

    return {
        "ready": db_ready,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe para Kubernetes.

    Verifica si la aplicación está viva (no colgada).
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
