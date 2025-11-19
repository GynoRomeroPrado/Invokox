# Sistema de Gestión de Facturas con OCR Multi-Motor

Sistema completo de gestión de facturas con procesamiento OCR, validación, aprobación y analytics, diseñado siguiendo principios de Clean Architecture.

## 🎯 Características Principales

### Gestión de Facturas
- **Carga Masiva**: Sube múltiples PDFs e imágenes simultáneamente
- **OCR Multi-Motor**: Soporte para PaddleOCR, Docling y Tesseract
- **Validación Inteligente**: Editor visual con vista previa del documento
- **Multi-Moneda**: Cada factura mantiene su propia moneda (USD, PEN, EUR, CLP, MXN)
- **Estados Completos**: PENDING, PROCESSING, COMPLETED, APPROVED, REJECTED, ERROR

### Usuarios y Roles
- **Admin**: Acceso completo al sistema, configuración y gestión de usuarios
- **Operator**: Carga, validación y aprobación/rechazo de facturas
- **Viewer**: Solo lectura de facturas y reportes

### Analytics y Reportes
- KPIs en tiempo real (total facturas, aprobadas, confianza OCR)
- Gráficos de distribución por estado
- Top emisores por volumen
- Evolución mensual
- Rendimiento por motor OCR
- Exportación en Excel, CSV, PDF y JSON

### Empresas
- Catálogo de emisores y receptores
- Deduplicación por Tax ID/RUC
- Búsqueda y filtrado
- Vinculación automática desde facturas

### Sincronización
- Modo cliente-servidor
- Sincronización automática o manual
- Resolución de conflictos
- Historial de auditoría completo

## 🏗️ Arquitectura

El sistema está construido siguiendo **Clean Architecture**:

- **Entidades**: Invoice, Company, User, AuditLog
- **Casos de Uso**: Upload, OCR Processing, Validation, Approval
- **Adaptadores**: React Components, Mock Data (preparado para APIs reales)
- **Frameworks**: React 18, TypeScript, Tailwind CSS, Recharts

## 📦 Componentes Principales

```
/App.tsx              # Enrutador principal y navegación
/components/
  - Login.tsx         # Autenticación con roles
  - Dashboard.tsx     # Panel principal con KPIs
  - InvoicePanel.tsx  # Lista de facturas con filtros
  - UploadInvoices.tsx # Carga de archivos con OCR
  - ValidateInvoice.tsx # Editor de factura con validación
  - ViewInvoice.tsx    # Vista de solo lectura
  - Companies.tsx      # Catálogo de empresas
  - Analytics.tsx      # Dashboard de analytics
  - Export.tsx         # Exportación configurable
  - GeneralSettings.tsx # Configuración general
  - OcrSettings.tsx    # Configuración de motores OCR
  - ServerSync.tsx     # Sincronización cliente-servidor
  - UsersRoles.tsx     # Administración de usuarios
  - Help.tsx           # Ayuda y soporte
/types/
  - invoice.ts        # Definiciones de tipos
/data/
  - mockData.ts       # Datos de ejemplo
```

## 🚀 Inicio Rápido

### Credenciales de Demo

Puedes iniciar sesión con cualquiera de los siguientes usuarios:

- **Admin**: `admin@example.com` (cualquier contraseña)
- **Operator**: `operator@example.com` (cualquier contraseña)
- **Viewer**: `viewer@example.com` (cualquier contraseña)

### Flujo de Trabajo Básico

1. **Cargar Facturas**: Ve a "Cargar Facturas" y sube PDFs o imágenes
2. **Procesar OCR**: Selecciona el motor OCR y procesa los archivos
3. **Validar**: Revisa y corrige los datos extraídos
4. **Aprobar/Rechazar**: Aprueba facturas correctas o rechaza con nota
5. **Exportar**: Exporta facturas aprobadas en el formato deseado
6. **Analytics**: Visualiza métricas y tendencias

## 🔧 Configuración

### OCR Multi-Motor

**PaddleOCR** (Recomendado)
- Modelo Server o Mobile
- Soporte GPU configurable
- Múltiples idiomas (ES, EN, PT, FR)
- Umbral de confianza ajustable

**Docling**
- Servicio en la nube
- Requiere API Key
- Selección de región

**Tesseract**
- Código abierto
- Configuración PSM y OEM
- Múltiples idiomas

### Sincronización

- URL de API personalizable
- Autenticación con API Key
- Sincronización automática o manual
- Resolución de conflictos configurable

## 📊 Modelo de Datos

### Invoice (Factura)
- Cabecera: serie, fechas, moneda, estado
- Emisor y Receptor (vinculados a Companies)
- Items: descripción, cantidad, precios, impuestos
- Pagos/Cuotas: número, fecha, monto
- Metadatos OCR: motor, confianza, tiempo
- Auditoría: creado/actualizado por usuario

### Company (Empresa)
- Tax ID/RUC (único)
- Nombre legal y comercial
- Tipo: EMISOR, RECEPTOR, AMBOS
- Datos de contacto
- Contador de facturas

### AuditLog (Auditoría)
- Usuario y timestamp
- Acción realizada
- Cambios aplicados (delta)

## 🎨 Diseño

- **Tipografía**: Sistema de diseño con tokens CSS
- **Colores**: Modo claro (extensible a oscuro)
- **Accesibilidad**: WCAG AA
- **Responsivo**: Diseño adaptable a móvil y desktop

## ⚠️ Notas Importantes

### Multi-Moneda
El sistema **NO impone una moneda global**. Cada factura define y almacena su propia moneda, la cual se muestra siempre junto a los montos. No hay conversión automática entre monedas.

### Validaciones
- Al menos 1 ítem requerido para aprobar
- Totales deben cuadrar con impuestos configurados
- Estados y transiciones auditados

### Permisos
- Viewer: solo lectura
- Operator: gestión completa de facturas
- Admin: acceso total incluyendo configuración y usuarios

## 🔮 Próximos Pasos (Sugerencias)

Para convertir esto en un sistema de producción completo, considera:

1. **Backend Real**: Implementar API REST o GraphQL
2. **Base de Datos**: PostgreSQL o MongoDB con esquema de auditoría
3. **Autenticación**: JWT, OAuth2, o integración con IdP
4. **OCR Real**: Integrar servicios OCR reales (PaddleOCR server, Tesseract)
5. **Almacenamiento**: S3 o similar para PDFs originales
6. **WebSockets**: Para actualizaciones en tiempo real
7. **Tests**: Unit tests, integration tests, E2E tests
8. **CI/CD**: Pipeline automatizado de despliegue

## 📄 Licencia

Este es un proyecto de demostración. Ajusta según tus necesidades.

---

**Versión**: 1.0.0  
**Fecha**: 18 de Noviembre, 2024  
**Arquitectura**: Clean Architecture  
**Motores OCR**: 3 soportados (PaddleOCR, Docling, Tesseract)
