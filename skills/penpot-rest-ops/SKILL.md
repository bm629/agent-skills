---
# ─── UNIVERSAL CORE ──────────────────────────────────────────────────────
name: penpot-rest-ops
description: >
  Use when driving the Penpot design API directly with curl (no SDK) —
  creating, reading, renaming, deleting, or duplicating design files and
  projects, listing teams/projects/files, or verifying a token. Penpot is a
  command RPC: every operation is POST to
  <base_url>/api/rpc/command/<command>, authenticated with
  "Authorization: Token <token>" (not Bearer). Resolves any of the 137
  commands from a bundled OpenAPI spec via a command index + a $ref-resolver,
  with the RPC patterns (Accept: application/json transit trap, UUID ids,
  per-command field names, the {type,code,hint} error envelope) handled
  explicitly. Consumes caller-injected credentials (base_url + a token
  resolved by variable name) — it does not provision or resolve them; the
  token value is read only by curl, never printed.

# ─── PROVIDER-SPECIFIC EXTENSIONS ────────────────────────────────────────
extensions:
  claude:
    allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
    user-invocable: true
    when_to_use: "performing a Penpot design-file/project operation directly via the RPC API"
    argument-hint: "<operation, e.g. 'create a design file in project X'>"
  copilot: {}
  cursor:
    alwaysApply: false
    globs: []
  gemini: {}
  codex: {}

version: "1.0.0"

forge:
  status: unreviewed
  forged: 2026-06-12
  reviewed: null
---

# penpot-rest-ops

## Overview

This skill lets an agent perform Penpot design-tool operations by calling the **RPC API directly with `curl`** — no SDK, no `pip` dependency. Penpot's API is a **command RPC**: every operation is a `POST` to `<base_url>/api/rpc/command/<command-name>` with a JSON body, authenticated with a personal access token. The agent consumes the credentials the caller injected, finds a command in a bundled OpenAPI spec via a **command index + a `$ref`-resolver**, constructs the `curl`, and parses the JSON. It covers the feasible design-seam surface — files, projects, teams, profile — and deliberately excludes rich canvas authoring (the `update-file` "changes" format), which is an internal, transit-encoded surface unfit for a general client.

## When to activate

- ✅ Creating / getting / renaming / deleting / duplicating a Penpot **design file**.
- ✅ Listing or creating **projects**; listing **teams**; listing files in a project.
- ✅ Verifying an injected token works (`get-profile` whoami) or reading account/team/project metadata.

**Do NOT activate when:**

- You need to **author canvas content** (add/modify shapes, frames, tokens) inside a file — that is the `update-file` "changes" surface, which is out of scope (see Anti-patterns).
- You only need credential setup — credentials are provided by the caller; this skill does not provision or resolve them (see `references/credentials.md` for the contract it consumes).
- The target is the editor-bound Penpot MCP rather than the headless REST/RPC API.

## Workflow

### Step 1 — Receive the injected credentials

The caller has already resolved the account and injected what this operation needs — **consume** it; do **not** look for a record yourself. You receive from context:

- **`base_url`** (e.g. `https://design.penpot.app` or a self-hosted host) and the **capability** the account acts under (`design`) — as context values, not read from a file.
- **The token, by an ordered load rule** the context carries the **variable NAME** for. Resolve that name as: the project-level **`.env` value if that file exists** and defines the var, **else** the **environment variable** of that name — project `.env` is tried first. The token **value** is never in the context prose — only its variable name; `curl` reads the value from the environment. The project root is supplied by the context; perform **no** scope resolution or directory walk to find the `.env`, and it is project `.env`, not `.envrc`.

Then bridge into the scripts' fixed vars `base_url` / `PENPOT_TOKEN`. Penpot auth is `Authorization: Token <token>` — **`Token`, not `Bearer`**. Full contract + the bridge: [`references/credentials.md`](references/credentials.md).

### Step 2 — Find the command

Scan [`assets/endpoint-index.md`](assets/) (one line per command: `command — req: <fields> | opt: <fields>`) for the operation you need. Penpot reads are commands too — `get-file`, `get-projects`, `get-profile` are all there. Never load the full spec into context — it is ~1.2 MB.

