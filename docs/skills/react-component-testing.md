# react-component-testing

> The RTL + MSW + vitest-axe component-test layer for a Vite + React + TypeScript
> SPA under Vitest (jsdom). Render a real component tree, drive it like a user
> (React Testing Library + `user-event`), mock the **network boundary** (Mock
> Service Worker v2 — not the module, so the real generated client + serialization
> run and contract drift surfaces), and assert the output is accessible
> (`vitest-axe` `toHaveNoViolations`). The middle of the test pyramid: above
> Vitest unit tests, below Playwright e2e.

**Skill file:** [`skills/react-component-testing/SKILL.md`](../../skills/react-component-testing/SKILL.md)
**Version:** 1.0.0

## Purpose

A component test renders a component tree and asserts what a user sees and does —
catching the integration of component + hooks + data-fetching that unit tests miss
and that is far cheaper than driving every state through a browser e2e. This skill
sets up the component-test environment (the `jsdom` env, `@vitejs/plugin-react`,
`setupFiles`) and teaches the authoring layer: accessible queries, `user-event`,
async, MSW network-boundary mocking (including a generated `@hey-api/openapi-ts`
client), a per-test TanStack Query client, and runtime a11y. It owns the RTL + MSW
+ vitest-axe layer; the runner belongs to `vitest`, the router test harness to
`tanstack-router`, static a11y to `biome`, e2e to `playwright-best-practices`.

## When to activate

- ✅ Writing a component test: render → interact → assert state → assert accessible.
- ✅ Setting up the component-test environment (`jsdom`, `@vitejs/plugin-react`, `setupFiles`).
- ✅ Mocking an HTTP boundary — especially a generated `@hey-api/openapi-ts` / `openapi-fetch` client — so the real client runs and contract drift surfaces.
- ✅ Testing TanStack Query loading / empty / success / error states by varying the mocked response.
- ✅ Adding a runtime accessibility assertion (`toHaveNoViolations`) to a component test.

### When NOT to activate

- The Vitest **runner** itself (config, coverage thresholds, watch/CI) — that's `vitest`.
- **e2e** browser testing — that's `playwright-best-practices` (Vitest browser mode is a documented alternative in `references/browser-mode.md`, not the default).
- **Static** a11y linting — that's `biome` (ported jsx-a11y); vitest-axe is the runtime complement.
- The **router test harness** (`createMemoryHistory` + test `RouterProvider`) — that's `tanstack-router`; this composes it in.

## Workflow

| Step | Does |
|---|---|
| 1 Network-boundary principle | Mock with MSW at the network, never module-mock the generated client (that skips the layer under test); `vi.mock` only for non-HTTP collaborators. |
| 2 Environment | `environment: 'jsdom'` (NOT happy-dom — breaks axe), `@vitejs/plugin-react`, `globals`, `setupFiles` (jest-dom `/vitest`, RTL cleanup, MSW lifecycle, vitest-axe extend). |
| 3 Query the UI | Accessible-query priority (`getByRole` → label/placeholder → text → `getByTestId` last); assert behavior, not implementation. |
| 4 Interact | `userEvent.setup()` + **always `await`** every interaction (v14 returns Promises). |
| 5 Async | Prefer `findBy*` (= `getBy` + `waitFor`); only the assertion inside a bare `waitFor`. |
| 6 Providers | A custom `render` mounting a fresh `QueryClient` per render (`retry:false`); compose the router harness for routed components. |
| 7 Accessibility | `await axe(container)` + `toHaveNoViolations()`; jsdom required; honest WCAG-subset scope. |

## Hard rules it enforces

- **Mock the network with MSW; never module-mock a generated HTTP client** — module-mocking can't catch contract drift.
- **`await` every `user-event` interaction** — a missing `await` silently races.
- **Use `jsdom`, not `happy-dom`, for any vitest-axe test** — happy-dom's `Node.prototype.isConnected` breaks axe traversal.
- **`server.listen()` before the HTTP client is created** — MSW installs its interceptor on `listen()`.
- **Query by accessibility first; test observable behavior, never implementation details.**

## Progressive disclosure (`references/`)

- `references/msw-and-generated-clients.md` — MSW v2 `setupServer`/`http`/`HttpResponse`, the Node lifecycle, per-test overrides, reading the request body, the query-param warning, and intercepting a generated `@hey-api/openapi-ts` / `openapi-fetch` client (listen-before-create + the custom-`fetch` caveat).
- `references/accessibility-with-vitest-axe.md` — vitest-axe setup, `toHaveNoViolations`, the jsdom requirement, rule config, and the honest WCAG-subset scope.
- `references/states-and-forms.md` — loading/empty/success/error state testing with MSW + TanStack Query, and the form + request-body + security-invariant assertion patterns.
- `references/browser-mode.md` — the documented alternative: Vitest browser mode (Playwright provider) + `@axe-core/playwright`, with the trade-offs. jsdom is the default.
- `references/sources.md` — research provenance + the verify-against-docs list.

## Limitations

- **Library majors confirmed at forge** (`@testing-library/react` 16.x, `user-event` 14.x, `jest-dom` 6.x, `msw` 2.x, `vitest-axe` 0.1.x, `@tanstack/react-query` 5.x); taught version-agnostically — re-confirm the exact versions + the happy-dom caveat when installing.
- **Owns the component-test layer, not the runner** — `vitest` owns config/coverage/CI; this contributes the env + authoring.
- **Automated axe covers a subset of WCAG** — necessary, not sufficient; manual / assistive-tech review still required.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
