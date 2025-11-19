import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoicesApi, type InvoiceListParams } from '@/services/invoices';
import type { Invoice } from '@/types/invoice';
import { toast } from 'sonner';

export const INVOICES_QUERY_KEY = 'invoices';

// Hook para listar facturas con paginación
export function useInvoices(params?: InvoiceListParams) {
  return useQuery({
    queryKey: [INVOICES_QUERY_KEY, params],
    queryFn: () => invoicesApi.list(params),
    staleTime: 30000, // 30 segundos
  });
}

// Hook para obtener una factura por ID
export function useInvoice(id: string | null) {
  return useQuery({
    queryKey: [INVOICES_QUERY_KEY, id],
    queryFn: () => invoicesApi.getById(id!),
    enabled: !!id,
  });
}

// Hook para crear factura
export function useCreateInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Invoice>) => invoicesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY] });
      toast.success('Factura creada exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al crear factura');
    },
  });
}

// Hook para actualizar factura
export function useUpdateInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Invoice> }) =>
      invoicesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY, variables.id] });
      toast.success('Factura actualizada exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al actualizar factura');
    },
  });
}

// Hook para eliminar factura
export function useDeleteInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => invoicesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY] });
      toast.success('Factura eliminada exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al eliminar factura');
    },
  });
}

// Hook para subir archivo
export function useUploadInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) =>
      invoicesApi.uploadFile(file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY] });
      toast.success('Archivo subido, procesando con OCR...');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al subir archivo');
    },
  });
}

// Hook para aprobar factura
export function useApproveInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => invoicesApi.approve(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY, id] });
      toast.success('Factura aprobada exitosamente');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al aprobar factura');
    },
  });
}

// Hook para rechazar factura
export function useRejectInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      invoicesApi.reject(id, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [INVOICES_QUERY_KEY, variables.id] });
      toast.success('Factura rechazada');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al rechazar factura');
    },
  });
}
