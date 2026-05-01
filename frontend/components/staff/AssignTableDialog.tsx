import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Input, YStack, Text } from 'tamagui';
import { AppButton } from '@/components/ui/AppButton';

type AssignTableDialogProps = {
  onSubmit: (tableId: string) => void;
  loading?: boolean;
};

export function AssignTableDialog({ onSubmit, loading = false }: AssignTableDialogProps) {
  const { t } = useTranslation();
  const [tableId, setTableId] = useState('');

  return (
    <YStack gap="$3">
      <Text>{t('staff.booking.assignTable')}</Text>
      <Input
        accessibilityLabel={t('booking.detail.table')}
        value={tableId}
        onChangeText={setTableId}
        placeholder={t('staff.booking.tableId')}
      />
      <AppButton onPress={() => onSubmit(tableId)} loading={loading} disabled={!tableId.trim()}>
        {t('common.submit')}
      </AppButton>
    </YStack>
  );
}
