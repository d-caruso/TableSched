import { useTranslation } from 'react-i18next';
import { Text, XStack, YStack } from 'tamagui';

export type OpeningHour = {
  day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
  opens?: string | null;
  closes?: string | null;
  closed?: boolean;
};

type OpeningHoursListProps = {
  hours: OpeningHour[];
};

export function OpeningHoursList({ hours }: OpeningHoursListProps) {
  const { t } = useTranslation();

  return (
    <YStack gap="$3">
      {hours.map((hour) => (
        <XStack key={hour.day} justifyContent="space-between" gap="$4">
          <Text fontWeight="$6">{t(`booking.weekdays.${hour.day}`)}</Text>
          <Text color="$color10">
            {hour.closed
              ? t('booking.hours.closed')
              : `${hour.opens ?? '--:--'} - ${hour.closes ?? '--:--'}`}
          </Text>
        </XStack>
      ))}
    </YStack>
  );
}

