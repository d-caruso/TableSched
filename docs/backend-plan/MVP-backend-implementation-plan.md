# MVP Backend Implementation Plan — Index

Backend-only implementation plan for the Restaurant Booking MVP.

Strict references — anything in this plan that conflicts with these docs is wrong:
- `docs/MVP-business-analysis.md`
- `docs/MVP-technical-analysis.md`
- `CLAUDE.md` (engineering rules: KISS, YAGNI, DRY, file <500 LOC, function <50 LOC, class <100 LOC, no hardcoded user-facing strings, branching policy)

The plan is split into four phase groups. Each group is one file:

1. [`01-foundation-Phases-1-3.md`](./01-foundation-Phases-1-3.md) — **Phases 1–3**
   - Phase 1: Repository & Project Bootstrap
   - Phase 2: Multi-Tenancy Foundation
   - Phase 3: Common Infrastructure (codes, errors, base classes)

2. [`02-domain-core-Phases-4-7.md`](./02-domain-core-Phases-4-7.md) — **Phases 4–7**
   - Phase 4: Authentication & Authorization (staff only)
   - Phase 5: Customers & Booking Access Tokens
   - Phase 6: Restaurant Configuration
   - Phase 7: Booking Lifecycle

3. [`03-payments-and-notifications-Phases-8-10.md`](./03-payments-and-notifications-Phases-8-10.md) — **Phases 8–10**
   - Phase 8: Payments (Stripe only)
   - Phase 9: Notifications (Twilio SMS + Django SMTP, synchronous, localized)
   - Phase 10: Walk-ins

4. [`04-ops-Phases-11-16.md`](./04-ops-Phases-11-16.md) — **Phases 11–16**
   - Phase 11: Opportunistic Background Sweeps
   - Phase 12: Audit Log
   - Phase 13: Security Hardening
   - Phase 14: Testing Strategy
   - Phase 15: Observability
   - Phase 16: Deployment Prep

---

## Out of Scope (do not implement, even partially)

PayPal, automatic table assignment, table combinations, advanced capacity engine, advanced reminder system, advanced refund automation, partial refunds, viewer role, analytics, RAG, customer registration / accounts, OTP / phone verification, mobile app release.

---

## Cross-Cutting Compliance Checklist (CLAUDE.md)

These rules apply to **every** phase. Verify before merging any phase branch.

- [ ] No file > 500 LOC (split apps when nearing limit)
- [ ] No function > 50 LOC (extract helpers in `services/`)
- [ ] No class > 100 LOC (favor service modules over fat models)
- [ ] No hardcoded user-facing strings in API responses (codes only; staff messages excepted)
- [ ] Every feature has tests (Phase 14)
- [ ] Every PR follows BRANCHING_STRATEGY.md and pre-merge checks
- [ ] Documentation updated per CLAUDE.md "Documentation Update Policy" after each phase
