"""
==============================================================================
USE CASE: DELETE INVOICE
==============================================================================
Caso de uso para eliminar (soft delete) una factura.

Este Use Case implementa eliminación lógica (soft delete) en lugar de
eliminación física (hard delete) para mantener trazabilidad y permitir
auditoría completa del sistema.

Responsabilidades:
- Validar que la factura existe
- Validar que puede ser eliminada (reglas de negocio)
- Marcar como eliminada (soft delete) o eliminar físicamente según configuración
- Actualizar contadores de empresas
- Registrar auditoría de la eliminación
- Notificar a sistemas externos si es necesario

Reglas de negocio:
- No se pueden eliminar facturas APPROVED (ya aprobadas y contabilizadas)
- Facturas PENDING o ERROR pueden eliminarse libremente
- Facturas PROCESSING deben cancelar primero el procesamiento
- Facturas REJECTED pueden eliminarse
- Se requiere justificación (razón) para eliminar

Tipos de eliminación:
1. Soft Delete (recomendado):
   - Marca is_deleted=True, deleted_at=now(), deleted_by=user
   - Los datos permanecen en la base de datos
   - No aparece en consultas normales
   - Puede revertirse

2. Hard Delete (no recomendado):
   - Elimina físicamente el registro
   - No se puede recuperar
   - Rompe trazabilidad
   - Solo para casos especiales (GDPR, etc.)

Patrón: Command - Modifica estado del sistema
==============================================================================
"""

from datetime import datetime
from typing import Optional

from src.domain.entities.invoice import Invoice
from src.application.interfaces.repository_interface import (
    IInvoiceRepository,
    ICompanyRepository,
)


# ==============================================================================
# INPUT DTO
# ==============================================================================


class DeleteInvoiceInput:
    """
    Data Transfer Object para eliminar una factura.

    Attributes:
        invoice_id: ID de la factura a eliminar (requerido)
        deleted_by: Usuario que realiza la eliminación (requerido)
        reason: Razón de la eliminación (requerido para auditoría)
        force: Si True, permite eliminar facturas en estados normalmente protegidos (opcional)
        hard_delete: Si True, elimina físicamente (usar con precaución) (opcional)

    Example:
        >>> # Eliminación normal
        >>> input_dto = DeleteInvoiceInput(
        ...     invoice_id=123,
        ...     deleted_by="admin@invokox.com",
        ...     reason="Factura duplicada"
        ... )
        >>>
        >>> # Eliminación forzada (casos especiales)
        >>> input_dto = DeleteInvoiceInput(
        ...     invoice_id=123,
        ...     deleted_by="supervisor@invokox.com",
        ...     reason="Corrección contable autorizada por gerencia",
        ...     force=True  # Permite eliminar facturas aprobadas
        ... )
    """

    def __init__(
        self,
        invoice_id: int,
        deleted_by: str,
        reason: str,
        force: bool = False,
        hard_delete: bool = False,
    ):
        """
        Inicializar DTO de eliminación.

        Args:
            invoice_id: ID de la factura (> 0)
            deleted_by: Email/ID del usuario que elimina (no vacío)
            reason: Justificación de la eliminación (no vacío)
            force: Permitir eliminar facturas protegidas (default: False)
            hard_delete: Eliminación física vs lógica (default: False)

        Raises:
            ValueError: Si parámetros son inválidos
        """
        # Validar invoice_id
        if invoice_id is None or invoice_id <= 0:
            raise ValueError(f"Invalid invoice_id: {invoice_id}")

        # Validar deleted_by
        if not deleted_by or not deleted_by.strip():
            raise ValueError("deleted_by cannot be empty")

        # Validar reason (requerido para auditoría)
        if not reason or not reason.strip():
            raise ValueError(
                "Reason is required for deleting an invoice. "
                "Please provide a justification for auditing purposes."
            )

        # Validar combinación force + hard_delete
        if hard_delete and not force:
            raise ValueError(
                "hard_delete requires force=True. "
                "Physical deletion is a dangerous operation."
            )

        self.invoice_id = invoice_id
        self.deleted_by = deleted_by.strip()
        self.reason = reason.strip()
        self.force = force
        self.hard_delete = hard_delete


# ==============================================================================
# USE CASE
# ==============================================================================


