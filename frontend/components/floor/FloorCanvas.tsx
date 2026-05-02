import { useMutation, useQueryClient } from '@tanstack/react-query';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { FLEX_ONE } from '@/constants/styles';
import { Stack, YStack } from 'tamagui';
import { DraggableTable } from '@/components/floor/DraggableTable';
import { staffApi } from '@/lib/api/endpoints';
import type { Room } from '@/lib/api/types';

type Props = {
  room: Room;
  tenant: string;
  token: string;
};

export function FloorCanvas({ room, tenant, token }: Props) {
  const queryClient = useQueryClient();

  const updatePosition = useMutation({
    mutationFn: ({
      tableId,
      x,
      y,
    }: {
      tableId: string;
      x: number;
      y: number;
    }) => staffApi.updateTablePosition(tenant, token, tableId, x, y),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['staff-rooms', tenant] });
    },
  });

  return (
    // GestureHandlerRootView has no Tamagui equivalent — kept as-is
    <GestureHandlerRootView style={FLEX_ONE}>
      <YStack
        minHeight={320}
        borderRadius="$4"
        backgroundColor="$backgroundHover"
        position="relative"
        overflow="hidden"
      >
        {(room.tables ?? []).map(table => (
          <DraggableTable
            key={table.id}
            table={table}
            onDrop={(x, y) => updatePosition.mutate({ tableId: table.id, x, y })}
          />
        ))}
      </YStack>
    </GestureHandlerRootView>
  );
}
