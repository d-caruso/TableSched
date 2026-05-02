jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    getBooking: jest.fn(),
    refundPayment: jest.fn(() => Promise.resolve({ id: 'p1', status: 'refund_pending' })),
    postDecision: jest.fn(() => Promise.resolve({})),
    assignTables: jest.fn(() => Promise.resolve({ tables: [] })),
    patchBooking: jest.fn(() => Promise.resolve({})),
  },
}));

jest.mock('expo-router', () => ({
  useLocalSearchParams: () => ({ id: 'b1' }),
}));

jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => ({ accessToken: 'tok', tenant: 'r' }),
}));

jest.mock('@/components/booking/BookingInfoCard', () => ({ BookingInfoCard: () => null }));
jest.mock('@/components/ui/StatusBadge', () => ({ StatusBadge: () => null }));
jest.mock('@/components/ui/ErrorMessage', () => ({ ErrorMessage: () => null }));
jest.mock('@/components/staff/StaffBookingActions', () => ({ StaffBookingActions: () => null }));
jest.mock('@/components/ui/AppButton', () => ({
  AppButton: ({ children, onPress }: any) => {
    const { Text, Pressable } = require('react-native');
    return <Pressable onPress={onPress}><Text>{children}</Text></Pressable>;
  },
}));

import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import '@/lib/i18n';
import StaffBookingDetail from '@/app/(staff)/dashboard/bookings/[id]';

const capturedPaymentBooking = {
  id: 'b1',
  status: 'confirmed' as const,
  date: '2026-05-01',
  time: '19:00',
  party_size: 2,
  customer: { name: 'A', phone: '+39', locale: 'it' },
  created_at: '',
  payment: { id: 'p1', status: 'captured' as const, amount: 2000, currency: 'eur' },
};

const noPaymentBooking = { ...capturedPaymentBooking, payment: null };

function renderWithClient(ui: ReactElement) {
  return render(<QueryClientProvider client={new QueryClient()}>{ui}</QueryClientProvider>);
}

test('refund button calls refundPayment when payment is captured', async () => {
  const { staffApi } = require('@/lib/api/endpoints');
  (staffApi.getBooking as any).mockResolvedValue(capturedPaymentBooking);
  renderWithClient(<StaffBookingDetail />);
  await waitFor(() => expect(screen.getByText('Refund deposit')).toBeTruthy());
  fireEvent.press(screen.getByText('Refund deposit'));
  await waitFor(() =>
    expect(staffApi.refundPayment).toHaveBeenCalledWith('r', 'tok', 'p1'),
  );
});

test('refund button is not shown when payment is not captured', async () => {
  const { staffApi } = require('@/lib/api/endpoints');
  (staffApi.getBooking as any).mockResolvedValue(noPaymentBooking);
  renderWithClient(<StaffBookingDetail />);
  await waitFor(() => expect(screen.queryByText('Refund deposit')).toBeNull());
});

test('request payment button is not rendered', async () => {
  const { staffApi } = require('@/lib/api/endpoints');
  (staffApi.getBooking as any).mockResolvedValue(capturedPaymentBooking);
  renderWithClient(<StaffBookingDetail />);
  await waitFor(() => expect(screen.queryByText('Request payment')).toBeNull());
});
