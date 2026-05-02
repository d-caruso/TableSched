import { useTranslation } from 'react-i18next';
import { Stack, Text, XStack } from 'tamagui';
import '@/lib/i18n';

export type TimeSlotItem = {
  time: string;
  available: boolean;
  busy_warning?: boolean;
};

type TimeSlotGridProps = {
  slots: TimeSlotItem[];
  loading: boolean;
  selected: string;
  onSelect: (time: string) => void;
};

export function TimeSlotGrid({ slots, loading, selected, onSelect }: TimeSlotGridProps) {
  const { t } = useTranslation();

  if (loading) {
    return (
      <Stack>
        <Text>{t('common.loading')}</Text>
      </Stack>
    );
  }

  return (
    <XStack flexWrap="wrap" gap="$2">
      {slots.map((slot) =>
        slot.available ? (
          <Stack
            key={slot.time}
            accessibilityRole="button"
            onPress={() => onSelect(slot.time)}
            pressStyle={{ opacity: 0.7 }}
          >
            <Text>{slot.time}</Text>
            {slot.busy_warning ? <Text>{t('booking.timeSlots.busyWarning')}</Text> : null}
            {selected === slot.time ? <Text>{t('common.selected')}</Text> : null}
          </Stack>
        ) : (
          <Stack key={slot.time}>
            <Text>{slot.time}</Text>
            {slot.busy_warning ? <Text>{t('booking.timeSlots.busyWarning')}</Text> : null}
          </Stack>
        ),
      )}
    </XStack>
  );
}
