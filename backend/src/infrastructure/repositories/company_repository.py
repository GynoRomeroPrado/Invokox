"""
Company Repository Implementation

Implementación concreta del repositorio de empresas usando SQLModel.
"""

from typing import Optional
from sqlmodel import Session, select, func, or_

from src.domain.entities.company import Company
from src.application.interfaces.repository_interface import ICompanyRepository
from src.infrastructure.database.models import CompanyDB, InvoiceDB


class CompanyRepository(ICompanyRepository):
    """
    Implementación del repositorio de empresas.

    Traduce entre entidades de dominio (Company) y modelos de BD (CompanyDB).
    """

    def __init__(self, session: Session):
        self.session = session

    # ==========================================================================
    # MÉTODOS BÁSICOS (CRUD)
    # ==========================================================================

    async def get_by_id(self, id: int) -> Optional[Company]:
        """Obtiene una empresa por ID."""
        company_db = self.session.get(CompanyDB, id)
        if not company_db:
            return None

        return self._to_domain(company_db)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: any
    ) -> list[Company]:
        """Obtiene lista de empresas con paginación."""
        statement = select(CompanyDB).offset(skip).limit(limit)

        # Aplicar filtros
        if "type" in filters:
            statement = statement.where(CompanyDB.type == filters["type"])
        if "is_active" in filters:
            statement = statement.where(CompanyDB.is_active == filters["is_active"])

        # Ordenar por nombre
        statement = statement.order_by(CompanyDB.name)

        results = self.session.exec(statement).all()
        return [self._to_domain(company) for company in results]

    async def count(self, **filters: any) -> int:
        """Cuenta el total de empresas."""
        statement = select(func.count(CompanyDB.id))

        if "type" in filters:
            statement = statement.where(CompanyDB.type == filters["type"])
        if "is_active" in filters:
            statement = statement.where(CompanyDB.is_active == filters["is_active"])

        return self.session.exec(statement).one()

    async def create(self, entity: Company) -> Company:
        """Crea una nueva empresa."""
        company_db = self._to_db_model(entity)

        self.session.add(company_db)
        self.session.commit()
        self.session.refresh(company_db)

        return self._to_domain(company_db)

    async def update(self, entity: Company) -> Company:
        """Actualiza una empresa existente."""
        if not entity.id:
            raise ValueError("Company must have an ID to be updated")

        company_db = self.session.get(CompanyDB, entity.id)
        if not company_db:
            raise ValueError(f"Company with ID {entity.id} not found")

        # Actualizar campos
        company_db.tax_id = entity.tax_id
        company_db.name = entity.name
        company_db.commercial_name = entity.commercial_name
        company_db.type = entity.type
        company_db.address = entity.address
        company_db.email = entity.email
        company_db.phone = entity.phone
        company_db.website = entity.website
        company_db.updated_at = entity.updated_at
        company_db.is_active = entity.is_active

        self.session.commit()
        self.session.refresh(company_db)

        return self._to_domain(company_db)

    async def delete(self, id: int) -> bool:
        """Elimina una empresa por ID."""
        company_db = self.session.get(CompanyDB, id)
        if not company_db:
            return False

        # Verificar que no tenga facturas asociadas
        invoice_count = self.session.exec(
            select(func.count(InvoiceDB.id)).where(
                or_(
                    InvoiceDB.issuer_id == id,
                    InvoiceDB.receiver_id == id
                )
            )
        ).one()

        if invoice_count > 0:
            raise ValueError(
                f"Cannot delete company with {invoice_count} associated invoices. "
                "Set is_active=False instead."
            )

        self.session.delete(company_db)
        self.session.commit()
        return True

    # ==========================================================================
    # MÉTODOS ESPECÍFICOS DE COMPANY
    # ==========================================================================

    async def get_by_tax_id(self, tax_id: str) -> Optional[Company]:
        """Obtiene una empresa por su identificador fiscal."""
        statement = select(CompanyDB).where(CompanyDB.tax_id == tax_id)
        company_db = self.session.exec(statement).first()

        if not company_db:
            return None

        return self._to_domain(company_db)

    async def get_by_type(
        self,
        company_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Company]:
        """Obtiene empresas por tipo."""
        statement = (
            select(CompanyDB)
            .where(CompanyDB.type == company_type)
            .where(CompanyDB.is_active == True)
            .order_by(CompanyDB.name)
            .offset(skip)
            .limit(limit)
        )

        results = self.session.exec(statement).all()
        return [self._to_domain(company) for company in results]

    async def search_by_name(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Company]:
        """Búsqueda de empresas por nombre o nombre comercial."""
        search_term = f"%{query}%"

        statement = (
            select(CompanyDB)
            .where(
                or_(
                    CompanyDB.name.like(search_term),
                    CompanyDB.commercial_name.like(search_term),
                    CompanyDB.tax_id.like(search_term),
                )
            )
            .where(CompanyDB.is_active == True)
            .order_by(CompanyDB.name)
            .offset(skip)
            .limit(limit)
        )

        results = self.session.exec(statement).all()
        return [self._to_domain(company) for company in results]

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
        # Intentar obtener existente
        company = await self.get_by_tax_id(tax_id)

        if company:
            return company

        # Si no existe, crear nueva
        company = Company(
            tax_id=tax_id,
            name=name,
            commercial_name=additional_data.get("commercial_name"),
            type=additional_data.get("type", "AMBOS"),
            address=additional_data.get("address"),
            email=additional_data.get("email"),
            phone=additional_data.get("phone"),
            website=additional_data.get("website"),
        )

        return await self.create(company)

    async def update_invoice_count(self, company_id: int) -> None:
        """Actualiza el contador de facturas de una empresa."""
        # Contar facturas donde es emisor
        issued_count = self.session.exec(
            select(func.count(InvoiceDB.id)).where(InvoiceDB.issuer_id == company_id)
        ).one()

        # Contar facturas donde es receptor
        received_count = self.session.exec(
            select(func.count(InvoiceDB.id)).where(InvoiceDB.receiver_id == company_id)
        ).one()

        # Total
        total_count = issued_count + received_count

        # Actualizar
        company_db = self.session.get(CompanyDB, company_id)
        if company_db:
            company_db.invoice_count = total_count
            self.session.commit()

    # ==========================================================================
    # MÉTODOS DE CONVERSIÓN (MAPPERS)
    # ==========================================================================

    def _to_domain(self, company_db: CompanyDB) -> Company:
        """Convierte modelo de BD a entidad de dominio."""
        return Company(
            id=company_db.id,
            tax_id=company_db.tax_id,
            name=company_db.name,
            commercial_name=company_db.commercial_name,
            type=company_db.type,
            address=company_db.address,
            email=company_db.email,
            phone=company_db.phone,
            website=company_db.website,
            created_at=company_db.created_at,
            updated_at=company_db.updated_at,
            is_active=company_db.is_active,
            invoice_count=company_db.invoice_count,
        )

    def _to_db_model(self, company: Company) -> CompanyDB:
        """Convierte entidad de dominio a modelo de BD."""
        return CompanyDB(
            tax_id=company.tax_id,
            name=company.name,
            commercial_name=company.commercial_name,
            type=company.type,
            address=company.address,
            email=company.email,
            phone=company.phone,
            website=company.website,
            is_active=company.is_active,
            invoice_count=company.invoice_count,
        )
