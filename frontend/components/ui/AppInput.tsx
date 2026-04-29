import type { ComponentProps } from 'react';
import { Input, Text, YStack } from 'tamagui';

type AppInputProps = ComponentProps<typeof Input> & {
  label: string;
};

export function AppInput({ label, ...props }: AppInputProps) {
  return (
    <YStack gap="$2">
      <Text color="$color" fontSize="$3" fontWeight="$6">
        {label}
      </Text>
      <Input borderRadius="$4" {...props} />
    </YStack>
  );
}
