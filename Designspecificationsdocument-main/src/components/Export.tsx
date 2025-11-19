import { useState } from 'react';
import { mockInvoices } from '../data/mockData';
import { Download, FileSpreadsheet, FileText, FileJson, Check } from 'lucide-react';

export function Export() {
  const [format, setFormat] = useState<'excel' | 'csv' | 'pdf' | 'json'>('excel');
  const [includeItems, setIncludeItems] = useState(false);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string[]>(['APPROVED']);

  const filteredCount = mockInvoices.filter(inv => {
    const matchesDate = (!dateFrom || inv.issue_date >= dateFrom) && (!dateTo || inv.issue_date <= dateTo);
    const matchesStatus = selectedStatus.length === 0 || selectedStatus.includes(inv.status);
    return matchesDate && matchesStatus;
  }).length;

  const handleExport = () => {
    alert(`Exportando ${filteredCount} facturas en formato ${format.toUpperCase()}`);
  };

  const toggleStatus = (status: string) => {
    setSelectedStatus(prev =>
      prev.includes(status)
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Exportación</h1>
        <p className="text-gray-600">Exporta facturas en diferentes formatos</p>
      </div>

      <div className="space-y-6">
        {/* Format Selection */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Formato de Exportación</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <FormatOption
              icon={<FileSpreadsheet className="w-6 h-6" />}
              label="Excel"
              selected={format === 'excel'}
              onClick={() => setFormat('excel')}
            />
            <FormatOption
              icon={<FileText className="w-6 h-6" />}
              label="CSV"
              selected={format === 'csv'}
              onClick={() => setFormat('csv')}
            />
            <FormatOption
              icon={<FileText className="w-6 h-6" />}
              label="PDF"
              selected={format === 'pdf'}
              onClick={() => setFormat('pdf')}
            />
            <FormatOption
              icon={<FileJson className="w-6 h-6" />}
              label="JSON"
              selected={format === 'json'}
              onClick={() => setFormat('json')}
            />
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Filtros</h2>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 mb-2">Fecha Desde</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-gray-700 mb-2">Fecha Hasta</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-700 mb-2">Estados</label>
              <div className="flex flex-wrap gap-2">
                {['PENDING', 'PROCESSING', 'COMPLETED', 'APPROVED', 'REJECTED'].map(status => (
                  <button
                    key={status}
                    onClick={() => toggleStatus(status)}
                    className={`px-4 py-2 rounded-lg border transition-colors ${
                      selectedStatus.includes(status)
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:border-blue-300'
                    }`}
                  >
                    {status === 'PENDING' && 'Pendiente'}
                    {status === 'PROCESSING' && 'Procesando'}
                    {status === 'COMPLETED' && 'Completada'}
                    {status === 'APPROVED' && 'Aprobada'}
                    {status === 'REJECTED' && 'Rechazada'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Options */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Opciones</h2>
          
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={includeItems}
                onChange={(e) => setIncludeItems(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <span className="text-gray-900">Incluir desglose de ítems</span>
                <p className="text-gray-600 text-sm">Genera una hoja/sección adicional con el detalle de cada ítem</p>
              </div>
            </label>
          </div>
        </div>

        {/* Preview */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Vista Previa</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Facturas a exportar:</span>
              <span className="text-gray-900">{filteredCount}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Formato:</span>
              <span className="text-gray-900">{format.toUpperCase()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Desglose de ítems:</span>
              <span className="text-gray-900">{includeItems ? 'Sí' : 'No'}</span>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-gray-700 mb-3">Columnas incluidas:</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
              {[
                'Serie',
                'Emisor (Nombre)',
                'Emisor (RUC)',
                'Receptor (Nombre)',
                'Receptor (RUC)',
                'Fecha Emisión',
                'Fecha Vencimiento',
                'Moneda',
                'Subtotal',
                'Impuestos',
                'Total',
                'Estado',
                'Confianza OCR'
              ].map(col => (
                <div key={col} className="flex items-center gap-2 text-gray-700">
                  <Check className="w-4 h-4 text-green-600" />
                  <span>{col}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Export Button */}
        <div className="flex gap-4">
          <button
            onClick={handleExport}
            disabled={filteredCount === 0}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Download className="w-5 h-5" />
            Exportar {filteredCount} Factura{filteredCount !== 1 ? 's' : ''}
          </button>
        </div>
      </div>
    </div>
  );
}

interface FormatOptionProps {
  icon: React.ReactNode;
  label: string;
  selected: boolean;
  onClick: () => void;
}

function FormatOption({ icon, label, selected, onClick }: FormatOptionProps) {
  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-lg border-2 transition-all ${
        selected
          ? 'border-blue-600 bg-blue-50'
          : 'border-gray-200 bg-white hover:border-blue-300'
      }`}
    >
      <div className={`flex flex-col items-center gap-2 ${
        selected ? 'text-blue-600' : 'text-gray-700'
      }`}>
        {icon}
        <span className="font-medium">{label}</span>
      </div>
    </button>
  );
}
