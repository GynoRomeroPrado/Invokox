import { useState, useMemo } from 'react';
import { View, UserRole } from '../App';
import { mockInvoices } from '../data/mockData';
import { Invoice, InvoiceStatus, Currency } from '../types/invoice';
import { Search, Filter, Download, Trash2, CheckCircle, XCircle, Eye, Edit, ChevronLeft, ChevronRight } from 'lucide-react';

interface InvoicePanelProps {
  navigateTo: (view: View, invoiceId?: string) => void;
  userRole: UserRole;
}

export function InvoicePanel({ navigateTo, userRole }: InvoicePanelProps) {
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<InvoiceStatus | 'ALL'>('ALL');
  const [currencyFilter, setCurrencyFilter] = useState<Currency | 'ALL'>('ALL');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const filteredInvoices = useMemo(() => {
    return mockInvoices.filter(invoice => {
      const matchesSearch = !searchText || 
        invoice.series.toLowerCase().includes(searchText.toLowerCase()) ||
        invoice.issuer_name.toLowerCase().includes(searchText.toLowerCase()) ||
        invoice.receiver_name.toLowerCase().includes(searchText.toLowerCase());
      
      const matchesStatus = statusFilter === 'ALL' || invoice.status === statusFilter;
      const matchesCurrency = currencyFilter === 'ALL' || invoice.currency === currencyFilter;
      
      const matchesDateFrom = !dateFrom || invoice.issue_date >= dateFrom;
      const matchesDateTo = !dateTo || invoice.issue_date <= dateTo;

      return matchesSearch && matchesStatus && matchesCurrency && matchesDateFrom && matchesDateTo;
    });
  }, [searchText, statusFilter, currencyFilter, dateFrom, dateTo]);

  const totalPages = Math.ceil(filteredInvoices.length / itemsPerPage);
  const paginatedInvoices = filteredInvoices.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const toggleSelection = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === paginatedInvoices.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(paginatedInvoices.map(inv => inv.id)));
    }
  };

  const handleBulkApprove = () => {
    if (userRole === 'viewer') {
      alert('No tienes permisos para aprobar facturas');
      return;
    }
    alert(`Aprobar ${selectedIds.size} facturas seleccionadas`);
    setSelectedIds(new Set());
  };

  const handleBulkReject = () => {
    if (userRole === 'viewer') {
      alert('No tienes permisos para rechazar facturas');
      return;
    }
    alert(`Rechazar ${selectedIds.size} facturas seleccionadas`);
    setSelectedIds(new Set());
  };

  const handleBulkExport = () => {
    alert(`Exportar ${selectedIds.size} facturas seleccionadas`);
  };

  const handleView = (invoice: Invoice) => {
    if (invoice.status === 'APPROVED' || invoice.status === 'REJECTED') {
      navigateTo('view', invoice.id);
    } else {
      navigateTo('validate', invoice.id);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Panel de Facturas</h1>
        <p className="text-gray-600">Gestiona y filtra todas las facturas del sistema</p>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <label className="block text-gray-700 mb-2">Buscar</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Serie, emisor, receptor..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-gray-700 mb-2">Estado</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as InvoiceStatus | 'ALL')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">Todos</option>
              <option value="PENDING">Pendiente</option>
              <option value="PROCESSING">Procesando</option>
              <option value="COMPLETED">Completada</option>
              <option value="APPROVED">Aprobada</option>
              <option value="REJECTED">Rechazada</option>
              <option value="ERROR">Error</option>
            </select>
          </div>

          {/* Currency Filter */}
          <div>
            <label className="block text-gray-700 mb-2">Moneda</label>
            <select
              value={currencyFilter}
              onChange={(e) => setCurrencyFilter(e.target.value as Currency | 'ALL')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">Todas</option>
              <option value="USD">USD</option>
              <option value="PEN">PEN</option>
              <option value="EUR">EUR</option>
              <option value="CLP">CLP</option>
              <option value="MXN">MXN</option>
            </select>
          </div>

          {/* Date From */}
          <div>
            <label className="block text-gray-700 mb-2">Desde</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Date To */}
          <div>
            <label className="block text-gray-700 mb-2">Hasta</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Active filters count */}
        {(searchText || statusFilter !== 'ALL' || currencyFilter !== 'ALL' || dateFrom || dateTo) && (
          <div className="mt-4 flex items-center gap-2">
            <Filter className="w-4 h-4 text-blue-600" />
            <span className="text-sm text-gray-700">
              {filteredInvoices.length} factura{filteredInvoices.length !== 1 ? 's' : ''} encontrada{filteredInvoices.length !== 1 ? 's' : ''}
            </span>
            <button
              onClick={() => {
                setSearchText('');
                setStatusFilter('ALL');
                setCurrencyFilter('ALL');
                setDateFrom('');
                setDateTo('');
              }}
              className="text-sm text-blue-600 hover:text-blue-700 ml-2"
            >
              Limpiar filtros
            </button>
          </div>
        )}
      </div>

      {/* Bulk Actions */}
      {selectedIds.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6 flex items-center justify-between">
          <span className="text-blue-900">
            {selectedIds.size} factura{selectedIds.size !== 1 ? 's' : ''} seleccionada{selectedIds.size !== 1 ? 's' : ''}
          </span>
          <div className="flex gap-3">
            {userRole !== 'viewer' && (
              <>
                <button
                  onClick={handleBulkApprove}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Aprobar
                </button>
                <button
                  onClick={handleBulkReject}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                >
                  <XCircle className="w-4 h-4" />
                  Rechazar
                </button>
              </>
            )}
            <button
              onClick={handleBulkExport}
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Exportar
            </button>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {filteredInvoices.length === 0 ? (
          <div className="p-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-gray-900 mb-2">No se encontraron facturas</h3>
            <p className="text-gray-600 mb-6">
              Intenta ajustar los filtros o{' '}
              <button onClick={() => navigateTo('upload')} className="text-blue-600 hover:text-blue-700">
                cargar nuevas facturas
              </button>
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedIds.size === paginatedInvoices.length && paginatedInvoices.length > 0}
                        onChange={toggleSelectAll}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-gray-700">Serie</th>
                    <th className="px-6 py-3 text-left text-gray-700">Emisor</th>
                    <th className="px-6 py-3 text-left text-gray-700">Receptor</th>
                    <th className="px-6 py-3 text-left text-gray-700">Fecha</th>
                    <th className="px-6 py-3 text-left text-gray-700">Total</th>
                    <th className="px-6 py-3 text-left text-gray-700">Estado</th>
                    <th className="px-6 py-3 text-left text-gray-700">Confianza</th>
                    <th className="px-6 py-3 text-left text-gray-700">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {paginatedInvoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedIds.has(invoice.id)}
                          onChange={() => toggleSelection(invoice.id)}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-6 py-4 text-gray-900">{invoice.series}</td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="text-gray-900">{invoice.issuer_name}</p>
                          <p className="text-gray-500 text-sm">{invoice.issuer_tax_id}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="text-gray-900">{invoice.receiver_name}</p>
                          <p className="text-gray-500 text-sm">{invoice.receiver_tax_id}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-700">
                        {new Date(invoice.issue_date).toLocaleDateString('es-ES')}
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="text-gray-900">{invoice.currency} {invoice.total.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={invoice.status} />
                      </td>
                      <td className="px-6 py-4">
                        <ConfidenceBadge confidence={invoice.ocr_confidence} />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleView(invoice)}
                            className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                            title="Ver"
                          >
                            {invoice.status === 'APPROVED' || invoice.status === 'REJECTED' ? (
                              <Eye className="w-4 h-4" />
                            ) : (
                              <Edit className="w-4 h-4" />
                            )}
                          </button>
                          <button
                            className="p-1 text-gray-600 hover:bg-gray-50 rounded"
                            title="Descargar"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-gray-700 text-sm">
                  Mostrando {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, filteredInvoices.length)} de {filteredInvoices.length} facturas
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="px-4 py-2 text-gray-700">
                    Página {currentPage} de {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: InvoiceStatus }) {
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
    <span className={`px-2 py-1 rounded text-xs ${styles[status]}`}>
      {labels[status]}
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
