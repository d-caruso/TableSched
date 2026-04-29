import { Redirect, Slot, useSegments } from 'expo-router';
import { Spinner, YStack } from 'tamagui';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';

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
