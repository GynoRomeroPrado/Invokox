"""
Company Endpoints

API REST para gestión de empresas (CRUD completo).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List, Optional

from src.infrastructure.database.config import get_session_dependency
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.domain.entities.company import Company

router = APIRouter(prefix="/companies")


# ==============================================================================
# RESPONSE MODELS
# ==============================================================================

class CompanyResponse(Company):
    """Response model para company."""
    pass


# ==============================================================================
# DEPENDENCY INJECTION
# ==============================================================================

def get_company_repository(
    session: Session = Depends(get_session_dependency)
) -> CompanyRepository:
    """Dependency para obtener company repository."""
    return CompanyRepository(session)


# ==============================================================================
# ENDPOINTS - CRUD BÁSICO
# ==============================================================================

@router.get("", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = Query(None, description="Filtrar por tipo (EMISOR, RECEPTOR, AMBOS)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    repository: CompanyRepository = Depends(get_company_repository)
) -> List[Company]:
    """
    Lista todas las empresas con paginación y filtros.

    **Parámetros:**
    - `skip`: Número de registros a saltar
    - `limit`: Máximo de registros a retornar
    - `type`: Filtrar por tipo (EMISOR, RECEPTOR, AMBOS)
    - `is_active`: Filtrar por estado activo

    **Returns:**
    - Lista de empresas ordenadas por nombre
    """
    filters = {}
    if type:
        filters["type"] = type
    if is_active is not None:
        filters["is_active"] = is_active

    companies = await repository.get_all(skip=skip, limit=limit, **filters)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    repository: CompanyRepository = Depends(get_company_repository)
) -> Company:
    """
    Obtiene una empresa por ID.

    **Raises:**
    - 404: Si la empresa no existe
    """
    company = await repository.get_by_id(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    return company


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: dict,  # TODO: Crear schema Pydantic
    repository: CompanyRepository = Depends(get_company_repository)
) -> Company:
    """
    Crea una nueva empresa.

    **Body:**
    ```json
    {
      "tax_id": "20123456789",
      "name": "EMPRESA DEMO S.A.C.",
      "commercial_name": "EMPRESA DEMO",
      "type": "EMISOR",
      "address": "Av. Principal 123, Lima",
      "email": "contacto@empresademo.com",
      "phone": "+51 1 234-5678"
    }
    ```

    **Raises:**
    - 400: Si el tax_id ya existe
    """
    # Verificar que el tax_id no exista
    existing = await repository.get_by_tax_id(company_data["tax_id"])
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with tax_id '{company_data['tax_id']}' already exists"
        )

    # Crear empresa
    company = Company(**company_data)

    try:
        created_company = await repository.create(company)
        return created_company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: dict,
    repository: CompanyRepository = Depends(get_company_repository)
) -> Company:
    """
    Actualiza una empresa existente.

    **Raises:**
    - 404: Si la empresa no existe
    - 400: Si los datos son inválidos
    """
    company = await repository.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    # Actualizar campos
    for key, value in company_data.items():
        if hasattr(company, key) and key not in ["id", "created_at", "invoice_count"]:
            setattr(company, key, value)

    company.update_timestamp()

    try:
        updated_company = await repository.update(company)
        return updated_company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    repository: CompanyRepository = Depends(get_company_repository)
):
    """
    Elimina una empresa.

    **Nota:** Solo se puede eliminar si no tiene facturas asociadas.
    De lo contrario, usar PATCH para marcar como is_active=False.

    **Raises:**
    - 404: Si la empresa no existe
    - 400: Si tiene facturas asociadas
    """
    company = await repository.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    try:
        deleted = await repository.delete(company_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete company"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==============================================================================
# ENDPOINTS - BÚSQUEDA
# ==============================================================================

@router.get("/search/{query}", response_model=List[CompanyResponse])
async def search_companies(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: CompanyRepository = Depends(get_company_repository)
) -> List[Company]:
    """
    Búsqueda de empresas por nombre, nombre comercial o tax_id.

    **Ejemplo:**
    ```
    GET /api/v1/companies/search/ACME
    ```
    """
    companies = await repository.search_by_name(query, skip=skip, limit=limit)
    return companies


@router.get("/by-tax-id/{tax_id}", response_model=CompanyResponse)
async def get_company_by_tax_id(
    tax_id: str,
    repository: CompanyRepository = Depends(get_company_repository)
) -> Company:
    """
    Obtiene una empresa por su identificador fiscal.

    **Ejemplo:**
    ```
    GET /api/v1/companies/by-tax-id/20123456789
    ```
    """
    company = await repository.get_by_tax_id(tax_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with tax_id '{tax_id}' not found"
        )

    return company


@router.get("/by-type/{company_type}", response_model=List[CompanyResponse])
async def get_companies_by_type(
    company_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: CompanyRepository = Depends(get_company_repository)
) -> List[Company]:
    """
    Obtiene empresas por tipo.

    **Tipos válidos:**
    - EMISOR
    - RECEPTOR
    - AMBOS
    """
    companies = await repository.get_by_type(company_type, skip=skip, limit=limit)
    return companies


# ==============================================================================
# ENDPOINTS - OPERACIONES ESPECIALES
# ==============================================================================

@router.post("/{company_id}/update-invoice-count", response_model=CompanyResponse)
async def update_invoice_count(
    company_id: int,
    repository: CompanyRepository = Depends(get_company_repository)
) -> Company:
    """
    Actualiza el contador de facturas de una empresa.

    Cuenta todas las facturas donde la empresa es emisor o receptor.

    **Returns:**
    - Empresa con invoice_count actualizado
    """
    company = await repository.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    await repository.update_invoice_count(company_id)

    # Obtener empresa actualizada
    updated_company = await repository.get_by_id(company_id)
    return updated_company


@router.get("/stats/count")
async def get_companies_count(
    type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    repository: CompanyRepository = Depends(get_company_repository)
) -> dict:
    """
    Obtiene el conteo de empresas con filtros opcionales.

    **Returns:**
    ```json
    {
      "count": 15,
      "filters": {...}
    }
    ```
    """
    filters = {}
    if type:
        filters["type"] = type
    if is_active is not None:
        filters["is_active"] = is_active

    count = await repository.count(**filters)

    return {
        "count": count,
        "filters": filters
    }
