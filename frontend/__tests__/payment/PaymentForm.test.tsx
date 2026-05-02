jest.mock('@stripe/react-stripe-js', () => {
  const confirmPayment = jest.fn(async () => ({ error: null }));

  return {
    PaymentElement: () => null,
    useStripe: () => ({ confirmPayment }),
    useElements: () => ({}),
  };
});

import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { PaymentForm } from '@/components/payment/PaymentForm';

test('calls confirmPayment on submit', async () => {
  const { useStripe } = require('@stripe/react-stripe-js');

  render(<PaymentForm token="tok" />);

  fireEvent.press(screen.getByText('Confirm'));

  await waitFor(() => expect(useStripe().confirmPayment).toHaveBeenCalled());
});

test('displays stripe error message on failure', async () => {
  const { useStripe } = require('@stripe/react-stripe-js');

  useStripe().confirmPayment.mockResolvedValueOnce({ error: { message: 'Card declined' } });

  render(<PaymentForm token="tok" />);

  fireEvent.press(screen.getByText('Confirm'));

  await waitFor(() => expect(screen.getByText('Card declined')).toBeTruthy());
});
