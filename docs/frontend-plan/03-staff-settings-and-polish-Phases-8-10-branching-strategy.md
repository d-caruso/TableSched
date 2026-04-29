# Branching Strategy — Phases 8–10: Staff Settings, Floor Plan & Polish

References:
- Implementation plan: [`03-staff-settings-and-polish-Phases-8-10.md`](./03-staff-settings-and-polish-Phases-8-10.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text via i18n keys. Day names, policy labels, and status text must all use `t('...')`.
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
└── feature/frontend-mvp
    ├── feature/frontend-mvp-Phase8-staff-settings    ← created from feature/frontend-mvp AFTER Phase 7 merged
    │   ├── task/frontend-mvp-Task8.1-settings-screen
    │   ├── task/frontend-mvp-Task8.2-opening-hours
    │   └── task/frontend-mvp-Task8.3-deposit-policy
    ├── feature/frontend-mvp-Phase9-floor-plan        ← created from feature/frontend-mvp AFTER Phase 8 merged
    │   ├── task/frontend-mvp-Task9.1-floor-screen
    │   └── task/frontend-mvp-Task9.2-drag-and-drop
    └── feature/frontend-mvp-Phase10-polish           ← created from feature/frontend-mvp AFTER Phase 9 merged
        ├── task/frontend-mvp-Task10.1-i18n-completion
        ├── task/frontend-mvp-Task10.2-responsive-layout
        ├── task/frontend-mvp-Task10.3-vercel-config
        └── task/frontend-mvp-Task10.4-documentation
```

---

## ❌ Phase 8 — Staff Restaurant Settings

Opening hours (weekly schedule) and deposit policy (never / always / by party size). Changes are persisted via `PATCH /api/restaurant/`. No automatic table assignment or advanced configuration in MVP (business doc §6, §4, technical doc §11).

**⚠️ Create this branch only after Phase 7 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase8-staff-settings` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase8-staff-settings
git push -u origin feature/frontend-mvp-Phase8-staff-settings
```

---

### ✅ Task 8.1 — Settings Screen

Implement `app/(staff)/dashboard/settings/index.tsx`. Fetches current restaurant settings, diffs local `draft` state, and sends `PATCH` on save. Save button is disabled when `draft` is empty (nothing changed).

**Branch:** `task/frontend-mvp-Task8.1-settings-screen` — created from `feature/frontend-mvp-Phase8-staff-settings`

```bash
git checkout feature/frontend-mvp-Phase8-staff-settings
git pull origin feature/frontend-mvp-Phase8-staff-settings
git checkout -b task/frontend-mvp-Task8.1-settings-screen
```

**Files to create:**
- `app/(staff)/dashboard/settings/index.tsx` — fetches settings, holds `draft` state, delegates editors to child components, submits on save

**Tests:**

```tsx
// __tests__/staff/SettingsScreen.test.tsx
import { render, screen, waitFor } from '@testing-library/react-native';
import SettingsScreen from '@/app/(staff)/dashboard/settings/index';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: {
    getRestaurantSettings: jest.fn(async () => ({
      slug: 'r', name: 'Test', opening_hours: [], deposit_policy: { mode: 'never' }, cancellation_cutoff_hours: 24,
    })),
    updateRestaurantSettings: jest.fn(async () => ({})),
  },
}));
jest.mock('@/lib/auth/AuthContext', () => ({ useAuth: () => ({ accessToken: 'tok', tenant: 'r' }) }));

test('renders settings title', async () => {
  render(<SettingsScreen />);
  await waitFor(() => expect(screen.getByText('Settings')).toBeTruthy());
});

