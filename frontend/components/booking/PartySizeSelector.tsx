import { Pressable, Text, View } from 'react-native';

type PartySizeSelectorProps = {
  label?: string;
  value: number;
  onChange: (value: number) => void;
};

export function PartySizeSelector({ label = 'Party size', value, onChange }: PartySizeSelectorProps) {
  return (
    <View accessibilityLabel={label}>
      <Text>{label}</Text>
      <View style={{ flexDirection: 'row', gap: 12 }}>
        <Pressable
          accessibilityRole="button"
          onPress={() => {
            if (value > 1) {
              onChange(value - 1);
            }
          }}
        >
          <Text>−</Text>
        </Pressable>
        <Text>{value}</Text>
        <Pressable accessibilityRole="button" onPress={() => onChange(value + 1)}>
          <Text>+</Text>
        </Pressable>
      </View>
    </View>
  );
}
