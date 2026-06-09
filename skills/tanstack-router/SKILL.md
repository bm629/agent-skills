---
name: tanstack-router
description: >
  Use when setting up or using TanStack Router (@tanstack/react-router) in a
  Vite + React + TypeScript SPA — defining a route tree, end-to-end type-safe
  navigation, search-param validation, route loaders, code-splitting,
  preloading, authenticated routes, and the loader-to-TanStack-Query handshake.
  Produces a working file-based (or code-based) router: createRouter +
  RouterProvider + the Register augmentation, typed Link / useNavigate / useParams /
  useSearch, validateSearch, loaders with loaderDeps and deferred data, and a
  memory-history test harness for routed components. Covers file naming
  conventions, redirect guards, route masking, scroll restoration, head/meta,
  and notFound handling. Keywords: TanStack Router, type-safe routing, react
  router alternative, createFileRoute, search params, route loader, RouterProvider.
extensions:
  claude:
    when_to_use: "Setting up or using TanStack Router in a Vite + React + TS SPA (routing, type-safe nav, search params, loaders, code-splitting, query integration, routed-component test harness)."
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-10
  reviewed: 2026-06-10
---

# `tanstack-router` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, you read it, you wire up or extend a TanStack Router app, control returns to the caller.

> **Verified against `@tanstack/react-router` v1 (1.170.x), TanStack Router docs as of 2026-06.** TanStack Router is on the **v1** major (rolling, semver-minor releases). The API below was checked against the official `tanstack.com/router` docs at forge time. Treat exact option names as version-pinnable: if a name 404s in your installed version, check that version's docs page named in `references/sources.md`.

## Overview

TanStack Router is a fully type-safe client-side router for React SPAs. Its differentiator is that the **route tree is the type source**: once you register your router via TypeScript declaration merging, every `Link`, `navigate`, `useParams`, `useSearch`, and `useLoaderData` is checked against the real routes — invalid paths and missing params are compile errors. It owns **first-class search params** (URL state validated by a schema), **route loaders** (data fetched before render, with preloading), and **code-splitting**. This skill stands up the router, wires the routes type-safely, and covers the loader-to-data-fetching seam (including the TanStack Query handshake) and a test harness for routed components. It is the **routing layer**; the full-stack framework **TanStack Start** builds on top of it (out of scope here — see Boundaries).

## When to activate

- ✅ Setting up routing in a Vite + React + TypeScript SPA (or extending an existing TanStack Router app).
- ✅ Defining routes, typed navigation, validated search params, or route loaders.
- ✅ Wiring route loaders to TanStack Query (prefetch in loader, read in component).
- ✅ Writing a test that renders a routed component (needs the memory-history harness).

**Do NOT activate when:**

- The project uses **React Router** (`react-router` / Remix) — that is a different router; this skill does not translate to it.
- You need **TanStack Start** SSR / server functions / streaming dehydration — Start is the downstream consumer, not taught here.
- You need **TanStack Query mechanics divorced from routing** (cache config, mutations, infinite queries unrelated to a route) — that is the `tanstack-query` skill's job; this skill only covers query *as reached through a route loader/context*.

## Workflow

### Step 1: Install + wire the bundler plugin

```bash
npm install @tanstack/react-router
npm install -D @tanstack/router-plugin                    # file-based routing (Vite/Rspack/Webpack)
npm install -D @tanstack/react-router-devtools            # optional, dev-only
```

Add the plugin to Vite. The current export is **`tanstackRouter`** (camelCase) from `@tanstack/router-plugin/vite` — it must run **before** `@vitejs/plugin-react`:

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    tanstackRouter({ target: 'react', autoCodeSplitting: true }),
    react(),
  ],
})
```

The plugin watches `src/routes/` and generates `src/routeTree.gen.ts`. (The legacy `TanStackRouterVite` name and the `@tanstack/router-vite-plugin` package still work via aliasing, but `tanstackRouter` is the current name. See `references/sources.md`.)

### Step 2: Type-safe setup (`createRouter` + `RouterProvider` + `Register`)

This is the wiring that makes navigation type-safe app-wide. The `Register` declaration-merge is **mandatory** — without it the typed hooks fall back to unions and you lose autocomplete + compile checks.

```tsx
// src/router.tsx
import { createRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',          // preload on hover/focus; see Step 6
  scrollRestoration: true,
})

