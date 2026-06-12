# Validation: endpoint.py

- **Method**: `python -m py_compile`; lint (`ruff check --select E,F,W`); smoke against the bundled Pages slice.
- **Tools**: `python3 -m py_compile`; `ruff` (E/F/W); stdlib only.
- **Date**: 2026-06-12
- **Exit codes**: `py_compile`: 0 · `ruff E,F,W`: 0 (All checks passed) · smoke: 0 on found op, 1 on not-found, 0 on `--list`.

## Captured output

`endpoint.py pages-project-create-project` resolves `account_id` (path, required) + the JSON body (`name`*, `production_branch`*, build_config, deployment_configs, source) + the response envelope. `pages-deployment-create-deployment` correctly flags the `multipart/form-data` body as "use `wrangler pages deploy`, not a curl". `pages-domains-add-domain` resolves the required `name` body. `--list` enumerates the 20 ops. A bogus opid exits 1 with a pointer to `assets/endpoint-index.md`.

## Caveats

- The bundle is the **Pages-only slice** of Cloudflare's 10 MB official OpenAPI (11 account-pages paths + their transitive `$ref` closure; 0 dangling refs). The resolver handles OpenAPI 3.0.x (`components/schemas`, `requestBody.content`, `allOf`/`oneOf`/`anyOf`, path-level params merged).
- Repo-local `ruff` additionally opts into `D103` (Google-docstring policy for package code) which does not apply to a portable bundled helper; the portable `E,F,W` set is clean.
