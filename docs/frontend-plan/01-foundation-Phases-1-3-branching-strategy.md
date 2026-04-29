# Branching Strategy — Phases 1–3: Foundation

References:
- Implementation plan: [`01-foundation-Phases-1-3.md`](./01-foundation-Phases-1-3.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text shown to the user must use i18n translation keys. The API returns only `error_code`, `reason_code`, and `status` codes — never localized text (except staff-written free-text fields).
- **Tests are mandatory** for every task that introduces logic. Write tests in the same task branch, before merging.
- **Each task branch lifecycle:** create from parent → implement → commit → pre-merge checks → push → merge into parent.
- **Progress markers:** ❌ not done · ✅ done. Update in place as work completes.

## Pre-Merge Checks (Expo frontend — run in this order, one at a time)

```bash
# Run all commands from the frontend/ directory

# 1. Build
npm run build

# 2. Type check
npm run typecheck

# 3. Lint
npm run lint

# 4a. Tests — specific file(s) for changed code only
npm test -- <path/to/specific.test.tsx>

# 4b. Full test suite — only if 4a passes
npm test
```

All checks must pass (0 errors, 0 failures) before merging.

---

## Branch Hierarchy

```
develop
└── feature/frontend-mvp                                    ← created from develop
    ├── feature/frontend-mvp-Phase1-bootstrap               ← created from feature/frontend-mvp
    │   ├── task/frontend-mvp-Task1.1-scaffold
    │   ├── task/frontend-mvp-Task1.2-dependencies
    │   ├── task/frontend-mvp-Task1.3-config
    │   └── task/frontend-mvp-Task1.4-tamagui-root-layout
    ├── feature/frontend-mvp-Phase2-shared-infra            ← created from feature/frontend-mvp AFTER Phase 1 merged
    │   ├── task/frontend-mvp-Task2.1-i18n
    │   ├── task/frontend-mvp-Task2.2-api-client
    │   ├── task/frontend-mvp-Task2.3-auth-context
    │   └── task/frontend-mvp-Task2.4-ui-primitives
    └── feature/frontend-mvp-Phase3-public-booking          ← created from feature/frontend-mvp AFTER Phase 2 merged
        ├── task/frontend-mvp-Task3.1-restaurant-info
        ├── task/frontend-mvp-Task3.2-form-orchestrator
        ├── task/frontend-mvp-Task3.3-step-datetime
        └── task/frontend-mvp-Task3.4-step-contact-done
```

---

## Root Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/frontend-mvp
git push -u origin feature/frontend-mvp
```

---

## ❌ Phase 1 — Repository & Project Bootstrap

Sets up the Expo project skeleton, installs all dependencies, and configures Tamagui, TypeScript, Expo Router, and the root layout. No domain logic — just the scaffolding every subsequent phase builds on.

**Branch:** `feature/frontend-mvp-Phase1-bootstrap` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase1-bootstrap
git push -u origin feature/frontend-mvp-Phase1-bootstrap
```

---

### ❌ Task 1.1 — Expo Scaffold

Initialize the Expo project and create the full directory layout. No logic, no user-facing strings.

**Branch:** `task/frontend-mvp-Task1.1-scaffold` — created from `feature/frontend-mvp-Phase1-bootstrap`

```bash
git checkout feature/frontend-mvp-Phase1-bootstrap
git pull origin feature/frontend-mvp-Phase1-bootstrap
git checkout -b task/frontend-mvp-Task1.1-scaffold
```

**Commands:**

```bash
npx create-expo-app@latest frontend --template tabs
```

**Directory structure to create:**

```
frontend/
  app/
    _layout.tsx
    (public)/
      _layout.tsx
      [tenant]/
        index.tsx
        booking/
          [token]/
            index.tsx
            pay.tsx
    (staff)/
      _layout.tsx
      login.tsx
      dashboard/
        _layout.tsx
        index.tsx
        bookings/
          [id].tsx
        walkins.tsx
        settings/
          index.tsx
          floor.tsx
    +not-found.tsx
  components/
    booking/
      steps/
    payment/
    staff/
    floor/
    settings/
    ui/
  lib/
    api/
    auth/
    i18n/
      locales/
    env.ts
  constants/
    routes.ts
  assets/
```

**Tests:** None — no logic introduced.

**Commit:**
```bash
git add .
git commit -m "[TASK] 1.1 create Expo project scaffold and directory layout"
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task1.1-scaffold
git checkout feature/frontend-mvp-Phase1-bootstrap
git merge task/frontend-mvp-Task1.1-scaffold
git push origin feature/frontend-mvp-Phase1-bootstrap
```

---

### ❌ Task 1.2 — Dependencies

Pin all project dependencies in `package.json`, and add the initial ESLint config and package scripts for linting and type checking. No logic, no user-facing strings.

**Branch:** `task/frontend-mvp-Task1.2-dependencies` — created from `feature/frontend-mvp-Phase1-bootstrap`

```bash
git checkout feature/frontend-mvp-Phase1-bootstrap
git pull origin feature/frontend-mvp-Phase1-bootstrap
git checkout -b task/frontend-mvp-Task1.2-dependencies
```

**Key dependencies to add:**

```json
{
  "dependencies": {
    "expo": "~52.0.0",
    "expo-router": "~4.0.0",
    "react-native": "0.76.x",
    "react-native-web": "~0.19.x",
    "@tamagui/core": "^1.120.x",
    "@tamagui/config": "^1.120.x",
    "@tamagui/animations-react-native": "^1.120.x",
    "tamagui": "^1.120.x",
    "@tanstack/react-query": "^5.x",
    "@stripe/stripe-js": "^4.x",
    "@stripe/react-stripe-js": "^2.x",
    "expo-secure-store": "~14.x",
    "expo-constants": "~17.x",
    "react-native-gesture-handler": "~2.20.x",
    "react-native-reanimated": "~3.16.x",
    "react-native-safe-area-context": "4.12.x",
    "react-native-screens": "~4.4.x",
    "i18next": "^23.x",
    "react-i18next": "^15.x",
    "zod": "^3.x"
  },
  "devDependencies": {
    "@tamagui/babel-plugin": "^1.120.x",
    "typescript": "^5.x",
    "@types/react": "^18.x",
    "eslint": "^9.x",
    "@typescript-eslint/parser": "^8.x",
    "@testing-library/react-native": "^12.x",
    "jest": "^29.x",
    "jest-expo": "~52.x"
  }
}
```

Also add:
- `package.json` scripts for `typecheck` and `lint`
- an initial ESLint config file for the frontend app

No Celery, no Redis, no background job runner (technical doc §8).

**Tests:** None — no logic introduced.

**Commit:**
```bash
git add package.json package-lock.json
git commit -m "[TASK] 1.2 define project dependencies"
```

**Pre-merge checks:**
```bash
npm run typecheck
npm run lint
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task1.2-dependencies
git checkout feature/frontend-mvp-Phase1-bootstrap
git merge task/frontend-mvp-Task1.2-dependencies
git push origin feature/frontend-mvp-Phase1-bootstrap
```

---

### ❌ Task 1.3 — Configuration Files

Create `app.json`, `babel.config.js`, `tsconfig.json`, `.env.example`, `lib/env.ts`, and `constants/routes.ts`. No logic, no user-facing strings.

**Branch:** `task/frontend-mvp-Task1.3-config` — created from `feature/frontend-mvp-Phase1-bootstrap`

```bash
git checkout feature/frontend-mvp-Phase1-bootstrap
git pull origin feature/frontend-mvp-Phase1-bootstrap
git checkout -b task/frontend-mvp-Task1.3-config
```

**Files to create:**

`app.json` — sets Expo Router origin, enables web static export.

`babel.config.js` — configures `@tamagui/babel-plugin` and `react-native-reanimated/plugin`.

`tsconfig.json` — extends `expo/tsconfig.base`, enables `strict`, adds `@/*` path alias.

`.env.example`:

```
EXPO_PUBLIC_API_BASE_URL=https://api.tablesched.domenicocaruso.com
EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
EXPO_PUBLIC_APP_ENV=development
```

`lib/env.ts` — reads `EXPO_PUBLIC_*` vars; exported as a typed `ENV` constant. No fallback strings visible to users.

`constants/routes.ts` — typed route builder functions (no user-facing text).

**Tests:** None — no logic introduced.

**Commit:**
```bash
git add app.json babel.config.js tsconfig.json .env.example lib/env.ts constants/routes.ts
git commit -m "[TASK] 1.3 add project configuration files"
```

**Pre-merge checks:**
```bash
npm run typecheck
npm run lint
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task1.3-config
git checkout feature/frontend-mvp-Phase1-bootstrap
git merge task/frontend-mvp-Task1.3-config
git push origin feature/frontend-mvp-Phase1-bootstrap
```

---

### ❌ Task 1.4 — Tamagui Config & Root Layout

Create `tamagui.config.ts` with brand color tokens and `app/_layout.tsx` wiring `TamaguiProvider`, `QueryClientProvider`, and `I18nProvider` (stub at this stage).

**Branch:** `task/frontend-mvp-Task1.4-tamagui-root-layout` — created from `feature/frontend-mvp-Phase1-bootstrap`

```bash
git checkout feature/frontend-mvp-Phase1-bootstrap
git pull origin feature/frontend-mvp-Phase1-bootstrap
git checkout -b task/frontend-mvp-Task1.4-tamagui-root-layout
```

**`tamagui.config.ts`** — extends `@tamagui/config/v3`, adds tokens: `brand`, `brandDark`, `danger`, `warning`, `success`. Exports `AppConfig` type and adds module augmentation.

**`app/_layout.tsx`:**

```tsx
import { TamaguiProvider } from 'tamagui';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Slot } from 'expo-router';
import { tamaguiConfig } from '@/tamagui.config';
import { I18nProvider } from '@/lib/i18n/I18nProvider';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <TamaguiProvider config={tamaguiConfig} defaultTheme="light">
        <I18nProvider>
          <Slot />
        </I18nProvider>
      </TamaguiProvider>
    </QueryClientProvider>
  );
}
```

**Tests:**

```tsx
// __tests__/RootLayout.test.tsx
import { render } from '@testing-library/react-native';
import RootLayout from '@/app/_layout';

test('root layout renders without crash', () => {
  expect(() => render(<RootLayout />)).not.toThrow();
});
```

**Commit:**
```bash
git add tamagui.config.ts app/_layout.tsx __tests__/
git commit -m "[TASK] 1.4 add Tamagui config and root layout"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/RootLayout.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task1.4-tamagui-root-layout
git checkout feature/frontend-mvp-Phase1-bootstrap
git merge task/frontend-mvp-Task1.4-tamagui-root-layout
git push origin feature/frontend-mvp-Phase1-bootstrap
```

---

### ❌ Phase 1 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase1-bootstrap
git push origin feature/frontend-mvp
```

---

## ❌ Phase 2 — Shared Infrastructure

Establishes i18n (i18next + locale JSON files), the typed API client, the staff JWT auth context, and the shared Tamagui UI primitives used by all subsequent phases.

**⚠️ Create this branch only after Phase 1 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase2-shared-infra` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase2-shared-infra
git push -u origin feature/frontend-mvp-Phase2-shared-infra
```

---

### ❌ Task 2.1 — i18n Setup

Wire i18next with `en`, `it`, `de` locale files. All MVP translation keys must be present in all three files. **No raw strings in any component** — every user-visible label uses a translation key.

**Branch:** `task/frontend-mvp-Task2.1-i18n` — created from `feature/frontend-mvp-Phase2-shared-infra`

```bash
git checkout feature/frontend-mvp-Phase2-shared-infra
git pull origin feature/frontend-mvp-Phase2-shared-infra
git checkout -b task/frontend-mvp-Task2.1-i18n
```

**Files to create:**
- `lib/i18n/index.ts` — initializes i18next with all three locales, fallback `en`
- `lib/i18n/I18nProvider.tsx` — wraps `I18nextProvider`
- `lib/i18n/useLocale.ts` — `{ locale, setLocale }` hook
- `lib/i18n/locales/en.json` — complete MVP key set (see implementation plan)
- `lib/i18n/locales/it.json` — complete Italian translations
- `lib/i18n/locales/de.json` — complete German translations

**Tests:**

```ts
// __tests__/i18n.test.ts
import i18n from '@/lib/i18n';

test('all en keys are present in it and de', () => {
  const enKeys = Object.keys(i18n.getResourceBundle('en', 'translation'));
  const itKeys = Object.keys(i18n.getResourceBundle('it', 'translation'));
  const deKeys = Object.keys(i18n.getResourceBundle('de', 'translation'));
  enKeys.forEach(k => {
    expect(itKeys).toContain(k);
    expect(deKeys).toContain(k);
  });
});

test('booking status keys map to non-empty strings in en', () => {
  const statuses = ['pending_review', 'pending_payment', 'confirmed', 'declined'];
  statuses.forEach(s => {
    expect(i18n.t(`booking.status.${s}`)).toBeTruthy();
  });
});
```

**Commit:**
```bash
git add lib/i18n/
git commit -m "[TASK] 2.1 add i18n setup with en/it/de locale files"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/i18n.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task2.1-i18n
git checkout feature/frontend-mvp-Phase2-shared-infra
git merge task/frontend-mvp-Task2.1-i18n
git push origin feature/frontend-mvp-Phase2-shared-infra
```

---

### ✅ Task 2.2 — API Client

Implement `lib/api/client.ts` (typed `apiRequest`, `ApiError`), `lib/api/types.ts` (shared model types mirroring backend), and `lib/api/endpoints.ts` (`publicApi`, `staffApi`). **No localized error strings** — `ApiError` exposes `code` only; the frontend maps codes to i18n keys.

**Branch:** `task/frontend-mvp-Task2.2-api-client` — created from `feature/frontend-mvp-Phase2-shared-infra`

```bash
git checkout feature/frontend-mvp-Phase2-shared-infra
git pull origin feature/frontend-mvp-Phase2-shared-infra
git checkout -b task/frontend-mvp-Task2.2-api-client
```

**Files to create:**
- `lib/api/client.ts` — `apiRequest<T>()` generic fetch wrapper, `ApiError` class
- `lib/api/types.ts` — `BookingStatus`, `PaymentStatus`, `Booking`, `TimeSlot`, `RestaurantPublicInfo`, `Room`, `Table`, `BookingCreatePayload`
- `lib/api/endpoints.ts` — `publicApi` and `staffApi` namespaces

**Tests:**

```ts
// __tests__/api/client.test.ts
import { ApiError, apiRequest } from '@/lib/api/client';

global.fetch = jest.fn();

test('apiRequest throws ApiError on non-ok response', async () => {
  (fetch as jest.Mock).mockResolvedValueOnce({
    ok: false,
    json: async () => ({ code: 'BOOKING_NOT_FOUND' }),
  });
  await expect(apiRequest('/api/test/')).rejects.toBeInstanceOf(ApiError);
});

test('ApiError carries the error code', async () => {
  (fetch as jest.Mock).mockResolvedValueOnce({
    ok: false,
    json: async () => ({ code: 'TOKEN_EXPIRED' }),
  });
  try {
    await apiRequest('/api/test/');
  } catch (e) {
    expect((e as ApiError).code).toBe('TOKEN_EXPIRED');
  }
});

test('apiRequest returns parsed JSON on success', async () => {
  (fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: async () => ({ id: '123' }),
  });
  const result = await apiRequest<{ id: string }>('/api/test/');
  expect(result.id).toBe('123');
});
```

**Commit:**
```bash
git add lib/api/
git commit -m "[TASK] 2.2 add typed API client and endpoint definitions"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/api/client.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task2.2-api-client
git checkout feature/frontend-mvp-Phase2-shared-infra
git merge task/frontend-mvp-Task2.2-api-client
git push origin feature/frontend-mvp-Phase2-shared-infra
```

---

### ✅ Task 2.3 — Auth Context

Implement `lib/auth/AuthContext.tsx` with JWT storage (`sessionStorage` on web, `SecureStore` on native), login, and logout. Customers never authenticate — this is staff-only (technical doc §5, business doc §12).

**Branch:** `task/frontend-mvp-Task2.3-auth-context` — created from `feature/frontend-mvp-Phase2-shared-infra`

```bash
git checkout feature/frontend-mvp-Phase2-shared-infra
git pull origin feature/frontend-mvp-Phase2-shared-infra
git checkout -b task/frontend-mvp-Task2.3-auth-context
```

**Files to create:**
- `lib/auth/AuthContext.tsx` — `AuthProvider`, `useAuth` hook; reads stored tokens on mount; exposes `{ accessToken, tenant, isLoading, login, logout }`

**Tests:**

```tsx
// __tests__/auth/AuthContext.test.tsx
import { renderHook, act } from '@testing-library/react-native';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';

jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(async () => null),
  setItemAsync: jest.fn(async () => {}),
  deleteItemAsync: jest.fn(async () => {}),
}));

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    login: jest.fn(async () => ({ access: 'tok-access', refresh: 'tok-refresh' })),
  },
}));

test('initial state has no token', async () => {
  const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
  await act(async () => {});
  expect(result.current.accessToken).toBeNull();
});

test('login stores access token', async () => {
  const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
  await act(async () => { await result.current.login('a@b.com', 'pass', 'tenant1'); });
  expect(result.current.accessToken).toBe('tok-access');
  expect(result.current.tenant).toBe('tenant1');
});

test('logout clears token', async () => {
  const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
  await act(async () => { await result.current.login('a@b.com', 'pass', 'tenant1'); });
  await act(async () => { await result.current.logout(); });
  expect(result.current.accessToken).toBeNull();
});
```

**Commit:**
```bash
git add lib/auth/
git commit -m "[TASK] 2.3 add staff JWT auth context"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/auth/AuthContext.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task2.3-auth-context
git checkout feature/frontend-mvp-Phase2-shared-infra
git merge task/frontend-mvp-Task2.3-auth-context
git push origin feature/frontend-mvp-Phase2-shared-infra
```

---

### ✅ Task 2.4 — Shared UI Primitives

Implement `AppButton`, `AppInput`, `StatusBadge`, and `ErrorMessage`. All text via i18n keys — no hardcoded strings. `ErrorMessage` maps `ApiError.code` to an i18n key; if the key is missing it falls back to `common.error`.

**Branch:** `task/frontend-mvp-Task2.4-ui-primitives` — created from `feature/frontend-mvp-Phase2-shared-infra`

```bash
git checkout feature/frontend-mvp-Phase2-shared-infra
git pull origin feature/frontend-mvp-Phase2-shared-infra
git checkout -b task/frontend-mvp-Task2.4-ui-primitives
```

**Files to create:**
- `components/ui/AppButton.tsx` — wraps Tamagui `Button`; variants: `primary`, `secondary`, `danger`, `ghost`; `loading` prop
- `components/ui/AppInput.tsx` — wraps Tamagui `Input` with a label above
- `components/ui/StatusBadge.tsx` — maps `BookingStatus` to color + i18n label
- `components/ui/ErrorMessage.tsx` — maps `ApiError.code` → `t('error.<code>')`

**Tests:**

```tsx
// __tests__/ui/StatusBadge.test.tsx
import { render, screen } from '@testing-library/react-native';
import { StatusBadge } from '@/components/ui/StatusBadge';

