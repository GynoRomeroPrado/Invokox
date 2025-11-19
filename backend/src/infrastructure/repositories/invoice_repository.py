"""
Invoice Repository Implementation

Implementación concreta del repositorio de facturas usando SQLModel.
Funciona tanto con SQLite como con SQL Server.
"""

from typing import Optional
from datetime import date
from sqlmodel import Session, select, func, or_

from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_item import InvoiceItem
from src.application.interfaces.repository_interface import IInvoiceRepository
from src.infrastructure.database.models import InvoiceDB, InvoiceItemDB


class InvoiceRepository(IInvoiceRepository):
    """
    Implementación del repositorio de facturas.

    Traduce entre entidades de dominio (Invoice) y modelos de BD (InvoiceDB).
    """

    def __init__(self, session: Session):
        self.session = session

    # ==========================================================================
    # MÉTODOS BÁSICOS (CRUD)
    # ==========================================================================

    async def get_by_id(self, id: int) -> Optional[Invoice]:
        """Obtiene una factura por ID con sus items."""
        invoice_db = self.session.get(InvoiceDB, id)
        if not invoice_db:
            return None

        return self._to_domain(invoice_db)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: any
    ) -> list[Invoice]:
        """Obtiene lista de facturas con paginación."""
        statement = select(InvoiceDB).offset(skip).limit(limit)

        # Aplicar filtros si existen
        if "status" in filters:
            statement = statement.where(InvoiceDB.status == filters["status"])
        if "currency" in filters:
            statement = statement.where(InvoiceDB.currency == filters["currency"])

        # Ordenar por fecha de creación descendente
        statement = statement.order_by(InvoiceDB.created_at.desc())

        results = self.session.exec(statement).all()
        return [self._to_domain(inv) for inv in results]

    async def count(self, **filters: any) -> int:
        """Cuenta el total de facturas."""
        statement = select(func.count(InvoiceDB.id))

        if "status" in filters:
            statement = statement.where(InvoiceDB.status == filters["status"])
        if "currency" in filters:
            statement = statement.where(InvoiceDB.currency == filters["currency"])

        return self.session.exec(statement).one()

    async def create(self, entity: Invoice) -> Invoice:
        """Crea una nueva factura con sus items."""
        # Convertir entidad de dominio a modelo de BD
        invoice_db = self._to_db_model(entity)

        # Guardar en BD
        self.session.add(invoice_db)
        self.session.commit()
        self.session.refresh(invoice_db)

        # Retornar entidad de dominio actualizada con ID
        return self._to_domain(invoice_db)

    async def update(self, entity: Invoice) -> Invoice:
        """Actualiza una factura existente."""
        if not entity.id:
            raise ValueError("Invoice must have an ID to be updated")

        # Obtener factura existente
        invoice_db = self.session.get(InvoiceDB, entity.id)
        if not invoice_db:
            raise ValueError(f"Invoice with ID {entity.id} not found")

        # Actualizar campos
        invoice_db.series = entity.series
        invoice_db.document_type = entity.document_type
        invoice_db.issue_date = entity.issue_date
        invoice_db.due_date = entity.due_date
        invoice_db.status = entity.status
        invoice_db.currency = entity.currency
        invoice_db.subtotal = entity.subtotal
        invoice_db.tax_total = entity.tax_total
        invoice_db.discount_total = entity.discount_total
        invoice_db.withholding_total = entity.withholding_total
        invoice_db.total = entity.total
        invoice_db.ocr_engine = entity.ocr_engine
        invoice_db.ocr_confidence = entity.ocr_confidence
        invoice_db.processing_time = entity.processing_time
        invoice_db.notes = entity.notes
        invoice_db.updated_at = entity.updated_at
        invoice_db.updated_by = entity.updated_by
        invoice_db.sync_status = entity.sync_status
        invoice_db.version = entity.version

        # Actualizar items (eliminar viejos y crear nuevos)
        # NOTA: En producción, usar actualización más inteligente
        for item in invoice_db.items:
            self.session.delete(item)

        for item_entity in entity.items:
            item_db = InvoiceItemDB(
                invoice_id=invoice_db.id,
                code=item_entity.code,
                description=item_entity.description,
                unit=item_entity.unit,
                quantity=item_entity.quantity,
                unit_price=item_entity.unit_price,
                discount_percent=item_entity.discount_percent,
                tax_percent=item_entity.tax_percent,
                subtotal=item_entity.subtotal,
                discount_amount=item_entity.discount_amount,
                tax_amount=item_entity.tax_amount,
                total=item_entity.total,
            )
            self.session.add(item_db)

        self.session.commit()
        self.session.refresh(invoice_db)

        return self._to_domain(invoice_db)

    async def delete(self, id: int) -> bool:
        """Elimina una factura por ID."""
        invoice_db = self.session.get(InvoiceDB, id)
        if not invoice_db:
            return False

        self.session.delete(invoice_db)
        self.session.commit()
        return True

    # ==========================================================================
    # MÉTODOS ESPECÍFICOS DE INVOICE
    # ==========================================================================

    async def get_by_series(self, series: str) -> Optional[Invoice]:
        """Obtiene una factura por su número de serie."""
        statement = select(InvoiceDB).where(InvoiceDB.series == series)
        invoice_db = self.session.exec(statement).first()

        if not invoice_db:
            return None

        return self._to_domain(invoice_db)

    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """Obtiene facturas por estado."""
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.status == status)
            .order_by(InvoiceDB.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        results = self.session.exec(statement).all()
        return [self._to_domain(inv) for inv in results]

    async def get_by_company(
        self,
        company_id: int,
        is_issuer: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """Obtiene facturas de una empresa."""
        if is_issuer:
            statement = select(InvoiceDB).where(InvoiceDB.issuer_id == company_id)
        else:
            statement = select(InvoiceDB).where(InvoiceDB.receiver_id == company_id)

        statement = statement.order_by(InvoiceDB.created_at.desc()).offset(skip).limit(limit)

        results = self.session.exec(statement).all()
        return [self._to_domain(inv) for inv in results]

    async def get_by_date_range(
        self,
        start_date: str,
        end_date: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """Obtiene facturas en un rango de fechas."""
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.issue_date >= start_date)
            .where(InvoiceDB.issue_date <= end_date)
            .order_by(InvoiceDB.issue_date.desc())
            .offset(skip)
            .limit(limit)
        )

        results = self.session.exec(statement).all()
        return [self._to_domain(inv) for inv in results]

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """Búsqueda de texto completo en facturas."""
        search_term = f"%{query}%"

        statement = (
            select(InvoiceDB)
            .where(
                or_(
                    InvoiceDB.series.like(search_term),
                    InvoiceDB.issuer_name.like(search_term),
                    InvoiceDB.issuer_tax_id.like(search_term),
                    InvoiceDB.receiver_name.like(search_term),
                    InvoiceDB.receiver_tax_id.like(search_term),
                    InvoiceDB.notes.like(search_term),
                )
            )
            .order_by(InvoiceDB.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        results = self.session.exec(statement).all()
        return [self._to_domain(inv) for inv in results]

    async def get_pending_sync(self, limit: int = 100) -> list[Invoice]:
        """Obtiene facturas pendientes de sincronización."""
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.sync_status == "pending")
            .order_by(InvoiceDB.updated_at.desc())
            .limit(limit)
        )

        results = self.session.exec(statement).all()
        return [self._to_domain(inv) for inv in results]

    async def bulk_update_status(
        self,
        invoice_ids: list[int],
        status: str
    ) -> int:
        """Actualiza el estado de múltiples facturas."""
        statement = (
            select(InvoiceDB)
            .where(InvoiceDB.id.in_(invoice_ids))
        )

        invoices = self.session.exec(statement).all()

        for invoice in invoices:
            invoice.status = status

        self.session.commit()
        return len(invoices)

    # ==========================================================================
    # MÉTODOS DE CONVERSIÓN (MAPPERS)
    # ==========================================================================

    def _to_domain(self, invoice_db: InvoiceDB) -> Invoice:
        """Convierte modelo de BD a entidad de dominio."""
        # Convertir items
        items = [
            InvoiceItem(
                id=item.id,
                invoice_id=item.invoice_id,
                code=item.code,
                description=item.description,
                unit=item.unit,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_percent=item.tax_percent,
                subtotal=item.subtotal,
                discount_amount=item.discount_amount,
                tax_amount=item.tax_amount,
                total=item.total,
            )
            for item in invoice_db.items
        ]

        return Invoice(
            id=invoice_db.id,
            series=invoice_db.series,
            document_type=invoice_db.document_type,
            issue_date=invoice_db.issue_date,
            due_date=invoice_db.due_date,
            issuer_id=invoice_db.issuer_id,
            issuer_name=invoice_db.issuer_name,
            issuer_tax_id=invoice_db.issuer_tax_id,
            receiver_id=invoice_db.receiver_id,
            receiver_name=invoice_db.receiver_name,
            receiver_tax_id=invoice_db.receiver_tax_id,
            currency=invoice_db.currency,
            subtotal=invoice_db.subtotal,
            tax_total=invoice_db.tax_total,
            discount_total=invoice_db.discount_total,
            withholding_total=invoice_db.withholding_total,
            total=invoice_db.total,
            items=items,
            status=invoice_db.status,
            ocr_engine=invoice_db.ocr_engine,
            ocr_confidence=invoice_db.ocr_confidence,
            processing_time=invoice_db.processing_time,
            file_path=invoice_db.file_path,
            notes=invoice_db.notes,
            created_at=invoice_db.created_at,
            updated_at=invoice_db.updated_at,
            created_by=invoice_db.created_by,
            updated_by=invoice_db.updated_by,
            sync_status=invoice_db.sync_status,
            last_sync_at=invoice_db.last_sync_at,
            version=invoice_db.version,
        )

    def _to_db_model(self, invoice: Invoice) -> InvoiceDB:
        """Convierte entidad de dominio a modelo de BD."""
        invoice_db = InvoiceDB(
            series=invoice.series,
            document_type=invoice.document_type,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            issuer_id=invoice.issuer_id,
            issuer_name=invoice.issuer_name,
            issuer_tax_id=invoice.issuer_tax_id,
            receiver_id=invoice.receiver_id,
            receiver_name=invoice.receiver_name,
            receiver_tax_id=invoice.receiver_tax_id,
            currency=invoice.currency,
            subtotal=invoice.subtotal,
            tax_total=invoice.tax_total,
            discount_total=invoice.discount_total,
            withholding_total=invoice.withholding_total,
            total=invoice.total,
            status=invoice.status,
            ocr_engine=invoice.ocr_engine,
            ocr_confidence=invoice.ocr_confidence,
            processing_time=invoice.processing_time,
            file_path=invoice.file_path,
            notes=invoice.notes,
            created_by=invoice.created_by,
            updated_by=invoice.updated_by,
            sync_status=invoice.sync_status,
            version=invoice.version,
        )

        # Agregar items
        for item_entity in invoice.items:
            item_db = InvoiceItemDB(
                code=item_entity.code,
                description=item_entity.description,
                unit=item_entity.unit,
                quantity=item_entity.quantity,
                unit_price=item_entity.unit_price,
                discount_percent=item_entity.discount_percent,
                tax_percent=item_entity.tax_percent,
                subtotal=item_entity.subtotal,
                discount_amount=item_entity.discount_amount,
                tax_amount=item_entity.tax_amount,
                total=item_entity.total,
            )
            invoice_db.items.append(item_db)

        return invoice_db
