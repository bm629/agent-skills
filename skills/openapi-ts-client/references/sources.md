# Sources & provenance

Research for `openapi-ts-client`, forged 2026-06-09. Network research done in the main agent thread (background subagents had no WebFetch egress); external content treated per the workspace's external-content-sanitizer convention.

## Discovery (find-first)

Done at the sourcing stage: no adoptable skill cleared the gate — `softaworks@openapi-to-typescript` (3.7K) is OpenAPI-3.0-only + thin; `orval-labs/orval@orval` is official but 315 installs with a hooks-by-default model. Canonical tool = `@hey-api/openapi-ts` → decision: forge.

## Primary sources (live docs, fetched 2026-06-09)

- `@hey-api/openapi-ts` docs — heyapi.dev/openapi-ts: get-started (install `npm install @hey-api/openapi-ts -D -E`), configuration (`openapi-ts.config.ts` + `defineConfig({ input, output, plugins })`; input = path/URL/registry/object/spec; output = path or object), clients (fetch default, axios, next + others; **clients bundled in the generator since v0.73.0 — no separate install**, selected via `plugins`; `runtimeConfigPath` / `setConfig` / per-call; separate client-code-into-output bundling option), migrating (the v0.73.0 bundling statement), TanStack Query plugin (framework-specific plugin string; `Options`/`QueryKey`/`InfiniteOptions`/`Mutation` generated exports; `useQuery({ ...getPetByIdOptions({ path }) })`).
- `@hey-api/openapi-ts` package README (raw.githubusercontent.com/hey-api/openapi-ts/.../packages/openapi-ts/README.md) — Zod plugin string `zod`; Next.js client `@hey-api/client-next`; canonical `defineConfig` example.
- Version: `unpkg.com/@hey-api/openapi-ts/package.json` → **0.98.2** (0.x line) as of 2026-06-09.
- FastAPI "Generate Clients" — fastapi.tiangolo.com/advanced/generate-clients/: hey-api is the recommended TS generator; `npx @hey-api/openapi-ts -i http://localhost:8000/openapi.json -o src/client`; the `generate_unique_id_function` (`f"{route.tags[0]}-{route.name}"`) and the operationId-prefix-strip preprocess script.

## Fact-check notes (self-review + provenance)

- **SDK `{ data, error }` result shape + `throwOnError`:** CONFIRMED in the Step-4.5b fresh-review (WebSearch corroborated hey-api's documented default: functions resolve to `{ data, error }` and don't throw; `throwOnError: true` flips to throwing).
- **Client bundling (v0.73.0+):** CORRECTED during self-review. Clients are bundled inside `@hey-api/openapi-ts` since v0.73.0 (heyapi.dev/openapi-ts/migrating, verbatim: "all Hey API clients are bundled by default and don't require installing any additional dependencies"); you still add the client to `plugins`. An earlier draft wrongly taught separate per-client `npm install`s (a stale page read) — fixed across SKILL.md + clients.md.
- **Version pin:** 0.98.2 was current on the fetch date; re-confirm at setup time (the skill says so).
- **Legacy tool:** `openapi-typescript-codegen` is the older codegen hey-api succeeds; no explicit deprecation banner was seen — the skill frames hey-api as the maintained tool rather than citing a specific deprecation notice.
