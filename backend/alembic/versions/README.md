# 📦 Database Migrations - Alembic

Directorio de versiones de migraciones de base de datos usando Alembic.

## 🎯 Convenciones de Nomenclatura

Las migraciones se generan automáticamente con el formato:
```
YYYYMMDD_HHMM-{revision_id}_{slug}.py
```

Ejemplo:
```
20241119_1630-abc123def456_initial_schema.py
```

## 📝 Comandos Principales

### Crear Nueva Migración (Autogenerate)

```bash
# Genera migración automáticamente detectando cambios en modelos
alembic revision --autogenerate -m "descripcion del cambio"

# Ejemplo:
alembic revision --autogenerate -m "agregar campo email a companies"
```

### Aplicar Migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar migraciones específicas
alembic upgrade +1  # Aplicar siguiente
alembic upgrade abc123  # Aplicar hasta revisión específica
```

### Revertir Migraciones

```bash
# Revertir última migración
alembic downgrade -1

# Revertir a revisión específica
alembic downgrade abc123

# Revertir todas
alembic downgrade base
```

### Consultar Estado

```bash
# Ver migración actual
alembic current

# Ver historial completo
alembic history

# Ver migraciones pendientes
alembic heads
```

## 🏗️ Estructura de Migración

Cada archivo de migración contiene:

```python
def upgrade() -> None:
    """Aplicar cambios a la base de datos"""
    # Código para aplicar cambios
    pass


def downgrade() -> None:
    """Revertir cambios de la base de datos"""
    # Código para deshacer cambios
    pass
```

## ⚠️ Consideraciones Importantes

### Antes de Crear Migraciones

1. **Importar todos los modelos** en `alembic/env.py`
2. **Verificar cambios** en modelos SQLModel
3. **Revisar migración generada** antes de aplicar
4. **Probar en desarrollo** antes de producción

### Buenas Prácticas

✅ **DO:**
- Crear una migración por cada cambio lógico
- Escribir mensajes descriptivos
- Revisar el código generado
- Probar upgrade Y downgrade
- Mantener migraciones pequeñas y enfocadas

❌ **DON'T:**
- Editar migraciones ya aplicadas en producción
- Mezclar múltiples cambios no relacionados
- Eliminar migraciones del historial
- Aplicar migraciones sin revisar primero

### Autogenerate Limitations

Alembic autogenerate **detecta**:
- Nuevas tablas y columnas
- Cambios en tipos de datos
- Modificaciones de constraints
- Cambios en índices

Alembic autogenerate **NO detecta**:
- Cambios en nombres de tablas (requiere manual)
- Cambios en nombres de columnas (requiere manual)
- Cambios en constraints complejas
- Migraciones de datos

Para estos casos, edita manualmente la migración generada.

## 🔄 Workflow de Desarrollo

### 1. Modificar Modelos

```python
# src/infrastructure/database/models.py
class CompanyDB(SQLModel, table=True):
    # ... campos existentes ...
    email: str = Field(index=True)  # Nuevo campo
```

### 2. Generar Migración

```bash
alembic revision --autogenerate -m "agregar campo email a companies"
```

### 3. Revisar Migración Generada

```bash
# Verificar en: alembic/versions/YYYYMMDD_HHMM-{rev}_agregar_campo_email_a_companies.py
cat alembic/versions/202411*.py
```

### 4. Aplicar Migración

```bash
alembic upgrade head
```

### 5. Verificar en Base de Datos

```bash
# SQLite
sqlite3 data/invokox.db ".schema companies"

# PostgreSQL
psql -U invokox_user -d invokox_db -c "\d companies"
```

## 🐳 Uso con Docker

### Aplicar migraciones en contenedor

```bash
# Con Make
make migrate

# Con docker-compose directamente
docker-compose exec backend alembic upgrade head
```

### Crear migración en contenedor

```bash
# Con Make
make migrate-create msg="descripcion"

# Con docker-compose directamente
docker-compose exec backend alembic revision --autogenerate -m "descripcion"
```

### Revertir en contenedor

```bash
# Con Make
make migrate-down

# Con docker-compose directamente
docker-compose exec backend alembic downgrade -1
```

## 📊 Ejemplo de Migración

### Migración de Ejemplo

```python
"""agregar campo email a companies

Revision ID: abc123def456
Revises: prev_revision_id
Create Date: 2024-11-19 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'abc123def456'
down_revision: Union[str, None] = 'prev_revision_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna email
    op.add_column('companies', sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # Crear índice
    op.create_index(op.f('ix_companies_email'), 'companies', ['email'], unique=False)


def downgrade() -> None:
    # Eliminar índice
    op.drop_index(op.f('ix_companies_email'), table_name='companies')

    # Eliminar columna
    op.drop_column('companies', 'email')
```

## 🔐 Migraciones en Producción

### Checklist Pre-Deployment

- [ ] Migración revisada y aprobada
- [ ] Backup de base de datos creado
- [ ] Downgrade testeado
- [ ] Ventana de mantenimiento planificada
- [ ] Rollback plan documentado

### Aplicar en Producción

```bash
# 1. Crear backup
make backup-db

# 2. Ver migraciones pendientes
alembic current
alembic heads

# 3. Aplicar migraciones
alembic upgrade head

# 4. Verificar resultado
alembic current

# 5. Si hay problemas, revertir
alembic downgrade -1
```

## 📚 Recursos

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

## 🐛 Troubleshooting

### Error: "Target database is not up to date"

```bash
# Verificar versión actual
alembic current

# Ver historial
alembic history

# Aplicar migraciones pendientes
alembic upgrade head
```

### Error: "Can't locate revision identified by 'xxx'"

```bash
# Verificar que el archivo de migración exista
ls alembic/versions/

# Regenerar desde base si es necesario (¡CUIDADO!)
alembic stamp head
```

### Desincronización entre código y DB

```bash
# Opción 1: Stamp a versión específica (marca sin aplicar)
alembic stamp abc123

# Opción 2: Recrear desde cero (solo desarrollo)
rm data/invokox.db
alembic upgrade head
```

### Conflictos en Branching

```bash
# Ver todas las heads
alembic heads

# Merge branches
alembic merge -m "merge branches" head1 head2
```

---

**IMPORTANTE**: Nunca edites migraciones que ya fueron aplicadas en producción. Crea una nueva migración en su lugar.
