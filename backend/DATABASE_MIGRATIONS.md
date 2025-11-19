# 📦 Database Migrations - Guía Completa

Documentación completa para gestión de migraciones de base de datos en Invokox v2.0 usando Alembic.

## 📋 Tabla de Contenidos

- [Overview](#overview)
- [Configuración](#configuración)
- [Estructura de Schema](#estructura-de-schema)
- [Comandos de Migración](#comandos-de-migración)
- [Workflow de Desarrollo](#workflow-de-desarrollo)
- [Uso con Docker](#uso-con-docker)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

### ¿Qué es Alembic?

Alembic es una herramienta de migración de base de datos para SQLAlchemy que permite:
- Versionado de schema de base de datos
- Aplicar y revertir cambios de manera controlada
- Auto-generación de migraciones desde modelos
- Tracking de historial de cambios

### Schema Actual (Versión 001)

La migración inicial crea 4 tablas principales:

```
companies (empresas)
   ↓
invoices (facturas) ← tiene FK a companies
   ↓
invoice_items (líneas de factura) ← tiene FK a invoices

audit_logs (auditoría) ← independiente
```

## ⚙️ Configuración

### Archivos de Configuración

#### `alembic.ini`

Configuración principal de Alembic:

```ini
[alembic]
script_location = alembic
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 100 REVISION_SCRIPT_FILENAME
```

**Características:**
- Migraciones con timestamp: `YYYYMMDD_HHMM-{rev}_{slug}.py`
- Auto-formateo con Black (100 caracteres por línea)
- Logging configurado

#### `alembic/env.py`

Configuración de runtime:

```python
from sqlmodel import SQLModel
from src.infrastructure.database.models import (
    CompanyDB,
    InvoiceDB,
    InvoiceItemDB,
    AuditLogDB
)
from src.infrastructure.database.config import DATABASE_URL

# Configurar metadata para autogenerate
target_metadata = SQLModel.metadata

# Sobrescribir URL desde configuración
config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

**IMPORTANTE:** Importar TODOS los modelos SQLModel para que autogenerate los detecte.

### Variables de Entorno

```bash
# Development (SQLite)
DATABASE_URL=sqlite:///./data/invokox.db

# Development (PostgreSQL)
DATABASE_URL=postgresql://invokox_user:password@localhost:5432/invokox_db

# Production (SQL Server)
DATABASE_URL=mssql+pyodbc://user:password@server/invokox_db?driver=ODBC+Driver+18+for+SQL+Server
```

## 🗄️ Estructura de Schema

### Tabla: companies

Almacena información de empresas (emisoras y receptoras).

```sql
CREATE TABLE companies (
    -- Identity
    id INTEGER PRIMARY KEY,
    tax_id VARCHAR(50) UNIQUE NOT NULL,
    tax_id_type VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    trade_name VARCHAR(200),
    company_type VARCHAR(20) NOT NULL,  -- 'issuer', 'receiver', 'both'

    -- Contact
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    phone VARCHAR(50),
    email VARCHAR(100),
    website VARCHAR(200),

    -- Statistics
    invoice_count INTEGER DEFAULT 0,
    total_amount NUMERIC(18,2) DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Indexes
CREATE INDEX ix_companies_name ON companies(name);
CREATE UNIQUE INDEX ix_companies_tax_id ON companies(tax_id);
CREATE INDEX ix_companies_company_type ON companies(company_type);
CREATE INDEX ix_companies_is_active ON companies(is_active);
```

**Normalización:** Evita duplicar información de empresa en cada factura.

### Tabla: invoices

Facturas con información completa.

```sql
CREATE TABLE invoices (
    -- Identity
    id INTEGER PRIMARY KEY,
    series VARCHAR(50) UNIQUE NOT NULL,
    folio_number VARCHAR(50) NOT NULL,
    invoice_type VARCHAR(20) NOT NULL,

    -- Relations
    issuer_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    -- Denormalized for performance
    issuer_name VARCHAR(200) NOT NULL,
    issuer_tax_id VARCHAR(50) NOT NULL,
    receiver_name VARCHAR(200) NOT NULL,
    receiver_tax_id VARCHAR(50) NOT NULL,

    -- Dates
    issue_date DATE NOT NULL,
    due_date DATE,

    -- Amounts
    currency VARCHAR(3) DEFAULT 'PEN',
    subtotal NUMERIC(18,2) DEFAULT 0,
    tax_amount NUMERIC(18,2) DEFAULT 0,
    discount_amount NUMERIC(18,2) DEFAULT 0,
    total_amount NUMERIC(18,2) DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'PENDING',
    payment_status VARCHAR(20),
    payment_method VARCHAR(50),

    -- Processing
    file_path VARCHAR(500),
    ocr_confidence FLOAT,
    processing_time FLOAT,

    -- Notes
    notes TEXT,

    -- Optimistic Locking
    version INTEGER DEFAULT 1,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Indexes
CREATE UNIQUE INDEX ix_invoices_series ON invoices(series);
CREATE INDEX ix_invoices_status ON invoices(status);
CREATE INDEX ix_invoices_issue_date ON invoices(issue_date);
CREATE INDEX ix_invoices_issuer_id ON invoices(issuer_id);
CREATE INDEX ix_invoices_receiver_id ON invoices(receiver_id);
CREATE INDEX ix_invoices_invoice_type ON invoices(invoice_type);
CREATE INDEX ix_invoices_issue_date_status ON invoices(issue_date, status);
```

**Desnormalización estratégica:** Campos `issuer_name`, `issuer_tax_id`, etc. evitan JOINs en listados.

### Tabla: invoice_items

Items/líneas de cada factura.

```sql
CREATE TABLE invoice_items (
    -- Identity
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,

    -- Product/Service
    code VARCHAR(100),
    description VARCHAR(500) NOT NULL,
    unit VARCHAR(50),

    -- Quantities
    quantity NUMERIC(18,4) NOT NULL,
    unit_price NUMERIC(18,2) NOT NULL,
    discount_rate NUMERIC(5,2) DEFAULT 0,
    tax_rate NUMERIC(5,2) DEFAULT 0,

    -- Calculated amounts
    subtotal NUMERIC(18,2) NOT NULL,
    discount_amount NUMERIC(18,2) DEFAULT 0,
    tax_amount NUMERIC(18,2) DEFAULT 0,
    total NUMERIC(18,2) NOT NULL,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX ix_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX ix_invoice_items_invoice_line ON invoice_items(invoice_id, line_number);
```

**Cascade Delete:** Al eliminar una factura, se eliminan automáticamente sus items.

### Tabla: audit_logs

Registro de auditoría para trazabilidad.

```sql
CREATE TABLE audit_logs (
    -- Identity
    id INTEGER PRIMARY KEY,

    -- Event
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    action VARCHAR(50) NOT NULL,

    -- User
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Context
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),

    -- Changes (JSON)
    old_values TEXT,
    new_values TEXT,

    -- Description
    description VARCHAR(500)
);

-- Indexes
CREATE INDEX ix_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX ix_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX ix_audit_logs_action ON audit_logs(action);
CREATE INDEX ix_audit_logs_entity ON audit_logs(entity_type, entity_id, timestamp);
```

**Uso:** Tracking completo de operaciones CREATE, UPDATE, DELETE, APPROVE, REJECT.

## 🚀 Comandos de Migración

### Aplicar Migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar siguiente migración
alembic upgrade +1

# Aplicar hasta revisión específica
alembic upgrade abc123
```

### Revertir Migraciones

```bash
# Revertir última migración
alembic downgrade -1

# Revertir a revisión específica
alembic downgrade abc123

# Revertir todas (PELIGROSO)
alembic downgrade base
```

### Crear Nuevas Migraciones

```bash
# Auto-generar desde cambios en modelos
alembic revision --autogenerate -m "descripcion del cambio"

# Crear migración vacía (para migración manual)
alembic revision -m "descripcion"
```

### Consultar Estado

```bash
# Ver migración actual
alembic current

# Ver historial completo
alembic history

# Ver migraciones pendientes
alembic heads

# Ver información de revisión específica
alembic show abc123
```

### Otras Operaciones

```bash
# Marcar base de datos en revisión sin aplicar
alembic stamp head
alembic stamp abc123

# Merge de branches (raro)
alembic merge -m "merge description" head1 head2

# Generar SQL sin aplicar
alembic upgrade head --sql > migration.sql
```

## 🔄 Workflow de Desarrollo

### Escenario 1: Agregar Nueva Columna

**1. Modificar modelo SQLModel:**

```python
# src/infrastructure/database/models.py
class CompanyDB(SQLModel, table=True):
    __tablename__ = "companies"

    # ... campos existentes ...

    # NUEVO CAMPO
    registration_date: Optional[date] = Field(default=None, index=True)
```

**2. Generar migración:**

```bash
alembic revision --autogenerate -m "agregar registration_date a companies"
```

**3. Revisar migración generada:**

```bash
# Ver archivo en: alembic/versions/YYYYMMDD_HHMM-{rev}_agregar_registration_date_a_companies.py
cat alembic/versions/202*.py
```

**4. Aplicar migración:**

```bash
alembic upgrade head
```

**5. Verificar en base de datos:**

```bash
# SQLite
sqlite3 data/invokox.db ".schema companies"

# PostgreSQL
psql -U invokox_user -d invokox_db -c "\d companies"
```

### Escenario 2: Crear Nueva Tabla

**1. Crear modelo SQLModel:**

```python
# src/infrastructure/database/models.py
class PaymentDB(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoices.id")
    amount: Decimal = Field(max_digits=18, decimal_places=2)
    payment_date: date
    payment_method: str

    # Relationship
    invoice: "InvoiceDB" = Relationship(back_populates="payments")
```

**2. Actualizar modelo relacionado:**

```python
# Agregar a InvoiceDB
payments: list["PaymentDB"] = Relationship(back_populates="invoice")
```

**3. Importar en alembic/env.py:**

```python
from src.infrastructure.database.models import (
    CompanyDB,
    InvoiceDB,
    InvoiceItemDB,
    AuditLogDB,
    PaymentDB  # NUEVO
)
```

**4. Generar y aplicar migración:**

```bash
alembic revision --autogenerate -m "crear tabla payments"
alembic upgrade head
```

### Escenario 3: Renombrar Columna (Manual)

Alembic autogenerate NO detecta renames, solo ve DROP + ADD.

**Migración manual:**

```python
def upgrade() -> None:
    # Renombrar columna (PostgreSQL)
    op.alter_column('companies', 'trade_name', new_column_name='commercial_name')

    # SQLite no soporta ALTER COLUMN, necesita recrear tabla
    # (ver documentación de SQLite para workaround)


def downgrade() -> None:
    op.alter_column('companies', 'commercial_name', new_column_name='trade_name')
```

### Escenario 4: Migración de Datos

**Ejemplo:** Llenar campo nuevo con datos calculados.

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade() -> None:
    # 1. Agregar columna
    op.add_column('companies', sa.Column('full_name', sa.String(300)))

    # 2. Migración de datos
    companies = table('companies',
        column('id', sa.Integer),
        column('name', sa.String),
        column('trade_name', sa.String),
        column('full_name', sa.String)
    )

    conn = op.get_bind()
    results = conn.execute(sa.select(companies.c.id, companies.c.name, companies.c.trade_name))

    for company_id, name, trade_name in results:
        full = f"{name} ({trade_name})" if trade_name else name
        conn.execute(
            companies.update()
            .where(companies.c.id == company_id)
            .values(full_name=full)
        )

    # 3. Hacer NOT NULL después de llenar
    op.alter_column('companies', 'full_name', nullable=False)


def downgrade() -> None:
    op.drop_column('companies', 'full_name')
```

## 🐳 Uso con Docker

### Comandos con Make

```bash
# Aplicar migraciones
make migrate

# Crear nueva migración
make migrate-create msg="descripcion del cambio"

# Revertir última
make migrate-down

# Shell en backend
make shell-backend
alembic current
alembic history
```

### Comandos con Docker Compose

```bash
# Aplicar migraciones
docker-compose exec backend alembic upgrade head

# Crear migración
docker-compose exec backend alembic revision --autogenerate -m "descripcion"

# Revertir
docker-compose exec backend alembic downgrade -1

# Ver estado
docker-compose exec backend alembic current
```

### Auto-aplicar en Startup

El `docker-compose.yml` está configurado para aplicar migraciones automáticamente:

```yaml
backend:
  command: >
    sh -c "
      echo '📦 Running migrations...' &&
      alembic upgrade head &&
      echo '🌟 Starting FastAPI server...' &&
      uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload
    "
```

## 🐛 Troubleshooting

### Error: "Target database is not up to date"

**Causa:** Base de datos en versión diferente a código.

**Solución:**

```bash
# Ver estado actual
alembic current
alembic history

# Aplicar migraciones pendientes
alembic upgrade head
```

### Error: "Can't locate revision identified by 'xxx'"

**Causa:** Archivo de migración faltante o corrupto.

**Solución:**

```bash
# Verificar archivos
ls alembic/versions/

# Si desarrollo local (CUIDADO):
rm data/invokox.db
alembic upgrade head
```

### Error: "Column 'xxx' already exists"

**Causa:** Migración ya aplicada manualmente o duplicada.

**Solución:**

```bash
# Opción 1: Stamp a esa versión (marca sin aplicar)
alembic stamp abc123

# Opción 2: Editar migración para skip si existe
def upgrade():
    try:
        op.add_column('table', ...)
    except sa.exc.OperationalError:
        pass  # Column already exists
```

### Desincronización entre Código y DB

**Síntomas:** Autogenerate genera cambios que ya están aplicados.

**Causa:** Modelos no coinciden con schema actual.

**Solución:**

```bash
# 1. Verificar modelos vs. schema actual
alembic upgrade head  # Asegurar que DB está al día

# 2. Generar migración y revisar
alembic revision --autogenerate -m "sync check"

# 3. Si migración está vacía, todo está sincronizado
# 4. Si tiene cambios, revisar si son necesarios

# 5. Si es falsa alarma:
rm alembic/versions/202*_sync_check.py
```

### Performance Lento en Migraciones

**Problema:** Migración tarda mucho en tablas grandes.

**Solución:**

```python
# En la migración, usar batch operations
with op.batch_alter_table('large_table') as batch_op:
    batch_op.add_column(...)
    batch_op.create_index(...)

# O desactivar foreign keys temporalmente (SQLite)
op.execute('PRAGMA foreign_keys=OFF')
# ... operaciones ...
op.execute('PRAGMA foreign_keys=ON')
```

### Conflictos en Merge

**Problema:** Dos developers crearon migraciones simultáneamente.

**Solución:**

```bash
# Ver todas las heads
alembic heads

# Merge branches
alembic merge -m "merge feature branches" head1_id head2_id

# Aplicar merge
alembic upgrade head
```

## 📚 Mejores Prácticas

### ✅ DO

1. **Siempre revisar migraciones autogeneradas** antes de aplicar
2. **Probar upgrade Y downgrade** en desarrollo
3. **Crear backup antes de migrar** en producción
4. **Mantener migraciones pequeñas** y enfocadas
5. **Documentar cambios complejos** en docstring de migración
6. **Importar todos los modelos** en alembic/env.py
7. **Usar transacciones** para operaciones complejas
8. **Versionar archivos de migración** en git

### ❌ DON'T

1. **Nunca editar migraciones aplicadas** en producción
2. **No mezclar cambios no relacionados** en una migración
3. **No eliminar archivos de migración** del historial
4. **No aplicar sin revisar** en producción
5. **No usar DROP TABLE** sin downgrade plan
6. **No ignorar warnings** de Alembic
7. **No skip migraciones** del historial
8. **No olvidar foreign keys** en cascade deletes

## 🔐 Seguridad y Producción

### Checklist Pre-Deployment

- [ ] Migración revisada por otro developer
- [ ] Tests pasando
- [ ] Downgrade testeado
- [ ] Backup de producción creado
- [ ] Ventana de mantenimiento coordinada
- [ ] Plan de rollback documentado
- [ ] Stakeholders notificados

### Aplicar en Producción

```bash
# 1. Crear backup
pg_dump invokox_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Modo mantenimiento ON
# (poner API en modo read-only o down)

# 3. Verificar estado
alembic current

# 4. Aplicar migración
alembic upgrade head

# 5. Verificar resultado
alembic current
psql -c "SELECT COUNT(*) FROM companies"  # Verificar datos

# 6. Si todo OK, modo mantenimiento OFF

# 7. Si problemas, ROLLBACK:
alembic downgrade -1
psql -f backup_20241119_163000.sql
```

---

**Documentación creada:** 2024-11-19
**Última actualización:** 2024-11-19
**Versión de Schema:** 001 (Initial Schema)
