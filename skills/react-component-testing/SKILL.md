---
name: react-component-testing
description: >
  RTL + MSW + vitest-axe component-test layer for a Vite + React + TypeScript
  SPA under Vitest. Use when writing or setting up component tests that render a
  real component tree, drive it as a user does (React Testing Library +
  user-event), mock the NETWORK boundary (Mock Service Worker v2 — not the
  module), and assert the rendered output is accessible (vitest-axe
  toHaveNoViolations). Covers the jsdom test environment (explicitly not
  happy-dom, which breaks axe), accessible-query priority, the always-await
  user-event v14 rule, async findBy/waitFor, the MSW setupServer lifecycle,
  intercepting a generated @hey-api/openapi-ts client at the fetch layer, a
  per-test TanStack Query QueryClientProvider with retry:false, and form +
  request-body + a11y assertions. The middle of the test pyramid: above Vitest
  unit tests, below Playwright e2e.
extensions:
  claude:
    when_to_use: "Writing/setting up React component tests with RTL + MSW + vitest-axe under Vitest (jsdom)."
  copilot:
    applyTo: "**/*.test.tsx"
  cursor:
    alwaysApply: false
    globs: ["**/*.test.tsx", "**/setup-tests.ts", "**/test-utils.tsx"]
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-10
  reviewed: 2026-06-10
---

# `react-component-testing` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, runs to completion, returns a set-up + authored component-test layer (env + setupFiles + a worked test), control passes back to the caller.

> **Verified-at-forge versions.** `@testing-library/react` 16.x · `@testing-library/user-event` 14.x · `@testing-library/jest-dom` 6.x · `msw` 2.x · `vitest-axe` 0.1.x (wraps `axe-core`) · `@tanstack/react-query` 5.x · `vitest` 3.x · jsdom. Teach version-agnostically; re-confirm exact majors + the happy-dom caveat against the maintainer docs at use (see `references/sources.md`).

## Overview

Component tests are the middle layer of the test pyramid: above Vitest unit tests (pure logic — the `vitest` skill owns the runner) and below Playwright e2e (the `playwright-best-practices` skill). They render a **real component tree** and assert what a user sees and does, catching the integration between component + hooks + data-fetching that unit tests miss and that is far cheaper than driving every state through a browser e2e. Three tools compose into one cohesive layer: **React Testing Library (RTL)** renders and queries the tree the way a user perceives it and drives it with `user-event`; **Mock Service Worker (MSW v2)** mocks the **network boundary** so the app's real HTTP client and serialization run end-to-end; **vitest-axe** asserts the rendered output has no detectable accessibility violations. The load-bearing principle: *the more your tests resemble the way your software is used, the more confidence they can give you* — so you query by role/label, interact like a user, mock at the network not the module, and assert observable behavior, never implementation details. This skill owns the RTL + MSW + vitest-axe authoring layer and the component-test environment (`setupFiles`); it references — never re-teaches — the runner, the router harness, and static a11y lint.

## When to activate

- ✅ Writing a component test for a Vite + React + TS SPA: render → interact → assert state → assert accessible.
- ✅ Setting up the component-test environment: the `jsdom` env, `@vitejs/plugin-react`, `setupFiles` (jest-dom matchers, RTL cleanup, the MSW server lifecycle, the vitest-axe extend).
- ✅ Mocking an HTTP/data-fetching boundary in a test — especially a **generated** `@hey-api/openapi-ts` (or `openapi-fetch`) client — so the real client is exercised and contract drift surfaces.
- ✅ Testing TanStack Query loading / empty / success / error states by varying the mocked network response.
- ✅ Testing a form: filling via `user-event`, asserting the **request body** an MSW handler captured, and asserting `toHaveNoViolations`.
- ✅ Adding a runtime accessibility assertion to an existing component test.

**Do NOT activate when:**

