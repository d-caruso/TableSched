import { Text, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { ApiError } from '@/lib/api/client';

type ErrorMessageProps = {
  error?: ApiError | null;
};

function toTranslationKey(code: string) {
  return code.toLowerCase().replace(/[^a-z0-9]+/g, '_');
}

export function ErrorMessage({ error }: ErrorMessageProps) {
  const { t } = useTranslation();

  if (!error) {
    return null;
  }

  const key = `error.${toTranslationKey(error.code)}`;
  const message = t(key, { defaultValue: t('common.error') });

  return (
    <YStack
      backgroundColor="$danger"
      borderRadius="$4"
      padding="$3"
    >
      <Text color="$background" fontSize="$3" fontWeight="$6">
        {message}
      </Text>
    </YStack>
  );
}
