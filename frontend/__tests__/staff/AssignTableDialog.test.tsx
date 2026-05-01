jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View, TextInput } = require('react-native');
  return { Input: TextInput, Text, YStack: View };
});

jest.mock('@/components/ui/AppButton', () => ({
  AppButton: ({ children, onPress, disabled }: any) => {
    const { Text, Pressable } = require('react-native');
    return (
      <Pressable onPress={onPress} disabled={disabled} accessibilityState={{ disabled }}>
        <Text>{children}</Text>
      </Pressable>
    );
  },
}));

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    postDecision: jest.fn(() => Promise.resolve({})),
    assignTables: jest.fn(() => Promise.resolve({ tables: ['t1'] })),
  },
}));

import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import '@/lib/i18n';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';

const base = {
  id: 'b1',
  date: '2026-05-01',
  time: '19:00',
  party_size: 2,
  customer: { name: 'A', phone: '+39', locale: 'it' },
  created_at: '',
};

function renderWithClient(ui: ReactElement) {
  const client = new QueryClient();
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

test('assign table calls assignTables with array-wrapped tableId', async () => {
  const { staffApi } = require('@/lib/api/endpoints');
  renderWithClient(
    <StaffBookingActions
      booking={{ ...base, status: 'confirmed' }}
      tenant="r"
      token="tok"
      onActionComplete={() => undefined}
    />,
  );
  fireEvent.press(screen.getByText('Assign table'));
  fireEvent.changeText(screen.getByLabelText('Table'), 't1');
  fireEvent.press(screen.getByText('Submit'));
  await waitFor(() =>
    expect(staffApi.assignTables).toHaveBeenCalledWith('r', 'tok', 'b1', ['t1']),
  );
});