test('renders localized status label', () => {
  render(<StatusBadge status="pending_review" />);
  expect(screen.getByText('Pending review')).toBeTruthy();
});

// __tests__/ui/ErrorMessage.test.tsx
import { render, screen } from '@testing-library/react-native';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { ApiError } from '@/lib/api/client';

test('renders i18n key for known error code', () => {
  const err = new ApiError(404, 'BOOKING_NOT_FOUND');
  render(<ErrorMessage error={err} />);
  expect(screen.getByText('Booking not found')).toBeTruthy();
});

test('falls back to common.error for unknown code', () => {
  const err = new ApiError(500, 'VERY_UNKNOWN_CODE');
  render(<ErrorMessage error={err} />);
  expect(screen.getByText('Something went wrong')).toBeTruthy();
});
```

**Commit:**
```bash
git add components/ui/
git commit -m "[TASK] 2.4 add shared UI primitives (AppButton, AppInput, StatusBadge, ErrorMessage)"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/ui/
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task2.4-ui-primitives
git checkout feature/frontend-mvp-Phase2-shared-infra
git merge task/frontend-mvp-Task2.4-ui-primitives
git push origin feature/frontend-mvp-Phase2-shared-infra
```

---

### ❌ Phase 2 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase2-shared-infra
git push origin feature/frontend-mvp
```

