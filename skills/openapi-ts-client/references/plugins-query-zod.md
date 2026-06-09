# Plugins — TanStack Query + Zod

Load when wiring the generated query hooks or Zod schemas.

## TanStack Query plugin

The plugin string is **framework-specific** (it mirrors the TanStack package):

- React → `@tanstack/react-query`
- Vue → `@tanstack/vue-query`, Svelte → `@tanstack/svelte-query`, Solid → `@tanstack/solid-query`, Angular → `@tanstack/angular-query-experimental`, Preact → `@tanstack/preact-query`.

### Generated exports (naming convention)

For an operation `getPetById` it generates:

| Suffix | Example | Use |
|---|---|---|
| `Options` | `getPetByIdOptions()` | spread into `useQuery` |
| `QueryKey` | `getPetByIdQueryKey()` | the query key (for invalidation) |
| `InfiniteOptions` | `getPetByIdInfiniteOptions()` | `useInfiniteQuery` |
| `InfiniteQueryKey` | `getPetByIdInfiniteQueryKey()` | infinite query key |
| `Mutation` | `addPetMutation()` | spread into `useMutation` |

### Usage

```ts
const query = useQuery({
  ...getPetByIdOptions({ path: { petId: 1 } }),
});
```

The generated `Options`/`Mutation` helpers carry the typed `queryFn`/`mutationFn`, the right query key, and the param typing — you spread them into the TanStack hook.

### Composition — defer to the `tanstack-query` skill

This skill only **generates** the hooks. The patterns for *using* them — `QueryClient` setup, `useMutation` + `invalidateQueries` after a mutation, `staleTime`/cache config, optimistic updates, the `QueryClientProvider` — belong to the `tanstack-query` skill. Generate the helpers here; reach for that skill for the query/cache idioms. Invalidate with the generated `<op>QueryKey()` so keys stay consistent with the contract.

## Zod plugin

Plugin string: `zod`. It generates Zod schemas for request/response shapes from the spec, letting you validate at the API boundary (e.g. validating untrusted external data, or asserting a response in a test) without hand-writing schemas. Because both the SDK types and the Zod schemas come from the same contract, they stay consistent. Use the generated schemas at trust boundaries; rely on the generated TypeScript types for compile-time safety elsewhere.
