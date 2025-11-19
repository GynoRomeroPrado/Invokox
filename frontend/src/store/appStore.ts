import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AppMode = 'standalone' | 'server';

interface AppState {
  // Modo de operación
  mode: AppMode;
  apiBaseUrl: string;
  setMode: (mode: AppMode) => void;

  // Configuración de sincronización
  syncEnabled: boolean;
  lastSyncAt: Date | null;
  setSyncEnabled: (enabled: boolean) => void;
  setLastSyncAt: (date: Date) => void;

  // UI State
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  // Notificaciones
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Estado inicial
      mode: 'standalone',
      apiBaseUrl: 'http://localhost:8000',
      syncEnabled: false,
      lastSyncAt: null,
      sidebarCollapsed: false,
      notifications: [],

      // Acciones
      setMode: (mode) =>
        set({
          mode,
          apiBaseUrl:
            mode === 'standalone'
              ? 'http://localhost:8000'
              : import.meta.env.VITE_SERVER_API_URL || 'https://api.company.local',
        }),

      setSyncEnabled: (enabled) => set({ syncEnabled: enabled }),

      setLastSyncAt: (date) => set({ lastSyncAt: date }),

      toggleSidebar: () => set({ sidebarCollapsed: !get().sidebarCollapsed }),

      addNotification: (notification) =>
        set({
          notifications: [
            ...get().notifications,
            {
              ...notification,
              id: crypto.randomUUID(),
              timestamp: new Date(),
            },
          ],
        }),

      removeNotification: (id) =>
        set({
          notifications: get().notifications.filter((n) => n.id !== id),
        }),
    }),
    {
      name: 'invokox-app-storage',
      partialize: (state) => ({
        mode: state.mode,
        syncEnabled: state.syncEnabled,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
