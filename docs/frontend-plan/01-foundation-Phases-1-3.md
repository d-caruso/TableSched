# Phases 1–3 — Foundation

Covers project bootstrap, shared infrastructure (i18n, API client, auth context, UI kit), and the customer-facing public booking page.

---

## Phase 1 — Repository & Project Bootstrap

Branch: `feature/frontend-bootstrap`

### Task 1.1 — Expo + React Native Web scaffold

Directory layout:

```
frontend/
  app/                     # Expo Router file-based routing
    _layout.tsx            # Root layout: providers
    (public)/
      _layout.tsx
      [tenant]/
        index.tsx          # Public booking page
        booking/
          [token]/
            index.tsx      # Customer booking detail
            pay.tsx        # Stripe payment
    (staff)/
      _layout.tsx          # Auth guard
      login.tsx
      dashboard/
        _layout.tsx        # Tab navigator
        index.tsx          # Bookings list
        bookings/
          [id].tsx         # Booking detail + actions
        walkins.tsx
        settings/
          index.tsx        # Restaurant settings
          floor.tsx        # Floor plan editor
    +not-found.tsx
  components/
    booking/               # Customer booking components
    payment/               # Stripe components
    staff/                 # Staff dashboard components
    floor/                 # Floor plan editor
    settings/              # Settings editors
    ui/                    # Shared Tamagui primitives
  lib/
    api/                   # API client + typed endpoints
    auth/                  # Auth context + secure storage
    i18n/                  # i18next setup + locale files
    env.ts                 # Typed env vars
  constants/
    routes.ts
  assets/
  app.json
  package.json
  tsconfig.json
  tamagui.config.ts
  babel.config.js
  .env.example
```

Init command:

```bash
npx create-expo-app@latest frontend --template tabs
```

### Task 1.2 — Dependencies

`package.json` key entries:

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
    "@typescript-eslint/parser": "^8.x"
  }
}
```

Also add the initial frontend linting setup:
- `package.json` scripts for `typecheck` and `lint`
- an initial ESLint config file for the frontend app

### Task 1.3 — Configuration files

`app.json`:

```json
{
  "expo": {
    "name": "TableSched",
    "slug": "tablesched",
    "scheme": "tablesched",
    "web": { "bundler": "metro", "output": "static" },
    "platforms": ["ios", "android", "web"],
    "plugins": [
      ["expo-router", {
        "root": "app",
        "origin": "https://tablesched.domenicocaruso.com"
      }]
    ]
  }
}
```

`babel.config.js`:

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      ['@tamagui/babel-plugin', {
        components: ['tamagui'],
        config: './tamagui.config.ts',
        logTimings: true,
      }],
      'react-native-reanimated/plugin',
    ],
  };
};
```

`tsconfig.json`:

```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "paths": { "@/*": ["./*"] }
  }
}
```

`.env.example`:

```
EXPO_PUBLIC_API_BASE_URL=https://api.tablesched.domenicocaruso.com
EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
EXPO_PUBLIC_APP_ENV=development
```

`lib/env.ts`:

```ts
import Constants from 'expo-constants';

const extra = Constants.expoConfig?.extra ?? {};

export const ENV = {
  API_BASE_URL: process.env.EXPO_PUBLIC_API_BASE_URL ?? extra.apiBaseUrl ?? '',
  STRIPE_KEY: process.env.EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY ?? '',
  APP_ENV: process.env.EXPO_PUBLIC_APP_ENV ?? 'development',
} as const;
```

`constants/routes.ts`:

```ts
export const ROUTES = {
  publicBooking: (tenant: string) => `/${tenant}` as const,
  bookingDetail: (token: string) => `/booking/${token}` as const,
  bookingPay: (token: string) => `/booking/${token}/pay` as const,
  staffLogin: '/login',
  dashboard: '/dashboard',
  bookingAdmin: (id: string) => `/dashboard/bookings/${id}` as const,
  walkins: '/dashboard/walkins',
  settings: '/dashboard/settings',
  floor: '/dashboard/settings/floor',
} as const;
```

### Task 1.4 — Tamagui config & root layout

`tamagui.config.ts`:

