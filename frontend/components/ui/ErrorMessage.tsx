import { Text, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import { ApiError } from '@/lib/api/client';

function toTranslationKey(code: string) {
  return code.toLowerCase().replace(/[^a-z0-9]+/g, '_');
}

export function ErrorMessage({ error }: { error: unknown }) {
  const { t } = useTranslation();
  const code = error instanceof ApiError ? error.code : 'UNKNOWN_ERROR';

  return (
    <YStack padding="$3" backgroundColor="$red8" borderRadius="$3" opacity={0.9}>
      <Text color="white">{t(`error.${toTranslationKey(code)}`, { defaultValue: t('common.error') })}</Text>
    </YStack>
  );
}
