jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    Button: View,
    Text,
    YStack: View,
  };
});

import { render, screen } from '@testing-library/react-native';
import { expect, test } from '@jest/globals';
import { BookingFormFlow } from '@/components/booking/BookingFormFlow';

const restaurant = {
  slug: 'r',
  name: 'R',
  opening_hours: [],
  deposit_policy: { mode: 'never' },
  cancellation_cutoff_hours: 24,
};

test('starts on datetime step', () => {
  render(<BookingFormFlow tenant="r" restaurant={restaurant} />);
  expect(screen.getByTestId('step-datetime')).toBeTruthy();
});
