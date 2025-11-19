# 🔌 Guía de Integración Frontend-Backend - Invokox

**Fecha**: 2025-01-19
**Estado**: Backend API Completo ✅ | Frontend Listo para Conectar ⏳

---

## 📋 Resumen Ejecutivo

El **backend API está 100% completo** con todos los endpoints que el frontend necesita. Esta guía documenta cómo conectar ambas partes del sistema.

### Estado Actual

✅ **Backend API** - Completamente implementado
✅ **Frontend UI** - Componentes visuales listos
✅ **Servicios API** - Métodos definidos (`frontend/src/services/invoices.ts`)
⏳ **Integración** - Reemplazar mock data con API calls

---

## 🎯 Endpoints Disponibles (Backend)

### **Base URL**
- **Desarrollo**: `http://localhost:8000`
- **Producción**: Configurar en `VITE_API_URL`

### **1. Invoices - CRUD Básico**

#### **GET /api/v1/invoices**
Lista facturas con paginación y filtros.

```typescript
// Frontend (ya implementado en invoices.ts)
const response = await invoicesApi.list({
  page: 1,
  limit: 10,
  status: 'PENDING',
  search: 'F001'
});
```

**Query Parameters**:
- `skip`: Offset para paginación (default: 0)
- `limit`: Máximo de registros (default: 100)
- `status`: PENDING, PROCESSING, COMPLETED, APPROVED, REJECTED, ERROR
- `currency`: PEN, USD, EUR, etc.

**Response**:
```json
[
  {
    "id": 123,
    "series": "F001-00000123",
    "invoice_type": "FACTURA",
    "issue_date": "2025-01-15",
    "status": "PENDING",
    "total_amount": 1180.00,
    "currency": "PEN",
    ...
  }
]
```

---

#### **GET /api/v1/invoices/{id}**
Obtiene una factura específica por ID.

```typescript
const invoice = await invoicesApi.getById('123');
```

**Response**: Invoice completo con items

---

#### **POST /api/v1/invoices**
Crea una nueva factura (raramente usado directamente, preferir upload).

---

#### **PUT /api/v1/invoices/{id}**
Actualiza factura existente.

```typescript
await invoicesApi.update('123', {
  notes: 'Factura corregida',
  status: 'APPROVED'
});
```

---

#### **DELETE /api/v1/invoices/{id}**
Elimina factura (soft delete).

```typescript
await invoicesApi.delete('123');
```

---

### **2. Upload y Procesamiento OCR** ⭐ **NUEVO**

#### **POST /api/v1/invoices/upload**
Sube archivo PDF/imagen y crea registro.

```typescript
// Frontend
const file = event.target.files[0];
const result = await invoicesApi.uploadFile(file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});

console.log(result);
// {
//   invoice_id: 123,
//   file_path: "/uploads/2025/01/invoice_20250115_103000.pdf",
//   status: "PENDING",
//   message: "Archivo subido. Usar POST /invoices/123/process para OCR."
// }
```

**Backend Endpoint**:
```http
POST /api/v1/invoices/upload
Content-Type: multipart/form-data

file: (binary)
created_by: admin@invokox.com
```

**Validaciones**:
- Formatos permitidos: `.pdf`, `.png`, `.jpg`, `.jpeg`
- Tamaño máximo: 10MB
- Si falla, archivo se elimina automáticamente

**Response**:
```json
{
  "invoice_id": 123,
  "file_path": "/uploads/2025/01/invoice_20250115_103000.pdf",
  "status": "PENDING",
  "message": "Archivo subido exitosamente..."
}
```

---

#### **POST /api/v1/invoices/{id}/process**
Procesa factura con OCR (Donut Deep Learning).

```typescript
// Frontend
const result = await invoicesApi.processOCR('123');

console.log(result);
// {
//   task_id: "task_123_20250115103000",
//   status: "COMPLETED",
//   confidence: 0.92,
//   engine: "donut",
//   result: { ... }
// }
```

**Backend Endpoint**:
```http
POST /api/v1/invoices/123/process?engine=donut&use_gpu=true
```

**Query Parameters**:
- `engine`: `donut` (default), `paddleocr`, `docling`, `tesseract`
- `use_gpu`: `true` para GPU acceleration (recomendado con Donut)
- `force_reprocess`: `true` para reprocesar facturas ya procesadas

