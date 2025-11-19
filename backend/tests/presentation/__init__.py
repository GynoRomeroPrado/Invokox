"""
==============================================================================
PRESENTATION LAYER TESTS
==============================================================================
Tests de integración para el Presentation Layer (capa de presentación / API).

El Presentation Layer contiene:
- API Endpoints: REST API con FastAPI
- Request/Response schemas
- Authentication y Authorization middleware
- Error handling y HTTP status codes

Estos tests validan:
- Endpoints HTTP funcionan correctamente
- Request validation (Pydantic schemas)
- Response format y status codes
- Error handling (404, 400, 500, etc.)
- Authentication y permisos
- CORS headers
- Rate limiting

Archivos:
- test_api_health.py: Tests de health check endpoints
- test_api_invoices.py: Tests de endpoints /api/v1/invoices
- test_api_companies.py: Tests de endpoints /api/v1/companies

Estrategia de testing:
- FastAPI TestClient (no requiere servidor corriendo)
- Mocks de repositories y services
- Tests de happy path + error cases
- Verificar status codes HTTP
- Validar structure de respuestas JSON

Markers utilizados:
- @pytest.mark.integration: Tests de integración
- @pytest.mark.api: Tests de API
- @pytest.mark.asyncio: Tests asíncronos

Setup:
- TestClient de FastAPI
- Override de dependencies (repositories, auth)
- Base de datos de test o mocks

Ejecución:
    pytest -m api  # Solo tests de API
    pytest tests/presentation/  # Todos del layer
    pytest tests/presentation/test_api_invoices.py  # Archivo específico

Ejemplo de test:
    def test_get_invoice(test_client):
        response = test_client.get("/api/v1/invoices/123")
        assert response.status_code == 200
        assert "series" in response.json()
==============================================================================
"""