test('save button is disabled when no changes made', async () => {
  render(<SettingsScreen />);
  await waitFor(() => {
    const saveBtn = screen.getByText('Save');
    expect(saveBtn).toBeDisabled();
  });
});
```

**Commit:**
```bash
git add app/(staff)/dashboard/settings/index.tsx
git commit -m "[TASK] 8.1 add staff restaurant settings screen"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/staff/SettingsScreen.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task8.1-settings-screen
git checkout feature/frontend-mvp-Phase8-staff-settings
git merge task/frontend-mvp-Task8.1-settings-screen
git push origin feature/frontend-mvp-Phase8-staff-settings
```

---

### ✅ Task 8.2 — Opening Hours Editor

Implement `OpeningHoursEditor`. Each day can be toggled open/closed and given an open/close time. Closed days are omitted from the `opening_hours` array — not sent as `null`. No user-facing strings in component markup — day labels use i18n keys.

**Branch:** `task/frontend-mvp-Task8.2-opening-hours` — created from `feature/frontend-mvp-Phase8-staff-settings`

```bash
git checkout feature/frontend-mvp-Phase8-staff-settings
git pull origin feature/frontend-mvp-Phase8-staff-settings
git checkout -b task/frontend-mvp-Task8.2-opening-hours
```

**Files to create:**
- `components/settings/OpeningHoursEditor.tsx` — seven-day toggle list; toggling a day off removes it from the array; toggling on adds a default `09:00–22:00` entry

**Tests:**

```tsx
// __tests__/settings/OpeningHoursEditor.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { OpeningHoursEditor } from '@/components/settings/OpeningHoursEditor';

test('toggling a closed day adds a default entry', () => {
  const onChange = jest.fn();
  render(<OpeningHoursEditor hours={[]} onChange={onChange} />);
  // Toggle Monday (day index 1) on
  fireEvent(screen.getAllByRole('switch')[1], 'valueChange', true);
  expect(onChange).toHaveBeenCalledWith(
    expect.arrayContaining([expect.objectContaining({ day: 1, open: '09:00', close: '22:00' })])
  );
});

test('toggling an open day removes its entry', () => {
  const onChange = jest.fn();
  const hours = [{ day: 1 as const, open: '09:00', close: '22:00' }];
  render(<OpeningHoursEditor hours={hours} onChange={onChange} />);
  fireEvent(screen.getAllByRole('switch')[1], 'valueChange', false);
  expect(onChange).toHaveBeenCalledWith([]);
});

test('updating close time patches the correct day', () => {
  const onChange = jest.fn();
  const hours = [{ day: 1 as const, open: '09:00', close: '22:00' }];
  render(<OpeningHoursEditor hours={hours} onChange={onChange} />);
  // Find the close time input for day 1 and change it
  const inputs = screen.getAllByDisplayValue('22:00');
  fireEvent.changeText(inputs[0], '23:00');
  expect(onChange).toHaveBeenCalledWith([{ day: 1, open: '09:00', close: '23:00' }]);
});
```

**Commit:**
```bash
git add components/settings/OpeningHoursEditor.tsx
git commit -m "[TASK] 8.2 add opening hours editor"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/settings/OpeningHoursEditor.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task8.2-opening-hours
git checkout feature/frontend-mvp-Phase8-staff-settings
git merge task/frontend-mvp-Task8.2-opening-hours
git push origin feature/frontend-mvp-Phase8-staff-settings
```

---

### ✅ Task 8.3 — Deposit Policy Editor

Implement `DepositPolicyEditor`. Three modes: `never`, `always`, `by_party_size`. When `by_party_size` is selected a numeric input appears for `min_party_size`. All labels via i18n keys (business doc §4).

**Branch:** `task/frontend-mvp-Task8.3-deposit-policy` — created from `feature/frontend-mvp-Phase8-staff-settings`

```bash
git checkout feature/frontend-mvp-Phase8-staff-settings
git pull origin feature/frontend-mvp-Phase8-staff-settings
git checkout -b task/frontend-mvp-Task8.3-deposit-policy
```

**Files to create:**
- `components/settings/DepositPolicyEditor.tsx` — mode buttons (`never`, `always`, `by_party_size`); `min_party_size` input shown only when `by_party_size` selected

**Tests:**

```tsx
// __tests__/settings/DepositPolicyEditor.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { DepositPolicyEditor } from '@/components/settings/DepositPolicyEditor';

test('selecting always calls onChange with mode always', () => {
  const onChange = jest.fn();
  render(<DepositPolicyEditor policy={{ mode: 'never' }} onChange={onChange} />);
  fireEvent.press(screen.getByText('Always'));
  expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ mode: 'always' }));
});