- The task is the Vitest **runner** itself — config, coverage thresholds, watch/CI. The `vitest` skill owns that; this skill references it.
- The task is **e2e** browser testing — `playwright-best-practices` owns Playwright + `@axe-core/playwright`. (Vitest browser mode is covered as a documented *alternative* in [`references/browser-mode.md`](references/browser-mode.md), not the default.)
- The task is **static** a11y linting — the `biome` skill (ported jsx-a11y rules) covers lint-time a11y; vitest-axe is the **runtime** complement.
- The task is the **router test harness** — rendering a routed component needs `createMemoryHistory` + a test `RouterProvider`, which the `tanstack-router` skill owns; this skill references it.
- The task is a React, TanStack Query, or shadcn tutorial — those have their own skills; this composes with them.

## Workflow

### Step 1: Internalize the network-boundary principle (the load-bearing decision)

**Mock at the network boundary with MSW, not at the module boundary.** When the component crosses the network, intercept the HTTP request with MSW so the app's real generated client, query hooks, and request/response serialization all run — a contract change (a renamed field, a new required body key) then surfaces in the test. Module-mocking the client (`vi.mock('./generated-client')`) returns a canned object and **skips the exact layer under test**, so it can never catch contract drift.

**The rule:** anything that crosses the network is mocked with **MSW**; `vi.mock` is reserved for **non-HTTP collaborators only** — a clock (`vi.useFakeTimers`), a random-id/uuid generator, a non-deterministic browser API. Detail + the generated-client interception specifics in [`references/msw-and-generated-clients.md`](references/msw-and-generated-clients.md).

### Step 2: Set up the component-test environment (`jsdom`, never `happy-dom`)

In `vitest.config.ts`: add `@vitejs/plugin-react`, set `test.environment: 'jsdom'`, `test.globals: true` (so RTL auto-cleanup and jest-dom matchers register cleanly; otherwise import `{ describe, it, expect, afterEach }` explicitly and call `cleanup()` yourself in an `afterEach`), and point `test.setupFiles` at a setup module.

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup-tests.ts'],
  },
})
```

```ts
// src/test/setup-tests.ts
import '@testing-library/jest-dom/vitest' // toBeInTheDocument, toHaveValue, ...
import 'vitest-axe/extend-expect'         // toHaveNoViolations
import { afterAll, afterEach, beforeAll } from 'vitest'
import { server } from './msw-server'     // setupServer(...) — see references/msw-and-generated-clients.md

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

**Use `jsdom`, not `happy-dom`, for any test that runs vitest-axe.** Happy DOM has a documented `Node.prototype.isConnected` behavior that breaks axe-core's traversal, so vitest-axe assertions do not work under happy-dom. jsdom is also fast and CI-light. (Re-confirm this caveat against the current docs — see `references/sources.md`; if you ever must use happy-dom for non-a11y tests, keep the axe tests in a jsdom project.) With `globals: true`, RTL unmounts and cleans the DOM between tests automatically; without globals, add `afterEach(cleanup)`.

### Step 3: Render + query the way a user perceives the UI

Use `render(<Component />)` and the global `screen`. Query by the **accessible-query priority** — earlier is better:

1. **`getByRole`** (with the accessible `name`, e.g. `screen.getByRole('button', { name: /save/i })`) — what assistive tech and users perceive; the default first choice.
2. **`getByLabelText`** (form fields), then **`getByPlaceholderText`**.
3. **`getByText`** (non-interactive copy), then `getByDisplayValue`, `getByAltText`, `getByTitle`.
4. **`getByTestId`** — last resort only, when nothing user-visible identifies the node.

Assert **behavior, not implementation**: what is on screen and what the user can do, never component state, prop names, or internal call counts. `getBy*` throws if absent (use for "must exist"), `queryBy*` returns `null` (use for "must NOT exist"), `findBy*` is async (next step).

### Step 4: Drive interactions with `user-event` v14 — always `await`

