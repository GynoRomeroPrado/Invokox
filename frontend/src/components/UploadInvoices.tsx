import { useState } from 'react';
import { View } from '../App';
import { Upload, X, FileText, Image, CheckCircle, AlertCircle, Settings } from 'lucide-react';
import { OcrEngine } from '../types/invoice';

interface UploadInvoicesProps {
  navigateTo: (view: View) => void;
}

interface UploadFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'success' | 'error';
  progress: number;
  error?: string;
}

export function UploadInvoices({ navigateTo }: UploadInvoicesProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [ocrEngine, setOcrEngine] = useState<OcrEngine>('PaddleOCR');
  const [autoApprove, setAutoApprove] = useState(false);
  const [confidenceThreshold, setConfidenceThreshold] = useState(90);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = (newFiles: File[]) => {
    const validFiles: UploadFile[] = [];
    
    newFiles.forEach(file => {
      // Validate file type
      const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
      if (!validTypes.includes(file.type)) {
        alert(`Archivo no válido: ${file.name}. Solo se permiten PDF, PNG y JPG.`);
        return;
      }

      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        alert(`Archivo demasiado grande: ${file.name}. Tamaño máximo: 10MB.`);
        return;
      }

      validFiles.push({
        id: Math.random().toString(36).substr(2, 9),
        file,
        status: 'pending',
        progress: 0
      });
    });

    setFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const processFiles = async () => {
    for (const uploadFile of files) {
      if (uploadFile.status !== 'pending') continue;

      // Update to uploading
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? { ...f, status: 'uploading' as const } : f
      ));

      // Simulate upload progress
      for (let i = 0; i <= 100; i += 20) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setFiles(prev => prev.map(f => 
          f.id === uploadFile.id ? { ...f, progress: i } : f
        ));
      }

      // Update to processing
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? { ...f, status: 'processing' as const } : f
      ));

      // Simulate OCR processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Random success/error
      const success = Math.random() > 0.2;
      
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? {
          ...f,
          status: success ? 'success' as const : 'error' as const,
          progress: 100,
          error: success ? undefined : 'Error al procesar el archivo con OCR'
        } : f
      ));
    }
  };

  const hasFiles = files.length > 0;
  const hasPendingFiles = files.some(f => f.status === 'pending');
  const isProcessing = files.some(f => f.status === 'uploading' || f.status === 'processing');
  const successCount = files.filter(f => f.status === 'success').length;
  const errorCount = files.filter(f => f.status === 'error').length;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Cargar Facturas</h1>
        <p className="text-gray-600">Sube archivos PDF o imágenes para procesamiento OCR</p>
      </div>

      {/* Advanced Options Toggle */}
      <div className="mb-6">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700"
        >
          <Settings className="w-4 h-4" />
          <span>{showAdvanced ? 'Ocultar' : 'Mostrar'} opciones avanzadas</span>
        </button>
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="bg-white p-6 rounded-lg border border-gray-200 mb-6">
          <h3 className="text-gray-900 mb-4">Opciones Avanzadas</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-gray-700 mb-2">Motor OCR</label>
              <select
                value={ocrEngine}
                onChange={(e) => setOcrEngine(e.target.value as OcrEngine)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="PaddleOCR">PaddleOCR (Recomendado)</option>
                <option value="Docling">Docling</option>
                <option value="Tesseract">Tesseract</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 mb-2">
                Umbral de Confianza: {confidenceThreshold}%
              </label>
              <input
                type="range"
                min="50"
                max="100"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                className="w-full"
                disabled={!autoApprove}
              />
            </div>

            <div>
              <label className="flex items-center gap-2 mt-8">
                <input
                  type="checkbox"
                  checked={autoApprove}
                  onChange={(e) => setAutoApprove(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700">Auto-aprobar por umbral</span>
              </label>
            </div>
          </div>

          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm">
              <strong>Motor seleccionado:</strong> {ocrEngine}
              {autoApprove && (
                <> • Las facturas con confianza ≥ {confidenceThreshold}% se aprobarán automáticamente</>
              )}
            </p>
          </div>
        </div>
      )}

      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-white hover:border-gray-400'
        }`}
      >
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
          <Upload className="w-8 h-8 text-blue-600" />
        </div>
        <h3 className="text-gray-900 mb-2">Arrastra archivos aquí</h3>
        <p className="text-gray-600 mb-4">o haz clic para seleccionar</p>
        <input
          type="file"
          id="file-input"
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileSelect}
          className="hidden"
        />
        <label
          htmlFor="file-input"
          className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
        >
          Seleccionar Archivos
        </label>
        <p className="text-gray-500 text-sm mt-4">
          Formatos aceptados: PDF, PNG, JPG • Tamaño máximo: 10MB
        </p>
      </div>

      {/* File List */}
      {hasFiles && (
        <div className="mt-6 bg-white rounded-lg border border-gray-200">
          <div className="p-6 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h3 className="text-gray-900">Archivos ({files.length})</h3>
              {successCount > 0 && (
                <p className="text-green-600 text-sm mt-1">
                  {successCount} procesado{successCount !== 1 ? 's' : ''} exitosamente
                </p>
              )}
              {errorCount > 0 && (
                <p className="text-red-600 text-sm mt-1">
                  {errorCount} con error{errorCount !== 1 ? 'es' : ''}
                </p>
              )}
            </div>
            <div className="flex gap-3">
              {!isProcessing && hasPendingFiles && (
                <button
                  onClick={processFiles}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Procesar Archivos
                </button>
              )}
              {successCount > 0 && (
                <button
                  onClick={() => navigateTo('invoices')}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Ver Facturas
                </button>
              )}
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {files.map((uploadFile) => (
              <FileItem
                key={uploadFile.id}
                uploadFile={uploadFile}
                onRemove={removeFile}
              />
            ))}
          </div>
        </div>
      )}

      {/* Help */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-gray-900 mb-2">Consejos para mejores resultados:</h4>
        <ul className="text-gray-700 text-sm space-y-1">
          <li>• Asegúrate de que las imágenes sean claras y legibles</li>
          <li>• Evita archivos con baja resolución o mal escaneados</li>
          <li>• Los PDFs con texto incrustado se procesan más rápido</li>
          <li>• Puedes cargar múltiples archivos a la vez</li>
        </ul>
      </div>
    </div>
  );
}

interface FileItemProps {
  uploadFile: UploadFile;
  onRemove: (id: string) => void;
}

function FileItem({ uploadFile, onRemove }: FileItemProps) {
  const { file, status, progress, error } = uploadFile;
  
  const getIcon = () => {
    if (file.type === 'application/pdf') {
      return <FileText className="w-8 h-8 text-red-600" />;
    }
    return <Image className="w-8 h-8 text-blue-600" />;
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Pendiente';
      case 'uploading':
        return 'Subiendo...';
      case 'processing':
        return 'Procesando OCR...';
      case 'success':
        return 'Procesado exitosamente';
      case 'error':
        return error || 'Error al procesar';
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="p-4 hover:bg-gray-50">
      <div className="flex items-center gap-4">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <p className="text-gray-900 truncate">{file.name}</p>
            <div className="flex items-center gap-2">
              {getStatusIcon()}
              {status === 'pending' && (
                <button
                  onClick={() => onRemove(uploadFile.id)}
                  className="p-1 text-gray-400 hover:text-red-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-gray-500 text-sm">{formatSize(file.size)}</span>
            <span className="text-gray-500 text-sm">{file.type.split('/')[1].toUpperCase()}</span>
            <span className={`text-sm ${
              status === 'success' ? 'text-green-600' :
              status === 'error' ? 'text-red-600' :
              'text-blue-600'
            }`}>
              {getStatusText()}
            </span>
          </div>

          {(status === 'uploading' || status === 'processing') && (
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
