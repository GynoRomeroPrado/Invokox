# Workers - Celery Async Processing

Procesamiento asíncrono de tareas largas usando Celery + Redis.

## 📂 Estructura

```
workers/
├── tasks/                  # Tareas Celery
│   ├── ocr.py             # Procesamiento OCR (PaddleOCR, Docling)
│   ├── export.py          # Exportación a Excel/PDF
│   ├── sync.py            # Sincronización standalone ↔ server
│   ├── backup.py          # Backup de BD
│   └── cleanup.py         # Limpieza de archivos temporales
├── config/                # Configuración
│   ├── celery_config.py   # Configuración de Celery
│   └── beat_schedule.py   # Tareas programadas (cron)
└── __init__.py
```

## 🏗️ Arquitectura

```
┌────────────────┐
│  FastAPI (API) │
│  POST /process │
└────────┬───────┘
         │ 1. Encola tarea
         ▼
┌────────────────┐
│ Redis (Broker) │
│  Queue: tasks  │
└────────┬───────┘
         │ 2. Dequeue
         ▼
┌────────────────────┐
│ Celery Worker 1    │◄─── GPU habilitado
│ - process_ocr      │     (PaddleOCR acelerado)
└────────────────────┘
┌────────────────────┐
│ Celery Worker 2    │◄─── CPU only
│ - export_to_excel  │
│ - sync_data        │
└────────────────────┘
         │ 3. Resultado
         ▼
┌────────────────┐
│ Redis (Backend)│
│  Result: state │
└────────────────┘
         │ 4. Poll status
         ▼
┌────────────────┐
│  FastAPI (API) │
│  GET /tasks/id │
└────────────────┘
```

## 🚀 Instalación

Las dependencias ya están en `backend/pyproject.toml`:

```toml
[tool.poetry.dependencies]
celery = {extras = ["redis"], version = "^5.3.0"}
redis = "^5.0.0"
```

## 🔧 Configuración

### Celery Config

```python
# workers/config/celery_config.py
from celery import Celery

celery_app = Celery(
    'invokox_workers',
    broker='redis://localhost:6379/0',        # Cola de tareas
    backend='redis://localhost:6379/1',       # Resultados
    include=['workers.tasks']                 # Módulos con tareas
)

# Configuración
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Lima',
    enable_utc=True,

    # Retry settings
    task_acks_late=True,                      # Confirmar solo si termina
    task_reject_on_worker_lost=True,          # Re-encolar si worker muere
    task_track_started=True,                  # Trackear estado STARTED

    # Performance
    worker_prefetch_multiplier=1,             # 1 tarea a la vez (GPU)
    worker_max_tasks_per_child=50,            # Reiniciar worker cada 50 tareas

    # Timeouts
    task_time_limit=600,                      # 10 min máximo
    task_soft_time_limit=540,                 # 9 min soft limit
)
```

### Beat Schedule (Tareas Programadas)

```python
# workers/config/beat_schedule.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # Cleanup diario a las 2 AM
    'cleanup-temp-files': {
        'task': 'workers.tasks.cleanup.cleanup_temp_files',
        'schedule': crontab(hour=2, minute=0),
    },

    # Backup diario a las 3 AM
    'backup-database': {
        'task': 'workers.tasks.backup.backup_database',
        'schedule': crontab(hour=3, minute=0),
    },

    # Sincronización cada 15 minutos (modo server)
    'sync-data': {
        'task': 'workers.tasks.sync.sync_with_server',
        'schedule': crontab(minute='*/15'),
        'kwargs': {'mode': 'incremental'}
    },
}
```

## 📝 Definir Tareas

### Tarea Simple

```python
# workers/tasks/ocr.py
from celery import Task
from workers.config.celery_config import celery_app
from backend.src.infrastructure.services.ocr_service import OCRService

@celery_app.task(bind=True, name='process_invoice_ocr')
def process_invoice_ocr(self: Task, invoice_id: int) -> dict:
    """
    Procesar factura con OCR.

    Args:
        invoice_id: ID de la factura a procesar

    Returns:
        dict con resultado del OCR
    """
    try:
        # 1. Obtener factura de BD
        invoice = get_invoice(invoice_id)

        # 2. Actualizar estado a PROCESSING
        update_invoice_status(invoice_id, 'PROCESSING')
        self.update_state(state='PROCESSING', meta={'progress': 10})

        # 3. Ejecutar OCR
        ocr_service = OCRService()
        result = ocr_service.process(invoice.file_path)
        self.update_state(state='PROCESSING', meta={'progress': 80})

        # 4. Guardar resultado
        update_invoice_data(invoice_id, result)
        self.update_state(state='PROCESSING', meta={'progress': 100})

        return {
            'status': 'success',
            'invoice_id': invoice_id,
            'confidence': result.confidence
        }

    except Exception as exc:
        # Guardar error
        update_invoice_status(invoice_id, 'ERROR', error=str(exc))
        raise
```

### Tarea con Retry

```python
@celery_app.task(
    bind=True,
    name='export_to_excel',
    max_retries=3,
    default_retry_delay=60  # 1 minuto entre retries
)
def export_to_excel(self: Task, invoice_ids: list[int], output_path: str):
    """Exportar facturas a Excel con reintentos."""
    try:
        from backend.src.application.use_cases.export_excel import ExportExcelUseCase

        use_case = ExportExcelUseCase()
        file_path = use_case.execute(invoice_ids, output_path)

        return {'status': 'success', 'file_path': file_path}

    except Exception as exc:
        # Retry con backoff exponencial
        countdown = 60 * (2 ** self.request.retries)  # 1min, 2min, 4min
        raise self.retry(exc=exc, countdown=countdown)
```