Create a session once per test with `userEvent.setup()`, then **`await` every interaction** — in v14 every interaction returns a Promise, and a missing `await` silently races. Prefer `user-event` over the lower-level `fireEvent`; `fireEvent` dispatches a single raw event, while `user-event` simulates the full sequence a real user triggers (focus, keydown, input, keyup, …).

```ts
const user = userEvent.setup()
await user.type(screen.getByLabelText(/email/i), 'a@b.com')
await user.click(screen.getByRole('button', { name: /submit/i }))
```

### Step 5: Handle async output with `findBy*` / `waitFor`

After an interaction that triggers a fetch, wait for the result. Prefer **`findBy*`** — it bundles `getBy* + waitFor` and retries until the element appears or times out: `expect(await screen.findByText(/saved/i)).toBeInTheDocument()`. Reach for bare `waitFor` only when there is no element to query for; then put **only the assertion** inside the callback — **no side effects** (no `user-event`, no state mutation) inside `waitFor`, since it runs the callback repeatedly. Use `waitForElementToBeRemoved` to assert a spinner/loading node disappears.

### Step 6: Provide app context with a custom `render` (TanStack Query, theme, etc.)

Most components need providers. Write a `test-utils` wrapper that re-exports RTL and a custom `render` mounting a **fresh `QueryClient` per render** with `retry: false` (so error states resolve immediately and deterministically instead of retrying with backoff):

```tsx
// src/test/test-utils.tsx
import { type ReactElement, type ReactNode } from 'react'
import { render, type RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

function makeWrapper() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  )
}

export function renderWithProviders(ui: ReactElement, options?: RenderOptions) {
  return render(ui, { wrapper: makeWrapper(), ...options })
}
export * from '@testing-library/react'
```

A new client per render (plus `server.resetHandlers()` in `afterEach`) prevents cross-test cache bleed. For a **routed** component, compose the `tanstack-router` skill's test `RouterProvider` + `createMemoryHistory` into this wrapper — that harness is owned by that skill; do not re-derive it here. Vary the MSW response per test to exercise loading / empty (`{ data: [] }`) / success / error (a 500 / `ProblemDetail`) states — see [`references/states-and-forms.md`](references/states-and-forms.md).

### Step 7: Assert accessibility with vitest-axe

After rendering (and reaching the state you want to check), run axe on the rendered container and assert no violations. The matcher is registered by `import 'vitest-axe/extend-expect'` in the setup file (or `expect.extend(matchers)` from `vitest-axe/matchers`):

```ts
import { axe } from 'vitest-axe'
const { container } = renderWithProviders(<SignupForm />)
expect(await axe(container)).toHaveNoViolations()
```

vitest-axe needs a real DOM, hence `jsdom` (Step 2). **Honest scope:** automated axe-core detects a *subset* of WCAG issues (commonly cited at roughly a third to a half) — it complements but never replaces manual and assistive-technology review. Detail + rule config in [`references/accessibility-with-vitest-axe.md`](references/accessibility-with-vitest-axe.md).

### Step 8: Worked example — form → user-event → MSW asserts request body → state → no a11y violations

```tsx
// src/features/signup/SignupForm.test.tsx  (colocated *.test.tsx)
import { http, HttpResponse } from 'msw'
import { axe } from 'vitest-axe'
import { renderWithProviders, screen } from '../../test/test-utils'
import { server } from '../../test/msw-server'
import userEvent from '@testing-library/user-event'
import { SignupForm } from './SignupForm'

it('submits the form and shows success', async () => {
  const user = userEvent.setup()
  let captured: unknown

  server.use(
    http.post('/api/users', async ({ request }) => {
      captured = await request.json()                 // assert the REAL request body
      return HttpResponse.json({ id: 'u1' }, { status: 201 })
    }),
  )

  const { container } = renderWithProviders(<SignupForm />)

  await user.type(screen.getByLabelText(/email/i), 'a@b.com')
  await user.type(screen.getByLabelText(/^password/i), 's3cret!')
  await user.click(screen.getByRole('button', { name: /create account/i }))

  expect(await screen.findByText(/account created/i)).toBeInTheDocument()
  expect(captured).toEqual({ email: 'a@b.com', password: 's3cret!' })
  // security invariant: a field that must never leave the form is absent both places
  expect(screen.queryByLabelText(/internal token/i)).not.toBeInTheDocument()
  expect(captured).not.toHaveProperty('internalToken')

  expect(await axe(container)).toHaveNoViolations()
})
```

