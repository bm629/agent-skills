# Validation: endpoint.py

- **Method**: syntax check (`python -m py_compile`); lint (`ruff check --select E,F,W`); smoke runs against the bundled spec.
- **Tools**: `python3 -m py_compile`; `ruff` 0.x (portable E/F/W ruleset); no third-party imports (stdlib only).
- **Date**: 2026-06-12
- **Exit codes**: `py_compile`: 0 · `ruff --select E,F,W`: 0 (All checks passed) · smoke: 0 on found command, 1 on not-found.

## Captured output

`python3 endpoint.py create-file` resolves `POST <base_url>/api/rpc/command/create-file`, request body `name* (string), projectId* (Uuid), id (Uuid), isShared (Boolean), features (Features)` — matching the bundled spec. `get-profile` correctly prints `{ free-form object }` (no fields). A bogus command exits 1 with a pointer to `assets/endpoint-index.md`.

## Caveats

- The bundled spec declares request bodies only (no response/error schemas), so the resolver points response/error questions at `references/patterns.md` by design.
- Repo-local `ruff` additionally opts into `D103` (Google-docstring policy for package code) which does not apply to a portable bundled helper; the precedent `atlassian-rest-ops/scripts/endpoint.py` ships the same docstring-light internal helpers. The portable `E,F,W` set is clean.
