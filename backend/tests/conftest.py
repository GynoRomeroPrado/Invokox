"""
==============================================================================
PYTEST CONFIGURATION & FIXTURES
==============================================================================
Configuración global de pytest y fixtures compartidas para todos los tests.

Las fixtures definidas aquí están disponibles en todos los tests sin necesidad
de importarlas explícitamente.

Uso:
    def test_something(sample_invoice):
        # sample_invoice fixture está disponible automáticamente
        assert sample_invoice.total_amount > 0

Fixtures disponibles:
- sample_money: Money instance con valores por defecto
- sample_tax_id_peru: TaxID válido de Perú (RUC)
- sample_tax_id_mexico: TaxID válido de México (RFC)
- sample_company: Company instance con datos completos
- sample_invoice_item: InvoiceItem instance
- sample_invoice: Invoice instance completa con items
==============================================================================
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Generator

import pytest

# Importar clases del dominio que vamos a testear
from src.domain.entities.company import Company
from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_item import InvoiceItem
from src.domain.value_objects.money import Money
from src.domain.value_objects.tax_id import TaxID


# ==============================================================================
# FIXTURES - VALUE OBJECTS
# ==============================================================================


@pytest.fixture
def sample_money() -> Money:
    """
    Fixture que crea un objeto Money con valores por defecto.

    Returns:
        Money: Instancia de Money con 1000.00 PEN

    Uso:
        def test_addition(sample_money):
            result = sample_money + Money(Decimal("500.00"), "PEN")
            assert result.amount == Decimal("1500.00")
    """
    return Money(amount=Decimal("1000.00"), currency="PEN")


@pytest.fixture
def sample_tax_id_peru() -> TaxID:
    """
    Fixture que crea un TaxID válido de Perú (RUC).

    RUC Perú: 11 dígitos numéricos
    Ejemplo: 20123456789

    Returns:
        TaxID: Instancia de TaxID tipo RUC

    Uso:
        def test_peru_tax_id(sample_tax_id_peru):
            assert sample_tax_id_peru.is_valid()
            assert sample_tax_id_peru.type == "RUC"
    """
    return TaxID(value="20123456789", type="RUC")


@pytest.fixture
def sample_tax_id_mexico() -> TaxID:
    """
    Fixture que crea un TaxID válido de México (RFC).

    RFC México: 12-13 caracteres alfanuméricos
    Ejemplo: ABC123456789

    Returns:
        TaxID: Instancia de TaxID tipo RFC

    Uso:
        def test_mexico_tax_id(sample_tax_id_mexico):
            assert sample_tax_id_mexico.is_valid()
            assert sample_tax_id_mexico.type == "RFC"
    """
    return TaxID(value="ABC123456789", type="RFC")


# ==============================================================================
# FIXTURES - ENTITIES
# ==============================================================================


@pytest.fixture
def sample_company() -> Company:
    """
    Fixture que crea una Company con datos completos de ejemplo.

    La empresa creada es un emisor de facturas en Perú con todos
    los campos opcionales completados para facilitar tests.

    Returns:
        Company: Instancia de Company completamente configurada

    Datos creados:
        - tax_id: RUC peruano válido (20123456789)
        - name: Empresa de Pruebas S.A.C.
        - company_type: issuer
        - Información de contacto completa
        - Estado activo

    Uso:
        def test_company_creation(sample_company):
            assert sample_company.name == "Empresa de Pruebas S.A.C."
            assert sample_company.is_active is True
    """
    return Company(
        # Identificación - Campo obligatorio
        tax_id=TaxID(value="20123456789", type="RUC"),
        name="Empresa de Pruebas S.A.C.",
        # Nombre comercial - Campo opcional
        trade_name="Pruebas Corp",
        # Tipo de empresa - Campo obligatorio
        # Valores: 'issuer' (emisor), 'receiver' (receptor), 'both' (ambos)
        company_type="issuer",
        # Información de contacto - Campos opcionales
        address="Av. Principal 123",
        city="Lima",
        state="Lima",
        country="Peru",
        postal_code="15001",
        phone="+51 1 234 5678",
        email="contacto@pruebas.com",
        website="https://www.pruebas.com",
        # Estado - Campo con valor por defecto
        is_active=True,
    )


@pytest.fixture
def sample_invoice_item() -> InvoiceItem:
    """
    Fixture que crea un InvoiceItem (línea de factura) de ejemplo.

    Representa un item típico de factura con:
    - Producto/servicio con código y descripción
    - Cantidad y precio unitario
    - Descuento del 10%
    - IGV/IVA del 18%
    - Cálculos automáticos de montos

    Returns:
        InvoiceItem: Instancia de InvoiceItem con valores calculados

    Cálculos del ejemplo:
        Cantidad: 5 unidades
        Precio unitario: 100.00
        Subtotal: 500.00
        Descuento (10%): 50.00
        Base imponible: 450.00
        IGV (18% de 450): 81.00
        Total: 531.00

    Uso:
        def test_item_calculations(sample_invoice_item):
            assert sample_invoice_item.total == Decimal("531.00")
            assert sample_invoice_item.discount_amount == Decimal("50.00")
    """
    return InvoiceItem(
        # Orden de visualización
        line_number=1,
        # Información del producto/servicio
        code="PROD001",  # Código SKU o identificador
        description="Producto de Prueba",  # Descripción detallada
        unit="UND",  # Unidad de medida (UND, KG, M, etc.)
        # Cantidades y precios
        quantity=Decimal("5.00"),  # 5 unidades
        unit_price=Decimal("100.00"),  # 100.00 por unidad
        # Tasas de descuento e impuesto (en porcentaje)
        discount_rate=Decimal("10.00"),  # 10% de descuento
        tax_rate=Decimal("18.00"),  # 18% IGV/IVA
    )


@pytest.fixture
def sample_invoice(sample_company: Company, sample_invoice_item: InvoiceItem) -> Invoice:
    """
    Fixture que crea una Invoice (factura) completa de ejemplo.

    La factura incluye:
    - Serie y folio válidos
    - Emisor y receptor (usa sample_company para ambos por simplicidad)
    - Un item de factura
    - Montos calculados automáticamente
    - Fecha de emisión y vencimiento

    Args:
        sample_company: Fixture de Company (inyectada automáticamente)
        sample_invoice_item: Fixture de InvoiceItem (inyectada automáticamente)

    Returns:
        Invoice: Instancia de Invoice completa con un item

    Características:
        - Serie: F001-00000001 (formato estándar peruano)
        - Status: PENDING (recién creada)
        - Moneda: PEN (Soles peruanos)
        - Items: 1 item de ejemplo
        - Total calculado automáticamente

    Uso:
        def test_invoice_total(sample_invoice):
            # La factura debe tener el total calculado automáticamente
            assert sample_invoice.total_amount > Decimal("0")
            # Debe tener un item
            assert len(sample_invoice.items) == 1

    Note:
        Esta fixture usa sample_company tanto para issuer como receiver
        por simplicidad. En tests más complejos, crea companies diferentes.
    """
    # Crear la factura básica sin items
    invoice = Invoice(
        # Serie y folio - Identificación única de la factura
        # Formato típico peruano: SERIE-NUMERO (Ej: F001-00000001)
        series="F001-00000001",
        folio_number="00000001",
        # Tipo de factura
        # Valores comunes: 'FACTURA', 'BOLETA', 'NOTA_CREDITO', etc.
        invoice_type="FACTURA",
        # Empresas involucradas
        # issuer: Empresa que emite la factura
        # receiver: Empresa que recibe la factura
        issuer=sample_company,
        receiver=sample_company,  # Usando la misma por simplicidad
        # Fechas
        issue_date=date(2024, 11, 19),  # Fecha de emisión
        due_date=date(2024, 12, 19),  # Fecha de vencimiento (30 días después)
        # Moneda
        # Valores: 'PEN' (Perú), 'USD' (Dólares), 'MXN' (México), etc.
        currency="PEN",
        # Status inicial
        # Valores: 'PENDING', 'PROCESSING', 'COMPLETED', 'APPROVED', 'REJECTED', 'ERROR'
        status="PENDING",
        # Información de procesamiento OCR (opcional)
        file_path="/uploads/test_invoice.pdf",
        ocr_confidence=None,  # Se llena después del OCR
        processing_time=None,  # Se llena después del OCR
        # Usuario que crea la factura
        created_by="test_user",
    )

    # Agregar el item a la factura
    # Esto también recalcula automáticamente los totales
    invoice.add_item(sample_invoice_item)

    return invoice


# ==============================================================================
# FIXTURES - DATABASE & SESSIONS (para integration tests)
# ==============================================================================


@pytest.fixture
def in_memory_db() -> Generator:
    """
    Fixture que crea una base de datos SQLite en memoria para tests.

    Esta fixture es útil para integration tests que necesitan
    interactuar con una base de datos real pero temporal.

    Yields:
        Engine: SQLAlchemy engine conectado a SQLite en memoria

    Lifecycle:
        1. Setup: Crea base de datos en memoria
        2. Crea todas las tablas
        3. Yield: Tests usan la base de datos
        4. Teardown: Limpia y cierra conexiones

    Uso:
        def test_with_database(in_memory_db):
            # Usar in_memory_db para queries
            with Session(in_memory_db) as session:
                # ... operaciones de base de datos
                pass

    Note:
        Esta fixture está preparada pero comentada porque requiere
        SQLModel y las configuraciones de database. Descomentar cuando
        se necesite para integration tests.
    """
    # TODO: Implementar cuando se necesiten integration tests
    # from sqlmodel import SQLModel, create_engine
    # from src.infrastructure.database.config import get_engine
    #
    # engine = create_engine("sqlite:///:memory:")
    # SQLModel.metadata.create_all(engine)
    # yield engine
    # SQLModel.metadata.drop_all(engine)
    # engine.dispose()
    pass


# ==============================================================================
# CONFIGURACIÓN DE PYTEST
# ==============================================================================


def pytest_configure(config):
    """
    Hook de configuración de pytest que se ejecuta antes de los tests.

    Aquí se pueden agregar markers personalizados, configurar plugins,
    o realizar setup global necesario.

    Args:
        config: Objeto de configuración de pytest

    Markers registrados:
        - unit: Tests unitarios (rápidos, sin dependencias externas)
        - integration: Tests de integración (requieren DB, Redis, etc.)
        - slow: Tests lentos (OCR, procesamiento pesado)
        - smoke: Tests de smoke (validación básica del sistema)

    Uso de markers:
        # Ejecutar solo tests unitarios
        pytest -m unit

        # Ejecutar todo excepto tests lentos
        pytest -m "not slow"

        # Ejecutar smoke tests
        pytest -m smoke
    """
    # Registrar markers personalizados
    config.addinivalue_line("markers", "unit: Tests unitarios rápidos sin dependencias externas")
    config.addinivalue_line(
        "markers", "integration: Tests de integración que requieren DB, Redis, etc."
    )
    config.addinivalue_line("markers", "slow: Tests lentos que tardan varios segundos")
    config.addinivalue_line("markers", "smoke: Tests de smoke para validación básica del sistema")


# ==============================================================================
# HELPER FUNCTIONS PARA TESTS
# ==============================================================================


def assert_decimal_equal(actual: Decimal, expected: Decimal, places: int = 2) -> None:
    """
    Helper para comparar Decimals con precisión específica.

    Útil porque las operaciones con Decimal pueden generar más decimales
    de los esperados y queremos comparar solo hasta 2 decimales.

    Args:
        actual: Valor obtenido en el test
        expected: Valor esperado
        places: Número de decimales a comparar (default: 2)

    Raises:
        AssertionError: Si los valores no son iguales hasta N decimales

    Ejemplo:
        assert_decimal_equal(Decimal("10.999"), Decimal("11.00"), places=1)
        # Pass: 11.0 == 11.0 (redondeado a 1 decimal)

        assert_decimal_equal(Decimal("10.123"), Decimal("10.124"), places=2)
        # Pass: 10.12 == 10.12 (redondeado a 2 decimales)
    """
    # Redondear ambos valores al número de decimales especificado
    actual_rounded = round(actual, places)
    expected_rounded = round(expected, places)

    # Comparar valores redondeados
    assert actual_rounded == expected_rounded, (
        f"Decimals not equal: {actual} (rounded to {actual_rounded}) "
        f"!= {expected} (rounded to {expected_rounded})"
    )


def create_test_money(amount: str | float | Decimal, currency: str = "PEN") -> Money:
    """
    Helper para crear Money instances en tests de forma concisa.

    Args:
        amount: Monto (puede ser string, float o Decimal)
        currency: Código de moneda (default: PEN)

    Returns:
        Money: Instancia de Money creada

    Ejemplo:
        money1 = create_test_money("100.50", "USD")
        money2 = create_test_money(100.50, "USD")
        money3 = create_test_money(Decimal("100.50"), "USD")
        # Todos crean el mismo Money object
    """
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return Money(amount=amount, currency=currency)


def create_test_tax_id(value: str, type: str = "RUC") -> TaxID:
    """
    Helper para crear TaxID instances en tests de forma concisa.

    Args:
        value: Valor del tax ID (RUC, RFC, etc.)
        type: Tipo de tax ID (default: RUC)

    Returns:
        TaxID: Instancia de TaxID creada

    Ejemplo:
        ruc = create_test_tax_id("20123456789", "RUC")
        rfc = create_test_tax_id("ABC123456789", "RFC")
    """
    return TaxID(value=value, type=type)
