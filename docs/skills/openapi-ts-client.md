# openapi-ts-client

> Generate a typed TypeScript client from an OpenAPI 3.1 contract — e.g. a
> FastAPI `/openapi.json` — with `@hey-api/openapi-ts`: typed models, a typed
> SDK (one function per operation), TanStack Query hooks, and Zod schemas,
> regenerated from the spec rather than hand-written. Covers the
> `openapi-ts.config.ts` config, the fetch/axios/next clients, the
> tanstack-query + zod plugins, the regenerate-and-drift-check workflow, and the
> FastAPI `operationId` fix. Defers TanStack Query *usage* to `tanstack-query`.

**Skill file:** [`skills/openapi-ts-client/SKILL.md`](../../skills/openapi-ts-client/SKILL.md)
**Version:** 1.0.0

## Purpose

Keeps a frontend's API client in lock-step with the backend contract by
generating it from the OpenAPI spec instead of hand-maintaining it. The contract
is the single source of truth; the client is a build artifact you regenerate. It
is the contract-consumption layer between an OpenAPI/FastAPI backend and a
TypeScript/React frontend — and it deliberately does not re-teach TanStack Query
*usage* (cache, invalidation, `QueryClient`): it generates the hooks, the
`tanstack-query` skill governs how they're used.

## When to activate

- ✅ Generating a typed TS client/SDK from a FastAPI (or any OpenAPI 3.1) `/openapi.json`.
- ✅ Adding generated TanStack Query hooks or Zod request/response schemas off a spec.
- ✅ Replacing a hand-written or hand-maintained API client with a generated one.
- ✅ Setting up the regenerate-on-contract-change workflow + a CI drift check.

### When NOT to activate

- TanStack Query *usage* patterns (caching/invalidation/query keys) — use the `tanstack-query` skill.
- Authoring the backend, the OpenAPI spec, or Pydantic models — use the `fastapi` / `pydantic-v2` skills.

## Workflow

| Step | Does |
|---|---|
| 1 Install | `npm install @hey-api/openapi-ts -D -E`; clients ship bundled (v0.73.0+) — no separate client install |
| 2 Configure | `openapi-ts.config.ts` via `defineConfig({ input, output, plugins })`; input = the FastAPI `/openapi.json` URL or a saved spec |
| 3 Generate | a `package.json` `gen:api` script running `openapi-ts` (one-shot: `npx @hey-api/openapi-ts -i <input> -o <output>`) |
| 4 Consume SDK | `const { data, error } = await op({ path, query, body })`; `throwOnError: true` to throw instead |
| 5 Hooks + Zod | spread generated `<op>Options()` / `<op>Mutation()` into TanStack Query; generated `zod` schemas validate at the boundary |
| 6 FastAPI + regen | `generate_unique_id_function` for clean method names; regenerate + a `git diff --exit-code` CI drift check |

## Hard rules it enforces

- **Never hand-edit generated files** — they're overwritten; customize via config/plugins or wrap the SDK.
- **The OpenAPI contract is the single source** — regenerate on change; enforce with the CI drift check.
- **Pin the generator version** (`-E`) — hey-api is pre-1.0 (0.x) and moves fast.
- **Generate, don't hand-write** an API client off a spec.

## Progressive disclosure (`references/`)

- `references/configuration.md` — the full `openapi-ts.config.ts` schema (`input`/`output`/`plugins`), options, CLI.
- `references/clients.md` — fetch/axios/next transports in depth, runtime config (`setConfig`/`createClientConfig`/per-call), the v0.73.0 client bundling, the SDK `{ data, error }` shape.
- `references/plugins-query-zod.md` — the generated TanStack Query export naming + usage, the Zod plugin, and the hand-off to `tanstack-query`.
- `references/fastapi-regen.md` — the FastAPI `operationId` fix, the regenerate script, the CI drift check, commit-vs-gitignore.
- `references/sources.md` — research provenance.

## Limitations

- **OpenAPI 3.1 / FastAPI focus** — targets the 3.1 contracts FastAPI ≥ 0.99 emits; reads 3.0 but that is not the sweet spot.
- **Generation, not usage** — generates the TanStack Query hooks; the `tanstack-query` skill owns the query/cache idioms.
- **Pre-1.0 tool** — verified against `@hey-api/openapi-ts` v0.98.2; confirm the current major when setting up.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
