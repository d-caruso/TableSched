import { Text, XStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import type { BookingStatus } from '@/lib/api/types';

const COLORS: Record<BookingStatus, string> = {
  pending_review: '#c27803',
  pending_payment: '#c27803',
  confirmed: '#057a55',
  confirmed_without_deposit: '#057a55',
  declined: '#e02424',
  cancelled_by_customer: '#6b7280',
  authorization_expired: '#6b7280',
};

export function StatusBadge({ status }: { status: BookingStatus }) {
  const { t } = useTranslation();

  return (
    <XStack
      backgroundColor={`${COLORS[status]}20`}
      paddingHorizontal="$2"
      paddingVertical="$1"
      borderRadius="$2"
      alignSelf="flex-start"
    >
      <Text color={COLORS[status]} fontSize="$2" fontWeight="600">
        {t(`booking.status.${status}`)}
      </Text>
    </XStack>
  );
}
