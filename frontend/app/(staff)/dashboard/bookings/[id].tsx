import { useMemo } from 'react';
import { useLocalSearchParams } from 'expo-router';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { ScrollView, Spinner, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { BookingInfoCard } from '@/components/booking/BookingInfoCard';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';
import { AppButton } from '@/components/ui/AppButton';
import { useAuth } from '@/lib/auth/AuthContext';
import { staffApi } from '@/lib/api/endpoints';

export default function StaffBookingDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { accessToken, tenant } = useAuth();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const bookingId = useMemo(() => (Array.isArray(id) ? id[0] : id), [id]);

  const { data: booking, isLoading, error } = useQuery({
    queryKey: ['staff-booking', bookingId],
    queryFn: () => staffApi.getBooking(tenant!, accessToken!, bookingId),
    enabled: Boolean(bookingId && accessToken && tenant),
  });

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['staff-booking', bookingId] }),
      queryClient.invalidateQueries({ queryKey: ['staff-bookings'] }),
    ]);
  };

  const refund = useMutation({
    mutationFn: () => staffApi.refundPayment(tenant!, accessToken!, booking!.payment!.id),
    onSuccess: invalidate,
  });

  if (isLoading) {
    return <Spinner size="large" />;
  }

  if (error || !booking) {
    return <ErrorMessage error={error} />;
  }

  const canRefund = booking.payment?.status === 'captured';

  return (
    <ScrollView>
      <YStack width="100%" maxWidth={600} alignSelf="center" padding="$4" gap="$4">
        <StatusBadge status={booking.status} />
        <BookingInfoCard booking={booking} />
        <StaffBookingActions booking={booking} tenant={tenant!} token={accessToken!} onActionComplete={invalidate} />
        {canRefund ? (
          <AppButton variant="secondary" onPress={() => refund.mutate()} loading={refund.isPending}>
            {t('staff.booking.refund')}
          </AppButton>
        ) : null}
      </YStack>
    </ScrollView>
  );
}
