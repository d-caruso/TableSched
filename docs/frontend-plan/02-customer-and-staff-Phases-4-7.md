# Phases 4–7 — Customer Token Access, Payment, Staff Auth & Dashboard

Covers customer tokenized booking access (view/cancel/modify), Stripe payment flow, staff authentication, and the staff bookings dashboard (list, detail, actions, walk-ins).

---

## Phase 4 — Customer Tokenized Booking Access

Branch: `feature/frontend-customer-token`

Customers do not authenticate. After booking submission they receive a secure tokenized link via SMS/email. The token grants read, cancel, and modify access for that single booking (business doc §1, technical doc §14a).

### Task 4.1 — Booking detail screen

Completed in the frontend implementation branch.

`app/(public)/[tenant]/booking/[token]/index.tsx`:

```tsx
import { ScrollView, YStack, Spinner } from 'tamagui';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { publicApi } from '@/lib/api/endpoints';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { BookingInfoCard } from '@/components/booking/BookingInfoCard';
import { CustomerBookingActions } from '@/components/booking/CustomerBookingActions';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { ROUTES } from '@/constants/routes';

export default function CustomerBookingPage() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const { t } = useTranslation();
  const router = useRouter();
  const qc = useQueryClient();

  const { data: booking, isLoading, error } = useQuery({
    queryKey: ['booking', token],
    queryFn: () => publicApi.getBookingByToken(token),
    enabled: !!token,
  });

  const cancel = useMutation({
    mutationFn: () => publicApi.cancelBooking(token),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['booking', token] }),
  });

  if (isLoading) return <Spinner size="large" />;
  if (error || !booking) return <ErrorMessage error={error} />;

  return (
    <ScrollView>
      <YStack maxWidth={600} alignSelf="center" width="100%" padding="$4" gap="$4">
        <StatusBadge status={booking.status} />
        <BookingInfoCard booking={booking} />
        <CustomerBookingActions
          booking={booking}
          token={token}
          onCancel={() => cancel.mutate()}
          cancelling={cancel.isPending}
          onPay={() => router.push(ROUTES.bookingPay(token))}
        />
      </YStack>
    </ScrollView>
  );
}
```

`components/booking/BookingInfoCard.tsx`:

```tsx
import { YStack, XStack, Text } from 'tamagui';
import type { Booking } from '@/lib/api/types';
import { useTranslation } from 'react-i18next';

export function BookingInfoCard({ booking }: { booking: Booking }) {
  const { t } = useTranslation();
  return (
    <YStack gap="$2" padding="$3" borderWidth={1} borderColor="$borderColor" borderRadius="$4">
      <Text fontWeight="700" fontSize="$5">{booking.customer.name}</Text>
      <Text>{booking.date} · {booking.time}</Text>
      <Text>{t('booking.guestCount', { count: booking.party_size })}</Text>
      {booking.table && <Text>{booking.table.name}</Text>}
      {booking.payment && (
        <Text color="$placeholderColor" fontSize="$3">
          {t(`booking.payment_status.${booking.payment.status}`)} ·{' '}
          {(booking.payment.amount / 100).toFixed(2)} {booking.payment.currency.toUpperCase()}
        </Text>
      )}
      {booking.notes && <Text color="$placeholderColor">{booking.notes}</Text>}
    </YStack>
  );
}
```

### Task 4.2 — Customer action controls

`components/booking/CustomerBookingActions.tsx`:

```tsx
import { YStack } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { Booking } from '@/lib/api/types';
import { AppButton } from '@/components/ui/AppButton';
import { ModifyBookingForm } from '@/components/booking/ModifyBookingForm';

const CANCELLABLE: Booking['status'][] = ['pending_review', 'pending_payment', 'confirmed', 'confirmed_without_deposit'];
const PAYABLE: Booking['status'][] = ['pending_payment'];
const MODIFIABLE: Booking['status'][] = ['pending_review', 'confirmed', 'confirmed_without_deposit'];

interface Props {
  booking: Booking;
  token: string;
  onCancel: () => void;
  cancelling: boolean;
  onPay: () => void;
}

export function CustomerBookingActions({ booking, token, onCancel, cancelling, onPay }: Props) {
  const { t } = useTranslation();
  const [modifying, setModifying] = useState(false);

  if (modifying) {
    return <ModifyBookingForm token={token} booking={booking} onDone={() => setModifying(false)} />;
  }

  return (
    <YStack gap="$3">
      {PAYABLE.includes(booking.status) && (
        <AppButton onPress={onPay}>{t('booking.actions.pay')}</AppButton>
      )}
      {MODIFIABLE.includes(booking.status) && (
        <AppButton variant="secondary" onPress={() => setModifying(true)}>
          {t('booking.actions.modify')}
        </AppButton>
      )}
      {CANCELLABLE.includes(booking.status) && (
        <AppButton variant="danger" onPress={onCancel} loading={cancelling}>
          {t('booking.actions.cancel')}
        </AppButton>
      )}
    </YStack>
  );
}
```

