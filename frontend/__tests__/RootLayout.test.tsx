import { expect, jest, test } from '@jest/globals';
import { render } from '@testing-library/react-native';
import type { ReactNode } from 'react';

jest.mock('expo-router', () => ({
  Slot: () => null,
}));

jest.mock('@tamagui/config/v3', () => ({
  config: {
    tokens: {
      color: {},
    },
  },
}));

jest.mock('tamagui', () => ({
  createTamagui: (config: unknown) => config,
  TamaguiProvider: ({ children }: { children: ReactNode }) => children,
}));

import RootLayout from '@/app/_layout';

test('root layout renders without crash', () => {
  expect(() => render(<RootLayout />)).not.toThrow();
});