This exercises the whole layer: the real client serializes the body, MSW captures it at the network boundary, the success state renders, and the output is checked for a11y. Error/validation variants and the security-invariant pattern: [`references/states-and-forms.md`](references/states-and-forms.md).

### Step 9: Conventions + CI

Colocate component tests as `*.test.tsx` next to the component. Keep `test-utils.tsx`, `setup-tests.ts`, and `msw-server.ts` under a `src/test/` folder. **Coverage, thresholds, watch/CI, and the runner config are owned by the `vitest` skill** — run the suite via that skill's `test` script and CI gate; this skill does not re-teach the runner.

## Rules

**Hard rules (never violate):**

- **Mock at the network boundary with MSW; never module-mock a generated HTTP client.** Module-mocking skips the client + serialization and cannot catch contract drift. `vi.mock` is for non-HTTP collaborators only.
- **`await` every `user-event` interaction.** In v14 each one returns a Promise; a missing `await` silently races and produces flaky/false passes.
- **Use `jsdom`, not `happy-dom`, for any vitest-axe test.** Happy DOM's `isConnected` behavior breaks axe traversal; vitest-axe will not work under it.
- **`server.listen()` must run before the HTTP client is created.** MSW installs its interceptor on `listen()`; a client/fetch captured before that bypasses the mock (see references).
- **Query by accessibility first** (`getByRole`/`getByLabelText`); `getByTestId` is a last resort. Test observable behavior, never implementation details.
- **Only the assertion goes inside a `waitFor` callback** — no side effects; prefer `findBy*` over manual `waitFor`.
- **Fresh `QueryClient` per render with `retry: false`** + `resetHandlers()` per test — no shared client, no cross-test cache or handler bleed.

**Preferences (override-able):**

- Prefer `findBy*` over `waitFor` whenever there is an element to query for.
- Prefer a single `userEvent.setup()` per test over the deprecated direct `userEvent.click(...)` calls.
- Keep `onUnhandledRequest: 'error'` in `server.listen()` so an un-mocked request fails loudly instead of hitting the real network.
- Put a11y assertions on the state you actually ship (post-load, post-error), not only the initial render.

## Gotchas

- **Missing `await` on a `user-event` call.** The interaction's Promise never resolves before the assertion runs; the test passes for the wrong reason or flakes. Always `await`.
- **happy-dom + axe = silent breakage.** Tests "run" but vitest-axe behaves incorrectly because of the `Node.prototype.isConnected` bug. Pin the a11y tests to `jsdom`.
- **Client created at import time, before `listen()`.** A generated client that instantiates `fetch` at module load (top-level `const client = createClient()`) can bind a `fetch` reference MSW hasn't patched yet. Ensure MSW's setup file is in `setupFiles` (runs first) and, for some generated/`openapi-fetch` clients, pass MSW-visible `fetch` explicitly — see [`references/msw-and-generated-clients.md`](references/msw-and-generated-clients.md).
- **Query params in the handler path.** MSW matches on the pathname; putting `?foo=bar` in `http.get('/api/x?foo=bar', ...)` does not match — read query params from `new URL(request.url)` inside the handler instead.
- **Side effects inside `waitFor`.** `waitFor` re-runs its callback many times; a `user-event` or state mutation inside it fires repeatedly. Keep it assertion-only.
- **Forgetting jest-dom's `/vitest` entry.** Importing `@testing-library/jest-dom` (the Jest entry) instead of `@testing-library/jest-dom/vitest` fails to register matchers under Vitest.
- **Stale QueryClient across tests.** Reusing one client caches the first response; later tests see stale data. New client per render.
- **Over-trusting axe.** Zero violations is necessary, not sufficient — it covers a subset of WCAG; manual/AT review still required.

