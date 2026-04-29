import { useMemo, useState } from 'react';
import { Text, YStack } from 'tamagui';
import { StepDateTime } from '@/components/booking/steps/StepDateTime';
import { StepContact } from '@/components/booking/steps/StepContact';
import { StepDone } from '@/components/booking/steps/StepDone';

export type Draft = {
  date?: string;
  time?: string;
  party_size?: number;
  name?: string;
  phone?: string;
  email?: string;
  locale?: string;
  notes?: string;
};

export type Step = 'datetime' | 'contact' | 'done';

type BookingFormFlowProps = {
  tenant: string;
  restaurant: {
    slug?: string;
    name: string;
    opening_hours?: unknown[];
    deposit_policy?: { mode: string };
    cancellation_cutoff_hours?: number;
  };
};

export function BookingFormFlow({ tenant, restaurant }: BookingFormFlowProps) {
  const [step, setStep] = useState<Step>('datetime');
  const [draft, setDraft] = useState<Draft>({});

  const context = useMemo(
    () => ({ tenant, restaurant, draft, setDraft, step, setStep }),
    [tenant, restaurant, draft, step],
  );

  if (context.step === 'datetime') {
    return (
      <StepDateTime
        tenant={tenant}
        restaurant={restaurant}
        onContinue={() => setStep('contact')}
      />
    );
  }

  if (context.step === 'contact') {
    return (
      <StepContact
        draft={draft}
        tenant={tenant}
        onBack={() => setStep('datetime')}
        onNext={(nextDraft) => {
          setDraft((current) => ({ ...current, ...nextDraft }));
          setStep('done');
        }}
      />
    );
  }

  return <StepDone tenant={tenant} draft={draft} onDone={() => setStep('done')} />;
}