---

## ❌ Phase 3 — Public Booking Page

Customer-facing page: restaurant info display + multi-step booking form (date/time/party size → contact details → submit). No authentication. Booking is always a request, never an immediate confirmation (business doc §1).

**⚠️ Create this branch only after Phase 2 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase3-public-booking` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase3-public-booking
git push -u origin feature/frontend-mvp-Phase3-public-booking
```

---

### ✅ Task 3.1 — Restaurant Info Display

Implement `app/(public)/[tenant]/index.tsx`, `RestaurantHeader`, and `OpeningHoursList`. Fetches restaurant public info via `publicApi.getRestaurant`. No user-facing strings — all labels via i18n keys.

**Branch:** `task/frontend-mvp-Task3.1-restaurant-info` — created from `feature/frontend-mvp-Phase3-public-booking`

```bash
git checkout feature/frontend-mvp-Phase3-public-booking
git pull origin feature/frontend-mvp-Phase3-public-booking
git checkout -b task/frontend-mvp-Task3.1-restaurant-info
```

**Files to create:**
- `app/(public)/[tenant]/index.tsx` — fetches restaurant, renders header + hours + `BookingFormFlow` (stub)
- `app/(public)/_layout.tsx` — public layout (no auth guard)
- `components/booking/RestaurantHeader.tsx` — displays restaurant name
- `components/booking/OpeningHoursList.tsx` — renders weekly opening hours

