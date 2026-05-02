import { PRESS_STYLE } from '@/constants/styles';
import { useTranslation } from 'react-i18next';
import { Stack, Text, XStack } from 'tamagui';
import '@/lib/i18n';

type LocaleSelectorProps = {
  value?: string;
  onChange: (value: string) => void;
};

const locales = ['en', 'it', 'de'] as const;

export function LocaleSelector({ value, onChange }: LocaleSelectorProps) {
  const { t } = useTranslation();

  return (
    <Stack>
      <Text>{t('booking.contact.locale')}</Text>
      <XStack gap="$2">
        {locales.map((locale) => (
          <Stack
            key={locale}
            accessibilityRole="button"
            onPress={() => onChange(locale)}
            pressStyle={PRESS_STYLE}
          >
            <Text>{t(`booking.locales.${locale}`)}</Text>
            {value === locale ? <Text>{t('common.selectedIndicator')}</Text> : null}
          </Stack>
        ))}
      </XStack>
    </Stack>
  );
}
