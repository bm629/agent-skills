# validate.py — validation

Deterministic gate for `capability-map.yaml` + `manifest.yaml`. Read-only: reports
failures, never rewrites the files.

## Run

    python validate.py <capability-map.yaml> <manifest.yaml>

Exit 0 + one `OK:` line when every check passes; exit 1 + one `FAIL <rule>: ...`
line per violation otherwise. Requires `pyyaml` + `jsonschema` (baked into the
hq-scheduler image; the discover phases invoke it via Bash).

## Checks

1. `schema` — JSON Schema 2020-12 validation of each file against its sibling
   `../schemas/*.schema.json` (resolved relative to this script, cwd-independent).
2. `uniqueness` — no duplicate capability ids / document ids.
3. `ref-integrity` — capability `depends_on` / `superseded_by` / `merged_into`
   resolve within `product_capabilities`; manifest `documents[].depends_on`
   resolve within `documents`.
4. `acyclicity` — neither the capability `depends_on` graph nor the document
   `depends_on` graph has a cycle.
5. `iso-8601` — `manifest.generated_at` (and `capability-map._meta.generated_at`
   when present) parses as ISO-8601.
6. `cross-file` — every `documents[].scope` is `"system"` or a capability id.
7. enum normalization — kept-enum string fields (e.g. `scale.expected_users`)
   are whitespace-canonicalised in-memory before the schema enum check, so
   `"< 100"` matches `"<100"` without rewriting the file.

## Tests

Fixture suite `test_validate.py` (author-run; the repo has no harness/CI):

    uv run --with pyyaml --with jsonschema --with pytest pytest \
        skills/project-document-discovery/scripts/test_validate.py -q

Covers: a good pair (exit 0); each failure class — schema violation (bad id
pattern), duplicate id, within-file + cross-file dangling refs, a `depends_on`
cycle, a bad timestamp; and the `"< 100"` normalization (exit 0, file unchanged).
Plus the schema-relaxation acceptance/rejection tests (cycles 1–2).

Last run: `11 passed`.
