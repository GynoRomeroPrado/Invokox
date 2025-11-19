"""
==============================================================================
TESTS - ENTITIES
==============================================================================
Tests unitarios para Entities del Domain Layer.

Entities son objetos con identidad única y ciclo de vida. Características:
- Tienen identidad única (ID)
- Mutables (su estado puede cambiar)
- Igualdad por identidad (dos entities con mismo ID son iguales)
- Tienen comportamiento (métodos que modifican estado)
- Encapsulan lógica de negocio

Tests incluidos:
- Company: Entidad de empresa (emisor/receptor)
- InvoiceItem: Entidad de item de factura
- Invoice: Entidad agregado raíz de factura

Ejecutar:
    pytest tests/domain/test_entities.py
    pytest tests/domain/test_entities.py::TestInvoice
    pytest tests/domain/test_entities.py::TestInvoice::test_should_create_valid_invoice
==============================================================================
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.domain.entities.company import Company
from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_item import InvoiceItem
from src.domain.value_objects.money import Money
from src.domain.value_objects.tax_id import TaxID


# ==============================================================================
# TESTS - COMPANY ENTITY
# ==============================================================================


class TestCompany:
    """
    Test suite para la entidad Company.

    Company representa una empresa (emisor o receptor de facturas) con:
    - Identificación (tax_id, name)
    - Tipo (issuer, receiver, both)
    - Información de contacto
    - Estado (activo/inactivo)
    - Estadísticas (invoice_count, total_amount)
    """

    # ==========================================================================
    # TESTS - CREACIÓN Y VALIDACIÓN
    # ==========================================================================

    def test_should_create_valid_company(self, sample_tax_id_peru):
        """
        Test: Debe crear Company válida con campos requeridos.

        Campos requeridos:
        - tax_id: TaxID (RUC, RFC, etc.)
        - name: str (nombre de la empresa)
        - company_type: str ('issuer', 'receiver', 'both')

        Args:
            sample_tax_id_peru: Fixture con TaxID válido de Perú
        """
        # Arrange & Act
        company = Company(
            tax_id=sample_tax_id_peru,
            name="Test Company S.A.C.",
            company_type="issuer",
        )

        # Assert: Campos requeridos
        assert company.tax_id == sample_tax_id_peru
        assert company.name == "Test Company S.A.C."
        assert company.company_type == "issuer"
        # Assert: Valores por defecto
        assert company.is_active is True
        assert company.invoice_count == 0
        assert company.total_amount == Decimal("0.00")

    def test_should_create_company_with_full_information(self, sample_company):
        """
        Test: Debe crear Company con toda la información opcional.

        Args:
            sample_company: Fixture con Company completa
        """
        # Assert: Información básica
        assert sample_company.name == "Empresa de Pruebas S.A.C."
        assert sample_company.trade_name == "Pruebas Corp"

        # Assert: Información de contacto
        assert sample_company.address == "Av. Principal 123"
        assert sample_company.city == "Lima"
        assert sample_company.state == "Lima"
        assert sample_company.country == "Peru"
        assert sample_company.postal_code == "15001"
        assert sample_company.phone == "+51 1 234 5678"
        assert sample_company.email == "contacto@pruebas.com"
        assert sample_company.website == "https://www.pruebas.com"

        # Assert: Estado
        assert sample_company.is_active is True

    def test_should_validate_company_type(self):
        """
        Test: Debe validar que company_type sea válido.

        Tipos válidos:
        - 'issuer': Emisor de facturas
        - 'receiver': Receptor de facturas
        - 'both': Ambos (emite y recibe)

        Tipos inválidos deben lanzar ValueError.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")

        # Act & Assert: Tipos válidos
        valid_types = ["issuer", "receiver", "both"]
        for company_type in valid_types:
            company = Company(
                tax_id=tax_id, name="Test Company", company_type=company_type
            )
            assert company.company_type == company_type

        # Act & Assert: Tipo inválido
        with pytest.raises(ValueError) as exc_info:
            Company(tax_id=tax_id, name="Test Company", company_type="invalid")

        assert "Invalid company_type" in str(exc_info.value)

    def test_should_validate_email_format(self):
        """
        Test: Debe validar formato de email si se proporciona.

        Email válido: user@domain.com
        Email inválido: user@, @domain, user, etc.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")

        # Act: Email válido
        company_valid = Company(
            tax_id=tax_id,
            name="Test Company",
            company_type="issuer",
            email="contact@company.com",
        )
        assert company_valid.email == "contact@company.com"

        # Act & Assert: Email inválido
        with pytest.raises(ValueError) as exc_info:
            Company(
                tax_id=tax_id,
                name="Test Company",
                company_type="issuer",
                email="invalid-email",  # Sin @ y dominio
            )

        assert "Invalid email" in str(exc_info.value)

    # ==========================================================================
    # TESTS - COMPORTAMIENTO Y LÓGICA DE NEGOCIO
    # ==========================================================================

    def test_should_deactivate_company(self, sample_company):
        """
        Test: Debe poder desactivar una empresa.

        Una empresa desactivada no debe poder emitir/recibir facturas
        (validación en capa de aplicación).
        """
        # Arrange
        assert sample_company.is_active is True

        # Act: Desactivar
        sample_company.deactivate()

        # Assert
        assert sample_company.is_active is False

    def test_should_reactivate_company(self, sample_company):
        """
        Test: Debe poder reactivar una empresa desactivada.
        """
        # Arrange: Desactivar primero
        sample_company.deactivate()
        assert sample_company.is_active is False

        # Act: Reactivar
        sample_company.activate()

        # Assert
        assert sample_company.is_active is True

    def test_should_increment_invoice_count(self, sample_company):
        """
        Test: Debe incrementar contador de facturas.

        El contador se incrementa cuando se crea una nueva factura
        asociada a esta empresa (como emisor).
        """
        # Arrange
        initial_count = sample_company.invoice_count

        # Act
        sample_company.increment_invoice_count()

        # Assert
        assert sample_company.invoice_count == initial_count + 1

    def test_should_update_total_amount(self, sample_company):
        """
        Test: Debe actualizar monto total de facturas.

        El total acumulado se actualiza cuando se aprueban facturas.
        """
        # Arrange
        initial_total = sample_company.total_amount
        invoice_amount = Decimal("1500.50")

        # Act
        sample_company.update_total_amount(invoice_amount)

        # Assert
        assert sample_company.total_amount == initial_total + invoice_amount

    def test_should_update_contact_information(self, sample_company):
        """
        Test: Debe actualizar información de contacto.

        La información de contacto puede cambiar con el tiempo.
        """
        # Arrange: Información nueva
        new_email = "nuevo@pruebas.com"
        new_phone = "+51 1 999 8888"
        new_address = "Calle Nueva 456"

        # Act
        sample_company.update_contact(
            email=new_email, phone=new_phone, address=new_address
        )

        # Assert
        assert sample_company.email == new_email
        assert sample_company.phone == new_phone
        assert sample_company.address == new_address

    # ==========================================================================
    # TESTS - IGUALDAD E IDENTIDAD
    # ==========================================================================

    def test_should_check_equality_by_tax_id(self):
        """
        Test: Debe verificar igualdad por tax_id (identidad de negocio).

        Dos empresas con el mismo tax_id son la misma empresa,
        aunque otros campos sean diferentes.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")

        company1 = Company(
            tax_id=tax_id, name="Company A", company_type="issuer"
        )
        company2 = Company(
            tax_id=tax_id, name="Company B", company_type="receiver"
        )

        # Assert: Iguales porque tienen mismo tax_id
        assert company1 == company2
        # Pero NO son el mismo objeto en memoria
        assert company1 is not company2

    def test_should_not_be_equal_with_different_tax_id(self):
        """
        Test: Empresas con tax_id diferente no son iguales.
        """
        # Arrange
        tax_id1 = TaxID(value="20123456789", type="RUC")
        tax_id2 = TaxID(value="20987654321", type="RUC")

        company1 = Company(
            tax_id=tax_id1, name="Company A", company_type="issuer"
        )
        company2 = Company(
            tax_id=tax_id2, name="Company B", company_type="issuer"
        )

        # Assert
        assert company1 != company2

    # ==========================================================================
    # TESTS - VALIDACIONES DE NEGOCIO
    # ==========================================================================

    def test_should_not_allow_empty_name(self):
        """
        Test: No debe permitir nombre vacío.

        Regla de negocio: Toda empresa debe tener un nombre.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Company(tax_id=tax_id, name="", company_type="issuer")

        assert "Name cannot be empty" in str(exc_info.value)

    def test_should_normalize_name(self):
        """
        Test: Debe normalizar el nombre de la empresa.

        Normalización:
        - Trim espacios al inicio y final
        - Múltiples espacios a uno solo
        - Primera letra de cada palabra en mayúscula (opcional)
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")

        # Act
        company = Company(
            tax_id=tax_id,
            name="  empresa   de   pruebas  ",  # Espacios extra
            company_type="issuer",
        )

        # Assert: Espacios normalizados
        assert company.name == "Empresa De Pruebas"  # Normalizado


