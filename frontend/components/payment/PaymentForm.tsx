import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useElements, useStripe, PaymentElement } from '@stripe/react-stripe-js';
import { Button, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { ROUTES } from '@/constants/routes';

type PaymentFormProps = {
  token: string;
};

export function PaymentForm({ token }: PaymentFormProps) {
  const { t } = useTranslation();
  const stripe = useStripe();
  const elements = useElements();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!stripe || !elements) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    const result = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}${ROUTES.bookingDetail(token)}`,
      },
    });

    if (result.error) {
      setErrorMessage(result.error.message ?? t('common.error'));
    }

    setIsSubmitting(false);
  };

  return (
    <YStack gap="$3">
      <PaymentElement />
      {errorMessage ? <Text color="$red10">{errorMessage}</Text> : null}
      <Button onPress={handleSubmit} disabled={!stripe || !elements || isSubmitting}>
        <Text>{t('common.confirm')}</Text>
      </Button>
    </YStack>
  );
}
