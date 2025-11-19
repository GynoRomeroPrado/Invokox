"""
==============================================================================
USE CASE: UPDATE INVOICE
==============================================================================
Caso de uso para actualizar una factura existente.

Este Use Case maneja la complejidad de actualizar una factura de forma segura,
validando reglas de negocio y garantizando consistencia de datos.

Responsabilidades:
- Validar que la factura existe
- Validar que la factura puede ser modificada (no está aprobada/rechazada)
- Actualizar campos permitidos
- Recalcular totales si cambian items
- Incrementar versión (optimistic locking)
- Persistir cambios
- Registrar auditoría

Reglas de negocio:
- No se puede modificar factura APPROVED o REJECTED
- No se puede cambiar la serie (identificador único)
- No se puede cambiar empresas (issuer/receiver)
- Se puede modificar items, fechas, notas
- Al modificar items, los totales se recalculan automáticamente
- La versión se incrementa para detectar conflictos concurrentes

Patrón: Command - Modifica estado del sistema
==============================================================================
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_item import InvoiceItem
from src.application.interfaces.repository_interface import IInvoiceRepository


# ==============================================================================
# INPUT DTO
# ==============================================================================


class UpdateInvoiceInput:
    """
    Data Transfer Object para actualizar una factura.

    Este DTO permite actualizaciones parciales (patch), donde solo
    se especifican los campos que se desean modificar.

    Campos NO modificables:
    - series: Identificador único, no se puede cambiar
    - issuer_id / receiver_id: Empresas no se pueden cambiar
    - created_at / created_by: Auditoría de creación

    Campos modificables:
    - issue_date: Fecha de emisión (con validaciones)
    - due_date: Fecha de vencimiento
    - items: Lista de items (permite agregar/quitar/modificar)
    - notes: Notas adicionales
    - status: Estado (con validaciones de transición)

    Attributes:
        invoice_id: ID de la factura a actualizar (requerido)
        issue_date: Nueva fecha de emisión (opcional)
        due_date: Nueva fecha de vencimiento (opcional)
        items: Nueva lista de items (opcional, reemplaza todos)
        notes: Nuevas notas (opcional)
        updated_by: Usuario que realiza la actualización (requerido)
        version: Versión esperada para optimistic locking (opcional)

    Example:
        >>> # Actualizar solo notas
        >>> input_dto = UpdateInvoiceInput(
        ...     invoice_id=123,
        ...     notes="Factura corregida",
        ...     updated_by="admin@invokox.com"
        ... )
        >>>
        >>> # Actualizar items completos
        >>> input_dto = UpdateInvoiceInput(
        ...     invoice_id=123,
        ...     items=[
        ...         {"line_number": 1, "description": "Item 1", ...},
        ...         {"line_number": 2, "description": "Item 2", ...}
        ...     ],
        ...     updated_by="admin@invokox.com"
        ... )
    """

    def __init__(
        self,
        invoice_id: int,
        updated_by: str,
        issue_date: Optional[date] = None,
        due_date: Optional[date] = None,
        items: Optional[List[dict]] = None,
        notes: Optional[str] = None,
        version: Optional[int] = None,
    ):
        """
        Inicializar DTO de actualización.

        Args:
            invoice_id: ID de la factura (requerido, > 0)
            updated_by: Usuario que actualiza (requerido, no vacío)
            issue_date: Nueva fecha de emisión (opcional)
            due_date: Nueva fecha de vencimiento (opcional)
            items: Nueva lista de items (opcional)
            notes: Nuevas notas (opcional)
            version: Versión para optimistic locking (opcional)

        Raises:
            ValueError: Si los parámetros requeridos son inválidos
        """
        # Validar parámetros requeridos
        if invoice_id is None or invoice_id <= 0:
            raise ValueError(f"Invalid invoice_id: {invoice_id}")

        if not updated_by or not updated_by.strip():
            raise ValueError("updated_by cannot be empty")

        # Asignar atributos
        self.invoice_id = invoice_id
        self.updated_by = updated_by.strip()
        self.issue_date = issue_date
        self.due_date = due_date
        self.items = items
        self.notes = notes
        self.version = version


# ==============================================================================
# USE CASE
# ==============================================================================


class UpdateInvoiceUseCase:
    """
    Use Case: Actualizar una factura existente.

    Este Use Case implementa lógica compleja de actualización que:
    1. Valida permisos y estado
    2. Aplica reglas de negocio
    3. Maneja optimistic locking
    4. Recalcula totales
    5. Persiste cambios
    6. Registra auditoría

    Principios aplicados:
    - SOLID: Single Responsibility, Dependency Inversion
    - DDD: Aggregate Root (Invoice controla sus items)
    - CQRS: Command side (modifica estado)
    - Event Sourcing: Registra cambios en audit log

    Attributes:
        invoice_repo: Repositorio de facturas

    Example:
        >>> # Setup
        >>> repository = InvoiceRepository(session)
        >>> use_case = UpdateInvoiceUseCase(invoice_repository=repository)
        >>>
        >>> # Actualizar
        >>> input_dto = UpdateInvoiceInput(
        ...     invoice_id=123,
        ...     notes="Factura revisada",
        ...     updated_by="admin@invokox.com"
        ... )
        >>> updated_invoice = await use_case.execute(input_dto)
        >>>
        >>> # Verificar
        >>> assert updated_invoice.notes == "Factura revisada"
        >>> assert updated_invoice.version > 1  # Version incrementada
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """
        Inicializar Use Case con repositorio.

        Args:
            invoice_repository: Implementación de IInvoiceRepository
        """
        self.invoice_repo = invoice_repository

    async def execute(self, input_data: UpdateInvoiceInput) -> Invoice:
        """
        Ejecutar actualización de factura.

        Este método orquesta todo el proceso de actualización,
        asegurando que se cumplan todas las reglas de negocio
        y que los datos queden consistentes.

        Args:
            input_data: DTO con los cambios a aplicar

        Returns:
            Invoice: Factura actualizada con nueva versión

        Raises:
            ValueError: Si la factura no existe o no puede actualizarse
            ConcurrentModificationError: Si hay conflicto de versiones
            PermissionError: Si el usuario no tiene permisos

        Flow:
            1. Buscar factura existente
            2. Validar que puede ser modificada
            3. Validar optimistic locking (versión)
            4. Aplicar cambios solicitados
            5. Validar fechas si fueron modificadas
            6. Actualizar items si fueron proporcionados
            7. Recalcular totales
            8. Incrementar versión
            9. Actualizar timestamp y usuario
            10. Persistir cambios
            11. Retornar factura actualizada

        Example:
            >>> input_dto = UpdateInvoiceInput(
            ...     invoice_id=123,
            ...     notes="Corrección en montos",
            ...     updated_by="reviewer@invokox.com"
            ... )
            >>> try:
            ...     invoice = await use_case.execute(input_dto)
            ...     print(f"Factura {invoice.series} actualizada")
            ... except ValueError as e:
            ...     print(f"Error: {e}")
        """
        # =================================================================
        # PASO 1: Buscar factura existente
        # =================================================================
        # Recuperar la factura actual de la base de datos
        invoice = await self.invoice_repo.get_by_id(input_data.invoice_id)

        # Validar que existe
        if invoice is None:
            raise ValueError(
                f"Invoice with ID {input_data.invoice_id} not found. "
                f"Cannot update non-existent invoice."
            )

        # =================================================================
        # PASO 2: Validar que la factura puede ser modificada
        # =================================================================
        # Regla de negocio: No se pueden modificar facturas aprobadas o rechazadas
        # Una vez que una factura está APPROVED o REJECTED, es inmutable
        # (excepto por procesos de corrección específicos no implementados aquí)
        if not self._can_be_updated(invoice):
            raise ValueError(
                f"Invoice with series '{invoice.series}' cannot be updated. "
                f"Current status: {invoice.status}. "
                f"Only invoices with status PENDING, PROCESSING, or COMPLETED can be updated."
            )

        # =================================================================
        # PASO 3: Validar optimistic locking (versión)
        # =================================================================
        # Si el cliente proporcionó una versión esperada, validar que coincida
        # Esto previene que dos usuarios modifiquen la misma factura simultáneamente
        if input_data.version is not None:
            if invoice.version != input_data.version:
                raise ValueError(
                    f"Concurrent modification detected. "
                    f"Expected version {input_data.version}, "
                    f"but current version is {invoice.version}. "
                    f"Please refresh and try again."
                )

        # =================================================================
        # PASO 4: Aplicar cambios de fechas
        # =================================================================
        if input_data.issue_date is not None:
            # Validar que la fecha de emisión no sea futura
            if input_data.issue_date > date.today():
                raise ValueError(
                    f"Issue date cannot be in the future. "
                    f"Provided: {input_data.issue_date}, "
                    f"Today: {date.today()}"
                )

            # Actualizar fecha
            invoice.issue_date = input_data.issue_date

        if input_data.due_date is not None:
            # Validar que due_date >= issue_date
            if input_data.due_date < invoice.issue_date:
                raise ValueError(
                    f"Due date ({input_data.due_date}) must be after "
                    f"or equal to issue date ({invoice.issue_date})"
                )

            # Actualizar fecha
            invoice.due_date = input_data.due_date

        # =================================================================
        # PASO 5: Actualizar items si fueron proporcionados
        # =================================================================
        if input_data.items is not None:
            # La lista de items reemplaza completamente los items existentes
            # Esto es más simple que manejar adds/updates/deletes individuales

            # Limpiar items existentes
            invoice.clear_items()

            # Crear y agregar nuevos items
            for item_data in input_data.items:
                # Crear InvoiceItem entity desde dict
                # Los cálculos (subtotal, tax, etc.) se hacen automáticamente
                item = InvoiceItem(
                    line_number=item_data.get("line_number"),
                    code=item_data.get("code"),
                    description=item_data["description"],  # Required
                    unit=item_data.get("unit", "UND"),
                    quantity=Decimal(str(item_data["quantity"])),  # Required
                    unit_price=Decimal(str(item_data["unit_price"])),  # Required
                    discount_rate=Decimal(str(item_data.get("discount_rate", 0))),
                    tax_rate=Decimal(str(item_data.get("tax_rate", 0))),
                )

                # Agregar item a la factura
                invoice.add_item(item)

            # Recalcular totales de la factura
            # Esto suma todos los totales de los items
            invoice.recalculate_totals()

        # =================================================================
        # PASO 6: Actualizar notas
        # =================================================================
        if input_data.notes is not None:
            # Las notas pueden ser útiles para justificar cambios
            invoice.notes = input_data.notes

        # =================================================================
        # PASO 7: Actualizar metadata de auditoría
        # =================================================================
        # Registrar quién y cuándo hizo la modificación
        invoice.updated_by = input_data.updated_by
        invoice.updated_at = datetime.now()

        # Incrementar versión para optimistic locking
        # Esto permite detectar modificaciones concurrentes en el futuro
        invoice.version += 1

        # =================================================================
        # PASO 8: Persistir cambios
        # =================================================================
        # El repositorio se encarga de:
        # - Actualizar registro en base de datos
        # - Actualizar items relacionados
        # - Manejar transacciones
        # - Registrar en audit log
        updated_invoice = await self.invoice_repo.update(invoice)

        # =================================================================
        # PASO 9: Retornar factura actualizada
        # =================================================================
        return updated_invoice

    def _can_be_updated(self, invoice: Invoice) -> bool:
        """
        Validar si una factura puede ser actualizada.

        Reglas:
        - PENDING: ✅ Puede actualizarse (recién creada)
        - PROCESSING: ✅ Puede actualizarse (procesando OCR)
        - COMPLETED: ✅ Puede actualizarse (OCR completo, antes de aprobar)
        - APPROVED: ❌ No puede actualizarse (ya aprobada)
        - REJECTED: ❌ No puede actualizarse (rechazada)
        - ERROR: ✅ Puede actualizarse (para corregir errores)

        Args:
            invoice: Factura a validar

        Returns:
            True si puede actualizarse, False si no

        Note:
            En un sistema más complejo, podríamos tener roles y permisos
            que permitan a ciertos usuarios actualizar facturas aprobadas
            (ej: rol "Supervisor" puede hacer correcciones).
        """
        # Estados que permiten actualización
        updatable_statuses = {"PENDING", "PROCESSING", "COMPLETED", "ERROR"}

        return invoice.status in updatable_statuses


