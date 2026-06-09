# Authenticated routes, not-found, head/meta, and the router test harness

> Load for auth-guard patterns, not-found/head handling, and — importantly — the **router test harness** that the sibling component-testing skill consumes. This skill OWNS the harness.

## Authenticated routes

The pattern: a **typed router context** carries auth state; a **pathless `_authenticated` layout** guards a whole subtree in `beforeLoad`; child routes under it are reachable only when authenticated. Guards live in `beforeLoad`, never in components.

### 1. Typed context at the root

```tsx
// routes/__root.tsx
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'

interface RouterContext {
  auth: { isAuthenticated: boolean; user: User | null }
  // queryClient?: QueryClient   // commonly combined — see query-integration.md
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: () => <Outlet />,
})
```
Provide the context when creating the router, and inject the live value through `RouterProvider`:
```tsx
const router = createRouter({ routeTree, context: { auth: undefined! } })

function App() {
  const auth = useAuth()                       // your auth hook/store
  return <RouterProvider router={router} context={{ auth }} />
}
```

### 2. The pathless `_authenticated` guard

```tsx
// routes/_authenticated.tsx  (pathless layout — no URL segment)
import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
  },
})

// routes/_authenticated/dashboard.tsx  →  /dashboard (only when authed)
export const Route = createFileRoute('/_authenticated/dashboard')({
  component: Dashboard,
})
```
The login route reads `search.redirect` and navigates back after a successful login. `beforeLoad` runs before any child loader, so protected loaders never fire for an unauthenticated user. (Code-based equivalent: a pathless layout route with an `id` instead of a `path` — see `routing-approaches.md`.)

## Not-found handling

`notFound()` throws a special error caught by the nearest `notFoundComponent` (it bubbles up the tree if unhandled). Distinct from error boundaries — it is specifically for 404s.
```tsx
import { createFileRoute, notFound } from '@tanstack/react-router'

export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.postId)
    if (!post) throw notFound()                 // or notFound({ data: {...} }) to pass context
    return post
  },
  notFoundComponent: () => <p>No such post.</p>,
})
```
Set a global fallback on the router: `createRouter({ routeTree, defaultNotFoundComponent: () => <NotFound /> })`. A catch-all splat route (`routes/$.tsx`) can handle truly unknown paths.

## Head / meta management

Manage document title/meta/links per route via the `head` option. It can read `loaderData`:
```tsx
export const Route = createFileRoute('/posts/$postId')({
  loader: ({ params }) => fetchPost(params.postId),
  head: ({ loaderData }) => ({
    meta: [
      { title: loaderData.title },
      { name: 'description', content: loaderData.excerpt },
    ],
    links: [{ rel: 'canonical', href: `/posts/${loaderData.id}` }],
  }),
})
```
(Rendering the collected tags to the document is automatic in the router/Start integration.)

## The router test harness (this skill owns it)

To render a routed component in a test environment with no browser URL, build an **in-memory** router and wrap with `RouterProvider`. The sibling `react-component-testing` skill references this harness rather than redefining it.

### Code-based test router factory

```tsx
import { render, screen } from '@testing-library/react'
import {
  createMemoryHistory,
  createRootRoute,
  createRoute,
  createRouter,
  RouterProvider,
} from '@tanstack/react-router'

function renderAtPath(initialPath: string, Component: () => JSX.Element) {
  const rootRoute = createRootRoute()
  const route = createRoute({ getParentRoute: () => rootRoute, path: '/posts/$postId', component: Component })
  const routeTree = rootRoute.addChildren([route])

  const router = createRouter({
    routeTree,
    history: createMemoryHistory({ initialEntries: [initialPath] }),
  })

  render(<RouterProvider router={router} />)
  return router
}

// test
it('renders the post', async () => {
  renderAtPath('/posts/42', () => <div>post 42</div>)
  expect(await screen.findByText('post 42')).toBeInTheDocument()  // findBy* awaits route resolution
})
```

`createMemoryHistory({ initialEntries: ['/posts/42'] })` sets the starting location (and optional history stack) without touching `window.location`. Because the router resolves matches (and loaders) asynchronously, assert with Testing Library's `findBy*` / `waitFor` rather than `getBy*`.

### File-based tree variant

When testing against a generated route tree, import it and pass it straight to `createRouter`:
```tsx
import { routeTree } from '../routeTree.gen'
const router = createRouter({ routeTree, history: createMemoryHistory({ initialEntries: ['/posts/42'] }) })
render(<RouterProvider router={router} />)
```

### Driving navigation + awaiting readiness

```tsx
const router = renderAtPath('/', App)
await router.navigate({ to: '/posts/$postId', params: { postId: '42' } })
// If you need the router fully loaded before asserting (e.g. loaders run):
await router.load()
```
`router.navigate(...)` performs an in-memory navigation; `await router.load()` resolves the current match's pending loaders. Provide a typed context in tests the same way as production — `createRouter({ routeTree, context: { queryClient: testQueryClient } })` — to exercise loaders that read context.

> The RTL / MSW / vitest-axe component-test *authoring* (mocking network, accessibility assertions, render utilities) belongs to the `react-component-testing` skill. This skill owns only the router-specific harness above.
