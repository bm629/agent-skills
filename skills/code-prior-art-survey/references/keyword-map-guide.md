# Keyword-map guide — the schema explained

The authoritative contract is `schemas/keyword-map.schema.json`; this guide
explains each block and points at the worked example in
`scripts/fixtures/keyword-map.valid.yaml` (validator exit 0 — usable as a
self-test input). Never fork from the schema: on any disagreement, the schema
wins.

## Header — self-description

| field | meaning |
|---|---|
| `version` | schema version; always `2` for this contract |
| `project` | the surveyed project/idea name |
| `request` | the caller's external request/ticket number when its workflow numbers survey runs; omit/null when none exists |
| `mode` | `full` (first survey) or `delta` (net-new scope only) |
| `scope_capabilities` | OPTIONAL. full mode: empty/omitted (everything in scope); delta mode: the net-new capability ids this run covers |
| `created_at` | ISO-8601, quoted in YAML (unquoted timestamps parse as objects) |
| `revision` | starts 1; bumped by any rewrite — maps are never silently edited |
| `lineage.extends` | delta maps: path/reference of the baseline map (else null) |
| `lineage.inherited_group_ids` | groups deliberately NOT re-searched (baseline covered them) |

## `filters` — justified global constraints

Each value doubles as its justification (`recency: active within 24 months
unless stable/complete`). `languages` = the scope's primary IMPLEMENTATION
languages (programming languages, e.g. `[python]`) — search operators like
`language:python` consume it; human/locale reach is a scope-context
judgment, not this field. `popularity_floor` is schema-locked to `none`:
star/download floors may rank results inside a search pass but can never
exclude a candidate from the survey.

## `sources` — the run's search contract

`active`: chosen from `references/source-registry.yaml` (ids only).
`skipped`: the PLAUSIBLY-APPLICABLE sources deliberately not used, each with
a reason ("condition false for this scope") — not an inventory of the whole
registry; sources whose conditional plainly never applied need no entry.
The validator checks reasons exist on what IS listed, not completeness of
the skipped list — that judgment is the reviewer's. Coverage completeness
downstream is computed against `active` — this list is a promise.

## `seeds`

Known-name repositories from model knowledge, captured explicitly (repo, host,
why) instead of pretending search found them. Seeds skip into the caller's
merge pool with their own provenance.

## `probe` — the vocabulary-probe receipt

`performed: true` + `sources` (where you looked: awesome-list headings, topic
tags of 2–3 obvious repos) + `discoveries` (community terms harvested). If the
probe cannot run: `performed: false` and a `reason` (schema-required) — then
expansion proceeds from `extracted` + `model-knowledge` provenances only.

## `groups` — the heart

One group = one search concept: `canonical` term + 3–8 `expansions`.

- `id`: stable slug, `kw-` prefixed (`kw-cap-backtesting`) — coverage cells
  and candidate provenance reference groups by id.
- `type`: `domain` | `capability` | `technique` | `ecosystem_anchor` |
  `community` | `competitor`. Types drive which search mechanisms consume the
  group (the registry maps sources → applicable types).
- `capability`: the capability id when `type: capability` (schema-enforced),
  else null — this is what lets downstream stages check per-capability
  coverage.
- `negative_terms`: words marking a WRONG match, applied by every searcher.
- `expansions[]`: `term` + `provenance` (`extracted` | `model-knowledge` |
  `probe-discovered`) + `relation` (`synonym` | `abbreviation` | `broader` |
  `narrower` | `related` | `spelling-variant`). Terms unique within a group
  (validator-enforced); mix relation kinds. The 3–8 bounds are hard
  (schema-enforced): reach the floor with related-kind terms; a concept that
  cannot support three honest sisters belongs as an expansion inside a
  related group, not as its own group.

## `excluded` — the visible scope guard

Terms considered and rejected, each with a reason. Auditable: a reviewer can
see what was NOT searched and why, instead of guessing.

Convention — absent group TYPES are justified here too: when a whole type has
no group (e.g. no competitor products exist for the scope), add an entry
`term: "<type> (type absent)"` with the reason. That keeps "all six types
considered" checkable from the artifact alone.

## Validation

```bash
python <package>/scripts/validate_prior_art.py keyword-map <map-file>
```

Schema + group-id uniqueness + expansion-term uniqueness + delta-lineage
(delta mode requires `extends`). Fix every FAIL line; hand off only at exit 0.
