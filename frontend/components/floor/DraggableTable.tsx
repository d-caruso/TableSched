import { useMemo } from 'react';
import { Pressable, Text, View } from 'react-native';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, {
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
} from 'react-native-reanimated';
import type { Table } from '@/lib/api/types';

type Props = {
  table: Table;
  onDrop: (x: number, y: number) => void;
};

const TABLE_WIDTH = 96;
const TABLE_HEIGHT = 64;

export function DraggableTable({ table, onDrop }: Props) {
  const initialX = table.x ?? 0;
  const initialY = table.y ?? 0;
  const x = useSharedValue(initialX);
  const y = useSharedValue(initialY);
  const startX = useSharedValue(initialX);
  const startY = useSharedValue(initialY);

  const gesture = useMemo(
    () =>
      Gesture.Pan()
        .onBegin(() => {
          startX.value = x.value;
          startY.value = y.value;
        })
        .onUpdate(event => {
          x.value = startX.value + event.translationX;
          y.value = startY.value + event.translationY;
        })
        .onEnd(() => {
          runOnJS(onDrop)(Math.round(x.value), Math.round(y.value));
        }),
    [onDrop, startX, startY, x, y],
  );

  const style = useAnimatedStyle(() => ({
    position: 'absolute' as const,
    left: x.value,
    top: y.value,
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View
        accessibilityRole="button"
        style={[
          {
            width: TABLE_WIDTH,
            height: TABLE_HEIGHT,
          },
          style,
        ]}
      >
        <View style={{ flex: 1, borderRadius: 12, backgroundColor: '#111827', justifyContent: 'center', alignItems: 'center' }}>
          <Text style={{ color: 'white', fontWeight: '600' }}>{table.name}</Text>
          <Text style={{ color: 'white' }}>{`${table.capacity}p`}</Text>
        </View>
      </Animated.View>
    </GestureDetector>
  );
}
