# Branching Strategy — Phases 4–7: Customer Token Access, Payment, Staff Auth & Dashboard

References:
- Implementation plan: [`02-customer-and-staff-Phases-4-7.md`](./02-customer-and-staff-Phases-4-7.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text via i18n keys. `ApiError.code` is mapped to `t('error.<code>')` — never shown raw.
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
└── feature/frontend-mvp
    ├── feature/frontend-mvp-Phase4-customer-token       ← created from feature/frontend-mvp AFTER Phase 3 merged
    │   ├── task/frontend-mvp-Task4.1-booking-detail
    │   ├── task/frontend-mvp-Task4.2-customer-actions
    │   └── task/frontend-mvp-Task4.3-modify-form
    ├── feature/frontend-mvp-Phase5-stripe-payment       ← created from feature/frontend-mvp AFTER Phase 4 merged
    │   ├── task/frontend-mvp-Task5.1-stripe-bootstrap
    │   └── task/frontend-mvp-Task5.2-payment-screen
    ├── feature/frontend-mvp-Phase6-staff-auth           ← created from feature/frontend-mvp AFTER Phase 5 merged
    │   ├── task/frontend-mvp-Task6.1-login-screen
    │   └── task/frontend-mvp-Task6.2-auth-guard
    └── feature/frontend-mvp-Phase7-staff-dashboard      ← created from feature/frontend-mvp AFTER Phase 6 merged
        ├── task/frontend-mvp-Task7.1-bookings-list
        ├── task/frontend-mvp-Task7.2-booking-detail-actions
        └── task/frontend-mvp-Task7.3-walkins
```

---

## ❌ Phase 4 — Customer Tokenized Booking Access

Customers access their booking via a secure tokenized link sent by SMS/email — no authentication required. The token grants read, cancel, and modify access for that single booking only (technical doc §14a, business doc §1, §5).

**⚠️ Create this branch only after Phase 3 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase4-customer-token` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase4-customer-token
git push -u origin feature/frontend-mvp-Phase4-customer-token
```

---

### ✅ Task 4.1 — Booking Detail View

Implement `app/(public)/[tenant]/booking/[token]/index.tsx` and `BookingInfoCard`. Fetches booking via `publicApi.getBookingByToken(token)`. Displays status badge, booking details, and payment info (if any).

**Branch:** `task/frontend-mvp-Task4.1-booking-detail` — created from `feature/frontend-mvp-Phase4-customer-token`

```bash
git checkout feature/frontend-mvp-Phase4-customer-token
git pull origin feature/frontend-mvp-Phase4-customer-token
git checkout -b task/frontend-mvp-Task4.1-booking-detail
```

**Files to create:**
- `app/(public)/[tenant]/booking/[token]/index.tsx` — fetches booking, renders `StatusBadge` + `BookingInfoCard` + `CustomerBookingActions` (stub)
- `components/booking/BookingInfoCard.tsx` — displays date, time, party size, table, payment status, notes

**Tests:**

```tsx
// __tests__/booking/BookingInfoCard.test.tsx
import { render, screen } from '@testing-library/react-native';
import { BookingInfoCard } from '@/components/booking/BookingInfoCard';

const booking = {
  id: '1', status: 'confirmed' as const,
  date: '2025-06-15', time: '19:30', party_size: 4,
  customer: { name: 'Mario Rossi', phone: '+39333', locale: 'it' },
  created_at: '2025-06-01T10:00:00Z',
};

test('displays date, time and party size', () => {
  render(<BookingInfoCard booking={booking} />);
  expect(screen.getByText('2025-06-15')).toBeTruthy();
  expect(screen.getByText(/19:30/)).toBeTruthy();
  expect(screen.getByText(/4 guests/)).toBeTruthy();
});

test('does not crash when payment is absent', () => {
  expect(() => render(<BookingInfoCard booking={booking} />)).not.toThrow();
});
```

**Commit:**
```bash
git add app/(public)/[tenant]/booking/ components/booking/BookingInfoCard.tsx
git commit -m "[TASK] 4.1 add customer tokenized booking detail view"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/booking/BookingInfoCard.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task4.1-booking-detail
git checkout feature/frontend-mvp-Phase4-customer-token
git merge task/frontend-mvp-Task4.1-booking-detail
git push origin feature/frontend-mvp-Phase4-customer-token
```

---

### ✅ Task 4.2 — Customer Action Controls

Implement `CustomerBookingActions`. Derives available actions from booking status: cancel, modify, pay. Actions are shown only for statuses where they are valid (e.g., cannot cancel a `declined` booking). Cutoff enforcement is server-side; the frontend reflects the result via `ApiError`.

**Branch:** `task/frontend-mvp-Task4.2-customer-actions` — created from `feature/frontend-mvp-Phase4-customer-token`

```bash
git checkout feature/frontend-mvp-Phase4-customer-token
git pull origin feature/frontend-mvp-Phase4-customer-token
git checkout -b task/frontend-mvp-Task4.2-customer-actions
```

**Files to create:**
- `components/booking/CustomerBookingActions.tsx` — conditionally renders pay, modify, and cancel buttons based on `booking.status`

**Allowed statuses per action:**

| Action | Statuses |
|--------|---------|
| cancel | `pending_review`, `pending_payment`, `confirmed`, `confirmed_without_deposit` |
| modify | `pending_review`, `confirmed`, `confirmed_without_deposit` |
| pay | `pending_payment` |

**Tests:**

```tsx
// __tests__/booking/CustomerBookingActions.test.tsx
import { render, screen } from '@testing-library/react-native';
import { CustomerBookingActions } from '@/components/booking/CustomerBookingActions';

const base = { id: '1', date: '2025-06-15', time: '19:30', party_size: 2, customer: { name: 'A', phone: '+39', locale: 'it' }, created_at: '' };

test('shows cancel button for confirmed booking', () => {
  render(<CustomerBookingActions booking={{ ...base, status: 'confirmed' }} token="tok" onCancel={jest.fn()} cancelling={false} onPay={jest.fn()} />);
  expect(screen.getByText('Cancel booking')).toBeTruthy();
});

test('shows pay button only for pending_payment', () => {
  render(<CustomerBookingActions booking={{ ...base, status: 'pending_payment' }} token="tok" onCancel={jest.fn()} cancelling={false} onPay={jest.fn()} />);
  expect(screen.getByText('Pay deposit')).toBeTruthy();
});

test('shows no action buttons for declined booking', () => {
  render(<CustomerBookingActions booking={{ ...base, status: 'declined' }} token="tok" onCancel={jest.fn()} cancelling={false} onPay={jest.fn()} />);
  expect(screen.queryByText('Cancel booking')).toBeNull();
  expect(screen.queryByText('Pay deposit')).toBeNull();
});
```

**Commit:**
```bash
git add components/booking/CustomerBookingActions.tsx
git commit -m "[TASK] 4.2 add customer booking action controls"
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
git push origin task/frontend-mvp-Task4.2-customer-actions
git checkout feature/frontend-mvp-Phase4-customer-token
git merge task/frontend-mvp-Task4.2-customer-actions
git push origin feature/frontend-mvp-Phase4-customer-token
```

---

### ✅ Task 4.3 — Modify Booking Form

Implement `ModifyBookingForm`. Calls `publicApi.modifyBooking(token, payload)` on submit. Modification may trigger re-approval (the API handles status transition); the frontend only reflects the updated status after invalidating the query.

**Branch:** `task/frontend-mvp-Task4.3-modify-form` — created from `feature/frontend-mvp-Phase4-customer-token`

```bash
git checkout feature/frontend-mvp-Phase4-customer-token
git pull origin feature/frontend-mvp-Phase4-customer-token
git checkout -b task/frontend-mvp-Task4.3-modify-form
```

**Files to create:**
- `components/booking/ModifyBookingForm.tsx` — party size + date picker, reuses `PartySizeSelector` and `DatePicker` from Phase 3; calls `modifyBooking` mutation on submit

**Tests:**

```tsx
// __tests__/booking/ModifyBookingForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { ModifyBookingForm } from '@/components/booking/ModifyBookingForm';

jest.mock('@/lib/api/endpoints', () => ({
  publicApi: { modifyBooking: jest.fn(async () => ({})) },
}));

const booking = { id: '1', status: 'confirmed' as const, date: '2025-06-15', time: '19:30', party_size: 2, customer: { name: 'A', phone: '+39', locale: 'it' }, created_at: '' };

test('save button triggers modifyBooking', async () => {
  const { publicApi } = require('@/lib/api/endpoints');
  const onDone = jest.fn();
  render(<ModifyBookingForm token="tok" booking={booking} onDone={onDone} />);
  fireEvent.press(screen.getByText('Save'));
  await waitFor(() => expect(publicApi.modifyBooking).toHaveBeenCalledWith('tok', expect.any(Object)));
});
```

**Commit:**
```bash
git add components/booking/ModifyBookingForm.tsx
git commit -m "[TASK] 4.3 add customer modify booking form"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/booking/ModifyBookingForm.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task4.3-modify-form
git checkout feature/frontend-mvp-Phase4-customer-token
git merge task/frontend-mvp-Task4.3-modify-form
git push origin feature/frontend-mvp-Phase4-customer-token
```

---

### ✅ Phase 4 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase4-customer-token
git push origin feature/frontend-mvp
```

---

## ❌ Phase 5 — Customer Payment Flow (Stripe)

Near-term flow: customer authorizes a `PaymentIntent` with `capture_method=manual` via Stripe Payment Element. After successful authorization the booking remains `pending_review`; staff approval triggers capture (business doc §4, technical doc §6).

**⚠️ Create this branch only after Phase 4 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase5-stripe-payment` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase5-stripe-payment
git push -u origin feature/frontend-mvp-Phase5-stripe-payment
```

---

### ❌ Task 5.1 — Stripe Bootstrap

Create `lib/stripe.ts` with the lazily-loaded `stripePromise`. The publishable key is read from `ENV.STRIPE_KEY` (set via `EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY`) — never hardcoded.

**Branch:** `task/frontend-mvp-Task5.1-stripe-bootstrap` — created from `feature/frontend-mvp-Phase5-stripe-payment`

```bash
git checkout feature/frontend-mvp-Phase5-stripe-payment
git pull origin feature/frontend-mvp-Phase5-stripe-payment
git checkout -b task/frontend-mvp-Task5.1-stripe-bootstrap
```

**Files to create:**

`lib/stripe.ts`:

```ts
import { loadStripe } from '@stripe/stripe-js';
import { ENV } from './env';

export const stripePromise = loadStripe(ENV.STRIPE_KEY);
```

**Tests:**

```ts
// __tests__/stripe.test.ts
jest.mock('@stripe/stripe-js', () => ({ loadStripe: jest.fn(() => Promise.resolve({})) }));
jest.mock('@/lib/env', () => ({ ENV: { STRIPE_KEY: 'pk_test_stub' } }));

test('stripePromise calls loadStripe with env key', async () => {
  const { loadStripe } = require('@stripe/stripe-js');
  require('@/lib/stripe');
  expect(loadStripe).toHaveBeenCalledWith('pk_test_stub');
});
```

**Commit:**
```bash
git add lib/stripe.ts
git commit -m "[TASK] 5.1 add Stripe bootstrap (loadStripe with env key)"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/stripe.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task5.1-stripe-bootstrap
git checkout feature/frontend-mvp-Phase5-stripe-payment
git merge task/frontend-mvp-Task5.1-stripe-bootstrap
git push origin feature/frontend-mvp-Phase5-stripe-payment
```

---

### ❌ Task 5.2 — Payment Screen & Form

Implement `app/(public)/[tenant]/booking/[token]/pay.tsx` (fetches client secret from `publicApi.getPaymentIntent`) and `components/payment/PaymentForm.tsx` (wraps Stripe `PaymentElement`). On success Stripe redirects to the booking detail page; on failure the error is shown inline. No card data is ever stored locally (technical doc §15).

**Branch:** `task/frontend-mvp-Task5.2-payment-screen` — created from `feature/frontend-mvp-Phase5-stripe-payment`

```bash
git checkout feature/frontend-mvp-Phase5-stripe-payment
git pull origin feature/frontend-mvp-Phase5-stripe-payment
git checkout -b task/frontend-mvp-Task5.2-payment-screen
```

**Files to create:**
- `app/(public)/[tenant]/booking/[token]/pay.tsx` — fetches `client_secret`, wraps with `<Elements>`
- `components/payment/PaymentForm.tsx` — uses `useStripe`, `useElements`, `stripe.confirmPayment`; `return_url` points to booking detail route

**`return_url` construction:**

```ts
return_url: `${window.location.origin}${ROUTES.bookingDetail(token)}`
```

**Tests:**

```tsx
// __tests__/payment/PaymentForm.test.tsx
jest.mock('@stripe/react-stripe-js', () => ({
  PaymentElement: () => null,
  useStripe: () => ({ confirmPayment: jest.fn(async () => ({ error: null })) }),
  useElements: () => ({}),
}));

import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { PaymentForm } from '@/components/payment/PaymentForm';

test('calls confirmPayment on submit', async () => {
  const { useStripe } = require('@stripe/react-stripe-js');
  render(<PaymentForm token="tok" />);
  fireEvent.press(screen.getByText('Confirm'));
  await waitFor(() => expect(useStripe().confirmPayment).toHaveBeenCalled());
});

test('displays stripe error message on failure', async () => {
  const { useStripe } = require('@stripe/react-stripe-js');
  useStripe().confirmPayment.mockResolvedValueOnce({ error: { message: 'Card declined' } });
  render(<PaymentForm token="tok" />);
  fireEvent.press(screen.getByText('Confirm'));
  await waitFor(() => expect(screen.getByText('Card declined')).toBeTruthy());
});
```

**Commit:**
```bash
git add app/(public)/[tenant]/booking/[token]/pay.tsx components/payment/
git commit -m "[TASK] 5.2 add Stripe payment screen and PaymentElement form"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/payment/PaymentForm.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task5.2-payment-screen
git checkout feature/frontend-mvp-Phase5-stripe-payment
git merge task/frontend-mvp-Task5.2-payment-screen
git push origin feature/frontend-mvp-Phase5-stripe-payment
```

---

### ❌ Phase 5 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase5-stripe-payment
git push origin feature/frontend-mvp
```

---

## ❌ Phase 6 — Staff Authentication

Staff authenticate via email + password. JWT is stored in `sessionStorage` on web (wiped on tab close) and `SecureStore` on native. The auth guard redirects unauthenticated users to `/login` before rendering any staff screen (business doc §8, technical doc §5).

**⚠️ Create this branch only after Phase 5 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase6-staff-auth` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase6-staff-auth
git push -u origin feature/frontend-mvp-Phase6-staff-auth
```

---

### ❌ Task 6.1 — Login Screen

Implement `app/(staff)/login.tsx`. Calls `auth.login(email, password, tenant)` from `AuthContext`; on success redirects to `/dashboard`; on `ApiError` shows `t('staff.login.error')`.

**Branch:** `task/frontend-mvp-Task6.1-login-screen` — created from `feature/frontend-mvp-Phase6-staff-auth`

```bash
git checkout feature/frontend-mvp-Phase6-staff-auth
git pull origin feature/frontend-mvp-Phase6-staff-auth
git checkout -b task/frontend-mvp-Task6.1-login-screen
```

**Files to create:**
- `app/(staff)/login.tsx` — email, password, tenant fields; submit calls `useAuth().login`; error state mapped via i18n

**Tests:**

```tsx
// __tests__/staff/LoginScreen.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import LoginScreen from '@/app/(staff)/login';

const mockLogin = jest.fn();
jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => ({ login: mockLogin, accessToken: null, tenant: null, isLoading: false }),
}));
jest.mock('expo-router', () => ({ useRouter: () => ({ replace: jest.fn() }) }));

