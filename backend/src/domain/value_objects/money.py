"""
Value Object: Money

Representa una cantidad monetaria con su moneda.
Inmutable y validado.
"""

from decimal import Decimal
from dataclasses import dataclass
from typing import Literal


Currency = Literal["PEN", "USD", "EUR", "CLP", "MXN"]


@dataclass(frozen=True)
class Money:
    """
    Value Object que representa dinero con moneda.

    Inmutable y auto-validado.

    Examples:
        >>> total = Money(Decimal("1500.50"), "PEN")
        >>> tax = Money(Decimal("270.09"), "PEN")
        >>> subtotal = total - tax
    """

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        """Validación después de inicialización."""
        if not isinstance(self.amount, Decimal):
            # Convertir a Decimal si se pasó float/int
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))

        # Validar que la cantidad no sea negativa
        if self.amount < 0:
            raise ValueError(f"Money amount cannot be negative: {self.amount}")

        # Validar moneda
        valid_currencies: tuple[Currency, ...] = ("PEN", "USD", "EUR", "CLP", "MXN")
        if self.currency not in valid_currencies:
            raise ValueError(
                f"Invalid currency: {self.currency}. "
                f"Must be one of {valid_currencies}"
            )

    def __add__(self, other: "Money") -> "Money":
        """Suma de dinero (misma moneda)."""
        self._check_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Resta de dinero (misma moneda)."""
        self._check_same_currency(other)
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Subtraction would result in negative amount")
        return Money(result_amount, self.currency)

    def __mul__(self, factor: int | float | Decimal) -> "Money":
        """Multiplicación por un factor."""
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        return Money(self.amount * factor, self.currency)

    def __truediv__(self, divisor: int | float | Decimal) -> "Money":
        """División por un divisor."""
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / divisor, self.currency)

    def __eq__(self, other: object) -> bool:
        """Igualdad de dinero."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        """Menor que (misma moneda)."""
        self._check_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        """Menor o igual (misma moneda)."""
        self._check_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        """Mayor que (misma moneda)."""
        self._check_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        """Mayor o igual (misma moneda)."""
        self._check_same_currency(other)
        return self.amount >= other.amount

    def __str__(self) -> str:
        """Representación en string."""
        return f"{self.currency} {self.amount:.2f}"

    def __repr__(self) -> str:
        """Representación técnica."""
        return f"Money(amount=Decimal('{self.amount}'), currency='{self.currency}')"

    def _check_same_currency(self, other: "Money") -> None:
        """Verifica que dos Money tengan la misma moneda."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot operate with different currencies: "
                f"{self.currency} and {other.currency}"
            )

    def round(self, decimals: int = 2) -> "Money":
        """Redondea la cantidad a N decimales."""
        rounded_amount = round(self.amount, decimals)
        return Money(rounded_amount, self.currency)

    def to_dict(self) -> dict[str, str | float]:
        """Convierte a diccionario para serialización."""
        return {
            "amount": float(self.amount),
            "currency": self.currency,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | float]) -> "Money":
        """Crea Money desde diccionario."""
        return cls(
            amount=Decimal(str(data["amount"])),
            currency=data["currency"],  # type: ignore
        )

    @classmethod
    def zero(cls, currency: Currency = "PEN") -> "Money":
        """Crea Money con valor cero."""
        return cls(Decimal("0"), currency)
