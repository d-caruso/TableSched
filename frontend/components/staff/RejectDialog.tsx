import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { YStack, Text, Input } from 'tamagui';
import { AppButton } from '@/components/ui/AppButton';

type RejectDialogProps = {
  onSubmit: (reason: string) => void;
  loading?: boolean;
};

export function RejectDialog({ onSubmit, loading = false }: RejectDialogProps) {
  const { t } = useTranslation();
  const [reason, setReason] = useState('');

  return (
    <YStack gap="$3">
      <Text>{t('staff.booking.reject')}</Text>
      <Input
        accessibilityLabel={t('staff.booking.rejectReason')}
        value={reason}
        onChangeText={setReason}
        placeholder={t('staff.booking.rejectReason')}
      />
      <AppButton onPress={() => onSubmit(reason)} loading={loading} disabled={!reason.trim()}>
        {t('common.submit')}
      </AppButton>
    </YStack>
  );
}
