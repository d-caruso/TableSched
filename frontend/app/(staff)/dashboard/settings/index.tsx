import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ScrollView, Spinner, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { AppButton } from '@/components/ui/AppButton';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { useAuth } from '@/lib/auth/AuthContext';
import { staffApi } from '@/lib/api/endpoints';
import type { RestaurantSettings } from '@/lib/api/types';

export default function SettingsScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState<Partial<RestaurantSettings>>({});

  const { data, isLoading, error } = useQuery({
    queryKey: ['restaurant-settings', tenant],
    queryFn: () => staffApi.getRestaurantSettings(tenant!, accessToken!),
    enabled: Boolean(accessToken && tenant),
  });

  const save = useMutation({
    mutationFn: () => staffApi.updateRestaurantSettings(tenant!, accessToken!, draft),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['restaurant-settings', tenant] });
      setDraft({});
    },
  });

  if (isLoading) {
    return <Spinner size="large" />;
  }

  if (error || !data) {
    return <ErrorMessage error={error} />;
  }

  return (
    <ScrollView>
      <YStack width="100%" maxWidth={600} alignSelf="center" padding="$4" gap="$4">
        <Text fontSize="$6" fontWeight="$7">
          {t('staff.settings.title')}
        </Text>
        {save.error ? <ErrorMessage error={save.error} /> : null}
        <AppButton onPress={() => save.mutate()} loading={save.isPending} disabled={Object.keys(draft).length === 0}>
          {t('common.save')}
        </AppButton>
      </YStack>
    </ScrollView>
  );
}