### Tarea con Progress Updates

```python
@celery_app.task(bind=True, name='sync_large_dataset')
def sync_large_dataset(self: Task, dataset_size: int):
    """Sincronizar dataset grande con updates de progreso."""
    batch_size = 100
    total_batches = dataset_size // batch_size

    for i in range(total_batches):
        # Procesar batch
        process_batch(i * batch_size, (i + 1) * batch_size)

        # Actualizar progreso
        progress = int((i + 1) / total_batches * 100)
        self.update_state(
            state='PROCESSING',
            meta={
                'current': i + 1,
                'total': total_batches,
                'progress': progress
            }
        )

    return {'status': 'success', 'processed': dataset_size}
```

## 🏃 Ejecución

### Iniciar Worker

```bash
# Worker básico (1 proceso)
celery -A workers.config.celery_config:celery_app worker \
  --loglevel=info \
  --concurrency=2

# Worker con nombre específico
celery -A workers.config.celery_config:celery_app worker \
  --hostname=worker-ocr@%h \
  --queue=ocr \
  --concurrency=1  # 1 porque GPU

# Worker con auto-reload (desarrollo)
watchmedo auto-restart \
  --directory=./workers \
  --pattern='*.py' \
  --recursive \
  -- celery -A workers.config.celery_config:celery_app worker --loglevel=info
```

### Iniciar Beat (Scheduler)

```bash
# Beat para tareas programadas
celery -A workers.config.celery_config:celery_app beat \
  --loglevel=info
```

### Iniciar Flower (Monitoring UI)

```bash
# Flower - UI web para monitorear workers
celery -A workers.config.celery_config:celery_app flower \
  --port=5555

# Acceder a: http://localhost:5555
```

## 📊 Monitoreo

### Ver Estado de Workers

```bash
# Listar workers activos
celery -A workers.config.celery_config:celery_app inspect active

# Ver estadísticas
celery -A workers.config.celery_config:celery_app inspect stats

# Ver tareas registradas
celery -A workers.config.celery_config:celery_app inspect registered
```

### Logs

```bash
# Logs en tiempo real
celery -A workers.config.celery_config:celery_app events

# Guardar logs a archivo
celery -A workers.config.celery_config:celery_app worker \
  --logfile=/var/log/celery/worker.log
```

## 🔌 Integración con FastAPI

### Encolar Tarea

```python
# backend/src/presentation/api/v1/invoices.py
from fastapi import APIRouter
from workers.tasks.ocr import process_invoice_ocr

router = APIRouter()

@router.post("/invoices/{invoice_id}/process")
async def trigger_ocr(invoice_id: int):
    """Iniciar procesamiento OCR asíncrono."""
    task = process_invoice_ocr.delay(invoice_id)

    return {
        'task_id': str(task.id),
        'status': 'queued',
        'invoice_id': invoice_id
    }
```

### Consultar Estado

```python
@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Obtener estado de tarea."""
    from workers.config.celery_config import celery_app

    task = celery_app.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state == 'PROCESSING':
        response = {
            'state': task.state,
            'progress': task.info.get('progress', 0),
            'status': 'Processing...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result,
            'status': 'Completed'
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'error': str(task.info),
            'status': 'Failed'
        }

    return response
```

### Cancelar Tarea

```python
@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancelar tarea en ejecución."""
    from workers.config.celery_config import celery_app

    celery_app.control.revoke(task_id, terminate=True)
    return {'status': 'cancelled', 'task_id': task_id}
```

## 🚀 Producción

### Systemd Service (Linux)

```ini
# /etc/systemd/system/celery-worker.service
[Unit]
Description=Celery Worker for Invokox
After=network.target redis.service

[Service]
Type=forking
User=invokox
Group=invokox
WorkingDirectory=/opt/invokox
ExecStart=/opt/invokox/venv/bin/celery -A workers.config.celery_config:celery_app worker \
  --loglevel=info \
  --pidfile=/var/run/celery/worker.pid \
  --logfile=/var/log/celery/worker.log
ExecStop=/opt/invokox/venv/bin/celery -A workers.config.celery_config:celery_app control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y arrancar
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
sudo systemctl status celery-worker
```

### Docker Compose

```yaml
# docker/docker-compose.prod.yml
services:
  worker-ocr:
    image: invokox-worker:latest
    command: celery -A workers.config.celery_config:celery_app worker --hostname=ocr@%h --queue=ocr --concurrency=1
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: redis://redis:6379
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1  # GPU para OCR
    depends_on:
      - redis

  worker-general:
    image: invokox-worker:latest
    command: celery -A workers.config.celery_config:celery_app worker --hostname=general@%h --concurrency=4
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis

  beat:
    image: invokox-worker:latest
    command: celery -A workers.config.celery_config:celery_app beat --loglevel=info
    environment:
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis

  flower:
    image: invokox-worker:latest
    command: celery -A workers.config.celery_config:celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis
```

## 🧪 Testing

```python
# backend/tests/integration/test_celery_tasks.py
import pytest
from workers.tasks.ocr import process_invoice_ocr

def test_process_ocr_task():
    """Test de tarea OCR."""
    # Modo síncrono para testing
    result = process_invoice_ocr.apply(args=[123])

    assert result.successful()
    assert result.result['status'] == 'success'
    assert 'confidence' in result.result
```
