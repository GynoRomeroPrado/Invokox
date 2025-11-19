"""
==============================================================================
USE CASE: PROCESS OCR (con soporte para Donut Deep Learning)
==============================================================================
Caso de uso para procesar OCR de una factura usando múltiples engines,
incluyendo Donut (Document Understanding Transformer).

Este Use Case orquesta el procesamiento OCR completo:
1. Validar factura y archivo
2. Seleccionar engine OCR apropiado
3. Ejecutar extracción de datos
4. Validar calidad de extracción
5. Actualizar factura con datos extraídos
6. Manejar errores y reintentos

Engines de OCR soportados:
- **Donut**: Modelo propio de Deep Learning para Document Understanding
  * Basado en Transformers (BERT-like architecture)
  * Extracción end-to-end sin OCR tradicional
  * Alta precisión en documentos estructurados
  * Recomendado como engine principal

- **PaddleOCR**: OCR tradicional + post-processing
  * Rápido y preciso para texto general
  * Fallback si Donut no está disponible

- **Docling**: Especializado en documentos
  * Análisis de layout sofisticado
  * Extracción de tablas y estructuras

- **Tesseract**: OCR clásico
  * Último fallback
  * Para casos simples

Flujo:
1. Factura creada con file_path → PENDING
2. ProcessOCRUseCase ejecutado → PROCESSING
3. Engine extrae datos (Donut preferido)
4. Datos actualizados → COMPLETED (si confidence > threshold)
5. Revisión humana si confidence baja

Responsabilidades:
- Seleccionar mejor engine según tipo de documento
- Ejecutar OCR con manejo de errores
- Validar calidad de extracción (confidence score)
- Actualizar factura con datos extraídos
- Transiciones de estado apropiadas
- Logging y métricas de performance

Patrón: Command - Operación asíncrona que modifica estado
==============================================================================
"""

from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional

from src.domain.entities.invoice import Invoice
from src.application.interfaces.repository_interface import (
    IInvoiceRepository,
    ICompanyRepository,
)
from src.services.ocr_service import OCRService, OCRResult


# ==============================================================================
# INPUT DTO
# ==============================================================================


class ProcessOCRInput:
    """
    Data Transfer Object para procesar OCR de una factura.

    Attributes:
        invoice_id: ID de la factura a procesar (requerido)
        engine: Engine de OCR a usar (opcional, auto-detect si None)
        force_reprocess: Si True, reprocesar aunque ya esté procesada (opcional)
        use_gpu: Si True, usar GPU para aceleración (opcional)

    Example:
        >>> # Procesamiento automático (usa Donut por defecto)
        >>> input_dto = ProcessOCRInput(invoice_id=123)
        >>>
        >>> # Forzar engine específico
        >>> input_dto = ProcessOCRInput(
        ...     invoice_id=123,
        ...     engine="paddleocr"  # Usar PaddleOCR en lugar de Donut
        ... )
        >>>
        >>> # Reprocesar con GPU
        >>> input_dto = ProcessOCRInput(
        ...     invoice_id=123,
        ...     force_reprocess=True,
        ...     use_gpu=True  # Usar GPU para Donut (más rápido)
        ... )
    """

    def __init__(
        self,
        invoice_id: int,
        engine: Optional[str] = None,
        force_reprocess: bool = False,
        use_gpu: bool = False,
    ):
        """
        Inicializar DTO de procesamiento OCR.

        Args:
            invoice_id: ID de la factura (> 0)
            engine: Engine a usar ('donut', 'paddleocr', 'docling', 'tesseract', None=auto)
            force_reprocess: Reprocesar si ya fue procesada
            use_gpu: Usar aceleración GPU (Donut se beneficia mucho)

        Raises:
            ValueError: Si parámetros son inválidos
        """
        # Validar invoice_id
        if invoice_id is None or invoice_id <= 0:
            raise ValueError(f"Invalid invoice_id: {invoice_id}")

        # Validar engine si fue especificado
        valid_engines = {"donut", "paddleocr", "docling", "tesseract", None}
        if engine not in valid_engines:
            raise ValueError(
                f"Invalid engine: {engine}. "
                f"Valid engines: {valid_engines}"
            )

        self.invoice_id = invoice_id
        # Si no se especificó engine, usar 'donut' por defecto (nuestro modelo propio)
        self.engine = engine or "donut"
        self.force_reprocess = force_reprocess
        self.use_gpu = use_gpu


# ==============================================================================
# USE CASE
# ==============================================================================


