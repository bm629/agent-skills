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
reason: irrelevant            # irrelevant | vanished | unavailable — see the table below
bail_rationale: A pure CSS animation library — touches none of the project's scope.
checked_scope: [widget-rendering, plugin-loading]   # optional
```

A repository that could not be fetched carries a `cause` instead of a rationale:

```yaml
schema_version: 1
repo_id: github__acme__rate-limited
skipped: true
reason: unavailable
cause: "429 Too Many Requests (secondary rate limit), 3 attempts over 155s"
```

### The three reasons

| `reason` | Means | Requires |
|---|---|---|
| `irrelevant` | Read on the cheap skim; touches none of the scope | `bail_rationale` |
| `vanished` | The repository does NOT EXIST — a 404, the host says no such repo | `cause` |
| `unavailable` | Exists (or may), but could not be fetched — rate limit, auth wall, timeout, too large | `cause` |

Choose `vanished` only for a DEFINITIVE gone. It is a claim about the world, not about
your session: a 429 or a 401 recorded as `vanished` asserts that a repository someone
else can clone does not exist. When a fetch fails for any other reason, the honest label
is `unavailable`, and the run continues either way — neither is a park.

`bail_rationale` is REQUIRED (and non-trivial) when `reason: irrelevant` — the validator
checks its presence + non-triviality; the reviewer (condition 15) judges whether it is a confident
"touches none", not an uncertainty-drop. `cause` is REQUIRED (and substantive) on
`vanished` and `unavailable`: record the HTTP status or error text verbatim, plus the
attempt count where you retried. A bare `"404"` is a perfectly good cause — the validator
accepts any cause carrying a digit, or ten-plus characters of prose where no numeric
status exists. Without a cause neither label is falsifiable, which is why it is gated
rather than encouraged.

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
