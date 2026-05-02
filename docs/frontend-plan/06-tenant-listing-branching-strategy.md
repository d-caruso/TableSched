# Branching Strategy — Feature: Tenant Directory Page

References:
- Implementation plan: [`06-tenant-listing.md`](./06-tenant-listing.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text via i18n keys.
- **Tests are mandatory** for every task that introduces logic.
- **Each task branch lifecycle:** create from parent → implement → commit → pre-merge checks → push → merge into parent.
- **Progress markers:** ❌ not done · ✅ done. Update in place as work completes.

## Pre-Merge Checks (run in this order, one at a time)

```bash
# Run all commands from the frontend/ directory
npm run build
npm run typecheck
npm run lint
npm test -- <path/to/specific.test.tsx>   # specific file first
npm test                                   # full suite only if above passes
```

---

## Branch Hierarchy

```
develop
└── feature/frontend-tenant-listing
    ├── task/frontend-tenant-listing-Task1-api-method
    ├── task/frontend-tenant-listing-Task2-index-page
    ├── task/frontend-tenant-listing-Task3-tests
    └── task/frontend-tenant-listing-Task4-landing-page
```

---

## Feature branch setup

**⚠️ Create this branch from `develop` before starting any task.**

```bash
git checkout develop
git pull origin develop
git checkout -b feature/frontend-tenant-listing
git push -u origin feature/frontend-tenant-listing
```

---

## ❌ Task 1 — Add `tenantDirectory` to `publicApi`

Add `TenantEntry` type to `lib/api/types.ts` and `tenantDirectory()` method to `lib/api/endpoints.ts`.

**Branch:** `task/frontend-tenant-listing-Task1-api-method` — created from `feature/frontend-tenant-listing`

```bash
git checkout feature/frontend-tenant-listing
git pull origin feature/frontend-tenant-listing
git checkout -b task/frontend-tenant-listing-Task1-api-method
```

**Files to modify:**
- `lib/api/types.ts`
- `lib/api/endpoints.ts`

**Commit:**
```bash
git add lib/api/types.ts lib/api/endpoints.ts
git commit -m "[TASK] Task 1 - add tenantDirectory endpoint to publicApi"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/api/urlPatterns.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-tenant-listing-Task1-api-method
git checkout feature/frontend-tenant-listing
git merge task/frontend-tenant-listing-Task1-api-method
git push origin feature/frontend-tenant-listing
```

---

## ❌ Task 2 — Root index page

Create `app/index.tsx` with the tenant directory gated by `EXPO_PUBLIC_SHOW_TENANT_DIRECTORY`. Add `SHOW_TENANT_DIRECTORY` to `lib/env.ts` and i18n keys to all three locale files.

Directory layout: restaurant names as clickable booking links; a single "Staff Login" button at the bottom pointing to `/login` (staff login is centralised — not per-tenant).

**Branch:** `task/frontend-tenant-listing-Task2-index-page` — created from `feature/frontend-tenant-listing`

**⚠️ Create only after Task 2 is merged into `feature/frontend-tenant-listing`.**

```bash
git checkout feature/frontend-tenant-listing
git pull origin feature/frontend-tenant-listing
git checkout -b task/frontend-tenant-listing-Task2-index-page
```

**Files to modify/create:**
- `app/index.tsx` — NEW
- `lib/env.ts`
- `lib/i18n/locales/en.json`
- `lib/i18n/locales/it.json`
- `lib/i18n/locales/de.json`

**Commit:**
```bash
git add app/index.tsx lib/env.ts \
  lib/i18n/locales/en.json lib/i18n/locales/it.json lib/i18n/locales/de.json
git commit -m "[TASK] Task 2 - add tenant directory root page"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/TenantDirectory.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-tenant-listing-Task2-index-page
git checkout feature/frontend-tenant-listing
git merge task/frontend-tenant-listing-Task2-index-page
git push origin feature/frontend-tenant-listing
```

---

## ❌ Task 3 — Tests

Write tests for the tenant directory page: renders tenant rows when flag is enabled, redirects when flag is disabled.

**Branch:** `task/frontend-tenant-listing-Task3-tests` — created from `feature/frontend-tenant-listing`

**⚠️ Create only after Task 3 is merged into `feature/frontend-tenant-listing`.**

```bash
git checkout feature/frontend-tenant-listing
git pull origin feature/frontend-tenant-listing
git checkout -b task/frontend-tenant-listing-Task3-tests
```

**Files to create:**
- `__tests__/TenantDirectory.test.tsx` — NEW

**Commit:**
```bash
git add __tests__/TenantDirectory.test.tsx
git commit -m "[TASK] Task 3 - add tests for tenant directory page"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/TenantDirectory.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-tenant-listing-Task3-tests
git checkout feature/frontend-tenant-listing
git merge task/frontend-tenant-listing-Task3-tests
git push origin feature/frontend-tenant-listing
```

---

## ❌ Task 4 — Branded landing page

When `SHOW_TENANT_DIRECTORY` is false, render a minimal branded landing page instead of blank.

**Branch:** `task/frontend-tenant-listing-Task4-landing-page` — created from `feature/frontend-tenant-listing`

**⚠️ Create only after Task 3 is merged into `feature/frontend-tenant-listing`.**

```bash
git checkout feature/frontend-tenant-listing
git pull origin feature/frontend-tenant-listing
git checkout -b task/frontend-tenant-listing-Task4-landing-page
```

**Files to modify:**
- `app/index.tsx`
- `lib/i18n/locales/en.json`
- `lib/i18n/locales/it.json`
- `lib/i18n/locales/de.json`

**Commit:**
```bash
git add app/index.tsx lib/i18n/locales/en.json lib/i18n/locales/it.json lib/i18n/locales/de.json
git commit -m "[TASK] Task 4 - show branded landing page when directory is disabled"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/TenantDirectory.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-tenant-listing-Task4-landing-page
git checkout feature/frontend-tenant-listing
git merge task/frontend-tenant-listing-Task4-landing-page
git push origin feature/frontend-tenant-listing
```

---

## ❌ Feature complete — merge into develop

All tasks (1–4) complete. Run the full pre-merge checklist one final time:

```bash
npm run build
npm run typecheck
npm run lint
npm test
```

All checks must pass. Then — with explicit confirmation:

```bash
git checkout develop
git merge feature/frontend-tenant-listing
git push origin develop
```
