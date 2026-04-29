jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    Text,
    XStack: View,
    YStack: View,
  };
});

const mockPush = jest.fn();

jest.mock('expo-router', () => ({
  useRouter: () => ({ push: mockPush }),
}));

jest.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

jest.mock('@/components/ui/StatusBadge', () => ({
  StatusBadge: ({ status }: { status: string }) => null,
}));

import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test, beforeEach } from '@jest/globals';
import { BookingCard } from '@/components/staff/BookingCard';

beforeEach(() => {
  mockPush.mockReset();
});

test('navigates to booking detail on press', () => {
  render(
    <BookingCard
      booking={{
        id: '123',
        status: 'confirmed',
        date: '2025-06-15',
        time: '19:30',
        party_size: 4,
        customer: { name: 'Mario Rossi', phone: '+39333' },
        created_at: '2025-06-01T10:00:00Z',
      }}
    />,
  );

  fireEvent.press(screen.getByRole('button'));

  expect(mockPush).toHaveBeenCalledWith('/dashboard/bookings/123');
});
