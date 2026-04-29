# Architecture Overview

## Frontend

The frontend is an Expo Router application with route groups for public and staff experiences.

### File structure

- `frontend/app/(public)/...` for customer booking flows
- `frontend/app/(staff)/...` for staff login, dashboard, settings, and floor plan views
- `frontend/components/` for shared UI and domain components
- `frontend/lib/` for API clients, auth, i18n, and shared helpers

### Data flow

1. UI components call hooks or query functions from React Query.
2. Query functions use the API client in `frontend/lib/api`.
3. The API client talks to the Django backend through the configured base URL.
4. Auth state is stored in the frontend auth context and reused across staff screens.

### Rendering model

- Public booking pages are single-column and centered.
- Staff screens use shared UI primitives and responsive shell layout on wide screens.
- Tamagui provides styling primitives and theming across the app.

### Internationalization

- `frontend/lib/i18n` loads locale files from `frontend/lib/i18n/locales/`.
- English is the source of truth for keys.
- Italian and German must stay aligned with English.

## Backend API

- Public customer booking tokens expose the booking resource at `GET|PATCH|DELETE /api/v1/public/bookings/{token}/`.
- Customer booking changes go through `modify_by_customer`; customer cancellation goes through `cancel_by_customer`.
- Manual manager refunds use `POST /api/v1/payments/{payment_id}/refunds/`; the Stripe webhook remains `POST /stripe/webhook/`.
- Tenant restaurant settings are exposed at `GET|PATCH /api/v1/restaurant/settings/`; reads require tenant membership and updates require manager role.
- Tenant opening windows are exposed at `/api/v1/restaurant/opening-windows/`; reads require tenant membership and writes require manager role.
- Legacy public booking `POST` and singular payment refund aliases remain until the Phase 20 API cleanup.
