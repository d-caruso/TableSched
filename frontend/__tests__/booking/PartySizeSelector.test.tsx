import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';

test('increments party size', () => {
  const onChange = jest.fn();
  render(<PartySizeSelector value={2} onChange={onChange} />);
  fireEvent.press(screen.getByText('common.increment'));
  expect(onChange).toHaveBeenCalledWith(3);
});

test('does not decrement below 1', () => {
  const onChange = jest.fn();
  render(<PartySizeSelector value={1} onChange={onChange} />);
  fireEvent.press(screen.getByText('common.decrement'));
  expect(onChange).not.toHaveBeenCalled();
});
