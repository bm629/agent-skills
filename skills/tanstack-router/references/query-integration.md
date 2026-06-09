# TanStack Query integration (framed through routing)

> Load for the loader↔query seam. **Everything here is framed through routing.** For TanStack Query mechanics themselves — query keys, `queryOptions`, mutations, cache internals, infinite/paginated queries, `staleTime`/`gcTime` semantics — the **canonical source is the `tanstack-query` skill**. This file covers only how routing reaches into Query, and cross-references `tanstack-query` at each overlap. It does **not** teach standalone query patterns divorced from routing.

## Why combine them

TanStack Router's loaders give you *when* (fetch before render, preload on intent, cancel on navigation); TanStack Query gives you *caching* (dedupe, background refetch, stale-while-revalidate, mutation invalidation). Combined, the route loader **primes** the Query cache, and the component **reads** it — so the component renders with data already present and Query keeps it fresh afterward.

## The handshake: `ensureQueryData` in the loader → `useSuspenseQuery` in the component

The canonical pattern (per the official Router↔Query integration docs):

1. Define a `queryOptions` factory (this is a **TanStack Query** construct — see the `tanstack-query` skill for `queryOptions` semantics):
   ```tsx
   import { queryOptions } from '@tanstack/react-query'
   export const postQueryOptions = (postId: string) =>
     queryOptions({ queryKey: ['posts', postId], queryFn: () => fetchPost(postId) })
   ```
2. In the route loader, `ensureQueryData` it via the `queryClient` from router context — this awaits the data if it's missing/stale and primes the cache:
   ```tsx
   export const Route = createFileRoute('/posts/$postId')({
     loader: ({ context: { queryClient }, params }) =>
       queryClient.ensureQueryData(postQueryOptions(params.postId)),
     component: Post,
   })
   ```
3. In the component, read the **same** `queryOptions` with `useSuspenseQuery` — a cache hit (no refetch), and the component subscribes for background updates:
   ```tsx
   function Post() {
     const { postId } = Route.useParams()
     const { data: post } = useSuspenseQuery(postQueryOptions(postId))
     return <article>{post.title}</article>
   }
   ```

`ensureQueryData` returns cached data if present, fetches+caches+awaits if not, and **throws** on error (caught by the route's `errorComponent`). Using the same `queryOptions` object in both places is what makes the loader's prime and the component's read line up.

## Wiring the `queryClient` through router context

The loader reaches `queryClient` through the typed router context:
```tsx
// __root.tsx
export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({ component: () => <Outlet /> })

// router.tsx
const queryClient = new QueryClient()
const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultPreloadStaleTime: 0,   // let TanStack Query own freshness (see below)
})
```
Wrap the app with `QueryClientProvider` (a TanStack Query concern — see the `tanstack-query` skill) around `RouterProvider`, or use the router's `Wrap`/SSR-query integration helper. The same `queryClient` instance must be the one in context and the one the provider supplies.

## await-in-loader vs. defer-to-hook

A per-route decision about *which* data blocks navigation:

- **Await in the loader** (`await queryClient.ensureQueryData(...)`): the navigation waits until the data is cached. Use for **critical** data the page can't render without. The component's `useSuspenseQuery` is then a guaranteed cache hit.
- **Defer to the hook** (don't await in the loader; let the component's `useQuery` fetch): the route renders immediately and the component shows its own loading state. Use for **non-critical** data. You can also kick it off in the loader without awaiting (`queryClient.prefetchQuery(...)`) so the fetch starts early but doesn't block — then read it with `useQuery` (note `useQuery`, not `useSuspenseQuery`, since it may still be pending).

This mirrors the router's own deferred-data idea (raw-promise + `<Await>`, see `search-and-loaders.md`), but expressed through the Query cache.

## `defaultPreloadStaleTime` — who owns freshness

Set `defaultPreloadStaleTime: 0` on the router when TanStack Query manages caching. The router otherwise applies its *own* preload freshness window on top of Query's, which double-caches and can serve data the router thinks is fresh but Query would refetch. With `0`, the router defers entirely to Query's `staleTime`. (Configure Query's `staleTime`/`gcTime` in the `QueryClient` defaults — a `tanstack-query` concern; this is only the router-side flag that hands ownership over.)

## Invalidation after a mutation (tied to navigation)

After a mutation, you usually want both the Query cache **and** the route's loaded data refreshed:

- Invalidate the affected Query keys via the `queryClient` (mutation mechanics + `invalidateQueries` belong to the `tanstack-query` skill).
- Invalidate the **router** so it re-runs the current route's loaders with the now-fresh cache: `router.invalidate()`. This is the routing-side half — it re-pulls loader data after the cache changed.

```tsx
const router = useRouter()
const queryClient = useQueryClient()
const mutation = useMutation({
  mutationFn: updatePost,
  onSuccess: async () => {
    await queryClient.invalidateQueries({ queryKey: ['posts'] })  // Query cache — see tanstack-query
    await router.invalidate()                                     // re-run route loaders
  },
})
```
An `errorComponent` can also call `router.invalidate()` to retry a failed loader.

## Boundary restated

- **In scope here:** `ensureQueryData`/`prefetchQuery` in loaders, `useSuspenseQuery`/`useQuery` reading loader-primed data, `queryClient` via router context, `defaultPreloadStaleTime`, and `router.invalidate()` after a mutation — i.e. Query **as reached through a route**.
- **Out of scope (use `tanstack-query`):** `queryOptions`/`queryKey` design, mutation patterns, optimistic updates, infinite/paginated queries, `staleTime`/`gcTime` semantics, `QueryClientProvider` setup, devtools — the canonical query mechanics. Reach for that skill for any query concern not anchored to a route.