**Tests:**

```tsx
// __tests__/booking/RestaurantHeader.test.tsx
import { render, screen } from '@testing-library/react-native';
import { RestaurantHeader } from '@/components/booking/RestaurantHeader';

test('displays restaurant name', () => {
  render(<RestaurantHeader name="Da Mario" />);
  expect(screen.getByText('Da Mario')).toBeTruthy();
});
```

**Commit:**
```bash
git add app/(public)/ components/booking/RestaurantHeader.tsx components/booking/OpeningHoursList.tsx
git commit -m "[TASK] 3.1 add public restaurant info page and header"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/booking/RestaurantHeader.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task3.1-restaurant-info
git checkout feature/frontend-mvp-Phase3-public-booking
git merge task/frontend-mvp-Task3.1-restaurant-info
git push origin feature/frontend-mvp-Phase3-public-booking
```

---

### ✅ Task 3.2 — Booking Form Orchestrator

Implement `BookingFormFlow` — manages the `datetime → contact → done` step state and the accumulated draft payload. Contains no fetch logic of its own; delegates to step components.

**Branch:** `task/frontend-mvp-Task3.2-form-orchestrator` — created from `feature/frontend-mvp-Phase3-public-booking`

```bash
git checkout feature/frontend-mvp-Phase3-public-booking
git pull origin feature/frontend-mvp-Phase3-public-booking
git checkout -b task/frontend-mvp-Task3.2-form-orchestrator
```

