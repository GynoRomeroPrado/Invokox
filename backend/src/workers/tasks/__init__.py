"""
==============================================================================
CELERY TASKS PACKAGE
==============================================================================
Tareas asíncronas organizadas por dominio:

- ocr_tasks: Procesamiento OCR de facturas
- email_tasks: Envío de correos electrónicos
- cleanup_tasks: Limpieza de archivos temporales y mantenimiento

Uso:
    from src.workers.tasks.ocr_tasks import process_invoice_ocr
    from src.workers.tasks.email_tasks import send_invoice_notification
    from src.workers.tasks.cleanup_tasks import cleanup_old_files

    # Ejecutar asíncronamente
    process_invoice_ocr.delay(invoice_id=123)
==============================================================================
"""

from src.workers.tasks.ocr_tasks import process_invoice_ocr, batch_process_invoices
from src.workers.tasks.email_tasks import send_invoice_notification, send_daily_summary
from src.workers.tasks.cleanup_tasks import cleanup_old_files, cleanup_temp_files

__all__ = [
    # OCR Tasks
    "process_invoice_ocr",
    "batch_process_invoices",
    # Email Tasks
    "send_invoice_notification",
    "send_daily_summary",
    # Cleanup Tasks
    "cleanup_old_files",
    "cleanup_temp_files",
]