test('min_party_size input is hidden when mode is never', () => {
  render(<DepositPolicyEditor policy={{ mode: 'never' }} onChange={jest.fn()} />);
  expect(screen.queryByText('Min party size')).toBeNull();
});

test('min_party_size input is visible when mode is by_party_size', () => {
  render(<DepositPolicyEditor policy={{ mode: 'by_party_size', min_party_size: 4 }} onChange={jest.fn()} />);
  expect(screen.getByText('Min party size')).toBeTruthy();
});
```

**Commit:**
```bash
git add components/settings/DepositPolicyEditor.tsx
git commit -m "[TASK] 8.3 add deposit policy editor"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/settings/DepositPolicyEditor.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task8.3-deposit-policy
git checkout feature/frontend-mvp-Phase8-staff-settings
git merge task/frontend-mvp-Task8.3-deposit-policy
git push origin feature/frontend-mvp-Phase8-staff-settings
```

---

### ❌ Phase 8 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase8-staff-settings
git push origin feature/frontend-mvp
```

---

## ❌ Phase 9 — Floor Plan Editor

Staff can visually position tables within a room by dragging them. Coordinates are saved to the backend via `PATCH /api/tables/{id}/position/`. Table combinations are out of scope for MVP (business doc §7, technical doc §11).

**⚠️ Create this branch only after Phase 8 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase9-floor-plan` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase9-floor-plan
git push -u origin feature/frontend-mvp-Phase9-floor-plan
```

---

### ❌ Task 9.1 — Floor Screen & Room Tabs

Implement `app/(staff)/dashboard/settings/floor.tsx` and `RoomTabs`. Fetches rooms via `staffApi.listRooms`. If there is only one room, `RoomTabs` is not rendered. The first room is selected by default.

**Branch:** `task/frontend-mvp-Task9.1-floor-screen` — created from `feature/frontend-mvp-Phase9-floor-plan`

```bash
git checkout feature/frontend-mvp-Phase9-floor-plan
git pull origin feature/frontend-mvp-Phase9-floor-plan
git checkout -b task/frontend-mvp-Task9.1-floor-screen
```

**Files to create:**
- `app/(staff)/dashboard/settings/floor.tsx` — fetches rooms, manages `activeRoomId` state, renders `RoomTabs` (if >1 room) and `FloorCanvas` (stub)
- `components/floor/RoomTabs.tsx` — horizontal tab bar, one tab per room

**Tests:**

```tsx
// __tests__/floor/RoomTabs.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { RoomTabs } from '@/components/floor/RoomTabs';

const rooms = [
  { id: 'r1', name: 'Main', tables: [] },
  { id: 'r2', name: 'Terrace', tables: [] },
];

test('renders a tab per room', () => {
  render(<RoomTabs rooms={rooms} activeId="r1" onSelect={jest.fn()} />);
  expect(screen.getByText('Main')).toBeTruthy();
  expect(screen.getByText('Terrace')).toBeTruthy();
});

test('calls onSelect with correct room id', () => {
  const onSelect = jest.fn();
  render(<RoomTabs rooms={rooms} activeId="r1" onSelect={onSelect} />);
  fireEvent.press(screen.getByText('Terrace'));
  expect(onSelect).toHaveBeenCalledWith('r2');
});
```

**Commit:**
```bash
git add app/(staff)/dashboard/settings/floor.tsx components/floor/RoomTabs.tsx
git commit -m "[TASK] 9.1 add floor plan screen and room tabs"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/floor/RoomTabs.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task9.1-floor-screen
git checkout feature/frontend-mvp-Phase9-floor-plan
git merge task/frontend-mvp-Task9.1-floor-screen
git push origin feature/frontend-mvp-Phase9-floor-plan
```

---

### ❌ Task 9.2 — Canvas & Drag-and-Drop Tables

Implement `FloorCanvas` and `DraggableTable`. Uses `react-native-gesture-handler` + `react-native-reanimated` for drag. On drag end, calls `staffApi.updateTablePosition(tenant, token, tableId, x, y)`. Coordinates are absolute pixel offsets within the canvas view.

**Branch:** `task/frontend-mvp-Task9.2-drag-and-drop` — created from `feature/frontend-mvp-Phase9-floor-plan`

