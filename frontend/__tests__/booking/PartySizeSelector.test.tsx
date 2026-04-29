import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';

test('increments party size', () => {
  const onChange = jest.fn();
  render(<PartySizeSelector value={2} onChange={onChange} />);
  fireEvent.press(screen.getByText('+'));
  expect(onChange).toHaveBeenCalledWith(3);
});

test('does not decrement below 1', () => {
  const onChange = jest.fn();
  render(<PartySizeSelector value={1} onChange={onChange} />);
  fireEvent.press(screen.getByText('−'));
  expect(onChange).not.toHaveBeenCalled();
});

