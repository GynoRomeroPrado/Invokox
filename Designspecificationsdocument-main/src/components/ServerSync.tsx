import { useState } from 'react';
import { Server, RefreshCw, CheckCircle, AlertCircle, Clock, Upload, Download, Save } from 'lucide-react';

export function ServerSync() {
  const [apiUrl, setApiUrl] = useState('https://api.example.com');
  const [apiKey, setApiKey] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [latency, setLatency] = useState<number | null>(null);
  const [autoSync, setAutoSync] = useState(false);
  const [syncFrequency, setSyncFrequency] = useState(15);
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [uploadCount, setUploadCount] = useState(0);
  const [downloadCount, setDownloadCount] = useState(0);

  const handleTestConnection = async () => {
    setConnectionStatus('testing');
    setLatency(null);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    if (apiUrl && apiKey) {
      setConnectionStatus('success');
      setIsConnected(true);
      setLatency(Math.random() * 200 + 50);
    } else {
      setConnectionStatus('error');
      setIsConnected(false);
    }
  };

  const handleManualSync = () => {
    const now = new Date().toLocaleString('es-ES');
    setLastSync(now);
    setUploadCount(Math.floor(Math.random() * 5));
    setDownloadCount(Math.floor(Math.random() * 3));
    alert('Sincronización completada');
  };

  const handleSave = () => {
    alert('Configuración de servidor guardada');
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Servidor y Sincronización</h1>
        <p className="text-gray-600">Configuración del modo cliente-servidor</p>
      </div>

      <div className="space-y-6">
        {/* Connection Settings */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <Server className="w-5 h-5 text-gray-600" />
            <h2 className="text-gray-900">Conexión al Servidor</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 mb-2">URL de la API</label>
              <input
                type="url"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="https://api.example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-gray-700 mb-2">Clave de API</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="••••••••••••••••"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={handleTestConnection}
              disabled={connectionStatus === 'testing'}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
            >
              {connectionStatus === 'testing' ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Probando conexión...
                </>
              ) : (
                <>
                  <Server className="w-4 h-4" />
                  Probar Conexión
                </>
              )}
            </button>

            {connectionStatus === 'success' && (
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800">
                <CheckCircle className="w-5 h-5" />
                <div>
                  <p>Conexión exitosa</p>
                  {latency && (
                    <p className="text-sm">Latencia: {latency.toFixed(0)}ms</p>
                  )}
                </div>
              </div>
            )}

            {connectionStatus === 'error' && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800">
                <AlertCircle className="w-5 h-5" />
                <p>Error al conectar con el servidor</p>
              </div>
            )}
          </div>
        </div>

        {/* Sync Settings */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <RefreshCw className="w-5 h-5 text-gray-600" />
            <h2 className="text-gray-900">Sincronización</h2>
          </div>

          <div className="space-y-4">
            <label className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 cursor-pointer">
              <div>
                <p className="text-gray-900">Sincronización Automática</p>
                <p className="text-gray-600 text-sm">Sincronizar cambios periódicamente</p>
              </div>
              <input
                type="checkbox"
                checked={autoSync}
                onChange={(e) => setAutoSync(e.target.checked)}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </label>

            {autoSync && (
              <div>
                <label className="block text-gray-700 mb-2">
                  Frecuencia: {syncFrequency} minutos
                </label>
                <input
                  type="range"
                  min="5"
                  max="60"
                  step="5"
                  value={syncFrequency}
                  onChange={(e) => setSyncFrequency(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            )}

            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={handleManualSync}
                disabled={!isConnected}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Sincronizar Ahora
              </button>
            </div>
          </div>
        </div>

        {/* Sync Status */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Estado de Sincronización</h2>

          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-gray-600" />
                <span className="text-gray-600 text-sm">Última Sincronización</span>
              </div>
              <p className="text-gray-900">
                {lastSync || 'Nunca'}
              </p>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Upload className="w-4 h-4 text-blue-600" />
                <span className="text-gray-600 text-sm">Cambios Subidos</span>
              </div>
              <p className="text-gray-900">{uploadCount}</p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Download className="w-4 h-4 text-green-600" />
                <span className="text-gray-600 text-sm">Cambios Descargados</span>
              </div>
              <p className="text-gray-900">{downloadCount}</p>
            </div>
          </div>
        </div>

        {/* Conflict Resolution */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Resolución de Conflictos</h2>

          <div className="space-y-3">
            <label className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="conflict"
                defaultChecked
                className="mt-1 w-4 h-4 text-blue-600"
              />
              <div>
                <p className="text-gray-900">Última escritura gana</p>
                <p className="text-gray-600 text-sm">El cambio más reciente sobrescribe los anteriores</p>
              </div>
            </label>

            <label className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="conflict"
                className="mt-1 w-4 h-4 text-blue-600"
              />
              <div>
                <p className="text-gray-900">Mantener local</p>
                <p className="text-gray-600 text-sm">Priorizar cambios locales sobre el servidor</p>
              </div>
            </label>

            <label className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="conflict"
                className="mt-1 w-4 h-4 text-blue-600"
              />
              <div>
                <p className="text-gray-900">Mantener servidor</p>
                <p className="text-gray-600 text-sm">Priorizar cambios del servidor sobre locales</p>
              </div>
            </label>

            <label className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="conflict"
                className="mt-1 w-4 h-4 text-blue-600"
              />
              <div>
                <p className="text-gray-900">Merge manual</p>
                <p className="text-gray-600 text-sm">Solicitar intervención del usuario</p>
              </div>
            </label>
          </div>
        </div>

        {/* Sync Logs */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-gray-900">Historial de Sincronización</h2>
            <button className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded-lg text-sm">
              Exportar Logs
            </button>
          </div>

          <div className="space-y-2">
            {[
              { time: '18/11/2024 10:30', status: 'success', message: 'Sincronización exitosa: 3 facturas subidas' },
              { time: '18/11/2024 09:15', status: 'success', message: 'Sincronización exitosa: 1 factura descargada' },
              { time: '18/11/2024 08:00', status: 'warning', message: 'Conflicto resuelto en factura F001-00123' },
              { time: '17/11/2024 17:45', status: 'success', message: 'Sincronización exitosa: 5 facturas subidas' }
            ].map((log, index) => (
              <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50">
                <div className={`p-1 rounded ${
                  log.status === 'success' ? 'bg-green-100' :
                  log.status === 'warning' ? 'bg-yellow-100' : 'bg-red-100'
                }`}>
                  {log.status === 'success' && <CheckCircle className="w-4 h-4 text-green-600" />}
                  {log.status === 'warning' && <AlertCircle className="w-4 h-4 text-yellow-600" />}
                </div>
                <div className="flex-1">
                  <p className="text-gray-900 text-sm">{log.message}</p>
                  <p className="text-gray-500 text-xs mt-1">{log.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex gap-4">
          <button
            onClick={handleSave}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
          >
            <Save className="w-5 h-5" />
            Guardar Configuración
          </button>
        </div>
      </div>
    </div>
  );
}
