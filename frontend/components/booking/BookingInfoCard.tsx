import { useTranslation } from 'react-i18next';
import { Text, YStack, XStack } from 'tamagui';
import '@/lib/i18n';
import type { Booking } from '@/lib/api/types';

type BookingInfoCardProps = {
  booking: Booking;
};

function formatMoney(amount: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function BookingInfoCard({ booking }: BookingInfoCardProps) {
  const { t } = useTranslation();

  return (
    <YStack gap="$4">
      <YStack gap="$2">
        <Text fontSize="$5" fontWeight="$7">
          {t('booking.detail.title')}
        </Text>

        <XStack justifyContent="space-between" gap="$4">
          <Text>{t('booking.detail.date')}</Text>
          <Text>{booking.date}</Text>
        </XStack>

        <XStack justifyContent="space-between" gap="$4">
          <Text>{t('booking.detail.time')}</Text>
          <Text>{booking.time}</Text>
        </XStack>

        <XStack justifyContent="space-between" gap="$4">
          <Text>{t('booking.detail.guests')}</Text>
          <Text>{booking.party_size} {t('booking.detail.guests')}</Text>
        </XStack>

        <XStack justifyContent="space-between" gap="$4">
          <Text>{t('booking.detail.table')}</Text>
          <Text>{booking.table?.name ?? t('booking.detail.no_table')}</Text>
        </XStack>

        {booking.payment ? (
          <>
            <XStack justifyContent="space-between" gap="$4">
              <Text>{t('booking.detail.payment')}</Text>
              <Text>{t(`booking.payment_status.${booking.payment.status}`)}</Text>
            </XStack>
            <XStack justifyContent="space-between" gap="$4">
              <Text>{t('booking.detail.amount')}</Text>
              <Text>{formatMoney(booking.payment.amount, booking.payment.currency)}</Text>
            </XStack>
          </>
        ) : null}

        <XStack justifyContent="space-between" gap="$4">
          <Text>{t('booking.detail.notes')}</Text>
          <Text>{booking.notes ?? t('booking.detail.no_notes')}</Text>
        </XStack>
      </YStack>
    </YStack>
  );
}
