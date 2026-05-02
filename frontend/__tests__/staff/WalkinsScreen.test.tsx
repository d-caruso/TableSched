jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) =>
      ({
        'staff.walkins.title': 'Walk-ins',
        'staff.walkins.submit': 'Add walk-in',
        'staff.walkins.success': 'Walk-in added',
      })[key] ?? key,
  }),
}));

jest.mock('@/lib/i18n', () => ({}));

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    createWalkin: jest.fn(),
  },
}));

jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => ({ accessToken: 'tok', tenant: 'r' }),
}));

jest.mock('@/components/ui/AppButton', () => {
  const React = require('react');
  const { Pressable, Text } = require('react-native');
  return {
    AppButton: ({ children, onPress, ...props }: any) => (
      <Pressable accessibilityRole="button" accessibilityLabel={String(children)} onPress={onPress} {...props}>
        <Text>{children}</Text>
      </Pressable>
    ),
  };
});

import { expect, jest, test } from '@jest/globals';
import { staffApi } from '@/lib/api/endpoints';
import { submitWalkin } from '@/app/(staff)/dashboard/walkins';

test('calls createWalkin with selected party size', async () => {
  const createWalkin = staffApi.createWalkin as jest.MockedFunction<(...args: any[]) => Promise<unknown>>;
  createWalkin.mockResolvedValueOnce({ id: 'w1' });
  await submitWalkin('r', 'tok', 3);
  expect(createWalkin).toHaveBeenCalledWith('r', 'tok', { party_size: 3 });
});
