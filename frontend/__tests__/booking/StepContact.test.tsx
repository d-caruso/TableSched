jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) =>
      ({
        'booking.page.booking_flow': 'Booking flow',
        'booking.contact.full_name': 'Full name',
        'booking.contact.phone_number': 'Phone number',
        'booking.contact.email': 'Email',
        'booking.contact.notes': 'Notes',
        'booking.contact.locale': 'Language',
        'booking.page.back': 'Back',
        'booking.page.request_booking': 'Request booking',
      })[key] ?? key,
  }),
}));

jest.mock('@/lib/i18n', () => ({}));

import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { StepContact } from '@/components/booking/steps/StepContact';

test('submit button disabled when name or phone empty', () => {
  const onNext = jest.fn();
  render(<StepContact draft={{}} tenant="r" onBack={jest.fn()} onNext={onNext} />);
  fireEvent.press(screen.getByText('Request booking'));
  expect(onNext).not.toHaveBeenCalled();
});

test('calls onNext with contact fields when valid', () => {
  const onNext = jest.fn();
  render(<StepContact draft={{}} tenant="r" onBack={jest.fn()} onNext={onNext} />);
  fireEvent.changeText(screen.getByLabelText('Full name'), 'Mario Rossi');
  fireEvent.changeText(screen.getByLabelText('Phone number'), '+393331234567');
  fireEvent.press(screen.getByText('Request booking'));
  expect(onNext).toHaveBeenCalledWith(expect.objectContaining({ name: 'Mario Rossi', phone: '+393331234567' }));
});
