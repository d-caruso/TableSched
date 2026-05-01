import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Text, XStack, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { publicApi } from '@/lib/api/endpoints';
import { ENV } from '@/lib/env';
import type { TenantEntry } from '@/lib/api/types';

function tenantBookingUrl(tenant: TenantEntry): string {
  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  return `${origin}/restaurants/${tenant.schema}/`;
}

function tenantLoginUrl(tenant: TenantEntry): string {
  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  return `${origin}/restaurants/${tenant.schema}/login`;
}

const linkStyle: React.CSSProperties = { color: 'inherit' };

function TenantRow({ tenant }: { tenant: TenantEntry }) {
  const bookingUrl = tenantBookingUrl(tenant);
  const loginUrl = tenantLoginUrl(tenant);
  return (
    <XStack gap="$4" paddingVertical="$2" borderBottomWidth={1} borderBottomColor="$borderColor">
      <Text flex={1}>{tenant.name}</Text>
      <Text flex={2}>
        <a href={bookingUrl} target="_blank" rel="noopener noreferrer" style={linkStyle}>
          {bookingUrl}
        </a>
      </Text>
      <Text flex={2}>
        <a href={loginUrl} target="_blank" rel="noopener noreferrer" style={linkStyle}>
          {loginUrl}
        </a>
      </Text>
    </XStack>
  );
}

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
    <YStack padding="$8" gap="$6" maxWidth={960} alignSelf="center" width="100%">
      <Text fontSize="$8" fontWeight="$8">{t('tenantDirectory.title')}</Text>
      <YStack>
        <XStack gap="$4" paddingVertical="$3" borderBottomWidth={2} borderBottomColor="$borderColor">
          <Text fontWeight="$7" flex={1}>{t('tenantDirectory.restaurant')}</Text>
          <Text fontWeight="$7" flex={2}>{t('tenantDirectory.bookingUrl')}</Text>
          <Text fontWeight="$7" flex={2}>{t('tenantDirectory.staffLogin')}</Text>
        </XStack>
        {tenants.map((tenant) => (
          <TenantRow key={tenant.schema} tenant={tenant} />
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
