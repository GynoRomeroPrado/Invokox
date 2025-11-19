# 00 - VISIÓN Y ESTRATEGIA ARQUITECTÓNICA

## TABLA DE CONTENIDOS

1. [Contexto y Objetivos](#contexto-y-objetivos)
2. [Situación Actual](#situación-actual)
3. [Arquitectura Objetivo](#arquitectura-objetivo)
4. [Modos Operativos](#modos-operativos)
5. [Roadmap de Migración](#roadmap-de-migración)
6. [Principios Arquitectónicos](#principios-arquitectónicos)
7. [Decisiones Clave](#decisiones-clave)
8. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## CONTEXTO Y OBJETIVOS

### Propósito del Sistema
Sistema de **procesamiento inteligente de facturas** mediante OCR/AI con capacidad de operar en dos modalidades:
- **Standalone**: Aplicación desktop completa para usuarios con hardware potente
- **Cliente-Servidor**: Clientes ligeros conectados a Data Center corporativo

### Objetivos Estratégicos

#### Corto Plazo (0-6 meses)
- ✅ **Refactorización arquitectónica** para soportar dual-mode desde el inicio
- ✅ **Normalización del modelo de datos** con migraciones SQLite → SQL Server
- ✅ **Implementación de Clean Architecture** con capas desacopladas
- ✅ **Testing automatizado** (unitario, integración, e2e)

#### Mediano Plazo (6-12 meses)
- 🎯 **Despliegue de servidor FastAPI** en Data Center corporativo
- 🎯 **Migración a SQL Server** para base de datos centralizada
- 🎯 **Implementación de sincronización** bidireccional offline-first
- 🎯 **Rollout gradual** con usuarios piloto

#### Largo Plazo (12-24 meses)
- 🚀 **Escalabilidad horizontal** con múltiples servidores
- 🚀 **Multi-tenancy** para múltiples clientes corporativos
- 🚀 **API pública** para integraciones externas
- 🚀 **Analytics y BI** con Power BI / Tableau

### Requisitos No Funcionales

| Categoría | Requisito | Métrica Objetivo |
|-----------|-----------|------------------|
| **Performance** | Procesamiento OCR | < 10s por factura (GPU) / < 30s (CPU) |
| **Disponibilidad** | Uptime servidor | 99.5% (43h downtime/año) |
| **Escalabilidad** | Usuarios concurrentes | 100+ usuarios simultáneos |
| **Seguridad** | Encriptación datos | AES-256 en reposo, TLS 1.3 en tránsito |
| **Usabilidad** | Tiempo de respuesta UI | < 200ms (interacción local) |
| **Mantenibilidad** | Cobertura de tests | > 80% backend, > 70% frontend |

---

## SITUACIÓN ACTUAL

### Stack Tecnológico Existente

```
┌─────────────────────────────────────────┐
│         APLICACIÓN DESKTOP              │
├─────────────────────────────────────────┤
│  Frontend: React 18 + TypeScript        │
│  - Vite (build tool)                    │
│  - TailwindCSS (estilos)                │
│  - Zustand (estado)                     │
├─────────────────────────────────────────┤
│  Desktop Wrapper: PyWebview 5.1         │
├─────────────────────────────────────────┤
│  Backend: Python 3.11 Monolítico        │
│  - Arquitectura MVP (Model-View-Pres)   │
│  - Services + Presenters + Models       │
├─────────────────────────────────────────┤
│  ORM: SQLModel 0.0.16 / SQLAlchemy      │
├─────────────────────────────────────────┤
│  Base de Datos: SQLite (local file)     │
│  - facturasmodern.db                    │
│  - 97 campos en tabla Factura           │
├─────────────────────────────────────────┤
│  AI/OCR: Múltiples motores              │
│  - PaddleOCR, Docling, Tesseract        │
│  - Transformers (Hugging Face)          │
│  - PyTorch 2.9.1                        │
└─────────────────────────────────────────┘
```

### Problemas Identificados

#### 1. **Arquitectura Monolítica Rígida**
- ❌ Backend acoplado a PyWebview (dificulta modo cliente-servidor)
- ❌ Lógica de negocio mezclada con capa de presentación
- ❌ Imposible reutilizar servicios como API independiente

#### 2. **Modelo de Datos Desnormalizado**
- ❌ 97 campos en tabla única `Factura` (dificulta mantenimiento)
- ❌ Duplicación de datos (emisor/receptor repetidos en cada factura)
- ❌ Sin relaciones explícitas normalizadas

#### 3. **Base de Datos No Escalable**
- ❌ SQLite no soporta multi-usuario concurrente efectivamente
- ❌ Sin capacidades enterprise (replicación, clustering, backups automáticos)
- ❌ Límites de tamaño y performance para datasets grandes

#### 4. **Falta de Abstracción de Datos**
- ❌ Acceso directo a modelos SQLModel desde servicios
- ❌ Sin patrón Repository (dificulta testing y migración de BD)
- ❌ Lógica de BD acoplada a SQLite

#### 5. **UI Desktop Limitada**
- ❌ PyWebview tiene ecosistema limitado vs Electron/Tauri
- ❌ Dificulta empaquetado cross-platform robusto
- ❌ Sin soporte para auto-update nativo

#### 6. **Testing Insuficiente**
- ❌ Sin suite de tests automatizados mencionada
- ❌ Sin CI/CD pipeline
- ❌ Testing manual y regresiones frecuentes

---

## ARQUITECTURA OBJETIVO

### Patrón: Clean Architecture + Hexagonal (Ports & Adapters)

```
┌───────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                        │
│  ┌──────────────────┐              ┌──────────────────┐       │
│  │  Desktop Client  │              │   Web Client     │       │
│  │  (Electron/Tauri)│              │   (Opcional)     │       │
│  │  React + TS      │              │   React + TS     │       │
│  └────────┬─────────┘              └────────┬─────────┘       │
│           │                                 │                  │
│           └─────────────┬───────────────────┘                  │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (API)                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              FastAPI REST/GraphQL API                   │  │
│  │  - Authentication & Authorization (JWT)                 │  │
│  │  - Rate Limiting & Throttling                           │  │
│  │  - Request Validation (Pydantic)                        │  │
│  │  - OpenAPI Spec Auto-generated                          │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER (CORE)                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Use Cases (Application Services)                        │ │
│  │  ├─ ProcessInvoiceUseCase                               │ │
│  │  ├─ ValidateInvoiceUseCase                              │ │
│  │  ├─ ExportInvoicesUseCase                               │ │
│  │  └─ SyncInvoicesUseCase                                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Domain Models (Entities)                                │ │
│  │  ├─ Invoice (Agregado raíz)                             │ │
│  │  ├─ InvoiceItem (Entidad)                               │ │
│  │  ├─ Company (Value Object)                              │ │
│  │  └─ PaymentSchedule (Value Object)                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Domain Services                                         │ │
│  │  ├─ InvoiceCalculationService                           │ │
│  │  ├─ TaxCalculationService                               │ │
│  │  └─ InvoiceValidationService                            │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Repository Interfaces (Ports)                           │ │
│  │  ├─ IInvoiceRepository                                   │ │
│  │  ├─ ICompanyRepository                                   │ │
│  │  └─ IAuditLogRepository                                  │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Repository Implementations (Adapters)                   │ │
│  │  ├─ SQLiteInvoiceRepository                             │ │
│  │  ├─ SQLServerInvoiceRepository                          │ │
│  │  └─ InMemoryInvoiceRepository (testing)                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  External Services                                       │ │
│  │  ├─ OCRService (PaddleOCR, Docling)                     │ │
│  │  ├─ AIService (Transformers, PyTorch)                   │ │
│  │  ├─ FileStorageService                                  │ │
│  │  └─ EmailService / NotificationService                  │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Database (ORM)                                          │ │
│  │  ├─ SQLAlchemy 2.0                                       │ │
│  │  ├─ Alembic (Migrations)                                │ │
│  │  └─ SQLite (dev) / SQL Server (prod)                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### Principios de la Arquitectura

#### 1. **Dependency Inversion Principle (DIP)**
```python
# ❌ MAL: Domain depende de Infrastructure
class InvoiceService:
    def __init__(self):
        self.repo = SQLServerInvoiceRepository()  # Acoplamiento directo

# ✅ BIEN: Domain depende de abstracción
class InvoiceService:
    def __init__(self, repo: IInvoiceRepository):  # Inyección de dependencia
        self.repo = repo
```

#### 2. **Separation of Concerns**
- **Presentation**: Solo renderizado y eventos UI
- **Application**: Orquestación de casos de uso
- **Domain**: Lógica de negocio pura (sin dependencias externas)
- **Infrastructure**: Implementación de detalles técnicos

#### 3. **Domain-Driven Design (DDD)**
- **Agregados**: Agrupación de entidades con raíz (Invoice es raíz de InvoiceItems)
- **Value Objects**: Objetos inmutables sin identidad (Money, Address)
- **Bounded Contexts**: Límites claros entre subdominios

#### 4. **SOLID Principles**
- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

---

## MODOS OPERATIVOS

### Modo 1: Thick Client Standalone

**Características:**
- ✅ Aplicación desktop completa con backend embebido
- ✅ Base de datos SQLite local
- ✅ Procesamiento OCR/AI en máquina del usuario
- ✅ 100% offline (sin dependencia de red)
- ✅ Ideal para: demos, usuarios remotos, testing

**Arquitectura Técnica:**
```
┌─────────────────────────────────────┐
│     Electron/Tauri Container        │
│  ┌───────────────────────────────┐  │
│  │      React Frontend (UI)      │  │
│  └────────────┬──────────────────┘  │
│               │ IPC/Bridge           │
│  ┌────────────▼──────────────────┐  │
│  │  FastAPI (embebido/local)     │  │
│  │  - Puerto localhost:8000      │  │
│  └────────────┬──────────────────┘  │
│               │                      │
│  ┌────────────▼──────────────────┐  │
│  │    SQLite (facturasmodern.db) │  │
│  │    + Archivos PDF/Imgs        │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Ventajas:**
- ⚡ Latencia cero (todo local)
- 🔒 Seguridad (datos no salen de la máquina)
- 📦 Fácil distribución (un ejecutable)
- 🚀 Performance predecible

**Desventajas:**
- 💾 Requiere hardware potente (RAM, GPU para OCR)
- 🔄 Actualizaciones complejas (requiere reinstalación)
- 👥 Sin colaboración multi-usuario
- 💰 Costo por licencia de software IA

---

### Modo 2: Client-Server Centralizado

**Características:**
- ✅ Cliente ligero (solo UI + caché local)
- ✅ Servidor centralizado en Data Center
- ✅ Base de datos SQL Server corporativa
- ✅ Procesamiento OCR/AI en servidores GPU
- ✅ Multi-usuario concurrente

**Arquitectura Técnica:**
```
┌──────────────────────┐              ┌──────────────────────────┐
│   Desktop Client     │              │    Data Center Server    │
│  ┌────────────────┐  │              │  ┌────────────────────┐  │
│  │  React UI      │  │              │  │  FastAPI Cluster   │  │
│  └───────┬────────┘  │              │  │  (Load Balanced)   │  │
│          │ REST API  │              │  └──────┬─────────────┘  │
│  ┌───────▼────────┐  │              │         │                │
│  │ HTTP Client    │  │◄────LAN─────►│  ┌──────▼─────────────┐  │
│  │ (Axios/Fetch)  │  │              │  │  Celery Workers    │  │
│  └───────┬────────┘  │              │  │  (OCR/AI Queue)    │  │
│          │           │              │  └──────┬─────────────┘  │
│  ┌───────▼────────┐  │              │         │                │
│  │ SQLite Cache   │  │              │  ┌──────▼─────────────┐  │
│  │ (Opcional)     │  │              │  │  SQL Server 2022   │  │
│  └────────────────┘  │              │  │  - Multi-user      │  │
└──────────────────────┘              │  │  - Transactions    │  │
                                      │  │  - Replication     │  │
                                      │  └────────────────────┘  │
                                      └──────────────────────────┘
```

**Ventajas:**
- 💻 Cliente ligero (hardware básico)
- 🔄 Actualizaciones centralizadas (sin tocar clientes)
- 👥 Colaboración en tiempo real
- 💰 Licencias IA centralizadas (más económico)
- 🔐 Backup/DR empresarial

**Desventajas:**
- 🌐 Requiere conectividad LAN estable
- ⏱️ Latencia de red (50-200ms típico)
- 🛡️ Requiere seguridad de red (firewall, VPN)
- 🏗️ Infraestructura más compleja

---

### Modo 3: Híbrido (Offline-First con Sync)

**Características:**
- ✅ Cliente con caché local SQLite (trabajo offline)
- ✅ Sincronización bidireccional con servidor
- ✅ Resolución de conflictos automática/manual
- ✅ Ideal para laptops con conectividad intermitente

**Patrón de Sincronización:**
```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Laptop)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Usuario trabaja contra SQLite local (offline)      │ │
│  │     - Cambios marcados con "sync_pending = true"       │ │
│  │     - Timestamp local: "updated_at_local"              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  2. Cuando se detecta red:                             │ │
│  │     - Pull cambios del servidor (desde last_sync_at)   │ │
│  │     - Push cambios locales pendientes                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  3. Resolución de conflictos:                          │ │
│  │     IF updated_at_server > updated_at_local:           │ │
│  │       - Mostrar UI de resolución                       │ │
│  │       - Opciones: Keep Local / Keep Server / Merge     │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

**Campos Adicionales en Modelo:**
```python
class Invoice(SQLModel, table=True):
    # ... campos existentes ...
    
    # Sincronización
    sync_status: str = "synced"  # synced, pending, conflict
    last_sync_at: datetime | None = None
    updated_at_local: datetime
    updated_at_server: datetime | None = None
    version: int = 1  # Versionado optimista
```

---

## ROADMAP DE MIGRACIÓN

### Fase 1: Refactorización Base (Meses 1-3)

#### Objetivos
- ✅ Implementar Clean Architecture
- ✅ Normalizar modelo de datos
- ✅ Crear capa de abstracción (Repositories)
- ✅ Suite de tests automatizados

#### Tareas Detalladas

**Semana 1-2: Setup Proyecto**
- [ ] Crear nuevo repo con estructura clean
- [ ] Configurar Poetry con dependencias
- [ ] Setup pre-commit hooks (black, ruff, mypy)
- [ ] Configurar pytest + coverage

**Semana 3-4: Domain Layer**
- [ ] Definir entidades (Invoice, InvoiceItem, Company)
- [ ] Implementar value objects (Money, Address, TaxId)
- [ ] Crear interfaces de repositorios (IInvoiceRepository)
- [ ] Tests unitarios de dominio (>90% coverage)

**Semana 5-6: Infrastructure Layer**
- [ ] Implementar SQLiteInvoiceRepository
- [ ] Implementar InMemoryRepository (testing)
- [ ] Configurar Alembic para migraciones
- [ ] Crear primera migración (schema normalizado)

**Semana 7-8: Application Layer**
- [ ] Implementar use cases (ProcessInvoiceUseCase)
- [ ] Crear FastAPI endpoints básicos
- [ ] Implementar autenticación JWT
- [ ] Tests de integración (>80% coverage)

**Semana 9-10: Presentation Layer**
- [ ] Migrar de PyWebview a Electron (o Tauri)
- [ ] Refactorizar React UI (componentes limpios)
- [ ] Integrar con nueva API FastAPI
- [ ] Tests e2e con Playwright

**Semana 11-12: Testing y Documentación**
- [ ] Tests de carga (Locust/K6)
- [ ] Documentación OpenAPI completa
- [ ] README y guías de desarrollo
- [ ] Deploy en entorno de staging

---

### Fase 2: Servidor Centralizado (Meses 4-6)

#### Objetivos
- 🎯 Desplegar FastAPI en Data Center
- 🎯 Migrar de SQLite a SQL Server
- 🎯 Implementar cola Celery para OCR
- 🎯 Pruebas piloto con 10 usuarios

#### Tareas Detalladas

**Mes 4: Infraestructura Servidor**
- [ ] Provisionar VM en Data Center (Linux)
- [ ] Instalar Docker + Docker Compose
- [ ] Configurar SQL Server 2022
- [ ] Setup Redis para cache y cola Celery
- [ ] Configurar NGINX como reverse proxy
- [ ] SSL/TLS con certificados internos

**Mes 5: Backend Servidor**
- [ ] Implementar SQLServerInvoiceRepository
- [ ] Migración de datos SQLite → SQL Server
- [ ] Configurar Celery workers (OCR/AI)
- [ ] Implementar sistema de colas (RabbitMQ/Redis)
- [ ] Monitoreo con Prometheus + Grafana

**Mes 6: Rollout Piloto**
- [ ] Crear cliente híbrido (modo server)
- [ ] Migrar 5 usuarios voluntarios
- [ ] Recolectar feedback y métricas
- [ ] Ajustes de performance
- [ ] Documentación de troubleshooting

---

### Fase 3: Sincronización Offline-First (Meses 7-9)

#### Objetivos
- 🎯 Implementar sync bidireccional
- 🎯 Resolución de conflictos
- 🎯 Modo híbrido operativo

#### Tareas Detalladas

**Mes 7: Diseño y Prototipo**
- [ ] Diseñar protocolo de sync (delta updates)
- [ ] Implementar detección de conflictos
- [ ] Prototipo de UI para resolución manual
- [ ] Tests de escenarios de conflicto

**Mes 8: Implementación**
- [ ] Endpoints API sync (pull/push deltas)
- [ ] Lógica cliente de sincronización
- [ ] Almacenamiento local de cambios pendientes
- [ ] Retry automático con backoff exponencial

**Mes 9: Testing y Optimización**
- [ ] Tests de conectividad intermitente
- [ ] Benchmark de performance sync
- [ ] Compresión de payloads (gzip/brotli)
- [ ] Rollout a 50% de usuarios

---

### Fase 4: Optimización y Escalado (Meses 10-12)

#### Objetivos
- 🚀 Escalabilidad horizontal
- 🚀 Monitoreo avanzado
- 🚀 100% usuarios migrados

#### Tareas Detalladas

**Mes 10: Performance**
- [ ] Profiling y optimización de queries
- [ ] Cache agresivo (Redis)
- [ ] CDN para assets estáticos
- [ ] Optimización de modelos AI (ONNX, TorchScript)

**Mes 11: Escalado**
- [ ] Load balancing (NGINX/HAProxy)
- [ ] Auto-scaling de workers Celery
- [ ] Database connection pooling (PgBouncer)
- [ ] Replicación de SQL Server (HA)

**Mes 12: Rollout Final**
- [ ] Migración del 100% de usuarios
- [ ] Descomisionar versión antigua
- [ ] Celebración del equipo 🎉
- [ ] Post-mortem y lecciones aprendidas

---

## PRINCIPIOS ARQUITECTÓNICOS

### 1. **Offline-First**
> La aplicación DEBE funcionar sin conexión. La red es una mejora, no un requisito.

**Implementación:**
- Caché local SQLite siempre presente
- Sincronización en background
- UI optimista (aplicar cambios localmente primero)

### 2. **API-First**
> Todo acceso a lógica de negocio pasa por API bien definida.

**Implementación:**
- Cliente desktop consume misma API que cliente web
- OpenAPI spec como contrato
- Versionado semántico de API (v1, v2)

### 3. **Database Agnostic**
> El core del sistema NO debe depender de una BD específica.

**Implementación:**
- Patrón Repository con interfaces
- Uso exclusivo de SQLAlchemy Core (sin dialectos específicos)
- Tests contra múltiples backends

### 4. **Test-Driven Development (TDD)**
> Código nuevo requiere test primero.

**Implementación:**
- Tests unitarios: >80% coverage
- Tests integración: >70% coverage
- Tests e2e: happy paths + edge cases

### 5. **Fail-Fast & Graceful Degradation**
> Detectar errores temprano, degradar funcionalidad sin colapsar.

**Implementación:**
- Validación estricta en boundaries (Pydantic)
- Circuit breakers para servicios externos
- Modo offline automático si servidor inaccesible

### 6. **Security by Design**
> Seguridad no es opcional, es parte del diseño.

**Implementación:**
- Autenticación JWT con refresh tokens
- RBAC (Role-Based Access Control)
- Encriptación AES-256 de campos sensibles
- Audit logs inmutables

---

## DECISIONES CLAVE

### ADR-001: Electron vs Tauri vs PyWebview

**Contexto:**  
Necesitamos framework para empaquetar aplicación desktop cross-platform.

**Opciones Evaluadas:**
1. **PyWebview** (actual)
2. **Electron**
3. **Tauri**

**Decisión: Electron**

**Justificación:**
- ✅ Ecosistema maduro y probado (VS Code, Slack, Discord)
- ✅ Excelente tooling (electron-builder, electron-updater)
- ✅ Fácil integración con React existente
- ✅ Auto-update nativo
- ✅ Amplia documentación y comunidad

**Consecuencias:**
- ⚠️ Bundle más pesado (~150MB vs ~10MB PyWebview)
- ✅ Mejor mantenibilidad a largo plazo
- ✅ Facilita migración a web app futura

---

### ADR-002: SQLite + SQL Server (Dual Support)

**Contexto:**  
Necesitamos soportar desarrollo local (SQLite) y producción enterprise (SQL Server).

**Decisión: Abstracción total con SQLAlchemy + Alembic**

**Implementación:**
```python
# config.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./facturasmodern.db"  # Default desarrollo
)
# Producción: "mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+18+for+SQL+Server"

# repositories.py
class InvoiceRepository(IInvoiceRepository):
    def __init__(self, session: Session):
        self.session = session  # Agnóstico de dialecto
```

**Migraciones:**
```bash
# Generar migración (funciona para ambos)
alembic revision --autogenerate -m "Add companies table"

# Aplicar en SQLite (dev)
alembic upgrade head

# Aplicar en SQL Server (prod)
DATABASE_URL="mssql+pyodbc://..." alembic upgrade head
```

**Diferencias a Considerar:**

| Característica | SQLite | SQL Server | Estrategia |
|----------------|--------|------------|------------|
| **Auto-increment** | `AUTOINCREMENT` | `IDENTITY` | SQLAlchemy abstrae |
| **Boolean** | `INTEGER (0/1)` | `BIT` | SQLAlchemy abstrae |
| **DateTime** | `TEXT (ISO 8601)` | `DATETIME2` | SQLAlchemy abstrae |
| **JSON** | `TEXT` (sin validación) | `NVARCHAR(MAX)` + validación | Usar `JSON` type de SQLAlchemy |
| **Transactions** | File-level lock | Row-level lock | No afecta código |
| **Full-Text Search** | FTS5 extension | Built-in | Abstracción en Repository |

---

### ADR-003: REST vs GraphQL

**Contexto:**  
Definir protocolo de comunicación cliente-servidor.

**Decisión: REST API (JSON) con posible GraphQL futuro**

**Justificación:**
- ✅ Simplicidad para equipo (menor curva de aprendizaje)
- ✅ Tooling maduro (FastAPI auto-genera OpenAPI)
- ✅ Cache HTTP estándar (NGINX, Varnish)
- ✅ Suficiente para casos de uso actuales

**Futuro Opcional:**
- GraphQL si necesitamos queries complejas con múltiples relaciones
- Usar Strawberry (GraphQL para FastAPI)

---

### ADR-004: Celery vs RQ vs FastAPI Background Tasks

**Contexto:**  
Procesamiento asíncrono de OCR/AI (tareas largas).

**Decisión: Celery + Redis**

**Justificación:**
- ✅ Robusto y probado para producción
- ✅ Soporta tareas largas (>30min)
- ✅ Reintentos automáticos y DLQ (Dead Letter Queue)
- ✅ Monitoreo con Flower
- ✅ Escalado horizontal fácil (agregar workers)

**Alternativas Descartadas:**
- ❌ **RQ**: Más simple pero menos features (no schedules, no chord)
- ❌ **FastAPI BackgroundTasks**: Solo para tareas cortas (<30s)

---

## RIESGOS Y MITIGACIONES

### Riesgo 1: Complejidad de Migración de Datos

**Probabilidad:** Alta  
**Impacto:** Alto  

**Descripción:**  
Migrar 1000s de facturas de SQLite a SQL Server con datos inconsistentes.

**Mitigación:**
1. **Script de validación pre-migración**
   ```python
   # validate_data.py
   def validate_invoice(invoice):
       assert invoice.emisor_ruc, "RUC emisor vacío"
       assert invoice.total >= 0, "Total negativo"
       # ... más validaciones
   ```
2. **Migración incremental** (por lotes de 1000)
3. **Rollback automático** si >5% de registros fallan
4. **Ambiente staging** para testing previo

---

### Riesgo 2: Performance de Sincronización

**Probabilidad:** Media  
**Impacto:** Alto  

**Descripción:**  
Sync de 10,000 facturas puede tomar >5min y bloquear UI.

**Mitigación:**
1. **Sync incremental** (solo cambios desde last_sync_at)
2. **Pagination** (100 registros por request)
3. **Background sync** (no bloquea UI)
4. **Indicador de progreso** visual
5. **Compresión** de payloads (gzip reduce ~70%)

---

### Riesgo 3: Concurrencia y Conflictos

**Probabilidad:** Media  
**Impacto:** Medio  

**Descripción:**  
Dos usuarios editan misma factura simultáneamente.

**Mitigación:**
1. **Optimistic Locking** con campo `version`
   ```python
   # Si versiones difieren, lanzar ConflictError
   if invoice.version != expected_version:
       raise ConflictError("Factura modificada por otro usuario")
   ```
2. **UI de resolución** clara
3. **Last-Write-Wins** como fallback (con warning)

---

### Riesgo 4: Dependencia de Modelos AI Pesados

**Probabilidad:** Baja  
**Impacto:** Alto  

**Descripción:**  
Modelos Transformers de 2GB+ ralentizan startup y consumen RAM.

**Mitigación:**
1. **Lazy loading** (cargar solo cuando se usa OCR)
2. **Quantization** de modelos (ONNX, INT8)
3. **Model cache** compartido entre workers
4. **Fallback a OCR ligero** (Tesseract) si no hay GPU

---

### Riesgo 5: Seguridad de Red Interna

**Probabilidad:** Media  
**Impacto:** Crítico  

**Descripción:**  
Datos sensibles (facturas, RUCs) expuestos en LAN corporativa.

**Mitigación:**
1. **TLS 1.3** obligatorio (HTTPS)
2. **Mutual TLS** (cliente y servidor con certificados)
3. **VPN** para acceso remoto
4. **Firewall** (solo puerto 443 expuesto)
5. **Auditoría** de accesos (quién accedió a qué)

---

## MÉTRICAS DE ÉXITO

### KPIs Técnicos

| Métrica | Baseline Actual | Objetivo 6 Meses | Objetivo 12 Meses |
|---------|-----------------|------------------|-------------------|
| **Cobertura Tests** | 0% | 80% | 85% |
| **Tiempo Procesamiento OCR** | 45s (CPU) | 15s (GPU) | 10s (GPU opt) |
| **Latencia API (p95)** | N/A | <500ms | <200ms |
| **Uptime Servidor** | N/A | 99% | 99.5% |
| **Usuarios Concurrentes** | 1 | 50 | 100+ |
| **Tamaño Bundle Cliente** | 200MB | 150MB | 120MB |

### KPIs de Negocio

| Métrica | Baseline | Objetivo |
|---------|----------|----------|
| **Tiempo Entrenamiento Usuario** | 2 días | 4 horas |
| **Errores de Extracción** | 15% | <5% |
| **Facturas/Día por Usuario** | 50 | 200 |
| **Costo Infraestructura/Usuario/Mes** | N/A | <$20 USD |

---

## PRÓXIMOS PASOS

### Inmediatos (Esta Semana)
1. ✅ Revisar y aprobar esta visión arquitectónica
2. 📝 Definir equipo de desarrollo y roles
3. 📦 Crear repo base con estructura clean
4. 📅 Planificar sprint 1 (Domain Layer)

### Corto Plazo (Mes 1)
1. 🏗️ Implementar capas Domain e Infrastructure
2. 🧪 Suite de tests unitarios
3. 📊 Primer migración Alembic (schema normalizado)
4. 📖 Documentación de API (OpenAPI)

### Mediano Plazo (Mes 3)
1. 🖥️ Migrar a Electron + React refactorizado
2. 🔌 API FastAPI funcional (CRUD completo)
3. 🎯 Demo end-to-end funcionando
4. 📈 Métricas de performance baseline

---

## CONCLUSIÓN

Esta arquitectura evolutiva permite:

✅ **Flexibilidad**: Soporta múltiples modos operativos (standalone, client-server, híbrido)  
✅ **Escalabilidad**: De 1 usuario a 100+ sin reescritura  
✅ **Mantenibilidad**: Clean Architecture facilita cambios futuros  
✅ **Testabilidad**: Cobertura alta con tests automatizados  
✅ **Migrabilidad**: SQLite → SQL Server sin dolor  
✅ **Seguridad**: Diseñada desde el inicio, no como parche  

**Inversión estimada:**  
- 👨‍💻 Equipo: 2-3 desarrolladores  
- ⏰ Tiempo: 12 meses para rollout completo  
- 💰 Costo: ~$150k USD (salarios + infra)  

**ROI esperado:**  
- ⚡ 4x productividad de usuarios  
- 🐛 -70% bugs en producción  
- 💾 -50% costo de licencias IA (centralización)  
- 🚀 Plataforma lista para crecimiento 10x  

---

**Documento:** v1.0  
**Fecha:** 2025-11-18  
**Autor:** Equipo de Arquitectura  
**Próxima Revisión:** 2026-02-18 (3 meses)
