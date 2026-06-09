# Routing approaches — file-based conventions + code-based

> Load when choosing or implementing the routing structure. The SKILL.md body uses **file-based** as the primary worked path; this file gives the full file-naming reference AND the complete **code-based** approach.

## File-based routing (the recommended default)

The `@tanstack/router-plugin/vite` plugin (`tanstackRouter`) watches `src/routes/` and generates `src/routeTree.gen.ts`. You author route modules; the plugin assembles the tree. A route module exports `const Route = createFileRoute('/url/path')({ ...options })` — the **path string comes first**, then the options object. The root is `createRootRoute({...})` (or `createRootRouteWithContext<T>()({...})`).

### File-naming conventions

The router supports both **flat** (dot-delimited filenames) and **directory** (nested folders) styles; you can mix them. The conventions:

| Pattern | Meaning | Example file | Matches |
|---|---|---|---|
| `__root.tsx` | Root layout, wraps all routes | `routes/__root.tsx` | (every route) |
| `index.tsx` | Index route (exact parent path) | `routes/index.tsx` | `/` |
| `about.tsx` | Static segment | `routes/about.tsx` | `/about` |
| `$param` | Dynamic path param | `routes/posts.$postId.tsx` | `/posts/123` |
| folder + `index` | Nested index | `routes/posts/index.tsx` | `/posts` |
| `_pathless` | Pathless layout (groups children under shared layout/logic, **no URL segment**) | `routes/_auth.tsx` + `routes/_auth/dashboard.tsx` | `/dashboard` (under the `_auth` layout) |
| `(group)` | Route group (organizational folder, **no URL impact**) | `routes/(marketing)/about.tsx` | `/about` |
| `$` | Splat / catch-all | `routes/files/$.tsx` | `/files/*` (read via `_splat`) |
| `.` (dot) | Nesting in a flat filename | `routes/posts.$postId.edit.tsx` | `/posts/123/edit` |
| trailing `_` | **Non-nested** route — opts a child OUT of its parent's layout | `routes/posts_.$postId.tsx` | `/posts/123` but NOT wrapped by `posts.tsx`'s layout |

Notes verified against current docs:
- **Pathless** routes use a leading `_` and exist to share a layout/`beforeLoad`/context across children without adding a URL segment (the `_authenticated` pattern in `auth-and-testing.md`).
- **Route groups** use `(parens)` purely to organize files; they do not affect the URL.
- The **trailing underscore** (`posts_`) is the "un-nest" / non-nested escape — the segment still appears in the URL but the route is detached from the parent layout. To escape a literal trailing underscore in a segment, the current docs use a bracketed-escape form (`/posts[_].tsx`) under the upgraded non-nested-routes behavior — check your version's file-naming page (`references/sources.md`).
- `indexToken` and `routeFileIgnorePrefix`/`routeFilePrefix` are plugin options that let you rename the `index` token or ignore files; defaults match the table above.

### Virtual routes (lazy-only files)

If a route has **only** a component (no `loader`/`beforeLoad`/`validateSearch`/`loaderDeps`), you can skip the "critical" main file entirely and ship just `route.lazy.tsx` (`createLazyFileRoute`). The plugin auto-generates a minimal virtual route to anchor it. You need a non-lazy main file only when the route carries critical config (loader, beforeLoad, validateSearch, loaderDeps, context). See `navigation-and-splitting.md` for the lazy split.

## Code-based routing (full treatment)

Use code-based routing when you cannot run the bundler plugin (no build-step codegen, a non-standard bundler, or a deliberately hand-assembled tree). It is fully type-safe and first-class — the only loss is the file-convention ergonomics and auto code-splitting.

You build the tree explicitly: a root route, child routes that declare their parent via `getParentRoute`, then `addChildren` to assemble, then `createRouter`.

```tsx
import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from '@tanstack/react-router'
import { z } from 'zod'
import { zodValidator } from '@tanstack/zod-adapter'

const rootRoute = createRootRoute({
  component: () => <Outlet />,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

const postsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'posts',                         // child path segment (no leading slash needed under a parent)
  component: PostsLayout,                 // renders an <Outlet/> for its children
})

const postRoute = createRoute({
  getParentRoute: () => postsRoute,       // nests under /posts
  path: '$postId',
  validateSearch: zodValidator(z.object({ tab: z.enum(['body', 'comments']).catch('body') })),
  loader: async ({ params }) => fetchPost(params.postId),
  component: PostComponent,
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  postsRoute.addChildren([postRoute]),
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
```

### Reading typed data in code-based routes

The route objects ARE the type source — call their hooks directly:

```tsx
function PostComponent() {
  const { postId } = postRoute.useParams()      // typed { postId: string }
  const { tab } = postRoute.useSearch()         // typed
  const post = postRoute.useLoaderData()        // typed to the loader return
  return <article data-tab={tab}>{post.title}</article>
}
```

From a component that does not import the route, use `getRouteApi('/posts/$postId')` (the route id is the same string you'd pass to `from`). For a typed router context use `createRootRouteWithContext<{ queryClient: QueryClient }>()` as the root instead of `createRootRoute` (see `query-integration.md`).

### Pathless / layout routes in code

A layout route with no path of its own (the code-based equivalent of `_pathless`) uses `createRoute({ getParentRoute, id: 'layout', component: LayoutWithOutlet })` and the children declare `getParentRoute: () => layoutRoute`. The `id` (instead of `path`) marks it pathless.

## When to use which

| | File-based | Code-based |
|---|---|---|
| Default? | Yes (TanStack's recommendation) | Only when codegen is unavailable |
| Route tree | Auto-generated `routeTree.gen.ts` | Hand-assembled `addChildren` |
| Auto code-splitting | Yes (plugin `autoCodeSplitting`) | Manual `.lazy()` only |
| Type safety | Full | Full |
| Build step | Requires the bundler plugin | None needed |

Both share the same option surface (`loader`, `validateSearch`, `beforeLoad`, etc.) and the same typed hooks — the difference is purely how the tree is assembled.
