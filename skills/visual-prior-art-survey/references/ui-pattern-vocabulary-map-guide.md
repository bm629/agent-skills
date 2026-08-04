# The UI-pattern vocabulary map, explained

The map is a SEARCH PROTOCOL, not a glossary. It exists so a later reader can re-run what you
ran and tell the difference between "no documented convention exists" and "we searched badly".
Produced once, in wave 0; every angle queries from it rather than from its own recall.

Schema: `schemas/ui-pattern-vocabulary-map.schema.json`. Gate:
`validate_visual_prior_art.py keyword-map <file>`.

## The five axes

| Type | What it holds | Queried by |
| --- | --- | --- |
| `component` | The widgets the screens contain — table, combobox, dialog | a1, a2, b1, b3, b5 |
| `pattern` | Interaction patterns — progressive disclosure, undo, empty state | a1, a2, b1, b2, b4 |
| `screen-archetype` | The KIND of screen — admin console, settings, onboarding | a1, b2, b4, b5 |
| `platform-context` | The platform whose guidelines bind | b1 |
| `design-system` | Published systems to walk | a1, b5 |

Every axis carrying no group is listed in `scope_guard.absent_types` with a reason. A type that
is neither present nor declared is a silent omission, and it silently empties every angle that
depends on it — the gate rejects that.

`component` and `pattern` are the highest-leverage axes: they are what a2 selects normative
contracts by, and a2 is the angle whose output does not go stale between projects.

## Expansions

Canonical term plus expansions, each with a SKOS `relation` (`broader`, `narrower`, `related`,
`alt-label`) and an honest `provenance` — `extracted` claims a real corpus used the term,
`model-knowledge` says you supplied it, `probe-discovered` came from a live probe.

Provenance is not decoration. A map that is entirely `model-knowledge` has not been grounded in
anything, and should say so in its assumptions rather than implying research it did not do.

`expansion_cap` is the ceiling YOU commit to for that group before expanding it — a
self-imposed bound recorded so a reader can see you stopped deliberately rather than ran out of
ideas. Set it from how much genuine vocabulary the concept carries: a widely-named component
supports six or eight, a system name supports three. It binds the expansion list that follows
it, and the gate rejects a group that exceeds its own declared cap.

Floor of three per group; below that record `short_reason` — **never pad**. A padded group
manufactures queries that return noise, and noise costs a full deep read per false candidate.
A design-system group legitimately sits at the floor: a system name has no sister terms, only
vendor and spelling variants.

If no group shows more than one relation kind, the gate fails the map. A map of nothing but
`alt-label` expansions is a spelling list, not an expansion.

## Negative terms — required on `design-system` groups ONLY

The gate enforces it there and nowhere else, and the asymmetry is deliberate.

Most of this corpus is keyed by stable identifiers — `ARIA-combobox`, `WCAG-2.4.11`,
`DP-confirmshaming`. Those never collide, and demanding exclusions for them would manufacture
filler. But a1's first step is discovering design systems **by name**, and Polaris, Primer,
Carbon, Fluent, Spectrum and Lightning all collide with ordinary language and with unrelated
products. A search built from such a group cannot be made precise afterwards — the noise is
already in the result set.

Write them from the collisions you can actually foresee: `carbon emissions`, `carbon fibre` for
Carbon; `spectrum analyser` for Spectrum.

## Angle applicability

One verdict per registry angle, each with its precondition, a boolean `holds`, and a reason
grounded in the capability map's actual values — not "seems relevant".

The gate checks both directions: every registry angle needs a verdict, a verdict naming an
unknown angle is rejected, and **an always-on angle can never be recorded as `holds: false`**.
No map may switch one off; that is how a survey silently does nothing.

**On conditional angles.** Several preconditions are disjunctions where one leg rests on an
optional capability field. That is legitimate and the registry records those as `widening_legs`:
an optional leg beside a required one only ever ADDS firings, so it fails open. What would fail
closed — and what the registry's `trigger_anchor` list exists to prevent — is a predicate whose
*only* leg is optional, which silently never fires for any map that omitted the field.

## Sources and stamps

Every source is `active` (you read it) or `skipped` (you did not), both with a cause. Each active
source records `release` (or `rolling`), `as_of`, an `access` status, and a `sanitization` result.

**Record the sanitization result here** — a coverage cell has no field for it. That is the only
place the posture is checkable rather than asserted.

A source with `access: forbidden-by-terms` may never appear in `active`; recording a source you
deliberately did not read as one you read is a false receipt, and the gate rejects it.

## Assumptions

Every value the absent-input policy forced, with the SIGNAL it was inferred from — never a
rationale. "No level was declared and the downstream consumer requires AA unconditionally" is a
signal; "AA seemed sensible" is not. See `absent-input-policy.md`.

## Worked example (abridged)

```yaml
schema_version: 1
meta: {as_of: "2026-08-04T09:00:00Z", revision: 1}
groups:
  - id: data-table
    type: component
    canonical: data table
    expansion_cap: 6
    expansions:
      - {term: grid, provenance: extracted, relation: alt-label}
      - {term: treegrid, provenance: extracted, relation: related}
      - {term: list view, provenance: model-knowledge, relation: broader}
  - id: carbon
    type: design-system
    canonical: IBM Carbon
    expansion_cap: 3
    negative_terms: ["carbon emissions", "carbon fibre"]
    short_reason: A system name has no sister terms — only vendor and spelling variants.
    expansions:
      - {term: Carbon Design System, provenance: extracted, relation: alt-label}
angle_applicability:
  - {angle_id: a2, precondition: always applicable, holds: true,
     reason: "The named components are all ARIA-specified patterns."}
sources:
  active:
    - {id: aria-apg, release: rolling, as_of: "2026-08-04T09:00:00Z", access: open,
       sanitization: {status: sanitized}}
  skipped:
    - {id: mobbin, cause: "Excluded on modality and terms.", access: forbidden-by-terms}
```

The full fixture is `scripts/fixtures/ui-pattern-vocabulary-map.valid.yaml`.
