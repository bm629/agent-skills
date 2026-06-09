---
name: openapi-ts-client
description: >
  Use when generating or regenerating a typed TypeScript client from an OpenAPI
  3.1 contract — for example a FastAPI /openapi.json — with @hey-api/openapi-ts.
  Produces typed models, a typed SDK (one function per operation), TanStack Query
  hooks, and Zod schemas straight from the spec, so the frontend stays in
  lock-step with the API instead of a hand-written client. Covers the
  openapi-ts.config.ts config, the fetch/axios/next clients, the tanstack-query
  and zod plugins, the regenerate-and-drift-check workflow, and the FastAPI
  operationId naming fix. Use when wiring an OpenAPI or FastAPI backend to a
  TS/React frontend, replacing a hand-maintained API client, or adding generated
  query hooks. Not a TanStack Query usage tutorial (compose with that skill) and
  not backend/OpenAPI-spec authoring.
extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-09
  reviewed: 2026-06-09
---

# `openapi-ts-client` — SKILL.md

> **Variant:** standard · **When to use:** generating a typed TS client/SDK from an OpenAPI 3.1 contract with `@hey-api/openapi-ts`.

## Overview

`@hey-api/openapi-ts` is the maintained TypeScript code generator for OpenAPI — the tool FastAPI's own docs recommend for TS clients. Point it at an OpenAPI 3.1 document (a live `/openapi.json` URL or a saved file), and it emits typed models, a typed SDK (one async function per operation), and — via plugins — TanStack Query hooks and Zod schemas. The generated client is a build artifact: the OpenAPI contract is the single source of truth, and you regenerate rather than hand-edit. This skill covers configuring it, choosing a client transport, enabling the TanStack Query + Zod plugins, the regenerate-and-drift-check workflow, and the FastAPI-specific `operationId` naming fix. Verified against `@hey-api/openapi-ts` v0.98.2 (the 0.x line); confirm the current version when you set it up.

## When to activate

- ✅ Generating a typed TS client/SDK from a FastAPI (or any OpenAPI 3.1) `/openapi.json`.
- ✅ Adding generated TanStack Query hooks or Zod request/response schemas off a spec.
- ✅ Replacing a hand-written or hand-maintained API client with a generated one.
- ✅ Setting up the regenerate-on-contract-change workflow + a CI drift check.

**Do NOT activate when:**

- You need TanStack Query *usage* patterns (caching, invalidation, query keys) — compose with the `tanstack-query` skill; this skill only generates the hooks.
- You are authoring the backend, the OpenAPI spec, or Pydantic models — use the `fastapi` / `pydantic-v2` skills.
- The contract is OpenAPI 3.0 only and you need a 3.0-specialized tool — hey-api targets 3.1 (what FastAPI ≥ 0.99 emits); it reads 3.0 but the sweet spot is 3.1.

## Workflow

### Step 1: Install

Install the generator. As of v0.73.0 the clients ship bundled inside it — no separate client package install:

```sh
npm install @hey-api/openapi-ts -D -E      # generator (pnpm/yarn/bun analogous)
```

### Step 2: Write `openapi-ts.config.ts`

```ts
import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8000/openapi.json', // URL, file path, or a spec object
  output: 'src/client',                        // dir; or { path, format, lint }
  plugins: [
    '@hey-api/client-fetch',      // transport (fetch default; -axios / -next)
    '@tanstack/react-query',      // generated query/mutation hooks
    'zod',                        // generated request/response schemas
  ],
});
```

`@hey-api/typescript` (types), `@hey-api/sdk`, and `@hey-api/schemas` are core plugins included by default. Full schema + all options: [`references/configuration.md`](references/configuration.md). Client transports in depth: [`references/clients.md`](references/clients.md).

### Step 3: Generate

Run via a `package.json` script (not ad-hoc) so it is repeatable:

```jsonc
// package.json
"scripts": { "gen:api": "openapi-ts" }
```

`npm run gen:api` reads `openapi-ts.config.ts`. The one-shot CLI form is `npx @hey-api/openapi-ts -i <input> -o <output> -c @hey-api/client-fetch`.

### Step 4: Consume the SDK

Each operation becomes a typed async function; by default it resolves to a `{ data, error }` result (no throw). Params go in one options object (`path` / `query` / `body` / `headers`):

```ts
const { data, error } = await getItem({ path: { id: 1 } });
if (error) { /* typed error */ } else { /* typed data */ }
```

Set `throwOnError: true` (per-call or in client config) to make functions throw instead. Set the base URL once via the client config — see [`references/clients.md`](references/clients.md).

### Step 5: Use the generated TanStack Query hooks + Zod schemas

