import { View } from '../App';
import { mockInvoices, mockAuditLogs } from '../data/mockData';
import { Download, ArrowLeft, FileText } from 'lucide-react';

interface ViewInvoiceProps {
  invoiceId: string;
  navigateTo: (view: View) => void;
}

export function ViewInvoice({ invoiceId, navigateTo }: ViewInvoiceProps) {
  const invoice = mockInvoices.find(inv => inv.id === invoiceId);
  const auditLogs = mockAuditLogs.filter(log => log.invoice_id === invoiceId);

  if (!invoice) {
    return <div className="p-8">Factura no encontrada</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigateTo('invoices')}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Volver a facturas
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-gray-900 mb-2">Factura {invoice.series}</h1>
            <div className="flex gap-4 text-sm">
              <span className={`px-3 py-1 rounded ${
                invoice.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {invoice.status === 'APPROVED' ? 'Aprobada' : 'Rechazada'}
              </span>
              <span className="text-gray-600">
                Confianza OCR: {(invoice.ocr_confidence * 100).toFixed(0)}%
              </span>
              <span className="text-gray-600">
                Motor: {invoice.ocr_engine}
              </span>
            </div>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <Download className="w-4 h-4" />
              Descargar PDF
            </button>
            <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2">
              <Download className="w-4 h-4" />
              Exportar Excel
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* General Info */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-gray-900 mb-4">Información General</h2>
            <div className="grid grid-cols-2 gap-4">
              <InfoField label="Serie" value={invoice.series} />
              <InfoField label="Moneda" value={invoice.currency} />
              <InfoField 
                label="Fecha de Emisión" 
                value={new Date(invoice.issue_date).toLocaleDateString('es-ES')} 
              />
              <InfoField 
                label="Fecha de Vencimiento" 
                value={invoice.due_date ? new Date(invoice.due_date).toLocaleDateString('es-ES') : 'N/A'} 
              />
            </div>
          </div>

          {/* Parties */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-gray-900 mb-4">Emisor y Receptor</h2>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="text-gray-700 mb-2">Emisor</h3>
                <p className="text-gray-900">{invoice.issuer_name}</p>
                <p className="text-gray-600 text-sm">RUC: {invoice.issuer_tax_id}</p>
              </div>
              <div>
                <h3 className="text-gray-700 mb-2">Receptor</h3>
                <p className="text-gray-900">{invoice.receiver_name}</p>
                <p className="text-gray-600 text-sm">RUC: {invoice.receiver_tax_id}</p>
              </div>
            </div>
          </div>

          {/* Items */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-gray-900 mb-4">Ítems</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-gray-700">Descripción</th>
                    <th className="px-4 py-3 text-right text-gray-700">Cant.</th>
                    <th className="px-4 py-3 text-right text-gray-700">Precio</th>
                    <th className="px-4 py-3 text-right text-gray-700">Desc.</th>
                    <th className="px-4 py-3 text-right text-gray-700">IVA</th>
                    <th className="px-4 py-3 text-right text-gray-700">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {invoice.items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-4 py-3 text-gray-900">{item.description}</td>
                      <td className="px-4 py-3 text-right text-gray-700">{item.quantity}</td>
                      <td className="px-4 py-3 text-right text-gray-700">{item.unit_price.toFixed(2)}</td>
                      <td className="px-4 py-3 text-right text-gray-700">{item.discount_percent}%</td>
                      <td className="px-4 py-3 text-right text-gray-700">{item.tax_percent}%</td>
                      <td className="px-4 py-3 text-right text-gray-900">{item.line_total.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Totals */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-gray-900 mb-4">Totales</h2>
            <div className="space-y-2">
              <div className="flex justify-between text-gray-700">
                <span>Subtotal:</span>
                <span>{invoice.currency} {invoice.subtotal.toFixed(2)}</span>
              </div>
              {invoice.discount_total > 0 && (
                <div className="flex justify-between text-gray-700">
                  <span>Descuentos:</span>
                  <span>-{invoice.currency} {invoice.discount_total.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-gray-700">
                <span>Impuestos:</span>
                <span>{invoice.currency} {invoice.tax_total.toFixed(2)}</span>
              </div>
              {invoice.withholding_total > 0 && (
                <div className="flex justify-between text-gray-700">
                  <span>Retenciones:</span>
                  <span>-{invoice.currency} {invoice.withholding_total.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-gray-900 pt-2 border-t border-gray-300">
                <span>Total:</span>
                <span>{invoice.currency} {invoice.total.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Payments */}
          {invoice.payments.length > 0 && (
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h2 className="text-gray-900 mb-4">Cuotas de Pago</h2>
              <div className="space-y-3">
                {invoice.payments.map((payment) => (
                  <div key={payment.number} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="text-gray-900">Cuota {payment.number}</span>
                      <span className="text-gray-600 text-sm ml-4">
                        Vence: {new Date(payment.due_date).toLocaleDateString('es-ES')}
                      </span>
                    </div>
                    <span className="text-gray-900">
                      {invoice.currency} {payment.amount.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          {invoice.notes && (
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h2 className="text-gray-900 mb-4">Notas</h2>
              <p className="text-gray-700">{invoice.notes}</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* PDF Preview */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-gray-900 mb-4">Documento Original</h3>
            <div className="aspect-[3/4] bg-gray-100 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-400">
                <FileText className="w-12 h-12 mx-auto mb-2" />
                <p className="text-sm">Vista previa PDF</p>
              </div>
            </div>
            <button className="w-full mt-4 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center justify-center gap-2">
              <Download className="w-4 h-4" />
              Descargar Original
            </button>
          </div>

          {/* Metadata */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-gray-900 mb-4">Metadatos</h3>
            <div className="space-y-3 text-sm">
              <MetaItem label="Creado" value={new Date(invoice.created_at).toLocaleString('es-ES')} />
              <MetaItem label="Actualizado" value={new Date(invoice.updated_at).toLocaleString('es-ES')} />
              <MetaItem label="Creado por" value={invoice.created_by} />
              {invoice.updated_by && <MetaItem label="Actualizado por" value={invoice.updated_by} />}
              {invoice.processing_time && (
                <MetaItem label="Tiempo de procesamiento" value={`${invoice.processing_time.toFixed(1)}s`} />
              )}
            </div>
          </div>

          {/* Audit Log */}
          {auditLogs.length > 0 && (
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-gray-900 mb-4">Historial de Auditoría</h3>
              <div className="space-y-3">
                {auditLogs.map((log) => (
                  <div key={log.id} className="text-sm">
                    <p className="text-gray-900">{log.action.replace('_', ' ')}</p>
                    <p className="text-gray-600">{log.user_name}</p>
                    <p className="text-gray-500 text-xs">
                      {new Date(log.timestamp).toLocaleString('es-ES')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-gray-600 text-sm mb-1">{label}</p>
      <p className="text-gray-900">{value}</p>
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-600">{label}:</span>
      <span className="text-gray-900">{value}</span>
    </div>
  );
}
