import { useEffect, useState } from 'react';
import { useLocalSearchParams } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Text, YStack } from 'tamagui';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { OpeningHoursList, type OpeningHour } from '@/components/booking/OpeningHoursList';
import { RestaurantHeader } from '@/components/booking/RestaurantHeader';
import { publicApi } from '@/lib/api/endpoints';
import type { RestaurantPublicInfo } from '@/lib/api/types';
import { ApiError } from '@/lib/api/client';

type RestaurantInfo = RestaurantPublicInfo & {
  opening_hours?: OpeningHour[];
};

function BookingFormFlow() {
  const { t } = useTranslation();

  return (
    <YStack testID="booking-form-flow" paddingTop="$6">
      <Text fontSize="$5" fontWeight="$6">
        {t('booking.page.booking_flow')}
      </Text>
    </YStack>
  );
}

export default function RestaurantInfoPage() {
  const { tenant } = useLocalSearchParams<{ tenant: string }>();
  const { t } = useTranslation();
  const [restaurant, setRestaurant] = useState<RestaurantInfo | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!tenant) {
      setError(new ApiError(400, 'INVALID_TENANT'));
      setIsLoading(false);
      return;
    }

    void (async () => {
      try {
        const data = await publicApi.getRestaurantInfo(tenant);
        setRestaurant(data as RestaurantInfo);
      } catch (cause) {
        setError(cause instanceof ApiError ? cause : new ApiError(500, 'UNKNOWN_ERROR'));
      } finally {
        setIsLoading(false);
      }
    })();
  }, [tenant]);

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

  if (!restaurant) {
    return null;
  }

  return (
    <YStack padding="$4" gap="$6">
      <RestaurantHeader name={restaurant.name} description={restaurant.description ?? null} />
      <YStack gap="$3">
        <Text fontSize="$5" fontWeight="$6">
          {t('booking.page.opening_hours')}
        </Text>
        <OpeningHoursList hours={restaurant.opening_hours ?? []} />
      </YStack>
      <BookingFormFlow />
    </YStack>
  );
}
