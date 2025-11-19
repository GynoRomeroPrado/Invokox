"""
Value Object: TaxID

Representa un identificador fiscal (RUC, RFC, NIT, etc.) validado.
"""

import re
from dataclasses import dataclass
from typing import Literal


TaxIDType = Literal["RUC", "RFC", "NIT", "EIN", "VAT"]


@dataclass(frozen=True)
class TaxID:
    """
    Value Object que representa un ID de impuesto fiscal.

    Inmutable y auto-validado según el tipo.

    Examples:
        >>> ruc = TaxID("20123456789", "RUC")  # Perú
        >>> rfc = TaxID("XAXX010101000", "RFC")  # México
    """

    value: str
    type: TaxIDType = "RUC"

    def __post_init__(self) -> None:
        """Validación después de inicialización."""
        # Limpiar espacios y guiones
        cleaned = self.value.replace(" ", "").replace("-", "").upper()
        object.__setattr__(self, 'value', cleaned)

        # Validar según tipo
        if self.type == "RUC":
            self._validate_ruc()
        elif self.type == "RFC":
            self._validate_rfc()
        elif self.type == "NIT":
            self._validate_nit()
        elif self.type == "EIN":
            self._validate_ein()
        elif self.type == "VAT":
            self._validate_vat()
        else:
            raise ValueError(f"Invalid TaxID type: {self.type}")

    def _validate_ruc(self) -> None:
        """
        Valida RUC (Perú): 11 dígitos numéricos.

        Formato: XXXXXXXXXXX (11 dígitos)
        """
        if not re.match(r'^\d{11}$', self.value):
            raise ValueError(
                f"Invalid RUC format: {self.value}. "
                "Must be 11 numeric digits"
            )

    def _validate_rfc(self) -> None:
        """
        Valida RFC (México): 12-13 caracteres alfanuméricos.

        Formato Persona Moral: AAAMMDDXXX (10-13 caracteres)
        Formato Persona Física: AAAAMMDDXXX (13 caracteres)
        """
        if not re.match(r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$', self.value):
            raise ValueError(
                f"Invalid RFC format: {self.value}. "
                "Must match RFC pattern (12-13 alphanumeric)"
            )

    def _validate_nit(self) -> None:
        """
        Valida NIT (Colombia, Guatemala, etc.): 9-10 dígitos.

        Formato: XXXXXXXXX-X
        """
        if not re.match(r'^\d{9,10}$', self.value):
            raise ValueError(
                f"Invalid NIT format: {self.value}. "
                "Must be 9-10 numeric digits"
            )

    def _validate_ein(self) -> None:
        """
        Valida EIN (USA): 9 dígitos.

        Formato: XX-XXXXXXX
        """
        if not re.match(r'^\d{9}$', self.value):
            raise ValueError(
                f"Invalid EIN format: {self.value}. "
                "Must be 9 numeric digits"
            )

    def _validate_vat(self) -> None:
        """
        Valida VAT (Europa): Variable según país.

        Simplificado: 2 letras de país + 8-12 dígitos.
        """
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{8,12}$', self.value):
            raise ValueError(
                f"Invalid VAT format: {self.value}. "
                "Must start with 2 country letters + 8-12 alphanumeric"
            )

    def __str__(self) -> str:
        """Representación en string."""
        return self.value

    def __repr__(self) -> str:
        """Representación técnica."""
        return f"TaxID(value='{self.value}', type='{self.type}')"

    def formatted(self) -> str:
        """
        Retorna el TaxID formateado para display.

        Examples:
            RUC: 20-123456789
            RFC: XAXX-010101-000
            EIN: 12-3456789
        """
        if self.type == "RUC" and len(self.value) == 11:
            return f"{self.value[:2]}-{self.value[2:]}"
        elif self.type == "RFC" and len(self.value) == 13:
            return f"{self.value[:4]}-{self.value[4:10]}-{self.value[10:]}"
        elif self.type == "EIN" and len(self.value) == 9:
            return f"{self.value[:2]}-{self.value[2:]}"
        else:
            return self.value

    def to_dict(self) -> dict[str, str]:
        """Convierte a diccionario para serialización."""
        return {
            "value": self.value,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "TaxID":
        """Crea TaxID desde diccionario."""
        return cls(
            value=data["value"],
            type=data.get("type", "RUC"),  # type: ignore
        )
