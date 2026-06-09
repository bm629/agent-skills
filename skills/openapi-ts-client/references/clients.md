# Clients (transports)

Load when choosing or configuring the HTTP transport. The generated SDK is transport-agnostic; a **client plugin** supplies the actual HTTP layer. As of v0.73.0 every client ships **bundled inside `@hey-api/openapi-ts`** — you don't install a separate package; you select a client by adding it to `plugins` (fetch is the default).

## Available clients

hey-api ships several: Fetch (default), Axios, Next.js, Ky, OFetch, Angular, Nuxt, and more. The three most common for a typical SPA or Next.js app:

| Client | Plugin string | When |
|---|---|---|
| Fetch | `@hey-api/client-fetch` | Default; browser/SPA (e.g. a Vite React app). |
| Axios | `@hey-api/client-axios` | Project standardizes on axios (interceptors, etc.). |
| Next.js | `@hey-api/client-next` | A Next.js app (RSC/route handlers). |

Select a non-default client by adding it to `plugins` (no separate install — see below), e.g. axios:

```ts
plugins: ['@hey-api/client-axios']
```

Fetch is the default, so its plugin line is optional. Choose axios when you want axios features (interceptors, broad instance config).

### Next.js client (`@hey-api/client-next`)

For a Next.js app, the Next client wraps Next's extended `fetch`, so SDK calls participate in Next's caching/revalidation (cache tags, `revalidate`). Unlike plain Fetch it supports request/response **interceptors**. Initialize it for **both server and client environments** by exporting a `createClientConfig()` from a module referenced via `runtimeConfigPath` (rather than a one-time `setConfig()` call), so Server Components and client components share the configured base URL/headers:

```ts
plugins: [{ name: '@hey-api/client-next', runtimeConfigPath: './src/hey-api.ts' }]
```

## SDK result shape

By default a generated SDK function resolves to a `{ data, error }` result (plus request/response metadata) and does **not** throw. Check `error`:

```ts
const { data, error } = await getItem({ path: { id: 1 } });
```

Set `throwOnError: true` (per-call options, or in the client runtime config) to make functions throw on non-2xx instead of returning `error`.

## Runtime configuration (base URL, headers, interceptors)

Three approaches:

1. **`setConfig()`** — call the generated client's `setConfig` (imported from your generated client) once at app startup to set `baseUrl`, default headers, etc. For a Vite SPA pointed at a local FastAPI:
   ```ts
   // once, at app startup
   setConfig({ baseUrl: 'http://localhost:8000' });
   ```
2. **`runtimeConfigPath`** — point the client plugin at a module that exports `createClientConfig()`, which wraps/overrides defaults. Good for keeping config in code and out of the generated output.
   ```ts
   plugins: [{ name: '@hey-api/client-fetch', runtimeConfigPath: './src/hey-api.ts' }]
   ```
3. **Per-call options** — pass config (e.g. `baseUrl`, `headers`, `throwOnError`) directly to an individual SDK call.

## Bundling — two distinct meanings

1. **Clients ship bundled in the generator (v0.73.0+).** You do not install a separate `@hey-api/client-*` package — it's included in `@hey-api/openapi-ts`. Select a client by adding it to `plugins` (fetch is the default, so even that is optional). On a pre-0.73 project you'd have installed the client separately; remove those installs and regenerate.
2. **Inlining client code into the output.** Separately, a client can bundle its *code* into the generated output so the published package doesn't carry the client as a runtime dependency — an output option, unrelated to #1.
