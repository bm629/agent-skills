# Configuration — `openapi-ts.config.ts`

Load when writing or adjusting the config.

## Config file

Accepted names: `openapi-ts.config.ts`, `.cjs`, `.mjs`, `.js`. Export a config via `defineConfig`:

```ts
import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8000/openapi.json',
  output: 'src/client',
  plugins: ['@hey-api/client-fetch', '@tanstack/react-query', 'zod'],
});
```

## `input`

The OpenAPI source. Accepts:

- a string **file path** (`./openapi.json`),
- a **URL** (`https://…/openapi.json`) — read at generate time,
- an **API-registry shorthand** (e.g. `'hey-api/backend'`),
- an **object** wrapping any of the above (with extra options like filters/patches),
- or an **object that is the OpenAPI spec itself** (`{ openapi: '3.1.1', … }`).

For a FastAPI backend, the input is its `/openapi.json` (live URL) or a committed snapshot of it.

## `output`

- a string **destination directory** (`'src/client'`), or
- an **object** `{ path: 'src/client', … }` with options such as output formatting/linting of the generated files.

## `plugins`

An array; each entry is either a **plugin string** or an **object** `{ name, …options }` for per-plugin config:

```ts
plugins: [
  '@hey-api/client-fetch',
  { name: '@hey-api/client-axios', runtimeConfigPath: './src/hey-api.ts' },
  '@tanstack/react-query',
  'zod',
],
```

Core plugins included by default: `@hey-api/typescript` (models/types), `@hey-api/sdk` (one function per operation), `@hey-api/schemas`. Add a **client** plugin (transport — see `clients.md`), and optional plugins like the framework `@tanstack/*-query` and `zod`.

## Running the generator

Prefer a `package.json` script over ad-hoc invocation:

```jsonc
"scripts": { "gen:api": "openapi-ts" }   // reads openapi-ts.config.ts
```

One-shot CLI (no config file): `npx @hey-api/openapi-ts -i <input> -o <output> -c <client>`, where `-c` selects the client (e.g. `-c @hey-api/client-axios`).
