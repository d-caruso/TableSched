jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) =>
      ({
        'staff.settings.openingHours': 'Opening hours',
        'staff.settings.open': 'Open',
        'staff.settings.close': 'Close',
        'booking.weekdays.0': 'Sunday',
        'booking.weekdays.1': 'Monday',
        'booking.weekdays.2': 'Tuesday',
        'booking.weekdays.3': 'Wednesday',
        'booking.weekdays.4': 'Thursday',
        'booking.weekdays.5': 'Friday',
        'booking.weekdays.6': 'Saturday',
      })[key] ?? key,
  }),
}));

jest.mock('@/lib/i18n', () => ({}));

jest.mock('@/components/ui/AppInput', () => {
  const React = require('react');
  const { TextInput, View, Text } = require('react-native');

  return {
    AppInput: ({ label, ...props }: any) => (
      <View>
        <Text>{label}</Text>
        <TextInput accessibilityLabel={label} {...props} />
      </View>
    ),
  };
});

import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { OpeningHoursEditor } from '@/components/settings/OpeningHoursEditor';

test('toggling a closed day adds a default entry', () => {
  const onChange = jest.fn();
  render(<OpeningHoursEditor hours={[]} onChange={onChange} />);

  fireEvent(screen.getAllByRole('switch')[1], 'valueChange', true);

  expect(onChange).toHaveBeenCalledWith([
    expect.objectContaining({ weekday: 1, opens_at: '09:00', closes_at: '22:00' }),
  ]);
});

test('toggling an open day removes its entry', () => {
  const onChange = jest.fn();
  render(<OpeningHoursEditor hours={[{ weekday: 1, opens_at: '09:00', closes_at: '22:00' }]} onChange={onChange} />);

  fireEvent(screen.getAllByRole('switch')[1], 'valueChange', false);

  expect(onChange).toHaveBeenCalledWith([]);
});

test('updating close time patches the correct day', () => {
  const onChange = jest.fn();
  render(<OpeningHoursEditor hours={[{ weekday: 1, opens_at: '09:00', closes_at: '22:00' }]} onChange={onChange} />);

  const inputs = screen.getAllByDisplayValue('22:00');
  fireEvent.changeText(inputs[0], '23:00');

  expect(onChange).toHaveBeenCalledWith([{ weekday: 1, opens_at: '09:00', closes_at: '23:00' }]);
});
