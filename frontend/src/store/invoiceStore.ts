import { create } from 'zustand';
import { invoicesApi, InvoiceListParams } from '../services/invoices';
import type { Invoice } from '../types/invoice';

interface InvoiceFilters extends InvoiceListParams {
  search?: string;
}

interface InvoiceStore {
  // State
  invoices: Invoice[];
  selectedInvoice: Invoice | null;
  loading: boolean;
  error: string | null;
  filters: InvoiceFilters;

  // Actions - List
  loadInvoices: () => Promise<void>;
  setFilters: (filters: Partial<InvoiceFilters>) => void;
  clearFilters: () => void;

  // Actions - Single
  selectInvoice: (id: string) => Promise<void>;
  clearSelection: () => void;

  // Actions - Operations
  uploadInvoice: (file: File, createdBy: string, onProgress?: (progress: number) => void) => Promise<any>;
  processOCR: (invoiceId: string, engine?: string, useGpu?: boolean) => Promise<any>;
  approveInvoice: (invoiceId: string, approvedBy: string) => Promise<void>;
  rejectInvoice: (invoiceId: string, rejectedBy: string, reason?: string) => Promise<void>;

  // Actions - Batch
  batchApprove: (invoiceIds: number[], approvedBy: string) => Promise<any>;
  batchReject: (invoiceIds: number[], rejectedBy: string, reason?: string) => Promise<any>;

  // Utils
  refreshInvoice: (id: string) => Promise<void>;
}

export const useInvoiceStore = create<InvoiceStore>((set, get) => ({
  // Initial state
  invoices: [],
  selectedInvoice: null,
  loading: false,
  error: null,
  filters: {
    page: 1,
    limit: 100,
  },

  // Load invoices with current filters
  loadInvoices: async () => {
    set({ loading: true, error: null });
    try {
      const result = await invoicesApi.list(get().filters);

      // Backend podría retornar { items: [...] } o directamente [...]
      const invoices = Array.isArray(result) ? result : result.items || [];

      set({ invoices, loading: false });
    } catch (error: any) {
      console.error('Error loading invoices:', error);
      set({
        error: error.message || 'Error al cargar facturas',
        loading: false
      });
    }
  },

  // Set filters and reload
  setFilters: (filters) => {
    set((state) => ({
      filters: { ...state.filters, ...filters }
    }));
    get().loadInvoices();
  },

  // Clear all filters
  clearFilters: () => {
    set({
      filters: { page: 1, limit: 100 }
    });
    get().loadInvoices();
  },

  // Select and load single invoice
  selectInvoice: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const invoice = await invoicesApi.getById(id);
      set({ selectedInvoice: invoice, loading: false });
    } catch (error: any) {
      console.error('Error loading invoice:', error);
      set({
        error: error.message || 'Error al cargar factura',
        loading: false
      });
    }
  },

  // Clear selection
  clearSelection: () => {
    set({ selectedInvoice: null });
  },

  // Upload invoice file
  uploadInvoice: async (file: File, createdBy: string, onProgress?: (progress: number) => void) => {
    set({ loading: true, error: null });
    try {
      const result = await invoicesApi.uploadFile(file, onProgress);

      // Reload list
      await get().loadInvoices();

      set({ loading: false });
      return result;
    } catch (error: any) {
      console.error('Error uploading invoice:', error);
      set({
        error: error.message || 'Error al subir factura',
        loading: false
      });
      throw error;
    }
  },

  // Process OCR
  processOCR: async (invoiceId: string, engine?: string, useGpu?: boolean) => {
    set({ loading: true, error: null });
    try {
      const result = await invoicesApi.processOCR(invoiceId);
      set({ loading: false });
      return result;
    } catch (error: any) {
      console.error('Error processing OCR:', error);
      set({
        error: error.message || 'Error al procesar OCR',
        loading: false
      });
      throw error;
    }
  },

  // Approve invoice
  approveInvoice: async (invoiceId: string, approvedBy: string) => {
    set({ loading: true, error: null });
    try {
      await invoicesApi.approve(invoiceId);

      // Refresh invoice if selected
      if (get().selectedInvoice?.id === invoiceId) {
        await get().selectInvoice(invoiceId);
      }

      // Reload list
      await get().loadInvoices();

      set({ loading: false });
    } catch (error: any) {
      console.error('Error approving invoice:', error);
      set({
        error: error.message || 'Error al aprobar factura',
        loading: false
      });
      throw error;
    }
  },

  // Reject invoice
  rejectInvoice: async (invoiceId: string, rejectedBy: string, reason?: string) => {
    set({ loading: true, error: null });
    try {
      await invoicesApi.reject(invoiceId, reason);

      // Refresh invoice if selected
      if (get().selectedInvoice?.id === invoiceId) {
        await get().selectInvoice(invoiceId);
      }

      // Reload list
      await get().loadInvoices();

      set({ loading: false });
    } catch (error: any) {
      console.error('Error rejecting invoice:', error);
      set({
        error: error.message || 'Error al rechazar factura',
        loading: false
      });
      throw error;
    }
  },

  // Batch approve
  batchApprove: async (invoiceIds: number[], approvedBy: string) => {
    set({ loading: true, error: null });
    try {
      const result = await invoicesApi.batchApprove(invoiceIds, approvedBy);

      // Reload list
      await get().loadInvoices();

      set({ loading: false });
      return result;
    } catch (error: any) {
      console.error('Error batch approving:', error);
      set({
        error: error.message || 'Error en aprobación masiva',
        loading: false
      });
      throw error;
    }
  },

  // Batch reject
  batchReject: async (invoiceIds: number[], rejectedBy: string, reason?: string) => {
    set({ loading: true, error: null });
    try {
      const result = await invoicesApi.batchReject(invoiceIds, rejectedBy, reason);

      // Reload list
      await get().loadInvoices();

      set({ loading: false });
      return result;
    } catch (error: any) {
      console.error('Error batch rejecting:', error);
      set({
        error: error.message || 'Error en rechazo masivo',
        loading: false
      });
      throw error;
    }
  },

  // Refresh single invoice
  refreshInvoice: async (id: string) => {
    try {
      const invoice = await invoicesApi.getById(id);

      // Update in list
      set((state) => ({
        invoices: state.invoices.map((inv) =>
          inv.id === id ? invoice : inv
        ),
        selectedInvoice: state.selectedInvoice?.id === id ? invoice : state.selectedInvoice,
      }));
    } catch (error: any) {
      console.error('Error refreshing invoice:', error);
    }
  },
}));
