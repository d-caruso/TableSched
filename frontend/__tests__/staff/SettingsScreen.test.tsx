jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View } = require('react-native');

  return {
    ScrollView: View,
    Spinner: View,
    Text,
    YStack: View,
  };
});

const mockInvalidateQueries = jest.fn();
const mockMutate = jest.fn();

jest.mock('@tanstack/react-query', () => ({
  useQuery: () => ({
    data: {
      slug: 'r',
      name: 'Test',
      opening_hours: [],
      deposit_policy: { mode: 'never' },
      cancellation_cutoff_hours: 24,
    },
    isLoading: false,
    error: null,
  }),
  useMutation: () => ({
    mutate: mockMutate,
    isPending: false,
    error: null,
  }),
  useQueryClient: () => ({
    invalidateQueries: mockInvalidateQueries,
  }),
}));

jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => ({ accessToken: 'tok', tenant: 'r' }),
}));

jest.mock('@/components/ui/AppButton', () => {
  const React = require('react');
  const { Pressable, Text } = require('react-native');

  return {
    AppButton: ({ children, disabled, ...props }: any) => (
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={String(children)}
        accessibilityState={{ disabled: Boolean(disabled) }}
        disabled={disabled}
        {...props}
      >
        <Text>{children}</Text>
      </Pressable>
    ),
  };
});

import { render, screen, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import SettingsScreen from '@/app/(staff)/dashboard/settings';

test('renders settings title', async () => {
  render(<SettingsScreen />);
  await waitFor(() => expect(screen.getByText('Settings')).toBeTruthy());
});

test('save button is disabled when no changes made', async () => {
  render(<SettingsScreen />);
  await waitFor(() => expect(screen.getByRole('button', { name: 'Save' }).props.accessibilityState?.disabled).toBe(true));
});
