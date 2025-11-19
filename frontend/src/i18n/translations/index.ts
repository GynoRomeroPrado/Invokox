import { es } from './es';
import { en } from './en';

export const translations = {
  es,
  en,
};

export type Locale = keyof typeof translations;
export type TranslationKeys = typeof es;
