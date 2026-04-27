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
- Deposit flow:
  - pre-authorization for near-term bookings
  - payment link after approval for long-term bookings
  - capture immediately after staff approval

## 7. Notifications

- Twilio SMS
- In-app notification basics
- Notification templates stored by code
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
- Backend: Hugging Face for MVP
- Database: managed PostgreSQL
- Redis: managed Redis or lightweight hosted Redis

## 13. Domain

- Web app under subdomain of `domenicocaruso.com`
- API under separate subdomain if needed

## 14. Observability

MVP minimum:

- backend logs
- payment webhook logs
- notification delivery logs
- basic audit log for booking/payment actions

Advanced monitoring postponed.

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
