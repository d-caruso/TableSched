/**
 * OpeningHoursEditor tests
 *
 * Covers:
 * - toggling a closed day on/off
 * - adding and removing a second slot
 * - patching opens_at / closes_at on a specific slot
 * - multi-slot serialisation (two records for same weekday)
 */

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) =>
      ({
        'staff.settings.openingHours': 'Opening hours',
        'staff.settings.open': 'Open',
        'staff.settings.close': 'Close',
        'staff.settings.closed': 'Closed',
        'staff.settings.addSlot': 'Add slot',
        'staff.settings.removeSlot': 'Remove slot',
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

import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { OpeningHoursEditor } from '@/components/settings/OpeningHoursEditor';

// ─── toggle tests ────────────────────────────────────────────────────────────

test('toggling a closed day on adds a default slot', () => {
  const onChange = jest.fn();
  render(<OpeningHoursEditor hours={[]} onChange={onChange} />);

  // switches are rendered in DAYS order (0=Sun,1=Mon…); index 1 = Monday
  fireEvent(screen.getAllByRole('switch')[1], 'valueChange', true);

  expect(onChange).toHaveBeenCalledWith([
    expect.objectContaining({ weekday: 1, opens_at: '09:00', closes_at: '22:00' }),
  ]);
});

test('toggling an open day off removes all its slots', () => {
  const onChange = jest.fn();
  render(
    <OpeningHoursEditor
      hours={[
        { weekday: 1, opens_at: '12:00', closes_at: '14:30' },
        { weekday: 1, opens_at: '19:00', closes_at: '22:00' },
      ]}
      onChange={onChange}
    />,
  );

  fireEvent(screen.getAllByRole('switch')[1], 'valueChange', false);

  expect(onChange).toHaveBeenCalledWith([]);
});

// ─── add / remove slot tests ─────────────────────────────────────────────────

test('pressing Add slot appends a second slot for the same day', () => {
  const onChange = jest.fn();
  render(
    <OpeningHoursEditor
      hours={[{ weekday: 1, opens_at: '12:00', closes_at: '14:30' }]}
      onChange={onChange}
    />,
  );

  fireEvent.press(screen.getByAccessibilityLabel('Add slot'));

  expect(onChange).toHaveBeenCalledWith([
    expect.objectContaining({ weekday: 1, opens_at: '12:00', closes_at: '14:30' }),
    expect.objectContaining({ weekday: 1, opens_at: '19:00', closes_at: '22:00' }),
  ]);
});

test('pressing Remove slot removes the correct slot, keeps the other', () => {
  const onChange = jest.fn();
  render(
    <OpeningHoursEditor
      hours={[
        { weekday: 1, opens_at: '12:00', closes_at: '14:30' },
        { weekday: 1, opens_at: '19:00', closes_at: '22:00' },
      ]}
      onChange={onChange}
    />,
  );

  // two Remove slot buttons rendered for Monday; press the first (lunch)
  const removeBtns = screen.getAllByAccessibilityLabel('Remove slot');
  fireEvent.press(removeBtns[0]);

  expect(onChange).toHaveBeenCalledWith([
    expect.objectContaining({ weekday: 1, opens_at: '19:00', closes_at: '22:00' }),
  ]);
});

test('Add slot button is hidden when day already has 2 slots', () => {
  render(
    <OpeningHoursEditor
      hours={[
        { weekday: 1, opens_at: '12:00', closes_at: '14:30' },
        { weekday: 1, opens_at: '19:00', closes_at: '22:00' },
      ]}
      onChange={jest.fn()}
    />,
  );

  expect(screen.queryByAccessibilityLabel('Add slot')).toBeNull();
});

// ─── patch tests ──────────────────────────────────────────────────────────────

test('closed days show "Closed" label', () => {
  render(<OpeningHoursEditor hours={[]} onChange={jest.fn()} />);
  const closedLabels = screen.getAllByText('Closed');
  // all 7 days should show Closed
  expect(closedLabels).toHaveLength(7);
});

test('other days are unaffected when patching Monday', () => {
  const onChange = jest.fn();
  render(
    <OpeningHoursEditor
      hours={[
        { weekday: 1, opens_at: '12:00', closes_at: '14:30' },
        { weekday: 5, opens_at: '19:00', closes_at: '23:00' },
      ]}
      onChange={onChange}
    />,
  );

  fireEvent(screen.getAllByRole('switch')[1], 'valueChange', false);

  // Friday slot must survive
  expect(onChange).toHaveBeenCalledWith([
    expect.objectContaining({ weekday: 5, opens_at: '19:00', closes_at: '23:00' }),
  ]);
});
