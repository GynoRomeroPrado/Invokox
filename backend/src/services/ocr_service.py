"""
==============================================================================
OCR SERVICE
==============================================================================
Servicio de procesamiento OCR para extracción de datos de facturas.

Engines soportados:
- PaddleOCR: OCR general, rápido, buena precisión
- Docling: Especializado en documentos estructurados
- Tesseract: OCR tradicional, bueno para textos limpios

El servicio:
- Auto-selecciona el mejor engine según configuración
- Maneja múltiples formatos (PDF, PNG, JPG, etc.)
- Extrae texto y estructura de documentos
- Calcula confidence score
- Procesa facturas con layout analysis

Uso:
    from src.services.ocr_service import OCRService, OCRResult

    service = OCRService()
    result = service.process_invoice("path/to/invoice.pdf")

    print(result.text)
    print(result.confidence)
    print(result.structured_data)
==============================================================================
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.infrastructure.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ==============================================================================
# DATA CLASSES
# ==============================================================================


@dataclass
class OCRResult:
    """
    Resultado de procesamiento OCR.

    Attributes:
        text: Texto extraído completo
        confidence: Score de confianza (0-1)
        processing_time: Tiempo de procesamiento en segundos
        structured_data: Datos estructurados extraídos (dict)
        engine: Engine utilizado
        language: Idioma detectado
        page_count: Número de páginas procesadas
        errors: Lista de errores encontrados
    """

    text: str
    confidence: float
    processing_time: float
    structured_data: Dict[str, Any]
    engine: str
    language: str = "es"
    page_count: int = 1
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class InvoiceData:
    """
    Datos estructurados de una factura extraídos por OCR.

    Attributes:
        series: Serie de la factura (ej: F001)
        folio_number: Número de folio (ej: 00123456)
        issue_date: Fecha de emisión
        issuer_name: Nombre del emisor
        issuer_tax_id: RUC/RFC del emisor
        receiver_name: Nombre del receptor
        receiver_tax_id: RUC/RFC del receptor
        subtotal: Subtotal sin impuestos
        tax_amount: Monto de impuestos
        total_amount: Total a pagar
        currency: Moneda (PEN, USD, MXN, etc.)
        items: Lista de items/líneas
        raw_text: Texto original extraído
        confidence: Confianza general de la extracción
    """

    series: Optional[str] = None
    folio_number: Optional[str] = None
    issue_date: Optional[str] = None
    issuer_name: Optional[str] = None
    issuer_tax_id: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_tax_id: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "PEN"
    items: List[Dict[str, Any]] = None
    raw_text: str = ""
    confidence: float = 0.0

    def __post_init__(self):
        if self.items is None:
            self.items = []


# ==============================================================================
# OCR SERVICE
# ==============================================================================


class OCRService:
    """
    Servicio de procesamiento OCR para facturas.

    Maneja múltiples engines de OCR y extrae datos estructurados
    de facturas en diversos formatos.

    Example:
        >>> service = OCRService()
        >>> result = service.process_invoice("invoice.pdf")
        >>> print(f"Confidence: {result.confidence:.2f}")
        >>> print(f"Total: {result.structured_data.get('total_amount')}")
    """

    def __init__(self, engine: Optional[str] = None):
        """
        Inicializar servicio OCR.

        Args:
            engine: Engine a usar ('paddleocr', 'docling', 'tesseract').
                   Si es None, usa el configurado en settings.
        """
        self.engine = engine or settings.ocr_engine
        self.use_gpu = settings.use_gpu
        self.logger = logger

        self.logger.info(f"Initializing OCR service with engine: {self.engine}")

        # Lazy loading de engines (no importar si no se usa)
        self._ocr_instance = None

    def _get_ocr_instance(self):
        """
        Lazy loading del engine OCR.

        Importa y configura el engine solo cuando se necesita
        para evitar dependencias innecesarias.

        Returns:
            Instance del OCR engine configurado.

        Raises:
            ImportError: Si el engine no está disponible.
            ValueError: Si el engine no es válido.
        """
        if self._ocr_instance is not None:
            return self._ocr_instance

        if self.engine == "paddleocr":
            try:
                from paddleocr import PaddleOCR

                self._ocr_instance = PaddleOCR(
                    use_angle_cls=True,
                    lang="es",  # Español
                    use_gpu=self.use_gpu,
                    show_log=False,
                )
                self.logger.info("PaddleOCR initialized successfully")
                return self._ocr_instance

            except ImportError:
                self.logger.error("PaddleOCR not installed")
                raise ImportError(
                    "PaddleOCR not installed. Install with: pip install paddleocr"
                )

        elif self.engine == "docling":
            try:
                # TODO: Implementar Docling cuando esté disponible
                self.logger.warning("Docling engine not yet implemented, falling back to PaddleOCR")
                self.engine = "paddleocr"
                return self._get_ocr_instance()

            except ImportError:
                self.logger.error("Docling not installed")
                raise ImportError("Docling not installed. Install with: pip install docling")

        elif self.engine == "tesseract":
            try:
                import pytesseract

                # Verificar que tesseract esté instalado
                pytesseract.get_tesseract_version()
                self._ocr_instance = pytesseract
                self.logger.info("Tesseract initialized successfully")
                return self._ocr_instance

            except Exception as e:
                self.logger.error(f"Tesseract not available: {e}")
                raise ImportError(
                    "Tesseract not installed. Install with: apt-get install tesseract-ocr"
                )

        else:
            raise ValueError(f"Unknown OCR engine: {self.engine}")

    def process_invoice(self, file_path: str | Path) -> OCRResult:
        """
        Procesar factura con OCR.

        Args:
            file_path: Ruta al archivo de factura (PDF, imagen, etc.)

        Returns:
            OCRResult con texto extraído y datos estructurados.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el formato no es soportado.

        Example:
            >>> service = OCRService()
            >>> result = service.process_invoice("factura.pdf")
            >>> print(result.text)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.info(f"Processing invoice: {file_path}")
        start_time = time.time()

        # Determinar tipo de archivo
        file_ext = file_path.suffix.lower()

        try:
            if file_ext == ".pdf":
                result = self._process_pdf(file_path)
            elif file_ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                result = self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            processing_time = time.time() - start_time
            result.processing_time = processing_time

            self.logger.info(
                f"OCR completed in {processing_time:.2f}s "
                f"with confidence {result.confidence:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error processing invoice: {e}", exc_info=True)
            raise

    def _process_pdf(self, file_path: Path) -> OCRResult:
        """
        Procesar archivo PDF.

        Args:
            file_path: Ruta al PDF

        Returns:
            OCRResult con datos extraídos
        """
        try:
            from pdf2image import convert_from_path

            # Convertir PDF a imágenes
            images = convert_from_path(str(file_path))
            self.logger.info(f"PDF converted to {len(images)} images")

            all_text = []
            confidences = []

            # Procesar cada página
            for i, image in enumerate(images):
                self.logger.debug(f"Processing page {i+1}/{len(images)}")
                page_result = self._ocr_image(image)
                all_text.append(page_result[0])
                confidences.append(page_result[1])

            # Combinar resultados
            full_text = "\n\n--- PAGE BREAK ---\n\n".join(all_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Extraer datos estructurados
            invoice_data = self._extract_invoice_data(full_text)

            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                processing_time=0.0,  # Se setea en process_invoice
                structured_data=invoice_data.__dict__,
                engine=self.engine,
                language="es",
                page_count=len(images),
            )

        except ImportError:
            self.logger.error("pdf2image not installed")
            raise ImportError(
                "pdf2image not installed. Install with: pip install pdf2image"
            )

    def _process_image(self, file_path: Path) -> OCRResult:
        """
        Procesar archivo de imagen.

        Args:
            file_path: Ruta a la imagen

        Returns:
            OCRResult con datos extraídos
        """
        from PIL import Image

        image = Image.open(file_path)
        text, confidence = self._ocr_image(image)

        # Extraer datos estructurados
        invoice_data = self._extract_invoice_data(text)

        return OCRResult(
            text=text,
            confidence=confidence,
            processing_time=0.0,  # Se setea en process_invoice
            structured_data=invoice_data.__dict__,
            engine=self.engine,
            language="es",
            page_count=1,
        )

    def _ocr_image(self, image) -> Tuple[str, float]:
        """
        Ejecutar OCR en una imagen.

        Args:
            image: PIL Image o numpy array

        Returns:
            Tuple de (texto_extraído, confidence_score)
        """
        ocr_instance = self._get_ocr_instance()

        if self.engine == "paddleocr":
            import numpy as np

            # Convertir PIL Image a numpy array si es necesario
            if not isinstance(image, np.ndarray):
                image = np.array(image)

            result = ocr_instance.ocr(image, cls=True)

            if not result or not result[0]:
                return "", 0.0

            # Extraer texto y confidences
            texts = []
            confidences = []

            for line in result[0]:
                if line[1][0]:  # Text
                    texts.append(line[1][0])
                if line[1][1]:  # Confidence
                    confidences.append(line[1][1])

            text = "\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return text, avg_confidence

        elif self.engine == "tesseract":
            import pytesseract

            # Obtener texto
            text = pytesseract.image_to_string(image, lang="spa")

            # Obtener confidence (Tesseract devuelve por palabra)
            data = pytesseract.image_to_data(image, lang="spa", output_type=pytesseract.Output.DICT)
            confidences = [float(c) for c in data["conf"] if c != "-1"]
            avg_confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0

            return text, avg_confidence

        else:
            raise ValueError(f"Engine {self.engine} not implemented")

    def _extract_invoice_data(self, text: str) -> InvoiceData:
        """
        Extraer datos estructurados de factura del texto OCR.

        Usa expresiones regulares y pattern matching para identificar:
        - Serie y folio
        - RUC/RFC
        - Fechas
        - Montos
        - Nombres de empresas

        Args:
            text: Texto extraído por OCR

        Returns:
            InvoiceData con campos extraídos

        TODO: Implementar ML model para mejor extracción
        """
        import re
        from datetime import datetime

        invoice_data = InvoiceData(raw_text=text)

        # =================================================================
        # EXTRAER SERIE Y FOLIO
        # =================================================================
        # Patrones comunes: F001-00123456, E001-456, etc.
        series_pattern = r"([A-Z]\d{3})-?(\d+)"
        series_match = re.search(series_pattern, text)
        if series_match:
            invoice_data.series = series_match.group(1)
            invoice_data.folio_number = series_match.group(2)

        # =================================================================
        # EXTRAER RUC (Perú) - 11 dígitos
        # =================================================================
        ruc_pattern = r"\b(\d{11})\b"
        ruc_matches = re.findall(ruc_pattern, text)
        if len(ruc_matches) >= 2:
            invoice_data.issuer_tax_id = ruc_matches[0]
            invoice_data.receiver_tax_id = ruc_matches[1]
        elif len(ruc_matches) == 1:
            invoice_data.issuer_tax_id = ruc_matches[0]

        # =================================================================
        # EXTRAER FECHAS
        # =================================================================
        # Patrones: DD/MM/YYYY, DD-MM-YYYY
        date_pattern = r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b"
        date_match = re.search(date_pattern, text)
        if date_match:
            try:
                day, month, year = date_match.groups()
                invoice_data.issue_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            except ValueError:
                pass

        # =================================================================
        # EXTRAER MONTOS
        # =================================================================
        # Buscar TOTAL, SUBTOTAL, IGV, etc.
        amount_patterns = {
            "total_amount": r"TOTAL\s*:?\s*[S/\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            "subtotal": r"(?:SUB\s*)?TOTAL\s*:?\s*[S/\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            "tax_amount": r"(?:IGV|IVA|TAX)\s*:?\s*[S/\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        }

        for field, pattern in amount_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    setattr(invoice_data, field, float(amount_str))
                except ValueError:
                    pass

        # =================================================================
        # DETECTAR MONEDA
        # =================================================================
        if "S/" in text or "PEN" in text or "SOLES" in text:
            invoice_data.currency = "PEN"
        elif "USD" in text or "US$" in text or "DOLARES" in text:
            invoice_data.currency = "USD"
        elif "MXN" in text or "PESOS" in text:
            invoice_data.currency = "MXN"

        # =================================================================
        # CALCULAR CONFIDENCE
        # =================================================================
        # Score basado en campos extraídos
        fields_found = 0
        total_fields = 10

        if invoice_data.series:
            fields_found += 1
        if invoice_data.folio_number:
            fields_found += 1
        if invoice_data.issue_date:
            fields_found += 1
        if invoice_data.issuer_tax_id:
            fields_found += 1
        if invoice_data.receiver_tax_id:
            fields_found += 1
        if invoice_data.subtotal:
            fields_found += 1
        if invoice_data.tax_amount:
            fields_found += 1
        if invoice_data.total_amount:
            fields_found += 1
        if invoice_data.currency:
            fields_found += 1
        if len(text) > 50:  # Texto extraído razonablemente largo
            fields_found += 1

        invoice_data.confidence = fields_found / total_fields

        return invoice_data


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def create_ocr_service(engine: Optional[str] = None) -> OCRService:
    """
    Factory function para crear OCR service.

    Args:
        engine: Engine a usar (opcional)

    Returns:
        OCRService instance

    Example:
        >>> service = create_ocr_service("paddleocr")
        >>> result = service.process_invoice("invoice.pdf")
    """
    return OCRService(engine=engine)