```bash
git checkout feature/frontend-mvp-Phase9-floor-plan
git pull origin feature/frontend-mvp-Phase9-floor-plan
git checkout -b task/frontend-mvp-Task9.2-drag-and-drop
```

**Files to create:**
- `components/floor/FloorCanvas.tsx` — `GestureHandlerRootView` wrapper; renders one `DraggableTable` per table in the room; `onDrop` calls `updateTablePosition` mutation
- `components/floor/DraggableTable.tsx` — `Gesture.Pan()` with `useSharedValue` for x/y; `runOnJS(onDrop)` on gesture end; table name + capacity displayed inside

**Tests:**

```tsx
// __tests__/floor/DraggableTable.test.tsx
import { render, screen } from '@testing-library/react-native';
import { DraggableTable } from '@/components/floor/DraggableTable';

const table = { id: 't1', name: 'T1', capacity: 4, x: 100, y: 50 };

test('displays table name and capacity', () => {
  render(<DraggableTable table={table} onDrop={jest.fn()} />);
  expect(screen.getByText('T1')).toBeTruthy();
  expect(screen.getByText('4p')).toBeTruthy();
});

// __tests__/floor/FloorCanvas.test.tsx
import { render, screen } from '@testing-library/react-native';
import { FloorCanvas } from '@/components/floor/FloorCanvas';

jest.mock('@/lib/api/endpoints', () => ({
  staffApi: { updateTablePosition: jest.fn(async () => {}) },
}));

const room = { id: 'r1', name: 'Main', tables: [{ id: 't1', name: 'T1', capacity: 2, x: 0, y: 0 }] };

test('renders a table for each room table', () => {
  render(<FloorCanvas room={room} tenant="r" token="tok" />);
  expect(screen.getByText('T1')).toBeTruthy();
});
```

**Commit:**
```bash
git add components/floor/FloorCanvas.tsx components/floor/DraggableTable.tsx
git commit -m "[TASK] 9.2 add visual floor canvas with drag-and-drop table positioning"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/floor/DraggableTable.test.tsx __tests__/floor/FloorCanvas.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task9.2-drag-and-drop
git checkout feature/frontend-mvp-Phase9-floor-plan
git merge task/frontend-mvp-Task9.2-drag-and-drop
git push origin feature/frontend-mvp-Phase9-floor-plan
```

---

### ❌ Phase 9 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase9-floor-plan
git push origin feature/frontend-mvp
```

---

## ❌ Phase 10 — i18n Completion & Polish

Complete all translation files, add responsive layout for wide screens, configure Vercel deployment, and update documentation. This phase must not introduce any new features — polish only.

**⚠️ Create this branch only after Phase 9 is merged into `feature/frontend-mvp`.**

**Branch:** `feature/frontend-mvp-Phase10-polish` — created from `feature/frontend-mvp`

```bash
git checkout feature/frontend-mvp
git pull origin feature/frontend-mvp
git checkout -b feature/frontend-mvp-Phase10-polish
git push -u origin feature/frontend-mvp-Phase10-polish
```

---

### ❌ Task 10.1 — i18n Completion & Validation Script

Ensure `it.json` and `de.json` are complete translations of `en.json`. Add `scripts/validate-i18n.ts` that exits with code 1 if any key present in `en.json` is missing from the other locales. Add it to `package.json` scripts.

**Branch:** `task/frontend-mvp-Task10.1-i18n-completion` — created from `feature/frontend-mvp-Phase10-polish`

```bash
git checkout feature/frontend-mvp-Phase10-polish
git pull origin feature/frontend-mvp-Phase10-polish
git checkout -b task/frontend-mvp-Task10.1-i18n-completion
```

**Files to create/update:**
- `lib/i18n/locales/it.json` — complete Italian translation (all keys from `en.json`)
- `lib/i18n/locales/de.json` — complete German translation (all keys from `en.json`)
- `scripts/validate-i18n.ts` — flat-key diff; exits 1 on missing keys

**`scripts/validate-i18n.ts`:**

```ts
import en from '../lib/i18n/locales/en.json';
import it from '../lib/i18n/locales/it.json';
import de from '../lib/i18n/locales/de.json';

