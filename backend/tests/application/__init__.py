"""
==============================================================================
APPLICATION LAYER TESTS
==============================================================================
Tests unitarios para el Application Layer (capa de aplicación).

El Application Layer contiene:
- Use Cases: Orquestadores de lógica de negocio
- Interfaces: Contratos que define el dominio, implementa infraestructura
- DTOs: Data Transfer Objects para input/output

Estos tests validan:
- Ejecución correcta de Use Cases
- Validación de input DTOs
- Manejo de errores y excepciones
- Coordinación entre repositorios y entidades
- Flujos de negocio completos
- Dependency injection correcta

Archivos:
- test_use_cases.py: Tests para todos los Use Cases
- test_interfaces.py: Tests para interfaces y DTOs

Estrategia de testing:
- Mock de repositorios (no usar DB real)
- Fixtures para crear datos de prueba
- Parametrización para múltiples casos
- Verificación de llamadas a mocks
- Tests de happy path + error cases

Markers utilizados:
- @pytest.mark.unit: Tests unitarios rápidos
- @pytest.mark.asyncio: Tests asíncronos
==============================================================================
"""
