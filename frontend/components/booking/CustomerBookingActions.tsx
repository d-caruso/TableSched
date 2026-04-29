import { useTranslation } from 'react-i18next';
import { Button, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import type { Booking, BookingStatus } from '@/lib/api/types';

type CustomerBookingActionsProps = {
  booking: Booking;
  token: string;
  cancelling?: boolean;
  onCancel?: (token: string) => void;
  onModify?: (token: string) => void;
  onPay?: (token: string) => void;
};

const CANCELABLE_STATUSES: BookingStatus[] = [
  'pending_review',
  'pending_payment',
  'confirmed',
  'confirmed_without_deposit',
];

const MODIFIABLE_STATUSES: BookingStatus[] = [
  'pending_review',
  'confirmed',
  'confirmed_without_deposit',
];

const PAYABLE_STATUSES: BookingStatus[] = ['pending_payment'];

export function CustomerBookingActions({
  booking,
  token,
  cancelling = false,
  onCancel,
  onModify,
  onPay,
}: CustomerBookingActionsProps) {
  const { t } = useTranslation();

  return (
    <YStack gap="$3">
      {PAYABLE_STATUSES.includes(booking.status) ? (
        <Button onPress={() => onPay?.(token)}>
          <Text>{t('booking.actions.pay')}</Text>
        </Button>
      ) : null}

      {MODIFIABLE_STATUSES.includes(booking.status) ? (
        <Button onPress={() => onModify?.(token)}>
          <Text>{t('booking.actions.modify')}</Text>
        </Button>
      ) : null}

      {CANCELABLE_STATUSES.includes(booking.status) ? (
        <Button disabled={cancelling} onPress={() => onCancel?.(token)}>
          <Text>{t('booking.actions.cancel')}</Text>
        </Button>
      ) : null}
    </YStack>
  );
}