function flatKeys(obj: object, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) => {
    const full = prefix ? `${prefix}.${k}` : k;
    return typeof v === 'object' && v !== null ? flatKeys(v, full) : [full];
  });
}

const enKeys = flatKeys(en);
const missing = {
  it: enKeys.filter(k => !flatKeys(it).includes(k)),
  de: enKeys.filter(k => !flatKeys(de).includes(k)),
};

if (missing.it.length || missing.de.length) {
  console.error('Missing i18n keys:', missing);
  process.exit(1);
}
console.log('OK — all keys present in it and de.');
```

Add to `package.json`:

```json
{ "scripts": { "validate-i18n": "ts-node scripts/validate-i18n.ts" } }
```

**Tests:**

```ts
// __tests__/i18n/validate.test.ts
import en from '@/lib/i18n/locales/en.json';
import it from '@/lib/i18n/locales/it.json';
import de from '@/lib/i18n/locales/de.json';

function flatKeys(obj: object, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) => {
    const full = prefix ? `${prefix}.${k}` : k;
    return typeof v === 'object' && v !== null ? flatKeys(v, full) : [full];
  });
}

test('it.json has all en.json keys', () => {
  const enKeys = flatKeys(en);
  const itKeys = flatKeys(it);
  enKeys.forEach(k => expect(itKeys).toContain(k));
});

test('de.json has all en.json keys', () => {
  const enKeys = flatKeys(en);
  const deKeys = flatKeys(de);
  enKeys.forEach(k => expect(deKeys).toContain(k));
});

test('no locale contains empty string values', () => {
  [it, de].forEach(locale => {
    flatKeys(locale).forEach(k => {
      const val = k.split('.').reduce((o: any, p) => o?.[p], locale);
      expect(typeof val === 'string' && val.trim().length).toBeGreaterThan(0);
    });
  });
});
```

**Commit:**
```bash
git add lib/i18n/locales/ scripts/validate-i18n.ts package.json
git commit -m "[TASK] 10.1 complete it/de translations and add i18n validation script"
```

**Pre-merge checks:**
```bash
npm run validate-i18n
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/i18n/validate.test.ts
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task10.1-i18n-completion
git checkout feature/frontend-mvp-Phase10-polish
git merge task/frontend-mvp-Task10.1-i18n-completion
git push origin feature/frontend-mvp-Phase10-polish
```

---

### ❌ Task 10.2 — Responsive Layout

Implement `ResponsiveShell` using Tamagui's `useMedia`. On screens wider than `md` breakpoint the staff dashboard displays a sidebar; below it stacks vertically. The public booking page is already single-column and needs no changes.

**Branch:** `task/frontend-mvp-Task10.2-responsive-layout` — created from `feature/frontend-mvp-Phase10-polish`

```bash
git checkout feature/frontend-mvp-Phase10-polish
git pull origin feature/frontend-mvp-Phase10-polish
git checkout -b task/frontend-mvp-Task10.2-responsive-layout
```

**Files to create:**
- `components/ui/ResponsiveShell.tsx` — `useMedia().gtMd` switches between `XStack` (sidebar + content) and `YStack` (single column)

**Tests:**

```tsx
// __tests__/ui/ResponsiveShell.test.tsx
jest.mock('tamagui', () => ({
  ...jest.requireActual('tamagui'),
  useMedia: jest.fn(),
}));

import { render, screen } from '@testing-library/react-native';
import { useMedia } from 'tamagui';
import { ResponsiveShell } from '@/components/ui/ResponsiveShell';

test('renders sidebar on wide screens', () => {
  (useMedia as jest.Mock).mockReturnValue({ gtMd: true });
  render(<ResponsiveShell sidebar={<></>} content={<></>} />);
  // Sidebar container present
  expect(screen.getByTestId('sidebar-container')).toBeTruthy();
});

