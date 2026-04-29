jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    Button: View,
    Text,
    XStack: View,
    YStack: View,
  };
});

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { CustomerBookingActions } from '@/components/booking/CustomerBookingActions';

const base = {
  id: '1',
  date: '2025-06-15',
  time: '19:30',
  party_size: 2,
  customer: { name: 'A', phone: '+39', locale: 'it' },
  created_at: '',
};

test('shows cancel button for confirmed booking', () => {
  render(
    <CustomerBookingActions
      booking={{ ...base, status: 'confirmed' }}
      token="tok"
      onCancel={jest.fn()}
      cancelling={false}
      onPay={jest.fn()}
    />,
  );

  expect(screen.getByText('Cancel booking')).toBeTruthy();
});

test('shows pay button only for pending_payment', () => {
  render(
    <CustomerBookingActions
      booking={{ ...base, status: 'pending_payment' }}
      token="tok"
      onCancel={jest.fn()}
      cancelling={false}
      onPay={jest.fn()}
    />,
  );

  expect(screen.getByText('Pay deposit')).toBeTruthy();
});

test('shows no action buttons for declined booking', () => {
  render(
    <CustomerBookingActions
      booking={{ ...base, status: 'declined' }}
      token="tok"
      onCancel={jest.fn()}
      cancelling={false}
      onPay={jest.fn()}
    />,
  );

  expect(screen.queryByText('Cancel booking')).toBeNull();
  expect(screen.queryByText('Pay deposit')).toBeNull();
});
