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
      <Input accessibilityLabel="Table" value={tableId} onChangeText={setTableId} placeholder="Table ID" />
      <AppButton onPress={() => onSubmit(tableId)} loading={loading} disabled={!tableId.trim()}>
        {t('common.submit')}
      </AppButton>
    </YStack>
  );
}
