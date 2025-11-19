"""
==============================================================================
TESTS - VALUE OBJECTS
==============================================================================
Tests unitarios para Value Objects del Domain Layer.

Value Objects son objetos inmutables que se identifican por su valor,
no por su identidad. Características:
- Inmutables (no se pueden modificar después de crear)
- Igualdad por valor (dos objetos con mismo valor son iguales)
- Auto-validación (validan su estado en el constructor)
- Sin identidad única (no tienen ID)

Tests incluidos:
- Money: Objeto de valor para manejar montos monetarios
- TaxID: Objeto de valor para identificación fiscal

Ejecutar:
    pytest tests/domain/test_value_objects.py
    pytest tests/domain/test_value_objects.py::TestMoney
    pytest tests/domain/test_value_objects.py::TestMoney::test_should_create_valid_money
==============================================================================
"""

from decimal import Decimal

import pytest

from src.domain.value_objects.money import Money
from src.domain.value_objects.tax_id import TaxID

# ==============================================================================
# TESTS - MONEY VALUE OBJECT
# ==============================================================================


class TestMoney:
    """
    Test suite para el Value Object Money.

    Money representa un monto monetario con:
    - amount: Decimal (precisión para dinero)
    - currency: str (código de moneda ISO 4217: PEN, USD, MXN, etc.)

    Características testeadas:
    - Creación válida
    - Validaciones (monto positivo, moneda válida)
    - Operaciones aritméticas (suma, resta, multiplicación, división)
    - Comparaciones (igual, mayor, menor)
    - Inmutabilidad
    """

    # ==========================================================================
    # TESTS - CREACIÓN Y VALIDACIÓN
    # ==========================================================================

    def test_should_create_valid_money(self):
        """
        Test: Debe crear Money válido con amount y currency.

        Verifica que se puede crear un Money object con valores válidos
        y que los atributos se asignan correctamente.
        """
        # Arrange: Preparar datos de prueba
        amount = Decimal("100.50")
        currency = "PEN"

        # Act: Crear objeto Money
        money = Money(amount=amount, currency=currency)

        # Assert: Verificar que se creó correctamente
        assert money.amount == amount
        assert money.currency == currency

    def test_should_create_money_with_zero_amount(self):
        """
        Test: Debe permitir crear Money con monto cero.

        Casos de uso válidos:
        - Facturas sin costo
        - Descuentos del 100%
        - Valores iniciales
        """
        # Arrange & Act
        money = Money(amount=Decimal("0.00"), currency="USD")

        # Assert
        assert money.amount == Decimal("0.00")
        assert money.currency == "USD"

    def test_should_raise_error_for_negative_amount(self):
        """
        Test: Debe lanzar ValueError si el monto es negativo.

        Regla de negocio: Los montos monetarios no pueden ser negativos.
        Para representar deudas o créditos, usar campos separados o
        signos en el contexto de negocio.
        """
        # Arrange
        negative_amount = Decimal("-100.00")

        # Act & Assert: Verificar que lanza ValueError
        with pytest.raises(ValueError) as exc_info:
            Money(amount=negative_amount, currency="PEN")

        # Verificar mensaje de error
        assert "Amount cannot be negative" in str(exc_info.value)

    def test_should_raise_error_for_invalid_currency(self):
        """
        Test: Debe lanzar ValueError si la moneda es inválida.

        Monedas válidas: Códigos ISO 4217 de 3 letras (PEN, USD, EUR, etc.)
        Monedas inválidas: Vacías, muy cortas, muy largas, con números
        """
        # Arrange: Diferentes casos de monedas inválidas
        invalid_currencies = [
            "",  # Vacía
            "P",  # Muy corta
            "PE",  # Muy corta
            "PENS",  # Muy larga
            "123",  # Con números
            "pe",  # Minúsculas (debe ser mayúsculas)
        ]

        # Act & Assert: Cada moneda inválida debe lanzar ValueError
        for invalid_currency in invalid_currencies:
            with pytest.raises(ValueError) as exc_info:
                Money(amount=Decimal("100.00"), currency=invalid_currency)

            # Verificar que el error menciona moneda inválida
            assert "Invalid currency" in str(exc_info.value)

    def test_should_accept_common_currencies(self):
        """
        Test: Debe aceptar monedas comunes ISO 4217.

        Verifica que las monedas más utilizadas en Latinoamérica
        y el mundo son aceptadas.
        """
        # Arrange: Monedas comunes que deben ser válidas
        valid_currencies = [
            "PEN",  # Sol peruano
            "USD",  # Dólar estadounidense
            "EUR",  # Euro
            "MXN",  # Peso mexicano
            "COP",  # Peso colombiano
            "CLP",  # Peso chileno
            "ARS",  # Peso argentino
            "BRL",  # Real brasileño
        ]

        # Act & Assert: Cada moneda debe crear Money exitosamente
        for currency in valid_currencies:
            money = Money(amount=Decimal("100.00"), currency=currency)
            assert money.currency == currency

    # ==========================================================================
    # TESTS - OPERACIONES ARITMÉTICAS
    # ==========================================================================

    def test_should_add_money_with_same_currency(self, sample_money):
        """
        Test: Debe sumar dos Money objects con la misma moneda.

        Args:
            sample_money: Fixture que crea Money(1000.00, "PEN")
        """
        # Arrange: Usar fixture + crear otro Money
        money1 = sample_money  # 1000.00 PEN
        money2 = Money(amount=Decimal("500.00"), currency="PEN")

        # Act: Sumar
        result = money1 + money2

        # Assert: Verificar resultado
        assert result.amount == Decimal("1500.00")
        assert result.currency == "PEN"
        # Verificar inmutabilidad: originales no cambian
        assert money1.amount == Decimal("1000.00")
        assert money2.amount == Decimal("500.00")

    def test_should_raise_error_when_adding_different_currencies(self):
        """
        Test: Debe lanzar ValueError al sumar monedas diferentes.

        Regla de negocio: No se pueden sumar directamente PEN + USD.
        Primero se debe convertir a la misma moneda.
        """
        # Arrange
        money_pen = Money(amount=Decimal("100.00"), currency="PEN")
        money_usd = Money(amount=Decimal("100.00"), currency="USD")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            money_pen + money_usd

        assert "Cannot add money with different currencies" in str(exc_info.value)

    def test_should_subtract_money_with_same_currency(self):
        """
        Test: Debe restar dos Money objects con la misma moneda.

        Nota: El resultado puede ser negativo en la resta,
        pero Money no puede tener amount negativo, por lo que
        la resta solo es válida si el resultado es >= 0.
        """
        # Arrange
        money1 = Money(amount=Decimal("1000.00"), currency="PEN")
        money2 = Money(amount=Decimal("300.00"), currency="PEN")

        # Act
        result = money1 - money2

        # Assert
        assert result.amount == Decimal("700.00")
        assert result.currency == "PEN"

    def test_should_raise_error_when_subtracting_results_in_negative(self):
        """
        Test: Debe lanzar ValueError si la resta resulta en negativo.

        Ejemplo: 100 - 200 = -100 (no permitido)
        """
        # Arrange
        money1 = Money(amount=Decimal("100.00"), currency="PEN")
        money2 = Money(amount=Decimal("200.00"), currency="PEN")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            money1 - money2

        assert "Amount cannot be negative" in str(exc_info.value)

    def test_should_multiply_money_by_scalar(self):
        """
        Test: Debe multiplicar Money por un escalar (int o Decimal).

        Casos de uso:
        - Calcular precio total: precio_unitario * cantidad
        - Aplicar porcentajes: monto * 1.18 (con IGV)
        """
        # Arrange
        money = Money(amount=Decimal("100.00"), currency="USD")

        # Act: Multiplicar por entero
        result1 = money * 3
        # Act: Multiplicar por Decimal
        result2 = money * Decimal("2.5")

        # Assert
        assert result1.amount == Decimal("300.00")
        assert result1.currency == "USD"
        assert result2.amount == Decimal("250.00")
        assert result2.currency == "USD"

    def test_should_divide_money_by_scalar(self):
        """
        Test: Debe dividir Money por un escalar.

        Casos de uso:
        - Dividir cuenta entre personas
        - Calcular precio unitario: total / cantidad
        """
        # Arrange
        money = Money(amount=Decimal("100.00"), currency="EUR")

        # Act
        result = money / 4

        # Assert
        assert result.amount == Decimal("25.00")
        assert result.currency == "EUR"

    def test_should_raise_error_when_dividing_by_zero(self):
        """
        Test: Debe lanzar ZeroDivisionError al dividir por cero.
        """
        # Arrange
        money = Money(amount=Decimal("100.00"), currency="PEN")

        # Act & Assert
        with pytest.raises(ZeroDivisionError):
            money / 0

    # ==========================================================================
    # TESTS - COMPARACIONES
    # ==========================================================================

    def test_should_compare_money_with_same_currency(self):
        """
        Test: Debe comparar Money objects con la misma moneda.

        Operadores: ==, !=, <, <=, >, >=
        """
        # Arrange
        money1 = Money(amount=Decimal("100.00"), currency="PEN")
        money2 = Money(amount=Decimal("200.00"), currency="PEN")
        money3 = Money(amount=Decimal("100.00"), currency="PEN")

        # Assert: Igualdad
        assert money1 == money3  # Mismos valores
        assert money1 != money2  # Diferentes valores

        # Assert: Comparaciones
        assert money1 < money2  # 100 < 200
        assert money1 <= money2  # 100 <= 200
        assert money1 <= money3  # 100 <= 100
        assert money2 > money1  # 200 > 100
        assert money2 >= money1  # 200 >= 100
        assert money1 >= money3  # 100 >= 100

    def test_should_raise_error_when_comparing_different_currencies(self):
        """
        Test: Debe lanzar ValueError al comparar monedas diferentes.

        No se puede comparar directamente 100 PEN con 100 USD.
        """
        # Arrange
        money_pen = Money(amount=Decimal("100.00"), currency="PEN")
        money_usd = Money(amount=Decimal("100.00"), currency="USD")

        # Act & Assert: Cada operación de comparación debe fallar
        with pytest.raises(ValueError):
            money_pen < money_usd

        with pytest.raises(ValueError):
            money_pen > money_usd

        with pytest.raises(ValueError):
            money_pen <= money_usd

        with pytest.raises(ValueError):
            money_pen >= money_usd

    def test_should_check_equality_by_value(self):
        """
        Test: Debe verificar igualdad por valor, no por identidad.

        Value Object: Dos instancias con mismo valor son iguales,
        aunque sean objetos diferentes en memoria.
        """
        # Arrange: Crear dos Money diferentes con mismos valores
        money1 = Money(amount=Decimal("100.00"), currency="PEN")
        money2 = Money(amount=Decimal("100.00"), currency="PEN")

        # Assert: Son iguales por valor
        assert money1 == money2
        # Pero NO son el mismo objeto (identidades diferentes)
        assert money1 is not money2

    # ==========================================================================
    # TESTS - INMUTABILIDAD
    # ==========================================================================

    def test_should_be_immutable(self):
        """
        Test: Money debe ser inmutable (no modificable después de crear).

        Value Objects deben ser inmutables para:
        - Evitar efectos secundarios
        - Ser seguros para usar como keys en diccionarios
        - Facilitar reasoning sobre el código
        """
        # Arrange
        money = Money(amount=Decimal("100.00"), currency="PEN")
        original_amount = money.amount
        original_currency = money.currency

        # Act: Intentar modificar (debe lanzar error o no tener efecto)
        # Nota: En Python, la inmutabilidad se logra con @dataclass(frozen=True)
        # o property sin setter

        # Assert: Verificar que no se puede modificar
        with pytest.raises(AttributeError):
            money.amount = Decimal("200.00")  # type: ignore

        with pytest.raises(AttributeError):
            money.currency = "USD"  # type: ignore

        # Verificar que valores originales no cambiaron
        assert money.amount == original_amount
        assert money.currency == original_currency

    def test_should_create_new_instance_on_operations(self):
        """
        Test: Operaciones deben crear nuevas instancias, no modificar original.

        Inmutabilidad significa que cada operación retorna un NUEVO objeto.
        """
        # Arrange
        original = Money(amount=Decimal("100.00"), currency="PEN")
        original_id = id(original)  # Identidad en memoria

        # Act: Realizar operaciones
        result1 = original + Money(amount=Decimal("50.00"), currency="PEN")
        result2 = original * 2

        # Assert: Son objetos diferentes
        assert id(result1) != original_id  # Nueva instancia
        assert id(result2) != original_id  # Nueva instancia
        # Original no cambió
        assert original.amount == Decimal("100.00")

    # ==========================================================================
    # TESTS - REPRESENTACIÓN Y FORMATO
    # ==========================================================================

    def test_should_have_string_representation(self):
        """
        Test: Money debe tener representación en string legible.

        Formato esperado: "100.00 PEN"
        """
        # Arrange
        money = Money(amount=Decimal("100.50"), currency="USD")

        # Act
        string_repr = str(money)

        # Assert
        assert "100.50" in string_repr
        assert "USD" in string_repr

    def test_should_handle_decimal_precision(self):
        """
        Test: Money debe manejar precisión decimal correctamente.

        Dinero generalmente usa 2 decimales, pero internamente
        se deben preservar más decimales para cálculos exactos.
        """
        # Arrange: Crear con más de 2 decimales
        money = Money(amount=Decimal("100.123456"), currency="PEN")

        # Assert: Decimales se preservan
        assert money.amount == Decimal("100.123456")

        # Para display, redondear a 2 decimales
        display_amount = round(money.amount, 2)
        assert display_amount == Decimal("100.12")


