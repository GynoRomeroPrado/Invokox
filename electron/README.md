# Electron - Desktop Wrapper

Wrapper de Electron para ejecutar Invokox como aplicación de escritorio standalone.

## 📂 Estructura

```
electron/
├── main/                    # Main Process (Node.js)
│   ├── index.ts            # Punto de entrada principal
│   ├── window.ts           # Gestión de ventanas
│   ├── backend.ts          # Lanzar proceso FastAPI
│   ├── updater.ts          # Auto-actualización
│   └── ipc/                # IPC handlers
│       ├── file.ts         # Operaciones de archivos
│       └── system.ts       # Info del sistema
├── preload/                # Preload Scripts (bridge seguro)
│   └── index.ts            # Exponer APIs a renderer
├── renderer/               # Renderer Process (viene de frontend build)
└── package.json
```

## 🏗️ Arquitectura Electron

```
┌─────────────────────────────────────────────┐
│           Main Process (Node.js)            │
│  - Gestiona ventanas BrowserWindow          │
│  - Inicia backend FastAPI en puerto local  │
│  - Maneja IPC con renderer                  │
│  - Auto-updates con electron-updater        │
└─────────────┬───────────────────────────────┘
              │ IPC (Inter-Process Communication)
┌─────────────▼───────────────────────────────┐
│     Preload Script (Context Bridge)         │
│  - Expone APIs seguras a renderer           │
│  - window.electronAPI.selectFile()          │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│  Renderer Process (React + TypeScript)      │
│  - Corre en contexto de navegador           │
│  - Consume FastAPI via http://localhost     │
│  - UI construida con React (desde frontend) │
└─────────────────────────────────────────────┘
```

## 🚀 Instalación

```bash
npm install
```

## 🏃 Ejecución

```bash
# Desarrollo
npm run dev

# Build para distribución
npm run build

# Build específico por OS
npm run build:win   # Windows
npm run build:mac   # macOS
npm run build:linux # Linux

# Build para todas las plataformas
npm run build:all
```

## 📦 Empaquetado

Usa `electron-builder` para crear instaladores:

```json
// package.json - electron-builder config
{
  "build": {
    "appId": "com.invokox.app",
    "productName": "Invokox",
    "directories": {
      "output": "dist"
    },
    "files": [
      "main/**/*",
      "preload/**/*",
      "renderer/**/*",
      "package.json"
    ],
    "win": {
      "target": ["nsis", "portable"],
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": ["dmg", "zip"],
      "icon": "assets/icon.icns",
      "category": "public.app-category.business"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "assets/icon.png",
      "category": "Office"
    }
  }
}
```

## 🔄 Auto-Update

Configuración con `electron-updater`:

```typescript
// main/updater.ts
import { autoUpdater } from 'electron-updater';

export function setupAutoUpdater() {
  // Configurar servidor de updates
  autoUpdater.setFeedURL({
    provider: 'generic',
    url: 'https://updates.company.local/invokox'
  });

  // Eventos
  autoUpdater.on('update-available', (info) => {
    console.log('Update available:', info.version);
  });

  autoUpdater.on('update-downloaded', (info) => {
    // Notificar al usuario
    dialog.showMessageBox({
      type: 'info',
      title: 'Update Ready',
      message: 'Nueva versión descargada. ¿Instalar ahora?',
      buttons: ['Instalar', 'Después']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });

  // Chequear updates al inicio y cada 4 horas
  autoUpdater.checkForUpdatesAndNotify();
  setInterval(() => {
    autoUpdater.checkForUpdatesAndNotify();
  }, 4 * 60 * 60 * 1000);
}
```

## 🔐 Security Best Practices

### 1. Context Isolation (Habilitado)

```typescript
// main/window.ts
const mainWindow = new BrowserWindow({
  webPreferences: {
    nodeIntegration: false,        // ✅ Deshabilitar Node en renderer
    contextIsolation: true,        // ✅ Aislar contextos
    sandbox: true,                 // ✅ Sandbox habilitado
    preload: path.join(__dirname, '../preload/index.js')
  }
});
```

### 2. IPC Seguro con Context Bridge

