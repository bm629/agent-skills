# penpot-rest-ops

> Drive the Penpot design API directly with `curl` — no SDK. Penpot's API is a
> **command RPC**: every operation is a `POST` to
> `<base_url>/api/rpc/command/<command>` authenticated with
> `Authorization: Token <token>` (not Bearer). The skill resolves any of the
> 137 commands from a bundled OpenAPI via a command index + a `$ref`-resolver,
> and handles the RPC gotchas (the `Accept: application/json` transit trap,
> UUID ids, per-command field names, the `{type,code,hint}` error envelope).
> It consumes **caller-injected** credentials and never prints the token.

**Skill file:** [`skills/penpot-rest-ops/SKILL.md`](../../skills/penpot-rest-ops/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent the feasible Penpot design-seam surface — create / get / rename
/ delete / duplicate **files**, create / list **projects**, list **teams**,
verify a token (`get-profile`) — by calling the headless REST/RPC token API.
It deliberately excludes rich canvas authoring (the `update-file` "changes"
format is an internal, transit-encoded, revision-concurrency surface unfit for
a general client) and the editor-bound MCP. It is the OpenAPI-grounded sibling
of `atlassian-rest-ops`, adapted to Penpot's command-RPC + `Token` auth.

## When to activate

- ✅ Creating / reading / renaming / deleting / duplicating a Penpot design file.
- ✅ Listing or creating projects; listing teams; listing a project's files.
- ✅ Verifying an injected token (`get-profile` whoami) or reading account/team/project metadata.

Not for: rich canvas authoring (the `update-file` changes surface), credential
setup (caller-injected), or the editor-bound Penpot MCP.

## Workflow

1. **Receive the injected credentials** — `base_url` from context + the token by
   variable name (project `.env` value if defined, else the env var); bridge into
   `base_url` / `PENPOT_TOKEN`. Auth is `Authorization: Token`.
2. **Find the command** — scan `assets/endpoint-index.md` (one line per command
   with its required/optional fields).
3. **Resolve the shape** — `python3 scripts/endpoint.py <command>` `$ref`-resolves
   the request body + prints a curl skeleton (the bundled spec declares request
   bodies only).
4. **Call** — always `POST /api/rpc/command/<command>` with
   `Content-Type: application/json` **and** `Accept: application/json` (the transit
   trap), JSON body (`{}` for no-field commands).
5. **Handle the response** — reads return the resource (no pagination); errors are
   a non-2xx `{type, code, hint}` envelope.

## Key gotchas

- **The transit trap** — omitting `Accept: application/json` can return
  `application/transit+json` (datatype-tagged, not plain JSON).
- **POST for reads** — `get-*` are RPC POSTs, not HTTP GETs.
- **The doc URL is not the call URL** — the OpenAPI `servers` value
  `…/api/main/methods` is the doc namespace; call `/api/rpc/command/<cmd>`.
- **`Token`, not `Bearer`** — Penpot rejects `Bearer`.
- **Per-command field names** — `get-file` uses `id`, `duplicate-file` uses
  `fileId`; resolve each command, don't reuse a field name.

## Credential contract

Pure consumer of caller-injected credentials: `base_url` from context, the token
by variable NAME (project `.env`-then-env-var, no scope-walk, no `.service-accounts.yaml`,
no `--account`). The token value is read only by the `curl` subprocess, never
printed. A "Standalone usage" appendix documents the by-hand bridge for a manual
operator.
