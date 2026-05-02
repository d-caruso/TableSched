import { useMutation, useQueryClient } from '@tanstack/react-query';
import { StyleSheet, View } from 'react-native';

const styles = StyleSheet.create({
  root: { flex: 1 },
  canvas: {
    minHeight: 320,
    borderRadius: 16,
    backgroundColor: '#f3f4f6',
    position: 'relative',
    overflow: 'hidden',
  },
});
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
    <GestureHandlerRootView style={styles.root}>
      <View style={styles.canvas}>
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
