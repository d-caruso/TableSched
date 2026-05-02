jest.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

jest.mock('@/lib/i18n', () => ({}));

import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { TimeSlotGrid } from '@/components/booking/TimeSlotGrid';

test('unavailable slots are not pressable', () => {
  const onSelect = jest.fn();
  render(
    <TimeSlotGrid
      slots={[{ time: '13:00', available: false, busy_warning: false }]}
      loading={false}
      selected=""
      onSelect={onSelect}
    />,
  );
  fireEvent.press(screen.getByText('13:00'));
  expect(onSelect).not.toHaveBeenCalled();
});
