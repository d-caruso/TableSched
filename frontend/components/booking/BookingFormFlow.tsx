import { useMemo, useState } from 'react';
import { Button, Text, YStack } from 'tamagui';

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

function StepDateTime() {
  return (
    <YStack testID="step-datetime" gap="$3">
      <Text fontSize="$5" fontWeight="$6">
        Select date and time
      </Text>
      <Button>Continue</Button>
    </YStack>
  );
}

function StepContact() {
  return (
    <YStack testID="step-contact">
      <Text fontSize="$5" fontWeight="$6">
        Contact details
      </Text>
    </YStack>
  );
}

function StepDone() {
  return (
    <YStack testID="step-done">
      <Text fontSize="$5" fontWeight="$6">
        Done
      </Text>
    </YStack>
  );
}

export function BookingFormFlow({ tenant, restaurant }: BookingFormFlowProps) {
  const [step, setStep] = useState<Step>('datetime');
  const [draft, setDraft] = useState<Draft>({});

  const context = useMemo(
    () => ({ tenant, restaurant, draft, setDraft, step, setStep }),
    [tenant, restaurant, draft, step],
  );

  if (context.step === 'datetime') {
    return <StepDateTime />;
  }

  if (context.step === 'contact') {
    return <StepContact />;
  }

  return <StepDone />;
}