### Step 3 — Resolve the call shape

Run the resolver: `python3 scripts/endpoint.py <command>`. It `$ref`-resolves that one command's request body from the bundled spec and prints the required/optional fields, the spec example (shape, not values), and a `curl` skeleton. The spec declares **request bodies only** — response/error shapes live in `references/patterns.md`.

### Step 4 — Construct + run the `curl`

Apply the **RPC patterns** from [`references/patterns.md`](references/patterns.md):

- **Method + path:** always `POST <base_url>/api/rpc/command/<command>` — even for reads. No path/query params.
- **Auth:** `-H "Authorization: Token $PENPOT_TOKEN"`.
- **Headers:** `-H "Content-Type: application/json" -H "Accept: application/json"` — the `Accept` header is **mandatory** (Penpot can default to transit encoding without it).
- **Body:** JSON; commands with no parameters still POST `{}`. Build bodies with `jq` (or inline) from the resolved schema — UUID ids, and **per-command** field names (`id` vs `fileId`), so resolve, don't guess.

The four bundled `scripts/*.sh` (`get-profile`, `get-projects`, `create-file`, `get-file`) are worked examples of this shape.

### Step 5 — Handle the response

- **Reads** return the resource JSON (a profile, an array of projects/files, a file document). List commands return the **full array** — there is no pagination.
- **Errors** are a non-2xx `{type, code, hint}` envelope — read `code`/`hint` for the cause. A `401`/`403` usually means a missing/expired token or `Bearer` used instead of `Token`.

## Rules

**Hard rules (never violate):**

- **No SDK, no `pip`.** API calls use `curl`; the only helper is `scripts/endpoint.py` (`python3` **stdlib** only).
- **Never read or print the token value.** Reference it only as `$PENPOT_TOKEN` in a `curl` header; the subprocess reads it from the environment. The token lives only in `.env` (gitignored) or the environment.
- **Always POST to `/api/rpc/command/<command>`.** Reads are POST too. Never issue an HTTP `GET`, and never call the OpenAPI `…/api/main/methods` doc-namespace URL.
- **Always send `Accept: application/json`.** Without it Penpot may return transit, not plain JSON.
- **Resolve before constructing.** Build the body from the `$ref`-resolved schema (Step 3) — never from a guessed/remembered field set; field names differ per command.
- **This skill never writes credentials.** Credentials are provided by the caller; this skill never provisions or resolves them.

**Preferences (override-able):**

- Use `get-file-summary` / `get-file-info` instead of `get-file` when you only need metadata — `get-file` returns the whole document.
- Prefer `get-all-projects` (no team-id) for a cross-team listing; `get-projects` when you already have a `teamId`.
- Seed unknown ids from `get-profile` (`defaultTeamId` / `defaultProjectId`).

## Gotchas

- **The transit trap.** Omitting `Accept: application/json` is the most common "the JSON looks weird" failure — Penpot can answer in `application/transit+json` (datatype-tagged, not plain JSON). Always send the header.
- **POST for reads.** `get-*` commands are RPC POSTs, not HTTP GETs — a `GET /api/rpc/command/get-file` will not work.
- **The doc URL is not the call URL.** The OpenAPI `servers` value `…/api/main/methods` is where Penpot renders its docs; the real call path is `/api/rpc/command/<command>`.
- **`Token`, not `Bearer`.** Penpot rejects `Authorization: Bearer …`; the scheme is `Token`.
- **Inconsistent id field names.** `get-file`/`rename-file`/`delete-file` use `id`; `duplicate-file` uses `fileId`; listing uses `projectId`/`teamId`. Resolve each command — do not reuse a field name across commands.
- **`get-team` example is noise.** The spec's auto-generated example mislabels the field `fileId`; pass `{"id": <teamUuid>}` (confirm live).
- **No declared error/response schema.** The spec has request bodies only; treat the `{type, code, hint}` error envelope as conventional and confirm exact fields against a live failing call.
- **Big reads.** `get-file` can return a very large `data` document; some large-file reads have been reported to truncate. Prefer the summary variants when you can.

