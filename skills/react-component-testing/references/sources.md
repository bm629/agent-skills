# Sources — research provenance

Forged 2026-06-10 via `skill-forge`. Topic: the RTL + MSW + vitest-axe component-test layer for a Vite + React + TS SPA under Vitest (jsdom). Findings paraphrased, not copied. All external reads were intended to pass through `external-content-sanitizer`.

## DEGRADED-STEP DISCLOSURE (read before trusting version-specific facts)

This forge ran in a **network-restricted sandbox**. The following pipeline tools were **denied** and could not run:

- **`npx skills find`** (Step 2.1 discovery) — denied. Discovery relied on the spec's recorded forge-time sweep (below) rather than a fresh registry query.
- **`WebFetch` / live `deep-research` retrieval** (Step 2.2) — denied. The canonical maintainer docs (testing-library.com, mswjs.io, github.com/chaance/vitest-axe, vitest.dev, hey-api) could **NOT** be fetched fresh at forge time.

Mitigation actually applied: facts were grounded against **locally-installed canonical package source** where available (see "Locally-verified" below) and against the **design-reviewed spec** (which derived its coverage from these same canonical docs). Everything not locally verifiable is flagged "VERIFY" — the main thread must confirm these against live docs (the plan's Phase D is main-thread + doc-grounded for exactly this reason).

## Locally-verified facts (installed package source — trusted, not network)

Verified by reading installed packages in a sibling project's `node_modules` (canonical published artifacts):

- **`@testing-library/react` 16.3.2** — confirms current major is 16.x.
- **`@testing-library/user-event` 14.6.1** — confirms v14. The `dist/types/setup/directApi.d.ts` typings show every interaction (`click`, `type`, `clear`, `selectOptions`, `tab`, `hover`, `upload`, `paste`, etc.) returns a `Promise<…>`, and `setup()` returns a `UserEvent` session sharing input-device state → grounds the "always `await`" rule and the `userEvent.setup()` API.
- **`@testing-library/jest-dom` 6.9.1** — `package.json` `exports` confirms the `./vitest` entry (`@testing-library/jest-dom/vitest`) and the `./matchers` entry → grounds the setupFiles import.
- The user-event README confirms the guiding principle quote and the `fireEvent` → `user-event` evolution.

## Main-thread Phase-D verify (2026-06-10 — COMPLETED)

The plan's main-thread doc-grounded Phase D ran and **passed**. Items below were confirmed against canonical sources from the main thread (not the sandboxed forge worker):
- **Item 4 (happy-dom `isConnected` breaks axe → use jsdom):** CONFIRMED verbatim against the live `chaance/vitest-axe` README (WebFetch).
- **Item 8 (`vitest-axe/extend-expect` + `vitest-axe/matchers` + `toHaveNoViolations` + `axe(container)` usage):** CONFIRMED against the same README.
- **Items 1/2/3/5/6/7/10:** corroborated by the main thread's earlier `deep-research` RETRIEVE canonical snippets (testing-library.com RTL query priority + async + user-event v14 always-await; mswjs.io `setupServer`/`http`/`HttpResponse`/lifecycle/Node 18+; openapi-fetch custom-`fetch` + listen-before-create; vitest.dev browser-mode `instances`+playwright provider).
- **Item 6 exact `fetch` knob:** intentionally left hedged (generator-dependent) — accurate, not fabricated.
- The two background-forge degradations (no live WebFetch in the worker; zero fresh-reviewer cycles) were covered by this main-thread doc-grounded adversarial verify per [[feedback_background_forge_degraded_research]].

## VERIFY against live canonical docs (recorded at forge — now confirmed above)

1. **React Testing Library query priority** (testing-library.com/docs/queries/about) — the documented order `getByRole` → `getByLabelText`/`getByPlaceholderText`/`getByText` → … → `getByTestId` (last resort), and the three priority groups. Stated in the skill from established RTL guidance; confirm wording/order unchanged.
2. **user-event vs fireEvent** prose, and `userEvent.setup()` being the v14-recommended entry — confirm against testing-library.com/docs/user-event/intro.
3. **`findBy*` = `getBy` + `waitFor`**, "only the assertion inside `waitFor`, no side effects", `waitForElementToBeRemoved` — confirm against testing-library.com async docs.
4. **Happy DOM `Node.prototype.isConnected` bug breaking axe / vitest-axe** — THE load-bearing "use jsdom not happy-dom" claim. Could NOT be re-verified at forge. Confirm against the happy-dom and/or vitest-axe / axe-core issue trackers that this is real and current before relying on it.
5. **MSW v2 API + lifecycle** (mswjs.io) — `setupServer` from `msw/node`; `http` + `HttpResponse` replacing v1 `rest`/`res(ctx)`; `listen({ onUnhandledRequest: 'error' })` / `resetHandlers()` / `close()`; `server.use(...)`; Node 18+ requirement; `await request.json()` to read the body; the "query params belong in the handler, not the path" warning. Confirm exact API surface + the Node-version floor.
6. **Generated `@hey-api/openapi-ts` / `openapi-fetch` client interception** — the `listen()`-before-client-creation ordering and the custom-`fetch` caveat (a client given its own `fetch` may bypass MSW's global patch). FLAGGED in the skill body itself as unverified — confirm the exact `fetch` option name + behavior against current hey-api + MSW docs. Also confirm MSW intercepts global `fetch` in Node by default.
7. **TanStack Query v5 testing** (tanstack.com/query testing docs) — fresh `QueryClientProvider` per test + `retry: false` + new client per test. Confirm against the official testing guide.
8. **vitest-axe** (github.com/chaance/vitest-axe README) — `vitest-axe/extend-expect` and `vitest-axe/matchers`; `await axe(container)` + `toHaveNoViolations()`; jsdom requirement; current package version (forge assumed 0.1.x) and which axe-core version it wraps. Confirm version + the matcher type-augmentation path.
9. **axe-core WCAG-subset scope** — the "automated axe catches a subset of WCAG" claim. The skill deliberately states "a subset" and avoids a hard percentage (the commonly-cited ~30–57% figures vary by source). Cite a specific Deque/axe-core source if a number is wanted.
10. **Vitest browser mode** (vitest.dev/guide/browser) — `@vitest/browser` + the `playwright` provider, the `browser.instances` config shape, current stability label, and `@axe-core/playwright` for browser a11y. Confirm config shape + stability status.

## Discovery (Step 2.1 — degraded; from the spec's recorded forge-time sweep)

`npx skills find` was denied. The decision **FORGE** is carried from the approved spec (`docs/superpowers/react-component-testing/spec/v1.md`), whose fifth-sweep (2026-06-10) triage recorded: RTL candidates are sub-1K third-party (`itechmeat/llm-code@react-testing-library` ~950, `pproenca` ~231); the high-install `msw-*` hits are a name collision with a game plugin (the real `anivar/msw-skill@msw` ~56); and **no `vitest-axe` skill exists at all**. No clean ≥1K/official adoptable candidate for the combined three-tool scope → forge from the canonical maintainer docs, with the sub-1K third-party RTL skills as secondary source material only. None was installed verbatim.

## Sibling skills referenced (in-repo, not duplicated)

`vitest` (3.x — runner/coverage/CI), `tanstack-query` (v5 — the hooks under test), `tanstack-router` (router test harness), `playwright-best-practices` (e2e + `@axe-core/playwright`), `biome` (static jsx-a11y), `shadcn` (components under test). Boundaries stated in the skill body; their content is not restated here.
