#!/usr/bin/env python3
"""
==============================================================================
SCRIPT: Crear Migración Inicial de Base de Datos
==============================================================================
Este script crea la primera migración de Alembic para el schema completo.

Uso:
    python scripts/create_initial_migration.py

Prerequisitos:
    - Alembic configurado en alembic.ini
    - Modelos SQLModel importados en alembic/env.py
    - Poetry environment activado

El script:
    1. Verifica que no existan migraciones previas
    2. Genera migración automática del schema completo
    3. Muestra resumen de tablas detectadas
==============================================================================
"""

import subprocess
import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def main():
    """Crear migración inicial de base de datos."""

    print("=" * 80)
    print("  CREAR MIGRACIÓN INICIAL - INVOKOX V2.0")
    print("=" * 80)
    print()

    # Verificar directorio de migraciones
    versions_dir = root_dir / "alembic" / "versions"
    existing_migrations = list(versions_dir.glob("*.py"))

    if existing_migrations:
        print("⚠️  ADVERTENCIA: Ya existen migraciones:")
        for migration in existing_migrations:
            print(f"   - {migration.name}")
        print()
        response = input("¿Deseas continuar de todas formas? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operación cancelada")
            return 1

    print("📦 Importando modelos SQLModel...")
    try:
        from src.infrastructure.database.models import (
            CompanyDB,
            InvoiceDB,
            InvoiceItemDB,
            AuditLogDB
        )
        print(f"   ✓ CompanyDB")
        print(f"   ✓ InvoiceDB")
        print(f"   ✓ InvoiceItemDB")
        print(f"   ✓ AuditLogDB")
        print()
    except ImportError as e:
        print(f"❌ Error al importar modelos: {e}")
        return 1

    print("🔨 Generando migración automática...")
    print()

    # Ejecutar alembic revision --autogenerate
    cmd = [
        "alembic",
        "revision",
        "--autogenerate",
        "-m",
        "initial schema with companies, invoices, invoice_items, and audit_logs"
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )

        print(result.stdout)

        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)

        print()
        print("=" * 80)
        print("✅ MIGRACIÓN CREADA EXITOSAMENTE")
        print("=" * 80)
        print()
        print("📋 Próximos pasos:")
        print()
        print("1. Revisar el archivo de migración generado:")
        print("   ls -lah alembic/versions/")
        print()
        print("2. Verificar el contenido de la migración:")
        print("   cat alembic/versions/202*.py")
        print()
        print("3. Aplicar la migración:")
        print("   alembic upgrade head")
        print()
        print("4. Verificar que se aplicó correctamente:")
        print("   alembic current")
        print()

        return 0

    except subprocess.CalledProcessError as e:
        print(f"❌ Error al generar migración:")
        print(e.stdout)
        print(e.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
