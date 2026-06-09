# Navigation, code-splitting, preloading, scroll, masking

> Load for the full navigation surface and bundle/preload work. SKILL.md Step 5 shows the essentials; this file is the complete reference.

## Navigation

### `Link`

`<Link>` renders a real `<a href>` — it supports middle-click / cmd-click / "open in new tab", is announced as a link to screen readers, is crawlable, and preloads on intent. Prefer it over `useNavigate` for user-initiated navigation.

Typed props:
```tsx
<Link
  to="/posts/$postId"            // typed against the route tree
  params={{ postId: '123' }}     // required + typed for dynamic segments
  search={{ tab: 'comments' }}   // typed to the route's validated search (object or (prev)=>... updater)
  hash="section-2"
  activeProps={{ className: 'active', 'aria-current': 'page' }}
  inactiveProps={{ className: 'inactive' }}
  activeOptions={{ exact: true }}  // active only on exact match
  preload="intent"                 // override the router default for this link
  preloadDelay={100}
  mask={{ to: '/posts' }}          // see Route masking below
>
  Post 123
</Link>
```
Render-prop form for custom active UI:
```tsx
<Link to="/posts">{({ isActive }) => <span className={isActive ? 'on' : 'off'}>Posts</span>}</Link>
```

### `useNavigate` (imperative)

For side effects (after a form submit, after login). Returns a `navigate` function:
```tsx
const navigate = useNavigate()
navigate({ to: '/posts', search: { page: 1 } })
navigate({ to: '/posts', replace: true })                 // replace history entry
navigate({ to: '.', search: (prev) => ({ ...prev, page: 2 }) })  // relative, preserve search
```
For a render-time client redirect, the `<Navigate>` component is also available.

### `redirect` (guards)

Throw `redirect(...)` from `beforeLoad` or `loader` — never navigate from a component for a guard (it flashes content):
```tsx
import { redirect } from '@tanstack/react-router'
throw redirect({ to: '/login', search: { redirect: location.href } })
```
`redirect` accepts the same typed `to`/`params`/`search` as navigation, plus an optional status code for SSR. See `auth-and-testing.md` for the `_authenticated` guard pattern.

### Navigation blocking — `useBlocker`

Block navigation away from a dirty form. The current API takes `shouldBlockFn` (returns `boolean | Promise<boolean>`) and an optional `withResolver`:
```tsx
import { useBlocker } from '@tanstack/react-router'

// Simplest: block with a native confirm inside shouldBlockFn
useBlocker({ shouldBlockFn: () => isDirty && !window.confirm('Leave?') })

// Custom UI: withResolver gives you proceed/reset + a status
const { status, proceed, reset } = useBlocker({
  shouldBlockFn: () => isDirty,
  withResolver: true,
})
if (status === 'blocked') {
  return (
    <Dialog>
      <button onClick={proceed}>Leave</button>
      <button onClick={reset}>Stay</button>
    </Dialog>
  )
}
```
`shouldBlockFn` receives `{ current, next, action }` (the from/to locations + history action), so you can block only specific transitions. `status` is `'blocked' | 'idle'`.

## Code splitting

### Automatic (preferred with the plugin)

Enable `autoCodeSplitting: true` in the bundler plugin and the router splits each route's **non-critical** config (component, pending/error/notFound components) from its **critical** config (path, loader, beforeLoad, validateSearch, loaderDeps) automatically — no `.lazy` files needed.
```ts
tanstackRouter({ target: 'react', autoCodeSplitting: true })
```
Newer plugin versions also expose `defaultBehavior` / `splitBehavior` to customize how routes are grouped into chunks (by `routeId`). Check your version's automatic-code-splitting docs.

### Manual (`.lazy.tsx` / `createLazyFileRoute`)

When you cannot use auto-splitting, move the component into a sibling `route.lazy.tsx` using `createLazyFileRoute` (which accepts **only** component-related options); keep critical config in the main `route.tsx`:
```tsx
// posts.tsx — critical, eager
export const Route = createFileRoute('/posts')({ loader: () => fetchPosts() })

// posts.lazy.tsx — non-critical, lazy
import { createLazyFileRoute } from '@tanstack/react-router'
export const Route = createLazyFileRoute('/posts')({
  component: PostsPage,
  pendingComponent: PostsSkeleton,
  errorComponent: PostsError,
})
```
A component-only route can ship as **just** the `.lazy.tsx` (a virtual route is auto-generated — see `routing-approaches.md`). Code-based routes split via `.lazy()`:
```tsx
const r = createRoute({ getParentRoute: () => root, path: '/posts' })
  .lazy(() => import('./posts.lazy').then((m) => m.Route))
```
In a split component file, get type-safe hooks without importing the main route via `getRouteApi('/posts')`.

> **Keep the loader in the initial bundle.** Splitting the loader into its own chunk adds a network round-trip before data can be fetched, slowing the first load. Don't split loaders unless you have a specific reason.

## Preloading

Router-level defaults:
```tsx
const router = createRouter({
  routeTree,
  defaultPreload: 'intent',        // 'intent' | 'viewport' | 'render' | false
  defaultPreloadDelay: 50,         // ms to wait before preloading on intent
  defaultPreloadStaleTime: 30_000, // how long preloaded data stays fresh (set 0 when TanStack Query owns the cache)
})
```
| value | preload trigger | use for |
|---|---|---|
| `'intent'` | hover / focus | most links (default) |
| `'render'` | when the `Link` mounts | a near-certain next page |
| `'viewport'` | `Link` enters viewport | below-the-fold; mobile (no hover) |
| `false` | never | heavy, rarely-visited routes |

Override per-`Link` with the `preload` / `preloadDelay` props. Preloading runs the route's loader (and loads its code), so the click is near-instant.

## Scroll restoration

Enable on the router with `scrollRestoration: true` (restores scroll on back/forward). For full control, render the `<ScrollRestoration>` component (typically in `__root`) and optionally pass a custom `getKey={(location) => location.pathname}`.

## Route masking

Show one URL while routing to another — for modal/overlay routes that should have a shareable URL but render in-place. Per-navigation via the `mask` option:
```tsx
<Link to="/photos/$photoId" params={{ photoId: id }} mask={{ to: '/photos' }}>Open</Link>
navigate({ to: '/photos/$photoId', params: { photoId: id }, mask: { to: '/photos' } })
```
Or define reusable masks on the router so you don't repeat `mask` everywhere:
```tsx
import { createRouteMask, createRouter } from '@tanstack/react-router'
const photoMask = createRouteMask({
  routeTree,
  from: '/photos/$photoId',
  to: '/photos',
  params: true,
})
const router = createRouter({ routeTree, routeMasks: [photoMask] })
```
Masks are **client-side only**: a copied/shared URL is the real (unmasked) route, and direct navigation to the real URL bypasses the mask (shows the full page). The back button traverses history correctly.
