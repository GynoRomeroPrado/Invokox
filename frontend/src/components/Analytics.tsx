import { useState } from 'react';
import { mockInvoices, mockCompanies } from '../data/mockData';
import { BarChart, Bar, PieChart, Pie, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, DollarSign, FileText, CheckCircle, Download, Calendar } from 'lucide-react';

export function Analytics() {
  const [dateFrom, setDateFrom] = useState('2024-11-01');
  const [dateTo, setDateTo] = useState('2024-11-18');

  // Filter invoices by date
  const filteredInvoices = mockInvoices.filter(inv => {
    const date = inv.issue_date;
    return date >= dateFrom && date <= dateTo;
  });

  // KPIs
  const totalInvoices = filteredInvoices.length;
  const approvedInvoices = filteredInvoices.filter(i => i.status === 'APPROVED').length;
  const avgConfidence = filteredInvoices.reduce((sum, inv) => sum + inv.ocr_confidence, 0) / totalInvoices || 0;

  // Total by currency
  const totalByCurrency = filteredInvoices.reduce((acc, inv) => {
    if (inv.status === 'APPROVED') {
      acc[inv.currency] = (acc[inv.currency] || 0) + inv.total;
    }
    return acc;
  }, {} as Record<string, number>);

  // Status distribution
  const statusData = [
    { name: 'Aprobada', value: filteredInvoices.filter(i => i.status === 'APPROVED').length, color: '#10b981' },
    { name: 'Pendiente', value: filteredInvoices.filter(i => i.status === 'PENDING').length, color: '#f59e0b' },
    { name: 'Procesando', value: filteredInvoices.filter(i => i.status === 'PROCESSING').length, color: '#3b82f6' },
    { name: 'Rechazada', value: filteredInvoices.filter(i => i.status === 'REJECTED').length, color: '#ef4444' },
    { name: 'Error', value: filteredInvoices.filter(i => i.status === 'ERROR').length, color: '#6b7280' }
  ].filter(item => item.value > 0);

  // Top issuers
  const issuerStats = filteredInvoices.reduce((acc, inv) => {
    const key = inv.issuer_name;
    if (!acc[key]) {
      acc[key] = { name: key, count: 0, total: 0 };
    }
    acc[key].count += 1;
    if (inv.status === 'APPROVED') {
      acc[key].total += inv.total;
    }
    return acc;
  }, {} as Record<string, { name: string; count: number; total: number }>);

  const topIssuers = Object.values(issuerStats)
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  // Monthly evolution
  const monthlyData = filteredInvoices.reduce((acc, inv) => {
    const month = inv.issue_date.substring(0, 7); // YYYY-MM
    if (!acc[month]) {
      acc[month] = { month, count: 0, total: 0 };
    }
    acc[month].count += 1;
    if (inv.status === 'APPROVED') {
      acc[month].total += inv.total;
    }
    return acc;
  }, {} as Record<string, { month: string; count: number; total: number }>);

  const monthlyEvolution = Object.values(monthlyData).sort((a, b) => a.month.localeCompare(b.month));

  const handleExport = () => {
    alert('Exportando dashboard...');
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-gray-900 mb-2">Analytics</h1>
            <p className="text-gray-600">Estadísticas y KPIs del sistema</p>
          </div>
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Exportar PDF
          </button>
        </div>

        {/* Date Filters */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-4">
            <Calendar className="w-5 h-5 text-gray-600" />
            <div className="flex items-center gap-4">
              <div>
                <label className="block text-gray-700 text-sm mb-1">Desde</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-gray-700 text-sm mb-1">Hasta</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <KPICard
          icon={<FileText className="w-6 h-6 text-blue-600" />}
          label="Facturas Procesadas"
          value={totalInvoices.toString()}
          bgColor="bg-blue-50"
        />
        <KPICard
          icon={<CheckCircle className="w-6 h-6 text-green-600" />}
          label="Facturas Aprobadas"
          value={approvedInvoices.toString()}
          bgColor="bg-green-50"
        />
        <KPICard
          icon={<TrendingUp className="w-6 h-6 text-purple-600" />}
          label="Confianza OCR Media"
          value={`${(avgConfidence * 100).toFixed(1)}%`}
          bgColor="bg-purple-50"
        />
        <KPICard
          icon={<DollarSign className="w-6 h-6 text-green-600" />}
          label="Monedas Activas"
          value={Object.keys(totalByCurrency).length.toString()}
          bgColor="bg-green-50"
        />
      </div>

      {/* Totals by Currency */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
        <h2 className="text-gray-900 mb-4">Totales Aprobados por Moneda</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(totalByCurrency).map(([currency, total]) => (
            <div key={currency} className="p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-sm mb-1">{currency}</p>
              <p className="text-gray-900">
                {total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Status Distribution */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Distribución por Estado</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Issuers */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Top 5 Emisores</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topIssuers}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#3b82f6" name="Facturas" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Monthly Evolution */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h2 className="text-gray-900 mb-4">Evolución Mensual</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthlyEvolution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="count" stroke="#3b82f6" name="Cantidad" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="total" stroke="#10b981" name="Total Aprobado" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* OCR Engines Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        {['PaddleOCR', 'Docling', 'Tesseract'].map(engine => {
          const engineInvoices = filteredInvoices.filter(i => i.ocr_engine === engine);
          const avgConf = engineInvoices.length > 0
            ? engineInvoices.reduce((sum, inv) => sum + inv.ocr_confidence, 0) / engineInvoices.length
            : 0;
          const avgTime = engineInvoices.length > 0
            ? engineInvoices.reduce((sum, inv) => sum + (inv.processing_time || 0), 0) / engineInvoices.length
            : 0;

          return (
            <div key={engine} className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-gray-900 mb-4">{engine}</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Facturas Procesadas</p>
                  <p className="text-gray-900">{engineInvoices.length}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm mb-1">Confianza Promedio</p>
                  <p className="text-gray-900">{(avgConf * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm mb-1">Tiempo Promedio</p>
                  <p className="text-gray-900">{avgTime.toFixed(2)}s</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface KPICardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  bgColor: string;
}

function KPICard({ icon, label, value, bgColor }: KPICardProps) {
  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center gap-4">
        <div className={`p-3 ${bgColor} rounded-lg`}>
          {icon}
        </div>
        <div>
          <p className="text-gray-600 text-sm mb-1">{label}</p>
          <p className="text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
}
