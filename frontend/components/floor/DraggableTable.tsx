import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, { type StyleProps,
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
} from 'react-native-reanimated';
import { Text, YStack } from 'tamagui';
import type { Table } from '@/lib/api/types';

type Props = {
  table: Table;
  onDrop: (x: number, y: number) => void;
};

const TABLE_WIDTH = 96;
const TABLE_HEIGHT = 64;

const animatedStyle: StyleProps = {
  position: 'absolute',
  width: TABLE_WIDTH,
  height: TABLE_HEIGHT,
};

export function DraggableTable({ table, onDrop }: Props) {
  const { t } = useTranslation();
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

  const reanimatedStyle = useAnimatedStyle(() => ({
    left: x.value,
    top: y.value,
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View
        accessibilityRole="button"
        style={[animatedStyle, reanimatedStyle]}
      >
        <YStack
          flex={1}
          borderRadius="$4"
          backgroundColor="$color12"
          justifyContent="center"
          alignItems="center"
        >
          <Text color="$background" fontWeight="600">{table.name}</Text>
          <Text color="$background">{t('floor.tableCapacity', { count: table.capacity })}</Text>
        </YStack>
      </Animated.View>
    </GestureDetector>
  );
}
