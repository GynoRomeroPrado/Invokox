"""
Repository Interfaces (Ports)

Define contratos para acceso a datos sin depender de implementaciones concretas.
Principio de Inversión de Dependencias (DIP).
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from src.domain.entities.invoice import Invoice
from src.domain.entities.company import Company


# Type variables para repositorios genéricos
T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Interfaz base genérica para todos los repositorios.

    Define operaciones CRUD básicas.
    """

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene una entidad por su ID."""
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: any
    ) -> list[T]:
        """
        Obtiene lista de entidades con paginación y filtros.

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            **filters: Filtros adicionales específicos de la entidad
        """
        pass

    @abstractmethod
    async def count(self, **filters: any) -> int:
        """Cuenta el total de entidades que cumplen los filtros."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Crea una nueva entidad y la persiste."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Actualiza una entidad existente."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        Elimina una entidad por su ID.

        Returns:
            True si se eliminó, False si no existía
        """
        pass


class IInvoiceRepository(IRepository[Invoice]):
    """
    Interfaz específica para el repositorio de facturas.

    Extiende IRepository con operaciones específicas de Invoice.
    """

    @abstractmethod
    async def get_by_series(self, series: str) -> Optional[Invoice]:
        """Obtiene una factura por su número de serie."""
        pass

    @abstractmethod
    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """Obtiene facturas por estado."""
        pass

    @abstractmethod
    async def get_by_company(
        self,
        company_id: int,
        is_issuer: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """
        Obtiene facturas de una empresa.

        Args:
            company_id: ID de la empresa
            is_issuer: True si es emisor, False si es receptor
        """
        pass

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: str,
        end_date: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """Obtiene facturas en un rango de fechas."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        """
        Búsqueda de texto completo en facturas.

        Busca en: series, nombre emisor, nombre receptor, notas.
        """
        pass

    @abstractmethod
    async def get_pending_sync(self, limit: int = 100) -> list[Invoice]:
        """Obtiene facturas pendientes de sincronización."""
        pass

    @abstractmethod
    async def bulk_update_status(
        self,
        invoice_ids: list[int],
        status: str
    ) -> int:
        """
        Actualiza el estado de múltiples facturas.

        Returns:
            Número de facturas actualizadas
        """
        pass


class ICompanyRepository(IRepository[Company]):
    """
    Interfaz específica para el repositorio de empresas.

    Extiende IRepository con operaciones específicas de Company.
    """

    @abstractmethod
    async def get_by_tax_id(self, tax_id: str) -> Optional[Company]:
        """Obtiene una empresa por su identificador fiscal (RUC, RFC, etc.)."""
        pass

    @abstractmethod
    async def get_by_type(
        self,
        company_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Company]:
        """Obtiene empresas por tipo (EMISOR, RECEPTOR, AMBOS)."""
        pass

    @abstractmethod
    async def search_by_name(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Company]:
        """Búsqueda de empresas por nombre o nombre comercial."""
        pass

    @abstractmethod
    async def get_or_create_by_tax_id(
        self,
        tax_id: str,
        name: str,
        **additional_data: any
    ) -> Company:
        """
        Obtiene una empresa por tax_id o la crea si no existe.

        Útil para procesamiento OCR donde se extraen empresas automáticamente.
        """
        pass

    @abstractmethod
    async def update_invoice_count(self, company_id: int) -> None:
        """Actualiza el contador de facturas de una empresa."""
        pass
