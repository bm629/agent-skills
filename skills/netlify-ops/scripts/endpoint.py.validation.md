# Validation: endpoint.py

- **Method**: `python -m py_compile`; lint (`ruff check --select E,F,W`); smoke against the bundled spec.
- **Tools**: `python3 -m py_compile`; `ruff` (E/F/W); stdlib only.
- **Date**: 2026-06-12
- **Exit codes**: `py_compile`: 0 · `ruff E,F,W`: 0 (All checks passed) · smoke: 0 on found op, 1 on not-found, 0 on `--list`.

## Captured output

`endpoint.py createSiteDeploy` resolves the inline `deploy` body (files digest / zip / draft / async / functions); `updateSite` resolves `site_id` (path, required — merged from the path-level params) + the `site` body (custom_domain, domain_aliases) + the response. `--list` enumerates all operationIds. A bogus opid exits 1 with a pointer to `assets/endpoint-index.md`.

## Caveats

- The spec is **Swagger 2.0**, so the resolver handles `#/definitions` refs, `in: body` params (with `.schema`), `allOf`, and **path-level parameters** (Swagger shares them across methods — merged so `site_id` shows for updateSite/createSiteDeploy).
- Repo-local `ruff` additionally opts into `D103` (Google-docstring policy for package code) which does not apply to a portable bundled helper; the portable `E,F,W` set is clean.
