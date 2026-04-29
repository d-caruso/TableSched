import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import it from './locales/it.json';
import de from './locales/de.json';

export const supportedLocales = ['en', 'it', 'de'] as const;
export type SupportedLocale = (typeof supportedLocales)[number];

export const resources = {
  en: { translation: en },
  it: { translation: it },
  de: { translation: de },
} as const;

if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
    react: { useSuspense: false },
  });
}

export default i18n;
