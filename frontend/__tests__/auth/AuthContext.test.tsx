import { act, renderHook, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    login: jest.fn(async () => ({ access: 'tok-access', refresh: 'tok-refresh' })),
  },
}));

test('login stores access token', async () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  const { result } = renderHook(() => useAuth(), { wrapper });

  await waitFor(() => expect(result.current.isLoading).toBe(false));

  await act(async () => {
    await result.current.login('a@b.com', 'pass', 'tenant1');
  });

  expect(result.current.accessToken).toBe('tok-access');
  expect(result.current.tenant).toBe('tenant1');
});

test('logout clears token', async () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  const { result } = renderHook(() => useAuth(), { wrapper });

  await waitFor(() => expect(result.current.isLoading).toBe(false));

  await act(async () => {
    await result.current.login('a@b.com', 'pass', 'tenant1');
    await result.current.logout();
  });

  expect(result.current.accessToken).toBeNull();
  expect(result.current.tenant).toBeNull();
});
