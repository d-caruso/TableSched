# Branching Strategy — Refactor: Frontend API Client — RESTful Endpoint Alignment

References:
- Implementation plan: [`04-refactor-frontend-APIs.md`](./04-refactor-frontend-APIs.md)
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
└── refactor/frontend-APIs                          ← created from develop
    ├── task/frontend-APIs-Task1-staffapi-methods
    ├── task/frontend-APIs-Task2-booking-actions
    ├── task/frontend-APIs-Task3-assign-tables
    ├── task/frontend-APIs-Task4-noshow-modify
    ├── task/frontend-APIs-Task5-refund-cleanup
    └── task/frontend-APIs-Task6-cancel-booking
```

---

## Refactor branch setup

**⚠️ Create this branch from `develop` before starting any task.**

```bash
git checkout develop
git pull origin develop
git checkout -b refactor/frontend-APIs
git push -u origin refactor/frontend-APIs
```

---

## ✅ Task 1 — Replace `staffApi` method definitions

Remove verb-based methods (`approveBooking`, `rejectBooking`, `assignTable`, `markNoShow`, `modifyBooking`, `requestPayment`) and replace with RESTful equivalents (`postDecision`, `assignTables`, `patchBooking`, `refundPayment`) in `lib/api/endpoints.ts`.

**Branch:** `task/frontend-APIs-Task1-staffapi-methods` — created from `refactor/frontend-APIs`

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task1-staffapi-methods
```

**Files to modify:**
- `lib/api/endpoints.ts` — remove 6 methods, add 4 replacements

**Tests:**

```ts
// __tests__/api/staffApi.test.ts
import { staffApi } from '@/lib/api/endpoints';

test('staffApi exposes postDecision', () => {
  expect(typeof staffApi.postDecision).toBe('function');
});

test('staffApi exposes assignTables', () => {
  expect(typeof staffApi.assignTables).toBe('function');
});

test('staffApi exposes patchBooking', () => {
  expect(typeof staffApi.patchBooking).toBe('function');
});

test('staffApi exposes refundPayment', () => {
  expect(typeof staffApi.refundPayment).toBe('function');
});

test('staffApi does not expose deleted methods', () => {
  expect((staffApi as any).approveBooking).toBeUndefined();
  expect((staffApi as any).rejectBooking).toBeUndefined();
  expect((staffApi as any).assignTable).toBeUndefined();
  expect((staffApi as any).markNoShow).toBeUndefined();
  expect((staffApi as any).modifyBooking).toBeUndefined();
  expect((staffApi as any).requestPayment).toBeUndefined();
});
```

**Commit:**
```bash
git add lib/api/endpoints.ts
git commit -m "[TASK] 1 replace staffApi verb-endpoint methods with RESTful equivalents"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/api/staffApi.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task1-staffapi-methods
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task1-staffapi-methods
git push origin refactor/frontend-APIs
```

---

## ✅ Task 2 — Update `StaffBookingActions` mutations

Replace the single `approve` mutation (which was incorrectly reused for both approve and confirm-without-deposit) with three distinct mutations: `approve`, `confirmWithoutDeposit`, `decline` — each calling `staffApi.postDecision` with the correct `outcome`.

**Branch:** `task/frontend-APIs-Task2-booking-actions` — created from `refactor/frontend-APIs`

**⚠️ Create only after Task 1 is merged into `refactor/frontend-APIs`.**

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task2-booking-actions
```

**Files to modify:**
- `components/staff/StaffBookingActions.tsx` — replace single mutation with three; update button `onPress` bindings

**Tests:**

```tsx
// __tests__/staff/StaffBookingActions.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';
import { staffApi } from '@/lib/api/endpoints';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: { postDecision: jest.fn(async () => ({})) },
}));

const baseBooking = { id: 'b1', status: 'pending_review', party_size: 2, date: '2026-05-01', time: '19:00' };

test('approve button calls postDecision with outcome approved', async () => {
  render(<StaffBookingActions booking={baseBooking} tenant="r" token="tok" onActionComplete={jest.fn()} />);
  fireEvent.press(screen.getByText('Approve'));
  await waitFor(() =>
    expect(staffApi.postDecision).toHaveBeenCalledWith('r', 'tok', 'b1', { outcome: 'approved' })
  );
});

test('confirm-without-deposit button calls postDecision with correct outcome', async () => {
  const expiredBooking = { ...baseBooking, status: 'authorization_expired' };
  render(<StaffBookingActions booking={expiredBooking} tenant="r" token="tok" onActionComplete={jest.fn()} />);
  fireEvent.press(screen.getByText('Confirm without deposit'));
  await waitFor(() =>
    expect(staffApi.postDecision).toHaveBeenCalledWith('r', 'tok', 'b1', { outcome: 'confirmed_without_deposit' })
  );
});

