# Runtime accessibility with vitest-axe

> Load when adding a11y assertions to a component test. Verified-at-forge: `vitest-axe` 0.1.x (wraps `axe-core`). Re-confirm the package version + axe-core version + the exact setup entry path against github.com/chaance/vitest-axe (see `sources.md`).

## What it is

`vitest-axe` runs axe-core against rendered DOM inside a Vitest test and exposes a `toHaveNoViolations()` matcher. It is the Vitest-native port of `jest-axe` (same author lineage), adapted to Vitest's `expect.extend`. It is the **runtime** complement to static jsx-a11y lint (the `biome` skill) — lint catches a11y problems in source, vitest-axe catches them in the actually-rendered tree (computed roles, generated ids, conditionally-rendered content).

## Setup — register the matcher

Two equivalent ways; pick one and put it in the Vitest `setupFiles` so the matcher is global:

```ts
// Option A (simplest) — side-effect import in setup-tests.ts
import 'vitest-axe/extend-expect'
```

```ts
// Option B — explicit, e.g. if you also augment types yourself
import { expect } from 'vitest'
import * as matchers from 'vitest-axe/matchers'
expect.extend(matchers)
```

If TypeScript doesn't recognize `toHaveNoViolations`, add the vitest-axe matcher types to your test tsconfig (the package ships an ambient declaration for the `extend-expect` path; the `matchers` path may need an explicit `expect` interface augmentation — confirm against the current README).

## Usage

```ts
import { axe } from 'vitest-axe'

const { container } = renderWithProviders(<SignupForm />)
const results = await axe(container)
expect(results).toHaveNoViolations()
```

- `axe(container)` is **async** — always `await` it.
- Pass the **`container`** returned by RTL's `render` (the mounted subtree), not `document.body`, to scope the scan to the component under test.
- Run it on the **state you ship**: assert after the data has loaded, after an error renders, after a dialog opens — not only the initial empty render. An accessible loading state and an inaccessible loaded state is still a bug.

## Configuring rules

`axe(container, options)` accepts axe-core's run options — disable a rule that doesn't apply to a component fragment, or restrict to a WCAG tag set:

```ts
const results = await axe(container, {
  rules: { region: { enabled: false } },           // a fragment isn't a full page
})
// or scope by tags:
const results2 = await axe(container, { runOnly: ['wcag2a', 'wcag2aa'] })
```

Prefer fixing the violation over disabling the rule; disable only when the rule genuinely doesn't apply to an isolated component (e.g. the `region`/`landmark` rules on a fragment that is mounted inside a page region in production).

## Requires a real DOM — use jsdom, not happy-dom

vitest-axe needs a DOM implementation (it traverses the rendered tree). Run it under **`environment: 'jsdom'`**. **Do NOT run it under happy-dom** — happy-dom has a documented `Node.prototype.isConnected` behavior that breaks axe-core's connected-node traversal, so the matcher does not work correctly there. If part of your suite uses happy-dom for speed on non-a11y tests, isolate the vitest-axe tests into a jsdom project/workspace. *(This caveat could not be re-verified against live docs at forge time — WebFetch was sandbox-denied — confirm it still holds against the current happy-dom/axe issue tracker; see `sources.md`.)*

## Honest scope — a subset of WCAG, not all of it

Automated axe-core checks detect only a **subset** of accessibility issues — commonly cited at roughly a third to a half of WCAG success criteria. It is excellent at the mechanical, deterministic checks (missing labels, color contrast, ARIA misuse, missing alt text, heading order) and cannot judge the things that need human judgment (is the alt text *meaningful*? is the focus order *logical*? does the flow work with a screen reader?). **`toHaveNoViolations()` passing is necessary, not sufficient** — vitest-axe complements, never replaces, manual keyboard + assistive-technology review. State this honestly; do not claim a green axe run means "accessible." *(The exact percentage figure varies by source and is not a single canonical number — present it as "a subset," not a hard stat, unless you cite a specific axe-core/Deque source.)*
