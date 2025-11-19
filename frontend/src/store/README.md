# Estado Global con Zustand

Gestión del estado global de la aplicación utilizando Zustand.

## 📦 Stores Disponibles

### invoiceStore

Store principal para gestión de facturas.

## 🎯 InvoiceStore - API Completa

### Estado

```typescript
interface InvoiceStore {
  // Datos
  invoices: Invoice[];              // Lista de todas las facturas
  selectedInvoice: Invoice | null;  // Factura seleccionada actualmente

  // UI State
  loading: boolean;                 // Indicador de carga
  error: string | null;             // Mensaje de error

  // Filtros
  filters: {
    status?: InvoiceStatus;         // Filtro por estado
    currency?: Currency;            // Filtro por moneda
    dateFrom?: string;              // Fecha desde
    dateTo?: string;                // Fecha hasta
    page: number;                   // Página actual
    limit: number;                  // Items por página
  };

  // ... acciones (ver abajo)
}
```

### Acciones

#### **loadInvoices()**

Carga todas las facturas desde el backend.

```typescript
const store = useInvoiceStore();

// Cargar facturas
await store.loadInvoices();

// Acceder a datos
const { invoices, loading, error } = store;
```

**Uso**:
```typescript
useEffect(() => {
  store.loadInvoices();
}, []);
```

---

#### **uploadInvoice(file, createdBy, onProgress?)**

Sube un archivo de factura al backend.

**Parámetros**:
- `file`: File - Archivo PDF/PNG/JPG
- `createdBy`: string - Email del usuario
- `onProgress`: (progress: number) => void - Callback de progreso (0-100)

**Retorna**: `Promise<UploadResult>`
```typescript
{
  invoice_id: number;
  file_path: string;
  series: string;
  status: 'PENDING';
}
```

**Ejemplo**:
```typescript
const handleUpload = async (file: File) => {
  try {
    const result = await store.uploadInvoice(
      file,
      'admin@invokox.com',
      (progress) => {
        console.log(`Progress: ${progress}%`);
      }
    );

    console.log('Invoice ID:', result.invoice_id);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

---

#### **processOCR(invoiceId, engine?, useGpu?)**

Procesa una factura con OCR.

**Parámetros**:
- `invoiceId`: string - ID de la factura
- `engine`: 'donut' | 'paddleocr' | 'docling' | 'tesseract' (opcional, default: 'donut')
- `useGpu`: boolean (opcional, default: false)

**Retorna**: `Promise<OCRResult>`
```typescript
{
  task_id: string;
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED';
  confidence: number;  // 0.0 - 1.0
  result?: {
    series: string;
    issuer_name: string;
    // ... más datos extraídos
  };
}
```

**Ejemplo**:
```typescript
const handleProcessOCR = async (invoiceId: string) => {
  try {
    // Con Donut y GPU
    const result = await store.processOCR(
      invoiceId,
      'donut',
      true
    );

    console.log('Task ID:', result.task_id);
    console.log('Confidence:', result.confidence);
  } catch (error) {
    console.error('OCR failed:', error);
  }
};
```

---

#### **approveInvoice(invoiceId, approvedBy)**

Aprueba una factura.

**Parámetros**:
- `invoiceId`: string - ID de la factura
- `approvedBy`: string - Email del aprobador

**Ejemplo**:
```typescript
await store.approveInvoice('123', 'admin@invokox.com');
```

---

#### **rejectInvoice(invoiceId, rejectedBy, reason)**

Rechaza una factura.

**Parámetros**:
- `invoiceId`: string - ID de la factura
- `rejectedBy`: string - Email del rechazador
- `reason`: string - Motivo del rechazo

**Ejemplo**:
```typescript
await store.rejectInvoice(
  '123',
  'admin@invokox.com',
  'Datos incorrectos'
);
```

---

#### **batchApprove(invoiceIds, approvedBy)**

Aprueba múltiples facturas en lote.

**Parámetros**:
- `invoiceIds`: number[] - Array de IDs de facturas
- `approvedBy`: string - Email del aprobador

**Retorna**: `Promise<BatchResult>`
```typescript
{
  success_count: number;
  failed_count: number;
  approved_ids: number[];
  failed_ids: Array<{
    id: number;
    reason: string;
  }>;
}
```

**Ejemplo**:
```typescript
const selectedIds = [1, 2, 3, 4, 5];

const result = await store.batchApprove(
  selectedIds,
  'admin@invokox.com'
);

