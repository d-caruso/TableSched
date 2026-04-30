# Phases 17-20 — Adjustments

Refines the completed backend MVP plan where implementation exposed better domain/API shapes. These phases correct REST resource naming, support manual multi-table assignment, expose restaurant configuration as proper tenant resources, and remove legacy action endpoints after compatibility is handled.

These phases do not add automatic table assignment, table-combination logic, advanced capacity logic, partial refunds, customer accounts, or background workers.

---

## Phase 17 — Multi-Table Assignments

Bookings and walk-ins can be assigned one or more tables manually by staff. The existing singular `table` foreign keys are replaced with explicit assignment records so assignment metadata and future audit behavior remain clear.

### Task 17.1 — Booking table assignments

Add a tenant-schema `BookingTableAssignment` model linked to `Booking`, `Table`, and the staff membership that made the assignment. `assigned_by` must be nullable so migrated historical assignments can be represented honestly.

Required behavior:
- A booking may have zero, one, or many assigned tables.
- The same table cannot be assigned twice to the same booking.
- Existing `Booking.table` values must be migrated into assignment rows before removing the old field.
- No automatic table selection or table-combination rules are introduced.

Tests:
- Existing singular table assignments migrate into assignment rows.
- Multiple tables can be assigned to one booking.
- Duplicate booking/table assignment is rejected.
- Removing the old field does not break booking creation without tables.

### Task 17.2 — Walk-in table assignments

Add a tenant-schema `WalkinTableAssignment` model matching the booking assignment pattern. `assigned_by` must be nullable so migrated historical assignments can be represented honestly.

Required behavior:
- A walk-in may have zero, one, or many assigned tables.
- The same table cannot be assigned twice to the same walk-in.
- Existing `Walkin.table` values must be migrated into assignment rows before removing the old field.
- Walk-ins still have no customer, no status workflow, and no notifications.

Tests:
- Existing walk-in table values migrate into assignment rows.
- Multiple tables can be assigned to one walk-in.
- Duplicate walk-in/table assignment is rejected.

### Task 17.3 — Assignment services and serializers

Add service functions for replacing and removing assigned table sets. API serializers should expose assigned tables as `tables: [id, ...]` instead of a singular `table` field.

Required behavior:
- Assignment writes go through services, not direct serializer field assignment.
- Replacing assignments is idempotent for the same submitted table ids.
- Booking and walk-in responses expose assigned table ids consistently.
- Assignment request bodies use `{"tables": ["<table_id>", ...]}`.

Tests:
- Replacing assigned tables updates the assignment set exactly.
- Removing one assignment leaves the other assignments intact.
- Serializer output uses `tables` and no longer exposes `table`.

---

## Phase 18 — REST API Normalization

Replace RPC-style action URLs with resource-oriented endpoints. URLs must describe resources; HTTP methods and request bodies describe intended state changes. Domain side effects still go through services.

Do not remove legacy action endpoints in this phase. Keep them as compatibility aliases until Phase 20.

Target booking API:

```text
GET    /api/v1/bookings/
POST   /api/v1/bookings/
GET    /api/v1/bookings/{booking_id}/
PATCH  /api/v1/bookings/{booking_id}/
DELETE /api/v1/bookings/{booking_id}/
GET    /api/v1/bookings/{booking_id}/decisions/
POST   /api/v1/bookings/{booking_id}/decisions/
GET    /api/v1/bookings/{booking_id}/tables/
PUT    /api/v1/bookings/{booking_id}/tables/
DELETE /api/v1/bookings/{booking_id}/tables/{table_id}/
POST   /api/v1/bookings/{booking_id}/payment-requests/
```

Target walk-in API:

```text
GET    /api/v1/walkins/
POST   /api/v1/walkins/
GET    /api/v1/walkins/{walkin_id}/
PATCH  /api/v1/walkins/{walkin_id}/
DELETE /api/v1/walkins/{walkin_id}/
GET    /api/v1/walkins/{walkin_id}/tables/
PUT    /api/v1/walkins/{walkin_id}/tables/
DELETE /api/v1/walkins/{walkin_id}/tables/{table_id}/
```

Target public customer booking API:

```text
GET    /api/v1/public/bookings/{token}/
PATCH  /api/v1/public/bookings/{token}/
DELETE /api/v1/public/bookings/{token}/
```

Target payment API adjustment:

```text
POST /api/v1/payments/{payment_id}/refunds/
```

### Task 18.1 — Booking PATCH behavior

Keep booking updates on the booking resource. Simple editable fields are routed through the staff modify service. The only direct status change accepted through `PATCH /bookings/{id}/` is `status = "no_show"`, and it must call the existing no-show service.

Rejected direct status changes include approval, decline, payment states, customer cancellation, expiration, and authorization expiry.

Tests:
- Staff can patch editable booking fields through the service.
- `status = "no_show"` uses the state machine and records audit.
- Other status patches are rejected with a code-only validation error.

### Task 18.2 — Booking decisions endpoint

Add booking decision collection endpoints for staff review outcomes.

Required behavior:
- `POST /bookings/{id}/decisions/` creates a decision resource for approval or decline.
- Decision request bodies use `{"outcome": "approved"}` or `{"outcome": "declined", "reason_code": "...", "staff_message": "..."}`.
- Approval and decline must call the existing staff services so payment, notification, audit, and decided-by fields remain correct.
- Confirming without deposit is represented as a decision outcome only when staff explicitly chooses it.

