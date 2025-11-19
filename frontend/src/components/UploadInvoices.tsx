import { useState } from 'react';
import { View } from '../App';
import { Upload, X, FileText, Image, CheckCircle, AlertCircle, Settings, Loader2 } from 'lucide-react';
import { OcrEngine } from '../types/invoice';
import { useInvoiceStore } from '../store/invoiceStore';
import { useTaskPolling } from '../hooks/useTaskPolling';
import { toast } from 'sonner';

interface UploadInvoicesProps {
  navigateTo: (view: View, invoiceId?: string) => void;
}

interface UploadFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'success' | 'error';
  progress: number;
  error?: string;
  invoiceId?: number;
  taskId?: string;
}

export function UploadInvoices({ navigateTo }: UploadInvoicesProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [ocrEngine, setOcrEngine] = useState<OcrEngine>('Donut'); // Donut por defecto
  const [useGpu, setUseGpu] = useState(true); // GPU activado por defecto para Donut
  const [autoApprove, setAutoApprove] = useState(false);
  const [confidenceThreshold, setConfidenceThreshold] = useState(75); // 75% por defecto
  const [showAdvanced, setShowAdvanced] = useState(false);

  const store = useInvoiceStore();

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
        toast.error(`Archivo no válido: ${file.name}. Solo se permiten PDF, PNG y JPG.`);
        return;
      }

      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error(`Archivo demasiado grande: ${file.name}. Tamaño máximo: 10MB.`);
        return;
      }

      validFiles.push({
        id: Math.random().toString(36).substr(2, 9),
        file,
        status: 'pending',
        progress: 0
      });
    });

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles]);
      toast.success(`${validFiles.length} archivo(s) agregado(s)`);
    }
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const processFiles = async () => {
    for (const uploadFile of files) {
      if (uploadFile.status !== 'pending') continue;

      try {
        // 1. Upload archivo
        setFiles(prev => prev.map(f =>
          f.id === uploadFile.id ? { ...f, status: 'uploading' as const } : f
        ));

        const uploadResult = await store.uploadInvoice(
          uploadFile.file,
          'admin@invokox.com', // TODO: Obtener de usuario logueado
          (progress) => {
            setFiles(prev => prev.map(f =>
              f.id === uploadFile.id ? { ...f, progress } : f
            ));
          }
        );

        console.log('Upload result:', uploadResult);

        // 2. Procesar con OCR
        setFiles(prev => prev.map(f =>
          f.id === uploadFile.id ? {
            ...f,
            status: 'processing' as const,
            invoiceId: uploadResult.invoice_id,
            progress: 100
          } : f
        ));

        const ocrResult = await store.processOCR(
          uploadResult.invoice_id.toString(),
          ocrEngine.toLowerCase(),
          useGpu
        );

        console.log('OCR result:', ocrResult);

        // 3. Monitorear tarea si es async
        if (ocrResult.task_id) {
          // Actualizar con task_id
          setFiles(prev => prev.map(f =>
            f.id === uploadFile.id ? { ...f, taskId: ocrResult.task_id } : f
          ));

          // TODO: Implementar polling real aquí si es necesario
          // Por ahora el backend ejecuta sincrónicamente
        }

        // 4. Verificar resultado
        const confidence = ocrResult.confidence || ocrResult.result?.confidence || 0;

        if (ocrResult.status === 'COMPLETED' && confidence >= confidenceThreshold) {
          // Éxito
          setFiles(prev => prev.map(f =>
            f.id === uploadFile.id ? { ...f, status: 'success' as const } : f
          ));

          toast.success(`${uploadFile.file.name} procesado exitosamente (${Math.round(confidence * 100)}% confianza)`);

          // Auto-aprobar si está habilitado
          if (autoApprove && uploadResult.invoice_id) {
            try {
              await store.approveInvoice(
                uploadResult.invoice_id.toString(),
                'admin@invokox.com'
              );
              toast.success('Factura auto-aprobada');
            } catch (error) {
              console.error('Error auto-aprobando:', error);
            }
          }
        } else if (ocrResult.status === 'REVIEW_NEEDED') {
          // Requiere revisión manual
          setFiles(prev => prev.map(f =>
            f.id === uploadFile.id ? {
              ...f,
              status: 'success' as const,
              error: `Confianza baja (${Math.round(confidence * 100)}%). Requiere revisión.`
            } : f
          ));

          toast.warning(`${uploadFile.file.name} requiere revisión manual`);
        } else {
          // Error
          throw new Error(ocrResult.message || 'Error en procesamiento OCR');
        }

      } catch (error: any) {
        console.error('Error procesando archivo:', error);

        setFiles(prev => prev.map(f =>
          f.id === uploadFile.id ? {
            ...f,
            status: 'error' as const,
            error: error.message || 'Error desconocido'
          } : f
        ));

        toast.error(`Error: ${error.message || 'Error al procesar archivo'}`);
      }
    }

    // Al finalizar todo, recargar la lista
    await store.loadInvoices();
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-8 h-8" />;
    }
    return <FileText className="w-8 h-8" />;
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'uploading':
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return null;
    }
  };

  const getStatusText = (uploadFile: UploadFile) => {
    switch (uploadFile.status) {
      case 'pending':
        return 'Pendiente';
      case 'uploading':
        return `Subiendo... ${uploadFile.progress}%`;
      case 'processing':
        return `Procesando con ${ocrEngine}...`;
      case 'success':
        return uploadFile.error || 'Completado';
      case 'error':
        return uploadFile.error || 'Error';
    }
  };

  const pendingCount = files.filter(f => f.status === 'pending').length;
  const processingCount = files.filter(f => ['uploading', 'processing'].includes(f.status)).length;
  const successCount = files.filter(f => f.status === 'success').length;
  const errorCount = files.filter(f => f.status === 'error').length;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Subir Facturas</h1>
        <p className="text-gray-600">
          Arrastra archivos o haz clic para seleccionar. Las facturas se procesarán automáticamente con OCR.
        </p>
      </div>

      {/* Configuración de OCR */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Configuración de Procesamiento</h2>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
          >
            <Settings className="w-4 h-4" />
            {showAdvanced ? 'Ocultar opciones' : 'Opciones avanzadas'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Motor de OCR
            </label>
            <select
              value={ocrEngine}
              onChange={(e) => setOcrEngine(e.target.value as OcrEngine)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="Donut">Donut (Deep Learning) ⭐ Recomendado</option>
              <option value="PaddleOCR">PaddleOCR (Rápido)</option>
              <option value="Docling">Docling (Layout Analysis)</option>
              <option value="Tesseract">Tesseract (Tradicional)</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {ocrEngine === 'Donut' && 'Vision Transformer para facturas latinoamericanas'}
              {ocrEngine === 'PaddleOCR' && 'OCR rápido y preciso'}
              {ocrEngine === 'Docling' && 'Análisis avanzado de layout'}
              {ocrEngine === 'Tesseract' && 'OCR clásico de Google'}
            </p>
          </div>

          {ocrEngine === 'Donut' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Aceleración GPU
              </label>
              <div className="flex items-center gap-3 h-10">
                <input
                  type="checkbox"
                  checked={useGpu}
                  onChange={(e) => setUseGpu(e.target.checked)}
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-700">
                  Usar GPU (más rápido)
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Recomendado para Donut: ~2-3 seg/factura
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Umbral de Confianza
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min="50"
                max="100"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                className="flex-1"
              />
              <span className="text-sm font-medium text-gray-900 w-12">
                {confidenceThreshold}%
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              ≥{confidenceThreshold}%: Auto-completar | &lt;{confidenceThreshold}%: Revisar
            </p>
          </div>
        </div>

        {showAdvanced && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={autoApprove}
                onChange={(e) => setAutoApprove(e.target.checked)}
                className="w-4 h-4"
              />
              <div>
                <span className="text-sm font-medium text-gray-700">
                  Auto-aprobar facturas con alta confianza
                </span>
                <p className="text-xs text-gray-500">
                  Aprobar automáticamente facturas procesadas con ≥{confidenceThreshold}% de confianza
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
        `}
      >
        <Upload className={`w-16 h-16 mx-auto mb-4 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} />
        <p className="text-lg font-medium text-gray-900 mb-2">
          Arrastra archivos aquí o haz clic para seleccionar
        </p>
        <p className="text-sm text-gray-600 mb-4">
          Formatos soportados: PDF, PNG, JPG (máximo 10MB por archivo)
        </p>
        <input
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileSelect}
          className="hidden"
          id="file-input"
        />
        <label
          htmlFor="file-input"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 cursor-pointer"
        >
          Seleccionar archivos
        </label>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Archivos ({files.length})
            </h3>
            <div className="flex gap-4 text-sm">
              {pendingCount > 0 && (
                <span className="text-gray-600">Pendientes: {pendingCount}</span>
              )}
              {processingCount > 0 && (
                <span className="text-blue-600">Procesando: {processingCount}</span>
              )}
              {successCount > 0 && (
                <span className="text-green-600">Exitosos: {successCount}</span>
              )}
              {errorCount > 0 && (
                <span className="text-red-600">Errores: {errorCount}</span>
              )}
            </div>
          </div>

          <div className="space-y-3">
            {files.map((uploadFile) => (
              <div
                key={uploadFile.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
              >
                <div className="flex items-center gap-4">
                  <div className="text-gray-400">
                    {getFileIcon(uploadFile.file)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {uploadFile.file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-sm text-gray-700">
                        {getStatusText(uploadFile)}
                      </p>
                      {uploadFile.invoiceId && (
                        <p className="text-xs text-gray-500">
                          ID: {uploadFile.invoiceId}
                        </p>
                      )}
                    </div>

                    {getStatusIcon(uploadFile.status)}

                    {uploadFile.status === 'pending' && (
                      <button
                        onClick={() => removeFile(uploadFile.id)}
                        className="p-1 text-gray-400 hover:text-red-500"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Progress bar */}
                {(uploadFile.status === 'uploading' || uploadFile.status === 'processing') && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${uploadFile.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-6 flex gap-3">
            <button
              onClick={processFiles}
              disabled={pendingCount === 0 || processingCount > 0}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Procesar {pendingCount} archivo(s)
            </button>

            <button
              onClick={() => setFiles([])}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Limpiar lista
            </button>

            {successCount > 0 && (
              <button
                onClick={() => navigateTo('invoices')}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 ml-auto"
              >
                Ver facturas procesadas →
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
