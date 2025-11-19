"""
==============================================================================
EMAIL CELERY TASKS
==============================================================================
Tareas asíncronas para envío de correos electrónicos.

Tasks disponibles:
- send_invoice_notification: Enviar notificación de factura procesada
- send_daily_summary: Enviar resumen diario de facturas
- send_approval_notification: Notificar aprobación/rechazo de factura

Uso:
    from src.workers.tasks.email_tasks import send_invoice_notification

    # Ejecutar asíncronamente
    task = send_invoice_notification.delay(
        invoice_id=123,
        recipient="user@example.com"
    )
==============================================================================
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from celery import Task
from sqlalchemy import func, select
from sqlmodel import Session

from src.infrastructure.database.config import engine
from src.infrastructure.database.models import InvoiceDB
from src.workers.celery_app import app

logger = logging.getLogger(__name__)


# ==============================================================================
# BASE TASK CLASS
# ==============================================================================


class EmailTask(Task):
    """
    Clase base para tasks de email con retry logic.

    Características:
    - Auto-retry en caso de error temporal
    - Logging automático
    - Rate limiting para evitar spam
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 300}  # Retry cada 5 minutos
    rate_limit = "10/m"  # Max 10 emails por minuto

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handler para cuando task falla definitivamente."""
        logger.error(
            f"Email task {self.name}[{task_id}] failed",
            exc_info=exc,
            extra={"args": args, "kwargs": kwargs},
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)


# ==============================================================================
# EMAIL TASKS
# ==============================================================================


@app.task(
    bind=True,
    base=EmailTask,
    name="src.workers.tasks.email_tasks.send_invoice_notification",
    queue="email",
)
def send_invoice_notification(
    self,
    invoice_id: int,
    recipient: str,
    event_type: str = "processed",
) -> Dict:
    """
    Enviar notificación de factura procesada.

    Args:
        invoice_id: ID de la factura
        recipient: Email del destinatario
        event_type: Tipo de evento ('processed', 'approved', 'rejected', 'error')

    Returns:
        Dict con resultado del envío:
        {
            "status": "success" | "error",
            "recipient": str,
            "message_id": str,
            "event_type": str
        }

    Example:
        >>> task = send_invoice_notification.delay(
        ...     invoice_id=123,
        ...     recipient="user@example.com",
        ...     event_type="processed"
        ... )
    """
    logger.info(f"Sending {event_type} notification for invoice {invoice_id} to {recipient}")

    try:
        # Obtener datos de la factura
        with Session(engine) as session:
            invoice = session.get(InvoiceDB, invoice_id)
            if not invoice:
                error_msg = f"Invoice {invoice_id} not found"
                logger.error(error_msg)
                return {"status": "error", "error": error_msg}

        # TODO: Implementar envío real de email con SMTP o servicio de email
        # Por ahora solo logging
        subject = _get_email_subject(event_type, invoice)
        body = _get_email_body(event_type, invoice)

        logger.info(
            f"Email notification prepared:\n"
            f"  To: {recipient}\n"
            f"  Subject: {subject}\n"
            f"  Invoice: {invoice.series}\n"
            f"  Event: {event_type}"
        )

        # Simular envío exitoso
        message_id = f"msg_{invoice_id}_{datetime.now().timestamp()}"

        return {
            "status": "success",
            "recipient": recipient,
            "message_id": message_id,
            "event_type": event_type,
            "invoice_id": invoice_id,
        }

    except Exception as e:
        logger.error(f"Error sending email notification: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


@app.task(
    bind=True,
    base=EmailTask,
    name="src.workers.tasks.email_tasks.send_daily_summary",
    queue="email",
)
def send_daily_summary(self, recipient: Optional[str] = None) -> Dict:
    """
    Enviar resumen diario de facturas procesadas.

    Task periódica configurada en Celery Beat para ejecutar diariamente.

    Args:
        recipient: Email del destinatario (opcional, usa default de config)

    Returns:
        Dict con resultado del envío y estadísticas

    Example:
        Configurado en Celery Beat para ejecutar a las 8:00 AM diario
    """
    logger.info("Generating daily summary...")

    try:
        # Calcular rango de fechas (ayer)
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Obtener estadísticas del día
        with Session(engine) as session:
            # Total de facturas procesadas
            total_statement = (
                select(func.count(InvoiceDB.id))
                .where(InvoiceDB.created_at >= yesterday)
                .where(InvoiceDB.created_at < today)
            )
            total_count = session.exec(total_statement).first()

            # Facturas por status
            status_statement = (
                select(
                    InvoiceDB.status,
                    func.count(InvoiceDB.id),
                )
                .where(InvoiceDB.created_at >= yesterday)
                .where(InvoiceDB.created_at < today)
                .group_by(InvoiceDB.status)
            )
            status_counts = session.exec(status_statement).all()

            # Total en montos
            amount_statement = (
                select(
                    InvoiceDB.currency,
                    func.sum(InvoiceDB.total_amount),
                )
                .where(InvoiceDB.created_at >= yesterday)
                .where(InvoiceDB.created_at < today)
                .group_by(InvoiceDB.currency)
            )
            amount_totals = session.exec(amount_statement).all()

        # Formatear estadísticas
        stats = {
            "date": str(yesterday),
            "total_invoices": total_count or 0,
            "by_status": dict(status_counts) if status_counts else {},
            "by_currency": dict(amount_totals) if amount_totals else {},
        }

        logger.info(f"Daily summary stats: {stats}")

        # TODO: Enviar email real
        # Por ahora solo logging
        logger.info(
            f"Daily summary email:\n"
            f"  Date: {yesterday}\n"
            f"  Total: {stats['total_invoices']} invoices\n"
            f"  Status: {stats['by_status']}\n"
            f"  Amounts: {stats['by_currency']}"
        )

        return {
            "status": "success",
            "recipient": recipient or "admin@invokox.com",
            "stats": stats,
        }

    except Exception as e:
        logger.error(f"Error generating daily summary: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


@app.task(
    bind=True,
    base=EmailTask,
    name="src.workers.tasks.email_tasks.send_approval_notification",
    queue="email",
)
def send_approval_notification(
    self,
    invoice_id: int,
    recipient: str,
    approved: bool,
    approved_by: str,
    comments: Optional[str] = None,
) -> Dict:
    """
    Enviar notificación de aprobación/rechazo de factura.

    Args:
        invoice_id: ID de la factura
        recipient: Email del destinatario
        approved: True si fue aprobada, False si rechazada
        approved_by: Usuario que aprobó/rechazó
        comments: Comentarios opcionales

    Returns:
        Dict con resultado del envío

    Example:
        >>> task = send_approval_notification.delay(
        ...     invoice_id=123,
        ...     recipient="user@example.com",
        ...     approved=True,
        ...     approved_by="admin@invokox.com"
        ... )
    """
    event_type = "approved" if approved else "rejected"
    logger.info(f"Sending approval notification for invoice {invoice_id}: {event_type}")

    try:
        with Session(engine) as session:
            invoice = session.get(InvoiceDB, invoice_id)
            if not invoice:
                error_msg = f"Invoice {invoice_id} not found"
                logger.error(error_msg)
                return {"status": "error", "error": error_msg}

        # TODO: Implementar envío real
        logger.info(
            f"Approval notification:\n"
            f"  Invoice: {invoice.series}\n"
            f"  Status: {event_type}\n"
            f"  By: {approved_by}\n"
            f"  Comments: {comments or 'None'}\n"
            f"  To: {recipient}"
        )

        return {
            "status": "success",
            "recipient": recipient,
            "event_type": event_type,
            "invoice_id": invoice_id,
            "approved_by": approved_by,
        }

    except Exception as e:
        logger.error(f"Error sending approval notification: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def _get_email_subject(event_type: str, invoice: InvoiceDB) -> str:
    """Generar subject del email según tipo de evento."""
    subjects = {
        "processed": f"Factura {invoice.series} procesada exitosamente",
        "approved": f"Factura {invoice.series} aprobada",
        "rejected": f"Factura {invoice.series} rechazada",
        "error": f"Error al procesar factura {invoice.series}",
    }
    return subjects.get(event_type, f"Notificación de factura {invoice.series}")


def _get_email_body(event_type: str, invoice: InvoiceDB) -> str:
    """Generar cuerpo del email según tipo de evento."""
    # Template básico (TODO: usar HTML templates)
    body = f"""
    Estimado usuario,

    La factura {invoice.series} ha sido {event_type}.

    Detalles:
    - Emisor: {invoice.issuer_name} ({invoice.issuer_tax_id})
    - Receptor: {invoice.receiver_name} ({invoice.receiver_tax_id})
    - Fecha: {invoice.issue_date}
    - Monto: {invoice.currency} {invoice.total_amount}
    - Status: {invoice.status}

    Puede revisar los detalles completos en el sistema Invokox.

    Saludos,
    Sistema Invokox
    """
    return body.strip()
