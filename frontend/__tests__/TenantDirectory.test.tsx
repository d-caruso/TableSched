jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');
  return { Text, XStack: View, YStack: View };
});

jest.mock('expo-router', () => ({}));

jest.mock('@/lib/api/endpoints', () => ({
  publicApi: {
    tenantDirectory: jest.fn(async () => [
      { name: 'Rome Restaurant',  schema: 'rome',  api_prefix: '/restaurants/rome/'  },
      { name: 'Milan Restaurant', schema: 'milan', api_prefix: '/restaurants/milan/' },
    ]),
  },
}));

jest.mock('@/lib/env', () => ({
  ENV: { SHOW_TENANT_DIRECTORY: true },
}));

import { render, screen, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@/lib/i18n';
import TenantDirectoryPage from '@/app/index';

function wrap(ui: React.ReactElement) {
  return (
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      {ui}
    </QueryClientProvider>
  );
}

test('renders tenant names and URLs', async () => {
  render(wrap(<TenantDirectoryPage />));
  await waitFor(() => {
    expect(screen.getByText('Rome Restaurant')).toBeTruthy();
    expect(screen.getByText('Milan Restaurant')).toBeTruthy();
    expect(screen.getByText('http://localhost/restaurants/rome/')).toBeTruthy();
    expect(screen.getByText('http://localhost/restaurants/milan/')).toBeTruthy();
  });
});

