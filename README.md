# Invokox - Sistema de Procesamiento de Facturas v2.0

Sistema de gestión y procesamiento automatizado de facturas con OCR/AI, diseñado para funcionar en modo standalone (Electron) o cliente-servidor.

## 🏗️ Arquitectura

- **Clean Architecture**: Separación por capas (Domain, Application, Infrastructure, Presentation)
- **Modo Dual**: Standalone (Electron + SQLite) o Client-Server (Web + SQL Server)
- **Procesamiento Asíncrono**: Celery + Redis para tareas largas (OCR/AI)

## 📂 Estructura del Proyecto

```
Invokox/
├── backend/          # FastAPI backend (Python 3.11+)
├── frontend/         # React 18 + TypeScript + Vite
├── electron/         # Electron wrapper (modo standalone)
├── workers/          # Celery workers (procesamiento asíncrono)
├── shared/           # Código compartido entre frontend/backend
├── docs/             # Documentación técnica
├── scripts/          # Scripts de utilidad
├── docker/           # Dockerfiles y compose
└── data/             # Datos locales (SQLite, uploads)
```

## 🚀 Stack Tecnológico

### Backend
- **Framework**: FastAPI 0.104+
- **Base de Datos**: SQLite (dev) / SQL Server (prod)
- **ORM**: SQLModel + Alembic
- **Queue**: Celery + Redis
- **OCR/AI**: PaddleOCR, Docling, Tesseract

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Estado**: Zustand + TanStack Query
- **Styling**: TailwindCSS 4
- **Forms**: React Hook Form + Zod

### Desktop
- **Framework**: Electron 28+
- **Auto-update**: electron-updater

### Testing
- **Backend**: pytest + pytest-asyncio + pytest-cov
- **Frontend**: Vitest + Playwright
- **Coverage**: >80%

## 📋 Requisitos

- Python 3.11+
- Node.js 20+
- Redis 7+
- SQL Server 2022+ (producción) o SQLite (desarrollo)
- GPU NVIDIA (opcional, para OCR acelerado)

## 🛠️ Instalación

```bash
# Backend
cd backend
pip install poetry
poetry install

# Frontend
cd frontend
npm install

# Electron
cd electron
npm install
```

## 🏃 Ejecución

### Modo Desarrollo (Standalone)
```bash
# Terminal 1: Backend
cd backend
poetry run uvicorn src.presentation.api.main:app --reload

# Terminal 2: Redis
docker run -p 6379:6379 redis:7-alpine

# Terminal 3: Celery Worker
cd backend
poetry run celery -A workers.tasks worker --loglevel=info

# Terminal 4: Frontend
cd frontend
npm run dev

# Terminal 5: Electron
cd electron
npm run dev
```

### Modo Producción (Server)
```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 📚 Documentación

- [Arquitectura](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [Deployment](docs/deployment/README.md)

## 🧪 Testing

```bash
# Backend tests
cd backend
poetry run pytest tests/ -v --cov=src

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

## 📝 Licencia

Propietario - Todos los derechos reservados

## 👥 Equipo

Equipo de Desarrollo Invokox

---

**Versión**: 2.0.0
**Última actualización**: 2025-11-18
