# Business Logic & Requirements

## 1. Booking Model

### Customer Input
- Booking is based on:
  - Time slot (15-minute granularity)
  - Party size
- No table selection by customer
- Customer provides:
  - Phone number (mandatory)
  - Optional notes (e.g. accessibility, stroller)

### Booking Nature
- Booking is a **request**, not immediate confirmation
- Requires staff approval (configurable per restaurant)

---

## 2. Booking Lifecycle

### Booking Statuses

- `pending_review`
- `pending_payment`
- `confirmed`
- `confirmed_without_deposit`
- `declined`
- `cancelled_by_customer`
- `cancelled_by_staff`
- `no_show`
- `expired`
- `authorization_expired`

### Payment Statuses

Payment lifecycle is tracked separately from booking status.

- `pending`
- `authorized`
- `captured`
- `failed`
- `refund_pending`
- `refunded`
- `refund_failed`

### Expiration Rules

- `pending_review` → expires after configurable time (default: 3 days)
- `pending_payment` → expires after 24 hours if not paid
- Authorization expiry → based on payment provider

---

## 3. Availability Model

### Core Principle
- No automatic table assignment
- Staff decides whether to accept or reject bookings

### Capacity Handling
- Soft limits only (no hard blocking)
- System provides:
  - Global restaurant occupancy
  - Per-room occupancy
  - Booking count per slot

### Customer Experience
- Booking always allowed during opening hours
- If capacity exceeded → warning shown

---

## 4. Table Management

### Tables
- Defined per room/area
- Positioned via admin interface

### Table Combinations
- Manually defined by staff
- Each combination includes:
  - List of tables
  - Final seating capacity
- No automatic calculation of joined capacity

### Assignment
- Table assignment is internal
- Can be done:
  - After approval
  - Later
  - Modified at any time

---

## 5. Payment & Deposit

### Deposit Policy (per restaurant)
- Options:
  - Never
  - Always
  - Only for party size ≥ N

### Payment Strategy

#### Near-term bookings
- Pre-authorization at booking time
- Capture immediately after staff approval

#### Long-term bookings
- No payment at booking time
- Payment requested after approval
- Payment deadline: 24 hours

### Payment Failure Handling
- Staff can:
  - Confirm booking anyway
  - Refuse booking with reason

### Refund Policy
- Hybrid:
  - Automatic (based on policy)
  - Manual override allowed
- Partial refunds supported
- Failed refunds:
  - Status tracked
  - Retry possible

---

## 6. Cancellation & Modification

### Customer Cancellation
- Allowed until configurable cutoff (e.g. 24h before)
- After cutoff:
  - Not allowed via system
  - Manual handling required

### Customer Modification
- Allowed until same cutoff as cancellation
- After cutoff:
  - Not allowed or restricted

### Deposit Impact
- Refund depends on cancellation timing
- Modification may change deposit amount

### Approval Impact
- If approval mode enabled:
  - Modification requires re-approval

---

## 7. Staff Roles

- `manager`
- `staff`
- `viewer`

### Permissions
- Staff:
  - Approve/reject bookings
  - Assign tables
- Manager:
  - Configure rules, payments, settings
- Viewer:
  - Read-only access

---

## 8. Notifications

### Channels
- In-app
- SMS (optional)

### Events
- Booking request received
- Booking approved
- Payment required
- Booking confirmed
- Booking declined
- Booking cancelled
- Booking modified
- Reminder
- Refund processed

### Templates
- Configurable per restaurant
- Support i18n

---

## 9. Staff Reminders

### Configuration
- Per restaurant
- Multiple rules allowed

### Anchors
- After request datetime
- Before booking datetime
- Before authorization expiry datetime

### Default Rule
- +1 hour after booking request

### Behavior
- Reminders skipped if anchor not applicable (e.g. no authorization)

---

## 10. Walk-ins

- Can be added by staff
- Count toward capacity
- Can be assigned tables
- Do not become bookings
- No customer phone required

---

## 11. Opening Hours

### Weekly Schedule
- Configurable per day of week

### Exceptions
- Off days
- Off hours
- Special closures

---

## 12. Booking Limits

- Slot interval: 15 minutes
- Advance booking limit: 90 days
- Booking cutoff: up to 5 minutes before

---

## 13. Customer Model

- Supports:
  - Guest bookings
  - Registered users

---

## 14. Public Restaurant Profile

Includes:
- Name
- Address
- Opening hours
- Booking rules
- Policies
- Contact info

---

## 15. Audit & Tracking

Track:
- Booking actions (approve, reject, modify)
- Payment actions
- Refund actions
- Admin overrides

---

## 16. Timezone

- Each restaurant has its own timezone
- All booking logic uses restaurant timezone

---

## 17. Data Protection

- Handle:
  - Phone numbers
  - Payment references
  - Booking history
- Support:
  - Data retention
  - Deletion
  - Export
