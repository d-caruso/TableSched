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
  return [...hours].sort((a, b) => a.weekday - b.weekday);
}

function updateHours(hours: OpeningHour[], weekday: number, patch: Partial<OpeningHour>) {
  const existing = hours.find(hour => hour.weekday === weekday);

  if (!existing) {
    return sortHours([
      ...hours,
      {
        weekday,
        opens_at: patch.opens_at ?? '09:00',
        closes_at: patch.closes_at ?? '22:00',
      },
    ]);
  }

  return sortHours(hours.map(hour => (hour.weekday === weekday ? { ...hour, ...patch } : hour)));
}

export function OpeningHoursEditor({ hours = [], onChange }: Props) {
  const { t } = useTranslation();

  return (
    <View>
      <Text>{t('staff.settings.openingHours')}</Text>
      {DAYS.map(day => {
        const entry = hours.find(hour => hour.weekday === day);
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
                  onChange(hours.filter(hour => hour.weekday !== day));
                  return;
                }

                if (entry) {
                  onChange(hours);
                  return;
                }

                onChange(updateHours(hours, day, { opens_at: '09:00', closes_at: '22:00' }));
              }}
            />
            {entry ? (
              <View>
                <AppInput
                  label={t('staff.settings.open')}
                  value={entry.opens_at}
                  onChangeText={value => onChange(updateHours(hours, day, { opens_at: value }))}
                />
                <AppInput
                  label={t('staff.settings.close')}
                  value={entry.closes_at}
                  onChangeText={value => onChange(updateHours(hours, day, { closes_at: value }))}
                />
              </View>
            ) : null}
          </View>
        );
      })}
    </View>
  );
}
