import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Input, YStack, Text } from 'tamagui';
import { AppButton } from '@/components/ui/AppButton';
import type { Booking } from '@/lib/api/types';

type Props = {
  booking: Booking;
  onSubmit: (payload: { party_size?: number; notes?: string }) => void;
  onClose: () => void;
  loading?: boolean;
};

export function StaffModifyDialog({ booking, onSubmit, onClose, loading = false }: Props) {
  const { t } = useTranslation();
  const [partySize, setPartySize] = useState(String(booking.party_size));
  const [notes, setNotes] = useState(booking.notes ?? '');

  const handleSubmit = () => {
    const parsed = parseInt(partySize, 10);
    onSubmit({
      party_size: isNaN(parsed) ? undefined : parsed,
      notes: notes || undefined,
    });
  };

  return (
    <YStack gap="$3">
      <Text>{t('staff.booking.modify')}</Text>
      <Input
        accessibilityLabel="Party size"
        value={partySize}
        onChangeText={setPartySize}
        keyboardType="numeric"
      />
      <Input
        accessibilityLabel="Notes"
        value={notes}
        onChangeText={setNotes}
      />
      <AppButton onPress={handleSubmit} loading={loading}>
        {t('common.save')}
      </AppButton>
      <AppButton variant="secondary" onPress={onClose}>
        {t('common.cancel')}
      </AppButton>
    </YStack>
  );
}
