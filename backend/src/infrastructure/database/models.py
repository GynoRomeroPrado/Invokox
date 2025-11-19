"""
SQLModel Models - Database Schema

Modelos de base de datos usando SQLModel (SQLAlchemy + Pydantic).
Estos modelos son la representación en BD de las entidades de dominio.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


# ==============================================================================
# COMPANY MODEL
# ==============================================================================

class CompanyDB(SQLModel, table=True):
    """Modelo de base de datos para empresas."""

    __tablename__ = "companies"

    id: Optional[int] = Field(default=None, primary_key=True)
    tax_id: str = Field(index=True, unique=True, max_length=50)
    name: str = Field(max_length=255)
    commercial_name: Optional[str] = Field(default=None, max_length=255)
    type: str = Field(default="AMBOS", max_length=20)  # EMISOR, RECEPTOR, AMBOS

    # Contact info
    address: Optional[str] = Field(default=None, max_length=500)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = Field(default=None, max_length=255)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    invoice_count: int = Field(default=0)

    # Relationships
    issued_invoices: list["InvoiceDB"] = Relationship(
        back_populates="issuer",
        sa_relationship_kwargs={"foreign_keys": "[InvoiceDB.issuer_id]"}
    )
    received_invoices: list["InvoiceDB"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "[InvoiceDB.receiver_id]"}
    )


# ==============================================================================
# INVOICE MODEL
# ==============================================================================

class InvoiceDB(SQLModel, table=True):
    """Modelo de base de datos para facturas."""

    __tablename__ = "invoices"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Document info
    series: str = Field(index=True, unique=True, max_length=50)
    document_type: str = Field(default="FACTURA", max_length=50)
    issue_date: date = Field(index=True)
    due_date: Optional[date] = Field(default=None)

    # Foreign Keys
    issuer_id: int = Field(foreign_key="companies.id", index=True)
    issuer_name: str = Field(max_length=255)  # Desnormalizado para performance
    issuer_tax_id: str = Field(max_length=50)

    receiver_id: int = Field(foreign_key="companies.id", index=True)
    receiver_name: str = Field(max_length=255)
    receiver_tax_id: str = Field(max_length=50)

    # Monetary info
    currency: str = Field(default="PEN", max_length=3)
    subtotal: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    tax_total: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    discount_total: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    withholding_total: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    total: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2, index=True)

    # OCR info
    status: str = Field(default="PENDING", max_length=20, index=True)
    ocr_engine: Optional[str] = Field(default=None, max_length=50)
    ocr_confidence: Decimal = Field(default=Decimal("0"), max_digits=3, decimal_places=2)
    processing_time: Optional[int] = Field(default=None)  # seconds

    # Files
    file_path: str = Field(max_length=500)

    # Notes
    notes: Optional[str] = Field(default=None, max_length=2000)

    # Audit metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    created_by: str = Field(max_length=100)
    updated_by: Optional[str] = Field(default=None, max_length=100)

    # Sync fields (para modo dual)
    sync_status: str = Field(default="synced", max_length=20)
    last_sync_at: Optional[datetime] = Field(default=None)
    version: int = Field(default=1)  # Optimistic locking

    # Relationships
    issuer: CompanyDB = Relationship(
        back_populates="issued_invoices",
        sa_relationship_kwargs={"foreign_keys": "[InvoiceDB.issuer_id]"}
    )
    receiver: CompanyDB = Relationship(
        back_populates="received_invoices",
        sa_relationship_kwargs={"foreign_keys": "[InvoiceDB.receiver_id]"}
    )
    items: list["InvoiceItemDB"] = Relationship(
        back_populates="invoice",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ==============================================================================
# INVOICE ITEM MODEL
# ==============================================================================

class InvoiceItemDB(SQLModel, table=True):
    """Modelo de base de datos para items de factura."""

    __tablename__ = "invoice_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoices.id", index=True)

    # Product/Service info
    code: Optional[str] = Field(default=None, max_length=100)
    description: str = Field(max_length=500)
    unit: str = Field(default="UND", max_length=10)

    # Quantities and prices
    quantity: Decimal = Field(max_digits=10, decimal_places=2)
    unit_price: Decimal = Field(max_digits=15, decimal_places=2)

    # Discounts and taxes
    discount_percent: Decimal = Field(default=Decimal("0"), max_digits=5, decimal_places=2)
    tax_percent: Decimal = Field(default=Decimal("18"), max_digits=5, decimal_places=2)

    # Calculated totals
    subtotal: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    discount_amount: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    total: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)

    # Relationship
    invoice: InvoiceDB = Relationship(back_populates="items")


# ==============================================================================
# AUDIT LOG MODEL (opcional, para futuro)
# ==============================================================================

class AuditLogDB(SQLModel, table=True):
    """Modelo de base de datos para logs de auditoría."""

    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoices.id", index=True)
    user_id: Optional[int] = Field(default=None)  # Para cuando se implemente users
    user_email: str = Field(max_length=255)
    action: str = Field(max_length=50)  # CREATE, UPDATE, DELETE, APPROVE, REJECT
    changes: Optional[str] = Field(default=None)  # JSON con cambios
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)
