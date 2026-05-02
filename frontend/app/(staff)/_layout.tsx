import { Redirect, Slot, useSegments } from 'expo-router';
import { Spinner, YStack } from 'tamagui';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';
import { ENV } from '@/lib/env';

function Guard() {
  const { accessToken, isLoading } = useAuth();
  const segments = useSegments();

  if (isLoading) {
    return (
      <YStack flex={1} alignItems="center" justifyContent="center">
        <Spinner size="large" />
      </YStack>
    );
  }

  // SHOWCASE MODE: auth guard is disabled when SHOW_TENANT_DIRECTORY is true.
  // Re-enable by removing this block once login is working.
  if (ENV.SHOW_TENANT_DIRECTORY) {
    return <Slot />;
  }

  // Normal auth guard — restore this block when login is working:
  // const isLoginRoute = segments.join('/') === '(staff)/login';
  // if (!accessToken && !isLoginRoute) {
  //   return <Redirect href="/login" />;
  // }
  // if (accessToken && isLoginRoute) {
  //   return <Redirect href="/dashboard" />;
  // }

  const isLoginRoute = segments.join('/') === '(staff)/login';
  if (!accessToken && !isLoginRoute) {
    return <Redirect href="/login" />;
  }
  if (accessToken && isLoginRoute) {
    return <Redirect href="/dashboard" />;
  }

  return <Slot />;
}

export default function StaffLayout() {
  return (
    <AuthProvider>
      <Guard />
    </AuthProvider>
  );
}
