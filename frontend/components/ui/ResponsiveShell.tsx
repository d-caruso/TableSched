import type { ReactNode } from 'react';
import { useMedia, XStack, YStack } from 'tamagui';

type Props = {
  sidebar: ReactNode;
  content: ReactNode;
};

export function ResponsiveShell({ sidebar, content }: Props) {
  const media = useMedia();

  if (media.gtMd) {
    return (
      <XStack flex={1}>
        <YStack width={260} borderRightWidth={1} borderColor="$borderColor" testID="sidebar-container">
          {sidebar}
        </YStack>
        <YStack flex={1}>{content}</YStack>
      </XStack>
    );
  }

  return <YStack flex={1}>{content}</YStack>;
}
