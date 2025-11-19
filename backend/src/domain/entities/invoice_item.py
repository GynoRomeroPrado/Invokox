"""
Domain Entity: InvoiceItem

Representa una línea de detalle/item de una factura.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class InvoiceItem(BaseModel):
    """
    Entidad de dominio que representa un item/línea de factura.

    Contiene descripción, cantidad, precios y cálculos automáticos.
    """

    id: Optional[int] = None
    invoice_id: Optional[int] = None

    # Información del producto/servicio
    code: Optional[str] = Field(None, max_length=100, description="Código del producto")
    description: str = Field(..., min_length=1, max_length=500)
    unit: Optional[str] = Field(default="UND", max_length=10, description="Unidad de medida")

    # Cantidades y precios
    quantity: Decimal = Field(..., gt=0, description="Cantidad")
    unit_price: Decimal = Field(..., ge=0, description="Precio unitario sin impuestos")

    # Descuentos e impuestos
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_percent: Decimal = Field(default=Decimal("18"), ge=0, le=100, description="IGV/IVA %")

    # Totales (calculados automáticamente)
    subtotal: Decimal = Field(default=Decimal("0"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0"), ge=0)
    total: Decimal = Field(default=Decimal("0"), ge=0)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "PROD-001",
                "description": "Laptop HP Pavilion 15",
                "unit": "UND",
                "quantity": 2,
                "unit_price": 2500.00,
                "discount_percent": 10,
                "tax_percent": 18,
            }
        }

    @field_validator('quantity', 'unit_price', 'discount_percent', 'tax_percent', mode='before')
    @classmethod
    def convert_to_decimal(cls, v: any) -> Decimal:
        """Convierte valores numéricos a Decimal."""
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))

    def model_post_init(self, __context: any) -> None:
        """Calcula totales automáticamente después de inicialización."""
        self.calculate_totals()

    def calculate_totals(self) -> None:
        """
        Calcula todos los totales del item.

        Fórmulas:
        - subtotal = quantity * unit_price
        - discount_amount = subtotal * (discount_percent / 100)
        - subtotal_after_discount = subtotal - discount_amount
        - tax_amount = subtotal_after_discount * (tax_percent / 100)
        - total = subtotal_after_discount + tax_amount
        """
        # Subtotal sin descuentos ni impuestos
        self.subtotal = self.quantity * self.unit_price

        # Descuento
        self.discount_amount = self.subtotal * (self.discount_percent / Decimal("100"))
        subtotal_after_discount = self.subtotal - self.discount_amount

        # Impuesto sobre el subtotal después del descuento
        self.tax_amount = subtotal_after_discount * (self.tax_percent / Decimal("100"))

        # Total final
        self.total = subtotal_after_discount + self.tax_amount

        # Redondear a 2 decimales
        self.subtotal = self.subtotal.quantize(Decimal("0.01"))
        self.discount_amount = self.discount_amount.quantize(Decimal("0.01"))
        self.tax_amount = self.tax_amount.quantize(Decimal("0.01"))
        self.total = self.total.quantize(Decimal("0.01"))

    def update_quantity(self, new_quantity: Decimal) -> None:
        """Actualiza la cantidad y recalcula totales."""
        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        self.quantity = new_quantity
        self.calculate_totals()

    def update_unit_price(self, new_price: Decimal) -> None:
        """Actualiza el precio unitario y recalcula totales."""
        if new_price < 0:
            raise ValueError("Unit price cannot be negative")
        self.unit_price = new_price
        self.calculate_totals()

    def apply_discount(self, discount_percent: Decimal) -> None:
        """Aplica un descuento y recalcula totales."""
        if not (0 <= discount_percent <= 100):
            raise ValueError("Discount percent must be between 0 and 100")
        self.discount_percent = discount_percent
        self.calculate_totals()

    def __str__(self) -> str:
        return f"{self.description} (Qty: {self.quantity}, Total: {self.total})"

    def __repr__(self) -> str:
        return (
            f"InvoiceItem(id={self.id}, description='{self.description}', "
            f"quantity={self.quantity}, total={self.total})"
        )
