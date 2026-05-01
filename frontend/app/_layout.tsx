import React from 'react';
if (typeof window === 'undefined') {
  // Suppress useLayoutEffect SSR warning from libraries (Tamagui, Reanimated, etc.)
  (React as any).useLayoutEffect = React.useEffect;
}
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Slot } from 'expo-router';
import { TamaguiProvider } from 'tamagui';
import { I18nProvider } from '@/lib/i18n/I18nProvider';
import { tamaguiConfig } from '@/tamagui.config';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <TamaguiProvider config={tamaguiConfig} defaultTheme="light">
        <I18nProvider>
          <Slot />
        </I18nProvider>
      </TamaguiProvider>
    </QueryClientProvider>
  );
}
