"""
Task Endpoints

API REST para consultar estado de tareas asíncronas (Celery).
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ==============================================================================
# TASK STATUS ENDPOINT
# ==============================================================================

@router.get("/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado de una tarea asíncrona (Celery).

    **Parámetros:**
    - `task_id`: ID de la tarea Celery

    **Returns:**
    ```json
    {
      "task_id": "abc123-def456",
      "status": "PENDING|PROCESSING|COMPLETED|FAILED",
      "progress": 75,
      "result": {...},
      "error": "...",
      "created_at": "2025-01-15T10:30:00",
      "updated_at": "2025-01-15T10:35:00"
    }
    ```

    **Estados posibles:**
    - `PENDING`: Tarea en cola, esperando ejecución
    - `PROCESSING`: Tarea en ejecución
    - `COMPLETED`: Tarea completada exitosamente
    - `FAILED`: Tarea falló con error

    **Ejemplo:**
    ```
    GET /api/v1/tasks/task_123_20250115103000
    ```

    **Raises:**
    - 404: Si la tarea no existe
    """
    # TODO: Integrar con Celery real
    # Por ahora, simulamos respuestas basadas en el task_id

    # Simulación: Si el task_id contiene "invoice", retornar estado simulado
    if "invoice" in task_id.lower() or "task_" in task_id:
        # Parsear invoice_id del task_id si es posible
        invoice_id = None
        if "_" in task_id:
            parts = task_id.split("_")
            if len(parts) >= 2:
                try:
                    invoice_id = int(parts[1])
                except (ValueError, IndexError):
                    pass

        return {
            "task_id": task_id,
            "status": "COMPLETED",  # Simulado: siempre completado por ahora
            "progress": 100,
            "result": {
                "invoice_id": invoice_id,
                "status": "COMPLETED",
                "confidence": 0.92,
                "extracted_data": {
                    "series": "F001-00000123",
                    "issuer_name": "EMPRESA EJEMPLO S.A.C.",
                    "issuer_tax_id": "20123456789",
                    "receiver_name": "CLIENTE EJEMPLO S.R.L.",
                    "receiver_tax_id": "20987654321",
                    "total_amount": 1180.00,
                    "currency": "PEN",
                    "issue_date": "2025-01-15"
                },
                "processing_time": 2.5,
                "engine": "donut"
            },
            "error": None,
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-15T10:32:30"
        }
    else:
        # Tarea no encontrada
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found"
        )


# ==============================================================================
# TASK OPERATIONS
# ==============================================================================

@router.delete("/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, str]:
    """
    Cancela una tarea en ejecución.

    **Parámetros:**
    - `task_id`: ID de la tarea a cancelar

    **Returns:**
    ```json
    {
      "task_id": "abc123",
      "status": "CANCELLED",
      "message": "Task cancelled successfully"
    }
    ```

    **Raises:**
    - 404: Si la tarea no existe
    - 400: Si la tarea ya está completada o no puede cancelarse
    """
    # TODO: Implementar cancelación con Celery
    # celery_app.control.revoke(task_id, terminate=True)

    return {
        "task_id": task_id,
        "status": "CANCELLED",
        "message": "Task cancellation requested. Note: Task may complete before cancellation takes effect."
    }


@router.get("")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Lista todas las tareas recientes.

    **Parámetros:**
    - `status`: Filtrar por estado (PENDING, PROCESSING, COMPLETED, FAILED)
    - `limit`: Máximo de tareas a retornar (default: 100)

    **Returns:**
    ```json
    {
      "tasks": [
        {"task_id": "...", "status": "...", ...},
        ...
      ],
      "total": 42
    }
    ```

    **Ejemplo:**
    ```
    GET /api/v1/tasks?status=PROCESSING&limit=50
    ```
    """
    # TODO: Implementar con Celery Inspect
    # from celery import current_app
    # inspect = current_app.control.inspect()
    # active_tasks = inspect.active()

    return {
        "tasks": [],
        "total": 0,
        "message": "Task listing will be implemented with Celery integration"
    }


# ==============================================================================
# NOTAS DE IMPLEMENTACIÓN
# ==============================================================================
"""
Para integrar completamente con Celery, necesitas:

1. **Configurar Celery App** (backend/src/workers/celery_app.py):
   ```python
   from celery import Celery

   celery_app = Celery(
       'invokox',
       broker='redis://localhost:6379/0',
       backend='redis://localhost:6379/1'
   )
   ```

2. **Crear tarea OCR** (backend/src/workers/tasks/ocr_tasks.py):
   ```python
   from celery import shared_task
   from src.application.use_cases.process_ocr_use_case import ProcessOCRUseCase

   @shared_task(bind=True)
   def process_invoice_ocr_task(self, invoice_id: int):
       # Ejecutar ProcessOCRUseCase
       # Actualizar progreso con self.update_state()
       return result
   ```

3. **Lanzar tarea desde endpoint**:
   ```python
   from src.workers.tasks.ocr_tasks import process_invoice_ocr_task

   task = process_invoice_ocr_task.delay(invoice_id)
   return {"task_id": task.id}
   ```

4. **Consultar estado**:
   ```python
   from celery.result import AsyncResult

   result = AsyncResult(task_id)
   return {
       "status": result.status,
       "result": result.result if result.ready() else None
   }
   ```

5. **Iniciar Celery worker**:
   ```bash
   celery -A src.workers.celery_app worker --loglevel=info
   ```
"""
