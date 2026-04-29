import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import type { ReactNode } from 'react';
import { I18nProvider } from '@/lib/i18n/I18nProvider';
import { StepContact } from '@/components/booking/steps/StepContact';

const wrapper = ({ children }: { children: ReactNode }) => <I18nProvider>{children}</I18nProvider>;

test('submit button disabled when name or phone empty', () => {
  const onNext = jest.fn();
  render(<StepContact draft={{}} tenant="r" onBack={jest.fn()} onNext={onNext} />, { wrapper });
  fireEvent.press(screen.getByText('Request booking'));
  expect(onNext).not.toHaveBeenCalled();
});

test('calls onNext with contact fields when valid', () => {
  const onNext = jest.fn();
  render(<StepContact draft={{}} tenant="r" onBack={jest.fn()} onNext={onNext} />, { wrapper });
  fireEvent.changeText(screen.getByLabelText('Full name'), 'Mario Rossi');
  fireEvent.changeText(screen.getByLabelText('Phone number'), '+393331234567');
  fireEvent.press(screen.getByText('Request booking'));
  expect(onNext).toHaveBeenCalledWith(expect.objectContaining({ name: 'Mario Rossi', phone: '+393331234567' }));
});
