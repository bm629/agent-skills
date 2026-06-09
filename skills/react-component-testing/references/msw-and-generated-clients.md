# MSW v2 + intercepting a generated OpenAPI client

> Load when mocking the network boundary in a component test. Verified-at-forge: `msw` 2.x. Re-confirm the v2 API + the generated-client `fetch` caveat against mswjs.io (see `sources.md`).

## Why MSW (the network boundary), not `vi.mock`

Mock Service Worker intercepts the actual HTTP request your app makes, in the same Node process as the test, by patching the request layer (`fetch`/`XMLHttpRequest`). Because the interception happens at the **network boundary**, the app's real client — including a *generated* `@hey-api/openapi-ts` client, its query hooks, and its request/response serialization — all execute. A contract change (a renamed field, a newly-required body key, a changed status code) then surfaces as a test failure.

`vi.mock('./generated-client')` replaces the module with a canned object: the client, serialization, and error mapping never run, so the test cannot detect contract drift and is coupled to the client's internal shape. **Rule:** mock anything crossing the network with MSW; reserve `vi.mock` for non-HTTP collaborators (a clock via `vi.useFakeTimers`, a random-id/uuid generator, a flaky browser API).

## Node setup: `setupServer`

In Node (Vitest), use `setupServer` from `msw/node`. MSW v2 requires **Node 18+** (it relies on the platform `fetch`/`Request`/`Response`).

```ts
// src/test/msw-server.ts
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/users', () => HttpResponse.json([{ id: 'u1', email: 'a@b.com' }])),
  http.post('/api/users', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: 'u1', ...body }, { status: 201 })
  }),
]

export const server = setupServer(...handlers)
```

### The v2 API (replaced v1's `rest` + `res(ctx...)`)

- **`http`** (not `rest`) — `http.get`, `http.post`, `http.put`, `http.delete`, `http.all`, etc.
- **`HttpResponse`** — return it directly instead of the v1 `res(ctx.json(...))` callback. `HttpResponse.json(body, { status })`, `HttpResponse.text(...)`, `new HttpResponse(null, { status: 204 })`, `HttpResponse.error()` (a network error).
- The resolver receives `{ request, params, cookies }`; `request` is a standard `Request`.

## The canonical Node test lifecycle

Put this in `setupFiles` (so it runs once for the whole suite), not in each test:

```ts
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

- **`listen({ onUnhandledRequest: 'error' })`** — installs the interceptor and **fails** any request that has no matching handler (instead of silently hitting the real network). Use `'warn'` only if you deliberately allow passthrough.
- **`resetHandlers()`** in `afterEach` — discards per-test overrides added with `server.use(...)`, restoring the base `handlers`. Without it, an override leaks into the next test.
- **`close()`** in `afterAll` — removes the interceptor.

### Per-test overrides

Override the base handler for one test's scenario (success vs error vs empty):

```ts
server.use(
  http.get('/api/users', () => new HttpResponse(null, { status: 500 })),
)
```

The override applies until the next `resetHandlers()`.

## Reading / asserting the request body

The resolver's `request` is a standard `Request`; read it with the body methods and assert on it:

```ts
let captured: unknown
server.use(
  http.post('/api/users', async ({ request }) => {
    captured = await request.json()        // or .text(), .formData()
    return HttpResponse.json({ id: 'u1' }, { status: 201 })
  }),
)
// ... after the interaction:
expect(captured).toEqual({ email: 'a@b.com', password: 's3cret!' })
```

A request body can only be read **once** — read it into a variable inside the handler, then assert on that variable in the test.

## Query parameters belong in the handler, NOT the path

MSW matches on the request **pathname**. Encoding the query string in the path does not match:

```ts
// WRONG — never matches
http.get('/api/users?active=true', () => ...)

// RIGHT — match the path, read params from the URL
http.get('/api/users', ({ request }) => {
  const url = new URL(request.url)
  const active = url.searchParams.get('active')
  return HttpResponse.json(active === 'true' ? activeUsers : allUsers)
})
```

Path parameters (`http.get('/api/users/:id', ({ params }) => params.id)`) are fine — it is only the `?query=...` string that must move into the handler.

## Intercepting a GENERATED `@hey-api/openapi-ts` (or `openapi-fetch`) client

A generated client is exactly what you *want* exercised — it builds the URL, serializes the body, sets headers, and parses the response. MSW intercepts it at the fetch layer like any other request, with two ordering/wiring caveats:

### 1. `listen()` before the client is created (ordering)

MSW patches the request layer when `server.listen()` runs. A client that captures a `fetch` reference **at module-load time** (a top-level `const client = createClient({ ... })`) can bind a `fetch` that MSW hasn't patched yet, so its requests bypass the mock. Mitigations:

- Keep the MSW `server.listen()` in `setupFiles` — Vitest runs `setupFiles` before the test module's imports, so the interceptor is installed first.
- If the client still binds early, create/configure it **inside** the test (or a `beforeEach`) rather than at module top level, or import it lazily.

### 2. Some generated/`openapi-fetch` clients need an MSW-visible `fetch` (the custom-`fetch` caveat)

MSW patches the **global** `fetch`. A generated client that was configured with its **own** `fetch` implementation (a custom `fetch`, a polyfill, or one captured into a closure) may call that reference instead of the patched global — so MSW never sees the request. If requests aren't being intercepted:

- Configure the client to use the global `fetch` in tests (don't inject a custom one), **or**
- Pass MSW's expected global `fetch` into the client's `fetch` option explicitly, so the call goes through the patched path.

This is a documented gotcha for `openapi-fetch`-style clients; the exact knob depends on the generator's runtime config. **This caveat could not be re-verified against live hey-api/MSW docs at forge time (WebFetch sandbox-denied) — confirm the exact `fetch` option name + behavior against the current `@hey-api/openapi-ts` and MSW docs before relying on it** (see `sources.md`).

### 3. Confirm interception in Node

By default MSW intercepts the global `fetch` in Node (Node 18+). If a request escapes the mock with `onUnhandledRequest: 'error'`, you'll get a loud failure naming the un-mocked URL — that failure is the signal that one of the two caveats above applies.
