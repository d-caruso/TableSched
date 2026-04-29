import { useTranslation } from 'react-i18next';
import { Pressable, Text, View } from 'react-native';

type PartySizeSelectorProps = {
  label?: string;
  value: number;
  onChange: (value: number) => void;
};

export function PartySizeSelector({ label, value, onChange }: PartySizeSelectorProps) {
  const { t } = useTranslation();
  const resolvedLabel = label ?? t('booking.form.partySize');

  return (
    <View accessibilityLabel={resolvedLabel}>
      <Text>{resolvedLabel}</Text>
      <View style={{ flexDirection: 'row', gap: 12 }}>
        <Pressable
          accessibilityRole="button"
          onPress={() => {
            if (value > 1) {
              onChange(value - 1);
            }
          }}
        >
          <Text>{t('common.decrement')}</Text>
        </Pressable>
        <Text>{value}</Text>
        <Pressable accessibilityRole="button" onPress={() => onChange(value + 1)}>
          <Text>{t('common.increment')}</Text>
        </Pressable>
      </View>
    </View>
  );
}
