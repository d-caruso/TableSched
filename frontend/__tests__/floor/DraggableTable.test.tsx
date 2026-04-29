jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    Text,
    YStack: View,
  };
});

jest.mock('react-native-gesture-handler', () => {
  const React = require('react');
  const { View } = require('react-native');

  const gesture = {
    onBegin() {
      return gesture;
    },
    onUpdate() {
      return gesture;
    },
    onEnd() {
      return gesture;
    },
  };

  return {
    Gesture: {
      Pan: () => gesture,
    },
    GestureDetector: ({ children }: { children: React.ReactNode }) => children,
    GestureHandlerRootView: View,
  };
});

jest.mock('react-native-reanimated', () => {
  const React = require('react');
  const { View } = require('react-native');

  return {
    __esModule: true,
    default: { View },
    runOnJS: (fn: (...args: unknown[]) => unknown) => fn,
    useAnimatedStyle: (factory: () => Record<string, unknown>) => factory(),
    useSharedValue: (value: number) => ({ value }),
  };
});

jest.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (_key: string, options?: { count?: number }) => `${options?.count ?? ''} seats` }),
}));

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { DraggableTable } from '@/components/floor/DraggableTable';

const table = { id: 't1', name: 'T1', capacity: 4, x: 100, y: 50 };

test('displays table name and capacity', () => {
  render(<DraggableTable table={table} onDrop={jest.fn()} />);
  expect(screen.getByText('T1')).toBeTruthy();
  expect(screen.getByText('4 seats')).toBeTruthy();
});
