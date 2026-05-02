import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button, Text, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { publicApi } from '@/lib/api/endpoints';
import { ENV } from '@/lib/env';
import type { TenantEntry } from '@/lib/api/types';

function tenantBookingUrl(tenant: TenantEntry): string {
  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  return `${origin}/restaurants/${tenant.schema}/`;
}

function staffLoginUrl(): string {
  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  return `${origin}/login`;
}

const linkStyle: React.CSSProperties = { color: 'inherit', textDecoration: 'none' };

function TenantDirectory() {
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
    <YStack padding="$8" gap="$8" maxWidth={640} alignSelf="center" width="100%">
      <Text fontSize="$8" fontWeight="$8">{t('tenantDirectory.title')}</Text>
      <YStack gap="$3">
        {tenants.map((tenant) => (
          <a
            key={tenant.schema}
            href={tenantBookingUrl(tenant)}
            target="_blank"
            rel="noopener noreferrer"
            style={linkStyle}
          >
            <Button size="$5" width="100%" justifyContent="flex-start">
              {tenant.name}
            </Button>
          </a>
        ))}
      </YStack>
      <a href={staffLoginUrl()} style={linkStyle}>
        <Button size="$4" theme="alt1" width="100%">
          {t('tenantDirectory.staffLogin')}
        </Button>
      </a>
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

  return <TenantDirectory />;
}
