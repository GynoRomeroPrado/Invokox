"""
Use Case: Create Invoice

Caso de uso para crear una nueva factura.
Orquesta lógica de negocio sin depender de detalles de infraestructura.
"""

from datetime import datetime
from typing import Optional

from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_item import InvoiceItem
from src.application.interfaces.repository_interface import (
    IInvoiceRepository,
    ICompanyRepository
)


class CreateInvoiceInput:
    """DTO de entrada para crear factura."""

    def __init__(
        self,
        series: str,
        document_type: str,
        issue_date: str,
        issuer_tax_id: str,
        issuer_name: str,
        receiver_tax_id: str,
        receiver_name: str,
        currency: str,
        file_path: str,
        created_by: str,
        due_date: Optional[str] = None,
        items: Optional[list[dict]] = None,
        notes: Optional[str] = None,
    ):
        self.series = series
        self.document_type = document_type
        self.issue_date = issue_date
        self.due_date = due_date
        self.issuer_tax_id = issuer_tax_id
        self.issuer_name = issuer_name
        self.receiver_tax_id = receiver_tax_id
        self.receiver_name = receiver_name
        self.currency = currency
        self.file_path = file_path
        self.created_by = created_by
        self.items = items or []
        self.notes = notes


class CreateInvoiceUseCase:
    """
    Use Case: Crear una nueva factura.

    Responsabilidades:
    - Validar que el series no exista
    - Obtener o crear empresas (emisor y receptor)
    - Crear la factura con sus items
    - Calcular totales automáticamente
    - Persistir en el repositorio
    """

    def __init__(
        self,
        invoice_repository: IInvoiceRepository,
        company_repository: ICompanyRepository,
    ):
        self.invoice_repo = invoice_repository
        self.company_repo = company_repository

    async def execute(self, input_data: CreateInvoiceInput) -> Invoice:
        """
        Ejecuta el caso de uso.

        Args:
            input_data: Datos de entrada para crear la factura

        Returns:
            Factura creada con ID asignado

        Raises:
            ValueError: Si la factura ya existe o los datos son inválidos
        """
        # 1. Validar que el series no exista
        existing_invoice = await self.invoice_repo.get_by_series(input_data.series)
        if existing_invoice:
            raise ValueError(
                f"Invoice with series '{input_data.series}' already exists"
            )

        # 2. Obtener o crear empresa emisora
        issuer = await self.company_repo.get_or_create_by_tax_id(
            tax_id=input_data.issuer_tax_id,
            name=input_data.issuer_name,
            type="EMISOR"
        )

        # 3. Obtener o crear empresa receptora
        receiver = await self.company_repo.get_or_create_by_tax_id(
            tax_id=input_data.receiver_tax_id,
            name=input_data.receiver_name,
            type="RECEPTOR"
        )

        # 4. Crear items de la factura
        invoice_items = []
        for item_data in input_data.items:
            item = InvoiceItem(**item_data)
            invoice_items.append(item)

        # 5. Crear la factura
        invoice = Invoice(
            series=input_data.series,
            document_type=input_data.document_type,
            issue_date=input_data.issue_date,
            due_date=input_data.due_date,
            issuer_id=issuer.id,  # type: ignore
            issuer_name=issuer.name,
            issuer_tax_id=issuer.tax_id,
            receiver_id=receiver.id,  # type: ignore
            receiver_name=receiver.name,
            receiver_tax_id=receiver.tax_id,
            currency=input_data.currency,
            file_path=input_data.file_path,
            created_by=input_data.created_by,
            notes=input_data.notes,
            items=invoice_items,
        )

        # Los totales se calculan automáticamente en el modelo
        invoice.calculate_totals()

        # 6. Persistir la factura
        created_invoice = await self.invoice_repo.create(invoice)

        # 7. Actualizar contadores de empresas
        await self.company_repo.update_invoice_count(issuer.id)  # type: ignore
        await self.company_repo.update_invoice_count(receiver.id)  # type: ignore

        return created_invoice
