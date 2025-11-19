# Sistema de Internacionalización (i18n)

Sistema completo de internacionalización para Invokox con soporte para múltiples idiomas.

## 🌍 Idiomas Soportados

| Idioma | Código | Bandera | Estado | Líneas |
|--------|--------|---------|--------|--------|
| Español | `es` | 🇪🇸 | ✅ Default | 600+ |
| English | `en` | 🇬🇧 | ✅ Completo | 600+ |
| Português | `pt` | 🇧🇷 | ✅ Completo | 350+ |

## 📂 Estructura

```
i18n/
├── LanguageContext.tsx          # Provider y hook de contexto
├── index.ts                     # Exports principales
└── translations/
    ├── es.ts                    # Traducciones en español
    ├── en.ts                    # Traducciones en inglés
    ├── pt.ts                    # Traducciones en portugués
    └── index.ts                 # Exports de traducciones
```

## 🚀 Uso Básico

### 1. Configurar Provider (Ya configurado en main.tsx)

```typescript
// main.tsx
import { LanguageProvider } from './i18n';

<LanguageProvider>
  <App />
</LanguageProvider>
```

### 2. Usar en Componentes

```typescript
import { useLanguage } from '../i18n';

function MyComponent() {
  const { t, locale, setLocale } = useLanguage();

  return (
    <div>
      {/* Usar traducciones */}
      <h1>{t.dashboard.title}</h1>
      <p>{t.common.save}</p>

      {/* Idioma actual */}
      <p>Idioma: {locale}</p>

      {/* Cambiar idioma */}
      <button onClick={() => setLocale('en')}>
        English
      </button>
    </div>
  );
}
```

### 3. Selector de Idioma (Componente)

Ya incluido en la aplicación:

```typescript
import { LanguageSelector } from './components/LanguageSelector';

<LanguageSelector />
```

## 📝 Estructura de Traducciones

Cada archivo de traducción (es.ts, en.ts, pt.ts) tiene la misma estructura:

```typescript
export const es = {
  // Comunes
  common: {
    save: 'Guardar',
    cancel: 'Cancelar',
    delete: 'Eliminar',
    // ...
  },

  // Navegación
  nav: {
    dashboard: 'Dashboard',
    invoices: 'Facturas',
    upload: 'Subir Facturas',
    // ...
  },

  // Estados de factura
  invoiceStatus: {
    PENDING: 'Pendiente',
    PROCESSING: 'Procesando',
    COMPLETED: 'Completada',
    // ...
  },

  // Panel de facturas
  invoicePanel: {
    title: 'Panel de Facturas',
    subtitle: 'Gestiona y filtra todas las facturas',
    searchPlaceholder: 'Serie, emisor, receptor...',
    // ...
  },

  // Subir facturas
  uploadInvoices: {
    title: 'Subir Facturas',
    dropzone: 'Arrastra archivos aquí',
    // ...
  },

  // Validar factura
  validateInvoice: {
    title: 'Validar Factura',
    save: 'Guardar',
    approve: 'Aprobar',
    // ...
  },

  // Dashboard
  dashboard: {
    title: 'Dashboard',
    welcome: 'Bienvenido',
    // ...
  },

  // Empresas
  companies: {
    title: 'Gestión de Empresas',
    addCompany: 'Agregar Empresa',
    // ...
  },

  // Analytics
  analytics: {
    title: 'Análisis y Reportes',
    // ...
  },

  // Export
  export: {
    title: 'Exportar Datos',
    // ...
  },

  // Settings
  settings: {
    title: 'Configuración',
    general: 'General',
    ocr: 'OCR',
    // ...
  },

  // Mensajes del sistema
  messages: {
    confirmDelete: '¿Está seguro de eliminar?',
    operationSuccess: 'Operación exitosa',
    // ...
  },

  // Errores de validación
  errors: {
    required: 'Este campo es requerido',
    invalidEmail: 'Email inválido',
    // ...
  },
};
```

## ✨ Características

### 1. Cambio Dinámico

El idioma cambia **instantáneamente** en toda la aplicación sin recargar:

```typescript
const { setLocale } = useLanguage();

// Cambiar a inglés
setLocale('en');

// Cambiar a español
setLocale('es');

// Cambiar a portugués
setLocale('pt');
```

