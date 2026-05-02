import { PRESS_STYLE } from '@/constants/styles';
import { useTranslation } from 'react-i18next';
import { Stack, Text, XStack } from 'tamagui';

type PartySizeSelectorProps = {
  label?: string;
  value: number;
  onChange: (value: number) => void;
};

export function PartySizeSelector({ label, value, onChange }: PartySizeSelectorProps) {
  const { t } = useTranslation();
  const resolvedLabel = label ?? t('booking.form.partySize');

  return (
    <Stack accessibilityLabel={resolvedLabel}>
      <Text>{resolvedLabel}</Text>
      <XStack gap="$3">
        <Stack
          accessibilityRole="button"
          onPress={() => {
            if (value > 1) {
              onChange(value - 1);
            }
          }}
          pressStyle={PRESS_STYLE}
        >
          <Text>{t('common.decrement')}</Text>
        </Stack>
        <Text>{value}</Text>
        <Stack
          accessibilityRole="button"
          onPress={() => onChange(value + 1)}
          pressStyle={PRESS_STYLE}
        >
          <Text>{t('common.increment')}</Text>
        </Stack>
      </XStack>
    </Stack>
  );
}
