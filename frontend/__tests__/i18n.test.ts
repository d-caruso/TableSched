import { expect, test } from '@jest/globals';
import i18n from '@/lib/i18n';

test('all en keys are present in it and de', () => {
  const enKeys = Object.keys(i18n.getResourceBundle('en', 'translation'));
  const itKeys = Object.keys(i18n.getResourceBundle('it', 'translation'));
  const deKeys = Object.keys(i18n.getResourceBundle('de', 'translation'));

  enKeys.forEach((key) => {
    expect(itKeys).toContain(key);
    expect(deKeys).toContain(key);
  });
});

test('booking status keys resolve in en', () => {
  const statuses = [
    'pending_review',
    'pending_payment',
    'confirmed',
    'declined',
  ];

  statuses.forEach((status) => {
    expect(i18n.t(`booking.status.${status}`)).toBeTruthy();
  });
});