// Declaration merging: binds YOUR router's type into the library's hooks.
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
```

```tsx
// src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from '@tanstack/react-router'
import { router } from './router'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
```

### Step 3: The root route

```tsx
// src/routes/__root.tsx
import { createRootRoute, Outlet, Link } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

export const Route = createRootRoute({
  component: () => (
    <>
      <nav>
        <Link to="/">Home</Link>{' '}
        <Link to="/posts">Posts</Link>
      </nav>
      <Outlet />
      <TanStackRouterDevtools />
    </>
  ),
})
```

`__root.tsx` wraps every route; `<Outlet />` renders the matched child. For a **typed router context** (e.g. injecting a `queryClient`) use `createRootRouteWithContext<T>()` instead — see `references/auth-and-testing.md` and `references/query-integration.md`.

### Step 4: A worked route — file-based (the recommended default)

File-based routing is TanStack's default and the primary path here. The file's location determines its URL; `createFileRoute('/path')` takes the **path string first**, then an options object. A complete route with a path param, validated search, a loader, and a component:

```tsx
// src/routes/posts.$postId.tsx        ->  matches /posts/$postId
import { createFileRoute } from '@tanstack/react-router'
import { z } from 'zod'
import { zodValidator } from '@tanstack/zod-adapter'

const postSearchSchema = z.object({
  tab: z.enum(['body', 'comments']).catch('body'),
})

export const Route = createFileRoute('/posts/$postId')({
  validateSearch: zodValidator(postSearchSchema),   // Zod v3 adapter; Zod v4: pass schema directly
  loader: async ({ params }) => fetchPost(params.postId),
  component: PostComponent,
})

function PostComponent() {
  const { postId } = Route.useParams()        // { postId: string } — typed
  const { tab } = Route.useSearch()           // { tab: 'body' | 'comments' } — typed
  const post = Route.useLoaderData()          // typed to the loader's return
  return <article data-tab={tab}>{post.title}</article>
}
```

`Route.useParams()` / `Route.useSearch()` / `Route.useLoaderData()` are the in-file typed hooks — no `from` argument needed because the route object is the source. From *other* files use `useParams({ from: '/posts/$postId' })` or `getRouteApi('/posts/$postId')` (see `references/search-and-loaders.md`).

> **Code-based routing** (`createRootRoute` / `createRoute` with `getParentRoute` + `addChildren` + manual `createRouter`) is fully supported and gets first-class treatment in **`references/routing-approaches.md`** — use it when you cannot run the bundler plugin.

### Step 5: Navigation essentials

```tsx
import { Link, useNavigate, redirect } from '@tanstack/react-router'

// Declarative — renders a real <a href>; preloads on intent.
<Link to="/posts/$postId" params={{ postId: '123' }} search={{ tab: 'comments' }}
      activeProps={{ className: 'active' }}>Post 123</Link>

// Imperative — for side effects (after a form submit, etc.).
const navigate = useNavigate()
navigate({ to: '/posts', search: (prev) => ({ ...prev, tab: 'body' }) })

// Redirect — THROW it from beforeLoad/loader (never navigate in a component for guards).
throw redirect({ to: '/login', search: { redirect: location.href } })
```

Full surface — `activeOptions`, render-prop `isActive`, navigation blocking (`useBlocker`), route masking — is in `references/navigation-and-splitting.md`.

### Step 6: The loader-to-data seam (and the TanStack Query handshake)

A route loader runs **before** the component renders, so data is ready on mount and can be **preloaded** on link intent. The recommended integration with TanStack Query: define a `queryOptions` factory, `ensureQueryData` it in the loader, then read it with `useSuspenseQuery` in the component.

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'
import { postQueryOptions } from '../queries'   // a queryOptions factory

export const Route = createFileRoute('/posts/$postId')({
  loader: ({ context: { queryClient }, params }) =>
    queryClient.ensureQueryData(postQueryOptions(params.postId)),
  component: Post,
})

function Post() {
  const { postId } = Route.useParams()
  const { data: post } = useSuspenseQuery(postQueryOptions(postId))  // cache hit — no refetch
  return <article>{post.title}</article>
}
```

