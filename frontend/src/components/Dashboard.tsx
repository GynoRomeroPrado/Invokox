import { View } from '../App';
import { mockInvoices } from '../data/mockData';
import { FileText, Upload, CheckCircle, XCircle, Clock, AlertCircle, TrendingUp, DollarSign } from 'lucide-react';

interface DashboardProps {
  navigateTo: (view: View) => void;
}

export function Dashboard({ navigateTo }: DashboardProps) {
  const totalInvoices = mockInvoices.length;
  const pending = mockInvoices.filter(i => i.status === 'PENDING').length;
  const approved = mockInvoices.filter(i => i.status === 'APPROVED').length;
  const rejected = mockInvoices.filter(i => i.status === 'REJECTED').length;
  const processing = mockInvoices.filter(i => i.status === 'PROCESSING').length;
  const errors = mockInvoices.filter(i => i.status === 'ERROR').length;

  const avgConfidence = mockInvoices.reduce((sum, inv) => sum + inv.ocr_confidence, 0) / totalInvoices;

  const totalByCurrency = mockInvoices.reduce((acc, inv) => {
    if (inv.status === 'APPROVED') {
      acc[inv.currency] = (acc[inv.currency] || 0) + inv.total;
    }
    return acc;
  }, {} as Record<string, number>);

  const recentInvoices = [...mockInvoices]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Panel Principal</h1>
        <p className="text-gray-600">Resumen general del sistema de facturas</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<FileText className="w-6 h-6 text-blue-600" />}
          label="Total Facturas"
          value={totalInvoices.toString()}
          bgColor="bg-blue-50"
        />
        <StatCard
          icon={<Clock className="w-6 h-6 text-yellow-600" />}
          label="Pendientes"
          value={pending.toString()}
          bgColor="bg-yellow-50"
          onClick={() => navigateTo('invoices')}
          clickable
        />
        <StatCard
          icon={<CheckCircle className="w-6 h-6 text-green-600" />}
          label="Aprobadas"
          value={approved.toString()}
          bgColor="bg-green-50"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6 text-purple-600" />}
          label="Confianza OCR"
          value={`${(avgConfidence * 100).toFixed(1)}%`}
          bgColor="bg-purple-50"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-orange-50 rounded-lg">
              <Clock className="w-5 h-5 text-orange-600" />
            </div>
            <span className="text-gray-700">Procesando</span>
          </div>
          <p className="text-gray-900">{processing}</p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-red-50 rounded-lg">
              <XCircle className="w-5 h-5 text-red-600" />
            </div>
            <span className="text-gray-700">Rechazadas</span>
          </div>
          <p className="text-gray-900">{rejected}</p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-gray-50 rounded-lg">
              <AlertCircle className="w-5 h-5 text-gray-600" />
            </div>
            <span className="text-gray-700">Errores</span>
          </div>
          <p className="text-gray-900">{errors}</p>
        </div>
      </div>

      {/* Totales por Moneda */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <DollarSign className="w-6 h-6 text-green-600" />
          <h2 className="text-gray-900">Totales Aprobados por Moneda</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(totalByCurrency).map(([currency, total]) => (
            <div key={currency} className="p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-sm mb-1">{currency}</p>
              <p className="text-gray-900">{total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Invoices */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-gray-900">Facturas Recientes</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-gray-700">Serie</th>
                <th className="px-6 py-3 text-left text-gray-700">Emisor</th>
                <th className="px-6 py-3 text-left text-gray-700">Fecha</th>
                <th className="px-6 py-3 text-left text-gray-700">Total</th>
                <th className="px-6 py-3 text-left text-gray-700">Estado</th>
                <th className="px-6 py-3 text-left text-gray-700">Confianza</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {recentInvoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => navigateTo('invoices')}>
                  <td className="px-6 py-4 text-gray-900">{invoice.series}</td>
                  <td className="px-6 py-4 text-gray-700">{invoice.issuer_name}</td>
                  <td className="px-6 py-4 text-gray-700">
                    {new Date(invoice.issue_date).toLocaleDateString('es-ES')}
                  </td>
                  <td className="px-6 py-4 text-gray-900">
                    {invoice.currency} {invoice.total.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={invoice.status} />
                  </td>
                  <td className="px-6 py-4">
                    <ConfidenceBadge confidence={invoice.ocr_confidence} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={() => navigateTo('invoices')}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            Ver todas las facturas →
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <button
          onClick={() => navigateTo('upload')}
          className="p-6 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-4"
        >
          <Upload className="w-8 h-8" />
          <div className="text-left">
            <p className="font-medium">Cargar Nuevas Facturas</p>
            <p className="text-blue-100 text-sm">Procesar PDFs e imágenes con OCR</p>
          </div>
        </button>

        <button
          onClick={() => navigateTo('analytics')}
          className="p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors flex items-center gap-4"
        >
          <TrendingUp className="w-8 h-8 text-gray-700" />
          <div className="text-left">
            <p className="text-gray-900 font-medium">Ver Analytics</p>
            <p className="text-gray-600 text-sm">Reportes y estadísticas detalladas</p>
          </div>
        </button>
      </div>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  bgColor: string;
  onClick?: () => void;
  clickable?: boolean;
}

function StatCard({ icon, label, value, bgColor, onClick, clickable }: StatCardProps) {
  const Component = clickable ? 'button' : 'div';
  
  return (
    <Component
      onClick={onClick}
      className={`p-6 bg-white rounded-lg border border-gray-200 ${clickable ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
    >
      <div className="flex items-center gap-4">
        <div className={`p-3 ${bgColor} rounded-lg`}>
          {icon}
        </div>
        <div>
          <p className="text-gray-600 text-sm mb-1">{label}</p>
          <p className="text-gray-900">{value}</p>
        </div>
      </div>
    </Component>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    PROCESSING: 'bg-blue-100 text-blue-800',
    COMPLETED: 'bg-purple-100 text-purple-800',
    APPROVED: 'bg-green-100 text-green-800',
    REJECTED: 'bg-red-100 text-red-800',
    ERROR: 'bg-gray-100 text-gray-800'
  };

  const labels = {
    PENDING: 'Pendiente',
    PROCESSING: 'Procesando',
    COMPLETED: 'Completada',
    APPROVED: 'Aprobada',
    REJECTED: 'Rechazada',
    ERROR: 'Error'
  };

  return (
    <span className={`px-2 py-1 rounded text-xs ${styles[status as keyof typeof styles]}`}>
      {labels[status as keyof typeof labels]}
    </span>
  );
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const percent = confidence * 100;
  let color = 'bg-red-100 text-red-800';
  
  if (percent >= 90) color = 'bg-green-100 text-green-800';
  else if (percent >= 70) color = 'bg-yellow-100 text-yellow-800';
  
  return (
    <span className={`px-2 py-1 rounded text-xs ${color}`}>
      {percent.toFixed(0)}%
    </span>
  );
}