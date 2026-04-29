import { Pressable, Text, View } from 'react-native';

type PartySizeSelectorProps = {
  value: number;
  onChange: (value: number) => void;
};

export function PartySizeSelector({ value, onChange }: PartySizeSelectorProps) {
  return (
    <View accessibilityLabel="Party size">
      <Text>Party size</Text>
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

