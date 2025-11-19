"""
==============================================================================
APPLICATION LAYER - USE CASES
==============================================================================
Use Cases (Casos de Uso) del Application Layer.

Los Use Cases representan las operaciones de negocio que la aplicación
puede realizar. Cada Use Case encapsula una funcionalidad completa
del sistema.

Características:
- Independientes de la UI (pueden usarse desde API, CLI, GUI, etc.)
- Independientes de la infraestructura (usan interfaces, no implementaciones)
- Testeable fácilmente (inyección de dependencias)
- Orquestan el flujo de negocio
- Coordinan Entities y Repositories

Principios SOLID aplicados:
- Single Responsibility: Cada Use Case hace una cosa
- Open/Closed: Extensibles sin modificar código existente
- Liskov Substitution: Funcionan con cualquier implementación de interfaces
- Interface Segregation: Dependen solo de interfaces necesarias
- Dependency Inversion: Dependen de abstracciones, no implementaciones

Use Cases disponibles:
- CreateInvoiceUseCase: Crear nueva factura
- GetInvoiceUseCase: Obtener factura por ID
- UpdateInvoiceUseCase: Actualizar factura existente
- DeleteInvoiceUseCase: Eliminar factura (soft delete)
- ApproveInvoiceUseCase: Aprobar factura procesada
- ProcessOCRUseCase: Procesar OCR de factura (con soporte Donut)

Uso:
    >>> from src.application.use_cases import GetInvoiceUseCase, GetInvoiceInput
    >>> from src.infrastructure.repositories import InvoiceRepository
    >>>
    >>> # Setup
    >>> repository = InvoiceRepository(session)
    >>> use_case = GetInvoiceUseCase(invoice_repository=repository)
    >>>
    >>> # Ejecutar
    >>> input_dto = GetInvoiceInput(invoice_id=123)
    >>> invoice = await use_case.execute(input_dto)
==============================================================================
"""

# Import Use Cases
from src.application.use_cases.create_invoice_use_case import (
    CreateInvoiceUseCase,
    CreateInvoiceInput,
)
from src.application.use_cases.get_invoice_use_case import (
    GetInvoiceUseCase,
    GetInvoiceInput,
    GetInvoiceWithItemsUseCase,
    GetInvoiceBySeriesUseCase,
)
from src.application.use_cases.update_invoice_use_case import (
    UpdateInvoiceUseCase,
    UpdateInvoiceInput,
    UpdateInvoiceItemsUseCase,
    UpdateInvoiceNotesUseCase,
)
from src.application.use_cases.delete_invoice_use_case import (
    DeleteInvoiceUseCase,
    DeleteInvoiceInput,
    RestoreInvoiceUseCase,
)
from src.application.use_cases.approve_invoice_use_case import (
    ApproveInvoiceUseCase,
    ApproveInvoiceInput,
    BatchApproveInvoicesUseCase,
)
from src.application.use_cases.process_ocr_use_case import (
    ProcessOCRUseCase,
    ProcessOCRInput,
    BatchProcessOCRUseCase,
)

# Export all
__all__ = [
    # Create
    "CreateInvoiceUseCase",
    "CreateInvoiceInput",
    # Get
    "GetInvoiceUseCase",
    "GetInvoiceInput",
    "GetInvoiceWithItemsUseCase",
    "GetInvoiceBySeriesUseCase",
    # Update
    "UpdateInvoiceUseCase",
    "UpdateInvoiceInput",
    "UpdateInvoiceItemsUseCase",
    "UpdateInvoiceNotesUseCase",
    # Delete
    "DeleteInvoiceUseCase",
    "DeleteInvoiceInput",
    "RestoreInvoiceUseCase",
    # Approve
    "ApproveInvoiceUseCase",
    "ApproveInvoiceInput",
    "BatchApproveInvoicesUseCase",
    # Process OCR
    "ProcessOCRUseCase",
    "ProcessOCRInput",
    "BatchProcessOCRUseCase",
]
