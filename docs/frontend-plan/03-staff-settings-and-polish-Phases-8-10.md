# Phases 8–10 — Staff Settings, Floor Plan & Polish

Covers restaurant settings (opening hours, deposit policy), visual floor plan editor (drag-and-drop table positioning), and i18n completion with responsive layout polish.

---

## Phase 8 — Staff Restaurant Settings

Branch: `feature/frontend-staff-settings`

### Task 8.1 — Settings screen

`app/(staff)/dashboard/settings/index.tsx`:

```tsx
import { ScrollView, YStack, Text, Spinner } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/endpoints';
import type { RestaurantPublicInfo } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/AuthContext';
import { OpeningHoursEditor } from '@/components/settings/OpeningHoursEditor';
import { DepositPolicyEditor } from '@/components/settings/DepositPolicyEditor';
import { AppButton } from '@/components/ui/AppButton';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

export default function SettingsScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const qc = useQueryClient();
  const [draft, setDraft] = useState<Partial<RestaurantPublicInfo>>({});

  const { data, isLoading, error } = useQuery({
    queryKey: ['restaurant-settings', tenant],
    queryFn: () => staffApi.getRestaurantSettings(tenant!, accessToken!),
    enabled: !!accessToken,
  });

  const save = useMutation({
    mutationFn: () => staffApi.updateRestaurantSettings(tenant!, accessToken!, draft),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['restaurant-settings'] });
      setDraft({});
    },
  });

  if (isLoading) return <Spinner size="large" />;
  if (error || !data) return <ErrorMessage error={error} />;

  const settings = { ...data, ...draft };

  return (
    <ScrollView>
      <YStack maxWidth={600} alignSelf="center" width="100%" padding="$4" gap="$6">
        <Text fontWeight="700" fontSize="$5">{t('staff.settings.title')}</Text>
        <OpeningHoursEditor
          hours={settings.opening_hours}
          onChange={(opening_hours) => setDraft(d => ({ ...d, opening_hours }))}
        />
        <DepositPolicyEditor
          policy={settings.deposit_policy}
          onChange={(deposit_policy) => setDraft(d => ({ ...d, deposit_policy }))}
        />
        {save.error && <ErrorMessage error={save.error} />}
        <AppButton onPress={() => save.mutate()} loading={save.isPending} disabled={Object.keys(draft).length === 0}>
          {t('common.save')}
        </AppButton>
      </YStack>
    </ScrollView>
  );
}
```

### Task 8.2 — Opening hours editor

`components/settings/OpeningHoursEditor.tsx`:

```tsx
import { YStack, XStack, Text, Switch } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { OpeningHours } from '@/lib/api/types';
import { AppInput } from '@/components/ui/AppInput';

const DAY_KEYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'] as const;

interface Props {
  hours: OpeningHours[];
  onChange: (hours: OpeningHours[]) => void;
}

export function OpeningHoursEditor({ hours, onChange }: Props) {
  const { t } = useTranslation();

  const updateDay = (day: number, patch: Partial<OpeningHours>) => {
    const existing = hours.find(h => h.day === day);
    if (patch.open === '' && patch.close === '') {
      // Remove day (mark closed)
      onChange(hours.filter(h => h.day !== day));
    } else {
      onChange(
        existing
          ? hours.map(h => (h.day === day ? { ...h, ...patch } : h))
          : [...hours, { day: day as OpeningHours['day'], open: '09:00', close: '22:00', ...patch }],
      );
    }
  };

  return (
    <YStack gap="$4">
      <Text fontWeight="600">{t('staff.settings.openingHours')}</Text>
      {DAY_KEYS.map((key, day) => {
        const entry = hours.find(h => h.day === day);
        const isOpen = !!entry;
        return (
          <XStack key={key} gap="$3" alignItems="center">
            <Text width={40}>{key.toUpperCase()}</Text>
            <Switch
              checked={isOpen}
              onCheckedChange={v => updateDay(day, v ? { open: '09:00', close: '22:00' } : { open: '', close: '' })}
            >
              <Switch.Thumb />
            </Switch>
            {isOpen && (
              <>
                <AppInput value={entry!.open} onChangeText={v => updateDay(day, { open: v })} width={80} />
                <Text>–</Text>
                <AppInput value={entry!.close} onChangeText={v => updateDay(day, { close: v })} width={80} />
              </>
            )}
          </XStack>
        );
      })}
    </YStack>
  );
}
```