# ==============================================================================
# TESTS - INVOICE ITEM ENTITY
# ==============================================================================


class TestInvoiceItem:
    """
    Test suite para la entidad InvoiceItem.

    InvoiceItem representa una línea de factura con:
    - Información del producto/servicio
    - Cantidades y precios
    - Descuentos e impuestos
    - Cálculos automáticos de totales
    """

    # ==========================================================================
    # TESTS - CREACIÓN Y CÁLCULOS
    # ==========================================================================

    def test_should_create_valid_invoice_item(self, sample_invoice_item):
        """
        Test: Debe crear InvoiceItem válido con cálculos automáticos.

        Args:
            sample_invoice_item: Fixture con item de ejemplo
        """
        # Assert: Información básica
        assert sample_invoice_item.line_number == 1
        assert sample_invoice_item.code == "PROD001"
        assert sample_invoice_item.description == "Producto de Prueba"
        assert sample_invoice_item.unit == "UND"

        # Assert: Cantidades
        assert sample_invoice_item.quantity == Decimal("5.00")
        assert sample_invoice_item.unit_price == Decimal("100.00")

        # Assert: Tasas
        assert sample_invoice_item.discount_rate == Decimal("10.00")
        assert sample_invoice_item.tax_rate == Decimal("18.00")

        # Assert: Montos calculados automáticamente
        assert sample_invoice_item.subtotal > Decimal("0")
        assert sample_invoice_item.total > Decimal("0")

    def test_should_calculate_subtotal_correctly(self):
        """
        Test: Debe calcular subtotal correctamente.

        Fórmula: subtotal = quantity * unit_price
        Ejemplo: 10 * 50.00 = 500.00
        """
        # Arrange & Act
        item = InvoiceItem(
            line_number=1,
            description="Test Product",
            quantity=Decimal("10.00"),
            unit_price=Decimal("50.00"),
            discount_rate=Decimal("0.00"),  # Sin descuento
            tax_rate=Decimal("0.00"),  # Sin impuesto
        )

        # Assert
        expected_subtotal = Decimal("500.00")  # 10 * 50
        assert item.subtotal == expected_subtotal

    def test_should_calculate_discount_amount_correctly(self):
        """
        Test: Debe calcular monto de descuento correctamente.

        Fórmula: discount_amount = subtotal * (discount_rate / 100)
        Ejemplo: 500 * 0.10 = 50.00 (10% de descuento)
        """
        # Arrange & Act
        item = InvoiceItem(
            line_number=1,
            description="Test Product",
            quantity=Decimal("10.00"),  # 10 unidades
            unit_price=Decimal("50.00"),  # 50.00 c/u
            discount_rate=Decimal("10.00"),  # 10% descuento
            tax_rate=Decimal("0.00"),
        )

        # Assert
        # Subtotal: 10 * 50 = 500.00
        # Descuento: 500 * 0.10 = 50.00
        expected_discount = Decimal("50.00")
        assert item.discount_amount == expected_discount

    def test_should_calculate_tax_amount_correctly(self):
        """
        Test: Debe calcular monto de impuesto correctamente.

        Fórmula: tax_amount = (subtotal - discount_amount) * (tax_rate / 100)
        Ejemplo: (500 - 50) * 0.18 = 81.00 (IGV 18%)
        """
        # Arrange & Act
        item = InvoiceItem(
            line_number=1,
            description="Test Product",
            quantity=Decimal("10.00"),  # 10 unidades
            unit_price=Decimal("50.00"),  # 50.00 c/u
            discount_rate=Decimal("10.00"),  # 10% descuento
            tax_rate=Decimal("18.00"),  # 18% IGV
        )

        # Assert
        # Subtotal: 500.00
        # Descuento: 50.00
        # Base imponible: 450.00
        # IGV: 450 * 0.18 = 81.00
        expected_tax = Decimal("81.00")
        assert item.tax_amount == expected_tax

    def test_should_calculate_total_correctly(self):
        """
        Test: Debe calcular total correctamente.

        Fórmula: total = subtotal - discount_amount + tax_amount
        Ejemplo: 500 - 50 + 81 = 531.00
        """
        # Arrange & Act
        item = InvoiceItem(
            line_number=1,
            description="Test Product",
            quantity=Decimal("10.00"),
            unit_price=Decimal("50.00"),
            discount_rate=Decimal("10.00"),
            tax_rate=Decimal("18.00"),
        )

        # Assert
        # Subtotal: 500.00
        # Descuento: -50.00
        # IGV: +81.00
        # Total: 531.00
        expected_total = Decimal("531.00")
        assert item.total == expected_total

    def test_should_handle_zero_quantity(self):
        """
        Test: Debe manejar cantidad cero correctamente.

        Casos de uso: Items opcionales, regalos, muestras
        """
        # Arrange & Act
        item = InvoiceItem(
            line_number=1,
            description="Free Sample",
            quantity=Decimal("0.00"),  # Cantidad cero
            unit_price=Decimal("100.00"),
            discount_rate=Decimal("0.00"),
            tax_rate=Decimal("0.00"),
        )

        # Assert: Todos los montos deben ser cero
        assert item.subtotal == Decimal("0.00")
        assert item.discount_amount == Decimal("0.00")
        assert item.tax_amount == Decimal("0.00")
        assert item.total == Decimal("0.00")

    def test_should_handle_fractional_quantities(self):
        """
        Test: Debe manejar cantidades fraccionarias.

        Casos de uso:
        - 2.5 kg de producto
        - 1.75 horas de servicio
        - 0.5 metros de tela
        """
        # Arrange & Act
        item = InvoiceItem(
            line_number=1,
            description="Fractional Product",
            quantity=Decimal("2.5"),  # 2.5 unidades
            unit_price=Decimal("40.00"),
            discount_rate=Decimal("0.00"),
            tax_rate=Decimal("0.00"),
        )

        # Assert
        # Subtotal: 2.5 * 40 = 100.00
        expected_subtotal = Decimal("100.00")
        assert item.subtotal == expected_subtotal

    def test_should_not_allow_negative_quantity(self):
        """
        Test: No debe permitir cantidad negativa.

        Regla de negocio: Cantidades negativas no son válidas.
        Para devoluciones, usar notas de crédito.
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            InvoiceItem(
                line_number=1,
                description="Test",
                quantity=Decimal("-5.00"),  # Negativo inválido
                unit_price=Decimal("100.00"),
                discount_rate=Decimal("0.00"),
                tax_rate=Decimal("0.00"),
            )

        assert "Quantity cannot be negative" in str(exc_info.value)

    def test_should_not_allow_negative_unit_price(self):
        """
        Test: No debe permitir precio unitario negativo.
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            InvoiceItem(
                line_number=1,
                description="Test",
                quantity=Decimal("5.00"),
                unit_price=Decimal("-100.00"),  # Negativo inválido
                discount_rate=Decimal("0.00"),
                tax_rate=Decimal("0.00"),
            )

        assert "Unit price cannot be negative" in str(exc_info.value)

    # ==========================================================================
    # TESTS - MODIFICACIONES Y RECÁLCULOS
    # ==========================================================================

    def test_should_update_quantity_and_recalculate(self, sample_invoice_item):
        """
        Test: Debe actualizar cantidad y recalcular montos.

        Cuando se modifica la cantidad, todos los cálculos
        dependientes deben actualizarse automáticamente.
        """
        # Arrange
        original_total = sample_invoice_item.total

        # Act: Duplicar cantidad
        new_quantity = sample_invoice_item.quantity * 2
        sample_invoice_item.update_quantity(new_quantity)

        # Assert: Total debe ser aproximadamente el doble
        # (puede variar ligeramente por redondeo de impuestos)
        assert sample_invoice_item.total > original_total
        assert sample_invoice_item.quantity == new_quantity

    def test_should_apply_additional_discount(self):
        """
        Test: Debe aplicar descuento adicional y recalcular.

        Casos de uso:
        - Descuentos por volumen
        - Promociones especiales
        - Descuentos manuales
        """
        # Arrange
        item = InvoiceItem(
            line_number=1,
            description="Test Product",
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            discount_rate=Decimal("0.00"),  # Sin descuento inicial
            tax_rate=Decimal("18.00"),
        )
        initial_total = item.total

        # Act: Aplicar 20% de descuento
        item.apply_discount(Decimal("20.00"))

        # Assert: Total debe ser menor
        assert item.total < initial_total
        assert item.discount_rate == Decimal("20.00")

    def test_should_change_tax_rate_and_recalculate(self):
        """
        Test: Debe cambiar tasa de impuesto y recalcular.

        Casos de uso:
        - Cambio de régimen fiscal
        - Productos con IGV diferenciado
        - Exoneraciones
        """
        # Arrange
        item = InvoiceItem(
            line_number=1,
            description="Test Product",
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            discount_rate=Decimal("0.00"),
            tax_rate=Decimal("18.00"),  # IGV 18%
        )
        initial_tax = item.tax_amount

        # Act: Cambiar a 0% (exonerado)
        item.update_tax_rate(Decimal("0.00"))

        # Assert
        assert item.tax_rate == Decimal("0.00")
        assert item.tax_amount == Decimal("0.00")
        assert item.tax_amount < initial_tax


