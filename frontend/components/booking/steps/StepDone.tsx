import { useEffect, useRef, useState } from 'react';
import { Text, View } from 'react-native';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { publicApi } from '@/lib/api/endpoints';
import type { Draft } from '@/components/booking/BookingFormFlow';

type StepDoneProps = {
  tenant: string;
  draft: Draft;
  onDone?: () => void;
};

export function StepDone({ tenant, draft, onDone }: StepDoneProps) {
  const { t } = useTranslation();
  const fired = useRef(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    if (fired.current) return;
    fired.current = true;

    void (async () => {
      try {
        await publicApi.createBooking(tenant, {
          date: draft.date ?? '',
          time: draft.time ?? '',
          party_size: draft.party_size ?? 1,
          name: draft.name ?? '',
          phone: draft.phone ?? '',
          email: draft.email,
          notes: draft.notes,
        });
        setIsSuccess(true);
        onDone?.();
      } catch {
        setError(t('common.error'));
      } finally {
        setIsLoading(false);
      }
    })();
  }, [draft, onDone, t, tenant]);

  return (
    <View testID="step-done">
      {isLoading ? <Text>{t('common.loading')}</Text> : null}
      {isSuccess ? <Text>{t('booking.page.booking_confirmed')}</Text> : null}
      {error ? <Text>{error}</Text> : null}
    </View>
  );
}
