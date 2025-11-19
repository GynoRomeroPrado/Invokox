"""
Domain Entity: Company

Representa una empresa (emisor o receptor de facturas).
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


CompanyType = Literal["EMISOR", "RECEPTOR", "AMBOS"]


class Company(BaseModel):
    """
    Entidad de dominio que representa una empresa.

    Puede ser emisor, receptor o ambos.
    """

    id: Optional[int] = None
    tax_id: str = Field(..., description="RUC, RFC, NIT, etc.")
    name: str = Field(..., min_length=1, max_length=255)
    commercial_name: Optional[str] = Field(None, max_length=255)
    type: CompanyType = Field(default="AMBOS")

    # Información de contacto
    address: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)

    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)

    # Estadísticas (calculadas)
    invoice_count: int = Field(default=0, description="Número de facturas asociadas")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "tax_id": "20123456789",
                "name": "EMPRESA DEMO S.A.C.",
                "commercial_name": "EMPRESA DEMO",
                "type": "EMISOR",
                "address": "Av. Principal 123, Lima, Perú",
                "email": "contacto@empresademo.com",
                "phone": "+51 1 234-5678",
            }
        }

    def __str__(self) -> str:
        return f"{self.name} ({self.tax_id})"

    def __repr__(self) -> str:
        return f"Company(id={self.id}, tax_id='{self.tax_id}', name='{self.name}')"

    def update_timestamp(self) -> None:
        """Actualiza el timestamp de modificación."""
        self.updated_at = datetime.utcnow()

    def can_be_issuer(self) -> bool:
        """Verifica si la empresa puede ser emisor."""
        return self.type in ("EMISOR", "AMBOS")

    def can_be_receiver(self) -> bool:
        """Verifica si la empresa puede ser receptor."""
        return self.type in ("RECEPTOR", "AMBOS")