### Task 8.3 — Deposit policy editor

`components/settings/DepositPolicyEditor.tsx`:

```tsx
import { YStack, XStack, Text, Input } from 'tamagui';
import { useTranslation } from 'react-i18next';
import type { DepositPolicy } from '@/lib/api/types';
import { AppButton } from '@/components/ui/AppButton';

const MODES: DepositPolicy['mode'][] = ['never', 'always', 'by_party_size'];

interface Props { policy: DepositPolicy; onChange: (p: DepositPolicy) => void; }

export function DepositPolicyEditor({ policy, onChange }: Props) {
  const { t } = useTranslation();
  return (
    <YStack gap="$3">
      <Text fontWeight="600">{t('staff.settings.depositPolicy')}</Text>
      <XStack gap="$2" flexWrap="wrap">
        {MODES.map(mode => (
          <AppButton
            key={mode}
            variant={policy.mode === mode ? 'primary' : 'secondary'}
            size="$3"
            onPress={() => onChange({ mode, min_party_size: policy.min_party_size })}
          >
            {mode === 'by_party_size'
              ? t('staff.settings.byPartySize', { n: policy.min_party_size ?? 4 })
              : t(`staff.settings.${mode}`)}
          </AppButton>
        ))}
      </XStack>
      {policy.mode === 'by_party_size' && (
        <XStack alignItems="center" gap="$3">
          <Text>Min party size</Text>
          <Input
            keyboardType="number-pad"
            value={String(policy.min_party_size ?? '')}
            onChangeText={v => onChange({ ...policy, min_party_size: parseInt(v, 10) || undefined })}
            width={80}
          />
        </XStack>
      )}
    </YStack>
  );
}
```

**Verification — Phase 8:**
- Toggle day open/closed — change persists to backend on Save
- Switch deposit policy mode — change persists to backend
- Booking form on public page reflects updated deposit policy

---

## Phase 9 — Floor Plan Editor

Branch: `feature/frontend-floor-plan`

Tables can be positioned visually. Coordinates are stored in the backend (technical doc §11, business doc §7). Table combinations are out of scope for MVP.

### Task 9.1 — Floor screen & room tabs

`app/(staff)/dashboard/settings/floor.tsx`:

```tsx
import { YStack, Text, Spinner } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/endpoints';
import { useAuth } from '@/lib/auth/AuthContext';
import { RoomTabs } from '@/components/floor/RoomTabs';
import { FloorCanvas } from '@/components/floor/FloorCanvas';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

export default function FloorScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const [activeRoomId, setActiveRoomId] = useState<string | null>(null);

  const { data: rooms, isLoading, error } = useQuery({
    queryKey: ['rooms', tenant],
    queryFn: () => staffApi.listRooms(tenant!, accessToken!),
    enabled: !!accessToken,
  });

  if (isLoading) return <Spinner size="large" />;
  if (error || !rooms) return <ErrorMessage error={error} />;

  const currentId = activeRoomId ?? rooms[0]?.id ?? null;
  const room = rooms.find(r => r.id === currentId) ?? null;

  return (
    <YStack flex={1}>
      <Text padding="$4" fontWeight="700" fontSize="$5">{t('staff.floor.title')}</Text>
      {rooms.length > 1 && (
        <RoomTabs rooms={rooms} activeId={currentId} onSelect={setActiveRoomId} />
      )}
      {room && <FloorCanvas room={room} tenant={tenant!} token={accessToken!} />}
    </YStack>
  );
}
```

`components/floor/RoomTabs.tsx`:

