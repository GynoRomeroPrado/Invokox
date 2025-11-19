import { useState } from 'react';
import { Settings, Zap, Key, Languages, Save, TestTube } from 'lucide-react';
import { OcrEngine } from '../types/invoice';

export function OcrSettings() {
  // PaddleOCR settings
  const [paddleModel, setPaddleModel] = useState<'server' | 'mobile'>('server');
  const [paddleGpu, setPaddleGpu] = useState(false);
  const [paddleGpuUsage, setPaddleGpuUsage] = useState(80);
  const [paddleLanguages, setPaddleLanguages] = useState<string[]>(['es', 'en']);
  const [paddleThreshold, setPaddleThreshold] = useState(0.7);
  const [paddlePreprocess, setPaddlePreprocess] = useState(true);

  // Docling settings
  const [doclingApiKey, setDoclingApiKey] = useState('');
  const [doclingRegion, setDoclingRegion] = useState('us-east-1');
  
  // Tesseract settings
  const [tesseractLangs, setTesseractLangs] = useState<string[]>(['spa', 'eng']);
  const [tesseractPsm, setTesseractPsm] = useState(3);
  const [tesseractOem, setTesseractOem] = useState(3);

  const [selectedEngine, setSelectedEngine] = useState<OcrEngine>('PaddleOCR');
  const [testResult, setTestResult] = useState<string | null>(null);

  const handleSave = () => {
    alert('Configuración OCR guardada');
  };

  const handleTest = () => {
    setTestResult('Procesando...');
    setTimeout(() => {
      setTestResult(
        `Motor: ${selectedEngine}\nTexto extraído: Factura F001-00123\nConfianza: 95.2%\nTiempo: 2.3s`
      );
    }, 1500);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Configuración OCR Avanzada</h1>
        <p className="text-gray-600">Ajusta los parámetros de cada motor de reconocimiento</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* PaddleOCR */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Zap className="w-5 h-5 text-blue-600" />
            </div>
            <h2 className="text-gray-900">PaddleOCR</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 text-sm mb-2">Modelo</label>
              <select
                value={paddleModel}
                onChange={(e) => setPaddleModel(e.target.value as 'server' | 'mobile')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              >
                <option value="server">Server (Más preciso)</option>
                <option value="mobile">Mobile (Más rápido)</option>
              </select>
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={paddleGpu}
                  onChange={(e) => setPaddleGpu(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700 text-sm">Usar GPU</span>
              </label>
            </div>

            {paddleGpu && (
              <div>
                <label className="block text-gray-700 text-sm mb-2">
                  Uso de GPU: {paddleGpuUsage}%
                </label>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="10"
                  value={paddleGpuUsage}
                  onChange={(e) => setPaddleGpuUsage(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            )}

            <div>
              <label className="block text-gray-700 text-sm mb-2">Idiomas</label>
              <div className="flex flex-wrap gap-2">
                {['es', 'en', 'pt', 'fr'].map(lang => (
                  <button
                    key={lang}
                    onClick={() => {
                      if (paddleLanguages.includes(lang)) {
                        setPaddleLanguages(paddleLanguages.filter(l => l !== lang));
                      } else {
                        setPaddleLanguages([...paddleLanguages, lang]);
                      }
                    }}
                    className={`px-3 py-1 rounded text-sm ${
                      paddleLanguages.includes(lang)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {lang.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-gray-700 text-sm mb-2">
                Umbral de Confianza: {(paddleThreshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.5"
                max="1"
                step="0.05"
                value={paddleThreshold}
                onChange={(e) => setPaddleThreshold(Number(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={paddlePreprocess}
                  onChange={(e) => setPaddlePreprocess(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700 text-sm">Preprocesamiento de imagen</span>
              </label>
            </div>
          </div>
        </div>

        {/* Docling */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Key className="w-5 h-5 text-purple-600" />
            </div>
            <h2 className="text-gray-900">Docling</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 text-sm mb-2">API Key</label>
              <input
                type="password"
                value={doclingApiKey}
                onChange={(e) => setDoclingApiKey(e.target.value)}
                placeholder="••••••••••••••••"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-gray-700 text-sm mb-2">Región</label>
              <select
                value={doclingRegion}
                onChange={(e) => setDoclingRegion(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
              >
                <option value="us-east-1">US East (Virginia)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-west-1">EU (Ireland)</option>
                <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
              </select>
            </div>

            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="text-purple-800 text-xs">
                Docling es un servicio en la nube. Asegúrate de tener una cuenta activa y créditos disponibles.
              </p>
            </div>
          </div>
        </div>

        {/* Tesseract */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-50 rounded-lg">
              <Languages className="w-5 h-5 text-green-600" />
            </div>
            <h2 className="text-gray-900">Tesseract</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 text-sm mb-2">Idiomas Instalados</label>
              <div className="flex flex-wrap gap-2">
                {['spa', 'eng', 'por', 'fra'].map(lang => (
                  <button
                    key={lang}
                    onClick={() => {
                      if (tesseractLangs.includes(lang)) {
                        setTesseractLangs(tesseractLangs.filter(l => l !== lang));
                      } else {
                        setTesseractLangs([...tesseractLangs, lang]);
                      }
                    }}
                    className={`px-3 py-1 rounded text-sm ${
                      tesseractLangs.includes(lang)
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {lang.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-gray-700 text-sm mb-2">
                PSM (Page Segmentation Mode): {tesseractPsm}
              </label>
              <select
                value={tesseractPsm}
                onChange={(e) => setTesseractPsm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              >
                <option value="3">3 - Auto (Default)</option>
                <option value="4">4 - Single column</option>
                <option value="6">6 - Single block</option>
                <option value="11">11 - Sparse text</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 text-sm mb-2">
                OEM (OCR Engine Mode): {tesseractOem}
              </label>
              <select
                value={tesseractOem}
                onChange={(e) => setTesseractOem(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
              >
                <option value="0">0 - Legacy</option>
                <option value="1">1 - LSTM only</option>
                <option value="2">2 - Legacy + LSTM</option>
                <option value="3">3 - Default</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Test Section */}
      <div className="mt-8 bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <TestTube className="w-5 h-5 text-gray-600" />
          <h2 className="text-gray-900">Probar Configuración</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-700 mb-2">Motor a Probar</label>
            <select
              value={selectedEngine}
              onChange={(e) => setSelectedEngine(e.target.value as OcrEngine)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="PaddleOCR">PaddleOCR</option>
              <option value="Docling">Docling</option>
              <option value="Tesseract">Tesseract</option>
            </select>
            <button
              onClick={handleTest}
              className="w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Ejecutar Prueba
            </button>
          </div>

          <div>
            <label className="block text-gray-700 mb-2">Resultado</label>
            <div className="p-4 bg-gray-50 rounded-lg min-h-[100px] font-mono text-sm">
              {testResult || 'Selecciona un motor y ejecuta una prueba...'}
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="mt-8 flex gap-4">
        <button
          onClick={handleSave}
          className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
        >
          <Save className="w-5 h-5" />
          Guardar Configuración
        </button>
      </div>
    </div>
  );
}
