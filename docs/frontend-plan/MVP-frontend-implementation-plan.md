# MVP Frontend Implementation Plan — Index

Frontend-only implementation plan for the Restaurant Booking MVP.
The backend is fully implemented. This plan targets web-first deployment on Vercel using Expo + React Native Web + Tamagui.

Strict references — anything in this plan that conflicts with these docs is wrong:
- `docs/MVP-business-analysis.md`
- `docs/MVP-technical-analysis.md`
- `CLAUDE.md` (KISS, YAGNI, DRY, file <500 LOC, function <50 LOC, class <100 LOC, no hardcoded strings, branching policy)

---

The plan is split into three phase groups:

1. [`01-foundation-Phases-1-3.md`](./01-foundation-Phases-1-3.md) — **Phases 1–3**
   - Phase 1: Repository & Project Bootstrap (Expo, Tamagui, Expo Router, env)
   - Phase 2: Shared Infrastructure (i18n, API client, auth context, UI kit)
   - Phase 3: Public Booking Page (restaurant info display, multi-step booking form)

2. [`02-customer-and-staff-Phases-4-7.md`](./02-customer-and-staff-Phases-4-7.md) — **Phases 4–7**
   - Phase 4: Customer Tokenized Booking Access (view, cancel, modify via token link)
   - Phase 5: Customer Payment Flow (Stripe Payment Element, redirect handling)
   - Phase 6: Staff Authentication (login screen, JWT storage, auth guard)
   - Phase 7: Staff Bookings Dashboard (list, detail, approve/reject, walk-ins)

3. [`03-staff-settings-and-polish-Phases-8-10.md`](./03-staff-settings-and-polish-Phases-8-10.md) — **Phases 8–10**
   - Phase 8: Staff Restaurant Settings (opening hours, deposit policy)
   - Phase 9: Floor Plan Editor (visual drag-and-drop table positioning)
   - Phase 10: i18n Completion & Polish (en/it/de, responsive layout, docs)

---

## Out of Scope (do not implement, even partially)

PayPal, automatic table assignment, table combinations, advanced capacity engine, advanced reminder system, complex refund automation, partial refunds, viewer role, analytics, RAG, customer registration / accounts, OTP / phone verification, mobile app release.

---

## Cross-Cutting Compliance Checklist (CLAUDE.md)

These rules apply to **every** phase. Verify before merging any phase branch.

- [ ] No file > 500 LOC (split components when nearing limit)
- [ ] No function > 50 LOC (extract into hooks or helpers)
- [ ] No hardcoded user-facing strings (all text via i18n keys)
- [ ] No hardcoded API error messages (map error codes to i18n keys)
- [ ] Every screen tested end-to-end against the running backend
- [ ] Every PR follows BRANCHING_STRATEGY.md and pre-merge checks
- [ ] Documentation updated per CLAUDE.md after each phase