## Anti-patterns

- **"Just `vi.mock` the API client — it's simpler."** That deletes the layer under test; the generated client and serialization never run, so contract drift is invisible. Mock the network with MSW.
- **"`getByTestId` everywhere — it's stable."** Test IDs bypass the accessibility tree and let inaccessible UI pass. Query by role/label; testid is the last resort.
- **"`fireEvent.click` is fine."** It dispatches one synthetic event, not the real interaction sequence; reach for `user-event` for anything a user actually does.
- **"happy-dom is faster, use it for the a11y tests too."** It breaks axe. The speed win is not worth a silently non-functional a11y assertion.
- **"Assert the component called `fetch` / the hook's internal state."** Implementation coupling — refactors break the test without a behavior change. Assert what the user sees and the request the server received.
- **"Re-teach the Vitest config / coverage here."** Out of scope — the `vitest` skill owns the runner; reference it.

## Output

A working component-test layer for a Vite + React + TS SPA: the `jsdom` Vitest environment with `@vitejs/plugin-react`, a `setupFiles` module wiring jest-dom matchers + RTL cleanup + the MSW server lifecycle + the vitest-axe extend, a `test-utils` custom `render` (fresh TanStack Query client, `retry:false`, composable with the router harness), and authored `*.test.tsx` files that render, drive via `user-event`, mock the network with MSW (including a generated client), assert request bodies and UI state, and assert `toHaveNoViolations`. The consumer is the next workflow phase — the developer or dispatched agent who now writes contract-driven, accessible component tests, with the runner/coverage/CI provided by the `vitest` skill.

## Related

- `vitest` — owns the runner, config, coverage thresholds, watch/CI; this skill owns the component-test env + RTL/MSW/axe authoring on top.
- `tanstack-query` — the data-fetching hooks under test; this skill shows the per-test `QueryClientProvider` (`retry:false`), not the library itself.
- `tanstack-router` — owns the router test harness (`createMemoryHistory` + test `RouterProvider`); compose it into the custom `render` for routed components.
- `playwright-best-practices` — the e2e sibling (real-browser, `@axe-core/playwright`); component tests sit below it. See also [`references/browser-mode.md`](references/browser-mode.md).
- `biome` — static jsx-a11y lint (lint-time); vitest-axe is the runtime complement.
- `shadcn` — the components/forms under test.

## Progressive disclosure

- [`references/msw-and-generated-clients.md`](references/msw-and-generated-clients.md) — MSW v2 `setupServer`/`http`/`HttpResponse`, the Node lifecycle, per-test overrides, reading the request body, the query-param warning, and intercepting a generated `@hey-api/openapi-ts` / `openapi-fetch` client (listen-before-create ordering + the custom-`fetch` caveat). Load when mocking the network.
- [`references/accessibility-with-vitest-axe.md`](references/accessibility-with-vitest-axe.md) — vitest-axe setup variants, `toHaveNoViolations`, the jsdom requirement, rule configuration, and the honest WCAG-subset scope. Load when adding a11y assertions.
- [`references/states-and-forms.md`](references/states-and-forms.md) — loading/empty/success/error state testing with MSW + TanStack Query, and the form + request-body + security-invariant assertion patterns. Load when testing data states or forms.
- [`references/browser-mode.md`](references/browser-mode.md) — the documented *alternative*: Vitest browser mode (Playwright provider) + `@axe-core/playwright`, with the trade-offs (slower, heavier CI, a11y shifts off vitest-axe, overlaps the e2e skill). jsdom is the default; load only when real-browser fidelity is required.
- [`references/sources.md`](references/sources.md) — research provenance + the verify-against-docs list.

## Body budget

- `description` ≤ 1,024 chars.
- Body ≤ ~500 lines / 5,000 tokens; heavy content lives in `references/`, loaded on demand.
