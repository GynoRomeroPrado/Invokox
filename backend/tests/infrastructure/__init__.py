"""
==============================================================================
INFRASTRUCTURE LAYER TESTS
==============================================================================
Tests de integración para el Infrastructure Layer (capa de infraestructura).

El Infrastructure Layer contiene:
- Repositories: Implementaciones concretas de IRepository (SQLModel, etc.)
- Database: Configuración de conexión a base de datos
- Services: Servicios externos (OCR, email, storage, etc.)
- Workers: Celery tasks para procesamiento asíncrono

Estos tests validan:
- Persistencia correcta en base de datos
- Queries y filtros funcionan correctamente
- Transacciones y rollbacks
- Constraints y validaciones de DB
- Migraciones de base de datos
- Integración con servicios externos (mocks)

Archivos:
- test_repositories.py: Tests de InvoiceRepository y CompanyRepository
- test_database.py: Tests de configuración y conexión
- test_services.py: Tests de OCR Service y otros servicios

Estrategia de testing:
- Usar base de datos de prueba (SQLite in-memory o PostgreSQL test)
- Fixtures para setup/teardown de DB
- Transacciones con rollback para aislamiento
- Datos de prueba realistas
- Tests independientes (no comparten estado)

Markers utilizados:
- @pytest.mark.integration: Tests de integración (requieren DB)
- @pytest.mark.requires_db: Tests que requieren base de datos
- @pytest.mark.asyncio: Tests asíncronos

Setup:
Para ejecutar estos tests necesitas:
1. Base de datos de test configurada
2. Variables de entorno: TEST_DATABASE_URL
3. Alembic migrations aplicadas

Ejecución:
    pytest -m integration  # Solo tests de integración
    pytest tests/infrastructure/  # Todos los tests del layer
    pytest tests/infrastructure/test_repositories.py  # Archivo específico
==============================================================================
"""