test('calls login with email, password and tenant', async () => {
  mockLogin.mockResolvedValueOnce(undefined);
  render(<LoginScreen />);
  fireEvent.changeText(screen.getByLabelText('Email'), 'staff@restaurant.it');
  fireEvent.changeText(screen.getByLabelText('Password'), 'secret');
  fireEvent.changeText(screen.getByLabelText('Restaurant'), 'myrestaurant');
  fireEvent.press(screen.getByText('Sign in'));
  await waitFor(() => expect(mockLogin).toHaveBeenCalledWith('staff@restaurant.it', 'secret', 'myrestaurant'));
});

test('shows error message on login failure', async () => {
  const { ApiError } = require('@/lib/api/client');
  mockLogin.mockRejectedValueOnce(new ApiError(401, 'INVALID_CREDENTIALS'));
  render(<LoginScreen />);
  fireEvent.changeText(screen.getByLabelText('Email'), 'x@x.com');
  fireEvent.changeText(screen.getByLabelText('Password'), 'wrong');
  fireEvent.changeText(screen.getByLabelText('Restaurant'), 'r');
  fireEvent.press(screen.getByText('Sign in'));
  await waitFor(() => expect(screen.getByText('Invalid email or password')).toBeTruthy());
});
```

**Commit:**
```bash
git add app/(staff)/login.tsx
git commit -m "[TASK] 6.1 add staff login screen"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/LoginScreen.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task6.1-login-screen
git checkout feature/frontend-mvp-Phase6-staff-auth
git merge task/frontend-mvp-Task6.1-login-screen
git push origin feature/frontend-mvp-Phase6-staff-auth
```

---

### ❌ Task 6.2 — Auth Guard Layout

Implement `app/(staff)/_layout.tsx` with `AuthProvider` + `Guard`. Guard watches `accessToken` and `isLoading`; unauthenticated navigation to any staff route redirects to `/login`.

**Branch:** `task/frontend-mvp-Task6.2-auth-guard` — created from `feature/frontend-mvp-Phase6-staff-auth`

```bash
git checkout feature/frontend-mvp-Phase6-staff-auth
git pull origin feature/frontend-mvp-Phase6-staff-auth
git checkout -b task/frontend-mvp-Task6.2-auth-guard
```

**Files to create:**
- `app/(staff)/_layout.tsx` — wraps `<AuthProvider>` + `<Guard>`; Guard uses `useSegments` to detect staff routes and calls `router.replace('/login')` when unauthenticated

**Tests:**

```tsx
// __tests__/staff/AuthGuard.test.tsx
jest.mock('@/lib/auth/AuthContext', () => ({
  AuthProvider: ({ children }: any) => children,
  useAuth: jest.fn(),
}));
jest.mock('expo-router', () => ({
  Slot: () => null,
  useRouter: () => ({ replace: jest.fn() }),
  useSegments: () => ['(staff)', 'dashboard'],
}));