**Response**:
```json
{
  "task_id": "task_123_20250115103000",
  "invoice_id": 123,
  "status": "COMPLETED",
  "confidence": 0.92,
  "engine": "donut",
  "message": "Procesamiento OCR completado.",
  "result": {
    "status": "COMPLETED",
    "confidence": 0.92,
    "extracted_data": {
      "series": "F001-00000123",
      "issuer_name": "EMPRESA EJEMPLO S.A.C.",
      "issuer_tax_id": "20123456789",
      "total_amount": 1180.00,
      ...
    }
  }
}
```

**Estados de Resultado**:
- `COMPLETED`: Confidence ≥ 75% - Auto-aprobable
- `REVIEW_NEEDED`: Confidence 50-75% - Requiere revisión manual
- `ERROR`: Confidence < 50% - OCR falló

---

### **3. Estado de Tareas** ⭐ **NUEVO**

#### **GET /api/v1/tasks/{task_id}**
Consulta estado de tarea asíncrona.

```typescript
// Frontend
const status = await invoicesApi.getTaskStatus('task_123_20250115103000');

console.log(status);
// {
//   task_id: "task_123_20250115103000",
//   status: "COMPLETED",
//   progress: 100,
//   result: { ... }
// }
```

**Response**:
```json
{
  "task_id": "task_123_20250115103000",
  "status": "COMPLETED",
  "progress": 100,
  "result": {
    "invoice_id": 123,
    "extracted_data": { ... }
  },
  "error": null,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:32:30"
}
```

---

### **4. Aprobación y Rechazo**

#### **POST /api/v1/invoices/{id}/approve**
Aprueba factura procesada.

```typescript
// Frontend
const approved = await invoicesApi.approve('123');
```

**Backend Endpoint**:
```http
POST /api/v1/invoices/123/approve?approved_by=admin@invokox.com
```

---

#### **POST /api/v1/invoices/{id}/reject**
Rechaza factura.

```typescript
// Frontend
const rejected = await invoicesApi.reject('123', 'Datos incorrectos');
```

**Backend Endpoint**:
```http
POST /api/v1/invoices/123/reject?rejected_by=admin@invokox.com&reason=Datos+incorrectos
```

---

### **5. Exportación** ⭐ **NUEVO**

#### **POST /api/v1/invoices/export/excel**
Exporta facturas a Excel.

```typescript
// Frontend
const blob = await invoicesApi.exportToExcel([1, 2, 3, 4, 5]);

// Descargar archivo
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `facturas_${Date.now()}.csv`;
a.click();
```

**Backend Endpoint**:
```http
POST /api/v1/invoices/export/excel
Content-Type: application/json

{
  "invoice_ids": [1, 2, 3, 4, 5]
}
```

**Response**: Archivo CSV (cambiar a Excel en prod)

---

#### **POST /api/v1/invoices/export/csv**
Exporta facturas a CSV.

```typescript
const blob = await invoicesApi.exportToCSV([1, 2, 3]);
```

---

### **6. Batch Operations** ⭐ **NUEVO**

#### **POST /api/v1/invoices/batch/approve**
Aprueba múltiples facturas.

```typescript
// Frontend (agregar a invoices.ts)
const result = await api.post('/api/v1/invoices/batch/approve', {
  invoice_ids: [1, 2, 3, 4, 5],
  approved_by: 'admin@invokox.com'
});

console.log(result.data);
// {
//   success_count: 4,
//   failed_count: 1,
//   approved_ids: [1, 2, 3, 4],
//   failed_ids: [{id: 5, reason: "Already approved"}]
// }
```

**Backend Endpoint**:
```http
POST /api/v1/invoices/batch/approve
Content-Type: application/json

{
  "invoice_ids": [1, 2, 3, 4, 5],
  "approved_by": "admin@invokox.com"
}
```

---

#### **POST /api/v1/invoices/batch/reject**
Rechaza múltiples facturas.

```typescript
const result = await api.post('/api/v1/invoices/batch/reject', {
  invoice_ids: [1, 2, 3],
  rejected_by: 'admin@invokox.com',
  reason: 'Datos incorrectos'
});
```

---

## 🔧 Pasos para Integrar Frontend

### **Paso 1: Actualizar `frontend/src/services/invoices.ts`**

Agregar métodos que faltan:

