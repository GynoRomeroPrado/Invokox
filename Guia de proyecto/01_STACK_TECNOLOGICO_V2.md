# 01 - STACK TECNOLÓGICO V2: ANÁLISIS Y DECISIONES

## TABLA DE CONTENIDOS

1. [Visión General](#visión-general)
2. [Framework Desktop](#framework-desktop)
3. [Backend Framework](#backend-framework)
4. [Base de Datos](#base-de-datos)
5. [ORM y Migraciones](#orm-y-migraciones)
6. [Frontend Framework](#frontend-framework)
7. [Procesamiento Asíncrono](#procesamiento-asíncrono)
8. [AI/OCR Stack](#aiocr-stack)
9. [Testing Framework](#testing-framework)
10. [DevOps y Deployment](#devops-y-deployment)
11. [Stack Final Recomendado](#stack-final-recomendado)

---

## VISIÓN GENERAL

### Criterios de Evaluación

Cada tecnología se evalúa según:

| Criterio | Peso | Descripción |
|----------|------|-------------|
| **Madurez** | 20% | Estabilidad, versión, adopción en producción |
| **Ecosistema** | 15% | Librerías, plugins, comunidad, documentación |
| **Performance** | 20% | Velocidad, uso de recursos, escalabilidad |
| **Developer Experience** | 15% | Curva de aprendizaje, tooling, debugging |
| **Mantenibilidad** | 15% | Facilidad de actualización, backward compatibility |
| **Costo** | 10% | Licencias, infraestructura, desarrolladores |
| **Dual-Mode Support** | 5% | Capacidad de funcionar standalone y client-server |

**Escala de Puntuación:** 1-10 (1=Pobre, 5=Adecuado, 10=Excelente)

---

## FRAMEWORK DESKTOP

### Opciones Evaluadas

#### 1. **PyWebview** (Actual)

**Descripción:**  
Framework ligero que usa webview nativo del sistema (WebKit en macOS, EdgeHTML/Chromium en Windows).

**Pros:**
- ✅ **Muy ligero** (~5-10MB bundle)
- ✅ **Fácil integración con Python** (API nativa)
- ✅ **Sin dependencias externas** pesadas
- ✅ **Rápido startup** (<2s)

**Contras:**
- ❌ **Ecosistema limitado** (pocas librerías, plugins)
- ❌ **Sin auto-update** nativo (requiere implementación manual)
- ❌ **Inconsistencias cross-platform** (WebKit vs Chromium)
- ❌ **Debugging complejo** (sin DevTools integrado)
- ❌ **Comunidad pequeña** (<2k stars GitHub)

**Evaluación:**

| Criterio | Puntuación | Justificación |
|----------|------------|---------------|
| Madurez | 6/10 | Estable pero v5.1 es reciente, no muy battle-tested |
| Ecosistema | 4/10 | Pocas librerías, documentación básica |
| Performance | 9/10 | Excelente, muy ligero |
| Developer Experience | 5/10 | Debugging difícil, tooling limitado |
| Mantenibilidad | 6/10 | Actualizaciones poco frecuentes |
| Costo | 10/10 | Gratis, open source |
| Dual-Mode Support | 5/10 | Requiere mucho trabajo para modo server |
| **TOTAL** | **6.3/10** | |

---

#### 2. **Electron**

**Descripción:**  
Framework que empaqueta Chromium + Node.js, usado por VS Code, Slack, Discord, Teams.

**Pros:**
- ✅ **Ecosistema masivo** (plugins, templates, best practices)
- ✅ **DevTools integrado** (Chrome DevTools completo)
- ✅ **Auto-update nativo** (electron-updater)
- ✅ **Cross-platform consistente** (mismo Chromium en todos los OS)
- ✅ **Comunidad enorme** (100k+ stars GitHub)
- ✅ **Battle-tested** en producción (millones de usuarios)

**Contras:**
- ❌ **Bundle pesado** (~150-200MB con dependencias)
- ❌ **Consumo de RAM alto** (~150-300MB idle)
- ❌ **Startup lento** (3-5s primera vez)
- ❌ **Actualizaciones de Chromium** frecuentes (seguridad)

**Evaluación:**

| Criterio | Puntuación | Justificación |
|----------|------------|---------------|
| Madurez | 10/10 | v28+, usado por Microsoft, Slack, etc. |
| Ecosistema | 10/10 | Enorme, todo está resuelto |
| Performance | 6/10 | Pesado pero aceptable para desktop |
| Developer Experience | 10/10 | Excelente tooling y debugging |
| Mantenibilidad | 8/10 | Actualizaciones frecuentes (seguridad) |
| Costo | 9/10 | Gratis, pero mayor consumo de recursos |
| Dual-Mode Support | 9/10 | Fácil integrar con backend externo |
| **TOTAL** | **8.9/10** | |

---

#### 3. **Tauri**

**Descripción:**  
Framework moderno que usa webview nativo + backend Rust. Alternativa "ligera" a Electron.

**Pros:**
- ✅ **Muy ligero** (~15-30MB bundle)
- ✅ **Seguro por diseño** (Rust + sandboxing)
- ✅ **Performance excelente** (startup <1s, RAM ~50MB)
- ✅ **Auto-update nativo**
- ✅ **Moderno y en crecimiento** (comunidad activa)

**Contras:**
- ❌ **Menos maduro** (v1.0 recién en 2023)
- ❌ **Ecosistema en desarrollo** (menos plugins que Electron)
- ❌ **Curva de aprendizaje Rust** (si necesitas customizar)
- ❌ **Inconsistencias webview** (como PyWebview)
- ❌ **Menos casos de uso en producción**

**Evaluación:**

| Criterio | Puntuación | Justificación |
|----------|------------|---------------|
| Madurez | 7/10 | v1.0+ pero reciente, menos battle-tested |
| Ecosistema | 6/10 | Creciendo rápido pero aún limitado |
| Performance | 10/10 | Excelente, mejor que todos |
| Developer Experience | 7/10 | Bueno pero requiere aprender Rust |
| Mantenibilidad | 8/10 | Moderna, actualizaciones limpias |
| Costo | 10/10 | Gratis, menor consumo de recursos |
| Dual-Mode Support | 8/10 | Diseñado para separar frontend/backend |
| **TOTAL** | **8.0/10** | |

---

### Comparativa Directa

| Característica | PyWebview | Electron | Tauri |
|----------------|-----------|----------|-------|
| **Tamaño Bundle** | 5-10MB | 150-200MB | 15-30MB |
| **RAM (Idle)** | 30-50MB | 150-300MB | 50-80MB |
| **Startup Time** | <2s | 3-5s | <1s |
| **DevTools** | ❌ | ✅ | ✅ |
| **Auto-Update** | ❌ | ✅ | ✅ |
| **Cross-Platform** | ⚠️ Inconsistente | ✅ Consistente | ⚠️ Inconsistente |
| **Comunidad** | 🟡 Pequeña | 🟢 Enorme | 🟡 Creciendo |
| **Casos de Uso** | Apps simples | Apps complejas | Apps modernas |
| **Backend Integration** | 🟢 Python nativo | 🟡 Node.js | 🟢 Rust/CLI |

---

### Decisión: **Electron**

**Justificación:**

1. **Ecosistema maduro**: Resolver problemas comunes ya está documentado.
2. **DevTools esencial**: Para debugging de React + comunicación API.
3. **Auto-update crítico**: Desplegar fixes sin reinstalación manual.
4. **Dual-mode friendly**: Electron puede consumir API local (localhost) o remota (Data Center) sin cambios.
5. **Equipo familiarizado**: Si tienen experiencia con React, Node.js es natural.

**Trade-off aceptado:**  
Bundle de 150MB es aceptable para aplicación enterprise en 2025. PCs modernos tienen 8GB+ RAM.

**Plan de Migración:**
```bash
# Fase 1: Setup Electron
npm install electron electron-builder electron-updater

# Fase 2: Integrar React existente
# - Mover src/frontend a electron-app/renderer
# - Configurar preload.js para IPC

# Fase 3: Backend adaptado
# - FastAPI corriendo en puerto local (8000)
# - Electron inicia proceso Python en background
# - Frontend consume http://localhost:8000
```

---

## BACKEND FRAMEWORK

### Opciones Evaluadas

#### 1. **Flask**

**Pros:**
- ✅ Minimalista, fácil de aprender
- ✅ Flexible (no opinionado)
- ✅ Comunidad enorme

**Contras:**
- ❌ Sin async nativo (solo con extensiones)
- ❌ Sin validación automática de tipos
- ❌ Sin auto-generación de docs

**Evaluación:** 7.2/10

---

#### 2. **Django**

**Pros:**
- ✅ Batteries-included (ORM, admin, auth)
- ✅ Muy maduro y estable
- ✅ Excelente para CRUD

**Contras:**
- ❌ Pesado para APIs (Django REST Framework)
- ❌ Async limitado (ASGI reciente)
- ❌ Opinionado (estructura rígida)

**Evaluación:** 7.5/10

---

#### 3. **FastAPI** ⭐

**Pros:**
- ✅ **Async nativo** (ASGI, performance superior)
- ✅ **Validación automática** con Pydantic
- ✅ **Auto-generación OpenAPI** (docs interactivas)
- ✅ **Type hints** (mejor DX y tooling)
- ✅ **Moderno** (diseñado para 2020+)
- ✅ **Rápido** (comparable a Node.js/Go)

**Contras:**
- ❌ Menos maduro que Flask/Django (pero v0.100+ es estable)
- ❌ Ecosistema más pequeño (aunque creciendo rápido)

**Evaluación:**

| Criterio | Puntuación |
|----------|------------|
| Madurez | 8/10 |
| Ecosistema | 8/10 |
| Performance | 10/10 |
| Developer Experience | 10/10 |
| Mantenibilidad | 9/10 |
| Costo | 10/10 |
| Dual-Mode Support | 10/10 |
| **TOTAL** | **9.3/10** |

---

### Decisión: **FastAPI**

**Justificación:**

1. **Async esencial**: OCR/AI tarda 10-30s, async evita bloquear otros requests.
2. **Type safety**: Pydantic valida datos automáticamente.
3. **OpenAPI gratis**: Documentación siempre actualizada.
4. **Dual-mode perfecto**: Mismo código FastAPI corre en Electron (embebido) o Docker (servidor).

**Código Ejemplo:**

```python
# main.py - FastAPI que funciona en ambos modos
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI(title="Facturas API", version="2.0.0")

# Dependency Injection (DB session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint que funciona igual en standalone y server
@app.post("/api/v1/invoices", response_model=InvoiceOut)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db)
):
    # Use case pattern (Clean Architecture)
    use_case = CreateInvoiceUseCase(
        repo=InvoiceRepository(db),
        ocr_service=OCRService()
    )
    result = await use_case.execute(invoice)
    return result

# Modo Standalone: uvicorn main:app --host 127.0.0.1 --port 8000
# Modo Server: uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## BASE DE DATOS

### Desarrollo: SQLite

**Ventajas para Dev/Standalone:**
- ✅ Zero-config (archivo único)
- ✅ Portable (copiar archivo = backup)
- ✅ Rápido para datasets pequeños (<100GB)
- ✅ ACID compliant
- ✅ Testing rápido (in-memory)

**Limitaciones:**
- ❌ Single-writer (lock de archivo)
- ❌ Sin replicación nativa
- ❌ Sin full-text search avanzado
- ❌ Tipos limitados (sin JSON nativo hasta v3.38)

---

### Producción: SQL Server

**Ventajas para Server:**
- ✅ Multi-usuario robusto (row-level locking)
- ✅ Escalabilidad horizontal (Always On, clustering)
- ✅ Backup/restore empresarial
- ✅ Integración con ecosistema Microsoft (Power BI, SSIS)
- ✅ Full-text search avanzado
- ✅ JSON nativo (FOR JSON, OPENJSON)
- ✅ Seguridad enterprise (RLS, encryption)

**Limitaciones:**
- ❌ Licencia costosa (Express gratis hasta 10GB)
- ❌ Solo Windows/Linux (no macOS nativo)
- ❌ Configuración compleja

---

### Alternativa Considerada: PostgreSQL

**Por qué NO PostgreSQL:**

| Criterio | PostgreSQL | SQL Server |
|----------|------------|------------|
| Costo | ✅ Gratis | ⚠️ Licencia ($$$) |
| JSON | ✅ JSONB nativo | ✅ JSON nativo |
| Full-Text | ✅ Avanzado | ✅ Avanzado |
| Windows Support | ⚠️ Secundario | ✅ Nativo |
| Ecosistema MS | ❌ Limitado | ✅ Completo |
| Python ORM | ✅ Excelente (psycopg3) | ✅ Bueno (pyodbc) |

**Decisión:** SQL Server por **mandato corporativo** (asumido por contexto).  
Si no hay restricción, **PostgreSQL sería técnicamente superior y gratis**.

---

### Estrategia Dual-DB

```python
# config.py
import os

# Modo standalone (default)
DATABASE_URL = "sqlite:///./data/facturas.db"

# Modo server (override con variable de entorno)
if os.getenv("MODE") == "server":
    DATABASE_URL = (
        "mssql+pyodbc://user:password@server:1433/facturas_db"
        "?driver=ODBC+Driver+18+for+SQL+Server"
    )

# SQLAlchemy engine (agnóstico de dialecto)
engine = create_engine(DATABASE_URL, echo=True)
```

**Compatibilidad:**

| Feature | SQLite | SQL Server | SQLAlchemy Abstraction |
|---------|--------|------------|------------------------|
| **Auto-increment** | `INTEGER PRIMARY KEY` | `INT IDENTITY(1,1)` | `id: int = Field(primary_key=True)` |
| **Boolean** | `INTEGER` (0/1) | `BIT` | `active: bool` |
| **DateTime** | `TEXT` (ISO8601) | `DATETIME2` | `created_at: datetime` |
| **JSON** | `TEXT` | `NVARCHAR(MAX)` | `data: dict = Field(sa_column=Column(JSON))` |
| **UUID** | `TEXT` | `UNIQUEIDENTIFIER` | `uuid: UUID` |

---

## ORM Y MIGRACIONES

### ORM: SQLModel ⭐

**Ventajas:**
- ✅ **Pydantic + SQLAlchemy** (lo mejor de ambos)
- ✅ **Type hints nativos** (mejor IDE support)
- ✅ **Validación automática** (Pydantic)
- ✅ **Migraciones Alembic** (compatible)
- ✅ **Creado por creador de FastAPI** (integración perfecta)

**Ejemplo:**

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Company(SQLModel, table=True):
    """Emisor o Receptor de factura."""
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_id: str = Field(index=True, unique=True)  # RUC
    name: str
    address: Optional[str] = None
    
    # Relación 1:N con facturas
    issued_invoices: list["Invoice"] = Relationship(
        back_populates="issuer",
        sa_relationship_kwargs={"foreign_keys": "Invoice.issuer_id"}
    )

class Invoice(SQLModel, table=True):
    """Factura normalizada."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones (FKs)
    issuer_id: int = Field(foreign_key="company.id")
    receiver_id: int = Field(foreign_key="company.id")
    
    # Datos documento
    document_type: str  # FACTURA, BOLETA, NOTA_CREDITO
    series_number: str
    issue_date: datetime
    due_date: Optional[datetime] = None
    currency: str = "PEN"
    
    # Totales
    subtotal: float
    tax: float
    total: float
    
    # Metadata
    file_path: str = Field(unique=True, index=True)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(ge=0.0, le=1.0)
    status: str = Field(default="PENDING")  # PENDING, COMPLETED, ERROR
    
    # Relaciones
    issuer: Company = Relationship(
        back_populates="issued_invoices",
        sa_relationship_kwargs={"foreign_keys": "Invoice.issuer_id"}
    )
    items: list["InvoiceItem"] = Relationship(back_populates="invoice")

class InvoiceItem(SQLModel, table=True):
    """Línea de detalle de factura."""
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoice.id")
    
    code: Optional[str] = None
    description: str
    quantity: float
    unit_price: float
    subtotal: float
    tax: float
    total: float
    
    # Relación
    invoice: Invoice = Relationship(back_populates="items")
```

---

### Migraciones: Alembic

**Setup:**

```bash
# Instalar
pip install alembic

# Inicializar
alembic init alembic

# Configurar env.py
# target_metadata = SQLModel.metadata

# Generar migración auto
alembic revision --autogenerate -m "Create companies and invoices tables"

# Aplicar
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Ventajas:**
- ✅ Auto-detección de cambios en modelos
- ✅ Versionado de schema (Git-friendly)
- ✅ Rollback seguro
- ✅ Funciona con SQLite y SQL Server

---

## FRONTEND FRAMEWORK

### Decisión: **React 18 + TypeScript** (Mantener)

**Justificación:**
- ✅ Ya existe código React funcional
- ✅ Ecosistema maduro (millones de paquetes)
- ✅ TypeScript = type safety
- ✅ Hooks modernos (useState, useEffect, custom hooks)
- ✅ React Query ideal para sincronización

**No cambiar a:**
- ❌ Vue: Requiere reescritura completa
- ❌ Svelte: Ecosistema más pequeño
- ❌ Angular: Más pesado y opinionado

**Stack Frontend Actualizado:**

```
React 18.2+
├── TypeScript 5.0+
├── Vite 5.0 (build tool)
├── TailwindCSS 4.0 (styling)
├── Zustand 4.0 (estado global)
├── TanStack Query 5.0 (data fetching + cache)
├── React Hook Form 7.0 (formularios)
├── Zod (validación runtime)
└── React Router 6.0 (navegación)
```

**Mejoras Clave:**

1. **TanStack Query (React Query)** para data fetching:

```typescript
// Antes: useState + useEffect manual
const [invoices, setInvoices] = useState([]);
useEffect(() => {
  fetch('/api/invoices').then(r => r.json()).then(setInvoices);
}, []);

// Después: React Query (cache, refetch, invalidation automático)
const { data: invoices, isLoading } = useQuery({
  queryKey: ['invoices'],
  queryFn: () => api.invoices.list(),
  staleTime: 5 * 60 * 1000, // 5 min cache
});
```

2. **Zod para validación runtime:**

```typescript
import { z } from 'zod';

const InvoiceSchema = z.object({
  issuer_ruc: z.string().length(11, "RUC debe tener 11 dígitos"),
  total: z.number().positive("Total debe ser positivo"),
  issue_date: z.date(),
});

type Invoice = z.infer<typeof InvoiceSchema>;
```

3. **Zustand para estado global simple:**

```typescript
// store.ts
import { create } from 'zustand';

interface AppState {
  mode: 'standalone' | 'server';
  apiBaseUrl: string;
  setMode: (mode: 'standalone' | 'server') => void;
}

export const useAppStore = create<AppState>((set) => ({
  mode: 'standalone',
  apiBaseUrl: 'http://localhost:8000',
  setMode: (mode) => set({ 
    mode,
    apiBaseUrl: mode === 'standalone' 
      ? 'http://localhost:8000'
      : 'https://server.company.local'
  }),
}));
```

---

## PROCESAMIENTO ASÍNCRONO

### Decisión: **Celery + Redis**

**Justificación:**

1. **Tareas largas**: OCR puede tardar 30s-5min (no apto para request HTTP)
2. **Escalabilidad**: Agregar workers es trivial
3. **Reintentos**: Automático si falla (network, OOM, etc)
4. **Prioridades**: Facturas urgentes primero
5. **Monitoring**: Flower (UI web para Celery)

**Alternativas Descartadas:**

| Opción | Pros | Contras | Decisión |
|--------|------|---------|----------|
| **FastAPI BackgroundTasks** | Simple | Solo tareas cortas (<30s) | ❌ |
| **RQ (Redis Queue)** | Más simple que Celery | Sin schedules, sin chord | ❌ |
| **Dramatiq** | Moderno, ligero | Menos ecosistema | ❌ |
| **Celery** | Battle-tested, completo | Configuración compleja | ✅ |

**Arquitectura:**

```
┌─────────────────┐
│  FastAPI (API)  │
│  - Recibe POST  │
│  - Encola tarea │
└────────┬────────┘
         │ Redis (broker)
         ▼
┌─────────────────┐
│ Celery Worker 1 │◄─── GPU para OCR
│ - Procesa OCR   │
└─────────────────┘
┌─────────────────┐
│ Celery Worker 2 │◄─── CPU
│ - Backup, etc   │
└─────────────────┘
```

**Código Ejemplo:**

```python
# tasks.py
from celery import Celery

celery_app = Celery(
    "facturas",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@celery_app.task(bind=True, max_retries=3)
def process_invoice_ocr(self, invoice_id: int):
    """Procesar factura con OCR (tarea larga)."""
    try:
        invoice = get_invoice(invoice_id)
        result = run_paddle_ocr(invoice.file_path)
        update_invoice(invoice_id, result)
        return {"status": "success", "invoice_id": invoice_id}
    except Exception as exc:
        # Retry con backoff exponencial
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

# api.py
@app.post("/api/v1/invoices/{id}/process")
async def trigger_ocr(id: int):
    task = process_invoice_ocr.delay(id)
    return {"task_id": task.id, "status": "queued"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {"status": task.state, "result": task.result}
```

---

## AI/OCR STACK

### Stack Actual (Mantener con Optimizaciones)

```python
# OCR Engines (en orden de prioridad)
1. PaddleOCR (principal)
   - Mejor precisión para facturas
   - GPU-accelerated
   - Soporta tablas

2. Docling (IBM Research)
   - Extracción de documentos estructurados
   - Bueno para layout complejo

3. Tesseract (fallback)
   - CPU-only
   - Rápido pero menos preciso
```

**Optimizaciones Propuestas:**

1. **Lazy loading** (cargar solo cuando se usa):

```python
# Antes: Import al inicio (lento)
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='es')

# Después: Lazy loading
class OCRService:
    _paddle_instance = None
    
    @property
    def paddle(self):
        if self._paddle_instance is None:
            from paddleocr import PaddleOCR
            self._paddle_instance = PaddleOCR(use_angle_cls=True, lang='es')
        return self._paddle_instance
```

2. **Model quantization** (reducir tamaño/RAM):

```bash
# Convertir modelos a ONNX (más rápido, menor RAM)
python -m paddleocr.tools.export_model \
  --model_dir paddle_ocr_models \
  --save_inference_dir onnx_models \
  --quantization True  # INT8 quantization
```

3. **Batch processing** (procesar múltiples páginas juntas):

```python
async def process_batch(pdf_paths: list[str]):
    """Procesar lote de PDFs en una sola inferencia."""
    images = [pdf_to_image(p) for p in pdf_paths]
    results = ocr_service.batch_predict(images)  # GPU eficiente
    return results
```

---

## TESTING FRAMEWORK

### Stack Recomendado

```python
# Testing
pytest                # Framework principal
pytest-asyncio        # Tests async/await
pytest-cov            # Cobertura de código
pytest-mock           # Mocking
pytest-xdist          # Parallelización
faker                 # Datos fake realistas
factory-boy           # Fixtures complejas

# E2E Testing
playwright            # Browser automation (React UI)
```

**Estructura de Tests:**

```
tests/
├── unit/                   # Tests unitarios rápidos (<1s)
│   ├── domain/
│   │   ├── test_invoice.py
│   │   ├── test_company.py
│   │   └── test_money.py
│   └── services/
│       ├── test_ocr_service.py
│       └── test_calculation_service.py
│
├── integration/            # Tests con BD real (~1-5s)
│   ├── test_invoice_repository.py
│   ├── test_sync_service.py
│   └── test_api_endpoints.py
│
├── e2e/                    # Tests end-to-end (~10-60s)
│   ├── test_invoice_flow.py
│   ├── test_export_flow.py
│   └── test_sync_flow.py
│
└── fixtures/               # Datos de prueba
    ├── sample_invoices.pdf
    └── factories.py
```

**Ejemplo Test Unitario:**

```python
# tests/unit/domain/test_invoice.py
import pytest
from domain.entities import Invoice, InvoiceItem, Money

def test_invoice_calculate_total():
    """Total de factura = suma de items."""
    item1 = InvoiceItem(
        description="Producto A",
        quantity=2,
        unit_price=Money(100, "PEN")
    )
    item2 = InvoiceItem(
        description="Producto B",
        quantity=1,
        unit_price=Money(50, "PEN")
    )
    
    invoice = Invoice(items=[item1, item2])
    assert invoice.subtotal == Money(250, "PEN")
    assert invoice.tax == Money(45, "PEN")  # 18% IGV
    assert invoice.total == Money(295, "PEN")

def test_invoice_validation_fails_negative_total():
    """No permite totales negativos."""
    with pytest.raises(ValueError, match="Total no puede ser negativo"):
        Invoice(subtotal=Money(-100, "PEN"))
```

**Ejemplo Test Integración:**

```python
# tests/integration/test_invoice_repository.py
import pytest
from sqlmodel import Session, create_engine
from infrastructure.repositories import InvoiceRepository
from domain.entities import Invoice

@pytest.fixture
def db_session():
    """BD en memoria para testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_save_and_retrieve_invoice(db_session):
    """Guardar y recuperar factura."""
    repo = InvoiceRepository(db_session)
    
    invoice = Invoice(
        series_number="F001-00123",
        total=Money(1000, "PEN")
    )
    
    saved = repo.save(invoice)
    assert saved.id is not None
    
    retrieved = repo.get_by_id(saved.id)
    assert retrieved.series_number == "F001-00123"
```

**Ejemplo Test E2E:**

```python
# tests/e2e/test_invoice_flow.py
from playwright.sync_api import sync_playwright

def test_process_invoice_full_flow():
    """Flujo completo: upload PDF → OCR → validar → exportar."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 1. Login
        page.goto("http://localhost:3000")
        page.fill("#username", "admin")
        page.fill("#password", "secret")
        page.click("#login-btn")
        
        # 2. Upload factura
        page.set_input_files("#file-upload", "tests/fixtures/factura001.pdf")
        page.click("#process-btn")
        
        # 3. Esperar resultado OCR
        page.wait_for_selector(".ocr-result", timeout=30000)
        
        # 4. Validar datos extraídos
        assert "F001-00123" in page.text_content(".series-number")
        assert "S/. 1,234.56" in page.text_content(".total")
        
        # 5. Exportar a Excel
        page.click("#export-btn")
        download = page.wait_for_download()
        assert download.suggested_filename == "facturas_2025-11-18.xlsx"
        
        browser.close()
```

**CI/CD Pipeline (GitHub Actions):**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run unit tests
        run: poetry run pytest tests/unit -v --cov=src --cov-report=xml
      
      - name: Run integration tests
        run: poetry run pytest tests/integration -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## DEVOPS Y DEPLOYMENT

### Desarrollo (Local)

```bash
# Docker Compose para servicios locales
docker-compose.yml:

version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:  # Para testing de migración
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"
  
  sqlserver:  # Para testing SQL Server
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: Y
      SA_PASSWORD: YourStrong!Passw0rd
    ports:
      - "1433:1433"
```

---

### Producción (Data Center)

**Opción 1: Docker Swarm (Simple)**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: facturas-api:2.0.0
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: mssql+pyodbc://...
      REDIS_URL: redis://redis:6379
  
  worker:
    image: facturas-worker:2.0.0
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          devices:
            - driver: nvidia
              count: 1  # GPU para OCR
    environment:
      DATABASE_URL: mssql+pyodbc://...
      REDIS_URL: redis://redis:6379
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl

volumes:
  redis-data:
```

**Opción 2: Kubernetes (Escalable)**

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: facturas-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: facturas-api
  template:
    metadata:
      labels:
        app: facturas-api
    spec:
      containers:
      - name: api
        image: facturas-api:2.0.0
        resources:
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: facturas-api
spec:
  type: LoadBalancer
  ports:
  - port: 443
    targetPort: 8000
  selector:
    app: facturas-api
```

---

## STACK FINAL RECOMENDADO

### Resumen Ejecutivo

| Componente | Desarrollo | Producción | Justificación |
|------------|------------|------------|---------------|
| **Desktop Framework** | Electron | Electron | Ecosistema maduro, auto-update, DevTools |
| **Backend Framework** | FastAPI | FastAPI | Async, type-safe, OpenAPI auto |
| **Base de Datos** | SQLite | SQL Server | Portable vs Enterprise |
| **ORM** | SQLModel | SQLModel | Pydantic + SQLAlchemy |
| **Migraciones** | Alembic | Alembic | Versionado, rollback |
| **Frontend** | React 18 + TS | React 18 + TS | Mantener, ecosistema maduro |
| **Estado** | Zustand | Zustand | Simple, type-safe |
| **Data Fetching** | TanStack Query | TanStack Query | Cache, sync automático |
| **Job Queue** | Celery (local) | Celery + Redis | Tareas largas, escalable |
| **Testing** | pytest + Playwright | pytest + Playwright | Cobertura >80% |
| **Deployment** | - | Docker + K8s | Escalabilidad horizontal |

---

### Dependencias Completas

**Backend (`pyproject.toml`):**

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlmodel = "^0.0.14"
alembic = "^1.12.0"
pydantic = {extras = ["email"], version = "^2.5.0"}
python-multipart = "^0.0.6"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
celery = {extras = ["redis"], version = "^5.3.0"}
redis = "^5.0.0"

# OCR/AI
paddleocr = "^2.7.3"
paddlepaddle = "^2.6.1"
docling = "^2.55.1"
pytesseract = "^0.3.13"
torch = "^2.1.0"
transformers = "^4.36.0"

# Utils
python-dotenv = "^1.0.0"
httpx = "^0.25.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"
black = "^23.12.0"
ruff = "^0.1.8"
mypy = "^1.7.0"
```

**Frontend (`package.json`):**

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "@tanstack/react-query": "^5.14.0",
    "zustand": "^4.4.0",
    "react-router-dom": "^6.20.0",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.4.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "playwright": "^1.40.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0"
  }
}
```

---

## PRÓXIMOS PASOS

1. ✅ **Aprobar stack propuesto** (este documento)
2. 📦 **Setup proyecto base** con estructura Clean Architecture
3. 🗄️ **Diseñar modelo de datos normalizado** (siguiente documento)
4. 🧪 **Configurar CI/CD** con GitHub Actions
5. 👨‍💻 **Sprint 1**: Implementar Domain Layer + Tests

---

**Documento:** v1.0  
**Fecha:** 2025-11-18  
**Autor:** Equipo de Arquitectura  
**Próxima Revisión:** Sprint Review cada 2 semanas
