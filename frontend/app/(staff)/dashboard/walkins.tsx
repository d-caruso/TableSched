import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';
import { AppButton } from '@/components/ui/AppButton';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { useAuth } from '@/lib/auth/AuthContext';
import { staffApi } from '@/lib/api/endpoints';

export async function submitWalkin(tenant: string, token: string, partySize: number) {
  return staffApi.createWalkin(tenant, token, { party_size: partySize });
}

export default function WalkinsScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const [partySize, setPartySize] = useState(2);
  const [success, setSuccess] = useState(false);
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    if (!success) return;

    const timer = setTimeout(() => {
      setSuccess(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, [success]);

  const handleSubmit = async () => {
    setIsPending(true);
    setError(null);

    try {
      await submitWalkin(tenant!, accessToken!, partySize);
      setSuccess(true);
    } catch (cause) {
      setError(cause);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <YStack padding="$4" gap="$4">
      <Text fontSize="$6" fontWeight="$7">
        {t('staff.walkins.title')}
      </Text>
      <PartySizeSelector value={partySize} onChange={setPartySize} />
      {error ? <ErrorMessage error={error} /> : null}
      {success ? <Text color="$green10">{t('staff.walkins.success')}</Text> : null}
      <AppButton testID="walkin-submit" onPress={handleSubmit} loading={isPending}>
        {t('staff.walkins.submit')}
      </AppButton>
    </YStack>
  );
}
