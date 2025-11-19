import axios from 'axios';

// Detectar si estamos en modo Electron o Web
const isElectron = typeof window !== 'undefined' && (window as any).electronAPI;

// Base URL dependiendo del entorno
const getBaseURL = () => {
  // En desarrollo siempre usar localhost
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }

  // En producción, si es Electron usar localhost, si es web usar variable de entorno
  if (isElectron) {
    return 'http://localhost:8000';
  }

  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

// Instancia de Axios configurada
export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir token de autenticación si existe
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('auth_token');
      // Aquí podrías redirigir al login cuando esté implementado
    }

    return Promise.reject(error);
  }
);

// Helper para manejar errores
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }

  if (error.message) {
    return error.message;
  }

  return 'Error desconocido. Por favor, intente nuevamente.';
};
