import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Adapt, Select, Sheet, Spinner, Text, YStack } from 'tamagui';
import { useQuery } from '@tanstack/react-query';
import '@/lib/i18n';
import { useAuth } from '@/lib/auth/AuthContext';
import { ApiError } from '@/lib/api/client';
import { AppButton } from '@/components/ui/AppButton';
import { AppInput } from '@/components/ui/AppInput';
import { publicApi } from '@/lib/api/endpoints';
import type { TenantEntry } from '@/lib/api/types';

function TenantField({ value, onChange, tenants }: {
  value: string;
  onChange: (v: string) => void;
  tenants: TenantEntry[];
}) {
  const { t } = useTranslation();

  if (tenants.length === 1) {
    return (
      <YStack gap="$2">
        <Text color="$color" fontSize="$3" fontWeight="$6">{t('staff.login.tenant')}</Text>
        <Text fontSize="$4" paddingVertical="$2">{tenants[0].name}</Text>
      </YStack>
    );
  }

  return (
    <YStack gap="$2">
      <Text color="$color" fontSize="$3" fontWeight="$6">{t('staff.login.tenant')}</Text>
      <Select value={value} onValueChange={onChange}>
        <Select.Trigger>
          <Select.Value placeholder={t('staff.login.tenant')} />
        </Select.Trigger>

        <Adapt when={"sm" as any} platform="touch">
          <Sheet modal dismissOnSnapToBottom>
            <Sheet.Frame>
              <Sheet.ScrollView>
                <Adapt.Contents />
              </Sheet.ScrollView>
            </Sheet.Frame>
            <Sheet.Overlay />
          </Sheet>
        </Adapt>

        <Select.Content>
          <Select.Viewport>
            <Select.Group>
              {tenants.map((tenant, index) => (
                <Select.Item key={tenant.schema} index={index} value={tenant.schema}>
                  <Select.ItemText>{tenant.name}</Select.ItemText>
                </Select.Item>
              ))}
            </Select.Group>
          </Select.Viewport>
        </Select.Content>
      </Select>
    </YStack>
  );
}

export default function StaffLoginScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { login } = useAuth();
  const [tenant, setTenant] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: tenants = [], isLoading: tenantsLoading } = useQuery({
    queryKey: ['tenant-directory'],
    queryFn: (): Promise<TenantEntry[]> => publicApi.tenantDirectory(),
  });

  useEffect(() => {
    if (tenants.length === 1) setTenant(tenants[0].schema);
  }, [tenants]);

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

  if (tenantsLoading) {
    return (
      <YStack flex={1} justifyContent="center" alignItems="center">
        <Spinner size="large" />
      </YStack>
    );
  }

  return (
    <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
      <YStack width="100%" maxWidth={380} gap="$4">
        <Text fontWeight="$7" fontSize="$6">{t('staff.login.title')}</Text>
        <TenantField value={tenant} onChange={setTenant} tenants={tenants} />
        <AppInput
          label={t('staff.login.email')}
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          placeholder={t('staff.login.email')}
        />
        <AppInput
          label={t('staff.login.password')}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          placeholder={t('staff.login.password')}
        />
        {error ? <Text color="$red10">{error}</Text> : null}
        <AppButton onPress={handleLogin} loading={isSubmitting}>
          {t('staff.login.submit')}
        </AppButton>
      </YStack>
    </YStack>
  );
}