**Files to create:**
- `components/booking/BookingFormFlow.tsx` — `Step` union type, `draft` state, conditional render of step components (stubs accepted at this stage)

**Tests:**

```tsx
// __tests__/booking/BookingFormFlow.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { BookingFormFlow } from '@/components/booking/BookingFormFlow';

const restaurant = { slug: 'r', name: 'R', opening_hours: [], deposit_policy: { mode: 'never' }, cancellation_cutoff_hours: 24 };

test('starts on datetime step', () => {
  render(<BookingFormFlow tenant="r" restaurant={restaurant} />);
  expect(screen.getByTestId('step-datetime')).toBeTruthy();
});
```

**Commit:**
```bash
git add components/booking/BookingFormFlow.tsx
git commit -m "[TASK] 3.2 add booking form flow orchestrator"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/booking/BookingFormFlow.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task3.2-form-orchestrator
git checkout feature/frontend-mvp-Phase3-public-booking
git merge task/frontend-mvp-Task3.2-form-orchestrator
git push origin feature/frontend-mvp-Phase3-public-booking
```

---

### ✅ Task 3.3 — StepDateTime (date, time slot, party size)

Implement `StepDateTime`, `TimeSlotGrid`, and `PartySizeSelector`. Fetches available slots via `publicApi.getAvailableSlots` when a date is selected. Slots with `busy_warning` show an indicator but remain selectable (business doc §3). Time slots are 15-minute intervals; advance limit is 90 days (business doc §11).

**Branch:** `task/frontend-mvp-Task3.3-step-datetime` — created from `feature/frontend-mvp-Phase3-public-booking`

```bash
git checkout feature/frontend-mvp-Phase3-public-booking
git pull origin feature/frontend-mvp-Phase3-public-booking
git checkout -b task/frontend-mvp-Task3.3-step-datetime
```