class DeleteInvoiceUseCase:
    """
    Use Case: Eliminar (soft delete) una factura.

    Este Use Case implementa eliminación segura con validaciones
    estrictas y auditoría completa.

    Por defecto, realiza soft delete para mantener trazabilidad.
    La eliminación física (hard delete) requiere flag explícito.

    Attributes:
        invoice_repo: Repositorio de facturas
        company_repo: Repositorio de empresas (para actualizar contadores)

    Example:
        >>> # Setup
        >>> invoice_repo = InvoiceRepository(session)
        >>> company_repo = CompanyRepository(session)
        >>> use_case = DeleteInvoiceUseCase(
        ...     invoice_repository=invoice_repo,
        ...     company_repository=company_repo
        ... )
        >>>
        >>> # Eliminar factura duplicada
        >>> input_dto = DeleteInvoiceInput(
        ...     invoice_id=123,
        ...     deleted_by="admin@invokox.com",
        ...     reason="Factura duplicada, usar F001-00000124 en su lugar"
        ... )
        >>> result = await use_case.execute(input_dto)
        >>> print(f"Factura eliminada: {result}")
    """

    def __init__(
        self,
        invoice_repository: IInvoiceRepository,
        company_repository: ICompanyRepository,
    ):
        """
        Inicializar Use Case con dependencias.

        Args:
            invoice_repository: Repositorio de facturas
            company_repository: Repositorio de empresas
        """
        self.invoice_repo = invoice_repository
        self.company_repo = company_repository

    async def execute(self, input_data: DeleteInvoiceInput) -> bool:
        """
        Ejecutar eliminación de factura.

        Args:
            input_data: DTO con datos de eliminación

        Returns:
            bool: True si se eliminó exitosamente

        Raises:
            ValueError: Si la factura no existe o no puede eliminarse
            PermissionError: Si el usuario no tiene permisos suficientes

        Flow:
            1. Buscar factura existente
            2. Validar que puede ser eliminada
            3. Validar permisos del usuario (si force=True)
            4. Decrementar contadores de empresas
            5. Marcar como eliminada (soft) o eliminar (hard)
            6. Registrar en audit log
            7. Notificar a sistemas externos (opcional)
            8. Retornar True

        Example:
            >>> input_dto = DeleteInvoiceInput(
            ...     invoice_id=123,
            ...     deleted_by="admin@invokox.com",
            ...     reason="Error en datos fiscales"
            ... )
            >>> try:
            ...     success = await use_case.execute(input_dto)
            ...     if success:
            ...         print("Factura eliminada correctamente")
            ... except ValueError as e:
            ...     print(f"No se puede eliminar: {e}")
        """
        # =================================================================
        # PASO 1: Buscar factura existente
        # =================================================================
        invoice = await self.invoice_repo.get_by_id(input_data.invoice_id)

        if invoice is None:
            raise ValueError(
                f"Invoice with ID {input_data.invoice_id} not found. "
                f"Cannot delete non-existent invoice."
            )

        # =================================================================
        # PASO 2: Validar que la factura puede ser eliminada
        # =================================================================
        if not input_data.force:
            # Validación estricta: solo se pueden eliminar ciertos estados
            if not self._can_be_deleted(invoice):
                raise ValueError(
                    f"Invoice with series '{invoice.series}' cannot be deleted. "
                    f"Current status: {invoice.status}. "
                    f"Only invoices with status PENDING, ERROR, or REJECTED can be deleted. "
                    f"Use force=True to override (requires special permissions)."
                )
        else:
            # Modo force: validar permisos especiales
            # En un sistema real, aquí verificaríamos roles/permisos
            # Por ejemplo: solo usuarios con rol "Supervisor" pueden usar force
            self._validate_force_permissions(input_data.deleted_by)

        # =================================================================
        # PASO 3: Validar que no tenga dependencias críticas
        # =================================================================
        # Verificar si la factura tiene relaciones que impidan eliminación
        # Ejemplos:
        # - Pagos aplicados
        # - Referencias en notas de crédito
        # - Exportada a sistema contable
        if await self._has_critical_dependencies(invoice):
            raise ValueError(
                f"Invoice {invoice.series} has critical dependencies "
                f"and cannot be deleted. Please contact system administrator."
            )

        # =================================================================
        # PASO 4: Actualizar contadores de empresas
        # =================================================================
        # Decrementar contador de facturas de las empresas involucradas
        # Esto mantiene las estadísticas consistentes
        try:
            await self.company_repo.decrement_invoice_count(invoice.issuer_id)
            await self.company_repo.decrement_invoice_count(invoice.receiver_id)
        except Exception as e:
            # Si falla actualizar contadores, loggear pero continuar
            # Los contadores se pueden recalcular después
            print(f"Warning: Failed to update company counters: {e}")

        # =================================================================
        # PASO 5: Eliminar factura (soft o hard según configuración)
        # =================================================================
        if input_data.hard_delete:
            # ELIMINACIÓN FÍSICA (HARD DELETE)
            # Elimina permanentemente el registro de la base de datos
            # ⚠️  PRECAUCIÓN: No se puede recuperar después

            # Loggear operación crítica
            print(
                f"[CRITICAL] Hard deleting invoice {invoice.series} "
                f"by {input_data.deleted_by}. Reason: {input_data.reason}"
            )

            # Eliminar físicamente
            success = await self.invoice_repo.hard_delete(input_data.invoice_id)

            if not success:
                raise RuntimeError(
                    f"Failed to hard delete invoice {input_data.invoice_id}"
                )

        else:
            # ELIMINACIÓN LÓGICA (SOFT DELETE) - RECOMENDADO
            # Marca el registro como eliminado pero lo mantiene en la base de datos
            # ✅ Se puede recuperar si es necesario
            # ✅ Mantiene trazabilidad completa
            # ✅ No rompe relaciones de auditoría

            # Actualizar campos de eliminación
            invoice.is_deleted = True
            invoice.deleted_at = datetime.now()
            invoice.deleted_by = input_data.deleted_by
            invoice.deletion_reason = input_data.reason

            # Agregar nota de eliminación
            deletion_note = (
                f"[DELETED] {datetime.now().isoformat()} by {input_data.deleted_by}: "
                f"{input_data.reason}"
            )
            invoice.notes = (
                f"{invoice.notes}\n\n{deletion_note}"
                if invoice.notes
                else deletion_note
            )

            # Persistir cambios
            await self.invoice_repo.update(invoice)

        # =================================================================
        # PASO 6: Registrar en audit log
        # =================================================================
        # Crear entrada de auditoría para rastrear la eliminación
        await self._log_deletion(
            invoice=invoice,
            deleted_by=input_data.deleted_by,
            reason=input_data.reason,
            hard_delete=input_data.hard_delete,
        )

        # =================================================================
        # PASO 7: Notificar a sistemas externos (opcional)
        # =================================================================
        # Si hay integraciones con sistemas externos (contabilidad, ERP, etc.),
        # notificar que la factura fue eliminada
        # await self._notify_external_systems(invoice)

        # =================================================================
        # PASO 8: Retornar resultado exitoso
        # =================================================================
        return True

    def _can_be_deleted(self, invoice: Invoice) -> bool:
        """
        Validar si una factura puede ser eliminada (sin forzar).

        Reglas:
        - PENDING: ✅ Puede eliminarse (aún no procesada)
        - PROCESSING: ❌ No puede eliminarse (procesando OCR)
        - COMPLETED: ❌ No puede eliminarse (ya procesada)
        - APPROVED: ❌ No puede eliminarse (ya aprobada)
        - REJECTED: ✅ Puede eliminarse (rechazada)
        - ERROR: ✅ Puede eliminarse (con errores)

        Args:
            invoice: Factura a validar

        Returns:
            True si puede eliminarse, False si no

        Note:
            Esta validación se aplica solo cuando force=False.
            Con force=True, se puede eliminar en cualquier estado
            (requiere permisos especiales).
        """
        deletable_statuses = {"PENDING", "REJECTED", "ERROR"}
        return invoice.status in deletable_statuses

    def _validate_force_permissions(self, user_id: str) -> None:
        """
        Validar que el usuario tiene permisos para eliminación forzada.

        La eliminación forzada permite eliminar facturas en estados protegidos
        y requiere permisos especiales (rol Supervisor o Admin).

        Args:
            user_id: ID/email del usuario

        Raises:
            PermissionError: Si el usuario no tiene permisos suficientes

        Note:
            En producción, esta función debería consultar el sistema de
            permisos real para validar roles del usuario.

        Example:
            >>> # Verificar permisos
            >>> try:
            ...     self._validate_force_permissions("admin@invokox.com")
            ...     print("Usuario tiene permisos")
            ... except PermissionError:
            ...     print("Usuario NO tiene permisos")
        """
        # TODO: Implementar validación real de permisos
        # Por ahora, solo verificar que el usuario está especificado
        # En producción:
        # 1. Consultar base de datos de usuarios
        # 2. Verificar rol (Supervisor, Admin, etc.)
        # 3. Lanzar PermissionError si no tiene permisos

        # Temporal: permitir solo ciertos usuarios
        authorized_users = [
            "admin@invokox.com",
            "supervisor@invokox.com",
        ]

        if user_id not in authorized_users:
            raise PermissionError(
                f"User {user_id} does not have permissions for forced deletion. "
                f"This operation requires Supervisor or Admin role."
            )

    async def _has_critical_dependencies(self, invoice: Invoice) -> bool:
        """
        Verificar si la factura tiene dependencias críticas.

        Dependencias críticas son relaciones que impiden la eliminación:
        - Pagos aplicados a la factura
        - Notas de crédito referenciando esta factura
        - Exportada a sistema contable externo
        - Incluida en declaraciones fiscales

        Args:
            invoice: Factura a verificar

        Returns:
            True si tiene dependencias críticas, False si no

        Note:
            Por ahora retorna False (sin dependencias).
            En producción, implementar verificaciones reales.

        Example:
            >>> # Verificar dependencias
            >>> has_deps = await self._has_critical_dependencies(invoice)
            >>> if has_deps:
            ...     print("No se puede eliminar, tiene dependencias")
        """
        # TODO: Implementar verificaciones reales
        # 1. Verificar pagos: SELECT COUNT(*) FROM payments WHERE invoice_id = ?
        # 2. Verificar notas de crédito: SELECT COUNT(*) FROM credit_notes WHERE original_invoice_id = ?
        # 3. Verificar exportaciones: SELECT COUNT(*) FROM exports WHERE invoice_id = ?

        # Por ahora, retornar False (sin dependencias)
        return False

    async def _log_deletion(
        self,
        invoice: Invoice,
        deleted_by: str,
        reason: str,
        hard_delete: bool,
    ) -> None:
        """
        Registrar eliminación en audit log.

        Crea entrada en la tabla de auditoría para rastrear quién,
        cuándo y por qué eliminó una factura.

        Args:
            invoice: Factura eliminada
            deleted_by: Usuario que eliminó
            reason: Razón de eliminación
            hard_delete: Si fue eliminación física

        Note:
            Esta función es crítica para cumplir con requisitos
            de auditoría y trazabilidad del sistema.

        Example:
            >>> await self._log_deletion(
            ...     invoice=invoice,
            ...     deleted_by="admin@invokox.com",
            ...     reason="Factura duplicada",
            ...     hard_delete=False
            ... )
        """
        # TODO: Implementar registro en audit_logs table
        # Campos a registrar:
        # - entity_type: "invoice"
        # - entity_id: invoice.id
        # - action: "DELETE" o "HARD_DELETE"
        # - user_id: deleted_by
        # - timestamp: datetime.now()
        # - old_values: JSON con datos de la factura
        # - description: reason

        deletion_type = "HARD_DELETE" if hard_delete else "SOFT_DELETE"
        print(
            f"[AUDIT] {deletion_type} invoice {invoice.series} "
            f"by {deleted_by}: {reason}"
        )

        # En producción, insertar en tabla audit_logs:
        # await audit_log_repo.create(
        #     entity_type="invoice",
        #     entity_id=invoice.id,
        #     action=deletion_type,
        #     user_id=deleted_by,
        #     description=reason,
        #     old_values=invoice.to_dict(),
        # )