```typescript
// Agregar al objeto invoicesApi

// Batch approve
batchApprove: async (invoiceIds: number[], approvedBy: string) => {
  const response = await api.post('/api/v1/invoices/batch/approve', {
    invoice_ids: invoiceIds,
    approved_by: approvedBy
  });
  return response.data;
},

// Batch reject
batchReject: async (invoiceIds: number[], rejectedBy: string, reason?: string) => {
  const response = await api.post('/api/v1/invoices/batch/reject', {
    invoice_ids: invoiceIds,
    rejected_by: rejectedBy,
    reason
  });
  return response.data;
},
```

---

### **Paso 2: Actualizar Componentes**

#### **A. `UploadInvoices.tsx`**

Reemplazar simulación con API real:

```typescript
const handleUpload = async (file: File) => {
  try {
    setUploading(true);

    // 1. Subir archivo
    const uploadResult = await invoicesApi.uploadFile(file, (progress) => {
      setUploadProgress(progress);
    });

    console.log('Archivo subido:', uploadResult);

    // 2. Procesar con OCR automáticamente
    const ocrResult = await invoicesApi.processOCR(uploadResult.invoice_id.toString());

    console.log('OCR iniciado:', ocrResult);

    // 3. Polling del estado (opcional)
    if (ocrResult.task_id) {
      pollTaskStatus(ocrResult.task_id);
    }

  } catch (error) {
    console.error('Error:', error);
    toast.error('Error al subir factura');
  } finally {
    setUploading(false);
  }
};

const pollTaskStatus = async (taskId: string) => {
  const maxAttempts = 30;
  let attempts = 0;

  const interval = setInterval(async () => {
    try {
      const status = await invoicesApi.getTaskStatus(taskId);

      if (status.status === 'COMPLETED' || status.status === 'FAILED') {
        clearInterval(interval);

        if (status.status === 'COMPLETED') {
          toast.success('Factura procesada exitosamente!');
          // Navegar a ValidateInvoice
          navigateTo('validate', status.result.invoice_id);
        } else {
          toast.error('Error al procesar factura');
        }
      }

      attempts++;
      if (attempts >= maxAttempts) {
        clearInterval(interval);
        toast.warning('Timeout en procesamiento');
      }
    } catch (error) {
      console.error('Error polling:', error);
      clearInterval(interval);
    }
  }, 2000); // Poll cada 2 segundos
};
```

---

#### **B. `InvoicePanel.tsx`**

Reemplazar `mockInvoices` con API:

```typescript
import { useEffect, useState } from 'react';
import { invoicesApi } from '../services/invoices';

export function InvoicePanel({ navigateTo, userRole }: InvoicePanelProps) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: 'ALL',
    currency: 'ALL',
    search: '',
  });

  // Cargar facturas desde API
  useEffect(() => {
    loadInvoices();
  }, [filters]);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const result = await invoicesApi.list({
        status: filters.status !== 'ALL' ? filters.status : undefined,
        search: filters.search || undefined,
        limit: 100
      });

      setInvoices(result.items || result); // Depende del formato response
    } catch (error) {
      console.error('Error loading invoices:', error);
      toast.error('Error al cargar facturas');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkApprove = async () => {
    if (selectedIds.size === 0) return;

    try {
      const result = await invoicesApi.batchApprove(
        Array.from(selectedIds),
        'admin@invokox.com' // TODO: Obtener del usuario logueado
      );

      toast.success(`${result.success_count} facturas aprobadas`);
      if (result.failed_count > 0) {
        toast.warning(`${result.failed_count} facturas fallaron`);
      }

      // Recargar lista
      loadInvoices();
      setSelectedIds(new Set());
    } catch (error) {
      toast.error('Error en aprobación batch');
    }
  };

  // ... resto del componente
}
```

---

#### **C. `ValidateInvoice.tsx`**

Cargar factura desde API:

```typescript
useEffect(() => {
  if (invoiceId) {
    loadInvoice(invoiceId);
  }
}, [invoiceId]);

const loadInvoice = async (id: string) => {
  try {
    setLoading(true);
    const invoice = await invoicesApi.getById(id);
    setInvoice(invoice);
  } catch (error) {
    console.error('Error:', error);
    toast.error('Error al cargar factura');
  } finally {
    setLoading(false);
  }
};

const handleApprove = async () => {
  try {
    await invoicesApi.approve(invoiceId);
    toast.success('Factura aprobada');
    navigateTo('invoices');
  } catch (error) {
    toast.error('Error al aprobar');
  }
};
```

