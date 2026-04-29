jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) =>
      ({
        'staff.settings.depositPolicy': 'Deposit policy',
        'staff.settings.depositModes.never': 'Never',
        'staff.settings.depositModes.always': 'Always',
        'staff.settings.depositModes.by_party_size': 'By party size',
        'staff.settings.minPartySize': 'Min party size',
      })[key] ?? key,
  }),
}));

jest.mock('@/lib/i18n', () => ({}));

jest.mock('@/components/ui/AppButton', () => {
  const React = require('react');
  const { Pressable, Text } = require('react-native');

  return {
    AppButton: ({ children, onPress, ...props }: any) => (
      <Pressable accessibilityRole="button" onPress={onPress} {...props}>
        <Text>{children}</Text>
      </Pressable>
    ),
  };
});

jest.mock('@/components/ui/AppInput', () => {
  const React = require('react');
  const { TextInput, Text, View } = require('react-native');

  return {
    AppInput: ({ label, ...props }: any) => (
      <View>
        <Text>{label}</Text>
        <TextInput accessibilityLabel={label} {...props} />
      </View>
    ),
  };
});

import { fireEvent, render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { DepositPolicyEditor } from '@/components/settings/DepositPolicyEditor';

test('selecting always calls onChange with mode always', () => {
  const onChange = jest.fn();
  render(<DepositPolicyEditor policy={{ mode: 'never' }} onChange={onChange} />);

  fireEvent.press(screen.getByText('Always'));

  expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ mode: 'always' }));
});

test('min_party_size input is hidden when mode is never', () => {
  render(<DepositPolicyEditor policy={{ mode: 'never' }} onChange={jest.fn()} />);

  expect(screen.queryByText('Min party size')).toBeNull();
});

test('min_party_size input is visible when mode is by_party_size', () => {
  render(<DepositPolicyEditor policy={{ mode: 'by_party_size', min_party_size: 4 }} onChange={jest.fn()} />);

  expect(screen.getByText('Min party size')).toBeTruthy();
});
