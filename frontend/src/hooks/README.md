# Custom React Hooks

Hooks personalizados reutilizables para la aplicación Invokox.

## 📚 Hooks Disponibles

### useTaskPolling

Hook para hacer polling del estado de tareas asíncronas (OCR processing).

## 🎯 useTaskPolling - Documentación Completa

### Propósito

Monitorear el estado de tareas de larga duración (como procesamiento OCR) mediante polling periódico al backend.

### Firma

```typescript
function useTaskPolling(
  taskId: string | null,
  options?: UseTaskPollingOptions
): UseTaskPollingReturn
```

### Parámetros

#### `taskId: string | null`

ID de la tarea a monitorear. Si es `null`, el polling no se inicia.

#### `options?: UseTaskPollingOptions`

```typescript
interface UseTaskPollingOptions {
  interval?: number;        // Intervalo en ms (default: 2000)
  maxAttempts?: number;     // Máximo de intentos (default: 60)
  onComplete?: (result: any) => void;  // Callback al completar
  onError?: (error: string) => void;   // Callback en error
}
```

### Retorno

```typescript
interface UseTaskPollingReturn {
  taskStatus: TaskStatus | null;  // Estado actual de la tarea
  isPolling: boolean;              // Indicador de polling activo
  attempts: number;                // Intentos realizados
  startPolling: () => void;        // Iniciar polling manualmente
  stopPolling: () => void;         // Detener polling manualmente
}
```

#### `TaskStatus`

```typescript
interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  progress: number;     // 0-100
  result?: any;         // Resultado si completó
  error?: string;       // Error si falló
}
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Básico

```typescript
import { useTaskPolling } from '../hooks/useTaskPolling';

function OCRProcessor({ taskId }: { taskId: string | null }) {
  const { taskStatus, isPolling } = useTaskPolling(taskId);

  if (!taskStatus) return <div>No hay tarea</div>;
  if (isPolling) return <div>Procesando... {taskStatus.progress}%</div>;

  if (taskStatus.status === 'COMPLETED') {
    return <div>¡Completado! {JSON.stringify(taskStatus.result)}</div>;
  }

  if (taskStatus.status === 'FAILED') {
    return <div>Error: {taskStatus.error}</div>;
  }

  return null;
}
```

### Ejemplo 2: Con Callbacks

```typescript
import { useTaskPolling } from '../hooks/useTaskPolling';
import { toast } from 'sonner';

function UploadInvoice() {
  const [taskId, setTaskId] = useState<string | null>(null);

  const { taskStatus, isPolling } = useTaskPolling(taskId, {
    interval: 2000,        // Poll cada 2 segundos
    maxAttempts: 60,       // Máximo 2 minutos
    onComplete: (result) => {
      toast.success('OCR completado exitosamente');
      console.log('Datos extraídos:', result);
      // Navegar a validación
      navigateTo('validate', result.invoice_id);
    },
    onError: (error) => {
      toast.error(`Error en OCR: ${error}`);
    }
  });

  const handleUpload = async (file: File) => {
    // Upload
    const uploadResult = await uploadFile(file);

    // Process OCR
    const ocrResult = await processOCR(uploadResult.invoice_id);

    // Iniciar polling
    setTaskId(ocrResult.task_id);
  };

  return (
    <div>
      <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />

      {isPolling && (
        <div>
          <p>Procesando OCR...</p>
          <progress value={taskStatus?.progress || 0} max={100} />
          <p>{taskStatus?.progress}%</p>
        </div>
      )}
    </div>
  );
}
```

### Ejemplo 3: Control Manual

```typescript
import { useTaskPolling } from '../hooks/useTaskPolling';

function ManualPolling() {
  const [taskId, setTaskId] = useState<string | null>(null);

  const {
    taskStatus,
    isPolling,
    attempts,
    startPolling,
    stopPolling
  } = useTaskPolling(taskId, {
    // No iniciar automáticamente
  });

  const handleStartOCR = async () => {
    const result = await startOCRJob();
    setTaskId(result.task_id);
    startPolling();  // Iniciar manualmente
  };

  const handleStop = () => {
    stopPolling();
  };

  return (
    <div>
      <button onClick={handleStartOCR}>Iniciar OCR</button>
      <button onClick={handleStop} disabled={!isPolling}>
        Detener Polling
      </button>

      {isPolling && (
        <p>Intento {attempts} de 60</p>
      )}

      {taskStatus && (
        <div>
          <p>Estado: {taskStatus.status}</p>
          <p>Progreso: {taskStatus.progress}%</p>
        </div>
      )}
    </div>
  );
}
```

### Ejemplo 4: Con Progress Bar

```typescript
import { useTaskPolling } from '../hooks/useTaskPolling';
import { Loader2 } from 'lucide-react';

