import { useMemo } from 'react';
import { useLocalSearchParams } from 'expo-router';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ScrollView, Spinner, YStack } from 'tamagui';
import '@/lib/i18n';
import { BookingInfoCard } from '@/components/booking/BookingInfoCard';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';
import { useAuth } from '@/lib/auth/AuthContext';
import { staffApi } from '@/lib/api/endpoints';

export default function StaffBookingDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { accessToken, tenant } = useAuth();
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

  if (isLoading) {
    return <Spinner size="large" />;
  }

  if (error || !booking) {
    return <ErrorMessage error={error} />;
  }

  return (
    <ScrollView>
      <YStack width="100%" maxWidth={600} alignSelf="center" padding="$4" gap="$4">
        <StatusBadge status={booking.status} />
        <BookingInfoCard booking={booking} />
        <StaffBookingActions booking={booking} tenant={tenant!} token={accessToken!} onActionComplete={invalidate} />
      </YStack>
    </ScrollView>
  );
}
