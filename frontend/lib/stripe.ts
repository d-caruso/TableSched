import { loadStripe } from '@stripe/stripe-js';
import { ENV } from './env';

export const stripePromise = loadStripe(ENV.STRIPE_KEY);