import { render } from '@testing-library/react-native';
import StaffLayout from '@/app/(staff)/_layout';
import { useAuth } from '@/lib/auth/AuthContext';

test('redirects to login when not authenticated', () => {
  const replace = jest.fn();
  (useAuth as jest.Mock).mockReturnValue({ accessToken: null, isLoading: false });
  jest.mocked(require('expo-router').useRouter).mockReturnValue({ replace });
  render(<StaffLayout />);
  expect(replace).toHaveBeenCalledWith('/login');
});

test('does not redirect when authenticated', () => {
  const replace = jest.fn();
  (useAuth as jest.Mock).mockReturnValue({ accessToken: 'tok', isLoading: false });
  jest.mocked(require('expo-router').useRouter).mockReturnValue({ replace });
  render(<StaffLayout />);
  expect(replace).not.toHaveBeenCalled();
});
```

**Commit:**
```bash
git add app/(staff)/_layout.tsx
git commit -m "[TASK] 6.2 add staff auth guard layout"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/AuthGuard.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task6.2-auth-guard
git checkout feature/frontend-mvp-Phase6-staff-auth
git merge task/frontend-mvp-Task6.2-auth-guard
git push origin feature/frontend-mvp-Phase6-staff-auth
```

---

### ❌ Phase 6 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase6-staff-auth
git push origin feature/frontend-mvp
```