### Task 4.3 — Modify booking form

Completed in the frontend implementation branch.

`components/booking/ModifyBookingForm.tsx`:

```tsx
import { YStack } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { publicApi } from '@/lib/api/endpoints';
import type { Booking } from '@/lib/api/types';
import { AppButton } from '@/components/ui/AppButton';
import { DatePicker } from '@/components/booking/DatePicker';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

interface Props { token: string; booking: Booking; onDone: () => void; }

export function ModifyBookingForm({ token, booking, onDone }: Props) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [date, setDate] = useState(booking.date);
  const [time, setTime] = useState(booking.time);
  const [partySize, setPartySize] = useState(booking.party_size);

  const { mutate, isPending, error } = useMutation({
    mutationFn: () => publicApi.modifyBooking(token, { date, time, party_size: partySize }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['booking', token] }); onDone(); },
  });

  return (
    <YStack gap="$3">
      {error && <ErrorMessage error={error} />}
      <PartySizeSelector value={partySize} onChange={setPartySize} />
      <DatePicker label={t('booking.form.date')} value={date} onChange={setDate} minDate={new Date()} maxDays={90} />
      <AppButton onPress={() => mutate()} loading={isPending}>{t('common.save')}</AppButton>
      <AppButton variant="secondary" onPress={onDone}>{t('common.cancel')}</AppButton>
    </YStack>
  );
}
```

**Verification — Phase 4:**
- Navigate to `/booking/{valid-token}` — booking detail and status displayed
- Cancel booking — status updates to `cancelled_by_customer`
- Modify booking — re-approval triggered (status back to `pending_review`)
- Navigate to expired/invalid token — `TOKEN_EXPIRED` or `BOOKING_NOT_FOUND` error shown

---

## Phase 5 — Customer Payment Flow (Stripe)

Branch: `feature/frontend-stripe-payment`

Near-term flow: customer authorizes a PaymentIntent with `capture_method=manual`. Staff approval triggers capture. (business doc §4)

### Task 5.1 — Stripe bootstrap

Completed in the frontend implementation branch.

`lib/stripe.ts`:

```ts
import { loadStripe } from '@stripe/stripe-js';
import { ENV } from './env';

export const stripePromise = loadStripe(ENV.STRIPE_KEY);
```

### Task 5.2 — Payment screen

Completed in the frontend implementation branch.

`app/(public)/[tenant]/booking/[token]/pay.tsx`:

```tsx
import { YStack, Text, Spinner } from 'tamagui';
import { useLocalSearchParams } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Elements } from '@stripe/react-stripe-js';
import { useTranslation } from 'react-i18next';
import { stripePromise } from '@/lib/stripe';
import { publicApi } from '@/lib/api/endpoints';
import { PaymentForm } from '@/components/payment/PaymentForm';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

export default function PaymentPage() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const { t } = useTranslation();

  const { data, isLoading, error } = useQuery({
    queryKey: ['payment-intent', token],
    queryFn: () => publicApi.getPaymentIntent(token),
    enabled: !!token,
  });

  if (isLoading) return <Spinner size="large" />;
  if (error || !data) return <ErrorMessage error={error} />;

  return (
    <YStack maxWidth={480} alignSelf="center" width="100%" padding="$4" gap="$4">
      <Text fontWeight="700" fontSize="$5">{t('booking.actions.pay')}</Text>
      <Elements stripe={stripePromise} options={{ clientSecret: data.client_secret }}>
        <PaymentForm token={token} />
      </Elements>
    </YStack>
  );
}
```

### Task 5.3 — Stripe Payment Element form

`components/payment/PaymentForm.tsx`:

