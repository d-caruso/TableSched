# Branching Strategy — Phases 17-20: Adjustments

References:
- Implementation plan: [`05-adjustments-Phases-17-20.md`](./05-adjustments-Phases-17-20.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** API responses must return code-form values only.
- **No workarounds.** Use standard Django, DRF, and django-tenants patterns.
- **Tests are mandatory** for every task that introduces logic, migrations, or API behavior.
- **Each task branch lifecycle:** create from parent -> implement -> commit -> pre-merge checks -> push -> merge into parent.
- **Progress markers:** ❌ not done · ✅ done. Update in place as work completes.

## Pre-Merge Checks

Run checks in this order, one at a time:

```bash
ruff check backend/
mypy backend/
pytest tests/<specific_test_file>.py
pytest
```

All checks must pass before merging.

## Task Completion Commands

Use these commands after each task commit, replacing `<task-branch>` and `<parent-branch>` with the branch names listed below:

```bash
git push origin <task-branch>
git checkout <parent-branch>
git merge <task-branch>
git push origin <parent-branch>
```

---

## Branch Hierarchy

```text
develop
└── feature/backend-mvp
    ├── feature/backend-mvp-Phase17-multi-table-assignments
    │   ├── task/backend-mvp-Task17.1-booking-table-assignments
    │   ├── task/backend-mvp-Task17.2-walkin-table-assignments
    │   └── task/backend-mvp-Task17.3-assignment-services-serializers
    ├── feature/backend-mvp-Phase18-rest-api-normalization
    │   ├── task/backend-mvp-Task18.1-booking-patch-behavior
    │   ├── task/backend-mvp-Task18.2-booking-decisions-endpoint
    │   ├── task/backend-mvp-Task18.3-booking-tables-endpoint
    │   ├── task/backend-mvp-Task18.4-walkin-tables-endpoint
    │   ├── task/backend-mvp-Task18.5-public-booking-patch-delete
    │   └── task/backend-mvp-Task18.6-payment-refunds-endpoint
    ├── feature/backend-mvp-Phase19-restaurant-config-api
    │   ├── task/backend-mvp-Task19.1-restaurant-settings-endpoint
    │   ├── task/backend-mvp-Task19.2-opening-windows-endpoint
    │   ├── task/backend-mvp-Task19.3-closed-days-endpoint
    │   └── task/backend-mvp-Task19.4-rooms-tables-endpoints
    └── feature/backend-mvp-Phase20-api-compatibility-cleanup
        ├── task/backend-mvp-Task20.1-deprecation-tests-docs
        ├── task/backend-mvp-Task20.2-contract-verification
        └── task/backend-mvp-Task20.3-remove-action-endpoints
```

---

## ✅ Phase 17 — Multi-Table Assignments

Adds multi-table assignment support for bookings and walk-ins before API route normalization.

**Branch:** `feature/backend-mvp-Phase17-multi-table-assignments` — created from `feature/backend-mvp` after Phase 16 is merged.

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase17-multi-table-assignments
git push -u origin feature/backend-mvp-Phase17-multi-table-assignments
```

### ✅ Task 17.1 — Booking Table Assignments

**Branch:** `task/backend-mvp-Task17.1-booking-table-assignments`

```bash
git checkout feature/backend-mvp-Phase17-multi-table-assignments
git pull origin feature/backend-mvp-Phase17-multi-table-assignments
git checkout -b task/backend-mvp-Task17.1-booking-table-assignments
```

**Commit:**

```bash
git commit -m "[TASK] 17.1 add booking table assignments"
```

**Push & merge:**

```bash
git push origin task/backend-mvp-Task17.1-booking-table-assignments
git checkout feature/backend-mvp-Phase17-multi-table-assignments
git merge task/backend-mvp-Task17.1-booking-table-assignments
git push origin feature/backend-mvp-Phase17-multi-table-assignments
```

### ✅ Task 17.2 — Walk-in Table Assignments

**Branch:** `task/backend-mvp-Task17.2-walkin-table-assignments`

```bash
git checkout feature/backend-mvp-Phase17-multi-table-assignments
git pull origin feature/backend-mvp-Phase17-multi-table-assignments
git checkout -b task/backend-mvp-Task17.2-walkin-table-assignments
```

**Commit:**

```bash
git commit -m "[TASK] 17.2 add walk-in table assignments"
```

**Push & merge:**

```bash
git push origin task/backend-mvp-Task17.2-walkin-table-assignments
git checkout feature/backend-mvp-Phase17-multi-table-assignments
git merge task/backend-mvp-Task17.2-walkin-table-assignments
git push origin feature/backend-mvp-Phase17-multi-table-assignments
```

### ✅ Task 17.3 — Assignment Services And Serializers

**Branch:** `task/backend-mvp-Task17.3-assignment-services-serializers`

```bash
git checkout feature/backend-mvp-Phase17-multi-table-assignments
git pull origin feature/backend-mvp-Phase17-multi-table-assignments
git checkout -b task/backend-mvp-Task17.3-assignment-services-serializers
```

**Commit:**

```bash
git commit -m "[TASK] 17.3 add table assignment services and serializers"
```

**Push & merge:**

```bash
git push origin task/backend-mvp-Task17.3-assignment-services-serializers
git checkout feature/backend-mvp-Phase17-multi-table-assignments
git merge task/backend-mvp-Task17.3-assignment-services-serializers
git push origin feature/backend-mvp-Phase17-multi-table-assignments
```

---

## ❌ Phase 18 — REST API Normalization

Replaces action-style URLs with resource-oriented endpoints.

**Branch:** `feature/backend-mvp-Phase18-rest-api-normalization` — created from `feature/backend-mvp` after Phase 17 is merged.

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase18-rest-api-normalization
git push -u origin feature/backend-mvp-Phase18-rest-api-normalization
```

### ❌ Task 18.1 — Booking PATCH Behavior

**Branch:** `task/backend-mvp-Task18.1-booking-patch-behavior`

```bash
git checkout feature/backend-mvp-Phase18-rest-api-normalization
git pull origin feature/backend-mvp-Phase18-rest-api-normalization
git checkout -b task/backend-mvp-Task18.1-booking-patch-behavior
```

**Commit:**

```bash
git commit -m "[TASK] 18.1 normalize booking PATCH behavior"
```

### ❌ Task 18.2 — Booking Decisions Endpoint

**Branch:** `task/backend-mvp-Task18.2-booking-decisions-endpoint`

```bash
git checkout feature/backend-mvp-Phase18-rest-api-normalization
git pull origin feature/backend-mvp-Phase18-rest-api-normalization
git checkout -b task/backend-mvp-Task18.2-booking-decisions-endpoint
```

**Commit:**

```bash
git commit -m "[TASK] 18.2 add booking decisions endpoint"
```

### ❌ Task 18.3 — Booking Tables Endpoint

**Branch:** `task/backend-mvp-Task18.3-booking-tables-endpoint`

```bash
git checkout feature/backend-mvp-Phase18-rest-api-normalization
git pull origin feature/backend-mvp-Phase18-rest-api-normalization
git checkout -b task/backend-mvp-Task18.3-booking-tables-endpoint
```

**Commit:**

```bash
git commit -m "[TASK] 18.3 add booking tables endpoint"
```

### ❌ Task 18.4 — Walk-in Tables Endpoint

**Branch:** `task/backend-mvp-Task18.4-walkin-tables-endpoint`

```bash
git checkout feature/backend-mvp-Phase18-rest-api-normalization
git pull origin feature/backend-mvp-Phase18-rest-api-normalization
git checkout -b task/backend-mvp-Task18.4-walkin-tables-endpoint
```

**Commit:**

```bash
git commit -m "[TASK] 18.4 add walk-in tables endpoint"
```

### ❌ Task 18.5 — Public Booking PATCH/DELETE

**Branch:** `task/backend-mvp-Task18.5-public-booking-patch-delete`

```bash
git checkout feature/backend-mvp-Phase18-rest-api-normalization
git pull origin feature/backend-mvp-Phase18-rest-api-normalization
git checkout -b task/backend-mvp-Task18.5-public-booking-patch-delete
```

**Commit:**

```bash
git commit -m "[TASK] 18.5 normalize public booking token endpoint"
```

### ❌ Task 18.6 — Payment Refunds Endpoint

**Branch:** `task/backend-mvp-Task18.6-payment-refunds-endpoint`

```bash
git checkout feature/backend-mvp-Phase18-rest-api-normalization
git pull origin feature/backend-mvp-Phase18-rest-api-normalization
git checkout -b task/backend-mvp-Task18.6-payment-refunds-endpoint
```

**Commit:**

```bash
git commit -m "[TASK] 18.6 rename payment refund endpoint"
```

---

## ❌ Phase 19 — Restaurant Config API

Exposes restaurant settings, schedule, closed days, rooms, and tables as tenant resources.

**Branch:** `feature/backend-mvp-Phase19-restaurant-config-api` — created from `feature/backend-mvp` after Phase 18 is merged.

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase19-restaurant-config-api
git push -u origin feature/backend-mvp-Phase19-restaurant-config-api
```

### ❌ Task 19.1 — Restaurant Settings Endpoint

**Branch:** `task/backend-mvp-Task19.1-restaurant-settings-endpoint`

```bash
git checkout feature/backend-mvp-Phase19-restaurant-config-api
git pull origin feature/backend-mvp-Phase19-restaurant-config-api
git checkout -b task/backend-mvp-Task19.1-restaurant-settings-endpoint
```

**Commit:**

```bash
git commit -m "[TASK] 19.1 add restaurant settings endpoint"
```

### ❌ Task 19.2 — Opening Windows Endpoint

**Branch:** `task/backend-mvp-Task19.2-opening-windows-endpoint`

```bash
git checkout feature/backend-mvp-Phase19-restaurant-config-api
git pull origin feature/backend-mvp-Phase19-restaurant-config-api
git checkout -b task/backend-mvp-Task19.2-opening-windows-endpoint
```

**Commit:**

```bash
git commit -m "[TASK] 19.2 add opening windows endpoint"
```

### ❌ Task 19.3 — Closed Days Endpoint

**Branch:** `task/backend-mvp-Task19.3-closed-days-endpoint`

```bash
git checkout feature/backend-mvp-Phase19-restaurant-config-api
git pull origin feature/backend-mvp-Phase19-restaurant-config-api
git checkout -b task/backend-mvp-Task19.3-closed-days-endpoint
```

**Commit:**

```bash
git commit -m "[TASK] 19.3 add closed days endpoint"
```

### ❌ Task 19.4 — Rooms And Tables Endpoints

**Branch:** `task/backend-mvp-Task19.4-rooms-tables-endpoints`

```bash
git checkout feature/backend-mvp-Phase19-restaurant-config-api
git pull origin feature/backend-mvp-Phase19-restaurant-config-api
git checkout -b task/backend-mvp-Task19.4-rooms-tables-endpoints
```

**Commit:**

```bash
git commit -m "[TASK] 19.4 add rooms and tables endpoints"
```

---

## ❌ Phase 20 — API Compatibility Cleanup

Deprecates and removes old action endpoints after normalized endpoint usage is verified.

**Branch:** `feature/backend-mvp-Phase20-api-compatibility-cleanup` — created from `feature/backend-mvp` after Phase 19 is merged.

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase20-api-compatibility-cleanup
git push -u origin feature/backend-mvp-Phase20-api-compatibility-cleanup
```

### ❌ Task 20.1 — Deprecation Tests And Docs

**Branch:** `task/backend-mvp-Task20.1-deprecation-tests-docs`

```bash
git checkout feature/backend-mvp-Phase20-api-compatibility-cleanup
git pull origin feature/backend-mvp-Phase20-api-compatibility-cleanup
git checkout -b task/backend-mvp-Task20.1-deprecation-tests-docs
```

**Commit:**

```bash
git commit -m "[TASK] 20.1 document deprecated action endpoints"
```

### ❌ Task 20.2 — Contract Verification

**Branch:** `task/backend-mvp-Task20.2-contract-verification`

```bash
git checkout feature/backend-mvp-Phase20-api-compatibility-cleanup
git pull origin feature/backend-mvp-Phase20-api-compatibility-cleanup
git checkout -b task/backend-mvp-Task20.2-contract-verification
```

**Commit:**

```bash
git commit -m "[TEST] 20.2 verify normalized API contract"
```

### ❌ Task 20.3 — Remove Action Endpoints

**Branch:** `task/backend-mvp-Task20.3-remove-action-endpoints`

```bash
git checkout feature/backend-mvp-Phase20-api-compatibility-cleanup
git pull origin feature/backend-mvp-Phase20-api-compatibility-cleanup
git checkout -b task/backend-mvp-Task20.3-remove-action-endpoints
```

**Commit:**

```bash
git commit -m "[TASK] 20.3 remove legacy action endpoints"
```
