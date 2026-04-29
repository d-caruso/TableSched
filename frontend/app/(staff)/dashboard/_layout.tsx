import { Tabs } from 'expo-router';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';

export default function DashboardLayout() {
  const { t } = useTranslation();

  return (
    <Tabs screenOptions={{ headerShown: false }}>
      <Tabs.Screen name="index" options={{ title: t('staff.dashboard.tabs.bookings') }} />
      <Tabs.Screen name="walkins" options={{ title: t('staff.dashboard.tabs.walkins') }} />
      <Tabs.Screen name="settings" options={{ title: t('staff.dashboard.tabs.settings') }} />
    </Tabs>
  );
}
