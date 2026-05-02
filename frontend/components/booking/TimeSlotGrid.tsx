import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, Text, View } from 'react-native';

const styles = StyleSheet.create({
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
});
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
      <View>
        <Text>{t('common.loading')}</Text>
      </View>
    );
  }

  return (
    <View style={styles.grid}>
      {slots.map((slot) =>
        slot.available ? (
          <Pressable key={slot.time} accessibilityRole="button" onPress={() => onSelect(slot.time)}>
            <Text>{slot.time}</Text>
            {slot.busy_warning ? <Text>{t('booking.timeSlots.busyWarning')}</Text> : null}
            {selected === slot.time ? <Text>{t('common.selected')}</Text> : null}
          </Pressable>
        ) : (
          <View key={slot.time}>
            <Text>{slot.time}</Text>
            {slot.busy_warning ? <Text>{t('booking.timeSlots.busyWarning')}</Text> : null}
          </View>
        ),
      )}
    </View>
  );
}
