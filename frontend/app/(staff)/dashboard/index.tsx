import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery } from '@tanstack/react-query';
import { ScrollView, Spinner, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { BookingCard } from '@/components/staff/BookingCard';
import { FilterTabs } from '@/components/staff/FilterTabs';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { useAuth } from '@/lib/auth/AuthContext';
import { staffApi } from '@/lib/api/endpoints';
import type { BookingStatus } from '@/lib/api/types';

const FILTERS: Array<{ key: string; statuses: BookingStatus[] | null }> = [
  { key: 'all', statuses: null },
  { key: 'pending', statuses: ['pending_review', 'pending_payment', 'authorization_expired'] },
  { key: 'confirmed', statuses: ['confirmed', 'confirmed_without_deposit'] },
  { key: 'declined', statuses: ['declined', 'cancelled_by_customer', 'cancelled_by_staff'] },
];

export default function DashboardScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const [filterIdx, setFilterIdx] = useState(0);

  const { mutate: runMaintenance } = useMutation({
    mutationFn: () => staffApi.triggerOpportunisticMaintenance(tenant!, accessToken!),
  });

  useEffect(() => {
    if (accessToken && tenant) {
      runMaintenance();
    }
  }, [accessToken, tenant, runMaintenance]);

  const activeFilter = FILTERS[filterIdx];
  const params = activeFilter.statuses ? { status: activeFilter.statuses.join(',') } : undefined;

  const { data: bookings, isLoading, error } = useQuery({
    queryKey: ['staff-bookings', tenant, filterIdx],
    queryFn: () => staffApi.listBookings(tenant!, accessToken!, params),
    enabled: Boolean(accessToken && tenant),
    refetchInterval: 60_000,
  });

  return (
    <YStack flex={1}>
      <FilterTabs
        labels={FILTERS.map(filter => t(`staff.dashboard.filters.${filter.key}`))}
        selected={filterIdx}
        onSelect={setFilterIdx}
      />
      <ScrollView>
        <YStack padding="$4" gap="$3">
          {isLoading ? <Spinner /> : null}
          {error ? <ErrorMessage error={error} /> : null}
          {!isLoading && bookings?.length === 0 ? <Text color="$placeholderColor">{t('staff.dashboard.empty')}</Text> : null}
          {bookings?.map(booking => <BookingCard key={booking.id} booking={booking} />)}
        </YStack>
      </ScrollView>
    </YStack>
  );
}
