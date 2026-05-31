# Validation — `endpoint.py`

**What it does:** resolves one GitHub REST operation by `operationId` from
`assets/github-openapi.json` — `$ref`-dereferences its parameters / request body /
response (bounded depth + cycle guard) and prints a readable summary + a `gh api`
skeleton. `python3` stdlib only; no `pip`. Read-only: never authenticates or calls the
API (that is `gh api`'s job, per-call `GH_TOKEN`).

**Static validation (2026-05-31):**
- `python3 -m py_compile scripts/endpoint.py` → pass.
- `ruff check scripts/endpoint.py` → All checks passed.

**operationId coverage:** 1,186 / 1,186 operations carry an `operationId` (100%), so the
resolver finds every operation; `endpoint-index.md` lists them.

**Smoke tests (run against the bundled spec):**
- `endpoint.py repos/get` → `GET /repos/{owner}/{repo}`, path params + resolved 200
  response schema, `gh api repos/{owner}/{repo}` skeleton. OK.
- `endpoint.py issues/create` → `POST /repos/{owner}/{repo}/issues`, request body
  (`title` required, `oneOf`/array fields handled), POST skeleton with `-f`/`-F`/`--input`
  hint. OK.
- `endpoint.py` (no args) → usage to stderr, exit 2. OK.
- `endpoint.py bogus/nope` → "not found — scan assets/endpoint-index.md", exit 1. OK.

**Bounds:** `MAXDEPTH=5` for request bodies, depth 3 for responses, with a `$ref` cycle
guard (`(recursive)` marker) — deeply nested schemas (e.g. `repository`) print a
`… (max depth)` marker rather than recursing without limit.

**Live validation:** the resolver needs no network. End-to-end `gh api` calls built from
its output are exercised in Phase 2.E (live smoke).
