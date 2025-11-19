# 🧪 Tests - Invokox v2.0

Suite completa de tests unitarios e integración para Invokox.

## 📋 Tabla de Contenidos

- [Overview](#overview)
- [Estructura](#estructura)
- [Ejecutar Tests](#ejecutar-tests)
- [Escribir Tests](#escribir-tests)
- [Coverage](#coverage)
- [CI/CD](#cicd)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

### Tipos de Tests

1. **Tests Unitarios** (`@pytest.mark.unit`)
   - Testean componentes individuales aislados
   - No dependen de DB, Redis, u otros servicios externos
   - Muy rápidos (< 1 segundo)
   - Domain Layer: Value Objects, Entities

2. **Tests de Integración** (`@pytest.mark.integration`)
   - Testean interacción entre componentes
   - Requieren servicios externos (DB, Redis)
   - Más lentos (< 10 segundos)
   - Repository Layer, API Layer

3. **Tests E2E** (End-to-End)
   - Testean flujos completos
   - Requieren todo el stack corriendo
   - Lentos (> 10 segundos)
   - Workflows completos de negocio

### Estadísticas Actuales

```
Tests Unitarios:     50+ tests
Coverage:            80%+ (objetivo: 90%)
Tiempo ejecución:    < 5 segundos
```

## 📁 Estructura

```
tests/
├── __init__.py                  # Documentación del package
├── conftest.py                  # Fixtures globales y configuración
├── README.md                    # Esta guía
│
├── domain/                      # Tests del Domain Layer
│   ├── __init__.py
│   ├── test_value_objects.py   # Tests de Money, TaxID
│   └── test_entities.py        # Tests de Invoice, Company, InvoiceItem
│
├── application/                 # Tests del Application Layer
│   ├── __init__.py
│   ├── test_use_cases.py       # Tests de Use Cases
│   └── test_interfaces.py      # Tests de interfaces
│
├── infrastructure/              # Tests del Infrastructure Layer
│   ├── __init__.py
│   ├── test_repositories.py    # Tests de repositories
│   └── test_database.py        # Tests de database config
│
└── presentation/                # Tests del Presentation Layer
    ├── __init__.py
    ├── test_api_health.py      # Tests de health endpoints
    ├── test_api_invoices.py    # Tests de invoice endpoints
    └── test_api_companies.py   # Tests de company endpoints
```

## 🚀 Ejecutar Tests

### Comandos Básicos

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con output verbose
pytest -v

# Ejecutar con output muy detallado
pytest -vv

# Ejecutar mostrando print statements
pytest -s

# Ejecutar y mostrar duración de cada test
pytest --durations=10
```

### Por Categoría

```bash
# Solo tests unitarios (rápidos)
pytest -m unit

# Solo tests de integración
pytest -m integration

# Todos excepto tests lentos
pytest -m "not slow"

# Tests que requieren DB
pytest -m requires_db

# Combinar markers
pytest -m "unit and not slow"
```

### Por Archivo o Test Específico

```bash
# Ejecutar archivo específico
pytest tests/domain/test_value_objects.py

# Ejecutar clase específica
pytest tests/domain/test_value_objects.py::TestMoney

# Ejecutar test específico
pytest tests/domain/test_value_objects.py::TestMoney::test_should_create_valid_money

# Ejecutar usando keyword (-k)
pytest -k "money"  # Todos los tests con "money" en el nombre
pytest -k "test_should_create"  # Todos con "test_should_create"
```

### Con Docker

```bash
# Ejecutar tests en contenedor
docker-compose exec backend pytest

# Con coverage
docker-compose exec backend pytest --cov=src --cov-report=html

# Solo unitarios
docker-compose exec backend pytest -m unit
```

### Opciones Útiles

```bash
# Stopear en primer fallo
pytest -x

# Stopear después de N fallos
pytest --maxfail=3

# Ejecutar solo tests que fallaron la última vez
pytest --lf

# Ejecutar tests en orden aleatorio
pytest --random-order

# Modo debug (stopea en fallo con pdb)
pytest --pdb

# Parallel execution (requiere pytest-xdist)
pytest -n auto  # Usar todas las CPUs
pytest -n 4     # Usar 4 workers
```

## ✍️ Escribir Tests

### Convenciones

1. **Nombres descriptivos**: `test_should_do_something_when_condition`
2. **Arrange-Act-Assert**: Organizar código en 3 secciones
3. **Un assert por concepto**: Varios asserts OK si testean lo mismo
4. **Fixtures para setup**: Usar fixtures en lugar de setup/teardown
5. **Markers apropiados**: Marcar tests con @pytest.mark.unit, etc.

### Plantilla de Test

```python
@pytest.mark.unit
def test_should_calculate_total_correctly(self):
    """
    Test: Debe calcular el total correctamente.

    Verifica que la suma de subtotal + tax - discount
    resulta en el total esperado.
    """
    # Arrange: Preparar datos de prueba
    invoice = create_test_invoice(
        subtotal=Decimal("100.00"),
        tax_rate=Decimal("18.00"),
        discount=Decimal("10.00")
    )

    # Act: Ejecutar acción a testear
    result = invoice.calculate_total()

    # Assert: Verificar resultado
    expected = Decimal("108.00")  # 100 - 10 + 18
    assert result == expected
```

### Usar Fixtures

```python
def test_with_sample_invoice(sample_invoice):
    """
    Test que usa fixture sample_invoice de conftest.py

    Args:
        sample_invoice: Fixture inyectada automáticamente
    """
    # Fixture ya está disponible, no hay que crearla
    assert sample_invoice.total_amount > Decimal("0")
    assert len(sample_invoice.items) >= 1
```

### Parametrizar Tests

```python
@pytest.mark.parametrize("amount,currency,expected", [
    (Decimal("100.00"), "PEN", True),
    (Decimal("200.00"), "USD", True),
    (Decimal("-50.00"), "PEN", False),  # Negativo inválido
    (Decimal("100.00"), "XXX", False),  # Moneda inválida
])
def test_money_validation(amount, currency, expected):
    """Test con múltiples casos parametrizados."""
    if expected:
        money = Money(amount=amount, currency=currency)
        assert money.amount == amount
    else:
        with pytest.raises(ValueError):
            Money(amount=amount, currency=currency)
```

### Testear Excepciones

```python
def test_should_raise_error_for_invalid_input(self):
    """Test que verifica que se lanza excepción."""
    # Verificar que lanza ValueError
    with pytest.raises(ValueError) as exc_info:
        Money(amount=Decimal("-100.00"), currency="PEN")

    # Verificar mensaje de error
    assert "Amount cannot be negative" in str(exc_info.value)
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mocked_repository(self):
    """Test usando mock para repository."""
    # Crear mock de repository
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = create_test_invoice()

    # Usar en use case
    use_case = GetInvoiceUseCase(repository=mock_repo)
    result = use_case.execute(invoice_id=123)

    # Verificar que se llamó al mock
    mock_repo.get_by_id.assert_called_once_with(123)
```

### Tests Asíncronos

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation(self):
    """Test para función asíncrona."""
    result = await some_async_function()
    assert result is not None
```

## 📊 Coverage

### Generar Coverage Report

```bash
# Coverage en terminal
pytest --cov=src

# Coverage HTML (abre htmlcov/index.html)
pytest --cov=src --cov-report=html

# Coverage XML (para CI/CD)
pytest --cov=src --cov-report=xml

# Coverage con branch coverage
pytest --cov=src --cov-branch

# Fallar si coverage < 80%
pytest --cov=src --cov-fail-under=80
```

### Ver Coverage

```bash
# Abrir report HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Ver en terminal con detalle
pytest --cov=src --cov-report=term-missing
```

### Objetivos de Coverage

| Layer | Objetivo | Actual |
|-------|----------|--------|
| Domain | 95% | 85% |
| Application | 90% | 75% |
| Infrastructure | 80% | 70% |
| Presentation | 85% | 65% |
| **Total** | **90%** | **80%** |

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run tests
        run: |
          poetry run pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/sh
# Ejecutar tests unitarios antes de commit

echo "Running unit tests..."
pytest -m unit --maxfail=1

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## 🐛 Troubleshooting

### Problema: Tests Fallan Localmente pero Pasan en CI

**Causa**: Diferencias en entorno (variables, dependencias, archivos)

**Solución**:
```bash
# Limpiar cache de pytest
pytest --cache-clear

# Reinstalar dependencias
poetry install --sync

# Verificar variables de entorno
env | grep TEST
```

### Problema: Tests Lentos

**Causa**: Tests de integración mezclados con unitarios

**Solución**:
```bash
# Ejecutar solo tests unitarios
pytest -m unit

# Identificar tests lentos
pytest --durations=10

# Ejecutar en paralelo
pytest -n auto
```

### Problema: Fixtures No Encontradas

**Causa**: Fixtures no importadas o conftest.py no detectado

**Solución**:
1. Verificar que `conftest.py` existe en directorio de tests
2. Verificar que fixture está definida con `@pytest.fixture`
3. Verificar que no hay typo en nombre de fixture

```bash
# Ver fixtures disponibles
pytest --fixtures
```

### Problema: Import Errors

**Causa**: PYTHONPATH no configurado correctamente

**Solución**:
```bash
# Agregar directorio raíz al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/user/Invokox/backend"

# O en pytest.ini
pythonpath = .
```

### Problema: Tests de DB Fallan

**Causa**: Base de datos no inicializada o con datos incorrectos

**Solución**:
```bash
# Recrear DB de test
rm data/test_invokox.db
alembic upgrade head

# Usar transacciones en tests (rollback automático)
@pytest.fixture
def db_session():
    session = Session(engine)
    yield session
    session.rollback()  # Rollback después de test
    session.close()
```

## 📚 Recursos

### Documentación

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Parametrize](https://docs.pytest.org/en/stable/parametrize.html)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Plugins Útiles

```bash
# Instalar plugins adicionales
poetry add --group dev pytest-cov       # Coverage
poetry add --group dev pytest-xdist     # Parallel execution
poetry add --group dev pytest-asyncio   # Async tests
poetry add --group dev pytest-mock      # Mocking helpers
poetry add --group dev pytest-timeout   # Timeout para tests
poetry add --group dev pytest-randomly  # Orden aleatorio
```

### Best Practices

1. **Tests Independientes**: Cada test debe poder ejecutarse solo
2. **Tests Determinísticos**: Mismo resultado siempre (no aleatorios)
3. **Tests Rápidos**: Unitarios < 1s, integración < 10s
4. **Tests Claros**: Nombre y docstring explican qué testean
5. **Tests Completos**: Casos happy path + edge cases + errores
6. **Tests Mantenibles**: DRY, fixtures compartidas, helpers

## 🎯 Métricas de Calidad

### Objetivos

- ✅ Coverage > 90%
- ✅ Todos los tests pasan
- ✅ Tests unitarios < 5s total
- ✅ Tests integración < 30s total
- ✅ Sin warnings o deprecations
- ✅ Sin tests skipped (o justificados)

### Comandos de Verificación

```bash
# Verificar todo
pytest --cov=src --cov-fail-under=90 -m "not slow"

# Verificar sin warnings
pytest --strict-warnings

# Verificar que no hay tests skipped
pytest --runxfail
```

---

**Última actualización**: 2024-11-19
**Tests totales**: 50+
**Coverage**: 80%+
**Tiempo ejecución**: < 5s (unit), < 30s (integration)
