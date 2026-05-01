import { expect, jest, test } from '@jest/globals';

jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');
  return { Text, XStack: View, YStack: View };
});

jest.mock('expo-router', () => ({}));

jest.mock('@/lib/api/endpoints', () => ({
  publicApi: { tenantDirectory: jest.fn() },
}));

jest.mock('@/lib/env', () => ({
  ENV: { SHOW_TENANT_DIRECTORY: false },
}));

jest.mock('@/lib/i18n', () => {});

jest.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

import { render, screen } from '@testing-library/react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TenantDirectoryPage from '@/app/index';

function wrap(ui: React.ReactElement) {
  return (
    <QueryClientProvider client={new QueryClient()}>
      {ui}
    </QueryClientProvider>
  );
}

test('renders branded landing page when SHOW_TENANT_DIRECTORY is false', () => {
  render(wrap(<TenantDirectoryPage />));
  expect(screen.getByText('app.name')).toBeTruthy();
  expect(screen.getByText('app.tagline')).toBeTruthy();
});
