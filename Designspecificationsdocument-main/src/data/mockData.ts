import { Invoice, Company, AuditLog } from '../types/invoice';

export const mockCompanies: Company[] = [
  {
    id: 'comp-1',
    tax_id: '20123456789',
    name: 'Corporación Industrial S.A.',
    commercial_name: 'CORPIND',
    type: 'EMISOR',
    address: 'Av. Industrial 123, Lima',
    email: 'contacto@corpind.pe',
    phone: '+51 1 234 5678',
    website: 'www.corpind.pe',
    invoice_count: 45,
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 'comp-2',
    tax_id: '20987654321',
    name: 'Servicios Tecnológicos Ltda.',
    commercial_name: 'ServiTech',
    type: 'RECEPTOR',
    address: 'Jr. Tecnología 456, Santiago',
    email: 'info@servitech.cl',
    phone: '+56 2 3456 7890',
    invoice_count: 28,
    created_at: '2024-02-20T14:20:00Z'
  },
  {
    id: 'comp-3',
    tax_id: '20555444333',
    name: 'Distribuidora Global Inc.',
    commercial_name: 'DistriGlobal',
    type: 'AMBOS',
    address: 'Calle Comercio 789, Ciudad de México',
    email: 'ventas@distriglobal.mx',
    phone: '+52 55 1234 5678',
    invoice_count: 67,
    created_at: '2024-01-10T09:15:00Z'
  },
  {
    id: 'comp-4',
    tax_id: '20111222333',
    name: 'Consultoría Empresarial S.A.C.',
    type: 'EMISOR',
    invoice_count: 12,
    created_at: '2024-03-05T11:45:00Z'
  }
];

