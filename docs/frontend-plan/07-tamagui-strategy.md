# 07 — Tamagui Strategy

## Why This Document Exists

During development, Tamagui parse errors (`Unexpected token '{'`) surfaced repeatedly. The root cause and the correct long-term strategy were discussed and decided. This document records that decision so future development follows the same approach.

---

## Root Cause of the Parse Errors

Tamagui ships a **static compiler** (Babel/SWC plugin) that extracts styles at build time. It processes all JSX in the project — including React Native primitives (`View`, `Text`, etc.) that Tamagui does not own.

When those primitives use inline object literals (`style={{ flexDirection: 'row' }}`), the compiler's parser chokes on the inner `{` token:

```
Error in Tamagui parse, skipping
Unexpected token '{'
SyntaxError: Unexpected token '{'
```

The compiler was designed assuming Tamagui components are used exclusively. Mixing RN primitives with inline styles is the trigger.

---

## Why We Were Mixing Paradigms

No deliberate decision was made. React Native primitives are the default for any RN developer or AI code generation tool. Tamagui was added on top as a component library without a clear policy on which primitives to use. The two coexist at runtime without errors — the problem only appears at build time when the compiler runs.

---

## Options Considered

### Option A — Disable the static compiler
Remove `@tamagui/babel-plugin` from `babel.config.js`. No more parse errors.

Valid if not targeting web CSS extraction. But loses the main reason to use Tamagui's compiler.

### Option B — ESLint rule
Add `react-native/no-inline-styles: error`. Catches inline style objects at lint time before they reach the compiler.

Correct, but doesn't fix the mixing problem — just prevents one symptom.

### Option C — Go all-in on Tamagui components (chosen)
Replace RN primitives with Tamagui equivalents everywhere. Use Tamagui style props or design tokens instead of `style={{}}`. Keep the compiler on.

This is the intended usage and delivers the full benefit: build-time CSS extraction, design token resolution, and cross-platform consistency.

---

## Decision: Go All-In on Tamagui

**Rule:** Use Tamagui components and style props/tokens. Do not use RN primitives for UI layout or text unless there is a specific technical reason (see exceptions below).

### Style syntax

```tsx
// ❌ inline object — breaks the compiler
<View style={{ flexDirection: 'row', gap: 8 }} />

// ✅ Tamagui style prop with literal value
<XStack gap={8} />

// ✅ Tamagui style prop with design token
<XStack gap="$3" backgroundColor="$background" />
```

---

## RN → Tamagui Primitive Mapping

| RN primitive | Tamagui replacement | Notes |
|---|---|---|
| `View` | `Stack` / `XStack` / `YStack` | `XStack` = row, `YStack` = column, `Stack` = default |
| `Text` | `Text` (tamagui) | From `import { Text } from 'tamagui'` |
| `Switch` | `Switch` (tamagui) | From `import { Switch } from 'tamagui'` |
| `Pressable` | `Stack` + `onPress` + `pressStyle` | `Button` for common cases |
| `TextInput` | `Input` (tamagui) | Falls back to RN `TextInput` internally |
| `StyleSheet` | Tamagui style props | See exceptions below |

### Pressable example

```tsx
// ❌ RN Pressable
<Pressable onPress={handlePress}>
  <Text>Click me</Text>
</Pressable>

// ✅ Tamagui Stack
<Stack onPress={handlePress} pressStyle={{ opacity: 0.7 }}>
  <Text>Click me</Text>
</Stack>

// ✅ Tamagui Button (for standard button cases)
<Button onPress={handlePress}>Click me</Button>
```

---

## When RN Primitives Are Still Acceptable

| Use case | Why |
|---|---|
| `Pressable` in gesture-heavy UI | When combined with `react-native-gesture-handler` and precise hit slop / press state control is needed |
| `StyleSheet` + RN `View` inside `useAnimatedStyle` | Reanimated requires RN-compatible style objects on animated views |
| `GestureHandlerRootView` | react-native-gesture-handler primitive, no Tamagui equivalent |
| RN `TextInput` | Cursor position, text masking, IME quirks, or high-frequency controlled input where Tamagui's wrapper adds overhead |

In these cases, do **not** use inline `style={{}}` — extract to `StyleSheet.create`.

---

## Why Keep the Static Compiler

The static compiler exists to solve real problems, especially on web:

- Styles are extracted to real CSS at build time → smaller JS bundle, faster first paint
- No flash of unstyled content on SSR
- Design tokens (`$color`, `$space`, `$size`) are resolved at build time rather than runtime
- Component props like `backgroundColor="$red10"` become static CSS rules

These benefits only materialise when Tamagui components are used. Using RN primitives bypasses the compiler's intended input and causes it to fail.

---

## Enforcing the Decision

Add the ESLint rule as a safety net so drift is caught at lint time:

```js
// eslint.config.mjs / .eslintrc.js
rules: {
  'react-native/no-inline-styles': 'error',
}
```

This catches any `style={{ ... }}` that slips through, regardless of which component it appears on.
