# Penpot RPC patterns — call shape, content negotiation, errors

Penpot's API is a **command RPC over HTTP**, not a REST resource API. Internalize these five patterns and the bundled spec covers the rest.

## 1. Every call is POST `/api/rpc/command/<command>`

- The URL is always `<base_url>/api/rpc/command/<command-name>`. There are **no** path/query params and **no** REST verbs — `get-file`, `create-file`, `delete-file` are all **POST**. Issuing an HTTP `GET` is wrong even for reads.
- The OpenAPI declares its `servers` URL as `…/api/main/methods` — that is the **documentation namespace** where Penpot renders its API doc, **not** the call path. Call `/api/rpc/command/<command>`.
- The body is always JSON. Commands with no parameters still POST `{}` (e.g. `get-profile`, `get-teams`, `get-all-projects`).
- Cloud vs self-hosted differ **only** in `base_url` origin; the `/api/rpc/command/<command>` suffix, methods, auth, and schemas are identical. A self-hosted install behind a reverse-proxy path prefix may need that prefix in `base_url` — verify per deployment.

## 2. Content negotiation — always send `Accept: application/json`

Penpot's RPC negotiates response format on the `Accept` header and can default to **transit** (`application/transit+json`), a datatype-tagged encoding that is not plain JSON. **Always** send `Accept: application/json` (and `Content-Type: application/json` on the request). Omitting `Accept` is the most common "the JSON looks weird" failure. (The transit-default behavior is from Penpot's RPC layer; sending `Accept: application/json` is the safe action regardless.)

## 3. Ids are UUIDs; field names vary per command

- Every id (`teamId`, `projectId`, file `id`) is a UUID string.
- The file-id **field name is not consistent**: `get-file` / `rename-file` / `delete-file` take `id`, but `duplicate-file` takes `fileId`, and project listing takes `projectId`. Always resolve the exact field with `python3 scripts/endpoint.py <command>` — never assume.
- `get-profile` returns `defaultTeamId` and `defaultProjectId` — convenient seeds when you have no ids yet.

## 4. Errors — a non-2xx `{type, code, hint}` envelope

The spec declares **no** response or error schemas. On failure Penpot returns a non-2xx status with a structured JSON error of roughly the shape `{"type": ..., "code": ..., "hint": ...}` (the backend's `ex/raise` convention). Treat that as the conventional shape and read `code`/`hint` for the cause; confirm the exact fields against a live failing call. A `401`/`403` almost always means the token is missing, malformed (used `Bearer` instead of `Token`), expired, or lacks access to the target resource.

## 5. No pagination; large reads can be big

List commands (`get-teams`, `get-projects`, `get-all-projects`, `get-project-files`) take **no** pagination params and return the **full array**. There is no documented public rate limit (treat as unknown; back off on `429` if you ever see one). `get-file` returns the entire document `data` and can be very large — prefer `get-file-summary` / `get-file-info` when you only need metadata.

## Priority command quick-reference (resolve exact fields with the resolver)

| Need | Command | Required body |
|---|---|---|
| Verify the token / whoami | `get-profile` | `{}` |
| List teams | `get-teams` | `{}` |
| List projects in a team | `get-projects` | `teamId` |
| List projects across all teams | `get-all-projects` | `{}` |
| Get one project | `get-project` | `id` |
| Create a project | `create-project` | `teamId`, `name` |
| List files in a project | `get-project-files` | `projectId` |
| Create a file | `create-file` | `name`, `projectId` |
| Get a file (full document) | `get-file` | `id` |
| File metadata only | `get-file-summary` / `get-file-info` | `id` |
| Rename a file | `rename-file` | `id`, `name` |
| Delete a file | `delete-file` | `id` |
| Duplicate a file | `duplicate-file` | `fileId` |

Access-token lifecycle is itself scriptable once authenticated: `create-access-token` (`name`, optional `expiration`), `get-access-tokens`, `delete-access-token`.
