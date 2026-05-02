jest.mock('@/lib/i18n/useLocale', () => ({
  useLocale: () => ({ locale: 'en-US', setLocale: jest.fn() }),
}));

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { BookingInfoCard } from '@/components/booking/BookingInfoCard';

const booking = {
  id: '1',
  status: 'confirmed' as const,
  date: '2025-06-15',
  time: '19:30',
  party_size: 4,
  customer: { name: 'Mario Rossi', phone: '+39333', locale: 'it' },
  created_at: '2025-06-01T10:00:00Z',
};

test('displays date, time and party size', () => {
  render(<BookingInfoCard booking={booking} />);
  expect(screen.getByText('2025-06-15')).toBeTruthy();
  expect(screen.getByText(/19:30/)).toBeTruthy();
  expect(screen.getByText(/4 guests/)).toBeTruthy();
});

test('does not crash when payment is absent', () => {
  expect(() => render(<BookingInfoCard booking={booking} />)).not.toThrow();
});
