import { useState } from 'react';
import { HelpCircle, Book, Keyboard, MessageCircle, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

export function Help() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const faqs = [
    {
      question: '¿Cómo cargo una nueva factura?',
      answer: 'Ve a "Cargar Facturas" en el menú lateral, arrastra tus archivos PDF o imágenes, o haz clic en "Seleccionar Archivos". El sistema procesará automáticamente los documentos usando OCR.'
    },
    {
      question: '¿Qué formatos de archivo son soportados?',
      answer: 'El sistema acepta archivos PDF, PNG, JPG y JPEG con un tamaño máximo de 10MB por archivo. Los PDFs con texto incrustado se procesan más rápido que los escaneados.'
    },
    {
      question: '¿Cómo funcionan los motores OCR?',
      answer: 'Ofrecemos tres motores: PaddleOCR (recomendado, local y rápido), Docling (en la nube, requiere API key) y Tesseract (código abierto). Puedes configurar cada motor en "Configuración OCR".'
    },
    {
      question: '¿Qué significan los niveles de confianza OCR?',
      answer: 'El nivel de confianza indica qué tan seguro está el motor OCR de haber extraído correctamente el texto. 90-100% es excelente, 70-89% es bueno pero requiere revisión, y menos del 70% necesita validación manual.'
    },
    {
      question: '¿Cómo aprobo o rechazo facturas?',
      answer: 'En el "Panel de Facturas", puedes hacer clic en cada factura para validarla. Si los datos son correctos, haz clic en "Aprobar". Si hay errores, puedes editarlos antes de aprobar o rechazar la factura con una nota.'
    },
    {
      question: '¿El sistema soporta múltiples monedas?',
      answer: 'Sí. Cada factura mantiene su propia moneda (USD, PEN, EUR, CLP, MXN, etc.) y se muestra explícitamente junto a los montos. No hay conversión automática.'
    },
    {
      question: '¿Cómo exporto las facturas?',
      answer: 'Ve a "Exportación" en el menú, selecciona el formato deseado (Excel, CSV, PDF, JSON), aplica filtros si necesitas, y haz clic en "Exportar". Puedes incluir el desglose de ítems si lo necesitas.'
    },
    {
      question: '¿Qué hacen los diferentes roles de usuario?',
      answer: 'Admin tiene acceso completo, Operator puede gestionar facturas y aprobarlas/rechazarlas, y Viewer solo puede ver facturas y reportes sin poder modificar nada.'
    }
  ];

  const shortcuts = [
    { key: 'Ctrl + U', action: 'Abrir carga de facturas' },
    { key: 'Ctrl + F', action: 'Buscar en panel de facturas' },
    { key: 'Ctrl + E', action: 'Exportar facturas seleccionadas' },
    { key: 'Esc', action: 'Cerrar modal o diálogo' },
    { key: 'Tab', action: 'Navegar entre campos en formularios' }
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Ayuda y Soporte</h1>
        <p className="text-gray-600">Recursos y documentación del sistema</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Quick Start */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-50 rounded-lg">
              <Book className="w-6 h-6 text-blue-600" />
            </div>
            <h2 className="text-gray-900">Guía Rápida</h2>
          </div>
          <p className="text-gray-700 mb-4 text-sm">
            Aprende los conceptos básicos y empieza a usar el sistema en minutos.
          </p>
          <a
            href="#"
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm"
          >
            Ver tutorial
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>

        {/* Shortcuts */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-50 rounded-lg">
              <Keyboard className="w-6 h-6 text-purple-600" />
            </div>
            <h2 className="text-gray-900">Atajos de Teclado</h2>
          </div>
          <p className="text-gray-700 mb-4 text-sm">
            Aumenta tu productividad con atajos de teclado.
          </p>
          <button
            onClick={() => setOpenFaq(null)}
            className="flex items-center gap-2 text-purple-600 hover:text-purple-700 text-sm"
          >
            Ver atajos
          </button>
        </div>

        {/* Contact */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-green-50 rounded-lg">
              <MessageCircle className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-gray-900">Contactar Soporte</h2>
          </div>
          <p className="text-gray-700 mb-4 text-sm">
            ¿Necesitas ayuda? Nuestro equipo está listo para asistirte.
          </p>
          <a
            href="mailto:soporte@example.com"
            className="flex items-center gap-2 text-green-600 hover:text-green-700 text-sm"
          >
            soporte@example.com
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Keyboard Shortcuts */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Keyboard className="w-5 h-5 text-gray-600" />
          <h2 className="text-gray-900">Atajos de Teclado</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {shortcuts.map((shortcut, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-700">{shortcut.action}</span>
              <kbd className="px-3 py-1 bg-white border border-gray-300 rounded text-sm text-gray-900">
                {shortcut.key}
              </kbd>
            </div>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center gap-3 mb-6">
          <HelpCircle className="w-5 h-5 text-gray-600" />
          <h2 className="text-gray-900">Preguntas Frecuentes</h2>
        </div>
        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setOpenFaq(openFaq === index ? null : index)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 text-left"
              >
                <span className="text-gray-900">{faq.question}</span>
                {openFaq === index ? (
                  <ChevronUp className="w-5 h-5 text-gray-600 flex-shrink-0" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-600 flex-shrink-0" />
                )}
              </button>
              {openFaq === index && (
                <div className="p-4 pt-0 text-gray-700 text-sm">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Quick Start Guide */}
      <div className="mt-8 bg-white p-6 rounded-lg border border-gray-200">
        <h2 className="text-gray-900 mb-4">Flujo Básico de Trabajo</h2>
        <div className="space-y-6">
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
              1
            </div>
            <div>
              <h3 className="text-gray-900 mb-1">Cargar Facturas</h3>
              <p className="text-gray-700 text-sm">
                Sube tus archivos PDF o imágenes. El sistema los procesará automáticamente con OCR.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
              2
            </div>
            <div>
              <h3 className="text-gray-900 mb-1">Validar Extracción</h3>
              <p className="text-gray-700 text-sm">
                Revisa los datos extraídos. Corrige si es necesario. El sistema valida totales automáticamente.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
              3
            </div>
            <div>
              <h3 className="text-gray-900 mb-1">Aprobar o Rechazar</h3>
              <p className="text-gray-700 text-sm">
                Si todo está correcto, aprueba la factura. Si hay problemas, recházala con una nota explicativa.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
              4
            </div>
            <div>
              <h3 className="text-gray-900 mb-1">Exportar y Analizar</h3>
              <p className="text-gray-700 text-sm">
                Exporta tus facturas en Excel, PDF o CSV. Usa Analytics para obtener insights y métricas.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Report Issue */}
      <div className="mt-8 bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
        <h3 className="text-yellow-900 mb-2">Reportar un Problema</h3>
        <p className="text-yellow-800 text-sm mb-4">
          Si encuentras un error o tienes sugerencias de mejora, contáctanos con la siguiente información:
        </p>
        <ul className="list-disc list-inside text-yellow-800 text-sm space-y-1">
          <li>Descripción detallada del problema</li>
          <li>Pasos para reproducirlo</li>
          <li>Capturas de pantalla si es posible</li>
          <li>Navegador y versión del sistema operativo</li>
        </ul>
        <div className="mt-4">
          <a
            href="mailto:soporte@example.com?subject=Reporte de Problema"
            className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
          >
            <MessageCircle className="w-4 h-4" />
            Enviar Reporte
          </a>
        </div>
      </div>

      {/* System Info */}
      <div className="mt-8 bg-gray-50 p-4 rounded-lg text-sm">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-gray-700">
          <div>
            <span className="text-gray-600">Versión:</span> 1.0.0
          </div>
          <div>
            <span className="text-gray-600">Última actualización:</span> 18/11/2024
          </div>
          <div>
            <span className="text-gray-600">Arquitectura:</span> Clean Architecture
          </div>
          <div>
            <span className="text-gray-600">Motores OCR:</span> 3 disponibles
          </div>
        </div>
      </div>
    </div>
  );
}
