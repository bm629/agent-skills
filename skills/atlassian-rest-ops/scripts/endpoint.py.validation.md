# Validation: endpoint.py

- **Method**: syntax check (`py_compile`) + functional runs against the bundled specs
- **Tools**: python3 (stdlib only), `python3 -m py_compile`
- **Date**: 2026-05-31
- **Exit codes**: py_compile: 0 · valid op: 0 · missing op: 1 · bad usage: 2

## Captured output

- `confluence createPage` → request body resolved to `{ spaceId*, status, title, parentId, body{ representation ∈ [storage, atlas_doc_format, wiki], value }, subtype }` (oneOf representations).
- `jira createIssue` → `fields` (free-form object — populate per project/screen), `historyMetadata` (allOf; deep nodes capped with "… (max depth)").
- `confluence getPages` → `cursor` + `limit` params (cursor pagination).
- `jira searchAndReconsileIssuesUsingJql` → `nextPageToken` + `maxResults` params (token pagination).
- bad operationId → `exit 1` with "operationId '…' not found".

## Caveats

- Resolves to bounded depth (request `MAXDEPTH=5`, response depth 3) — very deep/recursive Jira schemas show `… (max depth)` / `→ X (recursive)`; rerun on a specific sub-schema's `$ref` if you need it.
- Jira `fields` is intentionally a free-form object in the spec (dynamic per project/screen).
