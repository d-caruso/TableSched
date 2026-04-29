jest.mock('tamagui', () => {
  const React = require('react');
  const { View } = require('react-native');

  return {
    Spinner: View,
    YStack: View,
  };
});

const mockReplace = jest.fn();
const mockUseAuth = jest.fn();

jest.mock('expo-router', () => ({
  Slot: () => null,
  useRouter: () => ({ replace: mockReplace }),
  useSegments: () => ['(staff)', 'dashboard'],
}));

jest.mock('@/lib/auth/AuthContext', () => ({
  AuthProvider: ({ children }: any) => children,
  useAuth: () => mockUseAuth(),
}));

import { render, waitFor } from '@testing-library/react-native';
import { expect, jest, test, beforeEach } from '@jest/globals';
import StaffLayout from '@/app/(staff)/_layout';

beforeEach(() => {
  mockReplace.mockReset();
  mockUseAuth.mockReset();
});

test('redirects to login when not authenticated', async () => {
  mockUseAuth.mockReturnValue({ accessToken: null, isLoading: false });

  render(<StaffLayout />);

  await waitFor(() => expect(mockReplace).toHaveBeenCalledWith('/login'));
});

test('does not redirect when authenticated', async () => {
  mockUseAuth.mockReturnValue({ accessToken: 'tok', isLoading: false });

  render(<StaffLayout />);

  await waitFor(() => expect(mockReplace).not.toHaveBeenCalled());
});