The `@tanstack/react-query` plugin generates `<op>Options()`, `<op>QueryKey()`, `<op>InfiniteOptions()`, and `<op>Mutation()` helpers you spread into TanStack Query — see [`references/plugins-query-zod.md`](references/plugins-query-zod.md). For the query/mutation/cache patterns themselves, defer to the `tanstack-query` skill. The `zod` plugin generates schemas to validate at the boundary (same file).

### Step 6: FastAPI operationId + regenerate/drift workflow

FastAPI's default `operationId` produces ugly method names (`createItemItemsPost`). Fix it at the source with `generate_unique_id_function` — see [`references/fastapi-regen.md`](references/fastapi-regen.md), which also covers the regenerate-on-change script, the CI drift check, and the commit-vs-gitignore decision.

## Rules

**Hard rules (never violate):**

- **Never hand-edit generated files.** They are overwritten on every regenerate. Customize via config/plugins or wrap the SDK, never by patching `src/client`.
- **The OpenAPI contract is the single source.** Regenerate when it changes; do not let the generated client drift from the spec (enforce with the CI drift check).
- **Pin the generator version** (`-E` / exact in `package.json`). hey-api is pre-1.0 (0.x) and moves fast; an unpinned bump can change output. Confirm the current version when setting up.
- **Generate, don't hand-write.** If you are typing API types or fetch wrappers by hand off a spec, stop and generate them.

**Preferences (override-able):**

- Default to the fetch client unless the project standardizes on axios or is a Next.js app.
- Keep the `{ data, error }` result style (explicit error handling) unless a layer wants `throwOnError`.
- Run codegen in a `package.json` script and in CI, not ad-hoc on each machine.

## Gotchas

- **Clients ship bundled in the generator (v0.73.0+) — don't install them separately.** Just add the client to `plugins` (fetch is the default, so even that is optional). If you inherit a pre-0.73 setup with `@hey-api/client-*` installs, you can remove them and regenerate. (Distinct concept: a client can inline its *code* into the generated output — an output option — which is unrelated to installing.)
- **FastAPI operationIds are verbose.** Without `generate_unique_id_function`, you get `createItemItemsPost`-style names. Fix it on the FastAPI side so every regenerate is clean (`references/fastapi-regen.md`).
- **SDK functions don't throw by default.** They resolve to `{ data, error }`; code that `try/catch`es and never checks `error` silently ignores failures. Use `throwOnError: true` if you want exceptions.
- **OpenAPI 3.0 vs 3.1.** hey-api targets 3.1 (FastAPI ≥ 0.99). A 3.0-only document or an old codegen mindset (`openapi-typescript-codegen`, the legacy tool hey-api succeeds) leads to wrong assumptions — use the current tool against a 3.1 spec.
- **Generating off a live server vs a saved spec.** A URL input needs the server up at generate time and regenerates silently when the API changes; a committed spec file is reproducible but must be refreshed deliberately. Pick per the drift strategy in `references/fastapi-regen.md`.

## Anti-patterns

- **"I'll just tweak the generated type."** No — it's overwritten next regenerate. Change the spec or wrap the output.
- **"I'll hand-write the client, it's faster."** It drifts from the contract immediately; the whole point is generation.
- **"Commit the generated client and forget it."** Without a CI drift check it silently goes stale against the API. Add the regenerate-and-`git diff --exit-code` gate.
- **"Let me also document query caching/invalidation here."** That's the `tanstack-query` skill's job; this skill stops at generating the hooks.

## Output

A generated, typed client under the configured `output` dir — models, a typed SDK, and (per plugins) TanStack Query hooks and Zod schemas — plus an `openapi-ts.config.ts`, a `gen:api` script, and (recommended) a CI drift check. The consumer is the frontend code (and its tests/CI) that calls the API through the generated SDK and hooks.

## Related

- `tanstack-query` — query/mutation/cache *usage*; this skill generates the hooks it consumes.
- `fastapi` / `pydantic-v2` — the backend that emits the OpenAPI contract this skill reads.
- `vite` — the SPA build the generated client typically ships in.

## Progressive disclosure

- `references/configuration.md` — load when writing `openapi-ts.config.ts`: full `input`/`output`/`plugins` schema, options, CLI flags, package.json wiring.
- `references/clients.md` — load when choosing/configuring a transport: fetch/axios/next (and others) in depth, runtime config (`setConfig`, `createClientConfig`, per-call), base URL, the client-code `bundle` option.
- `references/plugins-query-zod.md` — load when wiring the generated TanStack Query hooks or Zod schemas: generated export naming + usage, and the hand-off to the `tanstack-query` skill.
- `references/fastapi-regen.md` — load when integrating with FastAPI or setting up regeneration: the `operationId` fix, the regenerate script, the CI drift check, and commit-vs-gitignore.
- `references/sources.md` — research provenance + fact-check notes.

## Body budget

- `description` ≤ 1,024 chars; body ≤ ~500 lines / 5,000 tokens; heavy content in `references/`.
