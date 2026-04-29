import { Input, Text, YStack } from 'tamagui';

type DatePickerProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
};

export function DatePicker({ label, value, onChange }: DatePickerProps) {
  return (
    <YStack gap="$2">
      <Text>{label}</Text>
      <Input value={value} onChangeText={onChange} accessibilityLabel={label} />
    </YStack>
  );
}
