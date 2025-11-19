"""
==============================================================================
USE CASE: APPROVE INVOICE
==============================================================================
Caso de uso para aprobar una factura procesada.

Este Use Case implementa el flujo de aprobación de facturas, que es un paso
crítico en el proceso de gestión documental. Una factura aprobada se considera
válida y lista para contabilización.

Responsabilidades:
- Validar que la factura existe y está en estado apropiado
- Validar permisos del usuario aprobador
- Cambiar estado a APPROVED
- Registrar quién y cuándo aprobó
- Actualizar metadata de auditoría
- Notificar a sistemas externos (contabilidad, ERP, etc.)
- Enviar notificaciones por email (opcional)

Reglas de negocio:
- Solo se pueden aprobar facturas en estado COMPLETED o PENDING
- No se pueden aprobar facturas ya aprobadas (idempotencia)
- No se pueden aprobar facturas rechazadas (deben procesarse de nuevo)
- Se requiere usuario con permisos de aprobación
- Una vez aprobada, la factura es inmutable (salvo correcciones especiales)

Flujo típico:
1. OCR procesa factura → COMPLETED
2. Usuario revisa factura
3. Usuario aprueba → APPROVED
4. Sistema contable recibe notificación
5. Factura lista para pago/contabilización

Patrón: Command - Modifica estado del sistema (transición de estado)
==============================================================================
"""

from datetime import datetime
from typing import Optional

from src.domain.entities.invoice import Invoice
from src.application.interfaces.repository_interface import IInvoiceRepository


# ==============================================================================
# INPUT DTO
# ==============================================================================


class ApproveInvoiceInput:
    """
    Data Transfer Object para aprobar una factura.

    Attributes:
        invoice_id: ID de la factura a aprobar (requerido)
        approved_by: Usuario que aprueba (requerido)
        comments: Comentarios de aprobación (opcional)

    Example:
        >>> # Aprobación simple
        >>> input_dto = ApproveInvoiceInput(
        ...     invoice_id=123,
        ...     approved_by="reviewer@invokox.com"
        ... )
        >>>
        >>> # Aprobación con comentarios
        >>> input_dto = ApproveInvoiceInput(
        ...     invoice_id=123,
        ...     approved_by="reviewer@invokox.com",
        ...     comments="Verificado con proveedor, montos correctos"
        ... )
    """

    def __init__(
        self, invoice_id: int, approved_by: str, comments: Optional[str] = None
    ):
        """
        Inicializar DTO de aprobación.

        Args:
            invoice_id: ID de la factura (> 0)
            approved_by: Email/ID del usuario aprobador (no vacío)
            comments: Comentarios adicionales (opcional)

        Raises:
            ValueError: Si parámetros son inválidos
        """
        # Validar invoice_id
        if invoice_id is None or invoice_id <= 0:
            raise ValueError(f"Invalid invoice_id: {invoice_id}")

        # Validar approved_by
        if not approved_by or not approved_by.strip():
            raise ValueError("approved_by cannot be empty")

        self.invoice_id = invoice_id
        self.approved_by = approved_by.strip()
        self.comments = comments.strip() if comments else None


# ==============================================================================
# USE CASE
# ==============================================================================