function ProgressTracker({ taskId }: { taskId: string }) {
  const { taskStatus, isPolling } = useTaskPolling(taskId, {
    interval: 1000,  // Poll cada segundo para UI responsive
    onComplete: (result) => {
      console.log('Task completed:', result);
    }
  });

  if (!taskStatus) return null;

  const { status, progress } = taskStatus;

  return (
    <div className="space-y-2">
      {/* Status Badge */}
      <div className="flex items-center gap-2">
        {isPolling && <Loader2 className="w-4 h-4 animate-spin" />}
        <span className={`badge ${getStatusColor(status)}`}>
          {status}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Progress Text */}
      <p className="text-sm text-gray-600">
        {progress}% completado
      </p>
    </div>
  );
}

function getStatusColor(status: string) {
  switch (status) {
    case 'COMPLETED': return 'text-green-600';
    case 'FAILED': return 'text-red-600';
    case 'PROCESSING': return 'text-blue-600';
    default: return 'text-gray-600';
  }
}
```

---

## 🔧 Configuración Avanzada

### Timeouts Personalizados

```typescript
// Polling rápido (cada 500ms, máx 30 segundos)
useTaskPolling(taskId, {
  interval: 500,
  maxAttempts: 60
});

// Polling lento (cada 5s, máx 10 minutos)
useTaskPolling(taskId, {
  interval: 5000,
  maxAttempts: 120
});
```

### Manejo de Múltiples Tareas

```typescript
function MultiTaskMonitor() {
  const [tasks, setTasks] = useState<string[]>([]);

  return (
    <div>
      {tasks.map(taskId => (
        <TaskMonitor key={taskId} taskId={taskId} />
      ))}
    </div>
  );
}

function TaskMonitor({ taskId }: { taskId: string }) {
  const { taskStatus, isPolling } = useTaskPolling(taskId);
  // ... render individual task
}
```

---

## ⚡ Performance Tips

### 1. Limitar re-renders

```typescript
// Memoizar callbacks
const handleComplete = useCallback((result) => {
  console.log('Done:', result);
}, []);

useTaskPolling(taskId, {
  onComplete: handleComplete  // No cambia en cada render
});
```

### 2. Cleanup automático

El hook limpia automáticamente el intervalo al desmontar:

```typescript
// ✅ Seguro - se limpia automáticamente
useEffect(() => {
  // taskId cambia, el polling anterior se detiene
  useTaskPolling(taskId);
}, [taskId]);
```

### 3. Evitar polling innecesario

```typescript
// Solo hacer polling si hay taskId
const taskId = someCondition ? 'task_123' : null;
useTaskPolling(taskId);  // No pollará si taskId es null
```

---

## 🧪 Testing

```typescript
import { renderHook, act } from '@testing-library/react';
import { useTaskPolling } from './useTaskPolling';

// Mock del API
jest.mock('../services/invoices', () => ({
  invoicesApi: {
    getTaskStatus: jest.fn()
  }
}));

test('polls task status', async () => {
  const onComplete = jest.fn();

  const { result } = renderHook(() =>
    useTaskPolling('task_123', { onComplete })
  );

  // Simular que la tarea completa
  await act(async () => {
    // Mock response
    invoicesApi.getTaskStatus.mockResolvedValue({
      task_id: 'task_123',
      status: 'COMPLETED',
      progress: 100,
      result: { data: 'test' }
    });

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled();
    });
  });

  expect(result.current.taskStatus?.status).toBe('COMPLETED');
  expect(result.current.isPolling).toBe(false);
});
```

---

## 📊 Estados del Hook

```
┌─────────────┐
│  Idle       │ taskId = null
└─────────────┘
       │
       │ taskId set
       ↓
┌─────────────┐
│  Polling    │ isPolling = true
│  (interval) │ attempts++
└─────────────┘
       │
       ├─→ COMPLETED → onComplete() → stop
       ├─→ FAILED → onError() → stop
       └─→ maxAttempts → timeout → stop
```

---

## 🔗 API Backend

El hook espera esta respuesta del endpoint `/api/v1/tasks/{task_id}`:

```typescript
{
  "task_id": "task_abc123",
  "status": "PROCESSING" | "COMPLETED" | "FAILED",
  "progress": 75,  // 0-100
  "result": {
    // Datos si completó
    "invoice_id": 123,
    "series": "F001-001",
    "confidence": 0.95
  },
  "error": null | "mensaje de error"
}
```

---

## 📚 Recursos

- [React Hooks](https://react.dev/reference/react)
- [useEffect cleanup](https://react.dev/reference/react/useEffect#cleanup)

---

**Última actualización**: 2025-01-19
