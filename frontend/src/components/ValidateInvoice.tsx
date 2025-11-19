import { useState } from 'react';
import { View, UserRole } from '../App';
import { mockInvoices } from '../data/mockData';
import { InvoiceItem, Payment } from '../types/invoice';
import { Save, CheckCircle, XCircle, AlertCircle, Plus, Trash2, ZoomIn, ZoomOut, RotateCw } from 'lucide-react';

interface ValidateInvoiceProps {
  invoiceId: string;
  navigateTo: (view: View) => void;
  userRole: UserRole;
}

export function ValidateInvoice({ invoiceId, navigateTo, userRole }: ValidateInvoiceProps) {
  const originalInvoice = mockInvoices.find(inv => inv.id === invoiceId);
  
  if (!originalInvoice) {
    return <div className="p-8">Factura no encontrada</div>;
  }

  const [series, setSeries] = useState(originalInvoice.series);
  const [issueDate, setIssueDate] = useState(originalInvoice.issue_date);
  const [dueDate, setDueDate] = useState(originalInvoice.due_date || '');
  const [issuerName, setIssuerName] = useState(originalInvoice.issuer_name);
  const [issuerTaxId, setIssuerTaxId] = useState(originalInvoice.issuer_tax_id);
  const [receiverName, setReceiverName] = useState(originalInvoice.receiver_name);
  const [receiverTaxId, setReceiverTaxId] = useState(originalInvoice.receiver_tax_id);
  const [currency, setCurrency] = useState(originalInvoice.currency);
  const [notes, setNotes] = useState(originalInvoice.notes || '');
  const [items, setItems] = useState<InvoiceItem[]>(originalInvoice.items);
  const [payments, setPayments] = useState<Payment[]>(originalInvoice.payments);
  const [zoom, setZoom] = useState(100);

  const addItem = () => {
    setItems([...items, {
      id: `item-${Date.now()}`,
      description: '',
      quantity: 1,
      unit_price: 0,
      discount_percent: 0,
      tax_percent: 18,
      line_total: 0
    }]);
  };

  const removeItem = (id: string) => {
    setItems(items.filter(item => item.id !== id));
  };

  const updateItem = (id: string, field: keyof InvoiceItem, value: any) => {
    setItems(items.map(item => {
      if (item.id !== id) return item;
      
      const updated = { ...item, [field]: value };
      
      // Recalculate line total
      const subtotal = updated.quantity * updated.unit_price;
      const afterDiscount = subtotal * (1 - updated.discount_percent / 100);
      updated.line_total = afterDiscount * (1 + updated.tax_percent / 100);
      
      return updated;
    }));
  };

  const addPayment = () => {
    setPayments([...payments, {
      number: payments.length + 1,
      due_date: '',
      amount: 0
    }]);
  };

  const removePayment = (index: number) => {
    setPayments(payments.filter((_, i) => i !== index));
  };

  const updatePayment = (index: number, field: keyof Payment, value: any) => {
    setPayments(payments.map((payment, i) => 
      i === index ? { ...payment, [field]: value } : payment
    ));
  };

  const calculateTotals = () => {
    const subtotal = items.reduce((sum, item) => {
      const lineSubtotal = item.quantity * item.unit_price * (1 - item.discount_percent / 100);
      return sum + lineSubtotal;
    }, 0);

    const taxTotal = items.reduce((sum, item) => {
      const lineSubtotal = item.quantity * item.unit_price * (1 - item.discount_percent / 100);
      const lineTax = lineSubtotal * (item.tax_percent / 100);
      return sum + lineTax;
    }, 0);

    const total = subtotal + taxTotal;

    return { subtotal, taxTotal, total };
  };

  const { subtotal, taxTotal, total } = calculateTotals();

  const handleSave = () => {
    if (items.length === 0) {
      alert('Debe haber al menos un ítem en la factura');
      return;
    }
    alert('Factura guardada');
    navigateTo('invoices');
  };

  const handleApprove = () => {
    if (userRole === 'viewer') {
      alert('No tienes permisos para aprobar facturas');
      return;
    }
    if (items.length === 0) {
      alert('Debe haber al menos un ítem en la factura');
      return;
    }
    alert('Factura aprobada');
    navigateTo('invoices');
  };

  const handleReject = () => {
    if (userRole === 'viewer') {
      alert('No tienes permisos para rechazar facturas');
      return;
    }
    const reason = prompt('Motivo del rechazo:');
    if (reason) {
      alert('Factura rechazada');
      navigateTo('invoices');
    }
  };

  return (
    <div className="flex h-full">
      {/* PDF Viewer */}
      <div className="w-1/2 bg-gray-900 p-4 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white">Vista Previa del Documento</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setZoom(Math.max(50, zoom - 10))}
              className="p-2 bg-gray-800 text-white rounded hover:bg-gray-700"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="px-3 py-2 bg-gray-800 text-white rounded">{zoom}%</span>
            <button
              onClick={() => setZoom(Math.min(200, zoom + 10))}
              className="p-2 bg-gray-800 text-white rounded hover:bg-gray-700"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button className="p-2 bg-gray-800 text-white rounded hover:bg-gray-700">
              <RotateCw className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="flex-1 bg-gray-800 rounded-lg flex items-center justify-center overflow-auto">
          <div className="text-gray-400 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>Vista previa del PDF</p>
            <p className="text-sm mt-2">{originalInvoice.file_path}</p>
          </div>
        </div>
      </div>

      {/* Edit Form */}
      <div className="w-1/2 bg-white overflow-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-gray-900">Validar Factura</h2>
              <p className="text-gray-600 text-sm mt-1">
                Motor: {originalInvoice.ocr_engine} • Confianza: {(originalInvoice.ocr_confidence * 100).toFixed(0)}%
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Guardar
              </button>
              {userRole !== 'viewer' && (
                <>
                  <button
                    onClick={handleApprove}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Aprobar
                  </button>
                  <button
                    onClick={handleReject}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                  >
                    <XCircle className="w-4 h-4" />
                    Rechazar
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Header Fields */}
          <div className="space-y-6">
            <section>
              <h3 className="text-gray-900 mb-4">Información General</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-700 mb-2">Serie</label>
                  <input
                    type="text"
                    value={series}
                    onChange={(e) => setSeries(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Moneda</label>
                  <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="USD">USD</option>
                    <option value="PEN">PEN</option>
                    <option value="EUR">EUR</option>
                    <option value="CLP">CLP</option>
                    <option value="MXN">MXN</option>
                  </select>
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Fecha de Emisión</label>
                  <input
                    type="date"
                    value={issueDate}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Fecha de Vencimiento</label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </section>

            {/* Issuer/Receiver */}
            <section>
              <h3 className="text-gray-900 mb-4">Emisor y Receptor</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-700 mb-2">Emisor (Nombre)</label>
                  <input
                    type="text"
                    value={issuerName}
                    onChange={(e) => setIssuerName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Emisor (RUC/Tax ID)</label>
                  <input
                    type="text"
                    value={issuerTaxId}
                    onChange={(e) => setIssuerTaxId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Receptor (Nombre)</label>
                  <input
                    type="text"
                    value={receiverName}
                    onChange={(e) => setReceiverName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Receptor (RUC/Tax ID)</label>
                  <input
                    type="text"
                    value={receiverTaxId}
                    onChange={(e) => setReceiverTaxId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </section>

            {/* Items */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-900">Ítems de Factura</h3>
                <button
                  onClick={addItem}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Agregar Ítem
                </button>
              </div>

              {items.length === 0 ? (
                <div className="p-6 border-2 border-dashed border-gray-300 rounded-lg text-center">
                  <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">No hay ítems. Agrega al menos uno.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {items.map((item, index) => (
                    <div key={item.id} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-start gap-4">
                        <div className="flex-1 grid grid-cols-6 gap-3">
                          <div className="col-span-2">
                            <label className="block text-gray-700 text-sm mb-1">Descripción</label>
                            <input
                              type="text"
                              value={item.description}
                              onChange={(e) => updateItem(item.id, 'description', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-700 text-sm mb-1">Cantidad</label>
                            <input
                              type="number"
                              value={item.quantity}
                              onChange={(e) => updateItem(item.id, 'quantity', Number(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-700 text-sm mb-1">Precio Unit.</label>
                            <input
                              type="number"
                              step="0.01"
                              value={item.unit_price}
                              onChange={(e) => updateItem(item.id, 'unit_price', Number(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-700 text-sm mb-1">Desc. %</label>
                            <input
                              type="number"
                              value={item.discount_percent}
                              onChange={(e) => updateItem(item.id, 'discount_percent', Number(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-gray-700 text-sm mb-1">IVA %</label>
                            <input
                              type="number"
                              value={item.tax_percent}
                              onChange={(e) => updateItem(item.id, 'tax_percent', Number(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                        </div>
                        <div className="flex flex-col gap-2">
                          <span className="text-gray-700 text-sm">Total Línea</span>
                          <span className="text-gray-900">{item.line_total.toFixed(2)}</span>
                          <button
                            onClick={() => removeItem(item.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Totals */}
            <section className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-gray-900 mb-4">Resumen de Totales</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-gray-700">
                  <span>Subtotal:</span>
                  <span>{currency} {subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-700">
                  <span>Impuestos:</span>
                  <span>{currency} {taxTotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-900 pt-2 border-t border-gray-300">
                  <span>Total:</span>
                  <span>{currency} {total.toFixed(2)}</span>
                </div>
              </div>
            </section>

            {/* Payments */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-900">Cuotas de Pago</h3>
                <button
                  onClick={addPayment}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Agregar Cuota
                </button>
              </div>

              {payments.length > 0 && (
                <div className="space-y-3">
                  {payments.map((payment, index) => (
                    <div key={index} className="flex gap-3 items-center">
                      <input
                        type="text"
                        value={`Cuota ${payment.number}`}
                        disabled
                        className="w-32 px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-sm"
                      />
                      <input
                        type="date"
                        value={payment.due_date}
                        onChange={(e) => updatePayment(index, 'due_date', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                      <input
                        type="number"
                        step="0.01"
                        value={payment.amount}
                        onChange={(e) => updatePayment(index, 'amount', Number(e.target.value))}
                        className="w-40 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        placeholder="Monto"
                      />
                      <button
                        onClick={() => removePayment(index)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Notes */}
            <section>
              <label className="block text-gray-700 mb-2">Notas</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Notas adicionales..."
              />
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

function FileText({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}
