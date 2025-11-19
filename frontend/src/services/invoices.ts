import { api } from './api';
import type { Invoice } from '@/types/invoice';

export interface InvoiceListParams {
  page?: number;
  limit?: number;
  status?: string;
  search?: string;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface InvoiceListResponse {
  items: Invoice[];
  total: number;
  page: number;
  pages: number;
}

export const invoicesApi = {
  // Listar facturas con paginación y filtros
  list: async (params?: InvoiceListParams): Promise<InvoiceListResponse> => {
    const response = await api.get('/api/v1/invoices', { params });
    return response.data;
  },

  // Obtener una factura por ID
  getById: async (id: string): Promise<Invoice> => {
    const response = await api.get(`/api/v1/invoices/${id}`);
    return response.data;
  },

  // Crear nueva factura
  create: async (data: Partial<Invoice>): Promise<Invoice> => {
    const response = await api.post('/api/v1/invoices', data);
    return response.data;
  },

  // Actualizar factura
  update: async (id: string, data: Partial<Invoice>): Promise<Invoice> => {
    const response = await api.put(`/api/v1/invoices/${id}`, data);
    return response.data;
  },

  // Eliminar factura
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/invoices/${id}`);
  },

  // Subir archivo PDF/imagen para procesar
  uploadFile: async (file: File, onProgress?: (progress: number) => void): Promise<{ task_id: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/v1/invoices/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  // Procesar factura con OCR
  processOCR: async (invoiceId: string): Promise<{ task_id: string }> => {
    const response = await api.post(`/api/v1/invoices/${invoiceId}/process`);
    return response.data;
  },

  // Obtener estado de tarea de procesamiento
  getTaskStatus: async (taskId: string): Promise<{ status: string; result?: any; error?: string }> => {
    const response = await api.get(`/api/v1/tasks/${taskId}`);
    return response.data;
  },

  // Aprobar factura
  approve: async (invoiceId: string): Promise<Invoice> => {
    const response = await api.post(`/api/v1/invoices/${invoiceId}/approve`);
    return response.data;
  },

  // Rechazar factura
  reject: async (invoiceId: string, reason?: string): Promise<Invoice> => {
    const response = await api.post(`/api/v1/invoices/${invoiceId}/reject`, { reason });
    return response.data;
  },

  // Exportar facturas a Excel
  exportToExcel: async (invoiceIds: string[]): Promise<Blob> => {
    const response = await api.post(
      '/api/v1/invoices/export/excel',
      { invoice_ids: invoiceIds },
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Exportar facturas a CSV
  exportToCSV: async (invoiceIds: string[]): Promise<Blob> => {
    const response = await api.post(
      '/api/v1/invoices/export/csv',
      { invoice_ids: invoiceIds },
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Batch approve - Aprobar múltiples facturas
  batchApprove: async (invoiceIds: number[], approvedBy: string) => {
    const response = await api.post('/api/v1/invoices/batch/approve', {
      invoice_ids: invoiceIds,
      approved_by: approvedBy
    });
    return response.data;
  },

  // Batch reject - Rechazar múltiples facturas
  batchReject: async (invoiceIds: number[], rejectedBy: string, reason?: string) => {
    const response = await api.post('/api/v1/invoices/batch/reject', {
      invoice_ids: invoiceIds,
      rejected_by: rejectedBy,
      reason
    });
    return response.data;
  },
};
