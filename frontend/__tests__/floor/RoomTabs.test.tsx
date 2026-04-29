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
import { RoomTabs } from '@/components/floor/RoomTabs';

const rooms = [
  { id: 'r1', name: 'Main', tables: [] },
  { id: 'r2', name: 'Terrace', tables: [] },
];

test('renders a tab per room', () => {
  render(<RoomTabs rooms={rooms} activeId="r1" onSelect={jest.fn()} />);
  expect(screen.getByText('Main')).toBeTruthy();
  expect(screen.getByText('Terrace')).toBeTruthy();
});

test('calls onSelect with correct room id', () => {
  const onSelect = jest.fn();
  render(<RoomTabs rooms={rooms} activeId="r1" onSelect={onSelect} />);
  fireEvent.press(screen.getByText('Terrace'));
  expect(onSelect).toHaveBeenCalledWith('r2');
});
