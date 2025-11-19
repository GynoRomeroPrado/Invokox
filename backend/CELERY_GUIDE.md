# 🔄 Celery Guide - Invokox v2.0

Guía completa para trabajar con Celery y tareas asíncronas en Invokox.

## 📋 Tabla de Contenidos

- [Overview](#overview)
- [Arquitectura](#arquitectura)
- [Configuración](#configuración)
- [Tasks Disponibles](#tasks-disponibles)
- [Uso Básico](#uso-básico)
- [Monitoreo](#monitoreo)
- [Desarrollo](#desarrollo)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

### ¿Qué es Celery?

Celery es un sistema de cola de tareas distribuido que permite ejecutar operaciones de forma asíncrona. En Invokox se usa para:

- **Procesamiento OCR**: Extracción de datos de facturas (puede tomar varios segundos/minutos)
- **Envío de emails**: Notificaciones sin bloquear la API
- **Limpieza programada**: Mantenimiento automático del sistema
- **Procesamiento batch**: Múltiples facturas en paralelo

### Ventajas del Procesamiento Asíncrono

✅ **No bloquea la API**: Usuarios obtienen respuesta inmediata
✅ **Escalabilidad**: Procesar múltiples tareas en paralelo
✅ **Retry automático**: Reintentar en caso de fallas temporales
✅ **Programación**: Tasks periódicas con Celery Beat
✅ **Monitoreo**: Flower dashboard para visualizar estado

## 🏗️ Arquitectura

### Componentes

```
┌─────────────────────────────────────────────────────────┐
│                      FastAPI App                        │
│  (Encola tasks con .delay() o .apply_async())          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Redis Broker                         │
│  (Cola de mensajes: almacena tasks pendientes)         │
└────────┬────────────────────────────────┬───────────────┘
         │                                │
         ▼                                ▼
┌────────────────────┐          ┌────────────────────┐
│  Celery Worker 1   │          │  Celery Worker 2   │
│  (Ejecuta tasks)   │          │  (Ejecuta tasks)   │
└────────┬───────────┘          └────────┬───────────┘
         │                                │
         ▼                                ▼
┌─────────────────────────────────────────────────────────┐
│                 Redis Result Backend                    │
│  (Almacena resultados de tasks completadas)            │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   Flower Dashboard                      │
│  (Monitoreo en tiempo real - Puerto 5555)              │
└─────────────────────────────────────────────────────────┘

        Celery Beat (Scheduler)
              │
              ▼
       (Encola tasks periódicas)
```

### Flujo de una Task

1. **API encola task**: `process_invoice_ocr.delay(invoice_id=123)`
2. **Redis almacena task**: Task queda en cola con ID único
3. **Worker toma task**: Primer worker disponible ejecuta
4. **Task se ejecuta**: Procesamiento OCR de la factura
5. **Resultado guardado**: Redis almacena resultado con ID de task
6. **API consulta resultado**: `AsyncResult(task_id).get()`

## ⚙️ Configuración

### Celery App (`src/workers/celery_app.py`)

```python
from celery import Celery
from src.infrastructure.config import get_settings

settings = get_settings()

app = Celery(
    "invokox",
    broker=settings.celery_broker_url,     # Redis URL
    backend=settings.celery_result_backend, # Redis URL
)
```

### Configuración Principal

```python
app.conf.update(
    # Serialización
    task_serializer="json",              # Seguro (no pickle)
    result_serializer="json",

    # Timezone
    timezone="America/Lima",
    enable_utc=True,

    # Timeouts
    task_time_limit=1800,                # 30 min max total
    task_soft_time_limit=1500,           # 25 min soft limit

    # Retries
    task_acks_late=True,                 # ACK después de ejecutar
    task_reject_on_worker_lost=True,     # Rechazar si worker muere

    # Routing
    task_routes={
        "*.ocr_tasks.*": {"queue": "ocr"},
        "*.email_tasks.*": {"queue": "email"},
        "*.cleanup_tasks.*": {"queue": "cleanup"},
    },
)
```

### Variables de Entorno

```bash
# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Opcional: RabbitMQ
# CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
```

## 📝 Tasks Disponibles

### 1. OCR Tasks (`src/workers/tasks/ocr_tasks.py`)

#### `process_invoice_ocr`

Procesa una factura individual con OCR.

```python
from src.workers.tasks.ocr_tasks import process_invoice_ocr

# Ejecutar asíncronamente
task = process_invoice_ocr.delay(
    invoice_id=123,
    file_path="/uploads/invoice_123.pdf",
    engine="paddleocr"  # Opcional
)

# Obtener resultado (bloqueante)
result = task.get(timeout=300)  # Wait max 5 minutos
print(result["confidence"])     # 0.95
print(result["extracted_data"]) # {...}
```

**Características:**
- ✅ Auto-retry: 3 intentos con backoff exponencial
- ✅ Actualiza DB automáticamente
- ✅ Cambia status según confidence
- ✅ Queue: `ocr`

#### `batch_process_invoices`

Procesa múltiples facturas en paralelo.

```python
from src.workers.tasks.ocr_tasks import batch_process_invoices

# Procesar lote
task = batch_process_invoices.delay(
    invoice_ids=[1, 2, 3, 4, 5],
    engine="paddleocr"
)

result = task.get(timeout=600)
print(f"Processed: {result['successful']}/{result['total']}")
```

#### `check_pending_invoices`

Task periódica que busca facturas PENDING y las encola.

```python
# Ejecutada automáticamente por Celery Beat cada 5 minutos
# También se puede ejecutar manualmente:
from src.workers.tasks.ocr_tasks import check_pending_invoices

result = check_pending_invoices.delay()
```

### 2. Email Tasks (`src/workers/tasks/email_tasks.py`)

#### `send_invoice_notification`

Envía notificación de factura procesada.

```python
from src.workers.tasks.email_tasks import send_invoice_notification

task = send_invoice_notification.delay(
    invoice_id=123,
    recipient="user@example.com",
    event_type="processed"  # processed, approved, rejected, error
)
```

**Event Types:**
- `processed`: Factura procesada exitosamente
- `approved`: Factura aprobada
- `rejected`: Factura rechazada
- `error`: Error en procesamiento

#### `send_daily_summary`

Envía resumen diario de facturas.

```python
# Ejecutada automáticamente por Celery Beat a las 8:00 AM
# También manual:
from src.workers.tasks.email_tasks import send_daily_summary

task = send_daily_summary.delay(recipient="admin@invokox.com")
```

#### `send_approval_notification`

Notifica aprobación/rechazo de factura.

```python
from src.workers.tasks.email_tasks import send_approval_notification

task = send_approval_notification.delay(
    invoice_id=123,
    recipient="user@example.com",
    approved=True,
    approved_by="admin@invokox.com",
    comments="Aprobada - todo correcto"
)
```

### 3. Cleanup Tasks (`src/workers/tasks/cleanup_tasks.py`)

#### `cleanup_old_files`

Elimina archivos antiguos de uploads.

```python
from src.workers.tasks.cleanup_tasks import cleanup_old_files

# Ejecutada automáticamente por Celery Beat a las 2:00 AM
# También manual:
task = cleanup_old_files.delay(days_old=90)  # Eliminar > 90 días

result = task.get()
print(f"Deleted {result['deleted_files']} files")
print(f"Freed {result['freed_space_mb']} MB")
```

#### `cleanup_temp_files`

Limpia archivos temporales.

```python
# Ejecutada automáticamente cada hora
from src.workers.tasks.cleanup_tasks import cleanup_temp_files

task = cleanup_temp_files.delay()
```

#### `check_failed_tasks`

Reporta tasks que fallaron.

```python
# Ejecutada automáticamente cada 6 horas
from src.workers.tasks.cleanup_tasks import check_failed_tasks

result = check_failed_tasks.delay().get()
print(f"Failed tasks: {result['failed_count']}")
```

## 🚀 Uso Básico

### Ejecutar Task Asíncrona

```python
from src.workers.tasks.ocr_tasks import process_invoice_ocr

# 1. Encolar task
task = process_invoice_ocr.delay(invoice_id=123, file_path="/path/to/invoice.pdf")

# 2. Obtener task ID
task_id = task.id
print(f"Task ID: {task_id}")

# 3. Verificar estado
print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE

# 4. Esperar resultado (bloqueante)
try:
    result = task.get(timeout=300)  # Wait max 5 min
    print(result)
except TimeoutError:
    print("Task timed out")
```

### Ejecutar con Opciones Avanzadas

```python
# apply_async permite más opciones que .delay()
task = process_invoice_ocr.apply_async(
    args=(123, "/path/to/invoice.pdf"),
    kwargs={"engine": "paddleocr"},
    countdown=10,           # Ejecutar en 10 segundos
    expires=300,            # Expirar en 5 minutos si no ejecuta
    retry=True,
    retry_policy={
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.2,
    },
)
```

### Consultar Resultado de Task

```python
from celery.result import AsyncResult

# Con task ID
task_id = "abc123-def456-ghi789"
result = AsyncResult(task_id, app=app)

# Estado
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE, RETRY

# Si completó exitosamente
if result.successful():
    print(result.result)

# Si falló
if result.failed():
    print(result.traceback)

# Esperar resultado
try:
    result.get(timeout=60, propagate=True)
except Exception as e:
    print(f"Task failed: {e}")
```

### Ejecutar Tasks en Paralelo

```python
from celery import group
from src.workers.tasks.ocr_tasks import process_invoice_ocr

# Crear grupo de tasks
job = group(
    process_invoice_ocr.s(1, "/path/1.pdf"),
    process_invoice_ocr.s(2, "/path/2.pdf"),
    process_invoice_ocr.s(3, "/path/3.pdf"),
)

# Ejecutar todas en paralelo
result_group = job.apply_async()

# Esperar a que todas completen
results = result_group.get(timeout=600)
print(f"Processed {len(results)} invoices")
```

### Ejecutar Tasks en Secuencia (Chain)

```python
from celery import chain
from src.workers.tasks.ocr_tasks import process_invoice_ocr
from src.workers.tasks.email_tasks import send_invoice_notification

# Ejecutar en orden: primero OCR, luego email
workflow = chain(
    process_invoice_ocr.s(123, "/path/invoice.pdf"),
    send_invoice_notification.s(123, "user@example.com", "processed")
)

result = workflow.apply_async()
```

## 📊 Monitoreo

### Flower Dashboard

Flower es una herramienta web de monitoreo para Celery.

**Iniciar Flower:**

```bash
# Con Docker Compose (automático)
docker-compose up flower

# Manual
celery -A src.workers.celery_app flower --port=5555
```

**Acceder:** http://localhost:5555

**Características:**
- ✅ Ver tasks en tiempo real
- ✅ Estadísticas de workers
- ✅ Historial de tasks
- ✅ Gráficos de performance
- ✅ Cancelar tasks
- ✅ Retry tasks fallidas

### Comandos de Inspección

```bash
# Ver workers activos
celery -A src.workers.celery_app inspect active

# Ver tasks programadas
celery -A src.workers.celery_app inspect scheduled

# Ver workers registrados
celery -A src.workers.celery_app inspect registered

# Ver estadísticas
celery -A src.workers.celery_app inspect stats

# Ping workers
celery -A src.workers.celery_app inspect ping
```

### Logs

```bash
# Con Docker Compose
docker-compose logs -f celery-worker

# Ver solo errores
docker-compose logs celery-worker | grep ERROR

# Manual
celery -A src.workers.celery_app worker --loglevel=info
```

## 🛠️ Desarrollo

### Crear Nueva Task

**1. Crear archivo de task:**

```python
# src/workers/tasks/my_tasks.py
import logging
from src.workers.celery_app import app

logger = logging.getLogger(__name__)

@app.task(
    bind=True,
    name="src.workers.tasks.my_tasks.my_custom_task",
    queue="default",
)
def my_custom_task(self, param1: str, param2: int) -> dict:
    """
    Mi task personalizada.

    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2

    Returns:
        Dict con resultado
    """
    logger.info(f"Executing my_custom_task with {param1}, {param2}")

    # Lógica de la task
    result = param1 * param2

    logger.info(f"Task completed: {result}")

    return {
        "status": "success",
        "result": result,
    }
```

**2. Registrar en celery_app.py:**

```python
# src/workers/celery_app.py
app = Celery(
    "invokox",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.workers.tasks.ocr_tasks",
        "src.workers.tasks.email_tasks",
        "src.workers.tasks.cleanup_tasks",
        "src.workers.tasks.my_tasks",  # AGREGAR
    ],
)
```

**3. Usar la task:**

```python
from src.workers.tasks.my_tasks import my_custom_task

task = my_custom_task.delay("hello", 5)
result = task.get()
```

### Agregar Task Periódica (Celery Beat)

```python
# src/workers/celery_app.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    # ... tasks existentes ...

    # Nueva task periódica
    "my-periodic-task": {
        "task": "src.workers.tasks.my_tasks.my_custom_task",
        "schedule": crontab(hour=9, minute=0),  # 9:00 AM diario
        "args": ("hello", 5),
        "options": {"queue": "default"},
    },
}
```

**Crontab Examples:**

```python
# Cada minuto
crontab()

# Cada 15 minutos
crontab(minute="*/15")

# Cada hora
crontab(minute=0)

# Diario a las 8:00 AM
crontab(hour=8, minute=0)

# Cada lunes a las 7:30
crontab(day_of_week=1, hour=7, minute=30)

# Primer día del mes
crontab(day_of_month=1, hour=0, minute=0)
```

### Testing de Tasks

```python
# tests/test_tasks.py
import pytest
from src.workers.tasks.ocr_tasks import process_invoice_ocr

def test_process_invoice_ocr():
    # Ejecutar task síncronamente (para tests)
    result = process_invoice_ocr.apply(
        args=(123, "/path/to/test_invoice.pdf"),
        throw=True  # Lanza excepción si falla
    )

    assert result.get()["status"] == "success"
    assert result.get()["confidence"] > 0.5
```

## 🐛 Troubleshooting

### Worker no Inicia

**Síntoma:** `celery -A src.workers.celery_app worker` no inicia

**Solución:**

```bash
# 1. Verificar que Redis esté corriendo
redis-cli ping  # Debe responder PONG

# 2. Verificar URL de broker
echo $CELERY_BROKER_URL

# 3. Verificar imports
python -c "from src.workers.celery_app import app; print(app)"

# 4. Ver logs detallados
celery -A src.workers.celery_app worker --loglevel=debug
```

### Task Queda en PENDING

**Síntoma:** Task nunca pasa de estado PENDING

**Causas:**
1. Worker no está corriendo
2. Worker no está escuchando la queue correcta
3. Task routing mal configurado

**Solución:**

```bash
# 1. Verificar workers activos
celery -A src.workers.celery_app inspect active

# 2. Verificar que worker escucha la queue
celery -A src.workers.celery_app inspect active_queues

# 3. Iniciar worker con queue específica
celery -A src.workers.celery_app worker -Q ocr,email,cleanup,default
```

### Task Falla con Error

**Síntoma:** Task en estado FAILURE

**Investigar:**

```python
from celery.result import AsyncResult

result = AsyncResult("task-id")
print(result.state)       # FAILURE
print(result.info)        # Información del error
print(result.traceback)   # Stack trace completo
```

**Solución:**
1. Revisar logs del worker
2. Verificar que dependencias estén instaladas
3. Verificar permisos de archivos
4. Aumentar timeout si es necesario

### Tasks se Ejecutan Múltiples Veces

**Causa:** `task_acks_late=True` + worker muere

**Solución:**

```python
# Hacer tasks idempotentes (safe para ejecutar múltiples veces)
@app.task(bind=True)
def idempotent_task(self, invoice_id):
    # Verificar si ya fue procesado
    with Session(engine) as session:
        invoice = session.get(InvoiceDB, invoice_id)
        if invoice.status == "COMPLETED":
            logger.info(f"Invoice {invoice_id} already processed, skipping")
            return {"status": "already_processed"}

    # Procesar...
```

### Resultado de Task no Disponible

**Síntoma:** `result.get()` lanza `TaskRevokedError`

**Causa:** `result_expires` configurado muy corto

**Solución:**

```python
# Aumentar tiempo de expiración de resultados
app.conf.result_expires = 86400  # 24 horas en lugar de default
```

---

**Documentación creada:** 2024-11-19
**Última actualización:** 2024-11-19
**Versión de Celery:** 5.3+
