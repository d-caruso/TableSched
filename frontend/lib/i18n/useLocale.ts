import { useTranslation } from 'react-i18next';
import type { SupportedLocale } from './index';

export function useLocale() {
  const { i18n } = useTranslation();

  return {
    locale: (i18n.resolvedLanguage ?? i18n.language ?? 'en') as SupportedLocale,
    setLocale: (locale: SupportedLocale) => {
      void i18n.changeLanguage(locale);
    },
  };
}
