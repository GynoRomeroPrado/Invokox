export type InvoiceStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'APPROVED' | 'REJECTED' | 'ERROR';
export type Currency = 'USD' | 'PEN' | 'EUR' | 'CLP' | 'MXN';
export type CompanyType = 'EMISOR' | 'RECEPTOR' | 'AMBOS';
export type OcrEngine = 'PaddleOCR' | 'Docling' | 'Tesseract';

export interface Company {
  id: string;
  tax_id: string;
  name: string;
  commercial_name?: string;
  type: CompanyType;
  address?: string;
  email?: string;
  phone?: string;
  website?: string;
  invoice_count: number;
  created_at: string;
}

export interface InvoiceItem {
  id: string;
  description: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  tax_percent: number;
  line_total: number;
}

export interface Payment {
  number: number;
  due_date: string;
  amount: number;
}

export interface Invoice {
  id: string;
  series: string;
  issue_date: string;
  due_date?: string;
  issuer_id: string;
  issuer_name: string;
  issuer_tax_id: string;
  receiver_id: string;
  receiver_name: string;
  receiver_tax_id: string;
  currency: Currency;
  status: InvoiceStatus;
  ocr_confidence: number;
  ocr_engine: OcrEngine;
  processing_time?: number;
  file_path: string;
  subtotal: number;
  tax_total: number;
  discount_total: number;
  withholding_total: number;
  total: number;
  notes?: string;
  items: InvoiceItem[];
  payments: Payment[];
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by?: string;
}

export interface AuditLog {
  id: string;
  invoice_id: string;
  user_id: string;
  user_name: string;
  action: string;
  changes: Record<string, any>;
  timestamp: string;
}
