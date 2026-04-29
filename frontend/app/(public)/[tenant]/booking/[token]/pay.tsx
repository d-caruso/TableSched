import { useLocalSearchParams } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Elements } from '@stripe/react-stripe-js';
import { Spinner, Text, YStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { PaymentForm } from '@/components/payment/PaymentForm';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { publicApi } from '@/lib/api/endpoints';
import { stripePromise } from '@/lib/stripe';

export default function CustomerBookingPayPage() {
  const { token } = useLocalSearchParams<{ tenant: string; token: string }>();
  const { t } = useTranslation();
  const tokenValue = Array.isArray(token) ? token[0] : token;

  const { data, isLoading, error } = useQuery({
    queryKey: ['payment-intent', tokenValue],
    queryFn: () => publicApi.getPaymentIntent(tokenValue),
    enabled: !!tokenValue,
  });

  if (isLoading) {
    return (
      <YStack padding="$4">
        <Spinner />
      </YStack>
    );
  }

  if (error || !data) {
    return (
      <YStack padding="$4">
        <ErrorMessage error={error} />
      </YStack>
    );
  }

  return (
    <YStack padding="$4" gap="$4">
      <Text>{t('booking.actions.pay')}</Text>
      <Elements stripe={stripePromise} options={{ clientSecret: data.client_secret }}>
        <PaymentForm token={tokenValue} />
      </Elements>
    </YStack>
  );
}
