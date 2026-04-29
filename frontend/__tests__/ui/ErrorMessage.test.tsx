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
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { ApiError } from '@/lib/api/client';

test('renders i18n key for known error code', () => {
  const err = new ApiError(404, 'BOOKING_NOT_FOUND');
  render(<ErrorMessage error={err} />);
  expect(screen.getByText(/Booking not found/)).toBeTruthy();
});

test('falls back to common.error for unknown code', () => {
  const err = new ApiError(500, 'VERY_UNKNOWN_CODE');
  render(<ErrorMessage error={err} />);
  expect(screen.getByText(/Something went wrong/)).toBeTruthy();
});
