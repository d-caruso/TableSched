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

const mockMutate = jest.fn();
const mockInvalidateQueries = jest.fn();

jest.mock('@tanstack/react-query', () => ({
  useMutation: () => ({
    mutate: mockMutate,
    isPending: false,
    error: null,
  }),
  useQueryClient: () => ({
    invalidateQueries: mockInvalidateQueries,
  }),
}));

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    updateTablePosition: jest.fn(async () => {}),
  },
}));

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { FloorCanvas } from '@/components/floor/FloorCanvas';

const room = {
  id: 'r1',
  name: 'Main',
  tables: [{ id: 't1', name: 'T1', capacity: 2, x: 0, y: 0 }],
};

test('renders a table for each room table', () => {
  render(<FloorCanvas room={room} tenant="r" token="tok" />);
  expect(screen.getByText('T1')).toBeTruthy();
});