# ==============================================================================
# USE CASE VARIANTS
# ==============================================================================


class RestoreInvoiceUseCase:
    """
    Use Case para restaurar una factura eliminada (soft delete).

    Solo funciona con facturas que fueron eliminadas lógicamente
    (soft delete). Las facturas eliminadas físicamente (hard delete)
    no se pueden recuperar.

    Example:
        >>> # Restaurar factura eliminada por error
        >>> use_case = RestoreInvoiceUseCase(invoice_repository)
        >>> invoice = await use_case.execute(
        ...     invoice_id=123,
        ...     restored_by="admin@invokox.com",
        ...     reason="Eliminada por error, restaurando"
        ... )
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """Inicializar con repositorio."""
        self.invoice_repo = invoice_repository

    async def execute(
        self, invoice_id: int, restored_by: str, reason: str
    ) -> Invoice:
        """
        Restaurar factura eliminada.

        Args:
            invoice_id: ID de la factura a restaurar
            restored_by: Usuario que restaura
            reason: Razón de la restauración

        Returns:
            Invoice restaurada

        Raises:
            ValueError: Si la factura no existe o no fue soft deleted
        """
        # Buscar factura (incluyendo eliminadas)
        invoice = await self.invoice_repo.get_by_id_including_deleted(invoice_id)

        if invoice is None:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        if not invoice.is_deleted:
            raise ValueError(
                f"Invoice {invoice.series} is not deleted, cannot restore"
            )

        # Restaurar
        invoice.is_deleted = False
        invoice.deleted_at = None
        invoice.deleted_by = None
        invoice.deletion_reason = None

        # Agregar nota de restauración
        restore_note = (
            f"[RESTORED] {datetime.now().isoformat()} by {restored_by}: {reason}"
        )
        invoice.notes = f"{invoice.notes}\n\n{restore_note}" if invoice.notes else restore_note

        # Persistir
        return await self.invoice_repo.update(invoice)