---

## ❌ Phase 7 — Staff Bookings Dashboard

Bookings list with status filters, booking detail with staff actions (approve, reject, assign table), and walk-in creation. Expiration sweep is triggered opportunistically on dashboard load — no Celery in MVP (technical doc §8).

**⚠️ Create this branch only after Phase 6 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase7-staff-dashboard` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase7-staff-dashboard
git push -u origin feature/frontend-mvp-Phase7-staff-dashboard
```

---

### ❌ Task 7.1 — Bookings List

Implement `app/(staff)/dashboard/index.tsx`, `BookingCard`, and `FilterTabs`. Triggers `staffApi.triggerExpirationSweep` on mount. Polls every 60 seconds via `refetchInterval`. Filter options: all, pending, confirmed, declined.

**Branch:** `task/frontend-mvp-Task7.1-bookings-list` — created from `feature/frontend-mvp-Phase7-staff-dashboard`

```bash
git checkout feature/frontend-mvp-Phase7-staff-dashboard
git pull origin feature/frontend-mvp-Phase7-staff-dashboard
git checkout -b task/frontend-mvp-Task7.1-bookings-list
```

**Files to create:**
- `app/(staff)/dashboard/index.tsx` — list screen with sweep-on-mount, filter state, `refetchInterval: 60_000`
- `app/(staff)/dashboard/_layout.tsx` — tab navigator layout
- `components/staff/BookingCard.tsx` — pressable card showing name, status badge, date/time, party size
- `components/staff/FilterTabs.tsx` — horizontal tab bar for status filter

