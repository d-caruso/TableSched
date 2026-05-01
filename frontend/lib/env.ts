import Constants from 'expo-constants';

const extra = Constants.expoConfig?.extra ?? {};

export const ENV = {
  API_BASE_URL:
    process.env.EXPO_PUBLIC_API_BASE_URL ?? extra.apiBaseUrl ?? '',
  STRIPE_KEY: process.env.EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY ?? '',
  APP_ENV: process.env.EXPO_PUBLIC_APP_ENV ?? 'development',
  SHOW_TENANT_DIRECTORY: process.env.EXPO_PUBLIC_SHOW_TENANT_DIRECTORY === 'true',
} as const;