### 2. Persistencia

El idioma seleccionado se guarda en `localStorage` con la clave `invokox_language`:

```typescript
// Se guarda automáticamente al cambiar
localStorage.getItem('invokox_language'); // "es" | "en" | "pt"
```

### 3. Type-Safe

TypeScript proporciona autocompletado y validación:

```typescript
const { t } = useLanguage();

// ✅ Válido - TypeScript autocompleta
t.common.save
t.invoicePanel.title
t.dashboard.welcome

// ❌ Error de TypeScript
t.nonExistent.key  // Error: Property 'nonExistent' does not exist
```

### 4. Actualización HTML lang

El atributo `lang` del documento se actualiza automáticamente:

```html
<!-- Español -->
<html lang="es">

<!-- English -->
<html lang="en">

<!-- Português -->
<html lang="pt">
```

## 🔧 Agregar Nuevas Traducciones

### Paso 1: Editar archivos de idiomas

Agrega las mismas keys en **todos** los archivos de idioma:

```typescript
// es.ts
export const es = {
  // ...
  myNewSection: {
    title: 'Mi Nuevo Título',
    description: 'Mi descripción',
  }
};

// en.ts
export const en = {
  // ...
  myNewSection: {
    title: 'My New Title',
    description: 'My description',
  }
};

// pt.ts
export const pt = {
  // ...
  myNewSection: {
    title: 'Meu Novo Título',
    description: 'Minha descrição',
  }
};
```

### Paso 2: Usar en componente

```typescript
const { t } = useLanguage();

<div>
  <h1>{t.myNewSection.title}</h1>
  <p>{t.myNewSection.description}</p>
</div>
```

## 🎯 Ejemplos de Uso

### Ejemplo 1: Botón Simple

```typescript
const { t } = useLanguage();

<button>{t.common.save}</button>
// Español: "Guardar"
// English: "Save"
// Português: "Salvar"
```

### Ejemplo 2: Título de Página

```typescript
const { t } = useLanguage();

<h1>{t.invoicePanel.title}</h1>
// Español: "Panel de Facturas"
// English: "Invoice Panel"
// Português: "Painel de Faturas"
```

### Ejemplo 3: Mensajes Dinámicos

```typescript
const { t } = useLanguage();

// Usar con toast/alertas
toast.success(t.messages.operationSuccess);

// Usar con confirmaciones
const confirmed = confirm(t.messages.confirmDelete);
```

### Ejemplo 4: Estados de Factura

```typescript
const { t } = useLanguage();

function StatusBadge({ status }: { status: InvoiceStatus }) {
  return (
    <span>
      {t.invoiceStatus[status]}
    </span>
  );
}

// PENDING → "Pendiente" | "Pending" | "Pendente"
// APPROVED → "Aprobada" | "Approved" | "Aprovada"
```

### Ejemplo 5: Selector Completo

```typescript
import { LanguageSelector } from '../components/LanguageSelector';

function Header() {
  return (
    <header>
      <h1>Invokox</h1>
      <LanguageSelector />  {/* Dropdown con banderas */}
    </header>
  );
}
```

## 🧪 Testing

Para probar traducciones:

```typescript
import { render, screen } from '@testing-library/react';
import { LanguageProvider } from '../i18n';

test('renders in Spanish by default', () => {
  render(
    <LanguageProvider>
      <MyComponent />
    </LanguageProvider>
  );

  expect(screen.getByText('Panel de Facturas')).toBeInTheDocument();
});
```

## 📊 Estadísticas

- **Total de archivos**: 5
- **Total de líneas de traducción**: 1,550+
- **Keys de traducción**: 200+ por idioma
- **Secciones traducidas**: 15
- **Cobertura**: 100% en todos los idiomas

## 🔗 Referencias

- **Context API**: React Context para estado global
- **localStorage**: Persistencia del idioma seleccionado
- **TypeScript**: Type-safety con autocompletado

## 📞 Soporte

Si necesitas agregar un nuevo idioma:

1. Crea `frontend/src/i18n/translations/[codigo].ts`
2. Copia estructura de `es.ts`
3. Traduce todos los textos
4. Importa en `translations/index.ts`
5. Agrega opción en `LanguageSelector.tsx`

---

**Última actualización**: 2025-01-19
