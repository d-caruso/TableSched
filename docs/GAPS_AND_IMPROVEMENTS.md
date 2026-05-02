# Gaps and Improvements

## Backend

Known post-MVP backend gaps:

- **Per-tenant Stripe accounts** — currently all tenants share a single Stripe account (controlled by the platform). Future premium feature: each `RestaurantSettings` stores its own `stripe_api_key` and `stripe_webhook_secret`; the webhook verifies signatures using the correct tenant's secret resolved from `metadata.tenant_schema`.
- **JWT refresh endpoint not wired in frontend** — `/_allauth/app/v1/auth/token` can issue a new access token from a refresh token, but the frontend `AuthContext` does not yet call it when the access token expires. Staff will be silently logged out after 15 minutes until this is implemented.
- **`cryptography` not pinned in `pyproject.toml`** — required by allauth's JWT strategy but installed manually. Should be added as an explicit dependency.

## Frontend

Known post-MVP frontend gaps:

- Native mobile app release process still needs to be defined.
- Floor plan editor on mobile touch devices needs dedicated UX work.
- Viewer-role UI is still not implemented.
- Responsive staff sidebar is desktop-focused and should be validated on tablets.
- Internationalization coverage should be kept in sync as new strings are added.
- **Single `/login` with tenant selector** — currently each tenant has its own `/restaurants/{slug}/login` URL. Post-MVP: a single `/login` page where staff enter email + password, the backend resolves all `StaffMembership` records for that user, and if multiple tenants are found a "Select restaurant" screen is shown before redirecting to the correct dashboard.
- **Per-tenant visual theming** — two options with increasing complexity:
  - *Option A — Skin only*: the restaurant API response includes a `branding` object (`primary_color`, `accent_color`, `logo_url`, `font_family`). The `[tenant]/_layout.tsx` wraps children in a dynamic Tamagui theme built from those tokens. Page structure and all components stay identical across tenants.
  - *Option B — Swappable named layouts*: the API response adds a `layout` field (e.g. `"classic"`, `"minimal"`, `"compact"`). The `[tenant]/_layout.tsx` switches which shell component it renders based on that value. Components inside remain shared; only the outer frame (header style, sidebar vs. top-nav, hero section) differs. Each new variant is a new shell component to maintain and requires a frontend release to deploy.

