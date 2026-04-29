jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View, TextInput } = require('react-native');

  return {
    Input: TextInput,
    Text,
    YStack: View,
  };
});

jest.mock('@/components/ui/AppButton', () => ({
  AppButton: ({ children, onPress }: any) => {
    const { Text, Pressable } = require('react-native');
    return (
      <Pressable onPress={onPress}>
        <Text>{children}</Text>
      </Pressable>
    );
  },
}));

jest.mock('@/components/staff/RejectDialog', () => ({
  RejectDialog: () => null,
}));

jest.mock('@/components/staff/AssignTableDialog', () => ({
  AssignTableDialog: () => null,
}));

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import '@/lib/i18n';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';

const base = {
  id: '1',
  date: '2025-06-15',
  time: '19:30',
  party_size: 2,
  customer: { name: 'A', phone: '+39', locale: 'it' },
  created_at: '',
};

function renderWithClient(ui: ReactElement) {
  const client = new QueryClient();
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

test('shows approve and reject for pending_review', () => {
  renderWithClient(<StaffBookingActions booking={{ ...base, status: 'pending_review' }} tenant="r" token="tok" onActionComplete={() => undefined} />);
  expect(screen.getByText('Approve')).toBeTruthy();
  expect(screen.getByText('Reject')).toBeTruthy();
});

test('shows confirm without deposit for authorization_expired', () => {
  renderWithClient(<StaffBookingActions booking={{ ...base, status: 'authorization_expired' }} tenant="r" token="tok" onActionComplete={() => undefined} />);
  expect(screen.getByText('Confirm without deposit')).toBeTruthy();
});

test('does not show approve for confirmed booking', () => {
  renderWithClient(<StaffBookingActions booking={{ ...base, status: 'confirmed' }} tenant="r" token="tok" onActionComplete={() => undefined} />);
  expect(screen.queryByText('Approve')).toBeNull();
});