**Files to create:**
- `components/booking/steps/StepDateTime.tsx`
- `components/booking/TimeSlotGrid.tsx`
- `components/booking/PartySizeSelector.tsx`
- `components/booking/DatePicker.tsx` — wraps a date input; enforces `minDate = today`, `maxDays = 90`

**Tests:**

```tsx
// __tests__/booking/PartySizeSelector.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';

test('increments party size', () => {
  const onChange = jest.fn();
  render(<PartySizeSelector value={2} onChange={onChange} />);
  fireEvent.press(screen.getByText('+'));
  expect(onChange).toHaveBeenCalledWith(3);
});

test('does not decrement below 1', () => {
  const onChange = jest.fn();
  render(<PartySizeSelector value={1} onChange={onChange} />);
  fireEvent.press(screen.getByText('−'));
  expect(onChange).not.toHaveBeenCalled();
});

// __tests__/booking/TimeSlotGrid.test.tsx
test('unavailable slots are not pressable', () => {
  const onSelect = jest.fn();
  render(<TimeSlotGrid slots={[{ time: '13:00', available: false, busy_warning: false }]} loading={false} selected="" onSelect={onSelect} />);
  fireEvent.press(screen.getByText('13:00'));
  expect(onSelect).not.toHaveBeenCalled();
});
```

**Commit:**
```bash
git add components/booking/steps/StepDateTime.tsx components/booking/TimeSlotGrid.tsx components/booking/PartySizeSelector.tsx components/booking/DatePicker.tsx
git commit -m "[TASK] 3.3 add StepDateTime, TimeSlotGrid, PartySizeSelector"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/booking/PartySizeSelector.test.tsx __tests__/booking/TimeSlotGrid.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task3.3-step-datetime
git checkout feature/frontend-mvp-Phase3-public-booking
git merge task/frontend-mvp-Task3.3-step-datetime
git push origin feature/frontend-mvp-Phase3-public-booking
```

---

### ✅ Task 3.4 — StepContact, StepDone & LocaleSelector

Implement `StepContact` (name, phone, email, locale, notes), `StepDone` (submits via `publicApi.createBooking`, shows success), and `LocaleSelector`. Phone is required; email is optional (business doc §1, §12). `StepDone` fires the mutation once on mount.

**Branch:** `task/frontend-mvp-Task3.4-step-contact-done` — created from `feature/frontend-mvp-Phase3-public-booking`

```bash
git checkout feature/frontend-mvp-Phase3-public-booking
git pull origin feature/frontend-mvp-Phase3-public-booking
git checkout -b task/frontend-mvp-Task3.4-step-contact-done
```

**Files to create:**
- `components/booking/steps/StepContact.tsx`
- `components/booking/steps/StepDone.tsx`
- `components/booking/LocaleSelector.tsx` — dropdown for `en`, `it`, `de`

**Tests:**

```tsx
// __tests__/booking/StepContact.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { StepContact } from '@/components/booking/steps/StepContact';

test('submit button disabled when name or phone empty', () => {
  const onNext = jest.fn();
  render(<StepContact draft={{}} tenant="r" onBack={jest.fn()} onNext={onNext} />);
  fireEvent.press(screen.getByText('Request booking'));
  expect(onNext).not.toHaveBeenCalled();
});

test('calls onNext with contact fields when valid', () => {
  const onNext = jest.fn();
  render(<StepContact draft={{}} tenant="r" onBack={jest.fn()} onNext={onNext} />);
  fireEvent.changeText(screen.getByLabelText('Full name'), 'Mario Rossi');
  fireEvent.changeText(screen.getByLabelText('Phone number'), '+393331234567');
  fireEvent.press(screen.getByText('Request booking'));
  expect(onNext).toHaveBeenCalledWith(expect.objectContaining({ name: 'Mario Rossi', phone: '+393331234567' }));
});
```

**Commit:**
```bash
git add components/booking/steps/StepContact.tsx components/booking/steps/StepDone.tsx components/booking/LocaleSelector.tsx
git commit -m "[TASK] 3.4 add StepContact, StepDone, LocaleSelector"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/booking/StepContact.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task3.4-step-contact-done
git checkout feature/frontend-mvp-Phase3-public-booking
git merge task/frontend-mvp-Task3.4-step-contact-done
git push origin feature/frontend-mvp-Phase3-public-booking
```

---

### ❌ Phase 3 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase3-public-booking
git push origin feature/frontend-mvp
```