**Tests:**

```tsx
// __tests__/staff/FilterTabs.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { FilterTabs } from '@/components/staff/FilterTabs';

test('calls onSelect with correct index', () => {
  const onSelect = jest.fn();
  render(<FilterTabs labels={['All', 'Pending', 'Confirmed']} selected={0} onSelect={onSelect} />);
  fireEvent.press(screen.getByText('Pending'));
  expect(onSelect).toHaveBeenCalledWith(1);
});

test('highlights selected tab', () => {
  render(<FilterTabs labels={['All', 'Pending']} selected={1} onSelect={jest.fn()} />);
  // Pending should be visually distinct — test via accessible state or style
  expect(screen.getByText('Pending')).toBeTruthy();
});
```

**Commit:**
```bash
git add app/(staff)/dashboard/index.tsx app/(staff)/dashboard/_layout.tsx components/staff/BookingCard.tsx components/staff/FilterTabs.tsx
git commit -m "[TASK] 7.1 add staff bookings list with filter tabs and expiration sweep"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/FilterTabs.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task7.1-bookings-list
git checkout feature/frontend-mvp-Phase7-staff-dashboard
git merge task/frontend-mvp-Task7.1-bookings-list
git push origin feature/frontend-mvp-Phase7-staff-dashboard
```

