import { Pressable, StyleSheet, Text, View } from 'react-native';

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: 8 },
});
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
      <View style={styles.row}>
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
