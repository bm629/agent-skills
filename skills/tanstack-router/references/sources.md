# Sources — tanstack-router

Research provenance for the `tanstack-router` skill. Forged 2026-06-10.

## Version verified at forge

- **`@tanstack/react-router`**: v1 major, latest `1.170.x` (published within days of forge, June 2026). The library is on a rolling v1 with semver-minor releases.
- **`@tanstack/zod-adapter`**: `1.166.x`. Provides `zodValidator` for Zod v3; for Zod v4 the adapter is no longer required (pass schema directly to `validateSearch`). Supersedes the deprecated `@tanstack/router-zod-adapter`.

## Primary source — official TanStack Router docs (`tanstack.com/router`)

Doc pages consulted (via web search over `tanstack.com`, June 2026). WebFetch of full page bodies was unavailable in the forge environment (denied); grounding was done via targeted web-search summaries of the official docs, cross-checked against two community skills used as secondary source material.

- Installation with Vite — `/router/latest/docs/installation/with-vite` (plugin export `tanstackRouter` from `@tanstack/router-plugin/vite`; legacy `TanStackRouterVite` / `@tanstack/router-vite-plugin` aliased).
- Quick Start — `/router/latest/docs/framework/react/quick-start`.
- Routing Concepts — `/router/latest/docs/routing/routing-concepts`.
- File Naming Conventions — `/router/latest/docs/routing/file-naming-conventions` (`__root`, `index`, `$param`, `_pathless`, `(group)`, `$` splat, dot-notation, trailing-underscore non-nested).
- Virtual File Routes — `/router/latest/docs/routing/virtual-file-routes`.
- Creating a Router — `/router/v1/docs/framework/react/guide/creating-a-router` (`createRouter`, `RouterProvider`, the `Register` declaration merge).
- createFileRoute function — `/router/v1/docs/framework/react/api/router/createFileRouteFunction` (path string first, then options).
- Router Context — `/router/latest/docs/framework/react/guide/router-context` (`createRootRouteWithContext<T>()`).
- Data Loading — `/router/latest/docs/guide/data-loading` (loaders, `loaderDeps`, loader args incl. `abortController`/`cause`/`preload`).
- Deferred Data Loading — `/router/latest/docs/framework/react/guide/deferred-data-loading` (return raw unawaited promise; `<Await>` / `useAwaited`; `defer()` for SSR serialization).
- Search Params — `/router/latest/docs/guide/search-params` (`validateSearch`, `useSearch`, functional `search` updaters, parent→child inheritance, custom `serialize`/`parse`).
- Validate Search Parameters with Schemas — `/router/latest/docs/how-to/validate-search-params` (`zodValidator` from `@tanstack/zod-adapter`; Zod v4 needs no adapter).
- stripSearchParams / retainSearchParams middleware — `/router/latest/docs/framework/react/api/router/stripSearchParamsFunction`, `/router/v1/docs/framework/react/api/router/retainSearchParamsFunction` (route `search.middlewares` array).
- Navigation — `/router/latest/docs/guide/navigation` (`Link`, `useNavigate`, `<Navigate>`).
- Link Options — `/router/latest/docs/framework/react/guide/link-options`.
- Navigation Blocking + useBlocker hook — `/router/v1/docs/framework/react/guide/navigation-blocking`, `/router/v1/docs/api/router/useBlockerHook` (`shouldBlockFn`, `withResolver`, `status`/`proceed`/`reset`/`next`/`current`).
- Code Splitting — `/router/latest/docs/guide/code-splitting` (`createLazyFileRoute` / `.lazy.tsx`, manual `.lazy()`, keep loader in initial bundle).
- Automatic Code Splitting — `/router/latest/docs/guide/automatic-code-splitting` (`autoCodeSplitting`, `defaultBehavior`/`splitBehavior`).
- Route Masking + createRouteMask — `/router/latest/docs/guide/route-masking`, `/router/v1/docs/framework/react/api/router/createRouteMaskFunction` (`mask` on Link/navigate; `routeMasks` on router; client-side only).
- Authenticated Routes — `/router/latest/docs/guide/authenticated-routes` (`createRootRouteWithContext` + `_authenticated` pathless layout + `beforeLoad` redirect guard).
- TanStack Query Integration — `/router/latest/docs/integrations/query` (`ensureQueryData` in loader + `useSuspenseQuery` in component; `router.invalidate()`; set Query `staleTime > 0` for prefetch).
- External Data Loading — `/router/latest/docs/guide/external-data-loading` (`defaultPreloadStaleTime: 0` to hand caching to Query).
- Setup Testing / Test Router with File-Based Routing — `/router/latest/docs/framework/react/how-to/setup-testing`, `/router/latest/docs/how-to/test-file-based-routing` (`createMemoryHistory({ initialEntries })` + `createRouter` + `RouterProvider`; memory history for non-browser environments).
- History Types — `/router/v1/docs/guide/history-types` (`createMemoryHistory`).
- npm — `@tanstack/react-router`, `@tanstack/zod-adapter` (version + publish-date check).