console.log(`${result.success_count} aprobadas`);
console.log(`${result.failed_count} fallaron`);
```

---

#### **batchReject(invoiceIds, rejectedBy, reason?)**

Rechaza múltiples facturas en lote.

**Parámetros**:
- `invoiceIds`: number[] - Array de IDs
- `rejectedBy`: string - Email del rechazador
- `reason`: string (opcional) - Motivo del rechazo

**Ejemplo**:
```typescript
const selectedIds = [6, 7, 8];

const result = await store.batchReject(
  selectedIds,
  'admin@invokox.com',
  'Datos incompletos'
);
```

---

#### **setFilters(filters)**

Actualiza los filtros de búsqueda.

**Parámetros**:
- `filters`: Partial<FilterOptions>

**Ejemplo**:
```typescript
store.setFilters({
  status: 'PENDING',
  currency: 'USD',
  dateFrom: '2025-01-01',
  dateTo: '2025-01-31',
  page: 1,
  limit: 20
});
```

---

#### **selectInvoice(invoice)**

Selecciona una factura.

**Parámetros**:
- `invoice`: Invoice | null

**Ejemplo**:
```typescript
const invoice = invoices.find(inv => inv.id === '123');
store.selectInvoice(invoice);

// Acceder a factura seleccionada
const { selectedInvoice } = useInvoiceStore();
```

---

## 💡 Uso Completo en Componente

```typescript
import { useInvoiceStore } from '../store/invoiceStore';
import { useEffect } from 'react';

function InvoiceList() {
  const store = useInvoiceStore();
  const { invoices, loading, error } = store;

  // Cargar facturas al montar
  useEffect(() => {
    store.loadInvoices();
  }, []);

  // Manejar upload
  const handleUpload = async (file: File) => {
    try {
      // 1. Upload
      const uploadResult = await store.uploadInvoice(
        file,
        'admin@invokox.com',
        (progress) => console.log(`${progress}%`)
      );

      // 2. Process OCR
      const ocrResult = await store.processOCR(
        uploadResult.invoice_id.toString(),
        'donut',
        true
      );

      // 3. Auto-approve si confianza alta
      if (ocrResult.confidence >= 0.9) {
        await store.approveInvoice(
          uploadResult.invoice_id.toString(),
          'admin@invokox.com'
        );
      }

      // 4. Reload
      await store.loadInvoices();

    } catch (error) {
      console.error('Error:', error);
    }
  };

  // Manejar batch approve
  const handleBatchApprove = async (ids: number[]) => {
    const result = await store.batchApprove(ids, 'admin@invokox.com');
    console.log(`${result.success_count} aprobadas`);
    await store.loadInvoices();
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Facturas ({invoices.length})</h1>
      <input
        type="file"
        onChange={(e) => {
          if (e.target.files?.[0]) {
            handleUpload(e.target.files[0]);
          }
        }}
      />
      {/* Render invoices */}
    </div>
  );
}
```

---

## 🔄 Flujo Típico

```
1. Mount Component
   ↓
2. useEffect(() => store.loadInvoices())
   ↓
3. User Upload File
   ↓
4. store.uploadInvoice(file) → invoice_id
   ↓
5. store.processOCR(invoice_id) → task_id
   ↓
6. Poll task status (useTaskPolling hook)
   ↓
7. Task completes → show validation screen
   ↓
8. User edits/validates
   ↓
9. store.approveInvoice(invoice_id)
   ↓
10. store.loadInvoices() → refresh list
```

---

## ⚡ Performance Tips

### 1. Evitar re-renders innecesarios

Usa selectores específicos:

```typescript
// ❌ Malo - Re-render en cualquier cambio del store
const store = useInvoiceStore();

// ✅ Bueno - Solo re-render si invoices cambia
const invoices = useInvoiceStore(state => state.invoices);
const loading = useInvoiceStore(state => state.loading);
```

### 2. Memoizar datos filtrados

```typescript
const filteredInvoices = useMemo(() => {
  return invoices.filter(inv => inv.status === 'PENDING');
}, [invoices]);
```

### 3. Batch updates

Agrupa múltiples actualizaciones:

```typescript
// Zustand actualiza automáticamente en batch
store.setFilters({ status: 'PENDING' });
store.selectInvoice(null);
// Solo 1 re-render
```

---

## 🧪 Testing

```typescript
import { renderHook, act } from '@testing-library/react';
import { useInvoiceStore } from './invoiceStore';

test('loads invoices', async () => {
  const { result } = renderHook(() => useInvoiceStore());

  await act(async () => {
    await result.current.loadInvoices();
  });

  expect(result.current.invoices.length).toBeGreaterThan(0);
  expect(result.current.loading).toBe(false);
});
```

---

## 📚 Recursos

- [Zustand Docs](https://github.com/pmndrs/zustand)
- [React Query Integration](https://tanstack.com/query)

---

**Última actualización**: 2025-01-19
