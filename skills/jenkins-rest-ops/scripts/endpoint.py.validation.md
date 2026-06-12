# Validation: endpoint.py

- **Method**: `python -m py_compile`; lint (`ruff check --select E,F,W`); smoke against the bundled spec.
- **Tools**: `python3 -m py_compile`; `ruff` (E/F/W); stdlib only.
- **Date**: 2026-06-12
- **Exit codes**: `py_compile`: 0 · `ruff E,F,W`: 0 (All checks passed) · smoke: 0 on found op, 1 on not-found, 0 on `--list`.

## Captured output

`endpoint.py postJobBuild` resolves `POST <base_url>/job/{name}/build`; `getQueueItem` resolves the queue-item response schema (executable/why/blocked/cancelled); `--list` prints the CORE operationIds; a bogus opid exits 1 and points at `assets/endpoint-index.md`.

## Caveats

- Resolves the bundled UNOFFICIAL `swaggy-jenkins` spec, which is partial (omits `buildWithParameters`, `consoleText`, arbitrary `job/<n>/<build>/api/json`, copy/stop/doDelete-on-build) and models some ops oddly (e.g. `postJobBuild` lists a `json` query param swaggy-jenkins invented — the official trigger does not need it). The authoritative CORE table is `assets/endpoint-index.md`; the resolver is a schema cross-check only. Both facts are stated in the resolver output + `references/patterns.md`.
- Repo-local `ruff` additionally opts into `D103` (Google-docstring policy for package code) which does not apply to a portable bundled helper; the portable `E,F,W` set is clean.