test('reject button calls postDecision with outcome declined', async () => {
  render(<StaffBookingActions booking={baseBooking} tenant="r" token="tok" onActionComplete={jest.fn()} />);
  fireEvent.press(screen.getByText('Reject'));
  await waitFor(() =>
    expect(staffApi.postDecision).toHaveBeenCalledWith('r', 'tok', 'b1', expect.objectContaining({ outcome: 'declined' }))
  );
});
```

**Commit:**
```bash
git add components/staff/StaffBookingActions.tsx
git commit -m "[TASK] 2 split StaffBookingActions into three postDecision mutations"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/StaffBookingActions.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task2-booking-actions
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task2-booking-actions
git push origin refactor/frontend-APIs
```

---

## ✅ Task 3 — Update table assignment call site

Replace `staffApi.assignTable(tenant, token, booking.id, tableId)` with `staffApi.assignTables(tenant, token, booking.id, [tableId])`.

**Branch:** `task/frontend-APIs-Task3-assign-tables` — created from `refactor/frontend-APIs`

**⚠️ Create only after Task 2 is merged into `refactor/frontend-APIs`.**

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task3-assign-tables
```

**Files to modify:**
- `components/staff/AssignTableDialog.tsx` (or wherever `assignTable` is called)

**Tests:**

```tsx
// __tests__/staff/AssignTableDialog.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { AssignTableDialog } from '@/components/staff/AssignTableDialog';
import { staffApi } from '@/lib/api/endpoints';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: { assignTables: jest.fn(async () => ({ tables: ['t1'] })) },
}));

test('confirm calls assignTables with array-wrapped tableId', async () => {
  render(
    <AssignTableDialog bookingId="b1" tenant="r" token="tok" onComplete={jest.fn()} onClose={jest.fn()} />
  );
  fireEvent.press(screen.getByText('Table 1'));
  fireEvent.press(screen.getByText('Confirm'));
  await waitFor(() =>
    expect(staffApi.assignTables).toHaveBeenCalledWith('r', 'tok', 'b1', ['t1'])
  );
});
```

**Commit:**
```bash
git add components/staff/AssignTableDialog.tsx
git commit -m "[TASK] 3 update table assignment call site to assignTables"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/AssignTableDialog.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task3-assign-tables
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task3-assign-tables
git push origin refactor/frontend-APIs
```

---

## ✅ Task 4 — Update no-show and modify booking call sites

Replace `staffApi.markNoShow(...)` with `staffApi.patchBooking(..., { status: 'no_show' })` and `staffApi.modifyBooking(...)` with `staffApi.patchBooking(..., { starts_at, party_size, notes })`.

**Branch:** `task/frontend-APIs-Task4-noshow-modify` — created from `refactor/frontend-APIs`

**⚠️ Create only after Task 3 is merged into `refactor/frontend-APIs`.**

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task4-noshow-modify
```

**Files to modify:**
- Component(s) that call `markNoShow` and `modifyBooking` (e.g. `StaffBookingActions.tsx`, `ModifyBookingDialog.tsx`)

**Tests:**

```tsx
// __tests__/staff/NoShowAction.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';
import { staffApi } from '@/lib/api/endpoints';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: { postDecision: jest.fn(async () => ({})), patchBooking: jest.fn(async () => ({})) },
}));

const confirmedBooking = { id: 'b1', status: 'confirmed', party_size: 2, date: '2026-05-01', time: '19:00' };

test('no-show button calls patchBooking with status no_show', async () => {
  render(<StaffBookingActions booking={confirmedBooking} tenant="r" token="tok" onActionComplete={jest.fn()} />);
  fireEvent.press(screen.getByText('No show'));
  await waitFor(() =>
    expect(staffApi.patchBooking).toHaveBeenCalledWith('r', 'tok', 'b1', { status: 'no_show' })
  );
});

// __tests__/staff/ModifyBookingDialog.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { ModifyBookingDialog } from '@/components/staff/ModifyBookingDialog';
import { staffApi } from '@/lib/api/endpoints';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: { patchBooking: jest.fn(async () => ({})) },
}));

