"""
FastAPI Main Application

Aplicación principal de FastAPI con configuración completa.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from src.infrastructure.config import settings
from src.infrastructure.database.config import (
    create_db_and_tables,
    check_db_connection,
    get_db_info
)
from src.presentation.api.v1 import invoices, companies, health

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==============================================================================
# LIFESPAN EVENTS
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: ejecuta código al inicio y cierre de la aplicación.

    Startup:
    - Verificar conexión a BD
    - Crear tablas (solo en desarrollo)
    - Log de configuración

    Shutdown:
    - Cleanup si es necesario
    """
    # STARTUP
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Mode: {settings.mode}")
    logger.info("=" * 60)

    # Verificar conexión a BD
    if check_db_connection():
        logger.info("✓ Database connection successful")
        db_info = get_db_info()
        logger.info(f"  Database: {db_info['database_url']}")
        logger.info(f"  Type: {'SQLite' if db_info['is_sqlite'] else 'SQL Server'}")
    else:
        logger.error("✗ Database connection failed!")

    # En desarrollo, crear tablas automáticamente
    if settings.is_development:
        logger.info("Creating database tables (development mode)...")
        create_db_and_tables()
        logger.info("✓ Tables created")

    yield

    # SHUTDOWN
    logger.info("Shutting down application...")


# ==============================================================================
# FASTAPI APPLICATION
# ==============================================================================

app = FastAPI(
    title=settings.app_name,
    description="""
    # Invokox Backend API

    Sistema de procesamiento inteligente de facturas con OCR/AI.

    ## Características

    - 🚀 **Modo Dual**: Standalone (Electron + SQLite) o Client-Server (Web + SQL Server)
    - 🤖 **OCR/AI**: PaddleOCR, Docling, Tesseract para extracción automática
    - 📊 **Clean Architecture**: Domain, Application, Infrastructure, Presentation
    - 🔄 **Async**: Celery + Redis para tareas largas (OCR)
    - 🔐 **Seguro**: JWT authentication, RBAC (futuro)
    - 📝 **Validado**: Pydantic schemas con type hints
    - 🧪 **Testeable**: >80% coverage objetivo

    ## Stack Tecnológico

    - **Framework**: FastAPI 0.104+
    - **ORM**: SQLModel (SQLAlchemy + Pydantic)
    - **Database**: SQLite (dev) / SQL Server (prod)
    - **Queue**: Celery + Redis
    - **OCR/AI**: PaddleOCR, PyTorch, Transformers

    ## Arquitectura

    ```
    Domain Layer (Entities, Value Objects)
           ↓
    Application Layer (Use Cases, Interfaces)
           ↓
    Infrastructure Layer (Repositories, Services)
           ↓
    Presentation Layer (API Endpoints) ← YOU ARE HERE
    ```

    ## Endpoints Principales

    - `/api/v1/invoices`: Gestión de facturas
    - `/api/v1/companies`: Gestión de empresas
    - `/api/v1/tasks`: Estado de tareas Celery
    - `/health`: Health check
    """,
    version=settings.app_version,
    docs_url="/docs" if settings.is_development else None,  # Deshabilitar en prod
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
)


# ==============================================================================
# MIDDLEWARE
# ==============================================================================

# CORS - Permitir requests desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# GZip - Compresión de responses
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Middleware personalizado para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware que registra todas las requests con tiempo de procesamiento.
    """
    start_time = time.time()

    # Procesar request
    response = await call_next(request)

    # Calcular tiempo
    process_time = time.time() - start_time

    # Log
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    # Agregar header con tiempo de procesamiento
    response.headers["X-Process-Time"] = str(process_time)

    return response


# ==============================================================================
# EXCEPTION HANDLERS
# ==============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handler para errores de validación de negocio."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "type": "validation_error"
        }
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler para recursos no encontrados."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handler para errores internos del servidor."""
    logger.error(f"Internal error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if settings.is_production else str(exc),
            "type": "internal_error"
        }
    )


# ==============================================================================
# ROUTERS
# ==============================================================================

# Incluir routers de v1
app.include_router(
    health.router,
    tags=["Health"]
)

app.include_router(
    invoices.router,
    prefix=settings.api_v1_prefix,
    tags=["Invoices"]
)

app.include_router(
    companies.router,
    prefix=settings.api_v1_prefix,
    tags=["Companies"]
)


# ==============================================================================
# ROOT ENDPOINT
# ==============================================================================

@app.get("/")
async def root():
    """
    Root endpoint con información de la API.
    """
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "mode": settings.mode,
        "environment": settings.environment,
        "docs": "/docs" if settings.is_development else "Documentation disabled in production",
        "health": "/health"
    }


# ==============================================================================
# PARA EJECUTAR DIRECTAMENTE
# ==============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0" if settings.is_server_mode else "127.0.0.1",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