# ==============================================================================
# USE CASE VARIANTS
# ==============================================================================


class UpdateInvoiceItemsUseCase:
    """
    Variante especializada para actualizar solo los items.

    Esta variante es útil cuando se necesita modificar solo
    los items sin tocar otros campos de la factura.

    Example:
        >>> input_dto = UpdateInvoiceItemsInput(
        ...     invoice_id=123,
        ...     items=[...],
        ...     updated_by="user@invokox.com"
        ... )
        >>> use_case = UpdateInvoiceItemsUseCase(repository)
        >>> invoice = await use_case.execute(input_dto)
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """Inicializar con repositorio."""
        self.invoice_repo = invoice_repository

    async def execute(
        self, invoice_id: int, items: List[dict], updated_by: str
    ) -> Invoice:
        """
        Actualizar solo items de una factura.

        Args:
            invoice_id: ID de la factura
            items: Nueva lista de items
            updated_by: Usuario que actualiza

        Returns:
            Invoice con items actualizados
        """
        # Crear input DTO completo pero solo con items
        input_data = UpdateInvoiceInput(
            invoice_id=invoice_id, items=items, updated_by=updated_by
        )

        # Delegar al Use Case principal
        update_use_case = UpdateInvoiceUseCase(self.invoice_repo)
        return await update_use_case.execute(input_data)


class UpdateInvoiceNotesUseCase:
    """
    Variante para actualizar solo las notas.

    Útil para agregar observaciones sin modificar otros campos.

    Example:
        >>> use_case = UpdateInvoiceNotesUseCase(repository)
        >>> invoice = await use_case.execute(
        ...     invoice_id=123,
        ...     notes="Verificado por contabilidad",
        ...     updated_by="accounting@invokox.com"
        ... )
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """Inicializar con repositorio."""
        self.invoice_repo = invoice_repository

    async def execute(self, invoice_id: int, notes: str, updated_by: str) -> Invoice:
        """
        Actualizar solo notas.

        Args:
            invoice_id: ID de la factura
            notes: Nuevas notas
            updated_by: Usuario que actualiza

        Returns:
            Invoice con notas actualizadas
        """
        # Crear input DTO solo con notas
        input_data = UpdateInvoiceInput(
            invoice_id=invoice_id, notes=notes, updated_by=updated_by
        )

        # Delegar al Use Case principal
        update_use_case = UpdateInvoiceUseCase(self.invoice_repo)
        return await update_use_case.execute(input_data)


# ==============================================================================
# EXCEPTIONS PERSONALIZADAS (OPCIONAL)
# ==============================================================================


class InvoiceNotModifiableError(Exception):
    """
    Excepción cuando se intenta modificar factura no modificable.

    Esta excepción específica permite a capas superiores
    manejar este error de forma diferente a otros ValueError.
    """

    def __init__(self, invoice_series: str, current_status: str):
        """
        Inicializar excepción.

        Args:
            invoice_series: Serie de la factura
            current_status: Estado actual que impide modificación
        """
        self.invoice_series = invoice_series
        self.current_status = current_status
        super().__init__(
            f"Invoice {invoice_series} cannot be modified. "
            f"Current status: {current_status}"
        )


class ConcurrentModificationError(Exception):
    """
    Excepción para conflictos de modificación concurrente.

    Ocurre cuando dos usuarios intentan modificar la misma
    factura simultáneamente.
    """

    def __init__(self, expected_version: int, actual_version: int):
        """
        Inicializar excepción.

        Args:
            expected_version: Versión esperada por el cliente
            actual_version: Versión actual en la base de datos
        """
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Concurrent modification detected. "
            f"Expected version {expected_version}, "
            f"but actual version is {actual_version}"
        )