## Anti-patterns

- **Authoring canvas content via `update-file`.** Don't. `update-file` requires `sessionId` + `revn`/`vern` revision numbers (optimistic concurrency) and a `changes` body that is a 39-variant transit-encoded union of internal document-mutation ops produced by the editor. Reimplementing that grammar in a general client is out of scope; create/read/list/rename/delete/duplicate are the supported surface.
- **Guessing the body.** Don't hand-write a request body from memory — resolve the schema (Step 3); required fields and field names vary per command.
- **Echoing the token.** Never `echo $PENPOT_TOKEN`, never paste it into a printed command, never write its value to a file. Reference the env var inside the `curl` header only.
- **Loading the whole spec.** Don't `cat`/read the ~1.2 MB OpenAPI into context — scan the index, resolve one command.
- **Using `Bearer` / `GET` / dropping `Accept`.** The three quiet failure modes — token scheme is `Token`, every call is `POST`, and `Accept: application/json` is mandatory.
- **SDK creep.** Don't reach for an unofficial Penpot client or `pip install` — `curl` + the resolver cover every command.

## Output

This skill produces **API side effects** (the requested Penpot operation) and returns the parsed JSON response to the calling agent. It writes no files of its own (it only *consumes* the caller-injected credentials). For writes it reports the created/renamed/duplicated resource (id, name, projectId); for reads it returns the resource or the full array. The abstract consumer is the calling agent (or a sub-agent) that needs the design-seam operation performed; secrets never enter that output.

## Related

- [`references/credentials.md`](references/credentials.md) — the credential contract this skill consumes (caller-injected `base_url` + the ordered token-load rule + the `Authorization: Token` bridge).
- [`references/patterns.md`](references/patterns.md) — the RPC patterns (POST path, content negotiation, errors, no pagination, the command quick-reference).
- The REST/RPC-direct + bundled-OpenAPI-spec pattern generalizes to other API providers (the same shape as a `curl`-driven REST ops skill, adapted to Penpot's command-RPC + token auth).

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- [`references/credentials.md`](references/credentials.md) — the credential contract: caller-injected fields, the ordered token-load rule, the `Authorization: Token` bridge, honest-secret handling. Load in Step 1.
- [`references/patterns.md`](references/patterns.md) — RPC call shape, the `Accept` transit trap, UUID ids + per-command field names, the error envelope, no pagination, and the priority-command quick-reference. Load in Steps 4–5.
- [`references/sources.md`](references/sources.md) — provenance (the bundled spec + official Penpot docs) and the flagged "confirm live" items.
- `assets/penpot-openapi.json` — the bundled OpenAPI spec (authoritative; queried via the resolver, never loaded wholesale).
- `assets/endpoint-index.md` — one line per command, for discovery (Step 2).
- `scripts/endpoint.py` + `.validation.md` — the `python3` `$ref`-resolver (Step 3).
- `scripts/{get-profile,get-projects,create-file,get-file}.sh` + `.validation.md` — four validated example `curl`s.

## Standalone usage (optional, not required)

This is a convenience for a **human running the skill by hand** outside an agent-flow — it is **not a dependency of the skill**. The skill's normative contract is caller-injection (Step 1); this appendix is only the manual-operator bridge.

To run by hand, create an access token in Penpot (**Your account → Access tokens → Generate new token**), store its value in a gitignored `.env`, then populate the two vars yourself:

```bash
set -a; source .env; set +a                 # loads $PENPOT_DESIGN_TOKEN, never prints it
export base_url="https://design.penpot.app"
export PENPOT_TOKEN="$PENPOT_DESIGN_TOKEN"
bash scripts/get-profile.sh                  # verify the token
bash scripts/create-file.sh <project-uuid> "<file name>"
```

The token value is referenced by name only, never printed. A Penpot token has **no scopes** (full account access) — prefer a short expiry.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; RPC detail lives in `references/`.
- `assets/penpot-openapi.json` is large (queried on disk, never loaded into context).
