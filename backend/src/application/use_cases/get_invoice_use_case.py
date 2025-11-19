"""
==============================================================================
USE CASE: GET INVOICE
==============================================================================
Caso de uso para obtener una factura por su ID.

Este Use Case encapsula la lógica para recuperar una factura específica
con toda su información relacionada (items, empresas, etc.).

Responsabilidades:
- Validar que el ID sea válido
- Recuperar la factura del repositorio
- Manejar el caso de factura no encontrada
- Retornar la factura completa con sus relaciones

Flujo:
1. Validar input (ID no nulo, > 0)
2. Buscar factura en repositorio
3. Si no existe, lanzar excepción
4. Si existe, retornar factura completa

Patrón: Command Query Responsibility Segregation (CQRS) - Query side
==============================================================================
"""

from typing import Optional

from src.domain.entities.invoice import Invoice
from src.application.interfaces.repository_interface import IInvoiceRepository


# ==============================================================================
# INPUT DTO
# ==============================================================================


class GetInvoiceInput:
    """
    Data Transfer Object (DTO) de entrada para obtener una factura.

    DTOs separan la capa de aplicación de la capa de presentación,
    permitiendo cambiar la API sin afectar la lógica de negocio.

    Attributes:
        invoice_id: ID único de la factura a recuperar (int > 0)

    Example:
        >>> input_dto = GetInvoiceInput(invoice_id=123)
        >>> use_case = GetInvoiceUseCase(invoice_repository)
        >>> invoice = await use_case.execute(input_dto)
    """

    def __init__(self, invoice_id: int):
        """
        Inicializar DTO de entrada.

        Args:
            invoice_id: ID de la factura (debe ser > 0)

        Raises:
            ValueError: Si el ID es inválido (None, <= 0)
        """
        # Validación de entrada en el DTO
        # Esto previene que lógica de validación se esparza por todo el código
        if invoice_id is None:
            raise ValueError("Invoice ID cannot be None")
        if invoice_id <= 0:
            raise ValueError(f"Invoice ID must be positive, got: {invoice_id}")

        self.invoice_id = invoice_id


# ==============================================================================
# OUTPUT DTO (OPCIONAL)
# ==============================================================================
# En este caso, retornamos directamente la Entity Invoice.
# Si necesitáramos serialización específica para la capa de presentación,
# crearíamos un GetInvoiceOutput DTO aquí.
#
# class GetInvoiceOutput:
#     def __init__(self, invoice: Invoice):
#         self.id = invoice.id
#         self.series = invoice.series
#         self.total = invoice.total_amount
#         # ... más campos para serialización
# ==============================================================================


# ==============================================================================
# USE CASE
# ==============================================================================


