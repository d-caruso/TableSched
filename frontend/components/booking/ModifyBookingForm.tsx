import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { useTranslation } from 'react-i18next';
import { publicApi } from '@/lib/api/endpoints';
import type { Booking } from '@/lib/api/types';
import { DatePicker } from '@/components/booking/DatePicker';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

type ModifyBookingFormProps = {
  tenant: string;
  token: string;
  booking: Booking;
  onDone: () => void;
};

export function ModifyBookingForm({ tenant, token, booking, onDone }: ModifyBookingFormProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [date, setDate] = useState(booking.date);
  const [time] = useState(booking.time);
  const [partySize, setPartySize] = useState(booking.party_size);

  const mutation = useMutation({
    mutationFn: () => publicApi.modifyBooking(tenant, token, { date, time, party_size: partySize }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['booking', token] });
      onDone();
    },
  });

  return (
    <YStack gap="$3">
      {mutation.error ? <ErrorMessage error={mutation.error} /> : null}
      <PartySizeSelector label={t('booking.form.partySize')} value={partySize} onChange={setPartySize} />
      <DatePicker label={t('booking.form.date')} value={date} onChange={setDate} />
      <Button onPress={() => mutation.mutate()} disabled={mutation.isPending}>
        <Text>{t('common.save')}</Text>
      </Button>
      <Button variant="outlined" onPress={onDone}>
        <Text>{t('common.cancel')}</Text>
      </Button>
    </YStack>
  );
}
