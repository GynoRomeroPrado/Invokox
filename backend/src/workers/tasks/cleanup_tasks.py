"""
==============================================================================
CLEANUP CELERY TASKS
==============================================================================
Tareas asíncronas para limpieza y mantenimiento del sistema.

Tasks disponibles:
- cleanup_old_files: Limpiar archivos antiguos
- cleanup_temp_files: Limpiar archivos temporales
- check_failed_tasks: Verificar y reportar tasks fallidas
- cleanup_processed_invoices: Archivar facturas procesadas antiguas

Uso:
    from src.workers.tasks.cleanup_tasks import cleanup_old_files

    # Ejecutar asíncronamente
    task = cleanup_old_files.delay(days_old=30)

Estas tasks están configuradas en Celery Beat para ejecutar periódicamente.
==============================================================================
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from celery import Task
from sqlalchemy import select
from sqlmodel import Session

from src.infrastructure.config import get_settings
from src.infrastructure.database.config import engine
from src.infrastructure.database.models import InvoiceDB
from src.workers.celery_app import app

logger = logging.getLogger(__name__)
settings = get_settings()


# ==============================================================================
# BASE TASK CLASS
# ==============================================================================


class CleanupTask(Task):
    """
    Clase base para tasks de limpieza.

    Características:
    - Auto-retry en caso de error
    - Logging detallado
    - Rate limiting para evitar sobrecarga
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 2, "countdown": 600}  # Retry cada 10 minutos
    rate_limit = "1/m"  # Max 1 cleanup por minuto

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handler para cuando task falla."""
        logger.error(
            f"Cleanup task {self.name}[{task_id}] failed",
            exc_info=exc,
            extra={"args": args, "kwargs": kwargs},
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)


# ==============================================================================
# CLEANUP TASKS
# ==============================================================================


@app.task(
    bind=True,
    base=CleanupTask,
    name="src.workers.tasks.cleanup_tasks.cleanup_old_files",
    queue="cleanup",
)
def cleanup_old_files(self, days_old: int = 90) -> Dict:
    """
    Limpiar archivos de facturas más antiguos que X días.

    Esta task:
    1. Busca archivos en el directorio de uploads
    2. Elimina los que tienen más de X días
    3. Actualiza referencias en base de datos si es necesario

    Args:
        days_old: Número de días de antigüedad para eliminar (default: 90)

    Returns:
        Dict con estadísticas de limpieza:
        {
            "deleted_files": int,
            "freed_space_mb": float,
            "errors": list
        }

    Example:
        Configurado en Celery Beat para ejecutar diariamente a las 2:00 AM
    """
    logger.info(f"Starting cleanup of files older than {days_old} days")

    uploads_dir = Path(settings.upload_directory)
    if not uploads_dir.exists():
        logger.warning(f"Upload directory does not exist: {uploads_dir}")
        return {"deleted_files": 0, "freed_space_mb": 0.0, "errors": []}

    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted_files = 0
    freed_space = 0
    errors = []

    try:
        # Iterar sobre archivos en directorio
        for file_path in uploads_dir.rglob("*"):
            if not file_path.is_file():
                continue

            # Verificar antigüedad
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff_date:
                try:
                    # Obtener tamaño antes de eliminar
                    file_size = file_path.stat().st_size
                    freed_space += file_size

                    # Eliminar archivo
                    file_path.unlink()
                    deleted_files += 1

                    logger.debug(f"Deleted old file: {file_path}")

                except Exception as e:
                    error_msg = f"Error deleting {file_path}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        freed_space_mb = freed_space / (1024 * 1024)  # Convertir a MB

        logger.info(
            f"Cleanup completed: deleted {deleted_files} files, "
            f"freed {freed_space_mb:.2f} MB"
        )

        return {
            "deleted_files": deleted_files,
            "freed_space_mb": round(freed_space_mb, 2),
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Error in cleanup_old_files: {e}", exc_info=True)
        raise


@app.task(
    bind=True,
    base=CleanupTask,
    name="src.workers.tasks.cleanup_tasks.cleanup_temp_files",
    queue="cleanup",
)
def cleanup_temp_files(self) -> Dict:
    """
    Limpiar archivos temporales del sistema.

    Elimina:
    - Archivos en /tmp con prefijo 'invokox_'
    - Archivos temporales de OCR
    - Archivos de conversión PDF antiguos

    Returns:
        Dict con estadísticas de limpieza

    Example:
        Configurado en Celery Beat para ejecutar cada hora
    """
    logger.info("Starting cleanup of temporary files")

    temp_dir = Path("/tmp")
    deleted_files = 0
    freed_space = 0
    errors = []

    try:
        # Buscar archivos temporales de Invokox
        temp_patterns = [
            "invokox_*",
            "invoice_temp_*",
            "ocr_temp_*",
            "pdf_page_*",
        ]

        for pattern in temp_patterns:
            for file_path in temp_dir.glob(pattern):
                if not file_path.is_file():
                    continue

                try:
                    # Verificar que tenga al menos 1 hora de antigüedad
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if datetime.now() - file_mtime > timedelta(hours=1):
                        file_size = file_path.stat().st_size
                        freed_space += file_size

                        file_path.unlink()
                        deleted_files += 1

                        logger.debug(f"Deleted temp file: {file_path}")

                except Exception as e:
                    error_msg = f"Error deleting {file_path}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        freed_space_mb = freed_space / (1024 * 1024)

        logger.info(
            f"Temp cleanup completed: deleted {deleted_files} files, "
            f"freed {freed_space_mb:.2f} MB"
        )

        return {
            "deleted_files": deleted_files,
            "freed_space_mb": round(freed_space_mb, 2),
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Error in cleanup_temp_files: {e}", exc_info=True)
        raise


@app.task(
    bind=True,
    base=CleanupTask,
    name="src.workers.tasks.cleanup_tasks.check_failed_tasks",
    queue="cleanup",
)
def check_failed_tasks(self) -> Dict:
    """
    Verificar tasks fallidas en Celery y reportar.

    Revisa el backend de resultados de Celery para encontrar
    tasks que fallaron y genera un reporte.

    Returns:
        Dict con estadísticas de tasks fallidas:
        {
            "failed_count": int,
            "failed_tasks": list,
            "oldest_failure": str,
            "most_common_error": str
        }

    Example:
        Configurado en Celery Beat para ejecutar cada 6 horas
    """
    logger.info("Checking for failed tasks")

    try:
        # TODO: Implementar consulta a Celery result backend
        # Por ahora solo logging

        # Obtener tasks fallidas de Redis
        failed_tasks = []
        failed_count = len(failed_tasks)

        logger.info(f"Found {failed_count} failed tasks")

        # Analizar errores comunes
        error_counts = {}
        oldest_failure = None

        for task in failed_tasks:
            # Contar tipos de error
            error_type = task.get("error_type", "Unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

            # Encontrar falla más antigua
            if oldest_failure is None or task["failed_at"] < oldest_failure:
                oldest_failure = task["failed_at"]

        most_common_error = max(error_counts.items(), key=lambda x: x[1])[0] if error_counts else None

        result = {
            "failed_count": failed_count,
            "failed_tasks": failed_tasks[:10],  # Solo primeros 10
            "oldest_failure": str(oldest_failure) if oldest_failure else None,
            "most_common_error": most_common_error,
            "error_counts": error_counts,
        }

        if failed_count > 0:
            logger.warning(
                f"Found {failed_count} failed tasks. "
                f"Most common error: {most_common_error}"
            )

        return result

    except Exception as e:
        logger.error(f"Error checking failed tasks: {e}", exc_info=True)
        raise


@app.task(
    bind=True,
    base=CleanupTask,
    name="src.workers.tasks.cleanup_tasks.cleanup_processed_invoices",
    queue="cleanup",
)
def cleanup_processed_invoices(self, days_old: int = 365) -> Dict:
    """
    Archivar facturas procesadas antiguas.

    Facturas más antiguas que X días en status APPROVED o COMPLETED
    se mueven a una tabla de archivo o se exportan a almacenamiento frío.

    Args:
        days_old: Días de antigüedad para archivar (default: 365)

    Returns:
        Dict con estadísticas de archivado

    Example:
        >>> cleanup_processed_invoices.delay(days_old=730)  # 2 años
    """
    logger.info(f"Starting archiving of invoices older than {days_old} days")

    cutoff_date = datetime.now() - timedelta(days=days_old)
    archived_count = 0

    try:
        with Session(engine) as session:
            # Buscar facturas para archivar
            statement = (
                select(InvoiceDB)
                .where(InvoiceDB.status.in_(["APPROVED", "COMPLETED"]))
                .where(InvoiceDB.created_at < cutoff_date)
            )
            old_invoices = session.exec(statement).all()

            logger.info(f"Found {len(old_invoices)} invoices to archive")

            for invoice in old_invoices:
                # TODO: Implementar lógica de archivado
                # Opciones:
                # 1. Mover a tabla archive_invoices
                # 2. Exportar a S3/almacenamiento frío
                # 3. Comprimir y guardar en archivo

                # Por ahora solo logging
                logger.debug(f"Would archive invoice {invoice.id}: {invoice.series}")
                archived_count += 1

            # TODO: Commit cuando se implemente archivado real
            # session.commit()

        logger.info(f"Archived {archived_count} invoices")

        return {
            "archived_count": archived_count,
            "cutoff_date": str(cutoff_date),
        }

    except Exception as e:
        logger.error(f"Error archiving invoices: {e}", exc_info=True)
        raise


@app.task(
    bind=True,
    name="src.workers.tasks.cleanup_tasks.cleanup_orphaned_files",
    queue="cleanup",
)
def cleanup_orphaned_files(self) -> Dict:
    """
    Limpiar archivos huérfanos (sin referencia en base de datos).

    Busca archivos en uploads que no tienen invoice asociado
    en la base de datos y los elimina.

    Returns:
        Dict con estadísticas de limpieza

    Example:
        >>> cleanup_orphaned_files.delay()
    """
    logger.info("Starting cleanup of orphaned files")

    uploads_dir = Path(settings.upload_directory)
    if not uploads_dir.exists():
        logger.warning(f"Upload directory does not exist: {uploads_dir}")
        return {"deleted_files": 0, "freed_space_mb": 0.0}

    deleted_files = 0
    freed_space = 0

    try:
        # Obtener todos los file_paths de la base de datos
        with Session(engine) as session:
            statement = select(InvoiceDB.file_path).where(InvoiceDB.file_path.isnot(None))
            db_file_paths = set(session.exec(statement).all())

        logger.info(f"Found {len(db_file_paths)} files referenced in database")

        # Verificar archivos en disco
        for file_path in uploads_dir.rglob("*"):
            if not file_path.is_file():
                continue

            # Convertir a ruta relativa o absoluta según DB
            file_path_str = str(file_path)

            # Si el archivo no está en DB, es huérfano
            if file_path_str not in db_file_paths:
                try:
                    file_size = file_path.stat().st_size
                    freed_space += file_size

                    file_path.unlink()
                    deleted_files += 1

                    logger.debug(f"Deleted orphaned file: {file_path}")

                except Exception as e:
                    logger.error(f"Error deleting orphaned file {file_path}: {e}")

        freed_space_mb = freed_space / (1024 * 1024)

        logger.info(
            f"Orphan cleanup completed: deleted {deleted_files} files, "
            f"freed {freed_space_mb:.2f} MB"
        )

        return {
            "deleted_files": deleted_files,
            "freed_space_mb": round(freed_space_mb, 2),
        }

    except Exception as e:
        logger.error(f"Error cleaning up orphaned files: {e}", exc_info=True)
        raise