The `queryClient` reaches the loader through the **router context** (`createRootRouteWithContext<{ queryClient: QueryClient }>()` + `createRouter({ context: { queryClient } })`). The full integration — await-vs-defer, `defaultPreloadStaleTime: 0`, invalidation-after-mutation via `router.invalidate()`, and the **cross-reference to the canonical `tanstack-query` skill** — lives in `references/query-integration.md`. TanStack Query's own mechanics (query keys, mutations, cache tuning in the abstract) are **not** taught here; that is the `tanstack-query` skill.

### Step 7: Test a routed component

To render a route under test without a browser URL, build an in-memory router and wrap with `RouterProvider`. This skill **owns** this harness; the component-testing skill consumes it.

```tsx
import { render, screen } from '@testing-library/react'
import { createMemoryHistory, createRouter, RouterProvider, createRootRoute, createRoute } from '@tanstack/react-router'

function renderRoute(initialPath: string) {
  const rootRoute = createRootRoute()
  const indexRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', component: HomePage })
  const routeTree = rootRoute.addChildren([indexRoute])
  const router = createRouter({
    routeTree,
    history: createMemoryHistory({ initialEntries: [initialPath] }),
  })
  render(<RouterProvider router={router} />)
}
```

Await the rendered output via Testing Library's `findBy*` (the router resolves loaders before the matched component appears). Drive navigation with `router.navigate(...)`. Full harness — typed test router factory, file-based-tree variant, awaiting `router.load()` — is in `references/auth-and-testing.md`.

## Rules

**Hard rules (never violate):**

- **Always add the `Register` declaration merge.** Without `declare module '@tanstack/react-router' { interface Register { router: typeof router } }`, every typed hook degrades to a union of all routes and you lose compile-time route checking.
- **Put auth/redirect guards in `beforeLoad` (or `loader`), never in a component.** Throwing `redirect(...)` from `beforeLoad` stops the route before it renders — guarding in a component flashes protected content first.
- **Use `loaderDeps` whenever the loader depends on search params.** A loader does *not* re-run on a search change unless that dependency is declared in `loaderDeps` — omitting it serves stale data.
- **Validate every search param via `validateSearch`.** Search params are user-controlled URL input; an unvalidated read is an `any` hole and a runtime risk.
- **Pass a `from` (or use `Route.*` / `getRouteApi`) on typed hooks outside their own route file.** A bare `useParams()` in a shared component returns a union, not the route's exact type.
- **Keep query mechanics framed through routing.** This skill covers TanStack Query only at the loader/context seam and cross-references `tanstack-query` as canonical — do not lift standalone query patterns into router code.

**Preferences (override-able):**

- Prefer **file-based routing** (`tanstackRouter` plugin + `createFileRoute`); reach for code-based only when you cannot run the bundler plugin.
- Prefer **`<Link>`** over `useNavigate` for user-initiated navigation (real `<a href>`, middle-click, preloading, a11y); reserve `useNavigate` for side effects.
- Set `defaultPreload: 'intent'` for snappy navigation; set `defaultPreloadStaleTime: 0` when TanStack Query owns the cache.
- **Keep the `loader` in the initial bundle** (do not code-split it) unless you have a specific reason — splitting it adds a server round-trip before data can be fetched.

## Gotchas

- **`TanStackRouterVite` / `@tanstack/router-vite-plugin` look right but are the old names.** The current export is `tanstackRouter` from `@tanstack/router-plugin/vite`. Old names still alias through, so code "works" while drifting from the docs — match the current name.
- **`routeTree.gen.ts` is generated — never hand-edit it, and it must exist before `createRouter`.** If imports from `./routeTree.gen` fail, the plugin has not run (start the dev server / build) or is ordered after `react()` in the Vite config.
- **A loader silently serving stale data is almost always a missing `loaderDeps`.** Changing `?page=2` won't re-run the loader unless `loaderDeps: ({ search }) => ({ page: search.page })` declares it.
- **`useParams()` typing "breaks" in shared components.** Without `from`, it unions all routes' params. Use `from`, `Route.useParams()` (same file), or `getRouteApi(path)` (split file).
- **Zod adapter version trap.** For **Zod v3** wrap with `zodValidator` from `@tanstack/zod-adapter`; for **Zod v4** the adapter is unnecessary — pass the schema straight to `validateSearch`. The old `@tanstack/router-zod-adapter` package is deprecated.
- **Deferred data: return the raw promise, don't `await` it.** Current docs return an *unawaited* promise from the loader and consume it via `<Await>` / `useAwaited`. The standalone `defer()` helper is mainly for SSR/streaming serialization (Start), not required in an SPA — see `references/search-and-loaders.md`.
- **`useSuspenseQuery` with no loader prefetch suspends on first paint.** The point of `ensureQueryData` in the loader is that the component's `useSuspenseQuery` is a cache hit. Skip the loader and you reintroduce the waterfall the loader exists to remove.

