# Feature: Tenant Directory Page

## Context

The root URL `/` currently returns "Unmatched Route" because no `app/index.tsx` exists. For
operator use and project showcasing, a tenant directory page lists all active restaurants with
their public booking URL and staff login URL.

The page is gated by `EXPO_PUBLIC_SHOW_TENANT_DIRECTORY=true`. When the flag is absent or false,
the root shows a minimal branded landing page ("TableSched") with no tenant information exposed.
This allows the directory to be enabled in dev/staging and hidden in production.

The tenant list is fetched from the backend public endpoint `GET /api/tenants/` (see
`docs/backend-plan/07-tenant-provisioning-Phase22.md` Task 22.2).

**Branch:** `feature/frontend-tenant-listing`

---

## Tenant API response shape

```json
[
  { "name": "Rome Restaurant",  "schema": "rome",  "api_prefix": "/restaurants/rome/"  },
  { "name": "Milan Restaurant", "schema": "milan", "api_prefix": "/restaurants/milan/" }
]
```

---

## Tasks

### Task 1 — Add `tenantDirectory` method to `publicApi`

Add a new method to `lib/api/endpoints.ts`:

```ts
tenantDirectory() {
  return apiRequest<TenantEntry[]>('/api/tenants/');
},
```

Add the `TenantEntry` type to `lib/api/types.ts`:

```ts
export type TenantEntry = {
  name: string;
  schema: string;
  api_prefix: string;
};
```

**Files to modify:**
- `lib/api/endpoints.ts`
- `lib/api/types.ts`

**Commit:** `[TASK] Task 1 - add tenantDirectory endpoint to publicApi`

---

### Task 2 — Root index page with tenant directory

Create `app/index.tsx`. When `EXPO_PUBLIC_SHOW_TENANT_DIRECTORY=true`, fetch the tenant list
and render a table. Otherwise redirect to `/+not-found`.

```tsx
// app/index.tsx
import { Redirect } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Text, YStack, XStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { publicApi } from '@/lib/api/endpoints';
import { ENV } from '@/lib/env';

export default function TenantDirectoryPage() {
  const { t } = useTranslation();

  if (!ENV.SHOW_TENANT_DIRECTORY) {
    return <Redirect href="/+not-found" />;
  }

  const { data: tenants = [], isLoading } = useQuery({
    queryKey: ['tenant-directory'],
    queryFn: () => publicApi.tenantDirectory(),
  });

  if (isLoading) {
    return (
      <YStack padding="$4">
        <Text>{t('common.loading')}</Text>
      </YStack>
    );
  }

  return (
    <YStack padding="$4" gap="$6">
      <Text fontSize="$7" fontWeight="$8">{t('tenantDirectory.title')}</Text>
      <YStack gap="$2">
        <XStack gap="$4">
          <Text fontWeight="$7" flex={1}>{t('tenantDirectory.restaurant')}</Text>
          <Text fontWeight="$7" flex={2}>{t('tenantDirectory.bookingUrl')}</Text>
          <Text fontWeight="$7" flex={2}>{t('tenantDirectory.staffLogin')}</Text>
        </XStack>
        {tenants.map((tenant) => (
          <XStack key={tenant.schema} gap="$4">
            <Text flex={1}>{tenant.name}</Text>
            <Text flex={2}>{tenant.api_prefix}</Text>
            <Text flex={2}>{tenant.api_prefix}login</Text>
          </XStack>
        ))}
      </YStack>
    </YStack>
  );
}
```

**Files to create/modify:**
- `app/index.tsx` — NEW
- `lib/env.ts` — add `SHOW_TENANT_DIRECTORY` field
- `lib/i18n/locales/en.json` — add `tenantDirectory.*` keys
- `lib/i18n/locales/it.json` — add `tenantDirectory.*` keys
- `lib/i18n/locales/de.json` — add `tenantDirectory.*` keys

**i18n keys to add:**
```json
"tenantDirectory": {
  "title": "TableSched — Restaurants",
  "restaurant": "Restaurant",
  "bookingUrl": "Booking URL",
  "staffLogin": "Staff Login"
}
```

**`lib/env.ts` addition:**
```ts
SHOW_TENANT_DIRECTORY: process.env.EXPO_PUBLIC_SHOW_TENANT_DIRECTORY === 'true',
```

**Commit:** `[TASK] Task 2 - add tenant directory root page`

---

### Task 3 — Tests

```tsx
// __tests__/TenantDirectory.test.tsx
jest.mock('@/lib/api/endpoints', () => ({
  publicApi: {
    tenantDirectory: jest.fn(async () => [
      { name: 'Rome Restaurant',  schema: 'rome',  api_prefix: '/restaurants/rome/'  },
      { name: 'Milan Restaurant', schema: 'milan', api_prefix: '/restaurants/milan/' },
    ]),
  },
}));

test('renders tenant names and URLs', async () => {
  // renders the directory and verifies tenant rows
});

test('renders nothing (branded landing) when SHOW_TENANT_DIRECTORY is false', () => {
  // verifies branded landing page is shown
});
```

**Files:**
- `__tests__/TenantDirectory.test.tsx` — NEW

**Commit:** `[TASK] Task 3 - add tests for tenant directory page`

---

### Task 4 — Branded landing page when directory is disabled

When `EXPO_PUBLIC_SHOW_TENANT_DIRECTORY` is absent or false, `app/index.tsx` renders a minimal
branded landing page instead of blank. No tenant data is fetched or displayed.

```tsx
function LandingPage() {
  return (
    <YStack flex={1} alignItems="center" justifyContent="center" padding="$4" gap="$4">
      <Text fontSize="$9" fontWeight="$8">{t('app.name')}</Text>
      <Text color="$placeholderColor">{t('app.tagline')}</Text>
    </YStack>
  );
}
```

**i18n keys to add:**
```json
"app": {
  "name": "TableSched",
  "tagline": "Restaurant booking management"
}
```

**Files to modify:**
- `app/index.tsx`
- `lib/i18n/locales/en.json`
- `lib/i18n/locales/it.json`
- `lib/i18n/locales/de.json`

**Commit:** `[TASK] Task 4 - show branded landing page when directory is disabled`
