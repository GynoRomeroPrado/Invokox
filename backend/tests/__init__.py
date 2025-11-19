"""
==============================================================================
TESTS PACKAGE - INVOKOX V2.0
==============================================================================
Suite de tests unitarios para el Domain Layer.

Estructura:
- conftest.py: Fixtures compartidas y configuración de pytest
- domain/: Tests del Domain Layer
  - test_value_objects.py: Tests para Money y TaxID
  - test_entities.py: Tests para Invoice, Company, InvoiceItem
- application/: Tests del Application Layer
- infrastructure/: Tests del Infrastructure Layer

Ejecutar tests:
    pytest                          # Todos los tests
    pytest tests/domain/            # Solo domain tests
    pytest -v                       # Verbose
    pytest --cov=src               # Con coverage
    pytest -k "test_money"         # Tests específicos

Convenciones:
- Un archivo de test por módulo
- Una clase de test por clase del dominio
- Nombres descriptivos: test_should_do_something_when_condition
- Arrange-Act-Assert pattern
- Fixtures para setup común
==============================================================================
"""
