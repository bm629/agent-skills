# Data states + forms — MSW × TanStack Query

> Load when testing loading/empty/success/error states or a form. Verified-at-forge: `msw` 2.x, `@tanstack/react-query` 5.x, `@testing-library/user-event` 14.x.

## The four data states — vary the MSW response per test

A component that fetches has at least four user-visible states. Drive each one by overriding the handler with `server.use(...)` and asserting what the user sees. A fresh `QueryClient` with `retry: false` (the custom `render` in SKILL.md Step 6) makes the error state resolve immediately instead of retrying with backoff.

```tsx
import { http, HttpResponse } from 'msw'
import { renderWithProviders, screen } from '../../test/test-utils'
import { server } from '../../test/msw-server'
import { UserList } from './UserList'

// Loading — assert the loading affordance is shown before the response resolves.
it('shows a loading state', async () => {
  renderWithProviders(<UserList />)
  expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument()
})

// Success — 200 with data.
it('renders the users', async () => {
  server.use(http.get('/api/users', () =>
    HttpResponse.json([{ id: 'u1', email: 'a@b.com' }])))
  renderWithProviders(<UserList />)
  expect(await screen.findByText('a@b.com')).toBeInTheDocument()
})

// Empty — 200 with an empty collection; assert the empty-state copy, not a crash.
it('renders the empty state', async () => {
  server.use(http.get('/api/users', () => HttpResponse.json({ data: [] })))
  renderWithProviders(<UserList />)
  expect(await screen.findByText(/no users yet/i)).toBeInTheDocument()
})

// Error — 500 (or a ProblemDetail body); retry:false makes this fast + deterministic.
it('renders the error state', async () => {
  server.use(http.get('/api/users', () =>
    HttpResponse.json({ type: 'about:blank', title: 'Server error', status: 500 },
      { status: 500 })))
  renderWithProviders(<UserList />)
  expect(await screen.findByRole('alert')).toHaveTextContent(/something went wrong/i)
})
```

The empty `{ data: [] }` vs the bare `[]` shape depends on your API's contract — match what the generated client expects so the real deserialization runs.

## Forms — fill, submit, assert the request body

The high-value form test asserts the **request body the server actually received**, captured by the MSW handler — proving the form serialized correctly through the real client.

```tsx
import { http, HttpResponse } from 'msw'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'
import { renderWithProviders, screen } from '../../test/test-utils'
import { server } from '../../test/msw-server'
import { SignupForm } from './SignupForm'

it('submits valid input and shows success', async () => {
  const user = userEvent.setup()
  let captured: unknown
  server.use(http.post('/api/users', async ({ request }) => {
    captured = await request.json()
    return HttpResponse.json({ id: 'u1' }, { status: 201 })
  }))

  const { container } = renderWithProviders(<SignupForm />)
  await user.type(screen.getByLabelText(/email/i), 'a@b.com')
  await user.type(screen.getByLabelText(/^password/i), 's3cret!')
  await user.click(screen.getByRole('button', { name: /create account/i }))

  expect(await screen.findByText(/account created/i)).toBeInTheDocument()
  expect(captured).toEqual({ email: 'a@b.com', password: 's3cret!' })
  expect(await axe(container)).toHaveNoViolations()
})
```

## Validation errors — assert NO request was made

Client-side validation should block the request. Assert the inline error appears and the handler was never hit (a spy counter, or assert the captured body stays unset):

```tsx
it('blocks submit on invalid email and sends nothing', async () => {
  const user = userEvent.setup()
  let calls = 0
  server.use(http.post('/api/users', () => {
    calls += 1
    return HttpResponse.json({ id: 'u1' }, { status: 201 })
  }))

  renderWithProviders(<SignupForm />)
  await user.type(screen.getByLabelText(/email/i), 'not-an-email')
  await user.click(screen.getByRole('button', { name: /create account/i }))

  expect(await screen.findByText(/enter a valid email/i)).toBeInTheDocument()
  expect(calls).toBe(0)
})
```

## Submit (server) errors — surface the server's rejection

```tsx
it('shows the server error and keeps the form editable', async () => {
  const user = userEvent.setup()
  server.use(http.post('/api/users', () =>
    HttpResponse.json({ title: 'Email already taken', status: 409 }, { status: 409 })))

  renderWithProviders(<SignupForm />)
  await user.type(screen.getByLabelText(/email/i), 'a@b.com')
  await user.type(screen.getByLabelText(/^password/i), 's3cret!')
  await user.click(screen.getByRole('button', { name: /create account/i }))

  expect(await screen.findByRole('alert')).toHaveTextContent(/already taken/i)
  expect(screen.getByLabelText(/email/i)).toBeEnabled() // user can retry
})
```

## The security-invariant assertion (a field absent in BOTH places)

When a field must **never** be exposed to or sent by the form — e.g. an internal token, an admin-only flag, a server-managed id — assert it is absent from the **DOM** and absent from the **captured request body**. This is the generic pattern behind a "no secret-value input" test:

```tsx
it('never renders or submits the internal token', async () => {
  const user = userEvent.setup()
  let captured: Record<string, unknown> = {}
  server.use(http.post('/api/users', async ({ request }) => {
    captured = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ id: 'u1' }, { status: 201 })
  }))

  renderWithProviders(<SignupForm />)
  await user.type(screen.getByLabelText(/email/i), 'a@b.com')
  await user.type(screen.getByLabelText(/^password/i), 's3cret!')
  await user.click(screen.getByRole('button', { name: /create account/i }))
  await screen.findByText(/account created/i)

  expect(screen.queryByLabelText(/internal token/i)).not.toBeInTheDocument() // not in the DOM
  expect(captured).not.toHaveProperty('internalToken')                       // not on the wire
})
```

Use `queryBy*` (returns `null`) — never `getBy*` (throws) — for the "must NOT exist" assertion.
