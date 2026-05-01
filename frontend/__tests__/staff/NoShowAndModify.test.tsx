jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    postDecision: jest.fn(() => Promise.resolve({})),
    assignTables: jest.fn(() => Promise.resolve({ tables: [] })),
    patchBooking: jest.fn(() => Promise.resolve({})),
  },
}));

jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View, TextInput } = require('react-native');
  return { Input: TextInput, Text, YStack: View };
});

jest.mock('@/components/ui/AppButton', () => ({
  AppButton: ({ children, onPress, loading }: any) => {
    const { Text, Pressable } = require('react-native');
    return (
      <Pressable onPress={onPress} disabled={loading}>
        <Text>{children}</Text>
      </Pressable>
    );
  },
}));

jest.mock('@/components/staff/RejectDialog', () => ({ RejectDialog: () => null }));
jest.mock('@/components/staff/AssignTableDialog', () => ({ AssignTableDialog: () => null }));

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
  return render(<QueryClientProvider client={new QueryClient()}>{ui}</QueryClientProvider>);
}

test('no-show button calls patchBooking with status no_show', async () => {
  const { staffApi } = require('@/lib/api/endpoints');
  renderWithClient(
    <StaffBookingActions booking={{ ...base, status: 'confirmed' }} tenant="r" token="tok" onActionComplete={() => undefined} />,
  );
  fireEvent.press(screen.getByText('No show'));
  await waitFor(() =>
    expect(staffApi.patchBooking).toHaveBeenCalledWith('r', 'tok', 'b1', { status: 'no_show' }),
  );
});

test('no-show button is not shown for pending_review', () => {
  renderWithClient(
    <StaffBookingActions booking={{ ...base, status: 'pending_review' }} tenant="r" token="tok" onActionComplete={() => undefined} />,
  );
  expect(screen.queryByText('No show')).toBeNull();
});

test('modify button opens dialog and calls patchBooking', async () => {
  const { staffApi } = require('@/lib/api/endpoints');
  renderWithClient(
    <StaffBookingActions booking={{ ...base, status: 'confirmed' }} tenant="r" token="tok" onActionComplete={() => undefined} />,
  );
  fireEvent.press(screen.getByText('Modify booking'));
  fireEvent.changeText(screen.getByLabelText('Party size'), '4');
  fireEvent.press(screen.getByText('Save'));
  await waitFor(() =>
    expect(staffApi.patchBooking).toHaveBeenCalledWith('r', 'tok', 'b1', expect.objectContaining({ party_size: 4 })),
  );
});
