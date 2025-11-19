"""
Database Configuration

Configuración de conexión a base de datos con soporte dual:
- SQLite para desarrollo y modo standalone
- SQL Server para producción y modo server
"""

import os
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool


# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

def get_database_url() -> str:
    """
    Obtiene la URL de conexión a la base de datos.

    Prioridad:
    1. Variable de entorno DATABASE_URL
    2. Construcción desde MODE
    3. Default: SQLite local
    """
    # Si está especificada explícitamente
    if database_url := os.getenv("DATABASE_URL"):
        return database_url

    # Según el modo de operación
    mode = os.getenv("MODE", "standalone")

    if mode == "standalone":
        # SQLite local
        db_path = os.getenv("SQLITE_PATH", "./data/invokox.db")
        return f"sqlite:///{db_path}"

    elif mode == "server":
        # SQL Server (necesita todas estas variables)
        server = os.getenv("SQL_SERVER_HOST", "localhost")
        port = os.getenv("SQL_SERVER_PORT", "1433")
        database = os.getenv("SQL_SERVER_DATABASE", "invokox_db")
        username = os.getenv("SQL_SERVER_USER", "sa")
        password = os.getenv("SQL_SERVER_PASSWORD", "YourStrong!Passw0rd")
        driver = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 18 for SQL Server")

        return (
            f"mssql+pyodbc://{username}:{password}@{server}:{port}/{database}"
            f"?driver={driver}&TrustServerCertificate=yes"
        )

    else:
        # Default: SQLite
        return "sqlite:///./data/invokox.db"


# ==============================================================================
# ENGINE
# ==============================================================================

# Detectar tipo de base de datos
DATABASE_URL = get_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Configurar argumentos según el tipo de BD
connect_args = {}
engine_args = {
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
}

if IS_SQLITE:
    # SQLite: configuración especial para threading
    connect_args = {"check_same_thread": False}
    # Para testing: usar in-memory con StaticPool
    if DATABASE_URL == "sqlite:///:memory:":
        engine_args["poolclass"] = StaticPool
        engine_args["connect_args"] = connect_args
    else:
        engine_args["connect_args"] = connect_args
else:
    # SQL Server: pool de conexiones
    engine_args["pool_size"] = int(os.getenv("DB_POOL_SIZE", "5"))
    engine_args["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    engine_args["pool_timeout"] = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    engine_args["pool_recycle"] = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Crear engine
engine = create_engine(DATABASE_URL, **engine_args)


# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def create_db_and_tables() -> None:
    """
    Crea todas las tablas en la base de datos.

    IMPORTANTE: En producción usar Alembic en lugar de esto.
    Esta función es útil para desarrollo rápido.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    Obtiene una sesión de base de datos.

    Uso con context manager:
    ```python
    with get_session() as session:
        # usar session
        pass
    ```
    """
    return Session(engine)


def get_session_dependency():
    """
    Dependency injection para FastAPI.

    Usage:
    ```python
    @app.get("/invoices")
    def get_invoices(session: Session = Depends(get_session_dependency)):
        # usar session
    ```
    """
    with Session(engine) as session:
        yield session


# ==============================================================================
# INFORMACIÓN DE CONFIGURACIÓN
# ==============================================================================

def get_db_info() -> dict[str, any]:
    """Retorna información sobre la configuración de BD."""
    return {
        "database_url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
        "is_sqlite": IS_SQLITE,
        "mode": os.getenv("MODE", "standalone"),
        "echo": engine_args.get("echo", False),
        "pool_size": engine_args.get("pool_size", "N/A"),
    }


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

def check_db_connection() -> bool:
    """
    Verifica que la conexión a BD esté funcionando.

    Returns:
        True si la conexión es exitosa, False en caso contrario.
    """
    try:
        with Session(engine) as session:
            # Simple query para verificar conexión
            session.execute("SELECT 1" if IS_SQLITE else "SELECT 1 AS test")
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
