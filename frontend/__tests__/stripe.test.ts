jest.mock('@stripe/stripe-js', () => ({
  loadStripe: jest.fn(() => Promise.resolve({})),
}));

jest.mock('@/lib/env', () => ({
  ENV: { STRIPE_KEY: 'pk_test_stub' },
}));

import { expect, jest, test } from '@jest/globals';

test('stripePromise calls loadStripe with env key', async () => {
  const { loadStripe } = require('@stripe/stripe-js');

  require('@/lib/stripe');

  expect(loadStripe).toHaveBeenCalledWith('pk_test_stub');
});
