import { useMemo } from 'react';
import { Text, XStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import type { BookingStatus } from '@/lib/api/types';

const statusStyles: Record<BookingStatus, { backgroundColor: string; color: string }> = {
  pending_review: { backgroundColor: '$warning', color: '$background' },
  pending_payment: { backgroundColor: '$brand', color: '$background' },
  confirmed: { backgroundColor: '$success', color: '$background' },
  confirmed_without_deposit: { backgroundColor: '$success', color: '$background' },
  declined: { backgroundColor: '$danger', color: '$background' },
  cancelled_by_customer: { backgroundColor: '$color8', color: '$background' },
  authorization_expired: { backgroundColor: '$color9', color: '$background' },
};

const statusKeys: Record<BookingStatus, string> = {
  pending_review: 'booking.status.pending_review',
  pending_payment: 'booking.status.pending_payment',
  confirmed: 'booking.status.confirmed',
  confirmed_without_deposit: 'booking.status.confirmed_without_deposit',
  declined: 'booking.status.declined',
  cancelled_by_customer: 'booking.status.cancelled_by_customer',
  authorization_expired: 'booking.status.authorization_expired',
};

type StatusBadgeProps = {
  status: BookingStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const { t } = useTranslation();
  const styles = useMemo(() => statusStyles[status], [status]);

  return (
    <XStack
      alignSelf="flex-start"
      backgroundColor={styles.backgroundColor}
      borderRadius="$10"
      paddingHorizontal="$3"
      paddingVertical="$2"
    >
      <Text color={styles.color} fontSize="$2" fontWeight="$6">
        {t(statusKeys[status])}
      </Text>
    </XStack>
  );
}