```tsx
import { XStack, Text } from 'tamagui';
import { Pressable } from 'react-native';
import type { Room } from '@/lib/api/types';

interface Props { rooms: Room[]; activeId: string | null; onSelect: (id: string) => void; }

export function RoomTabs({ rooms, activeId, onSelect }: Props) {
  return (
    <XStack borderBottomWidth={1} borderColor="$borderColor" paddingHorizontal="$4">
      {rooms.map(room => (
        <Pressable key={room.id} onPress={() => onSelect(room.id)}>
          <XStack paddingVertical="$3" paddingHorizontal="$3"
            borderBottomWidth={2} borderColor={room.id === activeId ? '$brand' : 'transparent'}>
            <Text color={room.id === activeId ? '$brand' : '$placeholderColor'}>{room.name}</Text>
          </XStack>
        </Pressable>
      ))}
    </XStack>
  );
}
```

### Task 9.2 — Canvas with drag-and-drop

`components/floor/FloorCanvas.tsx`:

```tsx
import { View } from 'react-native';
import { useCallback } from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/endpoints';
import type { Room } from '@/lib/api/types';
import { DraggableTable } from './DraggableTable';

const CANVAS_HEIGHT = 500;

interface Props { room: Room; tenant: string; token: string; }

export function FloorCanvas({ room, tenant, token }: Props) {
  const qc = useQueryClient();

  const updatePosition = useMutation({
    mutationFn: ({ tableId, x, y }: { tableId: string; x: number; y: number }) =>
      staffApi.updateTablePosition(tenant, token, tableId, x, y),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rooms', tenant] }),
  });

  const handleDrop = useCallback(
    (tableId: string, x: number, y: number) => updatePosition.mutate({ tableId, x, y }),
    [tenant, token],
  );

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <View style={{ flex: 1, backgroundColor: '#f9fafb', borderRadius: 8, margin: 16, minHeight: CANVAS_HEIGHT, position: 'relative' }}>
        {room.tables.map(table => (
          <DraggableTable key={table.id} table={table} onDrop={(x, y) => handleDrop(table.id, x, y)} />
        ))}
      </View>
    </GestureHandlerRootView>
  );
}
```

`components/floor/DraggableTable.tsx`:

```tsx
import Animated, { useSharedValue, useAnimatedStyle, runOnJS } from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import { Text } from 'tamagui';
import type { Table } from '@/lib/api/types';

const SIZE = 64;

interface Props { table: Table; onDrop: (x: number, y: number) => void; }

export function DraggableTable({ table, onDrop }: Props) {
  const x = useSharedValue(table.x);
  const y = useSharedValue(table.y);
  const startX = useSharedValue(table.x);
  const startY = useSharedValue(table.y);

  const gesture = Gesture.Pan()
    .onStart(() => { startX.value = x.value; startY.value = y.value; })
    .onUpdate(e => { x.value = startX.value + e.translationX; y.value = startY.value + e.translationY; })
    .onEnd(() => { runOnJS(onDrop)(x.value, y.value); });

  const style = useAnimatedStyle(() => ({
    position: 'absolute',
    left: x.value,
    top: y.value,
    width: SIZE,
    height: SIZE,
    borderRadius: 8,
    backgroundColor: '#1a56db22',
    borderWidth: 1,
    borderColor: '#1a56db',
    justifyContent: 'center',
    alignItems: 'center',
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View style={style}>
        <Text fontSize={12} fontWeight="700">{table.name}</Text>
        <Text fontSize={10} color="$placeholderColor">{table.capacity}p</Text>
      </Animated.View>
    </GestureDetector>
  );
}
```

**Verification — Phase 9:**
- Tables render at stored coordinates on page load
- Drag a table to a new position — `PATCH /api/tables/{id}/position/` fires
- Reload page — table stays at new coordinates
- Multiple rooms — switching room tabs renders correct tables

---

## Phase 10 — i18n Completion & Polish

Branch: `feature/frontend-i18n-polish`

### Task 10.1 — Complete translation files

