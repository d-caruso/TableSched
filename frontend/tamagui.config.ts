import { config } from '@tamagui/config/v3';
import { createTamagui } from 'tamagui';

export const tamaguiConfig = createTamagui({
  ...config,
  tokens: {
    ...config.tokens,
    color: {
      ...config.tokens.color,
      brand: '#1a56db',
      brandDark: '#1e429f',
      danger: '#e02424',
      warning: '#c27803',
      success: '#057a55',
    },
  },
});

export type AppConfig = typeof tamaguiConfig;
