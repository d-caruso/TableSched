# MVP Business Scope

## Goal

Validate the core workflow:

Customer → booking request → staff approval → (optional) deposit → confirmation


---

## 1. Booking Flow

### Customer Side
- Select:
  - Date
  - Time slot (15-minute intervals)
  - Party size
- Provide:
  - Phone number (required)
  - Email (optional)
  - Name (required)
  - Preferred language / locale (required)
  - Optional notes (free text)

- Booking is always a **request**, not immediate confirmation
- Customers do not register or authenticate. After submitting a booking
  request, the customer receives a secure tokenized link (via SMS and/or
  email) that grants access to view, cancel, or modify that single booking.

### Staff Side
- View incoming booking requests
- Actions:
  - Approve
  - Reject
  - Modify (date, time, party size)
  - Assign table (optional)

---

## 2. Statuses (MVP)

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

---

## 3. Availability

- No automatic table assignment
- No hard blocking of bookings
- Customers can always request bookings during opening hours
- Optional warning shown when slot is busy

---

## 4. Payments (MVP)

### Deposit Policy
- Configurable per restaurant:
  - Never
  - Always
  - Only for party size ≥ N

### Payment Flows

#### Near-term bookings

- Booking is created first with status `pending_review`
- If deposit is required, a Stripe PaymentIntent is created afterwards
- Authorization is handled via Stripe Payment Element
- The PaymentIntent uses `capture_method=manual`
- After successful authorization:
  - `Payment.status` becomes `authorized`
  - `Booking.status` remains `pending_review`
- If staff approves the booking:
  - the authorization is captured immediately
  - `Payment.status` becomes `captured`
  - `Booking.status` becomes `confirmed`

#### Long-term bookings
- No payment at booking request
- Payment required after staff approval
- Payment must be completed within 24 hours

### Payment Failure
- Staff can:
  - Confirm booking without deposit
  - Reject booking with reason

### Authorized Deposit Expiration

If a payment pre-authorization expires before staff approval, the booking is not automatically cancelled.

The booking status becomes `authorization_expired`, staff is notified, and staff must choose one of the following actions:

- confirm the booking without deposit
- request payment again
- decline the booking with reason

### Refunds
- Supported (basic)
- Triggered manually by staff/manager
- No advanced automation in MVP

---

## 5. Cancellation & Modification

### Customer
- Can cancel or modify booking until configurable cutoff (e.g. 24h before)
- After cutoff:
  - Action not allowed via system

### Effects
- Deposit refund depends on timing
- Modification may require re-approval

---

## 6. Opening Hours

- Weekly schedule per restaurant
- Support for:
  - Closed days
  - Closed time ranges

---

## 7. Tables & Rooms

### Rooms
- Restaurant can define multiple rooms/areas

### Tables
- Tables defined per room
- Tables can be positioned visually

### Assignment
- Table assignment is internal
- Not required for booking confirmation

### Excluded in MVP
- Table combinations (joined tables)

---

## 8. Staff Roles (MVP)

- `manager`
- `staff`

### Capabilities
- Approve/reject bookings
- Modify bookings
- Assign tables
- Configure basic restaurant settings

---

## 9. Notifications

### Customer Notifications (SMS / Email)

Phone number is mandatory, so SMS is always sent. Email is optional; when
provided, the same notifications are also sent by email.

Notifications:
- Booking request received
- Booking approved
- Booking declined
- Payment required

Server-side localization is required: notification text is rendered on the
backend in the customer's locale (see §1).

### Staff Notifications
- New booking request

### Notes
- Basic templates only
- No advanced customization

---

## 10. Walk-ins

- Staff can add walk-ins
- Walk-ins:
  - Occupy capacity
  - Can be assigned tables
  - Do not become bookings
  - No customer phone required

---

## 11. Booking Limits

- Time slot interval: 15 minutes
- Booking cutoff: up to 5 minutes before
- Advance booking limit: 90 days

---

## 12. Customer Model

- Only guest bookings in MVP. No customer accounts, no authentication.
- Customer record fields: phone (required), email (optional), name (required), locale (required).
- Dedupe by phone: same phone = same customer; different phone = different customer.
- Email is secondary metadata; it does not merge customers.
- If the same phone provides a different email later, update the email; previous email may be retained as history.

---

## 13. Multi-Restaurant Support

- Multiple restaurants (tenants)
- Each restaurant has:
  - Own settings
  - Own bookings
  - Own staff

---

## 14. Public Restaurant Page

- Display:
  - Name
  - Opening hours
  - Booking form
  - Basic policies

---

## 15. Simplifications (MVP)

- No automatic table assignment (the system does NOT decide or reserve tables. Staff does it manually)
- No table combination logic
- No advanced capacity engine
- No advanced reminder system
- No PayPal
- No advanced refund automation
- No advanced notification configuration
- No analytics/dashboard beyond basic booking list