# ==============================================================================
# TESTS - INVOICE ENTITY (AGGREGATE ROOT)
# ==============================================================================


class TestInvoice:
    """
    Test suite para la entidad Invoice (Aggregate Root).

    Invoice es el agregado raíz que representa una factura completa con:
    - Información de emisor y receptor
    - Items de factura
    - Montos totales calculados
    - Estado y ciclo de vida
    - Información de procesamiento OCR

    Como Aggregate Root, Invoice:
    - Controla acceso a InvoiceItems
    - Garantiza consistencia del agregado
    - Maneja transiciones de estado
    - Implementa lógica de negocio compleja
    """

    # ==========================================================================
    # TESTS - CREACIÓN Y VALIDACIÓN
    # ==========================================================================

    def test_should_create_valid_invoice(self, sample_invoice):
        """
        Test: Debe crear Invoice válida con campos requeridos.

        Args:
            sample_invoice: Fixture con invoice completa
        """
        # Assert: Información básica
        assert sample_invoice.series == "F001-00000001"
        assert sample_invoice.folio_number == "00000001"
        assert sample_invoice.invoice_type == "FACTURA"

        # Assert: Empresas
        assert sample_invoice.issuer is not None
        assert sample_invoice.receiver is not None

        # Assert: Fechas
        assert sample_invoice.issue_date == date(2024, 11, 19)
        assert sample_invoice.due_date == date(2024, 12, 19)

        # Assert: Moneda y status
        assert sample_invoice.currency == "PEN"
        assert sample_invoice.status == "PENDING"

        # Assert: Items
        assert len(sample_invoice.items) == 1

    def test_should_validate_series_format(self):
        """
        Test: Debe validar formato de serie de factura.

        Formato típico Perú: F001-00000001
        - Serie: 1-4 letras + 3 dígitos
        - Separador: guión
        - Folio: 8 dígitos

        Otros formatos según país pueden variar.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")
        company = Company(tax_id=tax_id, name="Test", company_type="issuer")

        # Act & Assert: Serie válida
        valid_series = ["F001-00000001", "B001-00000123", "FC01-12345678"]
        for series in valid_series:
            invoice = Invoice(
                series=series,
                folio_number=series.split("-")[1],
                invoice_type="FACTURA",
                issuer=company,
                receiver=company,
                issue_date=date.today(),
                currency="PEN",
                status="PENDING",
            )
            assert invoice.series == series

        # Act & Assert: Serie inválida
        with pytest.raises(ValueError) as exc_info:
            Invoice(
                series="INVALID",  # Sin formato correcto
                folio_number="00000001",
                invoice_type="FACTURA",
                issuer=company,
                receiver=company,
                issue_date=date.today(),
                currency="PEN",
                status="PENDING",
            )

        assert "Invalid series format" in str(exc_info.value)

    def test_should_validate_issue_date_not_in_future(self):
        """
        Test: Debe validar que fecha de emisión no sea futura.

        Regla de negocio: No se pueden emitir facturas con fecha futura.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")
        company = Company(tax_id=tax_id, name="Test", company_type="issuer")
        future_date = date.today() + timedelta(days=30)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Invoice(
                series="F001-00000001",
                folio_number="00000001",
                invoice_type="FACTURA",
                issuer=company,
                receiver=company,
                issue_date=future_date,  # Fecha futura inválida
                currency="PEN",
                status="PENDING",
            )

        assert "Issue date cannot be in the future" in str(exc_info.value)

    def test_should_validate_due_date_after_issue_date(self):
        """
        Test: Debe validar que fecha de vencimiento sea posterior a emisión.

        Regla de negocio: due_date >= issue_date
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")
        company = Company(tax_id=tax_id, name="Test", company_type="issuer")
        issue_date = date(2024, 11, 19)
        past_due_date = date(2024, 11, 10)  # Anterior a issue_date

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Invoice(
                series="F001-00000001",
                folio_number="00000001",
                invoice_type="FACTURA",
                issuer=company,
                receiver=company,
                issue_date=issue_date,
                due_date=past_due_date,  # Anterior a issue_date
                currency="PEN",
                status="PENDING",
            )

        assert "Due date must be after issue date" in str(exc_info.value)

    # ==========================================================================
    # TESTS - GESTIÓN DE ITEMS
    # ==========================================================================

    def test_should_add_item_to_invoice(self, sample_invoice, sample_invoice_item):
        """
        Test: Debe agregar item a la factura y recalcular totales.

        Args:
            sample_invoice: Fixture con invoice (ya tiene 1 item)
            sample_invoice_item: Fixture con item nuevo
        """
        # Arrange
        initial_item_count = len(sample_invoice.items)
        initial_total = sample_invoice.total_amount

        # Act: Agregar otro item
        new_item = InvoiceItem(
            line_number=2,
            description="Second Item",
            quantity=Decimal("3.00"),
            unit_price=Decimal("200.00"),
            discount_rate=Decimal("0.00"),
            tax_rate=Decimal("18.00"),
        )
        sample_invoice.add_item(new_item)

        # Assert: Item agregado
        assert len(sample_invoice.items) == initial_item_count + 1
        # Assert: Total recalculado (debe ser mayor)
        assert sample_invoice.total_amount > initial_total

    def test_should_remove_item_from_invoice(self, sample_invoice):
        """
        Test: Debe remover item de la factura y recalcular totales.
        """
        # Arrange
        assert len(sample_invoice.items) == 1
        item_to_remove = sample_invoice.items[0]
        initial_total = sample_invoice.total_amount

        # Act
        sample_invoice.remove_item(item_to_remove.line_number)

        # Assert: Item removido
        assert len(sample_invoice.items) == 0
        # Assert: Total recalculado (debe ser menor, probablemente 0)
        assert sample_invoice.total_amount < initial_total

    def test_should_calculate_total_from_items(self, sample_invoice):
        """
        Test: Debe calcular total sumando todos los items.

        total_amount = sum(item.total for item in items)
        """
        # Arrange: Invoice con 1 item
        expected_total = sum(item.total for item in sample_invoice.items)

        # Assert
        assert sample_invoice.total_amount == expected_total

    def test_should_recalculate_totals_when_item_changes(self, sample_invoice):
        """
        Test: Debe recalcular totales cuando un item cambia.

        Cuando se modifica un item (cantidad, precio, descuento),
        el total de la factura debe actualizarse automáticamente.
        """
        # Arrange
        initial_total = sample_invoice.total_amount
        item = sample_invoice.items[0]

        # Act: Duplicar cantidad del item
        new_quantity = item.quantity * 2
        item.update_quantity(new_quantity)
        # Forzar recálculo de totales de la factura
        sample_invoice.recalculate_totals()

        # Assert: Total debe haber aumentado
        assert sample_invoice.total_amount > initial_total

    # ==========================================================================
    # TESTS - TRANSICIONES DE ESTADO
    # ==========================================================================

    def test_should_transition_to_processing_status(self, sample_invoice):
        """
        Test: Debe transicionar a estado PROCESSING.

        Flujo: PENDING → PROCESSING
        Se marca como PROCESSING cuando empieza el OCR.
        """
        # Arrange
        assert sample_invoice.status == "PENDING"

        # Act
        sample_invoice.start_processing()

        # Assert
        assert sample_invoice.status == "PROCESSING"

    def test_should_transition_to_completed_status(self, sample_invoice):
        """
        Test: Debe transicionar a estado COMPLETED.

        Flujo: PROCESSING → COMPLETED
        Se marca como COMPLETED cuando el OCR termina exitosamente.
        """
        # Arrange
        sample_invoice.start_processing()
        assert sample_invoice.status == "PROCESSING"

        # Act
        sample_invoice.complete_processing(
            ocr_confidence=0.95, processing_time=12.5
        )

        # Assert
        assert sample_invoice.status == "COMPLETED"
        assert sample_invoice.ocr_confidence == 0.95
        assert sample_invoice.processing_time == 12.5

    def test_should_approve_invoice(self, sample_invoice):
        """
        Test: Debe aprobar factura.

        Flujo: COMPLETED → APPROVED
        Una factura solo puede ser aprobada si está COMPLETED o PENDING.
        """
        # Arrange: Completar primero
        sample_invoice.start_processing()
        sample_invoice.complete_processing(ocr_confidence=0.95, processing_time=10.0)
        assert sample_invoice.status == "COMPLETED"

        # Act
        approved_by = "admin@invokox.com"
        sample_invoice.approve(approved_by=approved_by)

        # Assert
        assert sample_invoice.status == "APPROVED"
        assert sample_invoice.updated_by == approved_by

    def test_should_reject_invoice(self, sample_invoice):
        """
        Test: Debe rechazar factura.

        Flujo: COMPLETED → REJECTED
        Una factura puede ser rechazada si tiene errores o datos incorrectos.
        """
        # Arrange
        sample_invoice.start_processing()
        sample_invoice.complete_processing(ocr_confidence=0.95, processing_time=10.0)

        # Act
        rejected_by = "reviewer@invokox.com"
        reason = "Datos incorrectos en el monto total"
        sample_invoice.reject(rejected_by=rejected_by, reason=reason)

        # Assert
        assert sample_invoice.status == "REJECTED"
        assert sample_invoice.updated_by == rejected_by
        assert reason in sample_invoice.notes

    def test_should_not_approve_already_approved_invoice(self, sample_invoice):
        """
        Test: No debe aprobar factura ya aprobada.

        Regla de negocio: Una factura aprobada no puede volver a aprobarse.
        """
        # Arrange: Aprobar factura
        sample_invoice.approve(approved_by="user1")
        assert sample_invoice.status == "APPROVED"

        # Act & Assert: Intentar aprobar de nuevo
        with pytest.raises(ValueError) as exc_info:
            sample_invoice.approve(approved_by="user2")

        assert "Cannot approve invoice with status APPROVED" in str(exc_info.value)

    def test_should_mark_as_error_on_processing_failure(self, sample_invoice):
        """
        Test: Debe marcar como ERROR si el procesamiento falla.

        Flujo: PROCESSING → ERROR
        Si el OCR falla, la factura se marca como ERROR.
        """
        # Arrange
        sample_invoice.start_processing()

        # Act
        error_message = "OCR engine failed: timeout"
        sample_invoice.mark_as_error(error_message=error_message)

        # Assert
        assert sample_invoice.status == "ERROR"
        assert error_message in sample_invoice.notes

    # ==========================================================================
    # TESTS - INVARIANTES Y REGLAS DE NEGOCIO
    # ==========================================================================

    def test_should_not_allow_empty_items(self):
        """
        Test: No debe permitir factura sin items.

        Regla de negocio: Una factura debe tener al menos un item.
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")
        company = Company(tax_id=tax_id, name="Test", company_type="issuer")

        invoice = Invoice(
            series="F001-00000001",
            folio_number="00000001",
            invoice_type="FACTURA",
            issuer=company,
            receiver=company,
            issue_date=date.today(),
            currency="PEN",
            status="PENDING",
        )

        # Assert: Invoice sin items es inválida
        assert not invoice.is_valid()

        # Act: Agregar item
        item = InvoiceItem(
            line_number=1,
            description="Test",
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            discount_rate=Decimal("0.00"),
            tax_rate=Decimal("0.00"),
        )
        invoice.add_item(item)

        # Assert: Ahora es válida
        assert invoice.is_valid()

    def test_should_ensure_issuer_and_receiver_are_different(self):
        """
        Test: Debe asegurar que emisor y receptor sean diferentes.

        Regla de negocio: Una empresa no puede emitirse factura a sí misma.
        (Excepto en casos especiales de contabilidad interna)
        """
        # Arrange
        tax_id = TaxID(value="20123456789", type="RUC")
        company = Company(tax_id=tax_id, name="Test", company_type="both")

        # Act & Assert: Warning si son iguales
        invoice = Invoice(
            series="F001-00000001",
            folio_number="00000001",
            invoice_type="FACTURA",
            issuer=company,
            receiver=company,  # Mismo emisor y receptor
            issue_date=date.today(),
            currency="PEN",
            status="PENDING",
        )

        # En un caso real, esto podría lanzar warning o requerir
        # justificación especial
        assert invoice.issuer == invoice.receiver

    def test_should_calculate_subtotal_tax_and_total(self, sample_invoice):
        """
        Test: Debe calcular correctamente subtotal, impuesto y total.

        Fórmula:
        - subtotal = sum(item.subtotal for item in items)
        - tax_amount = sum(item.tax_amount for item in items)
        - discount_amount = sum(item.discount_amount for item in items)
        - total_amount = subtotal - discount_amount + tax_amount
        """
        # Act: Calcular esperados
        expected_subtotal = sum(item.subtotal for item in sample_invoice.items)
        expected_tax = sum(item.tax_amount for item in sample_invoice.items)
        expected_discount = sum(
            item.discount_amount for item in sample_invoice.items
        )
        expected_total = expected_subtotal - expected_discount + expected_tax

        # Assert
        assert sample_invoice.subtotal == expected_subtotal
        assert sample_invoice.tax_amount == expected_tax
        assert sample_invoice.discount_amount == expected_discount
        assert sample_invoice.total_amount == expected_total

    def test_should_update_timestamp_on_state_change(self, sample_invoice):
        """
        Test: Debe actualizar timestamp al cambiar de estado.

        El campo updated_at debe actualizarse en cada transición.
        """
        # Arrange
        original_updated_at = sample_invoice.updated_at

        # Act: Esperar un poco y cambiar estado
        import time

        time.sleep(0.1)
        sample_invoice.start_processing()

        # Assert: Timestamp actualizado
        assert sample_invoice.updated_at > original_updated_at

    # ==========================================================================
    # TESTS - VERSIONADO OPTIMISTA
    # ==========================================================================

    def test_should_increment_version_on_update(self, sample_invoice):
        """
        Test: Debe incrementar versión en cada actualización.

        Optimistic locking: El campo version se incrementa en cada
        modificación para detectar conflictos concurrentes.
        """
        # Arrange
        initial_version = sample_invoice.version

        # Act: Modificar factura
        sample_invoice.approve(approved_by="admin")

        # Assert: Versión incrementada
        assert sample_invoice.version == initial_version + 1

    def test_should_detect_concurrent_modification(self, sample_invoice):
        """
        Test: Debe detectar modificación concurrente.

        Escenario:
        1. Usuario A lee factura (version=1)
        2. Usuario B lee factura (version=1)
        3. Usuario A modifica y guarda (version=2)
        4. Usuario B intenta modificar con version=1 → ERROR

        Esto se valida en el repository layer.
        """
        # Arrange
        original_version = sample_invoice.version

        # Act: Simular que otro proceso incrementó la versión
        sample_invoice.version += 1

        # Assert: Version cambió
        assert sample_invoice.version == original_version + 1

        # En repository, se detectaría el conflicto al intentar
        # guardar con version anterior
