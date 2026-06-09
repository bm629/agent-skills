# tanstack-router

> Set up and use TanStack Router (`@tanstack/react-router`) in a Vite + React +
> TypeScript SPA — a fully type-safe client-side router where the route tree is
> the type source. Covers the bundler plugin (`tanstackRouter` from
> `@tanstack/router-plugin/vite`), the `createRouter` + `RouterProvider` +
> `Register` wiring, file-based routing (primary) and code-based (fully covered),
> validated search params, route loaders + the TanStack Query handshake,
> code-splitting, preloading, authenticated routes, route masking, and a
> memory-history test harness for routed components. The routing layer; TanStack
> Start (SSR) builds on top and is out of scope.

**Skill file:** [`skills/tanstack-router/SKILL.md`](../../skills/tanstack-router/SKILL.md)
**Version:** 1.0.0

## Purpose

TanStack Router's differentiator is end-to-end type safety: register the router via
TypeScript declaration merging and every `Link`/`navigate`/`useParams`/`useSearch`/
`useLoaderData` is checked against the real routes. This skill stands the router up,
wires routes type-safely, owns first-class search-param validation and route loaders
(including the loader↔TanStack-Query seam), and provides the test harness routed
components are rendered with. It is the routing layer — `tanstack-query` remains the
canonical source for query mechanics, `vite` runs the plugin, and TanStack Start (SSR)
is the downstream consumer, fenced out.

## When to activate

- ✅ Setting up routing in a Vite + React + TS SPA (or extending a TanStack Router app).
- ✅ Defining routes, typed navigation, validated search params, or route loaders.
- ✅ Wiring route loaders to TanStack Query (prefetch in loader, read in component).
- ✅ Writing a test that renders a routed component (needs the memory-history harness).

### When NOT to activate

- The project uses **React Router** (`react-router` / Remix) — a different router; this does not translate.
- You need **TanStack Start** SSR / server functions / streaming — Start is the downstream consumer, not taught.
- You need **TanStack Query mechanics divorced from routing** (cache config, mutations, infinite queries) — that's `tanstack-query`; this covers query only as reached through a route.

## Workflow

| Step | Does |
|---|---|
| 1 Plugin | `tanstackRouter({ target: 'react', autoCodeSplitting: true })` from `@tanstack/router-plugin/vite`, before `react()`; generates `routeTree.gen.ts`. |
| 2 Type-safe setup | `createRouter` + `RouterProvider` + the mandatory `Register` declaration merge. |
| 3 Root route | `createRootRoute` (or `createRootRouteWithContext<T>()` for a typed context). |
| 4 A worked route | File-based (primary): `createFileRoute('/path')({ validateSearch, loader, component })` + the in-file typed hooks; code-based fully covered in references. |
| 5 Navigation | `Link` (typed) for user nav; `useNavigate` for side effects; `throw redirect(...)` from `beforeLoad`. |
| 6 Loader↔data seam | `ensureQueryData` in the loader (via router-context `queryClient`) → `useSuspenseQuery` in the component. |
| 7 Test harness | `createMemoryHistory({ initialEntries })` + `createRouter` + `RouterProvider` (owned here; consumed by `react-component-testing`). |

## Hard rules it enforces

- **Always add the `Register` declaration merge** — without it the typed hooks degrade to unions and you lose compile-time route checking.
- **Put auth/redirect guards in `beforeLoad` (or `loader`), never in a component** — guarding in a component flashes protected content.
- **Use `loaderDeps` whenever the loader depends on search params** — otherwise the loader serves stale data on a search change.
- **Validate every search param via `validateSearch`** — search params are user-controlled URL input.
- **Keep query mechanics framed through routing** — cover Query only at the loader/context seam and cross-reference `tanstack-query` as canonical.

## Progressive disclosure (`references/`)

- `references/routing-approaches.md` — the full file-naming conventions table AND the complete code-based approach (`createRoute` + `getParentRoute` + `addChildren`), with a when-to-use comparison.
- `references/search-and-loaders.md` — `validateSearch` (pluggable validators; Zod v3 adapter vs v4 direct), reading/updating search, inheritance, serialization, middleware; loaders, `loaderDeps`, deferred data, parallel + context loading.
- `references/navigation-and-splitting.md` — `Link`/`useNavigate`/`redirect`/`useBlocker`, code-splitting (`createLazyFileRoute`/`autoCodeSplitting`), preloading, scroll restoration, route masking.
- `references/auth-and-testing.md` — authenticated routes (`createRootRouteWithContext` + `_authenticated` + `beforeLoad`), `notFound()`, head/meta, AND the full router test harness.
- `references/query-integration.md` — the loader↔query seam (`ensureQueryData` + `useSuspenseQuery`, await-vs-defer, `defaultPreloadStaleTime`, `router.invalidate()`), framed through routing and cross-referencing `tanstack-query`.
- `references/sources.md` — research provenance (official `tanstack.com/router` doc pages + npm versions).

## Limitations

- **`@tanstack/react-router` v1** (rolling, semver-minor); API confirmed against the official docs at forge — treat exact option names as version-pinnable (the trailing-underscore literal-escape file form and the plugin `defaultBehavior`/`splitBehavior` options are version-sensitive, flagged in-skill).
- **SPA client-side routing only** — TanStack Start SSR/streaming is out of scope.
- **Query coverage is routing-framed** — `tanstack-query` is canonical for query mechanics; this does not duplicate it.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