```ts
import { createTamagui } from 'tamagui';
import { config } from '@tamagui/config/v3';

export const tamaguiConfig = createTamagui({
  ...config,
  tokens: {
    ...config.tokens,
    color: {
      ...config.tokens.color,
      brand: '#1a56db',
      brandDark: '#1e429f',
      danger: '#e02424',
      warning: '#c27803',
      success: '#057a55',
    },
  },
});

export type AppConfig = typeof tamaguiConfig;
declare module 'tamagui' {
  interface TamaguiCustomConfig extends AppConfig {}
}
```

`app/_layout.tsx`:

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

**Verification — Phase 1:**
```bash
cd frontend && npm run web   # App loads at localhost:8081
npm run typecheck            # No errors
npm run lint                 # No errors
```

---

## Phase 2 — Shared Infrastructure

Branch: `feature/frontend-bootstrap` (same branch, continued)

### Task 2.1 — i18n setup

`lib/i18n/index.ts`:

```ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import it from './locales/it.json';
import de from './locales/de.json';

export const SUPPORTED_LOCALES = ['en', 'it', 'de'] as const;
export type Locale = typeof SUPPORTED_LOCALES[number];

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    it: { translation: it },
    de: { translation: de },
  },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export default i18n;
```

`lib/i18n/I18nProvider.tsx`:

```tsx
import { I18nextProvider } from 'react-i18next';
import i18n from './index';
import type { ReactNode } from 'react';

export function I18nProvider({ children }: { children: ReactNode }) {
  return <I18nextProvider i18n={i18n}>{children}</I18nextProvider>;
}
```

`lib/i18n/locales/en.json` (excerpt — all MVP keys):

```json
{
  "common": { "loading": "Loading…", "error": "Something went wrong", "retry": "Try again", "cancel": "Cancel", "confirm": "Confirm", "save": "Save", "back": "Back" },
  "booking": {
    "form": { "title": "Book a table", "date": "Date", "time": "Time", "partySize": "Party size", "name": "Full name", "phone": "Phone number", "email": "Email (optional)", "notes": "Notes (optional)", "locale": "Language", "submit": "Request booking" },
    "status": {
      "pending_review": "Pending review", "pending_payment": "Pending payment",
      "confirmed": "Confirmed", "confirmed_without_deposit": "Confirmed",
      "declined": "Declined", "cancelled_by_customer": "Cancelled",
      "cancelled_by_staff": "Cancelled", "no_show": "No show",
      "expired": "Expired", "authorization_expired": "Payment expired"
    },
    "payment_status": { "pending": "Payment pending", "authorized": "Authorized", "captured": "Captured", "failed": "Failed", "refund_pending": "Refund pending", "refunded": "Refunded", "refund_failed": "Refund failed" },
    "actions": { "cancel": "Cancel booking", "modify": "Modify booking", "pay": "Pay deposit" },
    "guestCount_one": "{{count}} guest",
    "guestCount_other": "{{count}} guests",
    "success": { "requested": "Booking request received", "requestedBody": "We'll notify you by SMS{{email}}.", "cancelled": "Your booking has been cancelled." }
  },
  "staff": {
    "login": { "title": "Staff login", "email": "Email", "password": "Password", "submit": "Sign in", "error": "Invalid email or password" },
    "dashboard": { "title": "Bookings", "filters": { "all": "All", "pending": "Pending", "confirmed": "Confirmed", "declined": "Declined" }, "empty": "No bookings found" },
    "booking": { "approve": "Approve", "reject": "Reject", "modify": "Modify", "assignTable": "Assign table", "refund": "Refund deposit", "noShow": "No show", "confirmWithoutDeposit": "Confirm without deposit" },
    "settings": { "title": "Settings", "openingHours": "Opening hours", "depositPolicy": "Deposit policy", "never": "Never", "always": "Always", "byPartySize": "For parties of {{n}} or more" },
    "floor": { "title": "Floor plan", "addRoom": "Add room", "addTable": "Add table", "saveLayout": "Save layout" }
  },
  "error": {
    "BOOKING_NOT_FOUND": "Booking not found", "TOKEN_EXPIRED": "This link has expired",
    "CUTOFF_PASSED": "Modifications are no longer allowed",
    "SLOT_UNAVAILABLE": "This time slot is no longer available",
    "VALIDATION_ERROR": "Please check your input",
    "PAYMENT_REQUIRED": "A deposit is required to complete this booking"
  }
}
```

