# MVP Technical Scope

## 1. Frontend

- Expo + React Native Web
- Tamagui
- Shared web/mobile codebase foundation
- Shared i18n JSON files
- No hardcoded frontend strings

## 2. Backend

- Django
- Django REST Framework
- Django Auth
- django-allauth

## 3. Multi-Tenancy

- django-tenants
- PostgreSQL schema-per-tenant
- One public schema for shared tenant/domain data
- One schema per restaurant
- Tenant routing: path-based via `TenantSubfolderMiddleware` (not subdomain-based)
- Tenant URL prefix: `/restaurants/<slug>/` (`TENANT_SUBFOLDER_PREFIX = "restaurants"`)

## 4. Database

- PostgreSQL
- Core entities only:
  - restaurants
  - users
  - staff memberships
  - rooms
  - tables
  - bookings
  - payments
  - notification logs

## 5. Authentication & Authorization

- Django Auth + django-allauth
- MVP roles:
  - manager
  - staff
- Viewer role postponed
- Tenant-aware permissions

## 6. Payments

- Stripe only for MVP
- PayPal postponed
- Stripe webhooks required
- Payment abstraction layer kept minimal but designed to support PayPal later
- Near-term flow uses Stripe Payment Element with PaymentIntent
  `capture_method=manual`
- Booking is created first; the PaymentIntent is created and confirmed
  afterwards
- Long-term flow uses a Stripe-hosted payment link sent after staff approval;
  payment must complete within 24 hours
- Capture happens immediately after staff approval (near-term flow)
- Payment lifecycle is tracked separately from booking status (see business
  doc §2 for the full payment status set)

## 7. Notifications

- Twilio SMS
- Email via Django SMTP (provider e.g. SendGrid or Mailgun via SMTP)
- In-app notification basics
- Notification templates stored by code
- Server-side template localization keyed off `Customer.locale`
- Supported locales (MVP): `en`, `it`, `de`. Default and fallback: `en`
- Templates are stored per code per locale
- Advanced template editor postponed

## 8. Background Processing

No Celery/Redis in MVP.

MVP uses synchronous operations and opportunistic checks:

- Twilio SMS sent synchronously
- Payment expiration checked on admin dashboard load
- Pending-review expiration checked on admin dashboard load
- Payment reconciliation checked on admin dashboard load
- Failed SMS/payment actions logged for manual retry

Important:
- SMS failure must not block booking flow
- Stripe webhooks are still required
- This should be revisited after MVP

## 9. Internationalization

- API returns:
  - status codes
  - reason codes
  - error codes
- Frontend maps codes to localized strings
- No user-facing strings returned directly from API except staff-written custom messages

## 10. Admin Interface

- Custom Expo/Tamagui admin UI
- Django Admin allowed for internal/dev operations only
- MVP admin features:
  - bookings list
  - approve/reject booking
  - modify booking
  - assign table
  - configure basic restaurant settings

## 11. Floor/Table Management

- Basic room/table setup
- Tables can be added manually
- Tables can be moved visually
- Store coordinates in DB
- Table combinations postponed from MVP

## 12. Hosting

- Frontend: Vercel
- Backend: Hugging Face Spaces (Docker SDK)
- Database: Supabase free tier (managed PostgreSQL, EU region)
  - No compute auto-suspend (unlike Neon)
  - Project pauses after 7 days of inactivity — mitigated by a GitHub Actions scheduled workflow pinging `/healthz/` every 6 days
  - django-tenants connects via direct connection URL (not Supabase's pooler)

## 13. Domain

- Frontend: `tablesched.domenicocaruso.com` — hosted on Vercel; CNAME configured on MisterDomain pointing to Vercel
- API: `tablesched.hf.space` — Hugging Face Spaces; no custom domain required
- Tenant routing is path-based (see §3); no wildcard DNS needed
- Demo tenants:
  - `tablesched.hf.space/restaurants/new-york/api/v1/`
  - `tablesched.hf.space/restaurants/rome/api/v1/`
- Frontend maps the restaurant slug to the correct API path prefix

## 14. Observability

MVP minimum:

- backend logs
- payment webhook logs
- notification delivery logs
- basic audit log for booking/payment actions

Advanced monitoring postponed.

## 14a. Customer Booking Access (Tokenized Links)

- Customers do not authenticate. Access to a booking is granted by a secure
  token sent via SMS and/or email after booking request.
- Token is tied to one booking only.
- Token is random, long, and unguessable (cryptographic random, ≥ 32 bytes
  base64url-encoded).
- Token expires 7 days after the booking datetime.
- Token grants: view, cancel, modify (subject to the cancellation/modification
  cutoff in business doc §5 and §11).
- No OTP / phone verification in MVP.

## 15. Security

- Tenant isolation enforced by django-tenants
- Backend validates all tenant access
- Stripe webhook signature verification
- Twilio credentials stored server-side only
- No payment card data stored locally

## 16. Explicitly Out of MVP

- PayPal
- RAG
- advanced notification editor
- configurable reminder rules
- advanced capacity engine
- automatic table assignment
- table combinations
- complex refund automation
- partial refunds
- viewer role
- advanced analytics
- mobile app release
- customer registration / accounts
- OTP / phone verification
