"""
Domain Entity: Invoice

Entidad raíz (Aggregate Root) que representa una factura.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

from .invoice_item import InvoiceItem


InvoiceStatus = Literal["PENDING", "PROCESSING", "COMPLETED", "APPROVED", "REJECTED", "ERROR"]
Currency = Literal["PEN", "USD", "EUR", "CLP", "MXN"]
OcrEngine = Literal["PaddleOCR", "Docling", "Tesseract"]


class Invoice(BaseModel):
    """
    Entidad raíz (Aggregate Root) que representa una factura.

    Gestiona su ciclo de vida completo y mantiene la integridad
    de sus items relacionados.
    """

    id: Optional[int] = None

    # Información del documento
    series: str = Field(..., max_length=50, description="Serie del documento (ej: F001-00001234)")
    document_type: str = Field(default="FACTURA", max_length=50)
    issue_date: date = Field(..., description="Fecha de emisión")
    due_date: Optional[date] = Field(None, description="Fecha de vencimiento")

    # Relaciones con empresas (FKs)
    issuer_id: int = Field(..., description="ID de la empresa emisora")
    issuer_name: str = Field(..., max_length=255)
    issuer_tax_id: str = Field(..., max_length=50)

    receiver_id: int = Field(..., description="ID de la empresa receptora")
    receiver_name: str = Field(..., max_length=255)
    receiver_tax_id: str = Field(..., max_length=50)

    # Información monetaria
    currency: Currency = Field(default="PEN")

    # Totales (calculados desde items)
    subtotal: Decimal = Field(default=Decimal("0"), ge=0)
    tax_total: Decimal = Field(default=Decimal("0"), ge=0)
    discount_total: Decimal = Field(default=Decimal("0"), ge=0)
    withholding_total: Decimal = Field(default=Decimal("0"), ge=0)
    total: Decimal = Field(default=Decimal("0"), ge=0)

    # Items de la factura
    items: list[InvoiceItem] = Field(default_factory=list)

    # Información del procesamiento OCR
    status: InvoiceStatus = Field(default="PENDING")
    ocr_engine: Optional[OcrEngine] = None
    ocr_confidence: Decimal = Field(default=Decimal("0"), ge=0, le=1)
    processing_time: Optional[int] = Field(None, description="Tiempo de procesamiento en segundos")

    # Archivos
    file_path: str = Field(..., max_length=500, description="Ruta del PDF/imagen original")

    # Notas y observaciones
    notes: Optional[str] = Field(None, max_length=2000)

    # Metadatos de auditoría
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: str = Field(..., max_length=100)
    updated_by: Optional[str] = Field(None, max_length=100)

    # Sincronización (para modo dual)
    sync_status: str = Field(default="synced", max_length=20)
    last_sync_at: Optional[datetime] = None
    version: int = Field(default=1, description="Control de versión optimista")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "series": "F001-00001234",
                "document_type": "FACTURA",
                "issue_date": "2025-01-15",
                "issuer_id": 1,
                "issuer_name": "EMPRESA EMISORA S.A.C.",
                "issuer_tax_id": "20123456789",
                "receiver_id": 2,
                "receiver_name": "EMPRESA RECEPTORA S.A.",
                "receiver_tax_id": "20987654321",
                "currency": "PEN",
                "file_path": "/uploads/2025/01/factura_001.pdf",
                "created_by": "admin@invokox.com",
            }
        }

    @field_validator('subtotal', 'tax_total', 'discount_total', 'withholding_total', 'total', 'ocr_confidence', mode='before')
    @classmethod
    def convert_to_decimal(cls, v: any) -> Decimal:
        """Convierte valores numéricos a Decimal."""
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))

    def add_item(self, item: InvoiceItem) -> None:
        """
        Agrega un item a la factura y recalcula totales.

        Args:
            item: Item a agregar
        """
        self.items.append(item)
        self.calculate_totals()

    def remove_item(self, item_id: int) -> None:
        """
        Elimina un item de la factura y recalcula totales.

        Args:
            item_id: ID del item a eliminar

        Raises:
            ValueError: Si el item no existe
        """
        original_count = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]

        if len(self.items) == original_count:
            raise ValueError(f"Item with id {item_id} not found")

        self.calculate_totals()

    def calculate_totals(self) -> None:
        """
        Calcula todos los totales de la factura desde sus items.

        Fórmulas:
        - subtotal = suma de subtotales de items (sin descuentos ni impuestos)
        - discount_total = suma de descuentos de items
        - tax_total = suma de impuestos de items
        - total = subtotal - discount_total + tax_total - withholding_total
        """
        if not self.items:
            self.subtotal = Decimal("0")
            self.discount_total = Decimal("0")
            self.tax_total = Decimal("0")
            self.total = Decimal("0")
            return

        # Calcular desde items
        self.subtotal = sum(item.subtotal for item in self.items)
        self.discount_total = sum(item.discount_amount for item in self.items)
        self.tax_total = sum(item.tax_amount for item in self.items)

        # Total final
        self.total = (
            self.subtotal
            - self.discount_total
            + self.tax_total
            - self.withholding_total
        )

        # Redondear a 2 decimales
        self.subtotal = self.subtotal.quantize(Decimal("0.01"))
        self.discount_total = self.discount_total.quantize(Decimal("0.01"))
        self.tax_total = self.tax_total.quantize(Decimal("0.01"))
        self.total = self.total.quantize(Decimal("0.01"))

    def mark_as_processing(self, ocr_engine: OcrEngine) -> None:
        """Marca la factura como en procesamiento OCR."""
        self.status = "PROCESSING"
        self.ocr_engine = ocr_engine
        self.update_timestamp()

    def mark_as_completed(self, confidence: Decimal, processing_time: int) -> None:
        """Marca la factura como completada después del OCR."""
        self.status = "COMPLETED"
        self.ocr_confidence = confidence
        self.processing_time = processing_time
        self.update_timestamp()

    def mark_as_error(self, error_message: str) -> None:
        """Marca la factura con error."""
        self.status = "ERROR"
        self.notes = f"ERROR: {error_message}"
        self.update_timestamp()

    def approve(self, approved_by: str) -> None:
        """Aprueba la factura."""
        if self.status not in ("COMPLETED", "PENDING"):
            raise ValueError(f"Cannot approve invoice with status {self.status}")
        self.status = "APPROVED"
        self.updated_by = approved_by
        self.update_timestamp()

    def reject(self, rejected_by: str, reason: Optional[str] = None) -> None:
        """Rechaza la factura."""
        if self.status == "APPROVED":
            raise ValueError("Cannot reject an already approved invoice")
        self.status = "REJECTED"
        self.updated_by = rejected_by
        if reason:
            self.notes = f"REJECTED: {reason}"
        self.update_timestamp()

    def update_timestamp(self) -> None:
        """Actualiza el timestamp de modificación e incrementa versión."""
        self.updated_at = datetime.utcnow()
        self.version += 1

    def mark_sync_pending(self) -> None:
        """Marca la factura como pendiente de sincronización."""
        self.sync_status = "pending"

    def mark_synced(self) -> None:
        """Marca la factura como sincronizada."""
        self.sync_status = "synced"
        self.last_sync_at = datetime.utcnow()

    def is_editable(self) -> bool:
        """Verifica si la factura puede ser editada."""
        return self.status in ("PENDING", "COMPLETED", "ERROR")

    def is_deletable(self) -> bool:
        """Verifica si la factura puede ser eliminada."""
        return self.status not in ("APPROVED",)

    def __str__(self) -> str:
        return f"Invoice {self.series} - {self.issuer_name} ({self.currency} {self.total})"

    def __repr__(self) -> str:
        return (
            f"Invoice(id={self.id}, series='{self.series}', "
            f"total={self.total}, status='{self.status}')"
        )
