jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    Text,
    YStack: View,
  };
});

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { RestaurantHeader } from '@/components/booking/RestaurantHeader';

test('displays restaurant name', () => {
  render(<RestaurantHeader name="Da Mario" />);
  expect(screen.getByText('Da Mario')).toBeTruthy();
});