`lib/i18n/locales/it.json` and `lib/i18n/locales/de.json` must be complete translations of `en.json`. No placeholder values or fallback to English for any key.

Enforce with a dev script `scripts/validate-i18n.ts`:

```ts
import en from '../lib/i18n/locales/en.json';
import it from '../lib/i18n/locales/it.json';
import de from '../lib/i18n/locales/de.json';

function flatKeys(obj: object, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) => {
    const full = prefix ? `${prefix}.${k}` : k;
    return typeof v === 'object' && v !== null ? flatKeys(v, full) : [full];
  });
}

const enKeys = flatKeys(en);
const missing = { it: enKeys.filter(k => !flatKeys(it).includes(k)), de: enKeys.filter(k => !flatKeys(de).includes(k)) };

if (missing.it.length || missing.de.length) {
  console.error('Missing i18n keys:', missing);
  process.exit(1);
}

console.log('All keys present in it and de.');
```

Add to `package.json`:

```json
{ "scripts": { "validate-i18n": "ts-node scripts/validate-i18n.ts" } }
```

### Task 10.2 — Responsive layout (web breakpoints)

Use Tamagui's `useMedia` hook for breakpoint-driven layout. Staff dashboard switches to a sidebar layout on wide screens:

`components/ui/ResponsiveShell.tsx`:

```tsx
import { useMedia, XStack, YStack } from 'tamagui';
import type { ReactNode } from 'react';

interface Props { sidebar: ReactNode; content: ReactNode; }

export function ResponsiveShell({ sidebar, content }: Props) {
  const media = useMedia();
  if (media.gtMd) {
    return (
      <XStack flex={1}>
        <YStack width={260} borderRightWidth={1} borderColor="$borderColor">{sidebar}</YStack>
        <YStack flex={1}>{content}</YStack>
      </XStack>
    );
  }
  return <YStack flex={1}>{content}</YStack>;
}
```

Public booking page is already single-column and centered at `maxWidth={600}` — no changes needed.

### Task 10.3 — AppInput component

Shared across all phases — implement once here if not done earlier:

`components/ui/AppInput.tsx`:

```tsx
import { YStack, Text, Input, type InputProps } from 'tamagui';

interface Props extends InputProps { label: string; }

export function AppInput({ label, ...props }: Props) {
  return (
    <YStack gap="$1">
      <Text fontSize="$3" color="$placeholderColor">{label}</Text>
      <Input
        borderWidth={1}
        borderColor="$borderColor"
        borderRadius="$3"
        paddingHorizontal="$3"
        paddingVertical="$2"
        focusStyle={{ borderColor: '$brand' }}
        {...props}
      />
    </YStack>
  );
}
```

### Task 10.4 — Vercel deployment config

`vercel.json` (at repo root, alongside `frontend/`):

```json
{
  "buildCommand": "cd frontend && npx expo export -p web",
  "outputDirectory": "frontend/dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "env": {
    "EXPO_PUBLIC_API_BASE_URL": "@tablesched_api_base_url",
    "EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY": "@tablesched_stripe_key"
  }
}
```

### Task 10.5 — Documentation updates

After Phase 10 completes, update (per CLAUDE.md policy):

- [ ] `docs/QUICK_START.md` — add frontend section (tech stack, how to run, env vars)
- [ ] `docs/ARCHITECTURE_OVERVIEW.md` — add frontend architecture diagram and file layout
- [ ] `docs/GAPS_AND_IMPROVEMENTS.md` — add known post-MVP frontend gaps (mobile app, floor editor mobile touch, viewer role)
- [ ] `docs/CONTEXT.md` — add to "Recent Changes" (frontend MVP complete)

**Verification — Phase 10:**
```bash
npm run validate-i18n   # No missing keys
npm run typecheck       # Zero errors
npm run lint            # Zero errors
npm run build           # Expo web export succeeds
```

Manual checks:
- Resize browser to tablet/desktop — staff dashboard shows sidebar layout
- All text in the app has i18n keys — no raw English strings in component JSX
- Deploy preview on Vercel loads correctly with env vars set
