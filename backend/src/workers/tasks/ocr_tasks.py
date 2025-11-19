"""
==============================================================================
OCR CELERY TASKS
==============================================================================
Tareas asíncronas para procesamiento OCR de facturas.

Tasks disponibles:
- process_invoice_ocr: Procesar una factura individualmente
- batch_process_invoices: Procesar múltiples facturas en batch
- reprocess_failed_invoice: Reprocesar factura que falló

Uso:
    from src.workers.tasks.ocr_tasks import process_invoice_ocr

    # Ejecutar asíncronamente
    task = process_invoice_ocr.delay(invoice_id=123, file_path="/path/to/invoice.pdf")

    # Verificar estado
    print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE

    # Obtener resultado (bloqueante)
    result = task.get(timeout=60)
==============================================================================
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from celery import Task, group
from celery.exceptions import Reject, Retry
from sqlalchemy import select
from sqlmodel import Session

from src.infrastructure.database.config import engine
from src.infrastructure.database.models import InvoiceDB
from src.services.ocr_service import OCRService, create_ocr_service
from src.workers.celery_app import app

logger = logging.getLogger(__name__)


# ==============================================================================
# BASE TASK CLASS
# ==============================================================================


class OCRTask(Task):
    """
    Clase base para tasks de OCR con retry logic y logging.

    Características:
    - Auto-retry en caso de error
    - Logging automático
    - Manejo de errores específicos
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 60}  # Retry cada 1 minuto
    retry_backoff = True  # Exponential backoff
    retry_backoff_max = 600  # Max 10 minutos entre retries
    retry_jitter = True  # Agregar jitter aleatorio

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handler para cuando task falla definitivamente."""
        logger.error(
            f"Task {self.name}[{task_id}] failed after all retries",
            exc_info=exc,
            extra={"args": args, "kwargs": kwargs},
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handler para cuando task se reintenta."""
        logger.warning(
            f"Task {self.name}[{task_id}] retrying",
            extra={"exception": str(exc), "args": args, "kwargs": kwargs},
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


# ==============================================================================
# OCR TASKS
# ==============================================================================


@app.task(
    bind=True,
    base=OCRTask,
    name="src.workers.tasks.ocr_tasks.process_invoice_ocr",
    queue="ocr",
)
def process_invoice_ocr(
    self,
    invoice_id: int,
    file_path: str,
    engine: Optional[str] = None,
) -> Dict:
    """
    Procesar factura con OCR y actualizar base de datos.

    Esta task:
    1. Lee el archivo de la factura
    2. Ejecuta OCR para extraer texto y datos estructurados
    3. Actualiza el invoice en la base de datos con los resultados
    4. Cambia el status a COMPLETED o ERROR según resultado

    Args:
        invoice_id: ID de la factura en base de datos
        file_path: Ruta al archivo de factura
        engine: Engine OCR a usar (opcional, usa default si None)

    Returns:
        Dict con resultados del procesamiento:
        {
            "invoice_id": int,
            "status": "success" | "error",
            "confidence": float,
            "processing_time": float,
            "extracted_data": dict,
            "errors": list
        }

    Raises:
        Retry: Si hay error temporal que puede retry
        Reject: Si hay error permanente que no se puede retry

    Example:
        >>> task = process_invoice_ocr.delay(
        ...     invoice_id=123,
        ...     file_path="/uploads/invoice_123.pdf"
        ... )
        >>> result = task.get(timeout=300)
        >>> print(result["confidence"])
        0.95
    """
    logger.info(f"Starting OCR processing for invoice {invoice_id}")

    try:
        # =====================================================================
        # 1. VALIDAR ARCHIVO
        # =====================================================================
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise Reject(error_msg, requeue=False)

        # =====================================================================
        # 2. ACTUALIZAR STATUS A PROCESSING
        # =====================================================================
        with Session(engine) as session:
            invoice = session.get(InvoiceDB, invoice_id)
            if not invoice:
                error_msg = f"Invoice {invoice_id} not found in database"
                logger.error(error_msg)
                raise Reject(error_msg, requeue=False)

            invoice.status = "PROCESSING"
            session.add(invoice)
            session.commit()
            logger.info(f"Invoice {invoice_id} status updated to PROCESSING")

        # =====================================================================
        # 3. EJECUTAR OCR
        # =====================================================================
        ocr_service = create_ocr_service(engine=engine)
        ocr_result = ocr_service.process_invoice(file_path)

        logger.info(
            f"OCR completed for invoice {invoice_id}: "
            f"confidence={ocr_result.confidence:.2f}, "
            f"time={ocr_result.processing_time:.2f}s"
        )

        # =====================================================================
        # 4. ACTUALIZAR BASE DE DATOS CON RESULTADOS
        # =====================================================================
        with Session(engine) as session:
            invoice = session.get(InvoiceDB, invoice_id)

            # Extraer datos estructurados
            structured_data = ocr_result.structured_data

            # Actualizar campos si fueron extraídos
            if structured_data.get("series"):
                invoice.series = structured_data["series"]
            if structured_data.get("folio_number"):
                invoice.folio_number = structured_data["folio_number"]
            if structured_data.get("issue_date"):
                invoice.issue_date = structured_data["issue_date"]
            if structured_data.get("issuer_name"):
                invoice.issuer_name = structured_data["issuer_name"]
            if structured_data.get("issuer_tax_id"):
                invoice.issuer_tax_id = structured_data["issuer_tax_id"]
            if structured_data.get("receiver_name"):
                invoice.receiver_name = structured_data["receiver_name"]
            if structured_data.get("receiver_tax_id"):
                invoice.receiver_tax_id = structured_data["receiver_tax_id"]
            if structured_data.get("subtotal"):
                invoice.subtotal = structured_data["subtotal"]
            if structured_data.get("tax_amount"):
                invoice.tax_amount = structured_data["tax_amount"]
            if structured_data.get("total_amount"):
                invoice.total_amount = structured_data["total_amount"]
            if structured_data.get("currency"):
                invoice.currency = structured_data["currency"]

            # Actualizar metadata de OCR
            invoice.ocr_confidence = ocr_result.confidence
            invoice.processing_time = ocr_result.processing_time

            # Actualizar status basado en confidence
            if ocr_result.confidence >= 0.7:
                invoice.status = "COMPLETED"
            elif ocr_result.confidence >= 0.5:
                invoice.status = "REVIEW_NEEDED"  # Requiere revisión manual
            else:
                invoice.status = "LOW_CONFIDENCE"  # Baja confianza, reprocesar

            session.add(invoice)
            session.commit()

            logger.info(f"Invoice {invoice_id} updated with OCR results")

        # =====================================================================
        # 5. RETORNAR RESULTADOS
        # =====================================================================
        return {
            "invoice_id": invoice_id,
            "status": "success",
            "confidence": ocr_result.confidence,
            "processing_time": ocr_result.processing_time,
            "extracted_data": structured_data,
            "errors": ocr_result.errors,
            "engine": ocr_result.engine,
        }

    except FileNotFoundError as e:
        # Error permanente, no retry
        logger.error(f"File not found for invoice {invoice_id}: {e}")

        with Session(engine) as session:
            invoice = session.get(InvoiceDB, invoice_id)
            if invoice:
                invoice.status = "ERROR"
                invoice.notes = f"File not found: {str(e)}"
                session.add(invoice)
                session.commit()

        raise Reject(str(e), requeue=False)

    except Exception as e:
        # Error temporal, puede retry
        logger.error(f"Error processing invoice {invoice_id}: {e}", exc_info=True)

        # Actualizar status a ERROR si ya agotamos retries
        if self.request.retries >= self.max_retries:
            with Session(engine) as session:
                invoice = session.get(InvoiceDB, invoice_id)
                if invoice:
                    invoice.status = "ERROR"
                    invoice.notes = f"OCR failed after {self.max_retries} retries: {str(e)}"
                    session.add(invoice)
                    session.commit()

        raise


@app.task(
    bind=True,
    name="src.workers.tasks.ocr_tasks.batch_process_invoices",
    queue="ocr",
)
def batch_process_invoices(
    self,
    invoice_ids: List[int],
    engine: Optional[str] = None,
) -> Dict:
    """
    Procesar múltiples facturas en batch.

    Ejecuta process_invoice_ocr para cada factura en paralelo
    usando Celery groups.

    Args:
        invoice_ids: Lista de IDs de facturas a procesar
        engine: Engine OCR a usar (opcional)

    Returns:
        Dict con resumen de resultados:
        {
            "total": int,
            "successful": int,
            "failed": int,
            "task_ids": list,
            "results": list
        }

    Example:
        >>> task = batch_process_invoices.delay([1, 2, 3, 4, 5])
        >>> result = task.get(timeout=600)
        >>> print(f"Processed {result['successful']}/{result['total']}")
    """
    logger.info(f"Starting batch OCR processing for {len(invoice_ids)} invoices")

    try:
        # Obtener file_paths de la base de datos
        with Session(engine) as session:
            statement = select(InvoiceDB).where(InvoiceDB.id.in_(invoice_ids))
            invoices = session.exec(statement).all()

            tasks_data = [
                {"invoice_id": inv.id, "file_path": inv.file_path}
                for inv in invoices
                if inv.file_path
            ]

        if not tasks_data:
            logger.warning("No invoices with file_path found")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "task_ids": [],
                "results": [],
            }

        # Crear group de tasks
        job = group(
            process_invoice_ocr.s(
                invoice_id=data["invoice_id"],
                file_path=data["file_path"],
                engine=engine,
            )
            for data in tasks_data
        )

        # Ejecutar en paralelo
        result_group = job.apply_async()

        # Esperar resultados (con timeout)
        results = result_group.get(timeout=600)  # 10 minutos max

        # Contar exitosos y fallidos
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful

        logger.info(
            f"Batch OCR completed: {successful} successful, {failed} failed out of {len(results)}"
        )

        return {
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "task_ids": [str(r.id) for r in result_group.children],
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error in batch processing: {e}", exc_info=True)
        raise


@app.task(
    bind=True,
    base=OCRTask,
    name="src.workers.tasks.ocr_tasks.reprocess_failed_invoice",
    queue="ocr",
)
def reprocess_failed_invoice(self, invoice_id: int) -> Dict:
    """
    Reprocesar factura que falló en procesamiento anterior.

    Args:
        invoice_id: ID de la factura a reprocesar

    Returns:
        Dict con resultados del reprocesamiento

    Example:
        >>> task = reprocess_failed_invoice.delay(invoice_id=123)
        >>> result = task.get()
    """
    logger.info(f"Reprocessing failed invoice {invoice_id}")

    with Session(engine) as session:
        invoice = session.get(InvoiceDB, invoice_id)

        if not invoice:
            raise Reject(f"Invoice {invoice_id} not found", requeue=False)

        if not invoice.file_path:
            raise Reject(f"Invoice {invoice_id} has no file_path", requeue=False)

        # Resetear status
        invoice.status = "PENDING"
        invoice.notes = "Reprocessing..."
        session.add(invoice)
        session.commit()

    # Llamar a task principal
    return process_invoice_ocr(
        self,
        invoice_id=invoice_id,
        file_path=invoice.file_path,
    )


# ==============================================================================
# HELPER TASKS
# ==============================================================================


@app.task(name="src.workers.tasks.ocr_tasks.check_pending_invoices", queue="ocr")
def check_pending_invoices() -> Dict:
    """
    Verificar facturas pendientes de procesamiento y encolarlas.

    Task periódica que busca facturas en status PENDING con file_path
    y las encola para procesamiento OCR.

    Returns:
        Dict con número de facturas encoladas

    Example:
        Configurado en Celery Beat para ejecutar cada 5 minutos
    """
    logger.info("Checking for pending invoices...")

    with Session(engine) as session:
        # Buscar facturas PENDING con archivo
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.status == "PENDING")
            .where(InvoiceDB.file_path.isnot(None))
        )
        pending_invoices = session.exec(statement).all()

        logger.info(f"Found {len(pending_invoices)} pending invoices")

        # Encolar para procesamiento
        for invoice in pending_invoices:
            process_invoice_ocr.delay(
                invoice_id=invoice.id,
                file_path=invoice.file_path,
            )
            logger.debug(f"Enqueued invoice {invoice.id} for OCR processing")

    return {
        "pending_invoices": len(pending_invoices),
        "enqueued": len(pending_invoices),
    }
