import { Pressable, Text, View } from 'react-native';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';

type LocaleSelectorProps = {
  value?: string;
  onChange: (value: string) => void;
};

const locales = ['en', 'it', 'de'] as const;

export function LocaleSelector({ value, onChange }: LocaleSelectorProps) {
  const { t } = useTranslation();

  return (
    <View>
      <Text>{t('booking.contact.locale')}</Text>
      <View style={{ flexDirection: 'row', gap: 8 }}>
        {locales.map((locale) => (
          <Pressable key={locale} accessibilityRole="button" onPress={() => onChange(locale)}>
            <Text>{t(`booking.locales.${locale}`)}</Text>
            {value === locale ? <Text>{t('common.selectedIndicator')}</Text> : null}
          </Pressable>
        ))}
      </View>
    </View>
  );
}
