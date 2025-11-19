import { useState } from 'react';
import { Globe, Moon, Sun, Monitor, Save } from 'lucide-react';

export function GeneralSettings() {
  const [language, setLanguage] = useState<'es' | 'en'>('es');
  const [theme, setTheme] = useState<'light' | 'dark' | 'auto'>('light');
  const [openOnStartup, setOpenOnStartup] = useState(false);

  const handleSave = () => {
    alert('Configuración guardada');
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-gray-900 mb-2">Configuración General</h1>
        <p className="text-gray-600">Preferencias de idioma, tema y comportamiento</p>
      </div>

      <div className="space-y-6">
        {/* Language */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <Globe className="w-5 h-5 text-gray-600" />
            <h2 className="text-gray-900">Idioma de la Interfaz</h2>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setLanguage('es')}
              className={`p-4 rounded-lg border-2 transition-all ${
                language === 'es'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-blue-300'
              }`}
            >
              <div className="text-left">
                <p className={`mb-1 ${language === 'es' ? 'text-blue-600' : 'text-gray-900'}`}>
                  Español
                </p>
                <p className="text-gray-600 text-sm">Idioma predeterminado</p>
              </div>
            </button>

            <button
              onClick={() => setLanguage('en')}
              className={`p-4 rounded-lg border-2 transition-all ${
                language === 'en'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-blue-300'
              }`}
            >
              <div className="text-left">
                <p className={`mb-1 ${language === 'en' ? 'text-blue-600' : 'text-gray-900'}`}>
                  English
                </p>
                <p className="text-gray-600 text-sm">Secondary language</p>
              </div>
            </button>
          </div>
        </div>

        {/* Theme */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <Monitor className="w-5 h-5 text-gray-600" />
            <h2 className="text-gray-900">Tema de Apariencia</h2>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <button
              onClick={() => setTheme('light')}
              className={`p-4 rounded-lg border-2 transition-all ${
                theme === 'light'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-blue-300'
              }`}
            >
              <Sun className={`w-6 h-6 mx-auto mb-2 ${theme === 'light' ? 'text-blue-600' : 'text-gray-600'}`} />
              <p className={`text-center ${theme === 'light' ? 'text-blue-600' : 'text-gray-900'}`}>
                Claro
              </p>
            </button>

            <button
              onClick={() => setTheme('dark')}
              className={`p-4 rounded-lg border-2 transition-all ${
                theme === 'dark'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-blue-300'
              }`}
            >
              <Moon className={`w-6 h-6 mx-auto mb-2 ${theme === 'dark' ? 'text-blue-600' : 'text-gray-600'}`} />
              <p className={`text-center ${theme === 'dark' ? 'text-blue-600' : 'text-gray-900'}`}>
                Oscuro
              </p>
            </button>

            <button
              onClick={() => setTheme('auto')}
              className={`p-4 rounded-lg border-2 transition-all ${
                theme === 'auto'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-blue-300'
              }`}
            >
              <Monitor className={`w-6 h-6 mx-auto mb-2 ${theme === 'auto' ? 'text-blue-600' : 'text-gray-600'}`} />
              <p className={`text-center ${theme === 'auto' ? 'text-blue-600' : 'text-gray-900'}`}>
                Auto
              </p>
            </button>
          </div>
        </div>

        {/* System Behavior */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h2 className="text-gray-900 mb-4">Comportamiento del Sistema</h2>
          
          <div className="space-y-3">
            <label className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 cursor-pointer">
              <div>
                <p className="text-gray-900">Abrir al iniciar el sistema</p>
                <p className="text-gray-600 text-sm">Iniciar automáticamente con el sistema operativo</p>
              </div>
              <input
                type="checkbox"
                checked={openOnStartup}
                onChange={(e) => setOpenOnStartup(e.target.checked)}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </label>
          </div>
        </div>

        {/* Important Note */}
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
          <h3 className="text-blue-900 mb-2">Nota Importante sobre Monedas</h3>
          <p className="text-blue-800 text-sm">
            Este sistema soporta múltiples monedas. Cada factura mantiene su propia moneda y se muestra explícitamente junto a los montos.
            No existe una "moneda por defecto del sistema" para evitar confusiones o conversiones no deseadas.
          </p>
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