### Task 2.2 — API client

`lib/api/client.ts`:

```ts
import { ENV } from '@/lib/env';

type RequestOptions = {
  method?: string;
  body?: unknown;
  token?: string;
  tenant?: string;
};

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    public readonly detail?: string,
  ) { super(code); }
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, token, tenant } = options;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (tenant) headers['X-Tenant-Slug'] = tenant;

  const res = await fetch(`${ENV.API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const payload = await res.json().catch(() => ({}));
    throw new ApiError(res.status, payload.code ?? 'UNKNOWN_ERROR', payload.detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
```

`lib/api/types.ts` (shared model types matching backend):

```ts
export type BookingStatus =
  | 'pending_review' | 'pending_payment' | 'confirmed'
  | 'confirmed_without_deposit' | 'declined' | 'cancelled_by_customer'
  | 'cancelled_by_staff' | 'no_show' | 'expired' | 'authorization_expired';

export type PaymentStatus =
  | 'pending' | 'authorized' | 'captured' | 'failed'
  | 'refund_pending' | 'refunded' | 'refund_failed';

export interface Booking {
  id: string;
  status: BookingStatus;
  date: string;
  time: string;
  party_size: number;
  notes?: string;
  customer: { name: string; phone: string; email?: string; locale: string };
  table?: { id: string; name: string };
  payment?: { status: PaymentStatus; amount: number; currency: string };
  created_at: string;
}

export interface TimeSlot { time: string; available: boolean; busy_warning: boolean; }

export interface OpeningHours { day: 0|1|2|3|4|5|6; open: string; close: string; }

export interface DepositPolicy {
  mode: 'never' | 'always' | 'by_party_size';
  min_party_size?: number;
}

export interface RestaurantPublicInfo {
  slug: string;
  name: string;
  opening_hours: OpeningHours[];
  deposit_policy: DepositPolicy;
  cancellation_cutoff_hours: number;
}

export interface Room { id: string; name: string; tables: Table[]; }
export interface Table { id: string; name: string; capacity: number; x: number; y: number; }

export interface BookingCreatePayload {
  date: string; time: string; party_size: number;
  name: string; phone: string; email?: string; locale: string; notes?: string;
}
```

`lib/api/endpoints.ts`:

```ts
import { apiRequest } from './client';
import type { Booking, BookingCreatePayload, RestaurantPublicInfo, Room, TimeSlot } from './types';

export const publicApi = {
  getRestaurant: (tenant: string) =>
    apiRequest<RestaurantPublicInfo>('/api/restaurant/', { tenant }),
  getAvailableSlots: (tenant: string, date: string, partySize: number) =>
    apiRequest<TimeSlot[]>(`/api/availability/?date=${date}&party_size=${partySize}`, { tenant }),
  createBooking: (tenant: string, payload: BookingCreatePayload) =>
    apiRequest<{ id: string; token: string }>('/api/bookings/', { method: 'POST', body: payload, tenant }),
  getBookingByToken: (token: string) =>
    apiRequest<Booking>(`/api/customer/bookings/${token}/`),
  cancelBooking: (token: string) =>
    apiRequest<void>(`/api/customer/bookings/${token}/cancel/`, { method: 'POST' }),
  modifyBooking: (token: string, payload: Partial<BookingCreatePayload>) =>
    apiRequest<Booking>(`/api/customer/bookings/${token}/modify/`, { method: 'PATCH', body: payload }),
  getPaymentIntent: (token: string) =>
    apiRequest<{ client_secret: string }>(`/api/customer/bookings/${token}/payment-intent/`),
};

export const staffApi = {
  login: (email: string, password: string) =>
    apiRequest<{ access: string; refresh: string }>('/api/auth/login/', { method: 'POST', body: { email, password } }),
  listBookings: (tenant: string, token: string, params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return apiRequest<Booking[]>(`/api/bookings/${qs}`, { tenant, token });
  },
  getBooking: (tenant: string, token: string, id: string) =>
    apiRequest<Booking>(`/api/bookings/${id}/`, { tenant, token }),
  approveBooking: (tenant: string, token: string, id: string) =>
    apiRequest<Booking>(`/api/bookings/${id}/approve/`, { method: 'POST', tenant, token }),
  rejectBooking: (tenant: string, token: string, id: string, reason: string) =>
    apiRequest<Booking>(`/api/bookings/${id}/reject/`, { method: 'POST', body: { reason }, tenant, token }),
  assignTable: (tenant: string, token: string, id: string, tableId: string) =>
    apiRequest<Booking>(`/api/bookings/${id}/assign-table/`, { method: 'POST', body: { table_id: tableId }, tenant, token }),
  triggerExpirationSweep: (tenant: string, token: string) =>
    apiRequest<void>('/api/bookings/sweep-expirations/', { method: 'POST', tenant, token }),
  createWalkin: (tenant: string, token: string, payload: { party_size: number; table_id?: string }) =>
    apiRequest<{ id: string }>('/api/walkins/', { method: 'POST', body: payload, tenant, token }),
  getRestaurantSettings: (tenant: string, token: string) =>
    apiRequest<RestaurantPublicInfo>('/api/restaurant/', { tenant, token }),
  updateRestaurantSettings: (tenant: string, token: string, payload: Partial<RestaurantPublicInfo>) =>
    apiRequest<RestaurantPublicInfo>('/api/restaurant/', { method: 'PATCH', body: payload, tenant, token }),
  listRooms: (tenant: string, token: string) =>
    apiRequest<Room[]>('/api/rooms/', { tenant, token }),
  updateTablePosition: (tenant: string, token: string, tableId: string, x: number, y: number) =>
    apiRequest<void>(`/api/tables/${tableId}/position/`, { method: 'PATCH', body: { x, y }, tenant, token }),
};
```

### Task 2.3 — Auth context (staff JWT)

`lib/auth/AuthContext.tsx`:

```tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import { staffApi } from '@/lib/api/endpoints';

interface AuthState { accessToken: string | null; tenant: string | null; isLoading: boolean; }
interface AuthContextValue extends AuthState {
  login: (email: string, password: string, tenant: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const KEY_ACCESS = 'ts_access', KEY_REFRESH = 'ts_refresh', KEY_TENANT = 'ts_tenant';

const get = (k: string): Promise<string | null> =>
  Platform.OS === 'web' ? Promise.resolve(sessionStorage.getItem(k)) : SecureStore.getItemAsync(k);
const set = (k: string, v: string) => Platform.OS === 'web' ? (sessionStorage.setItem(k, v), Promise.resolve()) : SecureStore.setItemAsync(k, v);
const del = (k: string) => Platform.OS === 'web' ? (sessionStorage.removeItem(k), Promise.resolve()) : SecureStore.deleteItemAsync(k);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ accessToken: null, tenant: null, isLoading: true });

  useEffect(() => {
    Promise.all([get(KEY_ACCESS), get(KEY_TENANT)]).then(([access, tenant]) => {
      setState({ accessToken: access, tenant, isLoading: false });
    });
  }, []);

  const login = async (email: string, password: string, tenant: string) => {
    const { access, refresh } = await staffApi.login(email, password);
    await Promise.all([set(KEY_ACCESS, access), set(KEY_REFRESH, refresh), set(KEY_TENANT, tenant)]);
    setState({ accessToken: access, tenant, isLoading: false });
  };

  const logout = async () => {
    await Promise.all([del(KEY_ACCESS), del(KEY_REFRESH), del(KEY_TENANT)]);
    setState({ accessToken: null, tenant: null, isLoading: false });
  };

  return <AuthContext.Provider value={{ ...state, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
```

### Task 2.4 — Shared UI primitives

`components/ui/AppButton.tsx`:

```tsx
import { Button, type ButtonProps } from 'tamagui';

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';

const STYLES: Record<Variant, Partial<ButtonProps>> = {
  primary: { backgroundColor: '$brand', color: 'white', hoverStyle: { backgroundColor: '$brandDark' } },
  secondary: { backgroundColor: 'transparent', borderWidth: 1, borderColor: '$borderColor' },
  danger: { backgroundColor: '$danger', color: 'white' },
  ghost: { backgroundColor: 'transparent' },
};

interface Props extends Omit<ButtonProps, 'variant'> { variant?: Variant; loading?: boolean; }

export function AppButton({ variant = 'primary', loading, children, ...props }: Props) {
  return (
    <Button {...STYLES[variant]} opacity={props.disabled || loading ? 0.6 : 1} pressStyle={{ opacity: 0.8 }} {...props}>
      {loading ? '…' : children}
    </Button>
  );
}
```

`components/ui/StatusBadge.tsx`:

```tsx
import { Text, XStack } from 'tamagui';
import { useTranslation } from 'react-i18next';
import type { BookingStatus } from '@/lib/api/types';

const COLORS: Record<BookingStatus, string> = {
  pending_review: '#c27803', pending_payment: '#c27803',
  confirmed: '#057a55', confirmed_without_deposit: '#057a55',
  declined: '#e02424', authorization_expired: '#e02424',
  cancelled_by_customer: '#6b7280', cancelled_by_staff: '#6b7280',
  no_show: '#6b7280', expired: '#6b7280',
};

export function StatusBadge({ status }: { status: BookingStatus }) {
  const { t } = useTranslation();
  return (
    <XStack backgroundColor={COLORS[status] + '20'} paddingHorizontal="$2" paddingVertical="$1" borderRadius="$2">
      <Text color={COLORS[status]} fontSize="$2" fontWeight="600">{t(`booking.status.${status}`)}</Text>
    </XStack>
  );
}
```

`components/ui/ErrorMessage.tsx`:

```tsx
import { YStack, Text } from 'tamagui';
import { useTranslation } from 'react-i18next';
import { ApiError } from '@/lib/api/client';

export function ErrorMessage({ error }: { error: unknown }) {
  const { t } = useTranslation();
  const code = error instanceof ApiError ? error.code : 'UNKNOWN_ERROR';
  return (
    <YStack padding="$3" backgroundColor="$danger" borderRadius="$3" opacity={0.9}>
      <Text color="white">{t(`error.${code}`, { defaultValue: t('common.error') })}</Text>
    </YStack>
  );
}
```

**Verification — Phase 2:**
```bash
npm run typecheck    # All types resolve, no errors
npm run web          # TamaguiProvider + i18n initializes without console errors
```

---

## Phase 3 — Public Booking Page

Branch: `feature/frontend-public-booking`

### Task 3.1 — Restaurant info display

`app/(public)/[tenant]/index.tsx`:

```tsx
import { ScrollView, YStack, Spinner } from 'tamagui';
import { useLocalSearchParams } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { publicApi } from '@/lib/api/endpoints';
import { RestaurantHeader } from '@/components/booking/RestaurantHeader';
import { OpeningHoursList } from '@/components/booking/OpeningHoursList';
import { BookingFormFlow } from '@/components/booking/BookingFormFlow';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

export default function PublicBookingPage() {
  const { tenant } = useLocalSearchParams<{ tenant: string }>();
  const { data: restaurant, isLoading, error } = useQuery({
    queryKey: ['restaurant', tenant],
    queryFn: () => publicApi.getRestaurant(tenant),
    enabled: !!tenant,
  });

  if (isLoading) return <Spinner size="large" />;
  if (error || !restaurant) return <ErrorMessage error={error} />;

  return (
    <ScrollView>
      <YStack maxWidth={600} alignSelf="center" width="100%" padding="$4" gap="$4">
        <RestaurantHeader name={restaurant.name} />
        <OpeningHoursList hours={restaurant.opening_hours} />
        <BookingFormFlow tenant={tenant} restaurant={restaurant} />
      </YStack>
    </ScrollView>
  );
}
```

### Task 3.2 — Multi-step booking form (orchestrator)

`components/booking/BookingFormFlow.tsx`:

```tsx
import { useState } from 'react';
import type { RestaurantPublicInfo, BookingCreatePayload } from '@/lib/api/types';
import { StepDateTime } from './steps/StepDateTime';
import { StepContact } from './steps/StepContact';
import { StepDone } from './steps/StepDone';

type Step = 'datetime' | 'contact' | 'done';

interface Props { tenant: string; restaurant: RestaurantPublicInfo; }

export function BookingFormFlow({ tenant, restaurant }: Props) {
  const [step, setStep] = useState<Step>('datetime');
  const [draft, setDraft] = useState<Partial<BookingCreatePayload>>({});

  const patch = (fields: Partial<BookingCreatePayload>) => setDraft(d => ({ ...d, ...fields }));

  if (step === 'datetime')
    return <StepDateTime tenant={tenant} restaurant={restaurant} draft={draft}
      onNext={f => { patch(f); setStep('contact'); }} />;

  if (step === 'contact')
    return <StepContact draft={draft} tenant={tenant}
      onBack={() => setStep('datetime')}
      onNext={f => { patch(f); setStep('done'); }} />;

  return <StepDone draft={draft as BookingCreatePayload} tenant={tenant} />;
}
```

### Task 3.3 — StepDateTime (date, time slot, party size)

`components/booking/steps/StepDateTime.tsx`:

```tsx
import { YStack, Text } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { publicApi, type RestaurantPublicInfo, type BookingCreatePayload } from '@/lib/api/endpoints';
import { AppButton } from '@/components/ui/AppButton';
import { DatePicker } from '@/components/booking/DatePicker';
import { TimeSlotGrid } from '@/components/booking/TimeSlotGrid';
import { PartySizeSelector } from '@/components/booking/PartySizeSelector';

interface Props {
  tenant: string;
  restaurant: RestaurantPublicInfo;
  draft: Partial<BookingCreatePayload>;
  onNext: (f: Pick<BookingCreatePayload, 'date' | 'time' | 'party_size'>) => void;
}

export function StepDateTime({ tenant, draft, onNext }: Props) {
  const { t } = useTranslation();
  const [date, setDate] = useState(draft.date ?? '');
  const [partySize, setPartySize] = useState(draft.party_size ?? 2);
  const [time, setTime] = useState(draft.time ?? '');

  const { data: slots, isLoading } = useQuery({
    queryKey: ['slots', tenant, date, partySize],
    queryFn: () => publicApi.getAvailableSlots(tenant, date, partySize),
    enabled: !!date,
  });

  return (
    <YStack gap="$4">
      <Text fontWeight="700" fontSize="$5">{t('booking.form.title')}</Text>
      <PartySizeSelector value={partySize} onChange={setPartySize} />
      <DatePicker label={t('booking.form.date')} value={date} onChange={setDate} minDate={new Date()} maxDays={90} />
      {date && <TimeSlotGrid slots={slots ?? []} loading={isLoading} selected={time} onSelect={setTime} />}
      <AppButton disabled={!date || !time} onPress={() => onNext({ date, time, party_size: partySize })}>
        {t('common.confirm')}
      </AppButton>
    </YStack>
  );
}
```

### Task 3.4 — StepContact (name, phone, email, locale, notes)

`components/booking/steps/StepContact.tsx`:

```tsx
import { YStack } from 'tamagui';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { BookingCreatePayload } from '@/lib/api/types';
import { AppButton } from '@/components/ui/AppButton';
import { AppInput } from '@/components/ui/AppInput';
import { LocaleSelector } from '@/components/booking/LocaleSelector';
import { useLocale } from '@/lib/i18n/useLocale';

type ContactFields = Pick<BookingCreatePayload, 'name' | 'phone' | 'email' | 'locale' | 'notes'>;

interface Props {
  draft: Partial<BookingCreatePayload>;
  tenant: string;
  onBack: () => void;
  onNext: (f: ContactFields) => void;
}

export function StepContact({ draft, onBack, onNext }: Props) {
  const { t } = useTranslation();
  const { locale } = useLocale();
  const [name, setName] = useState(draft.name ?? '');
  const [phone, setPhone] = useState(draft.phone ?? '');
  const [email, setEmail] = useState(draft.email ?? '');
  const [notes, setNotes] = useState(draft.notes ?? '');
  const [selectedLocale, setSelectedLocale] = useState(draft.locale ?? locale);

  const canSubmit = name.trim().length > 0 && phone.trim().length > 0;

  return (
    <YStack gap="$3">
      <AppInput label={t('booking.form.name')} value={name} onChangeText={setName} autoComplete="name" />
      <AppInput label={t('booking.form.phone')} value={phone} onChangeText={setPhone} keyboardType="phone-pad" autoComplete="tel" />
      <AppInput label={t('booking.form.email')} value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="email" />
      <LocaleSelector value={selectedLocale} onChange={setSelectedLocale} />
      <AppInput label={t('booking.form.notes')} value={notes} onChangeText={setNotes} multiline numberOfLines={3} />
      <AppButton variant="secondary" onPress={onBack}>{t('common.back')}</AppButton>
      <AppButton disabled={!canSubmit}
        onPress={() => canSubmit && onNext({ name, phone, email: email || undefined, locale: selectedLocale, notes: notes || undefined })}>
        {t('booking.form.submit')}
      </AppButton>
    </YStack>
  );
}
```

### Task 3.5 — StepDone (submit + success screen)

`components/booking/steps/StepDone.tsx`:

```tsx
import { YStack, Text, Spinner } from 'tamagui';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
import { publicApi } from '@/lib/api/endpoints';
import type { BookingCreatePayload } from '@/lib/api/types';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

export function StepDone({ draft, tenant }: { draft: BookingCreatePayload; tenant: string }) {
  const { t } = useTranslation();
  const { mutate, isPending, isSuccess, error } = useMutation({
    mutationFn: () => publicApi.createBooking(tenant, draft),
  });

  useEffect(() => { mutate(); }, []);

  if (isPending) return <Spinner size="large" />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <YStack gap="$3" alignItems="center" paddingVertical="$8">
      <Text fontSize="$8">✓</Text>
      <Text fontWeight="700" fontSize="$5">{t('booking.success.requested')}</Text>
      <Text color="$placeholderColor" textAlign="center">
        {t('booking.success.requestedBody', { email: draft.email ? ' and email' : '' })}
      </Text>
    </YStack>
  );
}
```

### Task 3.6 — Slot and party size pickers

`components/booking/TimeSlotGrid.tsx`:

```tsx
import { XStack, Text } from 'tamagui';
import { Pressable } from 'react-native';
import { useTranslation } from 'react-i18next';
import type { TimeSlot } from '@/lib/api/types';

interface Props { slots: TimeSlot[]; loading: boolean; selected: string; onSelect: (t: string) => void; }

export function TimeSlotGrid({ slots, loading, selected, onSelect }: Props) {
  const { t } = useTranslation();
  if (loading) return <Text>{t('common.loading')}</Text>;
  return (
    <XStack flexWrap="wrap" gap="$2">
      {slots.map(slot => (
        <Pressable key={slot.time} onPress={() => onSelect(slot.time)} disabled={!slot.available} style={{ opacity: slot.available ? 1 : 0.4 }}>
          <XStack paddingHorizontal="$3" paddingVertical="$2" borderRadius="$3" borderWidth={1}
            borderColor={selected === slot.time ? '$brand' : '$borderColor'}
            backgroundColor={selected === slot.time ? '$brand' : 'transparent'}>
            <Text color={selected === slot.time ? 'white' : '$color'}>{slot.time}</Text>
            {slot.busy_warning && <Text fontSize="$1" color="$warning" marginLeft="$1">!</Text>}
          </XStack>
        </Pressable>
      ))}
    </XStack>
  );
}
```

`components/booking/PartySizeSelector.tsx`:

```tsx
import { XStack, Text } from 'tamagui';
import { useTranslation } from 'react-i18next';
import { AppButton } from '@/components/ui/AppButton';

interface Props { value: number; onChange: (n: number) => void; }

export function PartySizeSelector({ value, onChange }: Props) {
  const { t } = useTranslation();
  return (
    <XStack alignItems="center" gap="$3">
      <Text>{t('booking.form.partySize')}</Text>
      <AppButton variant="secondary" size="$2" onPress={() => onChange(Math.max(1, value - 1))}>−</AppButton>
      <Text fontWeight="700" fontSize="$5" minWidth={30} textAlign="center">{value}</Text>
      <AppButton variant="secondary" size="$2" onPress={() => onChange(Math.min(20, value + 1))}>+</AppButton>
    </XStack>
  );
}
```

**Verification — Phase 3:**
- Navigate to `/{tenant}` — restaurant name and opening hours displayed
- Complete multi-step form end-to-end — booking created in backend
- Verify SMS/email notification fired after submission
- Verify `busy_warning` slots show indicator without blocking selection