# ==============================================================================
# TESTS - TAX ID VALUE OBJECT
# ==============================================================================


class TestTaxID:
    """
    Test suite para el Value Object TaxID.

    TaxID representa una identificación fiscal/tributaria con:
    - value: str (el número/código de identificación)
    - type: str (tipo: RUC, RFC, NIT, EIN, VAT, etc.)

    Tipos soportados:
    - RUC: Perú (11 dígitos)
    - RFC: México (12-13 caracteres alfanuméricos)
    - NIT: Colombia, Bolivia (9-10 dígitos + verificador)
    - EIN: USA (9 dígitos, formato XX-XXXXXXX)
    - VAT: Europa (variable según país)
    """

    # ==========================================================================
    # TESTS - CREACIÓN Y VALIDACIÓN
    # ==========================================================================

    def test_should_create_valid_tax_id(self):
        """
        Test: Debe crear TaxID válido con value y type.
        """
        # Arrange
        value = "20123456789"
        type_value = "RUC"

        # Act
        tax_id = TaxID(value=value, type=type_value)

        # Assert
        assert tax_id.value == value
        assert tax_id.type == type_value

    def test_should_validate_peru_ruc(self, sample_tax_id_peru):
        """
        Test: Debe validar RUC de Perú correctamente.

        RUC Perú:
        - 11 dígitos numéricos
        - Comienza con 10, 15, 16, 17, o 20
        - Tiene dígito verificador

        Args:
            sample_tax_id_peru: Fixture con RUC válido
        """
        # Assert: RUC de fixture es válido
        assert sample_tax_id_peru.is_valid()
        assert sample_tax_id_peru.type == "RUC"
        assert len(sample_tax_id_peru.value) == 11

    def test_should_invalidate_wrong_length_ruc(self):
        """
        Test: Debe invalidar RUC con longitud incorrecta.

        RUC debe tener exactamente 11 dígitos.
        """
        # Arrange: RUCs con longitud incorrecta
        invalid_rucs = [
            "2012345678",  # 10 dígitos (muy corto)
            "201234567890",  # 12 dígitos (muy largo)
            "123",  # Muy corto
        ]

        # Act & Assert
        for invalid_ruc in invalid_rucs:
            tax_id = TaxID(value=invalid_ruc, type="RUC")
            assert not tax_id.is_valid()

    def test_should_invalidate_non_numeric_ruc(self):
        """
        Test: Debe invalidar RUC con caracteres no numéricos.

        RUC solo puede contener dígitos.
        """
        # Arrange
        invalid_ruc = "2012345678A"  # Contiene letra

        # Act
        tax_id = TaxID(value=invalid_ruc, type="RUC")

        # Assert
        assert not tax_id.is_valid()

    def test_should_validate_mexico_rfc(self, sample_tax_id_mexico):
        """
        Test: Debe validar RFC de México correctamente.

        RFC México:
        - Personas morales: 12 caracteres (3 letras + 6 dígitos + 3 alfanum)
        - Personas físicas: 13 caracteres (4 letras + 6 dígitos + 3 alfanum)

        Args:
            sample_tax_id_mexico: Fixture con RFC válido
        """
        # Assert
        assert sample_tax_id_mexico.is_valid()
        assert sample_tax_id_mexico.type == "RFC"
        assert len(sample_tax_id_mexico.value) in [12, 13]

    def test_should_format_tax_id_for_display(self):
        """
        Test: Debe formatear TaxID para display legible.

        Ejemplos:
        - RUC: 20-12345678-9
        - RFC: ABC-123456-AB1
        - EIN: 12-3456789
        """
        # Arrange
        ruc = TaxID(value="20123456789", type="RUC")

        # Act
        formatted = ruc.formatted()

        # Assert: Verifica que tiene formato
        # (implementación específica depende del código)
        assert formatted is not None
        assert "20123456789" in formatted or "20-123456789" in formatted

    def test_should_check_equality_by_value(self):
        """
        Test: Debe verificar igualdad por valor.

        Dos TaxID con mismo value y type son iguales.
        """
        # Arrange
        tax_id1 = TaxID(value="20123456789", type="RUC")
        tax_id2 = TaxID(value="20123456789", type="RUC")
        tax_id3 = TaxID(value="20987654321", type="RUC")

        # Assert
        assert tax_id1 == tax_id2  # Mismos valores
        assert tax_id1 != tax_id3  # Diferentes valores
        assert tax_id1 is not tax_id2  # Diferentes objetos

    def test_should_be_immutable(self):
        """
        Test: TaxID debe ser inmutable.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")

        # Act & Assert: No se puede modificar
        with pytest.raises(AttributeError):
            tax_id.value = "20987654321"  # type: ignore

        with pytest.raises(AttributeError):
            tax_id.type = "RFC"  # type: ignore

    def test_should_normalize_tax_id_value(self):
        """
        Test: Debe normalizar el valor del TaxID.

        Normalización:
        - Eliminar espacios
        - Eliminar guiones
        - Mayúsculas
        """
        # Arrange: TaxID con formato "sucio"
        tax_id = TaxID(value="20-123-456-789", type="RUC")

        # Act: Obtener valor normalizado
        normalized = tax_id.normalized()

        # Assert: Sin guiones ni espacios
        assert normalized == "20123456789"
        assert "-" not in normalized
        assert " " not in normalized

    def test_should_validate_different_tax_id_types(self):
        """
        Test: Debe validar diferentes tipos de TaxID.

        Cada tipo tiene sus propias reglas de validación.
        """
        # Arrange: Diferentes tipos válidos
        test_cases = [
            ("20123456789", "RUC", True),  # RUC Perú válido
            ("ABC123456789", "RFC", True),  # RFC México válido
            ("12-3456789", "EIN", True),  # EIN USA válido
            ("12345", "RUC", False),  # RUC inválido (muy corto)
            ("", "RFC", False),  # RFC vacío
        ]

        # Act & Assert
        for value, type_val, expected_valid in test_cases:
            tax_id = TaxID(value=value, type=type_val)
            assert tax_id.is_valid() == expected_valid

    def test_should_have_string_representation(self):
        """
        Test: TaxID debe tener representación en string.

        Formato esperado: "RUC: 20123456789" o similar
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")

        # Act
        string_repr = str(tax_id)

        # Assert
        assert "RUC" in string_repr
        assert "20123456789" in string_repr

    # ==========================================================================
    # TESTS - CASOS EDGE
    # ==========================================================================

    def test_should_handle_empty_tax_id(self):
        """
        Test: Debe manejar TaxID vacío correctamente.

        TaxID vacío es inválido.
        """
        # Arrange
        tax_id = TaxID(value="", type="RUC")

        # Assert
        assert not tax_id.is_valid()

    def test_should_handle_whitespace_tax_id(self):
        """
        Test: Debe manejar TaxID con solo espacios.

        Espacios deben ser eliminados en normalización.
        """
        # Arrange
        tax_id = TaxID(value="  20123456789  ", type="RUC")

        # Act
        normalized = tax_id.normalized()

        # Assert
        assert normalized == "20123456789"
        assert tax_id.is_valid()  # Válido después de normalizar

    def test_should_handle_special_characters(self):
        """
        Test: Debe manejar caracteres especiales en TaxID.

        Algunos formatos incluyen guiones, puntos, etc.
        """
        # Arrange: EIN con formato
        tax_id = TaxID(value="12-3456789", type="EIN")

        # Assert: Debe ser válido (guiones son parte del formato)
        assert tax_id.is_valid()
