# Restaurant Booking Web App (MVP)

## Overview

Web application for managing restaurant reservations with a **staff-driven approval workflow**.

Customers submit booking requests. Staff review, approve/reject, optionally collect a deposit, and manage tables manually.

---

## Core Flow

Customer → Booking Request → Staff Review → (Optional Payment) → Confirmation


---

## Key Features

- Booking request (time slot + party size)
- Staff approval / rejection
- Optional deposit (Stripe)
- Manual table assignment (no automatic allocation)
- SMS notifications (Twilio)
- Multi-restaurant (multi-tenant) support
- Shared web/mobile frontend (Expo + React Native Web)

---

## Tech Stack

### Frontend
- Expo (React Native)
- React Native Web
- Tamagui
- i18n (no hardcoded strings)

### Backend
- Django
- Django REST Framework
- django-allauth (authentication)
- django-tenants (multi-tenancy)

### Database
- PostgreSQL (schema per tenant)

### Integrations
- Stripe (payments)
- Twilio (SMS)

---

## MVP Scope

Included:
- Basic booking lifecycle
- Staff dashboard (approve/reject/modify)
- Deposit handling (simple)
- SMS notifications
- Opening hours

Excluded:
- Automatic table assignment
- Table combinations
- Advanced capacity logic
- PayPal
- Advanced notifications/reminders

---

## Notes

- Booking is always a **request**, never auto-confirmed
- System provides **decision support**, not enforcement
- Designed to evolve toward mobile app and advanced automation

## License

This project is proprietary software.

See `LICENSE.txt` for full details.
