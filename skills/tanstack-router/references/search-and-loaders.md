# Search params + data loading (in depth)

> Load for the full search-param and loader surface. The SKILL.md body shows the basics; this file covers validators, inheritance, serialization, middleware, `loaderDeps`, deferred data, parallel loading, and context loading.

## Search params

Search params are **first-class typed URL state** in TanStack Router: a route declares a `validateSearch` schema, the router parses/validates the raw URL search on every navigation, and `useSearch()` returns the typed, validated object. Treat them as user-controlled input — always validate.

### `validateSearch` with a pluggable validator

`validateSearch` accepts any function `(raw: Record<string, unknown>) => TSearch`. That makes the validator pluggable:

**Zod (worked example).** The adapter story is version-sensitive:
- **Zod v3** — wrap with `zodValidator` from the dedicated `@tanstack/zod-adapter` package:
  ```tsx
  import { z } from 'zod'
  import { zodValidator } from '@tanstack/zod-adapter'

  const search = z.object({
    page: z.number().min(1).catch(1),
    sort: z.enum(['date', 'title']).catch('date'),
    q: z.string().optional(),
  })

  export const Route = createFileRoute('/posts')({
    validateSearch: zodValidator(search),
  })
  ```
- **Zod v4** — the adapter is **no longer required**; pass the schema (or `(s) => schema.parse(s)`) directly to `validateSearch`. (The older `@tanstack/router-zod-adapter` package is deprecated in favor of `@tanstack/zod-adapter`.)

Use `.catch(default)` (Zod) so a malformed URL falls back instead of throwing.

**Valibot.** Supported via its own adapter (`valibotValidator` from `@tanstack/valibot-adapter`) — same shape as the Zod adapter.

**Plain function (no library).** Fully valid — return a typed object:
```tsx
validateSearch: (search: Record<string, unknown>) => ({
  page: Number(search.page) || 1,
  sort: search.sort === 'title' ? 'title' : 'date',
}),
```

### Reading + updating

```tsx
const { page, sort } = Route.useSearch()                 // in the route file
const search = useSearch({ from: '/posts' })             // elsewhere, typed via `from`

// Update with a functional updater that PRESERVES other params:
navigate({ to: '.', search: (prev) => ({ ...prev, page: prev.page + 1 }) })
<Link to="/posts" search={(prev) => ({ ...prev, sort: 'title' })}>By title</Link>
```

A common pattern: when a filter changes, reset `page` to 1 inside the updater.

### Parent → child inheritance

Search params validated by a parent route are inherited by (and merged into the typed search of) child routes. A child's `validateSearch` extends, rather than replaces, the parent's — so a nested route sees both its own and its ancestors' validated params.

### Custom serialization

By default the router JSON-encodes search values. Override globally on `createRouter` to control the URL shape:
```tsx
const router = createRouter({
  routeTree,
  search: {
    // e.g. a flat/compact encoder instead of JSON
    serialize: (searchObj) => myStringify(searchObj),
    parse: (searchStr) => myParse(searchStr),
    strict: true,   // reject unknown params
  },
})
```
Route-level `validateSearch` still runs after parsing. Mind URL length (~2000 chars) and bookmarkability when choosing an opaque encoder.

### Search middleware

Apply cross-cutting transforms to a route's search via the `search.middlewares` array. Two built-ins from `@tanstack/react-router`:
- **`retainSearchParams(keysOrTrue)`** — keep listed params (or all, if `true`) across navigations that would otherwise drop them.
- **`stripSearchParams(defaults)`** — remove params whose value deep-equals the given default, keeping URLs clean.

```tsx
import { retainSearchParams, stripSearchParams } from '@tanstack/react-router'

export const Route = createFileRoute('/posts')({
  validateSearch: zodValidator(search),
  search: {
    middlewares: [
      retainSearchParams(['q']),
      stripSearchParams({ page: 1, sort: 'date' }),
    ],
  },
})
```
Middlewares chain in order.

## Data loading

### Route loaders

A `loader` runs during route matching, **before** the component renders, so data is ready on mount and is preloadable. The loader receives `{ params, context, deps, abortController, cause, preload, location }`.

```tsx
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, abortController }) => {
    const res = await fetch(`/api/posts/${params.postId}`, { signal: abortController.signal })
    return res.json()
  },
  component: () => <article>{Route.useLoaderData().title}</article>,
})
```
Use `abortController.signal` so stale preloads/navigations cancel their fetches. `cause` is `'enter' | 'stay' | 'preload'`; `preload` is a boolean for lighter preload-time work.

### `loaderDeps` — re-run on search change

A loader does **not** re-run when search params change unless you declare the dependency. `loaderDeps` maps the current search to the loader's `deps`:
```tsx
export const Route = createFileRoute('/posts')({
  loaderDeps: ({ search }) => ({ page: search.page, sort: search.sort }),
  loader: async ({ deps }) => fetchPosts(deps),
})
```
Omitting `loaderDeps` while the loader reads `search` is the #1 stale-data bug.

### Deferred data (raw promise + `Await`)

To stream non-critical data, **return the promise unawaited** from the loader and resolve it in the component with `<Await>` (or the `useAwaited` hook) inside `<Suspense>`. Fast data is awaited; slow data is handed off as a pending promise.

```tsx
export const Route = createFileRoute('/dashboard')({
  loader: async () => {
    const stats = await fetchStats()             // critical — awaited
    const feed = fetchActivityFeed()             // non-critical — NOT awaited
    return { stats, feed }
  },
  component: Dashboard,
})

function Dashboard() {
  const { stats, feed } = Route.useLoaderData()
  return (
    <>
      <Stats data={stats} />
      <Suspense fallback={<Spinner />}>
        <Await promise={feed}>{(data) => <Feed data={data} />}</Await>
      </Suspense>
    </>
  )
}
```
The standalone `defer()` helper still exists but in current docs is primarily about SSR/streaming serialization (TanStack Start); in an SPA, returning a raw promise is the idiomatic path.

### Parallel loading

Nested route loaders run **in parallel**, not as a waterfall — a child loader does not wait for its parent's loader. Within a single loader, parallelize independent fetches with `Promise.all`. Avoid creating artificial waterfalls (e.g. sequential `await`s in `beforeLoad`).

### Context-based loading

Inject shared dependencies (a `queryClient`, an auth object, an API client) via the **router context**, then read them in any loader/`beforeLoad`:
```tsx
// root: createRootRouteWithContext<{ queryClient: QueryClient }>()(...)
// createRouter({ routeTree, context: { queryClient } })

export const Route = createFileRoute('/posts')({
  loader: ({ context: { queryClient } }) => queryClient.ensureQueryData(postsQueryOptions),
})
```
`beforeLoad` can also **return** an object that extends the context for that route and its descendants. See `query-integration.md` for the full TanStack Query seam and `auth-and-testing.md` for the auth-context pattern.
