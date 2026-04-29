import { useEffect } from 'react';
import { Slot, useRouter, useSegments } from 'expo-router';
import { Spinner, YStack } from 'tamagui';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';

function Guard() {
  const { accessToken, isLoading } = useAuth();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    if (isLoading) {
      return;
    }

    const isLoginRoute = segments.join('/') === '(staff)/login';

    if (!accessToken && !isLoginRoute) {
      router.replace('/login');
    }

    if (accessToken && isLoginRoute) {
      router.replace('/dashboard');
    }
  }, [accessToken, isLoading, router, segments]);

  if (isLoading) {
    return (
      <YStack flex={1} alignItems="center" justifyContent="center">
        <Spinner size="large" />
      </YStack>
    );
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