```typescript
// preload/index.ts
import { contextBridge, ipcRenderer } from 'electron';

// Exponer APIs limitadas y seguras
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (data: string) => ipcRenderer.invoke('file:save', data),

  // System info
  getSystemInfo: () => ipcRenderer.invoke('system:info'),

  // Updates
  checkForUpdates: () => ipcRenderer.invoke('updater:check'),
  onUpdateAvailable: (callback: Function) =>
    ipcRenderer.on('update:available', (_, info) => callback(info))
});
```

### 3. CSP (Content Security Policy)

```typescript
// main/window.ts
mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      'Content-Security-Policy': [
        "default-src 'self'; " +
        "script-src 'self' 'unsafe-inline'; " +
        "style-src 'self' 'unsafe-inline'; " +
        "connect-src 'self' http://localhost:8000"
      ]
    }
  });
});
```

## 🔌 IPC Handlers

### Main Process

```typescript
// main/ipc/file.ts
import { ipcMain, dialog } from 'electron';

export function setupFileHandlers() {
  ipcMain.handle('dialog:openFile', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'PDFs', extensions: ['pdf'] },
        { name: 'Images', extensions: ['png', 'jpg', 'jpeg'] }
      ]
    });
    return result.filePaths;
  });

  ipcMain.handle('file:save', async (event, data: string) => {
    const result = await dialog.showSaveDialog({
      filters: [{ name: 'Excel', extensions: ['xlsx'] }]
    });

    if (!result.canceled && result.filePath) {
      await fs.promises.writeFile(result.filePath, data);
      return { success: true, path: result.filePath };
    }
    return { success: false };
  });
}
```

### Renderer Process (React)

```typescript
// frontend/src/hooks/useElectron.ts
export const useElectron = () => {
  const isElectron = typeof window !== 'undefined' && window.electronAPI;

  const selectFile = async () => {
    if (!isElectron) return null;
    return await window.electronAPI.selectFile();
  };

  const saveFile = async (data: string) => {
    if (!isElectron) {
      // Fallback para web: download link
      const blob = new Blob([data], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'export.xlsx';
      a.click();
      return;
    }
    return await window.electronAPI.saveFile(data);
  };

  return { isElectron, selectFile, saveFile };
};
```

## 🚀 Backend Integration

Electron inicia el proceso FastAPI automáticamente:

```typescript
// main/backend.ts
import { spawn } from 'child_process';
import path from 'path';

let backendProcess: any = null;

export function startBackend() {
  const pythonPath = path.join(
    process.resourcesPath,
    'backend',
    'venv',
    'bin',
    'python'
  );

  const mainPath = path.join(
    process.resourcesPath,
    'backend',
    'src',
    'presentation',
    'api',
    'main.py'
  );

  backendProcess = spawn(pythonPath, [
    '-m', 'uvicorn',
    'src.presentation.api.main:app',
    '--host', '127.0.0.1',
    '--port', '8000'
  ], {
    cwd: path.join(process.resourcesPath, 'backend'),
    env: {
      ...process.env,
      MODE: 'standalone',
      DATABASE_URL: `sqlite:///${app.getPath('userData')}/facturas.db`
    }
  });

  backendProcess.stdout.on('data', (data: Buffer) => {
    console.log(`[Backend] ${data.toString()}`);
  });

  backendProcess.stderr.on('data', (data: Buffer) => {
    console.error(`[Backend Error] ${data.toString()}`);
  });

  return new Promise((resolve) => {
    // Esperar a que el backend esté listo
    const checkInterval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          clearInterval(checkInterval);
          resolve(true);
        }
      } catch (e) {
        // Aún no está listo
      }
    }, 500);
  });
}

export function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}
```

## 📊 DevTools

En desarrollo, habilitar Chrome DevTools:

```typescript
// main/window.ts
if (process.env.NODE_ENV === 'development') {
  mainWindow.webContents.openDevTools();
}
```

## 🔍 Debugging

```bash
# Ver logs de main process
export ELECTRON_ENABLE_LOGGING=1
npm run dev

# Inspeccionar main process con Chrome
electron --inspect=5858 .
# Chrome: chrome://inspect
```
