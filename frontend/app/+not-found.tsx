import { Text, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';

export default function NotFoundPage() {
  const { t } = useTranslation();
  return (
    <YStack padding="$4">
      <Text>{t('error.notFound')}</Text>
    </YStack>
  );
}
