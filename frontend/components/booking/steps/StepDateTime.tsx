import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Stack, Text, YStack } from 'tamagui';
import { publicApi } from '@/lib/api/endpoints';
import { DatePicker } from '@/components/booking/DatePicker';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';
import { TimeSlotGrid, type TimeSlotItem } from '@/components/booking/TimeSlotGrid';

type StepDateTimeProps = {
  tenant: string;
  restaurant: {
    name: string;
  };
  onContinue?: () => void;
};

function toIsoDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

function toQuarterHourTimes() {
  const slots: string[] = [];
  for (let minutes = 0; minutes < 24 * 60; minutes += 15) {
    const hours = String(Math.floor(minutes / 60)).padStart(2, '0');
    const mins = String(minutes % 60).padStart(2, '0');
    slots.push(`${hours}:${mins}`);
  }
  return slots;
}

export function StepDateTime({ tenant, restaurant, onContinue }: StepDateTimeProps) {
  const { t } = useTranslation();
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [partySize, setPartySize] = useState(2);
  const [slots, setSlots] = useState<TimeSlotItem[]>([]);
  const [loading, setLoading] = useState(false);

  const allSlots = useMemo(toQuarterHourTimes, []);

  useEffect(() => {
    if (!date) {
      setSlots([]);
      setTime('');
      return;
    }

    let cancelled = false;
    setLoading(true);

    void (async () => {
      try {
        const available = await publicApi.getAvailableSlots(tenant, date);
        if (cancelled) return;

        const byTime = new Map(
          available.map((slot) => [
            slot.time,
            { available: slot.available, busy_warning: (slot as TimeSlotItem).busy_warning ?? false },
          ]),
        );
        setSlots(
          allSlots.map((slotTime) => ({
            time: slotTime,
            available: byTime.get(slotTime)?.available ?? false,
            busy_warning: byTime.get(slotTime)?.busy_warning ?? false,
          })),
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [allSlots, date, tenant]);

  const canContinue = !!date && !!time;

  return (
    <YStack testID="step-datetime">
      <Text>{restaurant.name}</Text>
      <DatePicker label={t('booking.form.date')} value={date} onChange={setDate} minDate={toIsoDate(new Date())} maxDays={90} />
      <PartySizeSelector label={t('booking.form.partySize')} value={partySize} onChange={setPartySize} />
      <TimeSlotGrid slots={slots} loading={loading} selected={time} onSelect={setTime} />
      <Stack
        accessibilityRole="button"
        onPress={canContinue ? onContinue : undefined}
        opacity={canContinue ? 1 : 0.4}
        pressStyle={{ opacity: 0.7 }}
      >
        <Text>{t('common.continue')}</Text>
      </Stack>
    </YStack>
  );
}