```tsx
import { YStack, Text } from 'tamagui';
import { useState } from 'react';
import { Platform } from 'react-native';
import { PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { useTranslation } from 'react-i18next';
import { AppButton } from '@/components/ui/AppButton';
import { ENV } from '@/lib/env';
import { ROUTES } from '@/constants/routes';

const getOrigin = () =>
  Platform.OS === 'web' && typeof window !== 'undefined'
    ? window.location.origin
    : ENV.API_BASE_URL;

export function PaymentForm({ token }: { token: string }) {
  const { t } = useTranslation();
  const stripe = useStripe();
  const elements = useElements();
  const [stripeError, setStripeError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!stripe || !elements) return;
    setLoading(true);
    setStripeError(null);

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        // Stripe redirects here on success; booking detail will show updated status
        return_url: `${getOrigin()}${ROUTES.bookingDetail(token)}`,
      },
    });

    // Only reached on error; success causes a page redirect
    if (error) {
      setStripeError(error.message ?? t('common.error'));
      setLoading(false);
    }
  };

  return (
    <YStack gap="$4">
      <PaymentElement />
      {stripeError && <Text color="$danger">{stripeError}</Text>}
      <AppButton onPress={handleSubmit} loading={loading}>{t('common.confirm')}</AppButton>
    </YStack>
  );
}
```

**Verification — Phase 5:**
- Use Stripe test card `4242 4242 4242 4242` — redirected to booking detail
- Booking status updates to `confirmed` after staff approval + capture
- Failed card (`4000 0000 0000 9995`) — Stripe error displayed inline, booking unchanged

---

## Phase 6 — Staff Authentication

Branch: `feature/frontend-staff-auth`

Staff (manager / staff roles) authenticate via email + password. Customers never authenticate (business doc §8, technical doc §5). JWT stored in `sessionStorage` on web (wiped on tab close), `SecureStore` on native.

### Task 6.1 — Login screen

`app/(staff)/login.tsx`:

```tsx
import { YStack, Text } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useRouter } from 'expo-router';
import { useAuth } from '@/lib/auth/AuthContext';
import { AppButton } from '@/components/ui/AppButton';
import { AppInput } from '@/components/ui/AppInput';
import { ApiError } from '@/lib/api/client';
import { ROUTES } from '@/constants/routes';

export default function LoginScreen() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tenant, setTenant] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password || !tenant) return;
    setLoading(true);
    setError(null);
    try {
      await login(email, password, tenant);
      router.replace(ROUTES.dashboard);
    } catch (e) {
      setError(e instanceof ApiError ? t('staff.login.error') : t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
      <YStack width="100%" maxWidth={380} gap="$4">
        <Text fontWeight="700" fontSize="$6">{t('staff.login.title')}</Text>
        <AppInput label="Restaurant" value={tenant} onChangeText={setTenant} autoCapitalize="none" />
        <AppInput label={t('staff.login.email')} value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" />
        <AppInput label={t('staff.login.password')} value={password} onChangeText={setPassword} secureTextEntry />
        {error && <Text color="$danger">{error}</Text>}
        <AppButton onPress={handleLogin} loading={loading}>{t('staff.login.submit')}</AppButton>
      </YStack>
    </YStack>
  );
}
```

Completed in the frontend implementation branch.

### Task 6.2 — Auth guard layout

`app/(staff)/_layout.tsx`:

```tsx
import { Slot, useRouter, useSegments } from 'expo-router';
import { useEffect } from 'react';
import { Spinner, YStack } from 'tamagui';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';

function Guard() {
  const { accessToken, isLoading } = useAuth();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    if (isLoading) return;
    const onLogin = segments[1] === 'login';
    if (!accessToken && !onLogin) router.replace('/login');
    if (accessToken && onLogin) router.replace('/dashboard');
  }, [accessToken, isLoading, segments]);

  if (isLoading)
    return <YStack flex={1} justifyContent="center" alignItems="center"><Spinner size="large" /></YStack>;

  return <Slot />;
}

export default function StaffLayout() {
  return <AuthProvider><Guard /></AuthProvider>;
}
```

Completed in the frontend implementation branch.

**Verification — Phase 6:**
- Login with valid credentials → redirected to `/dashboard`
- Invalid credentials → error message shown, no redirect
- Direct navigation to `/dashboard` without token → redirected to `/login`
- Session persists across page reloads (sessionStorage on web)

---

## Phase 7 — Staff Bookings Dashboard

Branch: `feature/frontend-staff-dashboard`

No Celery in MVP. Expiration sweep is triggered opportunistically on dashboard load (technical doc §8).

### Task 7.1 — Bookings list

`app/(staff)/dashboard/index.tsx`:

