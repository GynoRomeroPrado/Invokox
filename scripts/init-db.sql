-- ==============================================================================
-- DATABASE INITIALIZATION SCRIPT
-- ==============================================================================
-- Script de inicialización para PostgreSQL (desarrollo)
-- Se ejecuta automáticamente al crear el contenedor
-- ==============================================================================

-- Configurar encoding y locale
SET client_encoding = 'UTF8';

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para búsqueda de texto optimizada

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE '✓ Database initialized successfully';
    RAISE NOTICE '✓ Extensions created: uuid-ossp, pg_trgm';
END $$;

-- Las tablas se crearán con Alembic migrations
