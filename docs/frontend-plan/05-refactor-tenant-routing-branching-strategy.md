# Branching Strategy — Refactor: Frontend API URL Patterns — Path-Based Tenant Routing

References:
- Implementation plan: [`05-refactor-tenant-routing.md`](./05-refactor-tenant-routing.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text via i18n keys.
- **Tests are mandatory** for every task that introduces logic.
- **Each task branch lifecycle:** create from parent → implement → commit → pre-merge checks → push → merge into parent.
- **Progress markers:** ❌ not done · ✅ done. Update in place as work completes.

## Pre-Merge Checks (run in this order, one at a time)

```bash
# Run all commands from the frontend/ directory
npm run build
npm run typecheck
npm run lint
npm test -- <path/to/specific.test.tsx>   # specific file first
npm test                                   # full suite only if above passes
```

---

## Branch Hierarchy

```
develop
└── refactor/frontend-APIs                          ← already exists; Tasks 1–6 merged
    ├── task/frontend-APIs-Task7-url-patterns
    └── task/frontend-APIs-Task8-token-call-sites
```

---

## ❌ Task 7 — Update all URL paths in `lib/api/endpoints.ts`

Replace all old URL patterns with the path-based tenant prefix `/restaurants/${tenant}/api/v1/`.
Add a `tp()` helper. Add `tenant` parameter to the four token-based public methods.

**Branch:** `task/frontend-APIs-Task7-url-patterns` — created from `refactor/frontend-APIs`

**⚠️ Create only after Task 6 is merged into `refactor/frontend-APIs`.**

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task7-url-patterns
```

**Files to modify:**
- `lib/api/endpoints.ts`

**Tests:**

```ts
// __tests__/api/urlPatterns.test.ts
import { expect, jest, test, beforeEach } from '@jest/globals';

const fetchMock = jest.fn() as jest.MockedFunction<typeof fetch>;
global.fetch = fetchMock;

beforeEach(() => { fetchMock.mockClear(); });

const okResponse = { ok: true, status: 200, json: async () => ({}) } as Response;

import { publicApi, staffApi } from '@/lib/api/endpoints';

test('getRestaurantInfo uses /restaurants/{tenant}/api/v1/ prefix', async () => {
  fetchMock.mockResolvedValueOnce(okResponse);
  await publicApi.getRestaurantInfo('rome').catch(() => {});
  expect((fetchMock.mock.calls[0] as any[])[0]).toContain('/restaurants/rome/api/v1/');
});

test('getBookingByToken includes tenant in URL', async () => {
  fetchMock.mockResolvedValueOnce(okResponse);
  await publicApi.getBookingByToken('rome', 'tok123').catch(() => {});
  const url = (fetchMock.mock.calls[0] as any[])[0] as string;
  expect(url).toContain('/restaurants/rome/api/v1/');
  expect(url).toContain('tok123');
});

test('staffApi.login uses /restaurants/{tenant}/api/v1/auth/login/', async () => {
  fetchMock.mockResolvedValueOnce(okResponse);
  await staffApi.login('rome', 'a@b.com', 'pw').catch(() => {});
  expect((fetchMock.mock.calls[0] as any[])[0]).toContain('/restaurants/rome/api/v1/auth/login/');
});

test('staffApi.listBookings uses /restaurants/{tenant}/api/v1/bookings/', async () => {
  fetchMock.mockResolvedValueOnce({ ...okResponse, json: async () => [] } as any);
  await staffApi.listBookings('rome', 'tok').catch(() => {});
  expect((fetchMock.mock.calls[0] as any[])[0]).toContain('/restaurants/rome/api/v1/bookings/');
});

test('no old /api/public/ or /api/staff/ patterns reachable', async () => {
  fetchMock.mockResolvedValue(okResponse);
  await publicApi.getRestaurantInfo('rome').catch(() => {});
  const url = (fetchMock.mock.calls[0] as any[])[0] as string;
  expect(url).not.toContain('/api/public/');
  expect(url).not.toContain('/api/staff/');
});
```

**Commit:**
```bash
git add lib/api/endpoints.ts __tests__/api/urlPatterns.test.ts
git commit -m "[TASK] 7 align all API URL patterns with path-based tenant routing"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/api/urlPatterns.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task7-url-patterns
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task7-url-patterns
git push origin refactor/frontend-APIs
```

---

## ❌ Task 8 — Update call sites for token-based `publicApi` methods

`getBookingByToken`, `cancelBooking`, `modifyBooking`, `getPaymentIntent` now require `tenant` as
first argument. Update every call site to pass the tenant slug extracted from route params.

**Branch:** `task/frontend-APIs-Task8-token-call-sites` — created from `refactor/frontend-APIs`

**⚠️ Create only after Task 7 is merged into `refactor/frontend-APIs`.**

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task8-token-call-sites
```

**Files to modify:**
- `app/(public)/[tenant]/booking/[token]/index.tsx`
- `app/(public)/[tenant]/booking/[token]/pay.tsx`
- `components/booking/CustomerBookingActions.tsx`
- `components/booking/ModifyBookingForm.tsx`

**Pattern:** `tenant` is already available from `useLocalSearchParams<{ tenant: string; token: string }>()` in the route screens. Pass it down via props to child components.

**Tests:**

```tsx
// __tests__/booking/CustomerBookingActions.test.tsx  (extend existing if present)
jest.mock('@/lib/api/endpoints', () => ({
  publicApi: {
    cancelBooking: jest.fn(() => Promise.resolve()),
    modifyBooking: jest.fn(() => Promise.resolve({})),
  },
}));

import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@/lib/i18n';
import { CustomerBookingActions } from '@/components/booking/CustomerBookingActions';

const booking = {
  id: 'b1', status: 'confirmed' as const, date: '2026-05-10', time: '19:00',
  party_size: 2, customer: { name: 'A', phone: '+39', locale: 'it' }, created_at: '',
};

function wrap(ui: any) {
  return <QueryClientProvider client={new QueryClient()}>{ui}</QueryClientProvider>;
}

test('cancel passes tenant to cancelBooking', async () => {
  const { publicApi } = require('@/lib/api/endpoints');
  render(wrap(<CustomerBookingActions booking={booking} tenant="rome" token="tok" />));
  fireEvent.press(screen.getByText('Cancel booking'));
  await waitFor(() =>
    expect(publicApi.cancelBooking).toHaveBeenCalledWith('rome', 'tok'),
  );
});
```

**Commit:**
```bash
git add \
  app/\(public\)/\[tenant\]/booking/\[token\]/index.tsx \
  app/\(public\)/\[tenant\]/booking/\[token\]/pay.tsx \
  components/booking/CustomerBookingActions.tsx \
  components/booking/ModifyBookingForm.tsx \
  __tests__/booking/CustomerBookingActions.test.tsx
git commit -m "[TASK] 8 pass tenant to token-based publicApi call sites"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/booking/CustomerBookingActions.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task8-token-call-sites
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task8-token-call-sites
git push origin refactor/frontend-APIs
```

---

## ❌ Refactor complete — merge into develop

All tasks (1–8) complete. Run the full pre-merge checklist one final time:

```bash
npm run build
npm run typecheck
npm run lint
npm test
```

All checks must pass. Then — with explicit confirmation:

```bash
git checkout develop
git merge refactor/frontend-APIs
git push origin develop
```