## Secondary source material (external, sanitized clean before use)

Two cloned community skills, read as source material and **paraphrased** (never copied). Both passed `external-content-sanitizer` with zero injection findings:

- `tanstack-skills@tanstack-router` (single comprehensive `SKILL.md`).
- `deckardger/tanstack-agent-skills@tanstack-router` (`SKILL.md` + `rules/*.md`).

**Corrections applied where the candidates were stale vs. current docs:** (1) Vite plugin export is `tanstackRouter`, not `TanStackRouterVite`; (2) Zod search validation uses `zodValidator` from `@tanstack/zod-adapter` (v3) or direct schema (v4), not a bare `.parse` adapter; (3) deferred loading returns a raw unawaited promise consumed via `<Await>` (the `defer()` helper is for SSR serialization); (4) loaders should stay in the initial bundle (don't code-split them).

## Boundaries (named, not taught)

- **TanStack Start** — `/start/latest` — the SSR/full-stack framework built on the router; downstream consumer, out of scope.
- **React Router** (`react-router` / Remix) — the alternative router not chosen; out of scope.
- **TanStack Query mechanics** — canonical in the adopted `tanstack-query` skill; this skill cross-references it for all query internals.

## Main-thread Phase-D verify (2026-06-10 — COMPLETED)

The plan's main-thread doc-grounded Phase D ran and **passed** (the backstop for the background-forge degradations: WebFetch denied in the worker; zero fresh-reviewer cycles — see [[feedback_background_forge_degraded_research]]). Confirmed from the main thread:
- **Vite plugin export `tanstackRouter`** from `@tanstack/router-plugin/vite`, called `tanstackRouter({ target: 'react', autoCodeSplitting: true })` before `react()`, with the legacy `TanStackRouterVite`/`@tanstack/router-vite-plugin` aliasing — CONFIRMED (web search over the official `tanstack.com/router` install docs). The forge's correction from the stale candidate name was right.
- **Zod search validation** — `zodValidator` from `@tanstack/zod-adapter` for Zod v3; Zod v4 passes the schema directly (Standard Schema) + `.catch()`, no adapter — CONFIRMED (official validate-search-params docs + TanStack issue #4322).
- **`createFileRoute` path-first signature, the `Register` declaration merge, `createMemoryHistory` test harness, `defaultPreload`, `useBlocker`, search middleware, `router.invalidate()`** — corroborated by the main thread's earlier `deep-research` canonical snippets + the two sanitized candidate skills.
- **DQ3 query-overlap mitigation — VERIFIED HELD:** all query content is routing-framed and cross-references `tanstack-query` as canonical (`query-integration.md` has an explicit in-scope/out-of-scope boundary; SKILL.md Step 6 + Rules + Anti-patterns enforce it); no standalone query patterns.
- **Two version-sensitive items** (trailing-underscore literal-escape file form; plugin `defaultBehavior`/`splitBehavior`) remain hedged in-skill ("check your version's docs") — accurate, not load-bearing.
