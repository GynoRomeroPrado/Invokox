import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { translations, Locale, TranslationKeys } from './translations';

interface LanguageContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: TranslationKeys;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const STORAGE_KEY = 'invokox_language';
const DEFAULT_LOCALE: Locale = 'es'; // Español por defecto

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  // Load saved locale from localStorage or use default
  const [locale, setLocaleState] = useState<Locale>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && (saved === 'es' || saved === 'en')) {
      return saved as Locale;
    }
    return DEFAULT_LOCALE;
  });

  // Persist locale changes to localStorage
  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem(STORAGE_KEY, newLocale);
    // Update document language attribute
    document.documentElement.lang = newLocale;
  };

  // Set initial language attribute
  useEffect(() => {
    document.documentElement.lang = locale;
  }, []);

  const value: LanguageContextType = {
    locale,
    setLocale,
    t: translations[locale],
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

/**
 * Hook to access translations and language settings
 *
 * Usage:
 * ```tsx
 * const { t, locale, setLocale } = useLanguage();
 *
 * return (
 *   <div>
 *     <h1>{t.dashboard.title}</h1>
 *     <button onClick={() => setLocale('en')}>English</button>
 *   </div>
 * );
 * ```
 */
export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