export const mockInvoices: Invoice[] = [
  {
    id: 'inv-1',
    series: 'F001-00123',
    issue_date: '2024-11-15',
    due_date: '2024-12-15',
    issuer_id: 'comp-1',
    issuer_name: 'Corporación Industrial S.A.',
    issuer_tax_id: '20123456789',
    receiver_id: 'comp-2',
    receiver_name: 'Servicios Tecnológicos Ltda.',
    receiver_tax_id: '20987654321',
    currency: 'USD',
    status: 'PENDING',
    ocr_confidence: 0.92,
    ocr_engine: 'PaddleOCR',
    processing_time: 3.2,
    file_path: '/uploads/invoice-123.pdf',
    subtotal: 10000.00,
    tax_total: 1800.00,
    discount_total: 0,
    withholding_total: 0,
    total: 11800.00,
    notes: 'Factura por servicios de consultoría',
    items: [
      {
        id: 'item-1',
        description: 'Consultoría estratégica - 40 horas',
        quantity: 40,
        unit_price: 250.00,
        discount_percent: 0,
        tax_percent: 18,
        line_total: 10000.00
      }
    ],
    payments: [
      { number: 1, due_date: '2024-12-15', amount: 11800.00 }
    ],
    created_at: '2024-11-15T10:30:00Z',
    updated_at: '2024-11-15T10:30:00Z',
    created_by: 'user-1'
  },
  {
    id: 'inv-2',
    series: 'B002-00456',
    issue_date: '2024-11-10',
    due_date: '2025-01-10',
    issuer_id: 'comp-3',
    issuer_name: 'Distribuidora Global Inc.',
    issuer_tax_id: '20555444333',
    receiver_id: 'comp-1',
    receiver_name: 'Corporación Industrial S.A.',
    receiver_tax_id: '20123456789',
    currency: 'PEN',
    status: 'APPROVED',
    ocr_confidence: 0.98,
    ocr_engine: 'Docling',
    processing_time: 2.8,
    file_path: '/uploads/invoice-456.pdf',
    subtotal: 25000.00,
    tax_total: 4500.00,
    discount_total: 1250.00,
    withholding_total: 0,
    total: 28250.00,
    items: [
      {
        id: 'item-2',
        description: 'Equipos de cómputo',
        quantity: 10,
        unit_price: 2500.00,
        discount_percent: 5,
        tax_percent: 18,
        line_total: 23750.00
      },
      {
        id: 'item-3',
        description: 'Software de gestión',
        quantity: 5,
        unit_price: 900.00,
        discount_percent: 0,
        tax_percent: 18,
        line_total: 4500.00
      }
    ],
    payments: [
      { number: 1, due_date: '2024-12-10', amount: 14125.00 },
      { number: 2, due_date: '2025-01-10', amount: 14125.00 }
    ],
    created_at: '2024-11-10T14:20:00Z',
    updated_at: '2024-11-11T09:15:00Z',
    created_by: 'user-1',
    updated_by: 'user-2'
  },
  {
    id: 'inv-3',
    series: 'F001-00789',
    issue_date: '2024-11-12',
    issuer_id: 'comp-4',
    issuer_name: 'Consultoría Empresarial S.A.C.',
    issuer_tax_id: '20111222333',
    receiver_id: 'comp-3',
    receiver_name: 'Distribuidora Global Inc.',
    receiver_tax_id: '20555444333',
    currency: 'USD',
    status: 'PROCESSING',
    ocr_confidence: 0.75,
    ocr_engine: 'Tesseract',
    processing_time: 5.1,
    file_path: '/uploads/invoice-789.pdf',
    subtotal: 5400.00,
    tax_total: 972.00,
    discount_total: 0,
    withholding_total: 0,
    total: 6372.00,
    items: [
      {
        id: 'item-4',
        description: 'Auditoría financiera',
        quantity: 1,
        unit_price: 5400.00,
        discount_percent: 0,
        tax_percent: 18,
        line_total: 5400.00
      }
    ],
    payments: [
      { number: 1, due_date: '2024-12-12', amount: 6372.00 }
    ],
    created_at: '2024-11-12T16:45:00Z',
    updated_at: '2024-11-12T16:48:00Z',
    created_by: 'user-3'
  },
  {
    id: 'inv-4',
    series: 'F003-00234',
    issue_date: '2024-11-08',
    issuer_id: 'comp-1',
    issuer_name: 'Corporación Industrial S.A.',
    issuer_tax_id: '20123456789',
    receiver_id: 'comp-3',
    receiver_name: 'Distribuidora Global Inc.',
    receiver_tax_id: '20555444333',
    currency: 'EUR',
    status: 'REJECTED',
    ocr_confidence: 0.45,
    ocr_engine: 'PaddleOCR',
    processing_time: 4.2,
    file_path: '/uploads/invoice-234.pdf',
    subtotal: 3200.00,
    tax_total: 576.00,
    discount_total: 0,
    withholding_total: 0,
    total: 3776.00,
    notes: 'Rechazada por discrepancia en totales',
    items: [
      {
        id: 'item-5',
        description: 'Materiales de construcción',
        quantity: 100,
        unit_price: 32.00,
        discount_percent: 0,
        tax_percent: 18,
        line_total: 3200.00
      }
    ],
    payments: [
      { number: 1, due_date: '2024-12-08', amount: 3776.00 }
    ],
    created_at: '2024-11-08T11:20:00Z',
    updated_at: '2024-11-09T10:30:00Z',
    created_by: 'user-2',
    updated_by: 'user-1'
  },
  {
    id: 'inv-5',
    series: 'B001-00567',
    issue_date: '2024-11-05',
    issuer_id: 'comp-3',
    issuer_name: 'Distribuidora Global Inc.',
    issuer_tax_id: '20555444333',
    receiver_id: 'comp-2',
    receiver_name: 'Servicios Tecnológicos Ltda.',
    receiver_tax_id: '20987654321',
    currency: 'CLP',
    status: 'ERROR',
    ocr_confidence: 0.32,
    ocr_engine: 'Tesseract',
    file_path: '/uploads/invoice-567.pdf',
    subtotal: 0,
    tax_total: 0,
    discount_total: 0,
    withholding_total: 0,
    total: 0,
    notes: 'Error en procesamiento OCR - archivo ilegible',
    items: [],
    payments: [],
    created_at: '2024-11-05T09:10:00Z',
    updated_at: '2024-11-05T09:15:00Z',
    created_by: 'user-3'
  }
];

export const mockAuditLogs: AuditLog[] = [
  {
    id: 'audit-1',
    invoice_id: 'inv-2',
    user_id: 'user-1',
    user_name: 'Juan Pérez',
    action: 'STATUS_CHANGE',
    changes: {
      status: { from: 'PENDING', to: 'APPROVED' }
    },
    timestamp: '2024-11-11T09:15:00Z'
  },
  {
    id: 'audit-2',
    invoice_id: 'inv-2',
    user_id: 'user-2',
    user_name: 'María González',
    action: 'ITEM_UPDATED',
    changes: {
      items: { 
        updated: 'item-2',
        field: 'quantity',
        from: 8,
        to: 10
      }
    },
    timestamp: '2024-11-11T09:10:00Z'
  },
  {
    id: 'audit-3',
    invoice_id: 'inv-4',
    user_id: 'user-1',
    user_name: 'Juan Pérez',
    action: 'STATUS_CHANGE',
    changes: {
      status: { from: 'PENDING', to: 'REJECTED' },
      notes: 'Rechazada por discrepancia en totales'
    },
    timestamp: '2024-11-09T10:30:00Z'
  }
];
