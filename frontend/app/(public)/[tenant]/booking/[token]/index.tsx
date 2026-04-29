import { useEffect, useState } from 'react';
import { useLocalSearchParams } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Text, YStack } from 'tamagui';
import { BookingInfoCard } from '@/components/booking/BookingInfoCard';
import { CustomerBookingActions } from '@/components/booking/CustomerBookingActions';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { publicApi } from '@/lib/api/endpoints';
import { ApiError } from '@/lib/api/client';
import type { Booking } from '@/lib/api/types';

export default function CustomerBookingDetailPage() {
  const { token } = useLocalSearchParams<{ tenant: string; token: string }>();
  const { t } = useTranslation();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const tokenValue = Array.isArray(token) ? token[0] : token;

  useEffect(() => {
    if (!tokenValue) {
      setError(new ApiError(400, 'INVALID_TOKEN'));
      setIsLoading(false);
      return;
    }

    void (async () => {
      try {
        const data = await publicApi.getBookingByToken(tokenValue);
        setBooking(data);
      } catch (cause) {
        setError(cause instanceof ApiError ? cause : new ApiError(500, 'UNKNOWN_ERROR'));
      } finally {
        setIsLoading(false);
      }
    })();
  }, [tokenValue]);

  if (isLoading) {
    return (
      <YStack padding="$4">
        <Text>{t('common.loading')}</Text>
      </YStack>
    );
  }

  if (error) {
    return (
      <YStack padding="$4">
        <ErrorMessage error={error} />
      </YStack>
    );
  }

  if (!booking) {
    return null;
  }

  return (
    <YStack padding="$4" gap="$6">
      <StatusBadge status={booking.status} />
      <BookingInfoCard booking={booking} />
      <CustomerBookingActions booking={booking} token={tokenValue} />
    </YStack>
  );
}
