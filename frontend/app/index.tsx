import { useQuery } from '@tanstack/react-query';
import { Text, XStack, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { publicApi } from '@/lib/api/endpoints';
import { ENV } from '@/lib/env';

function TenantTable() {
  const { t } = useTranslation();
  const { data: tenants = [], isLoading } = useQuery({
    queryKey: ['tenant-directory'],
    queryFn: () => publicApi.tenantDirectory(),
  });

  if (isLoading) {
    return (
      <YStack padding="$4">
        <Text>{t('common.loading')}</Text>
      </YStack>
    );
  }

  return (
    <YStack padding="$4" gap="$6">
      <Text fontSize="$7" fontWeight="$8">{t('tenantDirectory.title')}</Text>
      <YStack gap="$2">
        <XStack gap="$4">
          <Text fontWeight="$7" flex={1}>{t('tenantDirectory.restaurant')}</Text>
          <Text fontWeight="$7" flex={2}>{t('tenantDirectory.bookingUrl')}</Text>
          <Text fontWeight="$7" flex={2}>{t('tenantDirectory.staffLogin')}</Text>
        </XStack>
        {tenants.map((tenant) => (
          <XStack key={tenant.schema} gap="$4">
            <Text flex={1}>{tenant.name}</Text>
            <Text flex={2}>{tenant.api_prefix}</Text>
            <Text flex={2}>{`${tenant.api_prefix}login`}</Text>
          </XStack>
        ))}
      </YStack>
    </YStack>
  );
}

function LandingPage() {
  const { t } = useTranslation();
  return (
    <YStack flex={1} alignItems="center" justifyContent="center" padding="$4" gap="$3">
      <Text fontSize="$9" fontWeight="$8">{t('app.name')}</Text>
      <Text fontSize="$5" color="$placeholderColor">{t('app.tagline')}</Text>
    </YStack>
  );
}

export default function TenantDirectoryPage() {
  if (!ENV.SHOW_TENANT_DIRECTORY) {
    return <LandingPage />;
  }

  return <TenantTable />;
}
