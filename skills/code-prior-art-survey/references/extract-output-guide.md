# Extract-output guide (the frontmatter schema)

`schemas/extract-output.schema.json` is authoritative; this guide explains it. The
extract record is `extract/<repo_id>.md` — a YAML frontmatter block above the 10-section
body (`extraction-template-guide.md`). The frontmatter is a discriminated union.

## Full extraction (a repo that was deep-read)

```yaml
schema_version: 1
repo_id: github__acme__widget-engine        # <host>__<owner>__<name>, threads all waves
code_repository: https://github.com/acme/widget-engine   # adapted from schema.org codeRepository
verdict: borrow-patterns                     # borrow-architecture | borrow-patterns | reference-failure-modes | discard
score: 7                                     # holistic 0-10 (quality-rubric.md); ranking-only
license: Apache-2.0                          # an SPDX id / expression (MIT OR Apache-2.0) — not free text
key_deps:                                    # Package-URL (purl) strings — not bare names
  - pkg:pypi/pydantic
capability_tags: [widget-rendering]
pattern_names: [plugin-registry]
extracted_at: 2026-07-19T00:00:00Z
```

## Skip record (a bail — no body)

```yaml
schema_version: 1
repo_id: github__acme__css-spinner
skipped: true
reason: irrelevant            # irrelevant (bailed on the cheap skim) | vanished (clone failed / gone)
bail_rationale: A pure CSS animation library — touches none of the project's scope.
checked_scope: [widget-rendering, plugin-loading]   # optional
```

`bail_rationale` is REQUIRED (and non-trivial) when `reason: irrelevant` — the validator
checks its presence + non-triviality; the reviewer (condition 15) judges whether it is a confident
"touches none", not an uncertainty-drop. A `vanished` skip needs no rationale.

## What the validator checks (shape + completeness only — OQ-C)

`validate_prior_art.py extract <file>` parses the frontmatter, validates it against the
schema (verdict/reason enums, `score` 0–10, SPDX-shaped `license`, purl-shaped
`key_deps`), checks the 10 body headings for a full extraction, and checks
`bail_rationale` presence for an `irrelevant` skip. It takes NO capability-map/context
input — relevance correctness is a reviewer judgment, never the validator's.

## Durability policy

The record outlives the code that reads it, so the schema evolves **additively only**:
never remove or repurpose a field; enums are frozen-but-extensible (growth = a minor
version bump, gated by `schema_version`); reuse externally-owned vocabularies (SPDX,
purl, schema.org) rather than inventing identifiers that rot. This keeps a years-old
record interpretable and crosswalkable to CodeMeta / SBOM tooling.