```tsx
import { YStack, ScrollView, Spinner, Text } from 'tamagui';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/endpoints';
import type { BookingStatus } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/AuthContext';
import { BookingCard } from '@/components/staff/BookingCard';
import { FilterTabs } from '@/components/staff/FilterTabs';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

const FILTERS: Array<{ key: string; statuses: BookingStatus[] | null }> = [
  { key: 'all', statuses: null },
  { key: 'pending', statuses: ['pending_review', 'pending_payment', 'authorization_expired'] },
  { key: 'confirmed', statuses: ['confirmed', 'confirmed_without_deposit'] },
  { key: 'declined', statuses: ['declined', 'cancelled_by_customer', 'cancelled_by_staff'] },
];

export default function DashboardScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const [filterIdx, setFilterIdx] = useState(0);

  const sweep = useMutation({
    mutationFn: () => staffApi.triggerExpirationSweep(tenant!, accessToken!),
  });

  useEffect(() => {
    if (accessToken && tenant) sweep.mutate();
  }, []);

  const params: Record<string, string> = {};
  const activeFilter = FILTERS[filterIdx];
  if (activeFilter.statuses) params['status'] = activeFilter.statuses.join(',');

  const { data: bookings, isLoading, error } = useQuery({
    queryKey: ['staff-bookings', tenant, filterIdx],
    queryFn: () => staffApi.listBookings(tenant!, accessToken!, params),
    enabled: !!accessToken && !!tenant,
    refetchInterval: 60_000,
  });

  return (
    <YStack flex={1}>
      <FilterTabs
        labels={FILTERS.map(f => t(`staff.dashboard.filters.${f.key}`))}
        selected={filterIdx}
        onSelect={setFilterIdx}
      />
      <ScrollView>
        <YStack padding="$4" gap="$3">
          {isLoading && <Spinner />}
          {error && <ErrorMessage error={error} />}
          {!isLoading && bookings?.length === 0 && (
            <Text color="$placeholderColor">{t('staff.dashboard.empty')}</Text>
          )}
          {bookings?.map(b => <BookingCard key={b.id} booking={b} />)}
        </YStack>
      </ScrollView>
    </YStack>
  );
}
```

`components/staff/BookingCard.tsx`:

```tsx
import { YStack, XStack, Text } from 'tamagui';
import { Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import type { Booking } from '@/lib/api/types';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ROUTES } from '@/constants/routes';

export function BookingCard({ booking }: { booking: Booking }) {
  const router = useRouter();
  const { t } = useTranslation();
  return (
    <Pressable onPress={() => router.push(ROUTES.bookingAdmin(booking.id))}>
      <YStack borderWidth={1} borderColor="$borderColor" borderRadius="$4" padding="$3" gap="$2"
        hoverStyle={{ backgroundColor: '$backgroundHover' }}>
        <XStack justifyContent="space-between" alignItems="center">
          <Text fontWeight="600">{booking.customer.name}</Text>
          <StatusBadge status={booking.status} />
        </XStack>
        <Text color="$placeholderColor" fontSize="$3">
          {booking.date} {booking.time} · {t('booking.guestCount', { count: booking.party_size })}
        </Text>
        <Text fontSize="$3">{booking.customer.phone}</Text>
      </YStack>
    </Pressable>
  );
}
```

`components/staff/FilterTabs.tsx`:

```tsx
import { XStack, Text } from 'tamagui';
import { Pressable } from 'react-native';

interface Props { labels: string[]; selected: number; onSelect: (i: number) => void; }

export function FilterTabs({ labels, selected, onSelect }: Props) {
  return (
    <XStack borderBottomWidth={1} borderColor="$borderColor" paddingHorizontal="$4">
      {labels.map((label, i) => (
        <Pressable key={label} onPress={() => onSelect(i)}>
          <XStack paddingVertical="$3" paddingHorizontal="$3"
            borderBottomWidth={2}
            borderColor={selected === i ? '$brand' : 'transparent'}>
            <Text color={selected === i ? '$brand' : '$placeholderColor'} fontWeight={selected === i ? '600' : '400'}>
              {label}
            </Text>
          </XStack>
        </Pressable>
      ))}
    </XStack>
  );
}
```

Completed in the frontend implementation branch.

### Task 7.2 — Booking detail + staff actions

`app/(staff)/dashboard/bookings/[id].tsx`:

