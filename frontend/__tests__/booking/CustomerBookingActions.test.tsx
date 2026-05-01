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

jest.mock('@/lib/api/endpoints', () => ({
  publicApi: {
    cancelBooking: jest.fn(() => Promise.resolve()),
    modifyBooking: jest.fn(() => Promise.resolve({})),
  },
}));

import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
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
      tenant="rome"
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
      tenant="rome"
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
      tenant="rome"
      token="tok"
      onCancel={jest.fn()}
      cancelling={false}
      onPay={jest.fn()}
    />,
  );

  expect(screen.queryByText('Cancel booking')).toBeNull();
  expect(screen.queryByText('Pay deposit')).toBeNull();
});

test('cancel passes tenant to cancelBooking', async () => {
  const { publicApi } = require('@/lib/api/endpoints') as { publicApi: { cancelBooking: ReturnType<typeof jest.fn> } };
  const onCancel = jest.fn((token: string) => publicApi.cancelBooking('rome', token));
  render(
    <CustomerBookingActions
      booking={{ ...base, status: 'confirmed' }}
      tenant="rome"
      token="tok"
      onCancel={onCancel}
      cancelling={false}
      onPay={jest.fn()}
    />,
  );
  fireEvent.press(screen.getByText('Cancel booking'));
  await waitFor(() =>
    expect(publicApi.cancelBooking).toHaveBeenCalledWith('rome', 'tok'),
  );
});
