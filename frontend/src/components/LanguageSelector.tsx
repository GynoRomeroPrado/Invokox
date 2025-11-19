import { Globe } from 'lucide-react';
import { useLanguage } from '../i18n';

/**
 * Language selector component
 * Shows current language and allows switching between Spanish and English
 */
export function LanguageSelector() {
  const { locale, setLocale } = useLanguage();

  const languages = [
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'en', name: 'English', flag: '🇬🇧' },
  ] as const;

  const currentLanguage = languages.find(lang => lang.code === locale) || languages[0];

  return (
    <div className="relative group">
      <button
        className="flex items-center gap-2 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        title="Cambiar idioma / Change language"
      >
        <Globe className="w-4 h-4" />
        <span className="text-sm font-medium">{currentLanguage.flag} {currentLanguage.name}</span>
      </button>

      {/* Dropdown */}
      <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => setLocale(lang.code)}
            className={`w-full flex items-center gap-3 px-4 py-2 text-left hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg transition-colors ${
              locale === lang.code ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
            }`}
          >
            <span className="text-xl">{lang.flag}</span>
            <span className="text-sm font-medium">{lang.name}</span>
            {locale === lang.code && (
              <span className="ml-auto text-blue-600">✓</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
