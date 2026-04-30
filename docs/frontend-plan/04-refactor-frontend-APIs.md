# Refactor: Frontend API Client — RESTful Endpoint Alignment

## Context

The backend REST API was refactored to replace verb-based action endpoints with resource-oriented
ones. This document plans the corresponding frontend changes only — what must be removed, renamed,
or replaced. It does not duplicate the existing implementation plan.

**Branch:** `refactor/frontend-APIs`

---

## Endpoint Mapping

### Staff API

| Deleted | Replacement |
|---|---|
| `POST /bookings/{id}/approve/` | `POST /bookings/{id}/decisions/` `{outcome:"approved"}` |
| `POST /bookings/{id}/decline/` | `POST /bookings/{id}/decisions/` `{outcome:"declined", reason_code?, staff_message?}` |
| `POST /bookings/{id}/confirm-without-deposit/` | `POST /bookings/{id}/decisions/` `{outcome:"confirmed_without_deposit"}` |
| `POST /bookings/{id}/modify/` | `PATCH /bookings/{id}/` `{starts_at?, party_size?, notes?}` |
| `POST /bookings/{id}/assign-table/` | `PUT /bookings/{id}/tables/` `{tables:[id]}` |
| `POST /bookings/{id}/mark-no-show/` | `PATCH /bookings/{id}/` `{status:"no_show"}` |
| `POST /bookings/{id}/request-payment/` | **removed** — no backend endpoint; drop from frontend |
| `POST /payments/{id}/refund/` | `POST /payments/{id}/refunds/` (trailing `s`) |

### Public API

| Deleted | Replacement |
|---|---|
| `POST /public/bookings/{token}/cancel/` | `DELETE /public/bookings/{token}/` |

---

## Tasks

### Task 1 — Replace `staffApi` method definitions in `lib/api/endpoints.ts`

Remove: `approveBooking`, `rejectBooking`, `assignTable`, `markNoShow`, `modifyBooking`, `requestPayment`.

Add:

```ts
postDecision: (
  tenant: string, token: string, id: string,
  payload: { outcome: 'approved' | 'declined' | 'confirmed_without_deposit'; reason_code?: string; staff_message?: string }
) => apiRequest<Booking>(`/api/bookings/${id}/decisions/`, { method: 'POST', body: payload, tenant, token }),

assignTables: (tenant: string, token: string, id: string, tableIds: string[]) =>
  apiRequest<{ tables: string[] }>(`/api/bookings/${id}/tables/`, { method: 'PUT', body: { tables: tableIds }, tenant, token }),

patchBooking: (
  tenant: string, token: string, id: string,
  payload: { starts_at?: string; party_size?: number; notes?: string; status?: 'no_show' }
) => apiRequest<Booking>(`/api/bookings/${id}/`, { method: 'PATCH', body: payload, tenant, token }),

refundPayment: (tenant: string, token: string, paymentId: string) =>
  apiRequest<Payment>(`/api/payments/${paymentId}/refunds/`, { method: 'POST', tenant, token }),
```

**Commit:** `[TASK] 1 replace staffApi verb-endpoint methods with RESTful equivalents`

---

### Task 2 — Update `StaffBookingActions` mutations

Replace the single `approve` mutation (which incorrectly covered confirm-without-deposit too) with three:

```ts
const approve = useMutation({
  mutationFn: () => staffApi.postDecision(tenant, token, booking.id, { outcome: 'approved' }),
  onSuccess: onActionComplete,
});

const confirmWithoutDeposit = useMutation({
  mutationFn: () =>
    staffApi.postDecision(tenant, token, booking.id, { outcome: 'confirmed_without_deposit' }),
  onSuccess: onActionComplete,
});

const decline = useMutation({
  mutationFn: (reason_code: string) =>
    staffApi.postDecision(tenant, token, booking.id, { outcome: 'declined', reason_code }),
  onSuccess: onActionComplete,
});
```

- "Confirm without deposit" button → `confirmWithoutDeposit.mutate()`
- "Reject" button → `decline.mutate(reasonCode)`

**Commit:** `[TASK] 2 split StaffBookingActions into three postDecision mutations`

---

### Task 3 — Update table assignment call site

```ts
// before
staffApi.assignTable(tenant, token, booking.id, tableId)
// after
staffApi.assignTables(tenant, token, booking.id, [tableId])
```

**Commit:** `[TASK] 3 update table assignment call site to assignTables`

---

### Task 4 — Update no-show and modify booking call sites

```ts
// no-show
staffApi.markNoShow(tenant, token, booking.id)
→ staffApi.patchBooking(tenant, token, booking.id, { status: 'no_show' })

// modify
staffApi.modifyBooking(tenant, token, booking.id, { starts_at, party_size, notes })
→ staffApi.patchBooking(tenant, token, booking.id, { starts_at, party_size, notes })
```

**Commit:** `[TASK] 4 update no-show and modify call sites to patchBooking`

---

### Task 5 — Update refund call site and remove requestPayment

- Update refund call site to use `staffApi.refundPayment(tenant, token, payment.id)` (URL now `/refunds/`).
- Remove `requestPayment` mutation and any associated UI button. No backend endpoint exists for this action.

**Commit:** `[TASK] 5 update refund call site and remove requestPayment`

---

### Task 6 — Fix `publicApi.cancelBooking` to use DELETE

`publicApi.cancelBooking` still uses the deleted `POST /api/public/bookings/{token}/cancel/`. Replace with `DELETE /api/public/bookings/{token}/`.

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

**File:** `lib/api/endpoints.ts`

**Commit:** `[TASK] 6 fix publicApi.cancelBooking to use DELETE instead of POST cancel`
