jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View, TextInput } = require('react-native');

  return {
    Button: View,
    Input: TextInput,
    Text,
    XStack: View,
    YStack: View,
  };
});

jest.mock('@/lib/api/endpoints', () => ({
  publicApi: { modifyBooking: jest.fn(async () => ({})) },
}));

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { ModifyBookingForm } from '@/components/booking/ModifyBookingForm';

const booking = {
  id: '1',
  status: 'confirmed' as const,
  date: '2025-06-15',
  time: '19:30',
  party_size: 2,
  customer: { name: 'A', phone: '+39', locale: 'it' },
  created_at: '',
};

test('save button triggers modifyBooking', async () => {
  const { publicApi } = require('@/lib/api/endpoints');
  const onDone = jest.fn();
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  render(
    <QueryClientProvider client={client}>
      <ModifyBookingForm tenant="rome" token="tok" booking={booking} onDone={onDone} />
    </QueryClientProvider>,
  );

  fireEvent.press(screen.getByText('Save'));

  await waitFor(() => expect(publicApi.modifyBooking).toHaveBeenCalledWith('rome', 'tok', expect.any(Object)));
});
