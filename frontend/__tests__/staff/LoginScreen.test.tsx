jest.mock('tamagui', () => {
  const React = require('react');
  const { Text, View, TextInput } = require('react-native');

  return {
    Button: View,
    Input: TextInput,
    Text,
    YStack: View,
  };
});

const mockReplace = jest.fn();
const mockLogin: jest.MockedFunction<(email: string, password: string, tenant: string) => Promise<void>> =
  jest.fn(async () => undefined);

jest.mock('expo-router', () => ({
  useRouter: () => ({ replace: mockReplace }),
}));

jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => ({ login: mockLogin, accessToken: null, tenant: null, isLoading: false }),
}));

import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import LoginScreen from '@/app/(staff)/login';
import { ApiError } from '@/lib/api/client';

test('calls login with email, password and tenant', async () => {
  mockLogin.mockResolvedValueOnce(undefined);
  render(<LoginScreen />);
  fireEvent.changeText(screen.getByLabelText('Restaurant'), 'myrestaurant');
  fireEvent.changeText(screen.getByLabelText('Email'), 'staff@restaurant.it');
  fireEvent.changeText(screen.getByLabelText('Password'), 'secret');
  fireEvent.press(screen.getByText('Sign in'));
  await waitFor(() => expect(mockLogin).toHaveBeenCalledWith('staff@restaurant.it', 'secret', 'myrestaurant'));
  expect(mockReplace).toHaveBeenCalledWith('/dashboard');
});

test('shows error message on login failure', async () => {
  mockLogin.mockRejectedValueOnce(new ApiError(401, 'INVALID_CREDENTIALS'));
  render(<LoginScreen />);
  fireEvent.changeText(screen.getByLabelText('Restaurant'), 'r');
  fireEvent.changeText(screen.getByLabelText('Email'), 'x@x.com');
  fireEvent.changeText(screen.getByLabelText('Password'), 'wrong');
  fireEvent.press(screen.getByText('Sign in'));
  await waitFor(() => expect(screen.getByText('Invalid email or password')).toBeTruthy());
});
