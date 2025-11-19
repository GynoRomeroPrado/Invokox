"""
Invoice Endpoints

API REST para gestión de facturas (CRUD completo + operaciones especiales).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import List, Optional
from datetime import date, datetime
from pathlib import Path
import aiofiles
import os
import io
import csv

from src.infrastructure.database.config import get_session_dependency
from src.infrastructure.repositories.invoice_repository import InvoiceRepository
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.application.use_cases.create_invoice_use_case import (
    CreateInvoiceUseCase,
    CreateInvoiceInput
)
from src.application.use_cases.process_ocr_use_case import (
    ProcessOCRUseCase,
    ProcessOCRInput
)
from src.application.use_cases.approve_invoice_use_case import (
    ApproveInvoiceUseCase,
    ApproveInvoiceInput
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


# ==============================================================================
# ENDPOINTS - UPLOAD Y PROCESAMIENTO OCR
# ==============================================================================

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_invoice_file(
    file: UploadFile = File(..., description="Archivo PDF o imagen de la factura"),
    created_by: str = Query(..., description="Email del usuario que sube el archivo"),
    invoice_repo: InvoiceRepository = Depends(get_invoice_repository),
    company_repo: CompanyRepository = Depends(get_company_repository)
) -> dict:
    """
    Sube un archivo de factura (PDF o imagen) y crea un registro PENDING.

    **Parámetros:**
    - `file`: Archivo PDF o imagen (PNG, JPG, JPEG)
    - `created_by`: Email del usuario

    **Returns:**
    ```json
    {
      "invoice_id": 123,
      "file_path": "/uploads/2025/01/factura_001.pdf",
      "status": "PENDING",
      "message": "Archivo subido exitosamente. Usar /invoices/{id}/process para procesar."
    }
    ```

    **Raises:**
    - 400: Si el archivo no es válido (formato, tamaño)
    - 500: Si falla el guardado del archivo
    """
    # Validar tipo de archivo
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg"}
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de archivo no soportado: {file_ext}. Permitidos: {', '.join(allowed_extensions)}"
        )

    # Validar tamaño (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()
    file.file.seek(0)  # Volver al inicio

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo muy grande: {file_size / 1024 / 1024:.2f}MB. Máximo: 10MB"
        )

    # Crear directorio de uploads si no existe
    upload_base = Path("uploads")
    current_date = datetime.now()
    upload_dir = upload_base / str(current_date.year) / f"{current_date.month:02d}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generar nombre único
    timestamp = current_date.strftime("%Y%m%d_%H%M%S")
    safe_filename = f"invoice_{timestamp}{file_ext}"
    file_path = upload_dir / safe_filename

    # Guardar archivo
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar archivo: {str(e)}"
        )

    # Crear registro de Invoice con status PENDING
    # Generamos un series temporal que luego será reemplazado por OCR
    temp_series = f"TEMP-{timestamp}"

    input_data = CreateInvoiceInput(
        series=temp_series,
        document_type="FACTURA",
        issue_date=current_date.date().isoformat(),
        issuer_tax_id="00000000000",  # Temporal, será llenado por OCR
        issuer_name="PENDIENTE DE PROCESAMIENTO",
        receiver_tax_id="00000000000",  # Temporal
        receiver_name="PENDIENTE DE PROCESAMIENTO",
        currency="PEN",  # Default, puede ser cambiado por OCR
        file_path=str(file_path),
        created_by=created_by,
        notes=f"Archivo subido: {file.filename}"
    )

    use_case = CreateInvoiceUseCase(invoice_repo, company_repo)

    try:
        invoice = await use_case.execute(input_data)

        return {
            "invoice_id": invoice.id,
            "file_path": str(file_path),
            "status": invoice.status,
            "message": f"Archivo subido exitosamente. Usar POST /invoices/{invoice.id}/process para procesar con OCR."
        }
    except ValueError as e:
        # Si falla la creación, eliminar el archivo subido
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{invoice_id}/process")
async def process_invoice_ocr(
    invoice_id: int,
    engine: Optional[str] = Query(None, description="Engine de OCR: donut, paddleocr, docling, tesseract"),
    use_gpu: bool = Query(False, description="Usar aceleración GPU"),
    force_reprocess: bool = Query(False, description="Forzar reprocesamiento si ya fue procesada"),
    invoice_repo: InvoiceRepository = Depends(get_invoice_repository)
) -> dict:
    """
    Procesa una factura con OCR (Donut Deep Learning por defecto).

    **Parámetros:**
    - `invoice_id`: ID de la factura
    - `engine`: Motor de OCR (default: donut)
      - `donut`: Document Understanding Transformer (recomendado, GPU acelerado)
      - `paddleocr`: PaddleOCR (fallback)
      - `docling`: Layout analysis
      - `tesseract`: OCR tradicional
    - `use_gpu`: Usar GPU para aceleración (recomendado para Donut)
    - `force_reprocess`: Reprocesar aunque ya esté procesada

    **Returns:**
    ```json
    {
      "task_id": "abc123-def456",
      "status": "PROCESSING",
      "message": "Procesamiento OCR iniciado. Usar GET /tasks/{task_id} para consultar estado."
    }
    ```

    **Notas:**
    - El procesamiento es asíncrono (usa Celery)
    - El estado de la factura cambia a PROCESSING
    - Al completar, cambia a COMPLETED, REVIEW_NEEDED o ERROR según confidence
    - Donut es el motor por defecto (Vision Transformer específico para facturas)

    **Raises:**
    - 404: Si la factura no existe
    - 400: Si la factura no puede ser procesada
    """
    # Obtener factura
    invoice = await invoice_repo.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )

    # Validar que tenga archivo
    if not invoice.file_path or not Path(invoice.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice file not found: {invoice.file_path}"
        )

    # Validar que pueda ser procesada
    if invoice.status == "PROCESSING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice is already being processed"
        )

    if invoice.status in ["APPROVED", "REJECTED"] and not force_reprocess:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice with status '{invoice.status}' cannot be reprocessed without force_reprocess=True"
        )

    # Crear input para Use Case
    input_data = ProcessOCRInput(
        invoice_id=invoice_id,
        engine=engine,  # None usa Donut por defecto
        force_reprocess=force_reprocess,
        use_gpu=use_gpu
    )

    # Ejecutar Use Case (asíncrono)
    use_case = ProcessOCRUseCase(invoice_repository=invoice_repo)

    try:
        # En producción, esto debería lanzar una tarea Celery y retornar task_id
        # Por ahora, ejecutamos directamente
        result = await use_case.execute(input_data)

        # Simular task_id (en producción vendría de Celery)
        task_id = f"task_{invoice_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return {
            "task_id": task_id,
            "invoice_id": invoice_id,
            "status": result.get("status", "PROCESSING"),
            "confidence": result.get("confidence"),
            "engine": engine or "donut",
            "message": "Procesamiento OCR completado." if result.get("status") == "COMPLETED" else "Procesamiento OCR iniciado.",
            "result": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en procesamiento OCR: {str(e)}"
        )


# ==============================================================================
# ENDPOINTS - EXPORTACIÓN
# ==============================================================================

@router.post("/export/excel")
async def export_invoices_to_excel(
    invoice_ids: List[int] = Body(..., description="Lista de IDs de facturas a exportar"),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> StreamingResponse:
    """
    Exporta facturas seleccionadas a formato Excel.

    **Body:**
    ```json
    {
      "invoice_ids": [1, 2, 3, 4, 5]
    }
    ```

    **Returns:**
    - Archivo Excel (.xlsx) para descarga

    **Raises:**
    - 400: Si no se proporcionan IDs o alguna factura no existe
    """
    if not invoice_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un invoice_id"
        )

    # Obtener facturas
    invoices = []
    for invoice_id in invoice_ids:
        invoice = await repository.get_by_id(invoice_id)
        if invoice:
            invoices.append(invoice)

    if not invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron facturas con los IDs proporcionados"
        )

    # Generar Excel
    try:
        # Por ahora, simulamos con CSV (en producción usar openpyxl o xlsxwriter)
        output = io.StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow([
            "ID", "Series", "Tipo", "Fecha Emisión", "Fecha Vencimiento",
            "Emisor", "RUC Emisor", "Receptor", "RUC Receptor",
            "Moneda", "Subtotal", "Impuestos", "Total", "Estado"
        ])

        # Datos
        for invoice in invoices:
            writer.writerow([
                invoice.id,
                invoice.series,
                invoice.invoice_type,
                invoice.issue_date,
                invoice.due_date,
                invoice.issuer.name if invoice.issuer else "",
                invoice.issuer.tax_id if invoice.issuer else "",
                invoice.receiver.name if invoice.receiver else "",
                invoice.receiver.tax_id if invoice.receiver else "",
                invoice.currency,
                invoice.subtotal_amount,
                invoice.tax_amount,
                invoice.total_amount,
                invoice.status
            ])

        # Convertir a bytes
        output.seek(0)
        content = output.getvalue().encode('utf-8')

        # Retornar como descarga
        return StreamingResponse(
            io.BytesIO(content),
            media_type="text/csv",  # Cambiar a application/vnd.openxmlformats-officedocument.spreadsheetml.sheet para Excel real
            headers={
                "Content-Disposition": f"attachment; filename=facturas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar archivo: {str(e)}"
        )


@router.post("/export/csv")
async def export_invoices_to_csv(
    invoice_ids: List[int] = Body(..., description="Lista de IDs de facturas a exportar"),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> StreamingResponse:
    """
    Exporta facturas seleccionadas a formato CSV.

    **Body:**
    ```json
    {
      "invoice_ids": [1, 2, 3, 4, 5]
    }
    ```

    **Returns:**
    - Archivo CSV para descarga

    **Raises:**
    - 400: Si no se proporcionan IDs o alguna factura no existe
    """
    if not invoice_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un invoice_id"
        )

    # Obtener facturas
    invoices = []
    for invoice_id in invoice_ids:
        invoice = await repository.get_by_id(invoice_id)
        if invoice:
            invoices.append(invoice)

    if not invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron facturas con los IDs proporcionados"
        )

    # Generar CSV
    try:
        output = io.StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow([
            "ID", "Series", "Tipo", "Fecha Emisión", "Fecha Vencimiento",
            "Emisor", "RUC Emisor", "Receptor", "RUC Receptor",
            "Moneda", "Subtotal", "Impuestos", "Total", "Estado",
            "Confianza OCR", "Fecha Creación", "Notas"
        ])

        # Datos
        for invoice in invoices:
            writer.writerow([
                invoice.id,
                invoice.series,
                invoice.invoice_type,
                invoice.issue_date,
                invoice.due_date,
                invoice.issuer.name if invoice.issuer else "",
                invoice.issuer.tax_id if invoice.issuer else "",
                invoice.receiver.name if invoice.receiver else "",
                invoice.receiver.tax_id if invoice.receiver else "",
                invoice.currency,
                invoice.subtotal_amount,
                invoice.tax_amount,
                invoice.total_amount,
                invoice.status,
                invoice.ocr_confidence if hasattr(invoice, 'ocr_confidence') else "",
                invoice.created_at,
                invoice.notes or ""
            ])

        # Convertir a bytes
        output.seek(0)
        content = output.getvalue().encode('utf-8')

        # Retornar como descarga
        return StreamingResponse(
            io.BytesIO(content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=facturas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar CSV: {str(e)}"
        )


# ==============================================================================
# ENDPOINTS - BATCH OPERATIONS
# ==============================================================================

@router.post("/batch/approve")
async def batch_approve_invoices(
    invoice_ids: List[int] = Body(..., description="Lista de IDs de facturas a aprobar"),
    approved_by: str = Body(..., description="Email del usuario que aprueba"),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> dict:
    """
    Aprueba múltiples facturas en lote.

    **Body:**
    ```json
    {
      "invoice_ids": [1, 2, 3, 4, 5],
      "approved_by": "admin@invokox.com"
    }
    ```

    **Returns:**
    ```json
    {
      "success_count": 3,
      "failed_count": 2,
      "approved_ids": [1, 2, 3],
      "failed_ids": [
        {"id": 4, "reason": "Already approved"},
        {"id": 5, "reason": "Invalid status"}
      ]
    }
    ```
    """
    if not invoice_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un invoice_id"
        )

    approved_ids = []
    failed_ids = []

    for invoice_id in invoice_ids:
        try:
            invoice = await repository.get_by_id(invoice_id)
            if not invoice:
                failed_ids.append({
                    "id": invoice_id,
                    "reason": "Invoice not found"
                })
                continue

            invoice.approve(approved_by)
            await repository.update(invoice)
            approved_ids.append(invoice_id)

        except ValueError as e:
            failed_ids.append({
                "id": invoice_id,
                "reason": str(e)
            })
        except Exception as e:
            failed_ids.append({
                "id": invoice_id,
                "reason": f"Unexpected error: {str(e)}"
            })

    return {
        "success_count": len(approved_ids),
        "failed_count": len(failed_ids),
        "approved_ids": approved_ids,
        "failed_ids": failed_ids
    }


@router.post("/batch/reject")
async def batch_reject_invoices(
    invoice_ids: List[int] = Body(..., description="Lista de IDs de facturas a rechazar"),
    rejected_by: str = Body(..., description="Email del usuario que rechaza"),
    reason: Optional[str] = Body(None, description="Razón del rechazo"),
    repository: InvoiceRepository = Depends(get_invoice_repository)
) -> dict:
    """
    Rechaza múltiples facturas en lote.

    **Body:**
    ```json
    {
      "invoice_ids": [1, 2, 3],
      "rejected_by": "admin@invokox.com",
      "reason": "Datos incorrectos"
    }
    ```

    **Returns:**
    ```json
    {
      "success_count": 2,
      "failed_count": 1,
      "rejected_ids": [1, 2],
      "failed_ids": [{"id": 3, "reason": "..."}]
    }
    ```
    """
    if not invoice_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un invoice_id"
        )

    rejected_ids = []
    failed_ids = []

    for invoice_id in invoice_ids:
        try:
            invoice = await repository.get_by_id(invoice_id)
            if not invoice:
                failed_ids.append({
                    "id": invoice_id,
                    "reason": "Invoice not found"
                })
                continue

            invoice.reject(rejected_by, reason)
            await repository.update(invoice)
            rejected_ids.append(invoice_id)

        except ValueError as e:
            failed_ids.append({
                "id": invoice_id,
                "reason": str(e)
            })
        except Exception as e:
            failed_ids.append({
                "id": invoice_id,
                "reason": f"Unexpected error: {str(e)}"
            })

    return {
        "success_count": len(rejected_ids),
        "failed_count": len(failed_ids),
        "rejected_ids": rejected_ids,
        "failed_ids": failed_ids
    }
