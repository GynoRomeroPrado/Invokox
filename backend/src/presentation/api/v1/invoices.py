"""
Invoice Endpoints

API REST para gestión de facturas (CRUD completo + operaciones especiales).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List, Optional
from datetime import date

from src.infrastructure.database.config import get_session_dependency
from src.infrastructure.repositories.invoice_repository import InvoiceRepository
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.application.use_cases.create_invoice_use_case import (
    CreateInvoiceUseCase,
    CreateInvoiceInput
)
from src.domain.entities.invoice import Invoice
from src.domain.entities.invoice_item import InvoiceItem

router = APIRouter(prefix="/invoices")


# ==============================================================================
# RESPONSE MODELS (DTOs)
# ==============================================================================

class InvoiceItemResponse(InvoiceItem):
    """Response model para invoice item."""
    pass


class InvoiceResponse(Invoice):
    """Response model para invoice."""
    pass


class InvoiceListResponse:
    """Response model para lista paginada de invoices."""
    items: List[InvoiceResponse]
    total: int
    page: int
    pages: int


class InvoiceCreateRequest:
    """Request model para crear invoice."""
    pass  # Por ahora usar el modelo de dominio directamente


# ==============================================================================
# DEPENDENCY INJECTION
# ==============================================================================

def get_invoice_repository(
    session: Session = Depends(get_session_dependency)
) -> InvoiceRepository:
    """Dependency para obtener invoice repository."""
    return InvoiceRepository(session)


def get_company_repository(
    session: Session = Depends(get_session_dependency)
) -> CompanyRepository:
    """Dependency para obtener company repository."""
    return CompanyRepository(session)


# ==============================================================================
# ENDPOINTS - CRUD BÁSICO
# ==============================================================================

@router.get("", response_model=List[InvoiceResponse])
async def list_invoices(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    currency: Optional[str] = Query(None, description="Filtrar por moneda"),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> List[Invoice]:
    """
    Lista todas las facturas con paginación y filtros.

    **Parámetros:**
    - `skip`: Número de registros a saltar (paginación)
    - `limit`: Máximo de registros a retornar
    - `status`: Filtrar por estado (PENDING, PROCESSING, COMPLETED, APPROVED, REJECTED, ERROR)
    - `currency`: Filtrar por moneda (PEN, USD, EUR, etc.)

    **Returns:**
    - Lista de facturas

    **Ejemplo:**
    ```
    GET /api/v1/invoices?skip=0&limit=10&status=PENDING
    ```
    """
    filters = {}
    if status:
        filters["status"] = status
    if currency:
        filters["currency"] = currency

    invoices = await repository.get_all(skip=skip, limit=limit, **filters)
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> Invoice:
    """
    Obtiene una factura por ID.

    **Parámetros:**
    - `invoice_id`: ID de la factura

    **Returns:**
    - Factura con sus items

    **Raises:**
    - 404: Si la factura no existe
    """
    invoice = await repository.get_by_id(invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )

    return invoice


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: dict,  # TODO: Crear schema Pydantic específico
    invoice_repo: InvoiceRepository = Depends(get_invoice_repository),
    company_repo: CompanyRepository = Depends(get_company_repository)
) -> Invoice:
    """
    Crea una nueva factura.

    **Body:**
    ```json
    {
      "series": "F001-00001234",
      "document_type": "FACTURA",
      "issue_date": "2025-01-15",
      "issuer_tax_id": "20123456789",
      "issuer_name": "EMPRESA EMISORA S.A.C.",
      "receiver_tax_id": "20987654321",
      "receiver_name": "EMPRESA RECEPTORA S.A.",
      "currency": "PEN",
      "file_path": "/uploads/2025/01/factura_001.pdf",
      "created_by": "admin@invokox.com",
      "items": [
        {
          "description": "Producto A",
          "quantity": 2,
          "unit_price": 100.00,
          "discount_percent": 0,
          "tax_percent": 18
        }
      ]
    }
    ```

    **Returns:**
    - Factura creada con ID asignado

    **Raises:**
    - 400: Si los datos son inválidos o el series ya existe
    """
    # Crear input para use case
    input_data = CreateInvoiceInput(
        series=invoice_data["series"],
        document_type=invoice_data.get("document_type", "FACTURA"),
        issue_date=invoice_data["issue_date"],
        due_date=invoice_data.get("due_date"),
        issuer_tax_id=invoice_data["issuer_tax_id"],
        issuer_name=invoice_data["issuer_name"],
        receiver_tax_id=invoice_data["receiver_tax_id"],
        receiver_name=invoice_data["receiver_name"],
        currency=invoice_data.get("currency", "PEN"),
        file_path=invoice_data["file_path"],
        created_by=invoice_data["created_by"],
        items=invoice_data.get("items", []),
        notes=invoice_data.get("notes"),
    )

    # Ejecutar use case
    use_case = CreateInvoiceUseCase(invoice_repo, company_repo)

    try:
        invoice = await use_case.execute(input_data)
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: dict,  # TODO: Crear schema Pydantic
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> Invoice:
    """
    Actualiza una factura existente.

    **Parámetros:**
    - `invoice_id`: ID de la factura

    **Body:**
    - Campos a actualizar (parcial o completo)

    **Returns:**
    - Factura actualizada

    **Raises:**
    - 404: Si la factura no existe
    - 400: Si los datos son inválidos
    """
    # Obtener factura existente
    invoice = await repository.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )

    # Verificar si es editable
    if not invoice.is_editable():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice with status '{invoice.status}' cannot be edited"
        )

    # Actualizar campos
    for key, value in invoice_data.items():
        if hasattr(invoice, key):
            setattr(invoice, key, value)

    # Recalcular totales
    invoice.calculate_totals()
    invoice.update_timestamp()

    # Guardar
    try:
        updated_invoice = await repository.update(invoice)
        return updated_invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    repository: InvoiceRepository = Depends(get_invoice_repository)
):
    """
    Elimina una factura.

    **Parámetros:**
    - `invoice_id`: ID de la factura

    **Returns:**
    - 204 No Content si se eliminó exitosamente

    **Raises:**
    - 404: Si la factura no existe
    - 400: Si la factura no puede ser eliminada (ej: está aprobada)
    """
    # Obtener factura
    invoice = await repository.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )

    # Verificar si es eliminable
    if not invoice.is_deletable():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice with status '{invoice.status}' cannot be deleted"
        )

    # Eliminar
    deleted = await repository.delete(invoice_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete invoice"
        )


# ==============================================================================
# ENDPOINTS - BÚSQUEDA Y FILTROS
# ==============================================================================

@router.get("/search/{query}", response_model=List[InvoiceResponse])
async def search_invoices(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> List[Invoice]:
    """
    Búsqueda de texto completo en facturas.

    Busca en: series, nombre emisor, nombre receptor, tax IDs, notas.

    **Parámetros:**
    - `query`: Texto a buscar

    **Ejemplo:**
    ```
    GET /api/v1/invoices/search/F001
    ```
    """
    invoices = await repository.search(query, skip=skip, limit=limit)
    return invoices


@router.get("/by-series/{series}", response_model=InvoiceResponse)
async def get_invoice_by_series(
    series: str,
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> Invoice:
    """
    Obtiene una factura por su número de serie.

    **Ejemplo:**
    ```
    GET /api/v1/invoices/by-series/F001-00001234
    ```
    """
    invoice = await repository.get_by_series(series)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with series '{series}' not found"
        )

    return invoice


@router.get("/by-status/{status_value}", response_model=List[InvoiceResponse])
async def get_invoices_by_status(
    status_value: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> List[Invoice]:
    """
    Obtiene facturas por estado.

    **Estados válidos:**
    - PENDING
    - PROCESSING
    - COMPLETED
    - APPROVED
    - REJECTED
    - ERROR
    """
    invoices = await repository.get_by_status(status_value, skip=skip, limit=limit)
    return invoices


@router.get("/by-company/{company_id}", response_model=List[InvoiceResponse])
async def get_invoices_by_company(
    company_id: int,
    is_issuer: bool = Query(True, description="True si es emisor, False si es receptor"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> List[Invoice]:
    """
    Obtiene facturas de una empresa.

    **Parámetros:**
    - `company_id`: ID de la empresa
    - `is_issuer`: True para facturas emitidas, False para recibidas
    """
    invoices = await repository.get_by_company(
        company_id,
        is_issuer=is_issuer,
        skip=skip,
        limit=limit
    )
    return invoices


# ==============================================================================
# ENDPOINTS - OPERACIONES ESPECIALES
# ==============================================================================

@router.post("/{invoice_id}/approve", response_model=InvoiceResponse)
async def approve_invoice(
    invoice_id: int,
    approved_by: str = Query(..., description="Email del usuario que aprueba"),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> Invoice:
    """
    Aprueba una factura.

    **Parámetros:**
    - `invoice_id`: ID de la factura
    - `approved_by`: Email del usuario que aprueba

    **Returns:**
    - Factura con estado APPROVED
    """
    invoice = await repository.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )

    try:
        invoice.approve(approved_by)
        updated_invoice = await repository.update(invoice)
        return updated_invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{invoice_id}/reject", response_model=InvoiceResponse)
async def reject_invoice(
    invoice_id: int,
    rejected_by: str = Query(..., description="Email del usuario que rechaza"),
    reason: Optional[str] = Query(None, description="Razón del rechazo"),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> Invoice:
    """
    Rechaza una factura.

    **Parámetros:**
    - `invoice_id`: ID de la factura
    - `rejected_by`: Email del usuario que rechaza
    - `reason`: Razón opcional del rechazo
    """
    invoice = await repository.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )

    try:
        invoice.reject(rejected_by, reason)
        updated_invoice = await repository.update(invoice)
        return updated_invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats/count")
async def get_invoices_count(
    status: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> dict:
    """
    Obtiene el conteo de facturas con filtros opcionales.

    **Returns:**
    ```json
    {
      "count": 42,
      "filters": {...}
    }
    ```
    """
    filters = {}
    if status:
        filters["status"] = status
    if currency:
        filters["currency"] = currency

    count = await repository.count(**filters)

    return {
        "count": count,
        "filters": filters
    }
