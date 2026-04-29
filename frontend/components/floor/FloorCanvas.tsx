import { useMutation, useQueryClient } from '@tanstack/react-query';
import { View } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
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
    <GestureHandlerRootView style={{ flex: 1 }}>
      <View
        style={{
          minHeight: 320,
          borderRadius: 16,
          backgroundColor: '#f3f4f6',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {(room.tables ?? []).map(table => (
          <DraggableTable
            key={table.id}
            table={table}
            onDrop={(x, y) => updatePosition.mutate({ tableId: table.id, x, y })}
          />
        ))}
      </View>
    </GestureHandlerRootView>
  );
}
