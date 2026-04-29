import { Switch, Text, View } from 'react-native';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { AppInput } from '@/components/ui/AppInput';
import type { OpeningHour } from '@/lib/api/types';

type Props = {
  hours: OpeningHour[];
  onChange: (hours: OpeningHour[]) => void;
};

const DAYS = [0, 1, 2, 3, 4, 5, 6] as const;

function sortHours(hours: OpeningHour[]) {
  return [...hours].sort((a, b) => a.day - b.day);
}

function updateHours(hours: OpeningHour[], day: number, patch: Partial<OpeningHour>) {
  const existing = hours.find(hour => hour.day === day);

  if (!existing) {
    return sortHours([
      ...hours,
      {
        day,
        open: patch.open ?? '09:00',
        close: patch.close ?? '22:00',
      },
    ]);
  }

  return sortHours(hours.map(hour => (hour.day === day ? { ...hour, ...patch } : hour)));
}

export function OpeningHoursEditor({ hours, onChange }: Props) {
  const { t } = useTranslation();

  return (
    <View>
      <Text>{t('staff.settings.openingHours')}</Text>
      {DAYS.map(day => {
        const entry = hours.find(hour => hour.day === day);
        const isOpen = Boolean(entry);
        const dayLabel = t(`booking.weekdays.${day}`);

        return (
          <View key={day} accessibilityLabel={dayLabel}>
            <Text>{dayLabel}</Text>
            <Switch
              accessibilityRole="switch"
              value={isOpen}
              onValueChange={next => {
                if (!next) {
                  onChange(hours.filter(hour => hour.day !== day));
                  return;
                }

                if (entry) {
                  onChange(hours);
                  return;
                }

                onChange(updateHours(hours, day, { open: '09:00', close: '22:00' }));
              }}
            />
            {entry ? (
              <View>
                <AppInput
                  label={t('staff.settings.open')}
                  value={entry.open}
                  onChangeText={value => onChange(updateHours(hours, day, { open: value }))}
                />
                <AppInput
                  label={t('staff.settings.close')}
                  value={entry.close}
                  onChangeText={value => onChange(updateHours(hours, day, { close: value }))}
                />
              </View>
            ) : null}
          </View>
        );
      })}
    </View>
  );
}