test('save calls patchBooking with updated fields', async () => {
  render(
    <ModifyBookingDialog bookingId="b1" tenant="r" token="tok" onComplete={jest.fn()} onClose={jest.fn()} />
  );
  fireEvent.changeText(screen.getByPlaceholderText('Party size'), '4');
  fireEvent.press(screen.getByText('Save'));
  await waitFor(() =>
    expect(staffApi.patchBooking).toHaveBeenCalledWith('r', 'tok', 'b1', expect.objectContaining({ party_size: 4 }))
  );
});
```

**Commit:**
```bash
git add components/staff/StaffBookingActions.tsx components/staff/ModifyBookingDialog.tsx
git commit -m "[TASK] 4 update no-show and modify call sites to patchBooking"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/NoShowAction.test.tsx __tests__/staff/ModifyBookingDialog.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task4-noshow-modify
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task4-noshow-modify
git push origin refactor/frontend-APIs
```

---

## ✅ Task 5 — Update refund call site and remove requestPayment

Update refund call site to use `staffApi.refundPayment(tenant, token, payment.id)` (URL now `/refunds/`). Remove any `requestPayment` mutation and its associated UI button — no backend endpoint exists.

**Branch:** `task/frontend-APIs-Task5-refund-cleanup` — created from `refactor/frontend-APIs`

**⚠️ Create only after Task 4 is merged into `refactor/frontend-APIs`.**

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task5-refund-cleanup
```

**Files to modify:**
- Component(s) that call `refundPayment` or `requestPayment` (e.g. `StaffBookingDetail.tsx`)

**Tests:**

```tsx
// __tests__/staff/RefundAction.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { StaffBookingDetail } from '@/app/(staff)/dashboard/bookings/[id]';
import { staffApi } from '@/lib/api/endpoints';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    getBooking: jest.fn(async () => ({
      id: 'b1', status: 'confirmed', payment: { id: 'p1', status: 'captured' }, party_size: 2,
    })),
    refundPayment: jest.fn(async () => ({ id: 'p1', status: 'refund_pending' })),
  },
}));

test('refund button calls refundPayment', async () => {
  render(<StaffBookingDetail />);
  await waitFor(() => fireEvent.press(screen.getByText('Refund deposit')));
  expect(staffApi.refundPayment).toHaveBeenCalledWith('r', 'tok', 'p1');
});

test('request payment button is not rendered', async () => {
  render(<StaffBookingDetail />);
  await waitFor(() => expect(screen.queryByText('Request payment')).toBeNull());
});
```

**Commit:**
```bash
git add app/(staff)/dashboard/bookings/\[id\].tsx
git commit -m "[TASK] 5 update refund call site and remove requestPayment"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/RefundAction.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task5-refund-cleanup
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task5-refund-cleanup
git push origin refactor/frontend-APIs
```

---

## ❌ Task 6 — Fix `publicApi.cancelBooking` to use DELETE

Replace the deleted `POST /api/public/bookings/{token}/cancel/` with `DELETE /api/public/bookings/{token}/`.

**Branch:** `task/frontend-APIs-Task6-cancel-booking` — created from `refactor/frontend-APIs`

**⚠️ Create only after Task 5 is merged into `refactor/frontend-APIs`.**

```bash
git checkout refactor/frontend-APIs
git pull origin refactor/frontend-APIs
git checkout -b task/frontend-APIs-Task6-cancel-booking
```

**Files to modify:**
- `lib/api/endpoints.ts` — update `cancelBooking` method

```ts
// before
cancelBooking(token: string) {
  return apiRequest<void>(`/api/public/bookings/${token}/cancel/`, { method: 'POST' });
},

// after
cancelBooking(token: string) {
  return apiRequest<void>(`/api/public/bookings/${token}/`, { method: 'DELETE' });
},
```

**Tests:**

```ts
// __tests__/api/publicApi.test.ts
import { expect, jest, test } from '@jest/globals';
import { publicApi } from '@/lib/api/endpoints';

const fetchMock = jest.fn() as jest.MockedFunction<typeof fetch>;
global.fetch = fetchMock;

test('cancelBooking calls DELETE on /api/public/bookings/{token}/', async () => {
  fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
  await publicApi.cancelBooking('tok123');
  expect(fetchMock).toHaveBeenCalledWith(
    expect.stringContaining('/api/public/bookings/tok123/'),
    expect.objectContaining({ method: 'DELETE' }),
  );
});

test('cancelBooking URL does not contain /cancel/', async () => {
  fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
  await publicApi.cancelBooking('tok123');
  const calledUrl = (fetchMock.mock.calls[0] as any)[0] as string;
  expect(calledUrl).not.toContain('/cancel/');
});
```

**Commit:**
```bash
git add lib/api/endpoints.ts __tests__/api/publicApi.test.ts
git commit -m "[TASK] 6 fix publicApi.cancelBooking to use DELETE instead of POST cancel"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/api/publicApi.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-APIs-Task6-cancel-booking
git checkout refactor/frontend-APIs
git merge task/frontend-APIs-Task6-cancel-booking
git push origin refactor/frontend-APIs
```

---

## ❌ Refactor complete — merge into develop

All tasks complete. Run the full pre-merge checklist one final time before merging to `develop`.

```bash
cd frontend
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