---

### ❌ Task 7.2 — Booking Detail & Staff Actions

Implement `app/(staff)/dashboard/bookings/[id].tsx`, `StaffBookingActions`, `RejectDialog`, and `AssignTableDialog`. Actions available per status:

| Action | Visible when |
|--------|-------------|
| Approve | `pending_review`, `authorization_expired` |
| Confirm without deposit | `authorization_expired` only |
| Reject | `pending_review`, `authorization_expired` |
| Assign table | `pending_review`, `authorization_expired`, `confirmed`, `confirmed_without_deposit` |

**Branch:** `task/frontend-mvp-Task7.2-booking-detail-actions` — created from `feature/frontend-mvp-Phase7-staff-dashboard`

```bash
git checkout feature/frontend-mvp-Phase7-staff-dashboard
git pull origin feature/frontend-mvp-Phase7-staff-dashboard
git checkout -b task/frontend-mvp-Task7.2-booking-detail-actions
```

**Files to create:**
- `app/(staff)/dashboard/bookings/[id].tsx` — fetches booking, invalidates on action
- `components/staff/StaffBookingActions.tsx` — conditional action buttons, toggles dialogs
- `components/staff/RejectDialog.tsx` — text input for rejection reason, calls `staffApi.rejectBooking`
- `components/staff/AssignTableDialog.tsx` — table picker, calls `staffApi.assignTable`