Tests:
- Approved decision produces the same result as the current approve service.
- Declined decision supports `reason_code` and `staff_message`.
- Invalid decision outcomes are rejected.

### Task 18.3 — Booking tables endpoint

Add booking table assignment resource endpoints backed by Phase 17 services.

Required behavior:
- `GET` returns currently assigned table ids.
- `PUT` replaces the assigned table set using `{"tables": ["<table_id>", ...]}`.
- `DELETE /tables/{table_id}/` removes one assignment.

Tests:
- Staff can replace booking tables with multiple table ids.
- Repeating the same `PUT` is idempotent.
- Deleting one table preserves other assignments.

### Task 18.4 — Walk-in tables endpoint

Add the same table assignment resource endpoints for walk-ins.

Required behavior:
- `GET` returns currently assigned table ids.
- `PUT` replaces the assigned table set using `{"tables": ["<table_id>", ...]}`.
- `DELETE /tables/{table_id}/` removes one assignment.

Tests:
- Staff can replace walk-in tables with multiple table ids.
- Repeating the same `PUT` is idempotent.
- Deleting one table preserves other assignments.

### Task 18.5 — Customer public booking PATCH/DELETE

Replace the current public `POST` action payload with HTTP methods on the token resource.

Required behavior:
- `PATCH /public/bookings/{token}/` modifies customer-editable booking fields through `modify_by_customer`.
- `DELETE /public/bookings/{token}/` cancels through `cancel_by_customer`.
- Token validation, throttling, cutoff rules, and code-only errors remain unchanged.
- Accepted customer patch fields remain `starts_at`, `party_size`, and `notes`.

Tests:
- Customer modification works through `PATCH`.
- Customer cancellation works through `DELETE`.
- Invalid, expired, and throttled tokens behave as before.

### Task 18.6 — Payment refunds endpoint rename

Rename the manual refund endpoint to a plural refund collection.

Required behavior:
- `POST /api/v1/payments/{payment_id}/refunds/` triggers the existing manager-only refund service.
- The Stripe webhook remains `POST /stripe/webhook/`.
- Partial refunds remain out of scope.

Tests:
- Managers can create a refund through `/refunds/`.
- Non-managers are rejected.

---

## Phase 19 — Restaurant Config API

Expose restaurant configuration as tenant resources. The dashboard remains an aggregate read model and does not own configuration sub-endpoints.

Target API:

```text
GET|PATCH       /api/v1/restaurant/settings/
GET|POST        /api/v1/restaurant/opening-windows/
GET|PATCH|DELETE /api/v1/restaurant/opening-windows/{id}/
GET|POST        /api/v1/restaurant/closed-days/
GET|PATCH|DELETE /api/v1/restaurant/closed-days/{id}/
GET|POST        /api/v1/restaurant/rooms/
GET|PATCH|DELETE /api/v1/restaurant/rooms/{id}/
GET|POST        /api/v1/restaurant/tables/
GET|PATCH|DELETE /api/v1/restaurant/tables/{id}/
```

### Task 19.1 — Restaurant settings endpoint

Add a tenant-member protected singleton endpoint for booking and deposit settings.

Tests:
- Staff can read settings.
- Managers can update settings when role restrictions are enforced.
- Anonymous users are rejected.

### Task 19.2 — Opening windows endpoint

Expose weekly opening windows as collection/detail resources. Use `OpeningWindow` naming in new API code, while preserving database compatibility if an existing model name differs.

Tests:
- Staff can list opening windows.
- Managers can create, update, and delete opening windows.
- Invalid weekday/time ranges are rejected.

### Task 19.3 — Closed days endpoint

Expose one-off closed days as collection/detail resources.

Tests:
- Staff can list closed days.
- Managers can create, update, and delete closed days.
- Duplicate closed dates are rejected.

### Task 19.4 — Rooms and tables endpoints

Expose floor layout resources for rooms and tables.

Tests:
- Staff can list rooms and tables.
- Managers can create, update, and delete rooms and tables.
- Table labels remain unique per room.

---

## Phase 20 — API Compatibility Cleanup

Remove legacy action-style endpoints after the new resource endpoints and frontend calls are migrated. Compatibility must be explicit and temporary.

### ✅ Task 20.1 — Deprecation tests and documentation

Document all old endpoints as deprecated and add tests that define the expected compatibility behavior until removal.

Deprecated endpoints:
- `POST /api/v1/bookings/{id}/approve/`
- `POST /api/v1/bookings/{id}/decline/`
- `POST /api/v1/bookings/{id}/modify/`
- `POST /api/v1/bookings/{id}/assign-table/`
- `POST /api/v1/bookings/{id}/mark-no-show/`
- `POST /api/v1/bookings/{id}/confirm-without-deposit/`
- `POST /api/v1/bookings/{id}/request-payment/`
- `POST /api/v1/public/bookings/{token}/`
- `POST /api/v1/payments/{id}/refund/`

### Task 20.2 — Frontend/backend contract verification

Verify the frontend uses only the normalized endpoints before removing legacy routes.

Tests:
- Backend route tests cover every supported normalized endpoint.
- No frontend API client references deprecated endpoint strings.

### Task 20.3 — Remove old action endpoints

Remove legacy routes and old tests after contract verification passes.

Tests:
- Deprecated endpoints return 404 or are absent from URL resolution.
- Full backend suite passes with only normalized endpoint tests.
