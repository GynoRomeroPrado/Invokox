# 🐳 Docker Setup - Invokox V2.0

Guía completa para configurar y usar el entorno de desarrollo con Docker Compose.

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Servicios Incluidos](#servicios-incluidos)
- [Inicio Rápido](#inicio-rápido)
- [Configuración](#configuración)
- [Comandos Útiles](#comandos-útiles)
- [Estructura de Volúmenes](#estructura-de-volúmenes)
- [Puertos](#puertos)
- [Troubleshooting](#troubleshooting)

## 🔧 Requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (opcional, para usar comandos simplificados)

**Verificar instalación:**
```bash
docker --version
docker-compose --version
make --version
```

## 🏗️ Servicios Incluidos

### Backend Stack
- **Backend (FastAPI)**: API REST con hot-reload
- **Celery Worker**: Procesamiento asíncrono (OCR, emails)
- **Celery Beat**: Scheduler para tareas periódicas
- **Flower**: Dashboard de monitoreo de Celery

### Infraestructura
- **Redis**: Message broker y caché
- **PostgreSQL**: Base de datos principal (simula SQL Server)
- **SQL Server** (opcional): Base de datos para producción

### Frontend
- **Frontend (React + Vite)**: UI con hot-reload

## 🚀 Inicio Rápido

### Opción 1: Usando Make (Recomendado)

```bash
# Ver todos los comandos disponibles
make help

# Iniciar todos los servicios
make up

# Ver logs en tiempo real
make logs

# Detener servicios
make down
```

### Opción 2: Usando Docker Compose

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

## ⚙️ Configuración

### 1. Variables de Entorno

El archivo `docker-compose.yml` incluye configuraciones por defecto. Para personalizarlas:

**Backend:**
```yaml
environment:
  MODE: "server"
  ENVIRONMENT: "development"
  DEBUG: "true"
  DATABASE_URL: "postgresql://..."
  # ... más variables
```

**Frontend:**
```yaml
environment:
  VITE_API_URL: "http://localhost:8000/api/v1"
  VITE_MODE: "development"
```

### 2. Base de Datos

Por defecto usa **PostgreSQL**. Para cambiar a **SQL Server**:

1. Descomentar el servicio `sqlserver` en `docker-compose.yml`
2. Cambiar `DATABASE_URL` en el servicio `backend`:
   ```yaml
   DATABASE_URL: "mssql+pyodbc://sa:YourStrong!Passw0rd@sqlserver:1433/invokox_db?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
   ```
3. Actualizar dependencias en `depends_on`

### 3. OCR Configuration

```yaml
environment:
  OCR_ENGINE: "paddleocr"  # opciones: paddleocr, docling, tesseract
  USE_GPU: "false"  # cambiar a "true" si tienes GPU NVIDIA
```

## 📝 Comandos Útiles

### Gestión de Servicios

```bash
# Iniciar servicios
make up

# Detener servicios
make down

# Reiniciar servicios
make restart

# Ver estado de servicios
make ps

# Reconstruir imágenes
make build

# Reconstruir sin caché
make rebuild
```

### Logs

```bash
# Ver logs de todos los servicios
make logs

# Ver logs del backend
make logs-backend

# Ver logs del frontend
make logs-frontend

# Ver logs de Celery
make logs-celery
```

### Migraciones de Base de Datos

```bash
# Ejecutar migraciones pendientes
make migrate

# Crear nueva migración
make migrate-create msg="agregar campo email a companies"

# Revertir última migración
make migrate-down
```

### Acceso a Shells

```bash
# Shell del backend (Python)
make shell-backend

# Shell del frontend (Node)
make shell-frontend

# Shell de PostgreSQL
make shell-db

# Shell de Redis
make shell-redis
```

### Testing y Calidad de Código

```bash
# Ejecutar tests
make test

# Tests con coverage
make test-cov

# Linters (ruff + mypy)
make lint

# Formatear código
make format
```

### Backup y Restore

```bash
# Crear backup de la base de datos
make backup-db

# Restaurar desde backup
make restore-db file=backup_20240115_143000.sql
```

### Limpieza

```bash
# Detener servicios y eliminar volúmenes
make clean

# Limpiar recursos no utilizados
make prune

# Ver estadísticas de uso
make stats
```

## 📦 Estructura de Volúmenes

Los volúmenes persistentes mantienen los datos entre reinicios:

```yaml
volumes:
  redis_data          # Datos de Redis
  postgres_data       # Datos de PostgreSQL
  backend_logs        # Logs del backend
  celery_logs         # Logs de Celery
  celery_beat_logs    # Logs de Celery Beat
```

**Volúmenes bind-mount** (desarrollo):
```yaml
- ./backend:/app              # Código backend (hot-reload)
- ./frontend:/app             # Código frontend (hot-reload)
- ./data/uploads:/app/data/uploads  # Archivos subidos
- ./models:/app/models        # Modelos OCR/AI
```

## 🔌 Puertos

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| Frontend | 5173 | http://localhost:5173 | Interfaz de usuario |
| Backend | 8000 | http://localhost:8000 | API REST |
| API Docs | 8000 | http://localhost:8000/docs | Swagger UI |
| Flower | 5555 | http://localhost:5555 | Monitor de Celery |
| Redis | 6379 | localhost:6379 | Cache y message broker |
| PostgreSQL | 5432 | localhost:5432 | Base de datos |
| SQL Server | 1433 | localhost:1433 | Base de datos (opcional) |

## 🔍 Health Checks

Todos los servicios tienen health checks configurados:

```bash
# Ver estado de salud
docker-compose ps

# Verificar health del backend
curl http://localhost:8000/api/v1/health

# Verificar health de Redis
docker-compose exec redis redis-cli ping

# Verificar health de PostgreSQL
docker-compose exec postgres pg_isready -U invokox_user
```

## 🐛 Troubleshooting

### Problema: Servicios no inician

```bash
# Ver logs detallados
docker-compose logs -f [servicio]

# Verificar que los puertos no estén en uso
netstat -tulpn | grep -E '5173|8000|6379|5432'

# Reiniciar servicios
make restart
```

### Problema: Errores de permisos en volúmenes

```bash
# Dar permisos a directorios
chmod -R 777 ./data/uploads ./logs

# Si persiste, verificar usuario en contenedor
docker-compose exec backend whoami
```

### Problema: Base de datos no conecta

```bash
# Verificar que PostgreSQL esté healthy
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Probar conexión manualmente
docker-compose exec backend python -c "from src.infrastructure.database.config import check_db_connection; print(check_db_connection())"
```

### Problema: Migraciones fallan

```bash
# Ver migraciones aplicadas
docker-compose exec backend alembic current

# Ver historial de migraciones
docker-compose exec backend alembic history

# Aplicar manualmente
docker-compose exec backend alembic upgrade head
```

### Problema: Hot-reload no funciona

**Backend:**
```bash
# Verificar que el volumen esté montado correctamente
docker-compose exec backend ls -la /app/src

# Reiniciar servicio
docker-compose restart backend
```

**Frontend:**
```bash
# Verificar montaje de volumen
docker-compose exec frontend ls -la /app/src

# Reinstalar dependencias
docker-compose exec frontend npm install

# Reiniciar servicio
docker-compose restart frontend
```

### Problema: Celery worker no procesa tareas

```bash
# Ver logs de Celery
make logs-celery

# Verificar conexión a Redis
docker-compose exec celery-worker python -c "from celery import Celery; app = Celery(broker='redis://redis:6379/0'); print(app.control.inspect().active())"

# Reiniciar worker
docker-compose restart celery-worker
```

### Problema: Alta utilización de recursos

```bash
# Ver estadísticas de uso
make stats

# Limitar recursos en docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

## 📚 Recursos Adicionales

- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Vite Documentation](https://vitejs.dev/)

## 🔐 Seguridad

### Para Desarrollo

Las configuraciones por defecto son **SOLO PARA DESARROLLO**:
- Contraseñas hardcodeadas
- CORS permisivo
- Debug habilitado
- Secret keys débiles

### Para Producción

**NUNCA usar estas configuraciones en producción**. Cambiar:

1. **Secret Keys**: Generar claves fuertes
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Contraseñas de BD**: Usar contraseñas complejas

3. **CORS**: Permitir solo orígenes específicos

4. **SSL/TLS**: Habilitar certificados

5. **Variables de entorno**: Usar secrets management (Docker Secrets, Vault)

## 📝 Notas Importantes

1. **Primer inicio**: La primera vez tomará más tiempo (descargar imágenes, instalar dependencias)

2. **Migraciones**: Se ejecutan automáticamente al iniciar el backend

3. **Hot-reload**: Cambios en código se reflejan automáticamente

4. **Volúmenes**: Los datos persisten entre reinicios. Usar `make clean` para eliminar

5. **Logs**: Se guardan en volúmenes persistentes

6. **Health checks**: Pueden tardar hasta 40s en estar "healthy"

---

**¿Necesitas ayuda?** Consulta la documentación completa o abre un issue en el repositorio.
