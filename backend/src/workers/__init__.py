"""
==============================================================================
WORKERS PACKAGE
==============================================================================
Procesamiento asíncrono con Celery para tareas en background:
- OCR de facturas
- Envío de emails
- Limpieza de archivos temporales
- Generación de reportes
- Sincronización de datos

Uso:
    from src.workers.celery_app import app
    from src.workers.tasks import process_invoice_ocr

    # Ejecutar task asíncrona
    result = process_invoice_ocr.delay(invoice_id=123)

    # Esperar resultado
    result.get(timeout=60)
==============================================================================
"""
