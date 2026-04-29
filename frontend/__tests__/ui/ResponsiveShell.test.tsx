jest.mock('tamagui', () => ({
  ...Object.assign({}, jest.requireActual('tamagui')),
  XStack: require('react-native').View,
  YStack: require('react-native').View,
  useMedia: jest.fn(),
}));

import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { useMedia } from 'tamagui';
import { ResponsiveShell } from '@/components/ui/ResponsiveShell';

test('renders sidebar on wide screens', () => {
  (useMedia as jest.Mock).mockReturnValue({ gtMd: true });
  render(<ResponsiveShell sidebar={<>Sidebar</>} content={<>Content</>} />);
  expect(screen.getByTestId('sidebar-container')).toBeTruthy();
});

test('hides sidebar on narrow screens', () => {
  (useMedia as jest.Mock).mockReturnValue({ gtMd: false });
  render(<ResponsiveShell sidebar={<>Sidebar</>} content={<>Content</>} />);
  expect(screen.queryByTestId('sidebar-container')).toBeNull();
});
