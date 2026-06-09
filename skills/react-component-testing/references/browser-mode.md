# Vitest browser mode — the documented alternative (NOT the default)

> Load only when real-browser fidelity is required for a component test. The **default** for component tests in this skill is jsdom + vitest-axe (see SKILL.md). This file documents the alternative and its trade-offs so the choice is explicit. Verified-at-forge: `vitest` 3.x + `@vitest/browser`. Re-confirm browser-mode stability/status against vitest.dev (see `sources.md`).

## What it is

Vitest **browser mode** runs the component tests in a real browser instead of a simulated DOM (jsdom). Instead of jsdom's JS implementation of the DOM, the tests execute against an actual browser engine driven by a provider — typically **Playwright** (`@vitest/browser` + the `playwright` provider, which can run Chromium/Firefox/WebKit). RTL queries and `user-event` still apply, but events and layout are real.

```ts
// vitest.config.ts (browser-mode project — separate from the jsdom default)
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    browser: {
      enabled: true,
      provider: 'playwright',
      instances: [{ browser: 'chromium' }],
    },
  },
})
```

## When it earns its cost

- The component relies on **real layout / computed styles / true visibility** that jsdom does not implement (jsdom has no layout engine — `getBoundingClientRect` returns zeros, no real scrolling/intersection).
- You need **real-browser fidelity** for focus management, pointer/scroll behavior, CSS-driven states, or canvas/WebGL.
- You want a11y assertions against the *rendered* browser tree via **`@axe-core/playwright`** rather than vitest-axe.

## The trade-offs (why it is the alternative, not the default)

- **Slower + heavier CI.** A real browser per worker is far more expensive than jsdom — more memory, more startup, slower runs. The component-test layer is meant to be fast and run on every change; jsdom keeps it cheap.
- **a11y shifts off vitest-axe.** In a browser you'd assert a11y with `@axe-core/playwright` (inject + analyze in the page) instead of vitest-axe's `toHaveNoViolations`. That moves the a11y mechanism into Playwright's surface.
- **Overlaps the e2e skill.** Once you're driving a real browser with Playwright, you're on the same machinery as `playwright-best-practices` (the e2e sibling). Keep the boundary clear: component tests = jsdom + vitest-axe (fast, isolated, network mocked with MSW); e2e = full-app Playwright. Don't let browser-mode component tests quietly become a second, slower e2e suite.
- **MSW still applies** but via the browser interception path (the service-worker / `setupWorker` flavor) rather than `setupServer`, adding setup surface.

## Recommendation

Default to **jsdom + vitest-axe** for component tests (the SKILL.md path). Reach for browser mode only for the specific components whose correctness genuinely depends on a real browser (layout/visibility/focus), and keep those in a **separate Vitest project** so the fast jsdom suite still runs on every change. For full user-journey a11y and cross-browser coverage, prefer the dedicated e2e skill (`playwright-best-practices` + `@axe-core/playwright`) over expanding browser-mode component tests.

*(Vitest browser mode has been maturing across the v2→v3 line; confirm its current stability label and the exact `browser.instances` config shape against the current vitest.dev docs before adopting — see `sources.md`.)*
