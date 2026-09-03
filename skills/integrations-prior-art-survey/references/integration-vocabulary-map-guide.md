# Building the integration vocabulary map (wave 0)

The map is the scope for every angle that follows. Build it before any angle runs.

## The envelope

`schema_version` is `1` and is the first thing a reader checks: a map with no version cannot be
told from a map built against a contract that has since moved.

`meta` carries `retrieved_at`, `revision`, `scope_ref` and `classification`. **`classification` is
REQUIRED and non-empty** — every `angle_applicability` verdict is checked against it, and a map
recording none leaves all eight unfalsifiable.

`notes[]` is free prose for what a reader would otherwise have to re-derive. **`assumptions[]` is
where you record what you had to ASSUME to build the map** — a term you read into the domain, a
seed-product list you derived rather than were handed. An assumption recorded is a thing the
reviewer can disagree with; an assumption left in your head is not.

## The six axes, each with a declared SOURCE

An axis whose input is undeclared has no bootstrap, which is why every one of the six names where
its terms come from.

| axis | source of its terms |
| --- | --- |
| `category` | the capability map's capabilities, mapped to the `category` vocabulary |
| `capability` | `capability-map.yaml` verbatim |
| `service` | `integrations.third_party_list` when present |
| `pattern` | `integrations.patterns` when present, else derived from `archetype.primary` + `scale.real_time` |
| `domain-noun` | the domain, with `context.md` as colour only |
| `seed-product` | the a1 catalogs' own vendor lists and category directories — **never another angle's output** |

An axis with no group goes in `scope_guard.absent_types` with a reason the capability map actually
supports. `pattern` is the standing candidate: it is reachable only through the conditional `b2`.

## What each group carries

`expansion_cap` is REQUIRED and bounds the query TERMS inside the group. It does NOT bound the cell
count — the cell is keyed `(group_id, source_id)`.

`negative_terms` is required on `category` and `domain-noun` groups, where the words are ordinary
English and the false-positive corpus is large.

At least two expansions on `category`, `capability`, `domain-noun` and `pattern` — the four axes the
corpus spells more than one way. NOT on `service` or `seed-product`, where the canonical is a proper
noun the corpus spells once, and demanding expansions there would demand invented spellings.

## The capability-coverage obligation

Every capability in the capability map maps to at least one `category` group, or is recorded in
`scope_guard.excluded[]` with its reason — so `excluded[].item` may be an uncovered CAPABILITY as
well as a term.

**RECORDING it is this artifact's job; CHECKING it is not.** Nothing in this package's validator can
see `capability-map.yaml`. The set-difference is owned deterministically by the coordinator's
keyword-map ticket, and the reviewing twin carries a condition as a second pass. Three places, each
with a named owner.

## The probe

THREE requests, not eight: one to each of the two always-on terminals that have a single URL
(`nango-providers` for a1, `apis-guru` for a2), plus one resolving a name from the map's own
`service` group. a3's terminal is `vendor-docs`, which is per-vendor with no single URL to probe —
which is why the third check is the service-group resolution rather than a fourth terminal.

Three cheap checks beat eight children dispatched against a vocabulary that reaches nothing. Record
the note: a zero here is a finding about the corpus rather than a failure, and a probe with no note
says neither.

## Worked example

`scripts/fixtures/integration-vocabulary-map.valid.yaml` is the calibration fixture and validates
clean:

```
uv run --with pyyaml --with jsonschema python scripts/validate_integrations_prior_art.py \
  keyword-map scripts/fixtures/integration-vocabulary-map.valid.yaml
```

It picks a scope where SEVEN angles hold and `b5` does not, so the always-on/conditional split is
exercised in both directions.
