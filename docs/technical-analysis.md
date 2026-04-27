# Tech Stack & Technical Decisions

## 1. Frontend

### Framework
- Expo (React Native)
- React Native Web (shared codebase for web and mobile)

### UI System
- Tamagui
  - Used for cross-platform components (web + mobile)
  - Custom design system built on top (tokens, themes, components)
  - No reliance on default styling

### Component Strategy
- Base components from Tamagui
- Custom product components:
  - RestaurantCard
  - BookingSlotPicker
  - AdminRoomEditor
  - TableItem (draggable)
- Shared design tokens between web and mobile

### Internationalization (i18n)
- No hardcoded strings in frontend
- Shared i18n JSON files between web and mobile
- API returns only codes/statuses
- Frontend maps codes → localized strings

---

## 2. Backend

### Framework
- Django
- Django REST Framework (API layer)

### Authentication
- Django Auth
- django-allauth
  - Social login
  - Magic link / code login
  - Email/password

### Authorization
- Django groups/roles:
  - manager
  - staff
  - viewer
- Custom permission logic (tenant-aware)

### Multi-tenancy
- django-tenants (schema-per-tenant)
- PostgreSQL schemas:
  - public schema (shared data)
  - one schema per restaurant

### Database
- PostgreSQL
- Tenant isolation via schema separation

---

## 3. Payments

### Providers
- Stripe
- PayPal

### Payment Model
- Dual strategy:
  - Pre-authorization (near-term bookings)
  - Payment after approval (long-term bookings)

### Payment Handling
- Authorization + capture (Stripe/PayPal)
- Webhook-driven state updates (source of truth)
- Payment abstraction layer (provider-agnostic)

### Refunds
- Hybrid model:
  - Automatic (policy-based)
  - Manual override
- Partial refunds supported
- Retry mechanism for failed refunds

---

## 4. Notifications

### Channels
- In-app notifications
- SMS via Twilio

### SMS
- Twilio integration
- Retry mechanism on failure
- Non-blocking (failures do not break flows)

### Notification System
- Template-based
- Per-tenant configuration
- i18n-compatible

---

## 5. Background Processing

### Task System
- Celery + Redis (recommended)
  - Reminders
  - Payment checks
  - Expiration handling
  - Notification delivery

### Alternative (MVP)
- Django cron jobs / management commands

---

## 6. Scheduling / Reminders

### Configurable per tenant
- Multiple reminder rules allowed
- Anchors:
  - after_request_datetime
  - before_booking_datetime
  - before_authorization_expiry_datetime

### Behavior
- Rules stored as structured configuration
- Conditional execution (e.g. skip if no authorization)

---

## 7. Booking System Architecture

### Core Principles
- No automatic table assignment
- Backend provides decision support (not enforcement)
- Soft limits (capacity warnings, not hard blocks)

### Table Management
- Tables defined per room
- Joinable tables via explicit admin-defined combinations
- No automatic capacity calculation for joins

### Floor Editor
- Custom implementation
- Drag & drop using:
  - React Native Gesture Handler
  - Reanimated
- Coordinates stored in DB

---

## 8. API Design

### Principles
- API returns codes, not user-facing strings
- Stateless REST API
- Strong validation at backend

### Error Handling
- Standardized error codes
- Frontend handles localization

---

## 9. Hosting & Infrastructure

### Frontend Hosting
- Vercel

### Backend Hosting
- Hugging Face (MVP only)
- Future migration recommended:
  - Render / Fly.io / Railway / Cloud provider

### Domain
- Subdomain structure:
  - `xxx.domenicocaruso.com`

---

## 10. Data & Compliance

### Audit Log
- Track:
  - booking actions
  - payment actions
  - admin overrides
  - refunds

### Timezone
- Per-restaurant timezone
- All backend logic uses restaurant timezone

### Data Protection
- GDPR considerations:
  - data retention
  - deletion
  - export

---

## 11. System Design Principles

- API-first backend
- Clear separation:
  - frontend (UI + i18n)
  - backend (logic + codes)
- Multi-tenant isolation at DB level
- Provider abstraction (payments, SMS)
- Event-driven updates (webhooks + async jobs)
- Configurable behavior per tenant
