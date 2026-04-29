import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import { resources } from '@/lib/i18n/resources';

export const i18n = i18next;

void i18n.use(initReactI18next).init({
  resources,
  lng: 'en',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});
