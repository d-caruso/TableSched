import { useTranslation } from 'react-i18next';
import { Text, View } from 'react-native';
import '@/lib/i18n';
import { AppButton } from '@/components/ui/AppButton';
import { AppInput } from '@/components/ui/AppInput';
import type { DepositPolicy } from '@/lib/api/types';

type Props = {
  policy: DepositPolicy;
  onChange: (policy: DepositPolicy) => void;
};

const MODES: DepositPolicy['mode'][] = ['never', 'always', 'by_party_size'];

function nextPolicy(policy: DepositPolicy, mode: DepositPolicy['mode']): DepositPolicy {
  if (mode === 'by_party_size') {
    return {
      mode,
      min_party_size: policy.min_party_size ?? 4,
    };
  }

  return { mode };
}

export function DepositPolicyEditor({ policy, onChange }: Props) {
  const { t } = useTranslation();

  return (
    <View>
      <Text>{t('staff.settings.depositPolicy')}</Text>
      <View>
        {MODES.map(mode => (
          <AppButton
            key={mode}
            variant={policy.mode === mode ? 'primary' : 'secondary'}
            onPress={() => onChange(nextPolicy(policy, mode))}
          >
            {t(`staff.settings.depositModes.${mode}`)}
          </AppButton>
        ))}
      </View>
      {policy.mode === 'by_party_size' ? (
        <AppInput
          label={t('staff.settings.minPartySize')}
          value={String(policy.min_party_size ?? '')}
          keyboardType="number-pad"
          onChangeText={value => {
            const parsed = Number.parseInt(value, 10);
            onChange({
              mode: 'by_party_size',
              min_party_size: Number.isFinite(parsed) ? parsed : undefined,
            });
          }}
        />
      ) : null}
    </View>
  );
}