```tsx
import { ScrollView, YStack, Spinner } from 'tamagui';
import { useLocalSearchParams } from 'expo-router';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/endpoints';
import { useAuth } from '@/lib/auth/AuthContext';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { BookingInfoCard } from '@/components/booking/BookingInfoCard';
import { StaffBookingActions } from '@/components/staff/StaffBookingActions';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

export default function StaffBookingDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { accessToken, tenant } = useAuth();
  const qc = useQueryClient();

  const { data: booking, isLoading, error } = useQuery({
    queryKey: ['staff-booking', id],
    queryFn: () => staffApi.getBooking(tenant!, accessToken!, id),
    enabled: !!id && !!accessToken,
  });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['staff-booking', id] });
    qc.invalidateQueries({ queryKey: ['staff-bookings'] });
  };

  if (isLoading) return <Spinner size="large" />;
  if (error || !booking) return <ErrorMessage error={error} />;

  return (
    <ScrollView>
      <YStack maxWidth={600} alignSelf="center" width="100%" padding="$4" gap="$4">
        <StatusBadge status={booking.status} />
        <BookingInfoCard booking={booking} />
        <StaffBookingActions booking={booking} tenant={tenant!} token={accessToken!} onActionComplete={invalidate} />
      </YStack>
    </ScrollView>
  );
}
```

`components/staff/StaffBookingActions.tsx`:

```tsx
import { YStack } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/endpoints';
import type { Booking } from '@/lib/api/types';
import { AppButton } from '@/components/ui/AppButton';
import { RejectDialog } from '@/components/staff/RejectDialog';
import { AssignTableDialog } from '@/components/staff/AssignTableDialog';

interface Props { booking: Booking; tenant: string; token: string; onActionComplete: () => void; }

export function StaffBookingActions({ booking, tenant, token, onActionComplete }: Props) {
  const { t } = useTranslation();
  const [showReject, setShowReject] = useState(false);
  const [showAssign, setShowAssign] = useState(false);

  const approve = useMutation({
    mutationFn: () => staffApi.approveBooking(tenant, token, booking.id),
    onSuccess: onActionComplete,
  });

  const isPending = booking.status === 'pending_review' || booking.status === 'authorization_expired';
  const isActive = isPending || booking.status === 'confirmed' || booking.status === 'confirmed_without_deposit';

  return (
    <YStack gap="$3">
      {isPending && (
        <>
          <AppButton onPress={() => approve.mutate()} loading={approve.isPending}>
            {t('staff.booking.approve')}
          </AppButton>
          {booking.status === 'authorization_expired' && (
            <AppButton variant="secondary" onPress={() => approve.mutate()}>
              {t('staff.booking.confirmWithoutDeposit')}
            </AppButton>
          )}
          <AppButton variant="danger" onPress={() => setShowReject(true)}>
            {t('staff.booking.reject')}
          </AppButton>
        </>
      )}
      {isActive && (
        <AppButton variant="secondary" onPress={() => setShowAssign(true)}>
          {t('staff.booking.assignTable')}
        </AppButton>
      )}
      {showReject && (
        <RejectDialog bookingId={booking.id} tenant={tenant} token={token}
          onDone={() => { setShowReject(false); onActionComplete(); }}
          onCancel={() => setShowReject(false)} />
      )}
      {showAssign && (
        <AssignTableDialog bookingId={booking.id} tenant={tenant} token={token}
          onDone={() => { setShowAssign(false); onActionComplete(); }}
          onCancel={() => setShowAssign(false)} />
      )}
    </YStack>
  );
}
```

Completed in the frontend implementation branch.

### Task 7.3 — Walk-in form

`app/(staff)/dashboard/walkins.tsx`:

```tsx
import { YStack, Text } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/endpoints';
import { useAuth } from '@/lib/auth/AuthContext';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';
import { AppButton } from '@/components/ui/AppButton';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

export default function WalkinsScreen() {
  const { t } = useTranslation();
  const { accessToken, tenant } = useAuth();
  const [partySize, setPartySize] = useState(2);
  const [success, setSuccess] = useState(false);

  const { mutate, isPending, error, reset } = useMutation({
    mutationFn: () => staffApi.createWalkin(tenant!, accessToken!, { party_size: partySize }),
    onSuccess: () => {
      setSuccess(true);
      setTimeout(() => { setSuccess(false); reset(); }, 3000);
    },
  });

  return (
    <YStack padding="$4" gap="$4">
      <Text fontWeight="700" fontSize="$5">{t('staff.dashboard.walkins')}</Text>
      <PartySizeSelector value={partySize} onChange={setPartySize} />
      {error && <ErrorMessage error={error} />}
      {success && <Text color="$success">Walk-in added</Text>}
      <AppButton onPress={() => mutate()} loading={isPending}>Add walk-in</AppButton>
    </YStack>
  );
}
```

Completed in the frontend implementation branch.

**Verification — Phase 7:**
- Dashboard loads with correct filter tabs and booking list
- Approve booking → status changes to `confirmed`, list refreshes
- Reject booking with reason → status changes to `declined`
- Expiration sweep fires on load (check backend logs for sweep endpoint call)
- Walk-in created → visible in capacity view
