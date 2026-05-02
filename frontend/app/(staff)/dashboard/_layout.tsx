import { PRESS_STYLE } from '@/constants/styles';
import { Slot, useRouter, useSegments } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Stack, Text, YStack } from 'tamagui';
import '@/lib/i18n';
import { ResponsiveShell } from '@/components/ui/ResponsiveShell';

const NAV_ITEMS = [
  { href: '/dashboard', labelKey: 'staff.dashboard.tabs.bookings' },
  { href: '/dashboard/walkins', labelKey: 'staff.dashboard.tabs.walkins' },
  { href: '/dashboard/settings', labelKey: 'staff.dashboard.tabs.settings' },
] as const;

function DashboardSidebar() {
  const { t } = useTranslation();
  const router = useRouter();
  const segments = useSegments();
  const path = `/${segments.slice(1).join('/')}`;

  return (
    <YStack padding="$4" gap="$2">
      {NAV_ITEMS.map(item => {
        const isActive = path === item.href;

        return (
          <Stack
            key={item.href}
            accessibilityRole="button"
            onPress={() => router.push(item.href)}
            pressStyle={PRESS_STYLE}
          >
            <YStack
              padding="$3"
              borderRadius="$4"
              backgroundColor={isActive ? '$color5' : 'transparent'}
              borderWidth={1}
              borderColor={isActive ? '$color10' : '$borderColor'}
            >
              <Text>{t(item.labelKey)}</Text>
            </YStack>
          </Stack>
        );
      })}
    </YStack>
  );
}

export default function DashboardLayout() {
  return (
    <ResponsiveShell sidebar={<DashboardSidebar />} content={<Slot />} />
  );
}