class ApproveInvoiceUseCase:
    """
    Use Case: Aprobar una factura procesada.

    Este Use Case maneja la lógica compleja de aprobación, incluyendo:
    - Validaciones de negocio
    - Transiciones de estado
    - Auditoría
    - Notificaciones

    Attributes:
        invoice_repo: Repositorio de facturas

    Example:
        >>> # Setup
        >>> repository = InvoiceRepository(session)
        >>> use_case = ApproveInvoiceUseCase(invoice_repository=repository)
        >>>
        >>> # Aprobar factura
        >>> input_dto = ApproveInvoiceInput(
        ...     invoice_id=123,
        ...     approved_by="reviewer@invokox.com"
        ... )
        >>> approved_invoice = await use_case.execute(input_dto)
        >>> assert approved_invoice.status == "APPROVED"
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """
        Inicializar Use Case con repositorio.

        Args:
            invoice_repository: Implementación de IInvoiceRepository
        """
        self.invoice_repo = invoice_repository

    async def execute(self, input_data: ApproveInvoiceInput) -> Invoice:
        """
        Ejecutar aprobación de factura.

        Args:
            input_data: DTO con datos de aprobación

        Returns:
            Invoice: Factura aprobada con estado APPROVED

        Raises:
            ValueError: Si la factura no existe o no puede aprobarse
            PermissionError: Si el usuario no tiene permisos

        Flow:
            1. Buscar factura existente
            2. Validar que puede ser aprobada
            3. Validar permisos del usuario
            4. Cambiar estado a APPROVED
            5. Registrar aprobador y timestamp
            6. Agregar comentarios si existen
            7. Incrementar versión
            8. Persistir cambios
            9. Notificar sistemas externos
            10. Enviar email de notificación
            11. Retornar factura aprobada

        Example:
            >>> input_dto = ApproveInvoiceInput(
            ...     invoice_id=123,
            ...     approved_by="reviewer@invokox.com",
            ...     comments="Todo correcto"
            ... )
            >>> try:
            ...     invoice = await use_case.execute(input_dto)
            ...     print(f"Factura {invoice.series} aprobada")
            ... except ValueError as e:
            ...     print(f"Error: {e}")
        """
        # =================================================================
        # PASO 1: Buscar factura existente
        # =================================================================
        invoice = await self.invoice_repo.get_by_id(input_data.invoice_id)

        if invoice is None:
            raise ValueError(
                f"Invoice with ID {input_data.invoice_id} not found. "
                f"Cannot approve non-existent invoice."
            )

        # =================================================================
        # PASO 2: Validar que la factura puede ser aprobada
        # =================================================================
        if not self._can_be_approved(invoice):
            raise ValueError(
                f"Invoice with series '{invoice.series}' cannot be approved. "
                f"Current status: {invoice.status}. "
                f"Only invoices with status COMPLETED or PENDING can be approved. "
                f"Rejected invoices must be reprocessed first."
            )

        # =================================================================
        # PASO 3: Validar permisos del usuario
        # =================================================================
        # En producción, verificar que el usuario tiene rol de aprobador
        self._validate_approval_permissions(input_data.approved_by)

        # =================================================================
        # PASO 4: Verificar que no esté ya aprobada (idempotencia)
        # =================================================================
        if invoice.status == "APPROVED":
            # Ya está aprobada, esto es idempotente
            # Retornar la factura sin modificar
            # (Alternativamente, se podría lanzar excepción)
            return invoice

        # =================================================================
        # PASO 5: Cambiar estado a APPROVED
        # =================================================================
        # Usar método del dominio que encapsula lógica de negocio
        invoice.approve(approved_by=input_data.approved_by)

        # =================================================================
        # PASO 6: Agregar comentarios si existen
        # =================================================================
        if input_data.comments:
            # Agregar comentarios a las notas
            approval_note = (
                f"\n[APPROVED] {datetime.now().isoformat()}\n"
                f"Approved by: {input_data.approved_by}\n"
                f"Comments: {input_data.comments}"
            )
            invoice.notes = (
                f"{invoice.notes}{approval_note}" if invoice.notes else approval_note
            )

        # =================================================================
        # PASO 7: Actualizar metadata de auditoría
        # =================================================================
        invoice.approved_at = datetime.now()
        invoice.approved_by = input_data.approved_by
        invoice.updated_at = datetime.now()
        invoice.updated_by = input_data.approved_by

        # Incrementar versión (optimistic locking)
        invoice.version += 1

        # =================================================================
        # PASO 8: Persistir cambios
        # =================================================================
        approved_invoice = await self.invoice_repo.update(invoice)

        # =================================================================
        # PASO 9: Notificar a sistemas externos
        # =================================================================
        # Notificar a sistema contable, ERP, etc.
        await self._notify_external_systems(approved_invoice)

        # =================================================================
        # PASO 10: Enviar email de notificación
        # =================================================================
        # Notificar al creador de la factura que fue aprobada
        await self._send_approval_notification(approved_invoice)

        # =================================================================
        # PASO 11: Retornar factura aprobada
        # =================================================================
        return approved_invoice

    def _can_be_approved(self, invoice: Invoice) -> bool:
        """
        Validar si una factura puede ser aprobada.

        Reglas:
        - PENDING: ✅ Puede aprobarse (aprobación sin OCR)
        - PROCESSING: ❌ No puede aprobarse (esperando OCR)
        - COMPLETED: ✅ Puede aprobarse (flujo normal)
        - APPROVED: ✅ Ya aprobada (idempotente)
        - REJECTED: ❌ No puede aprobarse (reprocesar primero)
        - ERROR: ❌ No puede aprobarse (corregir errores primero)

        Args:
            invoice: Factura a validar

        Returns:
            True si puede aprobarse, False si no

        Note:
            APPROVED se considera válido para permitir idempotencia
            (múltiples llamadas al mismo endpoint no fallan).
        """
        approvable_statuses = {"PENDING", "COMPLETED", "APPROVED"}
        return invoice.status in approvable_statuses

    def _validate_approval_permissions(self, user_id: str) -> None:
        """
        Validar que el usuario tiene permisos para aprobar facturas.

        La aprobación es una operación sensible que requiere permisos
        especiales (rol Reviewer, Approver, o Admin).

        Args:
            user_id: ID/email del usuario

        Raises:
            PermissionError: Si el usuario no tiene permisos

        Note:
            En producción, consultar sistema de permisos real.

        Example:
            >>> try:
            ...     self._validate_approval_permissions("reviewer@invokox.com")
            ...     print("Usuario puede aprobar")
            ... except PermissionError:
            ...     print("Usuario NO puede aprobar")
        """
        # TODO: Implementar validación real de permisos
        # Por ahora, permitir todos los usuarios
        # En producción:
        # 1. Consultar tabla de usuarios y roles
        # 2. Verificar rol (Reviewer, Approver, Admin)
        # 3. Lanzar PermissionError si no tiene permisos

        # Temporal: verificar que no sea usuario anónimo
        if not user_id or user_id == "anonymous":
            raise PermissionError(
                "Anonymous users cannot approve invoices. "
                "Please authenticate first."
            )

        # En producción:
        # user = await user_repo.get_by_id(user_id)
        # if not user.has_permission("approve_invoices"):
        #     raise PermissionError(f"User {user_id} does not have approval permissions")

    async def _notify_external_systems(self, invoice: Invoice) -> None:
        """
        Notificar a sistemas externos sobre la aprobación.

        Sistemas a notificar:
        - Sistema contable (crear asiento contable)
        - ERP (actualizar inventario, cuentas por pagar)
        - Sistema de pagos (factura lista para pago)
        - Reporting/BI (actualizar dashboards)

        Args:
            invoice: Factura aprobada

        Note:
            Las notificaciones deben ser asíncronas (message queue)
            para no bloquear la respuesta al usuario.

        Example:
            >>> await self._notify_external_systems(invoice)
            >>> # Sistema contable recibe notificación
            >>> # ERP actualiza registros
        """
        # TODO: Implementar notificaciones reales
        # Opciones de implementación:
        # 1. Message Queue (RabbitMQ, Redis, Kafka)
        # 2. Webhooks HTTP
        # 3. API REST directa
        # 4. Event Bus

        # Ejemplo con Celery task:
        # from src.workers.tasks.integration_tasks import notify_accounting_system
        # notify_accounting_system.delay(invoice_id=invoice.id)

        print(
            f"[NOTIFICATION] Invoice {invoice.series} approved, "
            f"notifying external systems..."
        )

    async def _send_approval_notification(self, invoice: Invoice) -> None:
        """
        Enviar email de notificación de aprobación.

        Destinatarios:
        - Usuario que creó la factura (created_by)
        - Usuarios interesados (watchers)
        - Equipo de contabilidad (opcional)

        Args:
            invoice: Factura aprobada

        Note:
            El envío de email debe ser asíncrono (Celery task)
            para no bloquear la respuesta.

        Example:
            >>> await self._send_approval_notification(invoice)
            >>> # Email enviado a created_by
        """
        # TODO: Implementar envío real de email
        # Usar Celery task para envío asíncrono

        # from src.workers.tasks.email_tasks import send_approval_notification
        # send_approval_notification.delay(
        #     invoice_id=invoice.id,
        #     recipient=invoice.created_by,
        #     approved_by=invoice.approved_by
        # )

        print(
            f"[EMAIL] Sending approval notification for invoice {invoice.series} "
            f"to {invoice.created_by}"
        )


# ==============================================================================
# USE CASE VARIANT: BATCH APPROVAL
# ==============================================================================


class BatchApproveInvoicesUseCase:
    """
    Use Case para aprobar múltiples facturas en batch.

    Útil cuando un revisor necesita aprobar muchas facturas a la vez.

    Example:
        >>> use_case = BatchApproveInvoicesUseCase(invoice_repository)
        >>> result = await use_case.execute(
        ...     invoice_ids=[123, 124, 125],
        ...     approved_by="reviewer@invokox.com",
        ...     comments="Lote revisado y aprobado"
        ... )
        >>> print(f"Aprobadas: {result['approved']}, Fallidas: {result['failed']}")
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """Inicializar con repositorio."""
        self.invoice_repo = invoice_repository
        # Reusar Use Case individual
        self.approve_use_case = ApproveInvoiceUseCase(invoice_repository)

    async def execute(
        self,
        invoice_ids: list[int],
        approved_by: str,
        comments: Optional[str] = None,
    ) -> dict:
        """
        Aprobar múltiples facturas.

        Args:
            invoice_ids: Lista de IDs a aprobar
            approved_by: Usuario aprobador
            comments: Comentarios aplicados a todas

        Returns:
            dict con:
            - approved: Lista de IDs aprobados exitosamente
            - failed: Lista de IDs que fallaron con razón
            - total: Total procesados

        Example:
            >>> result = await use_case.execute(
            ...     invoice_ids=[1, 2, 3, 4, 5],
            ...     approved_by="reviewer@invokox.com"
            ... )
            >>> print(result)
            {
                "approved": [1, 2, 3, 5],
                "failed": [{"id": 4, "reason": "Already approved"}],
                "total": 5
            }
        """
        approved = []
        failed = []

        for invoice_id in invoice_ids:
            try:
                # Crear input DTO para cada factura
                input_dto = ApproveInvoiceInput(
                    invoice_id=invoice_id,
                    approved_by=approved_by,
                    comments=comments,
                )

                # Aprobar usando Use Case individual
                await self.approve_use_case.execute(input_dto)

                # Agregar a lista de exitosos
                approved.append(invoice_id)

            except Exception as e:
                # Agregar a lista de fallidos con razón
                failed.append({"id": invoice_id, "reason": str(e)})

        # Retornar resumen
        return {"approved": approved, "failed": failed, "total": len(invoice_ids)}