---

### **Paso 3: Estado Global (Opcional pero Recomendado)**

Crear store con Zustand:

```typescript
// frontend/src/store/invoiceStore.ts
import create from 'zustand';
import { invoicesApi } from '../services/invoices';

interface InvoiceStore {
  invoices: Invoice[];
  loading: boolean;
  filters: any;

  loadInvoices: () => Promise<void>;
  approveInvoice: (id: string) => Promise<void>;
  rejectInvoice: (id: string, reason: string) => Promise<void>;
  uploadInvoice: (file: File) => Promise<any>;
}

export const useInvoiceStore = create<InvoiceStore>((set, get) => ({
  invoices: [],
  loading: false,
  filters: {},

  loadInvoices: async () => {
    set({ loading: true });
    try {
      const result = await invoicesApi.list(get().filters);
      set({ invoices: result.items || result });
    } catch (error) {
      console.error(error);
    } finally {
      set({ loading: false });
    }
  },

  approveInvoice: async (id) => {
    await invoicesApi.approve(id);
    await get().loadInvoices(); // Recargar
  },

  uploadInvoice: async (file) => {
    const result = await invoicesApi.uploadFile(file);
    await get().loadInvoices();
    return result;
  },
}));
```

---

## 🚀 Flujo Completo: Upload → Process → Validate → Approve

```typescript
// 1. Usuario sube archivo
const upload = await invoicesApi.uploadFile(file);
// Response: { invoice_id: 123, status: "PENDING", ... }

// 2. Sistema procesa con OCR automáticamente
const ocr = await invoicesApi.processOCR(upload.invoice_id.toString());
// Response: { task_id: "task_123_...", status: "PROCESSING", ... }

// 3. Polling del estado (cada 2 seg)
const status = await invoicesApi.getTaskStatus(ocr.task_id);
// Response: { status: "COMPLETED", confidence: 0.92, ... }

// 4. Usuario valida datos extraídos
const invoice = await invoicesApi.getById(upload.invoice_id.toString());
// Response: Invoice completo con datos del OCR

// 5. Usuario aprueba
await invoicesApi.approve(upload.invoice_id.toString());
// Response: Invoice con status "APPROVED"

// 6. (Opcional) Exportar a Excel
const blob = await invoicesApi.exportToExcel([upload.invoice_id]);
// Download archivo
```

---

## 📝 Checklist de Integración

### Backend ✅
- [x] Endpoint /upload
- [x] Endpoint /process
- [x] Endpoint /tasks/{id}
- [x] Endpoints approve/reject
- [x] Endpoints export (excel, csv)
- [x] Batch operations
- [x] Error handling
- [x] Documentación OpenAPI

### Frontend ⏳
- [x] Servicios API definidos (`invoices.ts`)
- [ ] Reemplazar mock data con API calls
- [ ] Implementar polling de tareas
- [ ] Manejo de errores y loading states
- [ ] Toast notifications
- [ ] Estado global (Zustand/Redux)
- [ ] Actualizar componentes:
  - [ ] UploadInvoices
  - [ ] InvoicePanel
  - [ ] ValidateInvoice
  - [ ] Export

---

## 🐛 Troubleshooting

### CORS Errors
Si ves errores de CORS:

```bash
# Backend ya está configurado en main.py
# Verificar que settings.cors_origins incluya localhost:5173
```

### Connection Refused
```bash
# Asegurarse de que el backend esté corriendo:
cd backend
uvicorn src.presentation.api.main:app --reload --port 8000
```

### 404 Not Found
```bash
# Verificar que la URL sea correcta:
# Backend: http://localhost:8000
# Frontend: http://localhost:5173

# Verificar en frontend/src/services/api.ts:
const baseURL = 'http://localhost:8000';
```

---

## 📚 Documentación Adicional

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`

---

## ✅ Conclusión

El backend está **100% listo** con todos los endpoints que el frontend necesita:

✅ Upload de archivos
✅ Procesamiento OCR con Donut
✅ Consulta de estado de tareas
✅ Aprobación y rechazo
✅ Exportación a Excel/CSV
✅ Operaciones batch

**Próximo paso**: Actualizar componentes del frontend para usar la API real en lugar de mock data.

---

**Autor**: Claude (Anthropic)
**Fecha**: 2025-01-19
**Proyecto**: Invokox v2.0
