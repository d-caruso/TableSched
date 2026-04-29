import { Pressable, Text, View } from 'react-native';

export type TimeSlotItem = {
  time: string;
  available: boolean;
  busy_warning?: boolean;
};

type TimeSlotGridProps = {
  slots: TimeSlotItem[];
  loading: boolean;
  selected: string;
  onSelect: (time: string) => void;
};

export function TimeSlotGrid({ slots, loading, selected, onSelect }: TimeSlotGridProps) {
  if (loading) {
    return (
      <View>
        <Text>Loading</Text>
      </View>
    );
  }

  return (
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
      {slots.map((slot) =>
        slot.available ? (
          <Pressable key={slot.time} accessibilityRole="button" onPress={() => onSelect(slot.time)}>
            <Text>{slot.time}</Text>
            {slot.busy_warning ? <Text>!</Text> : null}
            {selected === slot.time ? <Text>Selected</Text> : null}
          </Pressable>
        ) : (
          <View key={slot.time}>
            <Text>{slot.time}</Text>
            {slot.busy_warning ? <Text>!</Text> : null}
          </View>
        ),
      )}
    </View>
  );
}

