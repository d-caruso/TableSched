import { useMemo } from 'react';
import { Text, TextInput, View } from 'react-native';

type DatePickerProps = {
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

export function DatePicker({ value, onChange, minDate, maxDays = 90 }: DatePickerProps) {
  const bounds = useMemo(() => {
    const today = new Date();
    return {
      min: minDate ?? toIsoDate(today),
      max: toIsoDate(addDays(today, maxDays)),
    };
  }, [maxDays, minDate]);

  return (
    <View>
      <Text>Date</Text>
      <TextInput
        accessibilityLabel="Date"
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