class GetInvoiceUseCase:
    """
    Use Case: Obtener una factura por ID.

    Este Use Case implementa el patrón Repository para abstraer
    el acceso a datos y mantener la lógica de negocio independiente
    de los detalles de persistencia.

    Principios SOLID aplicados:
    - Single Responsibility: Solo se encarga de obtener una factura
    - Open/Closed: Abierto a extensión (decorators), cerrado a modificación
    - Liskov Substitution: Funciona con cualquier IInvoiceRepository
    - Interface Segregation: Depende solo de la interfaz necesaria
    - Dependency Inversion: Depende de abstracción (IInvoiceRepository)

    Attributes:
        invoice_repo: Repositorio de facturas (interfaz, no implementación)

    Example:
        >>> # Setup
        >>> repository = InvoiceRepository(session)
        >>> use_case = GetInvoiceUseCase(invoice_repository=repository)
        >>>
        >>> # Ejecución
        >>> input_dto = GetInvoiceInput(invoice_id=123)
        >>> invoice = await use_case.execute(input_dto)
        >>>
        >>> # Uso
        >>> print(f"Invoice: {invoice.series}")
        >>> print(f"Total: {invoice.total_amount}")
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """
        Inicializar Use Case con dependencias.

        Dependency Injection: El repositorio se inyecta desde fuera,
        permitiendo testing fácil con mocks y flexibilidad en runtime.

        Args:
            invoice_repository: Implementación de IInvoiceRepository
                               (puede ser real, mock, fake, etc.)
        """
        self.invoice_repo = invoice_repository

    async def execute(self, input_data: GetInvoiceInput) -> Invoice:
        """
        Ejecutar el caso de uso.

        Este método es async para soportar repositorios asíncronos,
        lo cual es importante para escalabilidad en aplicaciones
        con muchas consultas concurrentes.

        Args:
            input_data: DTO con el ID de la factura a buscar

        Returns:
            Invoice: Entidad de factura completa con todos sus datos

        Raises:
            ValueError: Si la factura no existe en el sistema
            RepositoryError: Si hay error en la capa de persistencia

        Flow:
            1. Extraer invoice_id del input DTO
            2. Llamar al repositorio para buscar la factura
            3. Validar que se encontró la factura
            4. Retornar la factura encontrada

        Example:
            >>> input_dto = GetInvoiceInput(invoice_id=123)
            >>> invoice = await use_case.execute(input_dto)
            >>> assert invoice.id == 123
            >>> assert invoice.series is not None

        Note:
            Este método NO realiza transformaciones de datos.
            Retorna la entidad del dominio tal cual está en el repositorio.
            Si necesitas serialización específica, crea un Output DTO.
        """
        # =================================================================
        # PASO 1: Extraer datos del input DTO
        # =================================================================
        # El DTO ya validó que el ID es válido en su constructor
        invoice_id = input_data.invoice_id

        # =================================================================
        # PASO 2: Buscar factura en el repositorio
        # =================================================================
        # Llamada asíncrona al repositorio
        # El repositorio se encarga de:
        # - Crear query/SQL
        # - Ejecutar contra la base de datos
        # - Mapear resultado a Entity
        # - Manejar errores de conexión
        invoice = await self.invoice_repo.get_by_id(invoice_id)

        # =================================================================
        # PASO 3: Validar resultado
        # =================================================================
        # Si el repositorio retorna None, significa que no existe
        if invoice is None:
            # Lanzar excepción específica de dominio
            # Esto permite a capas superiores manejar el error apropiadamente
            raise ValueError(
                f"Invoice with ID {invoice_id} not found. "
                f"The invoice may have been deleted or never existed."
            )

        # =================================================================
        # PASO 4: Retornar resultado
        # =================================================================
        # Retornar la entidad completa
        # La entidad ya tiene todos sus datos cargados por el repositorio:
        # - Información básica
        # - Items de factura
        # - Información de empresas
        # - Totales calculados
        return invoice


# ==============================================================================
# USE CASE VARIANTS (OPCIONAL)
# ==============================================================================


class GetInvoiceWithItemsUseCase(GetInvoiceUseCase):
    """
    Variante del Use Case que garantiza cargar los items.

    Algunos repositorios pueden implementar lazy loading.
    Esta variante asegura que los items estén cargados.

    Esta es una especialización del Use Case base usando herencia.
    """

    async def execute(self, input_data: GetInvoiceInput) -> Invoice:
        """
        Ejecutar obteniendo factura con items garantizados.

        Returns:
            Invoice con items cargados explícitamente
        """
        # Llamar al Use Case padre
        invoice = await super().execute(input_data)

        # Asegurar que items están cargados
        # (esto depende de la implementación del repositorio)
        if not hasattr(invoice, "items") or invoice.items is None:
            # Recargar con items explícitamente
            invoice = await self.invoice_repo.get_by_id_with_items(
                input_data.invoice_id
            )

        return invoice


class GetInvoiceBySeriesUseCase:
    """
    Use Case alternativo: Obtener factura por serie en lugar de ID.

    La serie (ej: F001-00000001) es un identificador de negocio único,
    mientras que el ID es un identificador técnico.

    En muchos casos, los usuarios solo conocen la serie, no el ID interno.

    Example:
        >>> input_dto = GetInvoiceBySeriesInput(series="F001-00000001")
        >>> use_case = GetInvoiceBySeriesUseCase(invoice_repository)
        >>> invoice = await use_case.execute(input_dto)
    """

    def __init__(self, invoice_repository: IInvoiceRepository):
        """Inicializar con repositorio."""
        self.invoice_repo = invoice_repository

    async def execute(self, series: str) -> Invoice:
        """
        Buscar factura por serie.

        Args:
            series: Serie de la factura (ej: "F001-00000001")

        Returns:
            Invoice encontrada

        Raises:
            ValueError: Si la serie no existe
        """
        # Validar serie
        if not series or not series.strip():
            raise ValueError("Series cannot be empty")

        # Buscar por serie
        invoice = await self.invoice_repo.get_by_series(series)

        # Validar resultado
        if invoice is None:
            raise ValueError(f"Invoice with series '{series}' not found")

        return invoice


# ==============================================================================
# HELPER FUNCTIONS (OPCIONAL)
# ==============================================================================


def validate_invoice_access(invoice: Invoice, user_id: str) -> bool:
    """
    Helper para validar si un usuario tiene acceso a una factura.

    Esta función puede ser usada por el Use Case para implementar
    control de acceso básico.

    Args:
        invoice: Factura a validar
        user_id: ID del usuario que intenta acceder

    Returns:
        True si tiene acceso, False si no

    Example:
        >>> invoice = await use_case.execute(input_dto)
        >>> if not validate_invoice_access(invoice, current_user.id):
        >>>     raise PermissionError("No tienes acceso a esta factura")
    """
    # Lógica de validación de acceso
    # Ejemplos:
    # - Usuario es el creador
    # - Usuario pertenece a la empresa emisora
    # - Usuario tiene rol de administrador
    # - etc.

    # Por ahora, retornar True (sin restricciones)
    # En producción, implementar lógica real de permisos
    return True