test('hides sidebar on narrow screens', () => {
  (useMedia as jest.Mock).mockReturnValue({ gtMd: false });
  render(<ResponsiveShell sidebar={<></>} content={<></>} />);
  expect(screen.queryByTestId('sidebar-container')).toBeNull();
});
```

**Commit:**
```bash
git add components/ui/ResponsiveShell.tsx
git commit -m "[TASK] 10.2 add responsive shell for staff dashboard"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
npm test -- __tests__/ui/ResponsiveShell.test.tsx
npm test
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task10.2-responsive-layout
git checkout feature/frontend-mvp-Phase10-polish
git merge task/frontend-mvp-Task10.2-responsive-layout
git push origin feature/frontend-mvp-Phase10-polish
```

---

### ❌ Task 10.3 — Vercel Deployment Config

Add `vercel.json` at the repo root. All env vars are referenced via Vercel secret names — no values committed to the repo.

**Branch:** `task/frontend-mvp-Task10.3-vercel-config` — created from `feature/frontend-mvp-Phase10-polish`

```bash
git checkout feature/frontend-mvp-Phase10-polish
git pull origin feature/frontend-mvp-Phase10-polish
git checkout -b task/frontend-mvp-Task10.3-vercel-config
```

**`vercel.json`:**

```json
{
  "buildCommand": "cd frontend && npx expo export -p web",
  "outputDirectory": "frontend/dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "env": {
    "EXPO_PUBLIC_API_BASE_URL": "@tablesched_api_base_url",
    "EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY": "@tablesched_stripe_key"
  }
}
```

**Tests:** None — no logic introduced. Verify manually: `npx expo export -p web` produces `frontend/dist/`.

**Commit:**
```bash
git add vercel.json
git commit -m "[TASK] 10.3 add Vercel deployment configuration"
```

**Pre-merge checks:**
```bash
npm run build
npm run typecheck
npm run lint
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task10.3-vercel-config
git checkout feature/frontend-mvp-Phase10-polish
git merge task/frontend-mvp-Task10.3-vercel-config
git push origin feature/frontend-mvp-Phase10-polish
```

---

### ❌ Task 10.4 — Documentation Updates

Update all required docs per CLAUDE.md Documentation Update Policy. No code changes.

**Branch:** `task/frontend-mvp-Task10.4-documentation` — created from `feature/frontend-mvp-Phase10-polish`

```bash
git checkout feature/frontend-mvp-Phase10-polish
git pull origin feature/frontend-mvp-Phase10-polish
git checkout -b task/frontend-mvp-Task10.4-documentation
```

**Files to update (inside `docs/` submodule):**

- `docs/QUICK_START.md` — add frontend section: tech stack, `npm run web`, env vars required
- `docs/ARCHITECTURE_OVERVIEW.md` — add frontend architecture: Expo Router file tree, data flow (TanStack Query → API client → Django), auth model
- `docs/GAPS_AND_IMPROVEMENTS.md` — add known post-MVP frontend gaps: mobile app release, floor editor on mobile touch, viewer role UI
- `docs/CONTEXT.md` — add to "Recent Changes": frontend MVP complete (keep last 5 entries)

**Commit (docs submodule — run from inside `docs/`):**

```bash
cd docs
git checkout -b feature/frontend-mvp-docs
git add QUICK_START.md ARCHITECTURE_OVERVIEW.md GAPS_AND_IMPROVEMENTS.md CONTEXT.md
git commit -m "[DOCS] update docs for frontend MVP completion"
git push origin feature/frontend-mvp-docs
cd ..
git add docs
git commit -m "[SUBMODULE] update docs reference after frontend MVP docs"
```

**Tests:** None — documentation only.

**Pre-merge checks:**
```bash
npm run typecheck
npm run lint
```

**Push & merge:**
```bash
git push origin task/frontend-mvp-Task10.4-documentation
git checkout feature/frontend-mvp-Phase10-polish
git merge task/frontend-mvp-Task10.4-documentation
git push origin feature/frontend-mvp-Phase10-polish
```

---

### ❌ Phase 10 complete — merge into feature branch

```bash
git checkout feature/frontend-mvp
git merge feature/frontend-mvp-Phase10-polish
git push origin feature/frontend-mvp
```

---

## ❌ Frontend MVP complete — merge feature branch into develop

All phases complete. Run the full pre-merge checklist one final time before merging to `develop`.

```bash
cd frontend
npm run validate-i18n
npm run build
npm run typecheck
npm run lint
npm test
```

All checks must pass. Then — with explicit confirmation:

```bash
git checkout develop
git merge feature/frontend-mvp
git push origin develop
```
