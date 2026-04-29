jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    Text,
    XStack: View,
  };
});

import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { FilterTabs } from '@/components/staff/FilterTabs';

test('calls onSelect with correct index', () => {
  const onSelect = jest.fn();

  render(<FilterTabs labels={['All', 'Pending', 'Confirmed']} selected={0} onSelect={onSelect} />);

  fireEvent.press(screen.getByText('Pending'));

  expect(onSelect).toHaveBeenCalledWith(1);
});

test('highlights selected tab', () => {
  render(<FilterTabs labels={['All', 'Pending']} selected={1} onSelect={jest.fn()} />);

  expect(screen.getByRole('tab', { selected: true })).toBeTruthy();
});
