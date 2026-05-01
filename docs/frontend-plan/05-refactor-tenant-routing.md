# Refactor: Frontend API URL Patterns — Path-Based Tenant Routing

## Context

The frontend was originally implemented against the subdomain-based tenant routing spec, producing
URL patterns like `/api/public/${tenant}/...` and `/api/staff/${tenant}/...`. The technical
analysis was then updated to path-based routing (`TenantSubfolderMiddleware`), where every request
must be prefixed with `/restaurants/<slug>/api/v1/`. This document tracks the changes required to
align the frontend with the new spec.

**Branch:** `refactor/frontend-APIs`

---

## Tenant URL Prefix (from `docs/MVP-technical-analysis.md` §3 and §13)

```
${API_BASE_URL}/restaurants/${tenant}/api/v1/${resource}
```

Example: `tablesched.hf.space/restaurants/rome/api/v1/bookings/`

---

## URL Mapping (old → new)

### publicApi

| Method | Old URL | New URL |
|---|---|---|
| `getRestaurantInfo` | `/api/public/${tenant}/restaurant/` | `/restaurants/${tenant}/api/v1/public/restaurant/` |
| `getAvailableSlots` | `/api/public/${tenant}/slots/?date=...` | `/restaurants/${tenant}/api/v1/public/slots/?date=...` |
| `createBooking` | `/api/public/${tenant}/bookings/` | `/restaurants/${tenant}/api/v1/public/bookings/` |
| `getBookingByToken` | `/api/public/bookings/${token}/` | `/restaurants/${tenant}/api/v1/public/bookings/${token}/` |
| `cancelBooking` | `/api/public/bookings/${token}/` | `/restaurants/${tenant}/api/v1/public/bookings/${token}/` |
| `modifyBooking` | `/api/public/bookings/${token}/` | `/restaurants/${tenant}/api/v1/public/bookings/${token}/` |
| `getPaymentIntent` | `/api/public/bookings/${token}/payment-intent/` | `/restaurants/${tenant}/api/v1/public/bookings/${token}/payment-intent/` |

Note: `getBookingByToken`, `cancelBooking`, `modifyBooking`, `getPaymentIntent` currently have no
`tenant` parameter — it must be added.

### staffApi

| Method | Old URL | New URL |
|---|---|---|
| `login` | `/api/staff/${tenant}/login/` | `/restaurants/${tenant}/api/v1/auth/login/` |
| `triggerExpirationSweep` | `/api/staff/${tenant}/bookings/sweep/` | `/restaurants/${tenant}/api/v1/bookings/sweep/` |
| `listBookings` | `/api/staff/${tenant}/bookings/` | `/restaurants/${tenant}/api/v1/bookings/` |
| `getBooking` | `/api/staff/${tenant}/bookings/${id}/` | `/restaurants/${tenant}/api/v1/bookings/${id}/` |
| `postDecision` | `/api/staff/${tenant}/bookings/${id}/decisions/` | `/restaurants/${tenant}/api/v1/bookings/${id}/decisions/` |
| `assignTables` | `/api/staff/${tenant}/bookings/${id}/tables/` | `/restaurants/${tenant}/api/v1/bookings/${id}/tables/` |
| `patchBooking` | `/api/staff/${tenant}/bookings/${id}/` | `/restaurants/${tenant}/api/v1/bookings/${id}/` |
| `refundPayment` | `/api/payments/${paymentId}/refunds/` | `/restaurants/${tenant}/api/v1/payments/${paymentId}/refunds/` |
| `createWalkin` | `/api/staff/${tenant}/walkins/` | `/restaurants/${tenant}/api/v1/walkins/` |
| `listRooms` | `/api/staff/${tenant}/rooms/` | `/restaurants/${tenant}/api/v1/rooms/` |
| `updateTablePosition` | `/api/tables/${tableId}/position/` | `/restaurants/${tenant}/api/v1/tables/${tableId}/position/` |
| `getRestaurantSettings` | `/api/staff/${tenant}/settings/` | `/restaurants/${tenant}/api/v1/settings/` |
| `updateRestaurantSettings` | `/api/staff/${tenant}/settings/` | `/restaurants/${tenant}/api/v1/settings/` |

---

## Tasks

### Task 1 — Update all URL paths in `lib/api/endpoints.ts`

Add a private path helper at the top of the file:

```ts
const tp = (tenant: string, path: string) =>
  `/restaurants/${tenant}/api/v1/${path}`;
```

Update every URL in `publicApi` and `staffApi` using `tp(tenant, ...)`.

Add `tenant: string` as first parameter to the four token-based methods that currently lack it:
`getBookingByToken`, `cancelBooking`, `modifyBooking`, `getPaymentIntent`.

**Commit:** `[TASK] 7 align all API URL patterns with path-based tenant routing`

---

### Task 2 — Update call sites for token-based `publicApi` methods

The four methods above gain a `tenant` parameter. Update every call site to pass the tenant slug.

**Files to update:**
- `app/(public)/[tenant]/booking/[token]/index.tsx` — `getBookingByToken`, `cancelBooking`, `modifyBooking`
- `app/(public)/[tenant]/booking/[token]/pay.tsx` — `getPaymentIntent`
- `components/booking/CustomerBookingActions.tsx` — add `tenant` prop; pass to cancel/modify callbacks
- `components/booking/ModifyBookingForm.tsx` — add `tenant` prop; pass to `modifyBooking`

**Commit:** `[TASK] 8 pass tenant to token-based publicApi call sites`
