# Guía Completa de Invokox - Sistema de Gestión de Facturas con OCR

## 📚 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Backend - API REST](#backend---api-rest)
4. [Frontend - React + i18n](#frontend---react--i18n)
5. [Sistema de Internacionalización](#sistema-de-internacionalización)
6. [Flujo de Trabajo Completo](#flujo-de-trabajo-completo)
7. [Guía de Desarrollo](#guía-de-desarrollo)
8. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

Invokox es un **sistema completo de gestión de facturas** que utiliza **OCR con IA (Donut Deep Learning)** para extraer automáticamente datos de facturas en PDF o imágenes.

### Características Principales:

✅ **Procesamiento OCR Inteligente**
- Donut (Vision Transformer) - Deep Learning
- PaddleOCR - Alta precisión
- Docling - Documentos estructurados
- Tesseract - Alternativa ligera

✅ **Multiidioma (i18n)**
- 🇪🇸 Español (por defecto)
- 🇬🇧 English
- 🇧🇷 Português (Brasil)

✅ **Flujo Completo**
1. Subir factura (PDF/PNG/JPG)
2. Procesar con OCR (automático)
3. Validar/editar datos extraídos
4. Aprobar/rechazar
5. Exportar a Excel/CSV

✅ **Arquitectura Moderna**
- Backend: FastAPI + Clean Architecture
- Frontend: React 18 + TypeScript + Zustand
- Base de datos: SQLite (dev) / SQL Server (prod)

---

## Arquitectura del Sistema

### Vista General

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Components  │  │   Zustand   │  │    i18n     │    │
│  │   (UI)      │→ │   (State)   │  │  (3 langs)  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│         ↓                ↓                              │
│  ┌──────────────────────────────────────────────┐      │
│  │        API Services (invoicesApi)            │      │
│  └──────────────────────────────────────────────┘      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                      │
│  ┌──────────────────────────────────────────────┐      │
│  │         Presentation Layer (API v1)          │      │
│  │  /invoices  /companies  /tasks  /export      │      │
│  └──────────────────────────────────────────────┘      │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────┐      │
│  │        Application Layer (Use Cases)         │      │
│  │  ProcessOCR  CreateInvoice  ExportData       │      │
│  └──────────────────────────────────────────────┘      │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────┐      │
│  │       Domain Layer (Business Logic)          │      │
│  │  Invoice  Company  InvoiceItem (Entities)    │      │
│  └──────────────────────────────────────────────┘      │
│                     ↓                                   │
│  ┌──────────────────────────────────────────────┐      │
│  │    Infrastructure Layer (Data & Services)    │      │
│  │  Repositories  OCRService  FileStorage       │      │
│  └──────────────────────────────────────────────┘      │
└────────────────────┬────────────────────────────────────┘
                     ↓
              ┌──────────────┐
              │   Database   │
              │ SQLite/MSSQL │
              └──────────────┘
```

### Clean Architecture

El backend sigue **Clean Architecture** con 4 capas claramente separadas:

1. **Domain**: Entidades de negocio puras (sin dependencias)
2. **Application**: Casos de uso y lógica de aplicación
3. **Infrastructure**: Implementaciones técnicas (DB, APIs)
4. **Presentation**: Controllers y endpoints HTTP

---

## Backend - API REST

### Estructura de Carpetas

```
backend/src/
├── domain/
│   ├── entities/
│   │   ├── invoice.py          # Entidad principal de factura
│   │   ├── company.py          # Entidad de empresa
│   │   └── invoice_item.py     # Item de factura
│   └── value_objects/          # Objetos de valor inmutables
│
├── application/
│   └── use_cases/
│       ├── process_ocr_use_case.py      # Procesar OCR
│       ├── create_invoice_use_case.py   # Crear factura
│       └── export_invoices_use_case.py  # Exportar datos
│
├── infrastructure/
│   ├── repositories/
│   │   └── invoice_repository.py        # Acceso a datos
│   ├── services/
│   │   └── ocr_service.py              # Servicio OCR
│   └── database/
│       └── models.py                    # Modelos SQLModel
│
└── presentation/
    └── api/
        ├── main.py                      # App principal FastAPI
        └── v1/
            ├── invoices.py              # Endpoints de facturas
            ├── companies.py             # Endpoints de empresas
            └── tasks.py                 # Estado de tareas async
```

### Endpoints Principales

#### **Facturas (Invoices)**

```python
# Listar facturas
GET /api/v1/invoices
Query params:
  - status: PENDING | PROCESSING | COMPLETED | APPROVED | REJECTED
  - page: int (default: 1)
  - limit: int (default: 100)

# Obtener factura por ID
GET /api/v1/invoices/{invoice_id}

# Subir archivo de factura
POST /api/v1/invoices/upload
Form-data:
  - file: File (PDF, PNG, JPG, max 10MB)
  - created_by: str (email del usuario)
Response:
  {
    "invoice_id": 123,
    "file_path": "/uploads/2025/01/factura_001.pdf",
    "series": "TEMP-20250119123456",
    "status": "PENDING"
  }

# Procesar con OCR
POST /api/v1/invoices/{invoice_id}/process
Query params:
  - engine: donut | paddleocr | docling | tesseract (default: donut)
  - use_gpu: bool (default: false)
  - force_reprocess: bool (default: false)
Response:
  {
    "task_id": "task_abc123",
    "status": "PROCESSING",
    "message": "OCR iniciado con Donut"
  }

# Actualizar factura
PUT /api/v1/invoices/{invoice_id}
Body: { series, issue_date, items[], totals, ... }

# Aprobar factura
POST /api/v1/invoices/{invoice_id}/approve
Body: { approved_by: str }

# Rechazar factura
POST /api/v1/invoices/{invoice_id}/reject
Body: { rejected_by: str, reason: str }

# Batch approve
POST /api/v1/invoices/batch/approve
Body: { invoice_ids: [1,2,3], approved_by: str }

# Batch reject
POST /api/v1/invoices/batch/reject
Body: { invoice_ids: [1,2,3], rejected_by: str, reason?: str }

# Exportar a Excel
POST /api/v1/invoices/export/excel
Body: { invoice_ids: [1,2,3] }
Response: archivo Excel descargable

# Exportar a CSV
POST /api/v1/invoices/export/csv
Body: { invoice_ids: [1,2,3] }
Response: archivo CSV descargable
```

#### **Tareas Asíncronas (Tasks)**

```python
# Obtener estado de tarea OCR
GET /api/v1/tasks/{task_id}
Response:
  {
    "task_id": "task_abc123",
    "status": "COMPLETED" | "PROCESSING" | "FAILED",
    "progress": 100,
    "result": { ... },  # Datos extraídos
    "error": null | "mensaje de error"
  }
```

### Modelos de Datos

#### **Invoice (Factura)**

```python
class Invoice(BaseModel):
    id: Optional[int]

    # Documento
    series: str              # "F001-00001234"
    issue_date: date         # Fecha de emisión
    due_date: Optional[date] # Fecha de vencimiento

    # Emisor
    issuer_id: int
    issuer_name: str
    issuer_tax_id: str       # RUC/CNPJ/Tax ID

    # Receptor
    receiver_id: int
    receiver_name: str
    receiver_tax_id: str

    # Totales
    currency: Currency       # PEN | USD | EUR | CLP | MXN
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    total: Decimal

    # Items
    items: list[InvoiceItem]

    # OCR
    status: InvoiceStatus    # PENDING | PROCESSING | COMPLETED | APPROVED | REJECTED
    ocr_engine: Optional[OcrEngine]  # Donut | PaddleOCR | Docling | Tesseract
    ocr_confidence: Decimal  # 0.0 - 1.0 (confianza del OCR)
    processing_time: Optional[int]   # Segundos

    # Archivo
    file_path: str           # Ruta del PDF/imagen original

    # Auditoría
    created_at: datetime
    created_by: str          # Email del usuario
    updated_at: Optional[datetime]
    updated_by: Optional[str]
```

---

## Frontend - React + i18n

### Estructura de Carpetas

```
frontend/src/
├── components/
│   ├── UploadInvoices.tsx       # Subir y procesar facturas
│   ├── InvoicePanel.tsx         # Panel de gestión
│   ├── ValidateInvoice.tsx      # Validar/editar factura
│   ├── ViewInvoice.tsx          # Ver factura (solo lectura)
│   ├── Dashboard.tsx            # Panel principal
│   ├── Companies.tsx            # Gestión de empresas
│   ├── Analytics.tsx            # Análisis y reportes
│   ├── Export.tsx               # Exportación masiva
│   └── LanguageSelector.tsx     # Selector de idioma
│
├── store/
│   └── invoiceStore.ts          # Estado global (Zustand)
│
├── hooks/
│   └── useTaskPolling.ts        # Hook para polling de tareas
│
├── services/
│   └── invoices.ts              # Cliente API
│
├── i18n/
│   ├── LanguageContext.tsx      # Context Provider
│   ├── index.ts                 # Exports
│   └── translations/
│       ├── es.ts                # Español (600+ líneas)
│       ├── en.ts                # English (600+ líneas)
│       ├── pt.ts                # Português (350+ líneas)
│       └── index.ts             # Exports
│
└── types/
    └── invoice.ts               # TypeScript types
```

### Componentes Principales

#### **1. UploadInvoices** (Subir Facturas)

**Funcionalidad**:
- Drag & drop de archivos (PDF, PNG, JPG)
- Validación de tipo y tamaño (max 10MB)
- Upload a backend
- Procesamiento OCR automático con Donut
- Configuración: engine, GPU, umbral de confianza
- Auto-aprobación si confianza > umbral
- Progress tracking en tiempo real

**Uso**:
```typescript
import { UploadInvoices } from './components/UploadInvoices';

<UploadInvoices navigateTo={navigateToFunction} />
```

**Código clave**:
```typescript
// Upload archivo
const uploadResult = await store.uploadInvoice(
  file,
  'admin@invokox.com',
  (progress) => setProgress(progress)
);

// Procesar con OCR
const ocrResult = await store.processOCR(
  uploadResult.invoice_id.toString(),
  'donut',  // engine
  true      // use GPU
);

// Auto-aprobar si confianza >= umbral
if (ocrResult.confidence >= confidenceThreshold) {
  await store.approveInvoice(invoiceId, 'admin@invokox.com');
}
```

#### **2. InvoicePanel** (Panel de Gestión)

**Funcionalidad**:
- Listar todas las facturas
- Búsqueda por serie, emisor, receptor
- Filtros: estado, moneda, rango de fechas
- Paginación (10 items por página)
- Selección múltiple con checkboxes
- Batch approve/reject
- Export a Excel
- Download de archivo original

**Uso**:
```typescript
<InvoicePanel
  navigateTo={navigateToFunction}
  userRole="admin"  // admin | operator | viewer
/>
```

#### **3. ValidateInvoice** (Validar/Editar)

**Funcionalidad**:
- Cargar factura desde API
- Vista previa del PDF/imagen original
- Formulario de edición de datos
- Gestión de items (agregar, editar, eliminar)
- Cálculo automático de totales
- Guardar cambios
- Aprobar/rechazar

**Uso**:
```typescript
<ValidateInvoice
  invoiceId="123"
  navigateTo={navigateToFunction}
  userRole="admin"
/>
```

### Estado Global (Zustand)

```typescript
// frontend/src/store/invoiceStore.ts

interface InvoiceStore {
  // Estado
  invoices: Invoice[];
  selectedInvoice: Invoice | null;
  loading: boolean;
  error: string | null;
  filters: FilterOptions;

  // Acciones
  loadInvoices: () => Promise<void>;
  uploadInvoice: (file: File, createdBy: string, onProgress?) => Promise<UploadResult>;
  processOCR: (invoiceId: string, engine?, useGpu?) => Promise<OCRResult>;
  approveInvoice: (invoiceId: string, approvedBy: string) => Promise<void>;
  rejectInvoice: (invoiceId: string, rejectedBy: string, reason: string) => Promise<void>;
  batchApprove: (invoiceIds: number[], approvedBy: string) => Promise<BatchResult>;
  batchReject: (invoiceIds: number[], rejectedBy: string, reason?) => Promise<BatchResult>;
}

// Uso en componentes
const store = useInvoiceStore();

// Cargar facturas
await store.loadInvoices();

// Subir factura
const result = await store.uploadInvoice(file, 'user@email.com');

// Procesar con OCR
const ocrResult = await store.processOCR(invoiceId);

// Aprobar
await store.approveInvoice(invoiceId, 'admin@email.com');
```

### Custom Hooks

#### **useTaskPolling** (Polling de Tareas)

```typescript
// frontend/src/hooks/useTaskPolling.ts

const { taskStatus, isPolling, startPolling, stopPolling } = useTaskPolling(
  taskId,
  {
    interval: 2000,        // Poll cada 2 segundos
    maxAttempts: 60,       // Máximo 2 minutos
    onComplete: (result) => {
      console.log('Tarea completada:', result);
    },
    onError: (error) => {
      console.error('Error en tarea:', error);
    }
  }
);

// Usar en componente
useEffect(() => {
  if (taskId) {
    startPolling();
  }
}, [taskId]);
```

---

## Sistema de Internacionalización

### Características

✅ **3 Idiomas soportados**:
- 🇪🇸 Español (default)
- 🇬🇧 English
- 🇧🇷 Português (Brasil)

✅ **Características**:
- Cambio dinámico sin recargar
- Persistencia en localStorage
- Type-safe con TypeScript
- Selector visual con banderas

### Estructura de Traducciones

```
frontend/src/i18n/
├── LanguageContext.tsx          # Provider y hook
├── index.ts                     # Exports
└── translations/
    ├── es.ts                    # 🇪🇸 Español (600+ líneas)
    ├── en.ts                    # 🇬🇧 English (600+ líneas)
    ├── pt.ts                    # 🇧🇷 Português (350+ líneas)
    └── index.ts
```

### Uso en Componentes

```typescript
import { useLanguage } from '../i18n';

function MyComponent() {
  const { t, locale, setLocale } = useLanguage();

  return (
    <div>
      {/* Usar traducciones */}
      <h1>{t.dashboard.title}</h1>
      <p>{t.invoicePanel.subtitle}</p>
      <button>{t.common.save}</button>

      {/* Cambiar idioma */}
      <button onClick={() => setLocale('es')}>Español</button>
      <button onClick={() => setLocale('en')}>English</button>
      <button onClick={() => setLocale('pt')}>Português</button>
    </div>
  );
}
```

### Agregar Nuevas Traducciones

1. Editar archivo de idioma (`es.ts`, `en.ts`, `pt.ts`)
2. Agregar nueva key en la sección correspondiente
3. TypeScript validará automáticamente

```typescript
// es.ts
export const es = {
  // ...
  myNewSection: {
    title: 'Nuevo Título',
    subtitle: 'Nuevo Subtítulo',
  }
};

// Uso en componente
const { t } = useLanguage();
<h1>{t.myNewSection.title}</h1>
```

---

## Flujo de Trabajo Completo

### 1. Subir Factura

```
Usuario → UploadInvoices Component
  ↓
  Drag & Drop / Select File
  ↓
  Validación (tipo, tamaño)
  ↓
  POST /api/v1/invoices/upload
  ↓
  Backend guarda archivo en /uploads/YYYY/MM/
  ↓
  Crea Invoice con status=PENDING
  ↓
  Retorna invoice_id
```

### 2. Procesar con OCR

```
Frontend → POST /api/v1/invoices/{id}/process
  ↓
  Backend → ProcessOCRUseCase
  ↓
  Selecciona engine (Donut por defecto)
  ↓
  Ejecuta OCR sobre PDF/imagen
  ↓
  Extrae datos: series, fecha, emisor, receptor, items, totales
  ↓
  Calcula confianza (0.0 - 1.0)
  ↓
  Actualiza Invoice:
    - status = COMPLETED
    - ocr_confidence = 0.85 (ejemplo)
    - series, issuer_name, items[], etc.
  ↓
  Retorna task_id para polling
```

### 3. Polling de Estado

```
Frontend → useTaskPolling hook
  ↓
  Cada 2 segundos: GET /api/v1/tasks/{task_id}
  ↓
  Backend retorna:
    { status: "COMPLETED", progress: 100, result: {...} }
  ↓
  Hook llama onComplete(result)
  ↓
  Frontend actualiza UI
```

### 4. Validar/Editar

```
Usuario → Navigate to ValidateInvoice
  ↓
  GET /api/v1/invoices/{id}
  ↓
  Backend retorna Invoice con datos OCR
  ↓
  Frontend muestra:
    - PDF preview (lado izquierdo)
    - Formulario editable (lado derecho)
  ↓
  Usuario edita campos, items, totales
  ↓
  Click "Guardar" → PUT /api/v1/invoices/{id}
  ↓
  Backend actualiza Invoice
```

### 5. Aprobar/Rechazar

```
Usuario → Click "Aprobar"
  ↓
  POST /api/v1/invoices/{id}/approve
  ↓
  Backend:
    invoice.approve(approved_by)
    invoice.status = APPROVED
  ↓
  Frontend → Redirect a InvoicePanel
```

### 6. Exportar

```
Usuario → Selecciona múltiples facturas
  ↓
  Click "Exportar"
  ↓
  POST /api/v1/invoices/export/excel
  Body: { invoice_ids: [1, 2, 3] }
  ↓
  Backend genera archivo Excel
  ↓
  StreamingResponse → Download automático
```

---

## Guía de Desarrollo

### Ejecutar en Modo Desarrollo

#### Terminal 1: Backend
```bash
cd backend
poetry install
poetry run uvicorn src.presentation.api.main:app --reload --port 8000
```

Acceso: http://localhost:8000
Docs API: http://localhost:8000/docs

#### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

Acceso: http://localhost:5173

### Agregar Nuevo Endpoint

1. **Crear caso de uso** (`backend/src/application/use_cases/`)
```python
# my_use_case.py
class MyUseCaseInput:
    def __init__(self, param1: str):
        self.param1 = param1

class MyUseCase:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def execute(self, input_data: MyUseCaseInput):
        # Lógica de negocio
        result = await self.repository.do_something(input_data.param1)
        return result
```

2. **Agregar endpoint** (`backend/src/presentation/api/v1/`)
```python
# my_endpoints.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(
    param1: str,
    repo: Repository = Depends(get_repository)
):
    use_case = MyUseCase(repository=repo)
    result = await use_case.execute(MyUseCaseInput(param1=param1))
    return result
```

3. **Registrar router** (`backend/src/presentation/api/main.py`)
```python
from .v1 import my_endpoints

app.include_router(my_endpoints.router, prefix="/api/v1", tags=["MyTag"])
```

### Agregar Nuevo Componente

1. **Crear componente** (`frontend/src/components/`)
```typescript
// MyComponent.tsx
import { useLanguage } from '../i18n';
import { useInvoiceStore } from '../store/invoiceStore';

export function MyComponent() {
  const { t } = useLanguage();
  const store = useInvoiceStore();

  return (
    <div>
      <h1>{t.mySection.title}</h1>
      {/* ... */}
    </div>
  );
}
```

2. **Agregar traducciones** (en `es.ts`, `en.ts`, `pt.ts`)
```typescript
mySection: {
  title: 'Mi Título',
  subtitle: 'Mi Subtítulo'
}
```

3. **Usar en App**
```typescript
// App.tsx
import { MyComponent } from './components/MyComponent';

// En el return:
{currentView === 'my-view' && <MyComponent />}
```

---

## Solución de Problemas

### Backend no inicia

**Error**: `ModuleNotFoundError: No module named 'X'`
**Solución**:
```bash
cd backend
poetry install
poetry run uvicorn src.presentation.api.main:app --reload
```

### Frontend no carga datos

**Error**: CORS o Network Error
**Solución**:
- Verificar que backend esté corriendo en puerto 8000
- Verificar URL en `frontend/src/services/api.ts`
```typescript
const BASE_URL = 'http://localhost:8000';  // Debe coincidir con backend
```

### OCR falla

**Error**: Donut model not found
**Solución**:
```bash
# El modelo se descarga automáticamente en primer uso
# Asegurar conexión a internet
# O especificar otro engine: paddleocr, tesseract
```

### Traducciones no funcionan

**Error**: Cannot read property 't' of undefined
**Solución**:
- Verificar que `<LanguageProvider>` envuelva `<App>` en `main.tsx`
```typescript
<LanguageProvider>
  <App />
</LanguageProvider>
```

### Base de datos locked

**Error**: database is locked (SQLite)
**Solución**:
```bash
# Cerrar todas las conexiones
# Reiniciar backend
# O usar PostgreSQL/SQL Server en producción
```

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisar esta documentación
2. Consultar `/docs` (Swagger UI) del backend
3. Revisar logs del backend y frontend
4. Crear issue en repositorio

---

## 📝 Licencia

[Tu licencia aquí]

---

**Última actualización**: 2025-01-19
**Versión**: 2.0.0
