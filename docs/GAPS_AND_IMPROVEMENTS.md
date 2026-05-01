# Gaps and Improvements

## Backend

Known post-MVP backend gaps:

- **Per-tenant Stripe accounts** — currently all tenants share a single Stripe account (controlled by the platform). Future premium feature: each `RestaurantSettings` stores its own `stripe_api_key` and `stripe_webhook_secret`; the webhook verifies signatures using the correct tenant's secret resolved from `metadata.tenant_schema`.

## Frontend

Known post-MVP frontend gaps:

- Native mobile app release process still needs to be defined.
- Floor plan editor on mobile touch devices needs dedicated UX work.
- Viewer-role UI is still not implemented.
- Responsive staff sidebar is desktop-focused and should be validated on tablets.
- Internationalization coverage should be kept in sync as new strings are added.
- **Single `/login` with tenant selector** — currently each tenant has its own `/restaurants/{slug}/login` URL. Post-MVP: a single `/login` page where staff enter email + password, the backend resolves all `StaffMembership` records for that user, and if multiple tenants are found a "Select restaurant" screen is shown before redirecting to the correct dashboard.

