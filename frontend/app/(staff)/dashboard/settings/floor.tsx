import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { ScrollView, Spinner, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { RoomTabs } from '@/components/floor/RoomTabs';
import { useAuth } from '@/lib/auth/AuthContext';
import { staffApi } from '@/lib/api/endpoints';
import type { Room } from '@/lib/api/types';

function FloorCanvas({ room }: { room: Room }) {
  return (
    <YStack padding="$4">
      <Text>{room.name}</Text>
    </YStack>
  );
}

export default function FloorScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const [activeRoomId, setActiveRoomId] = useState<string | null>(null);

  const { data: rooms, isLoading, error } = useQuery({
    queryKey: ['staff-rooms', tenant],
    queryFn: () => staffApi.listRooms(tenant!, accessToken!),
    enabled: Boolean(accessToken && tenant),
  });

  const roomList = rooms ?? [];

  useEffect(() => {
    if (!activeRoomId && roomList.length > 0) {
      setActiveRoomId(roomList[0].id);
    }
  }, [activeRoomId, roomList]);

  const activeRoom = useMemo(
    () => roomList.find(room => room.id === activeRoomId) ?? roomList[0] ?? null,
    [activeRoomId, roomList],
  );

  if (isLoading) {
    return <Spinner size="large" />;
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <ScrollView>
      <YStack width="100%" maxWidth={600} alignSelf="center" padding="$4" gap="$4">
        <Text fontSize="$6" fontWeight="$7">
          {t('staff.floor.title')}
        </Text>
        {roomList.length > 1 ? (
          <RoomTabs rooms={roomList} activeId={activeRoom?.id ?? roomList[0].id} onSelect={setActiveRoomId} />
        ) : null}
        {activeRoom ? <FloorCanvas room={activeRoom} /> : null}
      </YStack>
    </ScrollView>
  );
}
