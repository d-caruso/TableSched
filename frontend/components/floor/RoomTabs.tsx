import { Pressable } from 'react-native';
import { Text, XStack } from 'tamagui';
import type { Room } from '@/lib/api/types';

type Props = {
  rooms: Room[];
  activeId: string;
  onSelect: (id: string) => void;
};

export function RoomTabs({ rooms, activeId, onSelect }: Props) {
  return (
    <XStack borderBottomWidth={1} borderColor="$borderColor" paddingHorizontal="$4">
      {rooms.map(room => {
        const selected = room.id === activeId;

        return (
          <Pressable
            key={room.id}
            accessibilityRole="tab"
            accessibilityState={{ selected }}
            onPress={() => onSelect(room.id)}
          >
            <XStack
              paddingVertical="$3"
              paddingHorizontal="$3"
              borderBottomWidth={2}
              borderColor={selected ? '$color' : 'transparent'}
            >
              <Text fontWeight={selected ? '700' : '400'}>{room.name}</Text>
            </XStack>
          </Pressable>
        );
      })}
    </XStack>
  );
}