**Tests:**

```tsx
// __tests__/staff/StaffBookingActions.test.tsx
import { render, screen } from '@testing-library/react-native';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';

const base = { id: '1', date: '2025-06-15', time: '19:30', party_size: 2, customer: { name: 'A', phone: '+39', locale: 'it' }, created_at: '' };

test('shows approve and reject for pending_review', () => {
  render(<StaffBookingActions booking={{ ...base, status: 'pending_review' }} tenant="r" token="tok" onActionComplete={jest.fn()} />);
  expect(screen.getByText('Approve')).toBeTruthy();
  expect(screen.getByText('Reject')).toBeTruthy();
});

test('shows confirm without deposit for authorization_expired', () => {
  render(<StaffBookingActions booking={{ ...base, status: 'authorization_expired' }} tenant="r" token="tok" onActionComplete={jest.fn()} />);
  expect(screen.getByText('Confirm without deposit')).toBeTruthy();
});

test('does not show approve for confirmed booking', () => {
  render(<StaffBookingActions booking={{ ...base, status: 'confirmed' }} tenant="r" token="tok" onActionComplete={jest.fn()} />);
  expect(screen.queryByText('Approve')).toBeNull();
});
```

**Commit:**
```bash
git add app/(staff)/dashboard/bookings/ components/staff/StaffBookingActions.tsx components/staff/RejectDialog.tsx components/staff/AssignTableDialog.tsx
git commit -m "[TASK] 7.2 add staff booking detail and action controls"
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
git push origin task/frontend-mvp-Task7.2-booking-detail-actions
git checkout feature/frontend-mvp-Phase7-staff-dashboard
git merge task/frontend-mvp-Task7.2-booking-detail-actions
git push origin feature/frontend-mvp-Phase7-staff-dashboard
```

---

### ❌ Task 7.3 — Walk-in Form

Implement `app/(staff)/dashboard/walkins.tsx`. Walk-ins occupy capacity and can be assigned a table, but do not create a booking and require no customer phone number (business doc §10).

**Branch:** `task/frontend-mvp-Task7.3-walkins` — created from `feature/frontend-mvp-Phase7-staff-dashboard`

```bash
git checkout feature/frontend-mvp-Phase7-staff-dashboard
git pull origin feature/frontend-mvp-Phase7-staff-dashboard
git checkout -b task/frontend-mvp-Task7.3-walkins
```

**Files to create:**
- `app/(staff)/dashboard/walkins.tsx` — party size selector + submit; calls `staffApi.createWalkin`; shows transient success feedback

**Tests:**

```tsx
// __tests__/staff/WalkinsScreen.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import WalkinsScreen from '@/app/(staff)/dashboard/walkins';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: { createWalkin: jest.fn(async () => ({ id: 'w1' })) },
}));
jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => ({ accessToken: 'tok', tenant: 'r' }),
}));

test('calls createWalkin with selected party size', async () => {
  const { staffApi } = require('@/lib/api/endpoints');
  render(<WalkinsScreen />);
  fireEvent.press(screen.getByText('+'));   // partySize 2 → 3
  fireEvent.press(screen.getByText('Add walk-in'));
  await waitFor(() => expect(staffApi.createWalkin).toHaveBeenCalledWith('r', 'tok', { party_size: 3 }));
});
```

**Commit:**
```bash
git add app/(staff)/dashboard/walkins.tsx
git commit -m "[TASK] 7.3 add staff walk-in form"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/WalkinsScreen.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task7.3-walkins
git checkout feature/frontend-mvp-Phase7-staff-dashboard
git merge task/frontend-mvp-Task7.3-walkins
git push origin feature/frontend-mvp-Phase7-staff-dashboard
```

---

### ❌ Phase 7 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase7-staff-dashboard
git push origin feature/frontend-mvp
```
