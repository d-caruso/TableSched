import { PRESS_STYLE } from '@/constants/styles';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Stack, Text, XStack, YStack } from 'tamagui';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ROUTES } from '@/constants/routes';
import type { Booking } from '@/lib/api/types';

export function BookingCard({ booking }: { booking: Booking }) {
  const router = useRouter();
  const { t } = useTranslation();

  return (
    <Stack
      accessibilityRole="button"
      onPress={() => router.push(ROUTES.bookingAdmin(booking.id))}
      pressStyle={PRESS_STYLE}
    >
      <YStack borderWidth={1} borderColor="$borderColor" borderRadius="$4" padding="$3" gap="$2">
        <XStack justifyContent="space-between" alignItems="center" gap="$2">
          <Text fontWeight="600">{booking.customer.name}</Text>
          <StatusBadge status={booking.status} />
        </XStack>
        <Text color="$placeholderColor" fontSize="$3">
          {booking.date} {booking.time} · {booking.party_size} {t('booking.detail.guests')}
        </Text>
      </YStack>
    </Stack>
  );
}