## Anti-patterns

- **"I'll fetch in a `useEffect` instead of a loader."** That reintroduces the render-then-fetch waterfall and kills preloading — the loader is the point.
- **"I'll guard the route by redirecting inside the component."** Flash of protected content + an extra render. Guard in `beforeLoad`.
- **"I'll skip `validateSearch` and read `useSearch()` raw."** That is an unvalidated `any` from the URL; a malformed URL becomes a runtime crash.
- **"I'll teach the full TanStack Query cache/mutation API here since I'm integrating it."** Scope bleed — frame it through the route and point at `tanstack-query`.
- **"I'll document TanStack Start SSR/streaming because the router supports it."** Start is a separate product (the downstream consumer); fence it out.

## Output

This skill produces working TanStack Router code: a `vite.config.ts` plugin entry, a `router.tsx` (`createRouter` + `Register`), `RouterProvider` wiring, route modules (file-based primary, code-based supported), typed navigation and hooks, validated search params, loaders wired to TanStack Query, and a memory-history test harness. The abstract consumer is the engineer or coding agent standing up routing in a React SPA, and the sibling component-testing workflow that reuses the test harness.

## Related

- `tanstack-query` — **canonical** source for TanStack Query mechanics (query keys, `queryOptions`, mutations, cache tuning). This skill references it for everything at the loader/context seam and does not duplicate it.
- `vite` — the dev server + bundler that runs the `@tanstack/router-plugin/vite` plugin generating `routeTree.gen.ts`.
- `react-component-testing` (sibling) — consumes the router **test harness** this skill owns (Step 7 / `references/auth-and-testing.md`).
- `typescript-typecheck` — the `Register` augmentation + typed hooks assume a strict `tsconfig`; the route-tree type checking is what `tsc` enforces.
- **Boundaries (named, not taught):** **TanStack Start** (SSR/streaming full-stack framework — downstream consumer); **React Router** (`react-router` / Remix — the alternative not chosen for this stack).

## Progressive disclosure

Heavy content lives in `references/`, loaded on demand:

- `references/routing-approaches.md` — load when choosing or implementing routing structure: the full **file-naming conventions** table (`__root`, `index`, `$param`, `_pathless`, `(group)`, `$` splat, dot-notation, trailing-underscore un-nesting) AND the complete **code-based** approach (`createRoute` + `getParentRoute` + `addChildren` + manual `createRouter`), with a when-to-use comparison.
- `references/search-and-loaders.md` — load for search params + data loading depth: `validateSearch` with pluggable validators (Zod adapter worked example, Valibot/custom noted), reading/updating search, parent→child inheritance, custom serialization, search middleware (`retainSearchParams`/`stripSearchParams`); loaders, `loaderDeps`, deferred data (raw-promise + `Await`), parallel loading, context loading.
- `references/navigation-and-splitting.md` — load for navigation + bundle work: `Link` options, `useNavigate`, `redirect`, `useBlocker`, code-splitting (`createLazyFileRoute` / `autoCodeSplitting`), preloading (`defaultPreload` values, `preloadDelay`, stale times), scroll restoration, route masking.
- `references/auth-and-testing.md` — load for auth patterns or testing: `createRootRouteWithContext`, the pathless `_authenticated` layout, `beforeLoad` redirect guards, `notFound()`, head/meta; AND the full router **test harness** (memory-history factory, file-based-tree variant, awaiting router readiness).
- `references/query-integration.md` — load for the TanStack Query seam: the `ensureQueryData` + `useSuspenseQuery` handshake, await-vs-defer, the `queryOptions` factory, invalidation-after-mutation via `router.invalidate()`, `staleTime`/`gcTime`/`defaultPreloadStaleTime` — all framed through routing and cross-referencing the canonical `tanstack-query` skill.
- `references/sources.md` — research provenance (official `tanstack.com/router` doc pages + npm versions verified at forge).

This skill ships no `scripts/` or `assets/`.

## Body budget

- `description` ≤ 1,024 chars (respected).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; the long surface lives in `references/`.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k, error >50k.
