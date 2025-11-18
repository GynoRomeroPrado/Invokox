# Frontend - React + TypeScript

Interfaz de usuario del sistema Invokox construida con React 18 y TypeScript.

## 📂 Estructura

```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── common/          # Componentes reutilizables (Button, Input, Modal)
│   │   ├── invoices/        # Componentes específicos de facturas
│   │   ├── companies/       # Componentes de empresas
│   │   └── exports/         # Componentes de exportación
│   ├── pages/               # Páginas/Vistas principales
│   │   ├── Dashboard.tsx
│   │   ├── Invoices.tsx
│   │   └── Settings.tsx
│   ├── hooks/               # Custom React Hooks
│   │   ├── useInvoices.ts
│   │   └── useOCR.ts
│   ├── services/            # API clients y servicios
│   │   ├── api.ts           # Axios instance configurada
│   │   └── invoices.ts      # API de facturas
│   ├── store/               # Zustand stores (estado global)
│   │   ├── appStore.ts      # Estado de app (mode, config)
│   │   └── invoiceStore.ts  # Estado de facturas
│   ├── types/               # TypeScript types e interfaces
│   │   ├── invoice.ts
│   │   └── api.ts
│   ├── utils/               # Utilidades y helpers
│   │   ├── formatters.ts    # Formateo de fechas, monedas
│   │   └── validators.ts    # Validaciones Zod
│   └── assets/              # Recursos estáticos
│       ├── images/
│       └── styles/
├── public/                  # Archivos públicos (index.html, favicon)
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 🚀 Stack Tecnológico

- **React 18.2+**: UI library con Hooks
- **TypeScript 5.0+**: Type safety
- **Vite 5.0**: Build tool (más rápido que CRA)
- **TailwindCSS 4.0**: Utility-first CSS
- **TanStack Query 5.0**: Data fetching, caching, sincronización
- **Zustand 4.0**: Estado global simple
- **React Router 6.0**: Navegación
- **React Hook Form 7.0**: Formularios performantes
- **Zod 3.0**: Validación runtime
- **Axios**: HTTP client

## 🛠️ Instalación

```bash
# Instalar Node.js 20+ (si no está instalado)
# https://nodejs.org/

# Instalar dependencias
npm install
```

## 🏃 Ejecución

```bash
# Desarrollo (con hot-reload)
npm run dev
# Acceder a: http://localhost:5173

# Build para producción
npm run build

# Preview del build
npm run preview

# Linting
npm run lint

# Type checking
npm run type-check
```

## 🧪 Testing

```bash
# Unit tests (Vitest)
npm run test

# Tests en modo watch
npm run test:watch

# Coverage
npm run test:coverage

# E2E tests (Playwright)
npm run test:e2e

# E2E en modo UI
npm run test:e2e:ui
```

## 🎨 Componentes

### Estructura de Componente Típico

```tsx
// src/components/invoices/InvoiceCard.tsx
import { FC } from 'react';
import { Invoice } from '@/types/invoice';

interface InvoiceCardProps {
  invoice: Invoice;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export const InvoiceCard: FC<InvoiceCardProps> = ({
  invoice,
  onEdit,
  onDelete
}) => {
  return (
    <div className="border rounded-lg p-4 shadow-sm">
      <h3 className="text-lg font-semibold">{invoice.seriesNumber}</h3>
      <p className="text-gray-600">{invoice.issuer.name}</p>
      <div className="mt-2 flex justify-between">
        <span className="text-xl font-bold">
          {formatCurrency(invoice.total, invoice.currency)}
        </span>
        <div className="space-x-2">
          {onEdit && (
            <button onClick={() => onEdit(invoice.id)}>Edit</button>
          )}
          {onDelete && (
            <button onClick={() => onDelete(invoice.id)}>Delete</button>
          )}
        </div>
      </div>
    </div>
  );
};
```

## 🗄️ Estado Global (Zustand)

```typescript
// src/store/appStore.ts
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
      : 'https://api.company.local'
  }),
}));
```

## 📡 Data Fetching (TanStack Query)

```typescript
// src/hooks/useInvoices.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoicesApi } from '@/services/invoices';

export const useInvoices = () => {
  const queryClient = useQueryClient();

  const { data: invoices, isLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: invoicesApi.list,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  const createMutation = useMutation({
    mutationFn: invoicesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
    },
  });

  return {
    invoices,
    isLoading,
    createInvoice: createMutation.mutate,
  };
};
```

## 🎯 Validación con Zod

```typescript
// src/utils/validators.ts
import { z } from 'zod';

export const InvoiceSchema = z.object({
  seriesNumber: z.string().min(1, 'Serie requerida'),
  issuerRuc: z.string().length(11, 'RUC debe tener 11 dígitos'),
  total: z.number().positive('Total debe ser positivo'),
  issueDate: z.date(),
  currency: z.enum(['PEN', 'USD', 'EUR']),
});

export type InvoiceFormData = z.infer<typeof InvoiceSchema>;
```

## 📱 Responsive Design

Todas las vistas están optimizadas para:
- Desktop: 1920x1080+
- Tablet: 768x1024
- Mobile: 375x667 (no prioritario para v2.0)

## 🎨 Theming con Tailwind

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        // ... más colores
      },
    },
  },
};
```

## 🔗 Integración con Backend

El frontend se comunica con el backend FastAPI a través de HTTP:

- **Modo Standalone**: `http://localhost:8000`
- **Modo Server**: `https://api.company.local`

La URL base se configura automáticamente según el modo en `appStore.ts`.

## 📦 Build para Electron

```bash
# Build optimizado para Electron
npm run build:electron

# El output va a electron/renderer/
```

## 🔧 Configuración de Vite

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```