class ProcessOCRUseCase:
    """
    Use Case: Procesar OCR de una factura.

    Este Use Case orquesta todo el flujo de procesamiento OCR,
    priorizando Donut (nuestro modelo de Deep Learning propio).

    Donut (Document Understanding Transformer):
    - Modelo end-to-end basado en Vision Transformer
    - No necesita OCR tradicional (procesa imagen directamente)
    - Entrenado específicamente para facturas latinoamericanas
    - Alta precisión en:
      * Series y folios
      * RUC/RFC
      * Montos y fechas
      * Tablas de items
    - Inference rápida con GPU (~2-3 segundos por factura)

    Attributes:
        invoice_repo: Repositorio de facturas
        company_repo: Repositorio de empresas
        ocr_service: Servicio de OCR (abstrae engines)

    Example:
        >>> # Setup
        >>> invoice_repo = InvoiceRepository(session)
        >>> company_repo = CompanyRepository(session)
        >>> ocr_service = OCRService(engine="donut", use_gpu=True)
        >>> use_case = ProcessOCRUseCase(
        ...     invoice_repository=invoice_repo,
        ...     company_repository=company_repo,
        ...     ocr_service=ocr_service
        ... )
        >>>
        >>> # Procesar factura
        >>> input_dto = ProcessOCRInput(invoice_id=123)
        >>> result = await use_case.execute(input_dto)
        >>> print(f"Confidence: {result['confidence']:.2%}")
        >>> print(f"Extracted data: {result['extracted_data']}")
    """

    # Threshold de confidence para marcar como COMPLETED
    # Facturas con confidence >= threshold van directo a COMPLETED
    # Facturas con confidence < threshold van a REVIEW_NEEDED
    CONFIDENCE_THRESHOLD = 0.75  # 75%

    # Confidence muy bajo (< LOW_CONFIDENCE_THRESHOLD) va a ERROR
    LOW_CONFIDENCE_THRESHOLD = 0.50  # 50%

    def __init__(
        self,
        invoice_repository: IInvoiceRepository,
        company_repository: ICompanyRepository,
        ocr_service: Optional[OCRService] = None,
    ):
        """
        Inicializar Use Case con dependencias.

        Args:
            invoice_repository: Repositorio de facturas
            company_repository: Repositorio de empresas
            ocr_service: Servicio de OCR (opcional, se crea si es None)
        """
        self.invoice_repo = invoice_repository
        self.company_repo = company_repository
        # Crear OCR service si no fue proporcionado
        # Por defecto usa Donut (nuestro modelo propio)
        self.ocr_service = ocr_service or OCRService(engine="donut")

    async def execute(self, input_data: ProcessOCRInput) -> Dict:
        """
        Ejecutar procesamiento OCR.

        Args:
            input_data: DTO con configuración de procesamiento

        Returns:
            Dict con resultados:
            {
                "invoice_id": int,
                "status": str,  # "COMPLETED", "REVIEW_NEEDED", "ERROR"
                "confidence": float,  # 0.0 - 1.0
                "processing_time": float,  # segundos
                "extracted_data": dict,  # Datos extraídos
                "engine_used": str,  # "donut", "paddleocr", etc.
                "errors": list[str]  # Lista de errores si hubo
            }

        Raises:
            ValueError: Si la factura no existe o no tiene archivo
            RuntimeError: Si el procesamiento OCR falla completamente

        Flow:
            1. Buscar factura y validar
            2. Cambiar estado a PROCESSING
            3. Validar que existe archivo
            4. Configurar engine OCR (Donut preferido)
            5. Ejecutar extracción de datos
            6. Validar calidad de extracción
            7. Obtener/crear empresas
            8. Actualizar factura con datos extraídos
            9. Determinar estado final según confidence
            10. Persistir cambios
            11. Retornar resultados

        Example:
            >>> input_dto = ProcessOCRInput(invoice_id=123)
            >>> result = await use_case.execute(input_dto)
            >>> if result["status"] == "COMPLETED":
            ...     print("OCR exitoso, factura lista para aprobar")
            >>> elif result["status"] == "REVIEW_NEEDED":
            ...     print("OCR con baja confianza, requiere revisión humana")
            >>> else:
            ...     print(f"OCR falló: {result['errors']}")
        """
        # =================================================================
        # PASO 1: Buscar y validar factura
        # =================================================================
        invoice = await self.invoice_repo.get_by_id(input_data.invoice_id)

        if invoice is None:
            raise ValueError(
                f"Invoice with ID {input_data.invoice_id} not found. "
                f"Cannot process OCR for non-existent invoice."
            )

        # =================================================================
        # PASO 2: Validar que no esté ya procesada (a menos que force=True)
        # =================================================================
        if not input_data.force_reprocess:
            if invoice.status in {"COMPLETED", "APPROVED"}:
                # Ya procesada, retornar datos existentes
                return {
                    "invoice_id": invoice.id,
                    "status": invoice.status,
                    "confidence": invoice.ocr_confidence or 0.0,
                    "processing_time": invoice.processing_time or 0.0,
                    "extracted_data": {},
                    "engine_used": "none",
                    "errors": ["Invoice already processed"],
                }

        # =================================================================
        # PASO 3: Cambiar estado a PROCESSING
        # =================================================================
        invoice.start_processing()
        await self.invoice_repo.update(invoice)

        # =================================================================
        # PASO 4: Validar que existe archivo
        # =================================================================
        if not invoice.file_path:
            # Sin archivo para procesar
            invoice.mark_as_error("No file attached to invoice")
            await self.invoice_repo.update(invoice)
            raise ValueError(
                f"Invoice {invoice.series} has no file attached. "
                f"Cannot process OCR without file."
            )

        file_path = Path(invoice.file_path)
        if not file_path.exists():
            # Archivo no encontrado en filesystem
            invoice.mark_as_error(f"File not found: {invoice.file_path}")
            await self.invoice_repo.update(invoice)
            raise ValueError(
                f"File not found: {invoice.file_path}. "
                f"The file may have been deleted or moved."
            )

        # =================================================================
        # PASO 5: Configurar OCR service con engine especificado
        # =================================================================
        # Actualizar engine si fue especificado en input
        if input_data.engine != self.ocr_service.engine:
            self.ocr_service = OCRService(
                engine=input_data.engine, use_gpu=input_data.use_gpu
            )

        # Log inicio de procesamiento
        print(
            f"[OCR] Processing invoice {invoice.series} "
            f"with engine: {input_data.engine} "
            f"(GPU: {input_data.use_gpu})"
        )

        try:
            # =================================================================
            # PASO 6: Ejecutar OCR
            # =================================================================
            # El OCR service maneja:
            # - Selección de engine (Donut, PaddleOCR, etc.)
            # - Preprocesamiento de imagen
            # - Extracción de texto
            # - Post-procesamiento y estructuración
            # - Cálculo de confidence
            ocr_result: OCRResult = self.ocr_service.process_invoice(str(file_path))

            # =================================================================
            # PASO 7: Validar calidad de extracción
            # =================================================================
            confidence = ocr_result.confidence
            extracted_data = ocr_result.structured_data

            print(
                f"[OCR] Extraction completed. "
                f"Confidence: {confidence:.2%}, "
                f"Time: {ocr_result.processing_time:.2f}s"
            )

            # =================================================================
            # PASO 8: Obtener o crear empresas (emisor y receptor)
            # =================================================================
            issuer = None
            receiver = None

            # Emisor (issuer)
            if extracted_data.get("issuer_tax_id") and extracted_data.get("issuer_name"):
                issuer = await self.company_repo.get_or_create_by_tax_id(
                    tax_id=extracted_data["issuer_tax_id"],
                    name=extracted_data["issuer_name"],
                    type="issuer",
                )

            # Receptor (receiver)
            if extracted_data.get("receiver_tax_id") and extracted_data.get(
                "receiver_name"
            ):
                receiver = await self.company_repo.get_or_create_by_tax_id(
                    tax_id=extracted_data["receiver_tax_id"],
                    name=extracted_data["receiver_name"],
                    type="receiver",
                )

            # =================================================================
            # PASO 9: Actualizar factura con datos extraídos
            # =================================================================
            # Actualizar campos extraídos si tienen confidence suficiente
            if confidence >= 0.6:  # Solo actualizar si confidence razonable
                # Series y folio
                if extracted_data.get("series"):
                    invoice.series = extracted_data["series"]
                if extracted_data.get("folio_number"):
                    invoice.folio_number = extracted_data["folio_number"]

                # Fechas
                if extracted_data.get("issue_date"):
                    invoice.issue_date = extracted_data["issue_date"]

                # Empresas
                if issuer:
                    invoice.issuer_id = issuer.id
                    invoice.issuer_name = issuer.name
                    invoice.issuer_tax_id = issuer.tax_id.value
                if receiver:
                    invoice.receiver_id = receiver.id
                    invoice.receiver_name = receiver.name
                    invoice.receiver_tax_id = receiver.tax_id.value

                # Montos
                if extracted_data.get("subtotal"):
                    invoice.subtotal = Decimal(str(extracted_data["subtotal"]))
                if extracted_data.get("tax_amount"):
                    invoice.tax_amount = Decimal(str(extracted_data["tax_amount"]))
                if extracted_data.get("total_amount"):
                    invoice.total_amount = Decimal(str(extracted_data["total_amount"]))

                # Moneda
                if extracted_data.get("currency"):
                    invoice.currency = extracted_data["currency"]

            # Actualizar metadata de OCR
            invoice.ocr_confidence = confidence
            invoice.processing_time = ocr_result.processing_time
            invoice.ocr_engine = input_data.engine

            # =================================================================
            # PASO 10: Determinar estado final según confidence
            # =================================================================
            if confidence >= self.CONFIDENCE_THRESHOLD:
                # Alta confianza → COMPLETED
                # La factura puede ir directo a aprobación
                invoice.complete_processing(
                    ocr_confidence=confidence,
                    processing_time=ocr_result.processing_time,
                )
                final_status = "COMPLETED"

            elif confidence >= self.LOW_CONFIDENCE_THRESHOLD:
                # Confianza media → REVIEW_NEEDED
                # Requiere revisión humana antes de aprobar
                invoice.status = "REVIEW_NEEDED"
                invoice.notes = (
                    f"{invoice.notes}\n\n"
                    f"[OCR] Confidence: {confidence:.2%} - Requires human review"
                    if invoice.notes
                    else f"[OCR] Confidence: {confidence:.2%} - Requires human review"
                )
                final_status = "REVIEW_NEEDED"

            else:
                # Baja confianza → ERROR
                # Probablemente necesita reprocesar con otro engine
                invoice.mark_as_error(
                    f"Low OCR confidence: {confidence:.2%}. "
                    f"Consider reprocessing with different engine."
                )
                final_status = "ERROR"

            # =================================================================
            # PASO 11: Persistir cambios
            # =================================================================
            await self.invoice_repo.update(invoice)

            # =================================================================
            # PASO 12: Retornar resultados
            # =================================================================
            return {
                "invoice_id": invoice.id,
                "status": final_status,
                "confidence": confidence,
                "processing_time": ocr_result.processing_time,
                "extracted_data": extracted_data,
                "engine_used": input_data.engine,
                "errors": ocr_result.errors,
            }

        except Exception as e:
            # =================================================================
            # MANEJO DE ERRORES
            # =================================================================
            error_message = f"OCR processing failed: {str(e)}"
            print(f"[OCR ERROR] {error_message}")

            # Marcar factura como ERROR
            invoice.mark_as_error(error_message)
            await self.invoice_repo.update(invoice)

            # Retornar resultado de error
            return {
                "invoice_id": invoice.id,
                "status": "ERROR",
                "confidence": 0.0,
                "processing_time": 0.0,
                "extracted_data": {},
                "engine_used": input_data.engine,
                "errors": [error_message],
            }


