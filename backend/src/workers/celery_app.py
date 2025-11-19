"""
==============================================================================
CELERY APPLICATION
==============================================================================
Configuración principal de Celery para procesamiento asíncrono.

Características:
- Redis como broker y result backend
- Serialización JSON (segura)
- Task autodiscovery
- Result expiration (24h)
- Max retries y exponential backoff
- Routing de tasks por prioridad
- Monitoring con Flower

Uso:
    from src.workers.celery_app import app

    @app.task(bind=True)
    def my_task(self):
        return "done"
==============================================================================
"""

from celery import Celery
from celery.schedules import crontab

from src.infrastructure.config import get_settings

# Obtener settings
settings = get_settings()

# ==============================================================================
# CELERY APP CONFIGURATION
# ==============================================================================

app = Celery(
    "invokox",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.workers.tasks.ocr_tasks",
        "src.workers.tasks.email_tasks",
        "src.workers.tasks.cleanup_tasks",
    ],
)

# ==============================================================================
# CELERY CONFIGURATION
# ==============================================================================

app.conf.update(
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    # Usar JSON por seguridad (evitar pickle)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # =========================================================================
    # TIMEZONE
    # =========================================================================
    timezone="America/Lima",  # Peru timezone
    enable_utc=True,
    # =========================================================================
    # RESULT BACKEND
    # =========================================================================
    result_expires=86400,  # 24 horas
    result_backend_transport_options={"master_name": "mymaster"},
    # =========================================================================
    # TASK CONFIGURATION
    # =========================================================================
    task_track_started=True,  # Track cuando task inicia
    task_time_limit=1800,  # 30 minutos timeout total
    task_soft_time_limit=1500,  # 25 minutos soft timeout
    task_acks_late=True,  # Acknowledge después de ejecutar
    task_reject_on_worker_lost=True,  # Rechazar si worker muere
    worker_prefetch_multiplier=1,  # Tomar 1 task a la vez (para tasks largas)
    # =========================================================================
    # RETRY CONFIGURATION
    # =========================================================================
    task_default_max_retries=3,
    task_default_retry_delay=60,  # 1 minuto entre retries
    # =========================================================================
    # ROUTING
    # =========================================================================
    task_routes={
        "src.workers.tasks.ocr_tasks.*": {"queue": "ocr"},
        "src.workers.tasks.email_tasks.*": {"queue": "email"},
        "src.workers.tasks.cleanup_tasks.*": {"queue": "cleanup"},
    },
    task_default_queue="default",
    task_default_exchange="tasks",
    task_default_exchange_type="direct",
    task_default_routing_key="task.default",
    # =========================================================================
    # WORKER CONFIGURATION
    # =========================================================================
    worker_max_tasks_per_child=1000,  # Restart worker después de 1000 tasks
    worker_disable_rate_limits=False,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
    # =========================================================================
    # BROKER CONFIGURATION
    # =========================================================================
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_pool_limit=10,
    # =========================================================================
    # MONITORING
    # =========================================================================
    worker_send_task_events=True,  # Para Flower monitoring
    task_send_sent_event=True,
)

# ==============================================================================
# CELERY BEAT SCHEDULE (PERIODIC TASKS)
# ==============================================================================

app.conf.beat_schedule = {
    # =========================================================================
    # CLEANUP TASKS
    # =========================================================================
    "cleanup-old-files-daily": {
        "task": "src.workers.tasks.cleanup_tasks.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),  # 2:00 AM diario
        "options": {"queue": "cleanup"},
    },
    "cleanup-temp-files-hourly": {
        "task": "src.workers.tasks.cleanup_tasks.cleanup_temp_files",
        "schedule": crontab(minute=0),  # Cada hora
        "options": {"queue": "cleanup"},
    },
    # =========================================================================
    # EMAIL TASKS
    # =========================================================================
    "send-daily-summary": {
        "task": "src.workers.tasks.email_tasks.send_daily_summary",
        "schedule": crontab(hour=8, minute=0),  # 8:00 AM diario
        "options": {"queue": "email"},
    },
    # =========================================================================
    # MONITORING TASKS
    # =========================================================================
    "check-failed-tasks": {
        "task": "src.workers.tasks.cleanup_tasks.check_failed_tasks",
        "schedule": crontab(hour="*/6", minute=0),  # Cada 6 horas
        "options": {"queue": "default"},
    },
}


# ==============================================================================
# CELERY SIGNALS
# ==============================================================================


@app.task(bind=True)
def debug_task(self):
    """
    Task de debug para verificar configuración de Celery.

    Returns:
        dict: Información de configuración y request.

    Ejemplo:
        >>> from src.workers.celery_app import debug_task
        >>> result = debug_task.delay()
        >>> result.get()
        {'request': '...', 'broker': 'redis://...'}
    """
    return {
        "request": repr(self.request),
        "broker": settings.celery_broker_url,
        "backend": settings.celery_result_backend,
        "mode": settings.mode,
        "environment": settings.environment,
    }


# ==============================================================================
# SIGNALS PARA LOGGING
# ==============================================================================

from celery.signals import task_failure, task_success, task_retry
import logging

logger = logging.getLogger(__name__)


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, **kw):
    """Handler para tasks que fallan."""
    logger.error(
        f"Task {sender.name}[{task_id}] failed",
        exc_info=exception,
        extra={
            "task_id": task_id,
            "args": args,
            "kwargs": kwargs,
        },
    )


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Handler para tasks exitosas."""
    logger.info(f"Task {sender.name} completed successfully", extra={"result": result})


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, **kwargs):
    """Handler para task retries."""
    logger.warning(f"Task {sender.name}[{task_id}] retry: {reason}")


if __name__ == "__main__":
    app.start()
