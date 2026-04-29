import { Button, Input, Text, XStack, YStack } from 'tamagui';

type PartySizeSelectorProps = {
  label: string;
  value: number;
  onChange: (value: number) => void;
};

export function PartySizeSelector({ label, value, onChange }: PartySizeSelectorProps) {
  return (
    <YStack gap="$2">
      <Text>{label}</Text>
      <XStack gap="$2" alignItems="center">
        <Button onPress={() => onChange(Math.max(1, value - 1))}>
          <Text>-</Text>
        </Button>
        <Input
          value={String(value)}
          onChangeText={(next) => {
            const parsed = Number.parseInt(next, 10);
            if (!Number.isNaN(parsed)) onChange(parsed);
          }}
          keyboardType="number-pad"
          accessibilityLabel={label}
          width="$10"
          textAlign="center"
        />
        <Button onPress={() => onChange(value + 1)}>
          <Text>+</Text>
        </Button>
      </XStack>
    </YStack>
  );
}
