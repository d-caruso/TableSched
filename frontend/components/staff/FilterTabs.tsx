import { PRESS_STYLE } from '@/constants/styles';
import { Stack, Text, XStack } from 'tamagui';

type FilterTabsProps = {
  labels: string[];
  selected: number;
  onSelect: (index: number) => void;
};

export function FilterTabs({ labels, selected, onSelect }: FilterTabsProps) {
  return (
    <XStack borderBottomWidth={1} borderColor="$borderColor" paddingHorizontal="$4">
      {labels.map((label, index) => {
        const isSelected = index === selected;

        return (
          <Stack
            key={label}
            accessibilityRole="tab"
            accessibilityState={{ selected: isSelected }}
            onPress={() => onSelect(index)}
            pressStyle={PRESS_STYLE}
          >
            <XStack paddingVertical="$3" paddingHorizontal="$3" borderBottomWidth={2} borderColor={isSelected ? '$color' : 'transparent'}>
              <Text fontWeight={isSelected ? '700' : '400'}>{label}</Text>
            </XStack>
          </Stack>
        );
      })}
    </XStack>
  );
}