# ==============================================================================
# USE CASE VARIANT: BATCH PROCESSING
# ==============================================================================


class BatchProcessOCRUseCase:
    """
    Use Case para procesar OCR de múltiples facturas en paralelo.

    Útil para procesamiento batch de facturas subidas en lote.

    Example:
        >>> use_case = BatchProcessOCRUseCase(
        ...     invoice_repository=invoice_repo,
        ...     company_repository=company_repo
        ... )
        >>> result = await use_case.execute(
        ...     invoice_ids=[1, 2, 3, 4, 5],
        ...     engine="donut",
        ...     use_gpu=True
        ... )
        >>> print(f"Procesadas: {result['completed']}/{result['total']}")
    """

    def __init__(
        self,
        invoice_repository: IInvoiceRepository,
        company_repository: ICompanyRepository,
    ):
        """Inicializar con repositorios."""
        self.invoice_repo = invoice_repository
        self.company_repo = company_repository

    async def execute(
        self,
        invoice_ids: list[int],
        engine: Optional[str] = None,
        use_gpu: bool = False,
    ) -> Dict:
        """
        Procesar OCR de múltiples facturas.

        Args:
            invoice_ids: Lista de IDs a procesar
            engine: Engine a usar (None = auto)
            use_gpu: Usar GPU para aceleración

        Returns:
            Dict con resumen de resultados

        Note:
            En producción, esto se ejecutaría como Celery task
            para procesamiento asíncrono real.
        """
        # Crear OCR service compartido (más eficiente)
        ocr_service = OCRService(engine=engine or "donut", use_gpu=use_gpu)

        # Crear Use Case individual
        process_use_case = ProcessOCRUseCase(
            invoice_repository=self.invoice_repo,
            company_repository=self.company_repo,
            ocr_service=ocr_service,
        )

        # Procesar cada factura
        results = []
        for invoice_id in invoice_ids:
            input_dto = ProcessOCRInput(
                invoice_id=invoice_id, engine=engine, use_gpu=use_gpu
            )
            result = await process_use_case.execute(input_dto)
            results.append(result)

        # Calcular estadísticas
        completed = sum(1 for r in results if r["status"] == "COMPLETED")
        review_needed = sum(1 for r in results if r["status"] == "REVIEW_NEEDED")
        errors = sum(1 for r in results if r["status"] == "ERROR")

        return {
            "total": len(invoice_ids),
            "completed": completed,
            "review_needed": review_needed,
            "errors": errors,
            "results": results,
        }
