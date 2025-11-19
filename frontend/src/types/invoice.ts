export type InvoiceStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'APPROVED' | 'REJECTED' | 'ERROR';
export type Currency = 'USD' | 'PEN' | 'EUR' | 'CLP' | 'MXN';
export type CompanyType = 'EMISOR' | 'RECEPTOR' | 'AMBOS';
export type OcrEngine = 'Donut' | 'PaddleOCR' | 'Docling' | 'Tesseract';

export interface Company {
  id: string | number;  // Backend uses number, allow both for transition
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
  id: string | number;  // Backend uses number, allow both for transition
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
  id: string | number;  // Backend uses number, allow both for transition
  series: string;
  issue_date: string;
  due_date?: string;
  issuer_id: string | number;  // Backend uses number
  issuer_name: string;
  issuer_tax_id: string;
  receiver_id: string | number;  // Backend uses number
  receiver_name: string;
  receiver_tax_id: string;
  currency: Currency;
  status: InvoiceStatus;
  ocr_confidence: number;
  ocr_engine?: OcrEngine;  // Optional since it may be null before OCR
  processing_time?: number;
  file_path: string;
  subtotal: number;
  tax_total: number;
  discount_total: number;
  withholding_total: number;
  total: number;
  notes?: string;
  items: InvoiceItem[];
  payments?: Payment[];  // Optional since it may not be present
  created_at: string;
  updated_at?: string;  // Optional
  created_by: string;
  updated_by?: string;
}

export interface AuditLog {
  id: string | number;  // Backend uses number, allow both for transition
  invoice_id: string | number;  // Backend uses number
  user_id: string;
  user_name: string;
  action: string;
  changes: Record<string, any>;
  timestamp: string;
}
