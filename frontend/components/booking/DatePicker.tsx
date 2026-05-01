import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Text, TextInput, View } from 'react-native';

type DatePickerProps = {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  minDate?: string;
  maxDays?: number;
};

function toIsoDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

function addDays(date: Date, days: number) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

export function DatePicker({ label, value, onChange, minDate, maxDays = 90 }: DatePickerProps) {
  const { t } = useTranslation();
  const bounds = useMemo(() => {
    const today = new Date();
    return {
      min: minDate ?? toIsoDate(today),
      max: toIsoDate(addDays(today, maxDays)),
    };
  }, [maxDays, minDate]);
  const resolvedLabel = label ?? t('booking.form.date');

  return (
    <View>
      <Text>{resolvedLabel}</Text>
      <TextInput
        accessibilityLabel={resolvedLabel}
        value={value}
        onChangeText={(next) => {
          if (!next) {
            onChange(next);
            return;
          }

          if (next >= bounds.min && next <= bounds.max) {
            onChange(next);
          }
        }}
        placeholder={`${bounds.min} - ${bounds.max}`}
      />
    </View>
  );
}
