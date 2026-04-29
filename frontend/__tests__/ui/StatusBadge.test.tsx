jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    Button: View,
    Input: View,
    Text,
    XStack: View,
    YStack: View,
    TamaguiProvider: ({ children }: { children: React.ReactNode }) => children,
    createTamagui: (config: unknown) => config,
  };
});

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { StatusBadge } from '@/components/ui/StatusBadge';

test('renders localized status label', () => {
  render(<StatusBadge status="pending_review" />);
  expect(screen.getByText(/Pending review/)).toBeTruthy();
});
