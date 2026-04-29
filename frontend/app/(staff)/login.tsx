import { useState } from 'react';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Button, Input, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { useAuth } from '@/lib/auth/AuthContext';
import { ApiError } from '@/lib/api/client';

export default function StaffLoginScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { login } = useAuth();
  const [tenant, setTenant] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLogin = async () => {
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password, tenant);
      router.replace('/dashboard');
    } catch (cause) {
      const code = cause instanceof ApiError ? cause.code : 'UNKNOWN_ERROR';
      setError(t(`error.${code}`, { defaultValue: t('staff.login.error') }));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <YStack padding="$4" gap="$4">
      <Text fontSize="$6" fontWeight="$7">
        {t('staff.login.title')}
      </Text>
      <Input accessibilityLabel="Restaurant" placeholder={t('staff.login.title')} value={tenant} onChangeText={setTenant} />
      <Input accessibilityLabel="Email" value={email} onChangeText={setEmail} />
      <Input accessibilityLabel="Password" secureTextEntry value={password} onChangeText={setPassword} />
      {error ? <Text color="$red10">{error}</Text> : null}
      <Button onPress={handleLogin} disabled={isSubmitting}>
        <Text>{t('staff.login.submit')}</Text>
      </Button>
    </YStack>
  );
}
