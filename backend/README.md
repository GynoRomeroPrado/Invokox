# Backend - FastAPI

Backend del sistema Invokox basado en FastAPI con arquitectura limpia.

## 📂 Estructura

```
backend/
├── src/
│   ├── domain/              # Capa de Dominio (Entidades, Value Objects)
│   │   ├── entities/        # Invoice, Company, InvoiceItem
│   │   └── value_objects/   # Money, TaxID, DateRange
│   ├── application/         # Capa de Aplicación (Casos de Uso)
│   │   ├── use_cases/       # CreateInvoice, ProcessOCR, ExportData
│   │   └── interfaces/      # Interfaces de repositorios y servicios
│   ├── infrastructure/      # Capa de Infraestructura
│   │   ├── repositories/    # Implementaciones de repositorios
│   │   ├── services/        # OCR, Storage, Sync
│   │   └── database/        # Configuración de BD, modelos SQLModel
│   └── presentation/        # Capa de Presentación (API)
│       └── api/
│           └── v1/          # Endpoints FastAPI v1
├── tests/
│   ├── unit/                # Tests unitarios (<1s)
│   ├── integration/         # Tests con BD (1-5s)
│   ├── e2e/                 # Tests end-to-end (10-60s)
│   └── fixtures/            # Datos de prueba, factories
├── alembic/                 # Migraciones de base de datos
│   ├── versions/            # Archivos de migración
│   └── scripts/             # Scripts SQL personalizados
├── pyproject.toml           # Dependencias Poetry
└── .env.example             # Variables de entorno ejemplo
```

## 🏗️ Arquitectura - Clean Architecture

### Domain Layer (Dominio)
- **Sin dependencias externas** (solo Python estándar)
- Entidades de negocio: `Invoice`, `Company`, `InvoiceItem`
- Value Objects: `Money`, `TaxID`, `Currency`
- Reglas de negocio puras

### Application Layer (Aplicación)
- Casos de uso: `CreateInvoiceUseCase`, `ProcessOCRUseCase`
- Interfaces (puertos): `IInvoiceRepository`, `IOCRService`
- Orquestación de lógica de negocio

### Infrastructure Layer (Infraestructura)
- Implementaciones de interfaces
- Repositorios SQLModel
- Servicios externos (OCR, Storage)
- Configuración de BD

### Presentation Layer (Presentación)
- Endpoints FastAPI
- DTOs (Pydantic schemas)
- Validación de requests/responses

## 🚀 Instalación

```bash
# Instalar Poetry (si no está instalado)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell
```

## 🔧 Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar variables de entorno
nano .env
```

Variables principales:
- `MODE`: `standalone` o `server`
- `DATABASE_URL`: Conexión a BD
- `REDIS_URL`: Conexión a Redis
- `SECRET_KEY`: Para JWT

## 🏃 Ejecución

```bash
# Desarrollo (con hot-reload)
poetry run uvicorn src.presentation.api.main:app --reload --host 127.0.0.1 --port 8000

# Producción
poetry run uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🗄️ Base de Datos

```bash
# Crear migración automática
poetry run alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
poetry run alembic upgrade head

# Rollback
poetry run alembic downgrade -1

# Ver historial
poetry run alembic history
```

## 🧪 Testing

```bash
# Todos los tests
poetry run pytest tests/ -v

# Solo unit tests (rápido)
poetry run pytest tests/unit -v

# Con cobertura
poetry run pytest tests/ --cov=src --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html
```

## 📊 API Documentation

Una vez ejecutando, acceder a:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 🔍 Linting y Formato

```bash
# Formatear código
poetry run black src/ tests/

# Linting
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/
```

## 📦 Dependencias Principales

- **fastapi**: Framework web asíncrono
- **uvicorn**: ASGI server
- **sqlmodel**: ORM (SQLAlchemy + Pydantic)
- **alembic**: Migraciones de BD
- **celery**: Procesamiento asíncrono
- **paddleocr**: OCR principal
- **pydantic**: Validación de datos
