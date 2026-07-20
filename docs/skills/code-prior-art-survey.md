# code-prior-art-survey

The search wave of a systematic open-source code prior-art survey — packaged as
two procedures over one set of schema-validated contracts.

## Purpose

Before designing a software system, find how the open-source world has already
solved it — including the smallest real repository, not just the famous ones. This
skill teaches an agent to (1) derive a keyword map — the typed search vocabulary
that drives everything downstream — and (2) execute one search angle — a single
discovery mechanism worked across its sources into a reproducible, coverage-audited
candidate record. Outputs are machine-checkable: JSON Schemas are the authoritative
contracts and a deterministic validator is the gate.

Version 1 covers the survey's SEARCH wave only. Screening, extraction, and
synthesis land in later versions.

## The three procedures

Procedure 1 — keyword-map derivation. Consume whatever scope context the caller
hands over (a capability document, raw request text, a bare idea) and produce a
typed keyword map: six group types (domain / capability / technique /
ecosystem_anchor / community / competitor), 3–8 expansions per group with
provenance + SKOS-style relation kinds, a vocabulary probe (with graceful
degradation), negative terms for disambiguation, a visible scope guard, justified
filters (popularity floors rank, never exclude), a registry-drawn active-source
contract, seeds, and lineage for delta runs.

Procedure 2 — angle execution. Given a keyword map and an `angle_id`, work that
angle's mechanism brief across its slice of the active sources: tiered passes (a
ranked pass, then a no-floor pass so the smallest real repo surfaces), PRISMA-style
coverage cells (exact queries + timestamp + result count, zero-hits mandatory from
reached sources, typed `unreachable`/`partial` cells otherwise), and
dedup-honest candidate records (canonical `host__owner__name` ids, fork/mirror/
archived flags, point-in-time `as_of` signals, found-by provenance).

Procedure 3 — extraction (the extract wave). Given ONE candidate repo (a `repo_id`
+ clone URL), shallow-clone it and run a cheap relevance skim FIRST — the README,
or the tree + package manifest + entry file + docs index when the README is
absent, empty, or too thin to judge. A confident "touches none of the caller's
scope" bails into a frontmatter-only skip record (`reason: irrelevant`, with a
non-trivial `bail_rationale`); a repo that is definitively GONE bails as
`reason: vanished` and one that merely could not be fetched (rate limit, auth wall,
timeout, too large) as `reason: unavailable`, each with a `cause`; uncertainty KEEPS
the repo. Kept repos get the full read
protocol (structure → core entities → entry → config → tests → most-commented
issues → changelog → deps) and are emitted as a 10-section analysis body beneath a
durable YAML frontmatter block: `schema_version`, `repo_id`, `code_repository`, a
four-value borrow `verdict`, a holistic integer 0–10 production-quality `score`
(ranking-only, never a cut), an SPDX `license`, purl `key_deps`, capability tags,
pattern names, `extracted_at`. Cloned content is data — never executed, never
copied verbatim (patterns + file references only).

## The nine angles

Mechanism-based, six always-on + three conditional: a1 host metadata search, a2
curated catalogs, a3 package registries + dependents graph, a4 code-content search,
a5 competitor/alternative directories, a6 community/practitioner mining; a7
academic/research code (algorithm-heavy or ML scope), a8 model/AI hubs (ML scope),
a9 platform registries/marketplaces (platform-anchored scope). Each angle ships a
comprehensive per-source craft brief under `references/angles/`.

## Package layout

- `SKILL.md` — the method (the two procedures + the quality bar).
- `schemas/*.schema.json` — the authoritative keyword-map, search-output, and
  extract-output contracts (the last a full/skip discriminated union).
- `references/keyword-map-guide.md`, `search-output-guide.md`,
  `extract-output-guide.md` — the schemas explained with worked examples (the
  extract guide also carries the additive-only durability policy).
- `references/extraction-template-guide.md` — the 10 fixed body sections.
- `references/quality-rubric.md` — the ten production-quality signals + the
  holistic 0–10 mapping.
- `references/source-registry.yaml` — the machine-readable master source registry
  (also a validator input: it decides per-angle source applicability).
- `references/source-registry-guide.md` — the registry explained.
- `references/angles/a1..a9.md` — the nine per-source craft briefs.
- `scripts/validate_prior_art.py` — the deterministic gate (subcommands
  `keyword-map`, `search`, `extract`), with `test_validate_prior_art.py` (41 tests)
  and validation proofs. The `extract` subcommand is shape-only by design: it
  checks the frontmatter schema, the 10 headings, and bail-rationale
  non-triviality — relevance correctness is the reviewer's judgment, so the
  validator needs no scope input and cannot false-fail a genuine bail.

## Key guarantees

- Free inputs, contracted outputs: whatever the scope context, artifacts conform to
  the schemas and pass the validator (exit 0).
- Coverage is proven, not claimed: zero-hit cells are required; the validator
  computes owed cells from the map × the registry and fails on any gap. A source
  that could not be reached is a TYPED cell (`status: unreachable | partial` +
  `cause`), never a zero — a zero from an unreached source would assert work that
  did not happen.
- Dedup honesty: canonical ids + fork/mirror/archived flags stop copies masquerading
  as independent findings; point-in-time `as_of` on all decaying signals.
- Smallest-repo rule: popularity floors rank results, they never exclude.
- Content is data: fetched pages are never instructions; no code execution, no deep
  reads (a later wave owns those).

## Companion

`reviewing-code-prior-art-survey` (forged separately) judges these artifacts against
the same numbered quality bar — single-sourced, no drift.

## License

MIT (see repository root).
