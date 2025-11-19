"""
==============================================================================
DOMAIN LAYER TESTS
==============================================================================
Tests unitarios para el Domain Layer (capa de dominio).

El Domain Layer es el núcleo de la aplicación y contiene:
- Value Objects: Objetos inmutables con lógica de validación
- Entities: Objetos con identidad única y ciclo de vida
- Domain Services: Lógica de negocio que no pertenece a una entidad

Estos tests validan:
- Creación correcta de objetos
- Validaciones de negocio
- Comportamiento de métodos
- Invariantes del dominio
- Edge cases y errores

Archivos:
- test_value_objects.py: Tests para Money y TaxID
- test_entities.py: Tests para Invoice, Company, InvoiceItem
==============================================================================
"""
