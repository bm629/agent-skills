# Source-registry guide

`references/source-registry.yaml` is the versioned master catalog of search
sources — machine-readable and a VALIDATOR INPUT, not prose. Entry fields:

| field | meaning |
|---|---|
| `id` | stable source id — keyword maps (`sources.active`/`skipped`) and coverage cells reference it |
| `angle` | which angle (a1..a9) works this source |
| `tier` | signal-to-noise rank (1 = highest); work tier-first |
| `conditional` | null = always applicable, else the condition that activates it ("domain is cloud-native/infra-adjacent") |
| `group_types` | which keyword-group types this source is queried with — the applicability half of coverage completeness |
| `how_to` | one-line method pointer; the full craft lives in the angle brief |
| `fallbacks` | source ids to lean on when this one is unreachable (channels die) |
| `last_verified` | date the entry was last confirmed alive/accurate — staleness is visible |

## How the validator consumes it

For a search output with `meta.angle_id = aN`, the applicable pairs are:

```
{ (group, source) | source.angle == aN
                    AND source.id ∈ map.sources.active
                    AND group.type ∈ source.group_types }
```

Every applicable pair needs a coverage cell (zero-hit cells included).

## Maintenance rules

- Source lists live ONLY here — angle briefs reference ids, never duplicate
  the list. A channel death is: update the entry here (or its fallbacks),
  amend the affected brief's craft section, bump `updated`.
- New source: add the entry with all fields + `last_verified`, then extend
  the angle brief with its craft section.
- Conditional sources stay in the registry even when inactive for a given
  run — the keyword map's `skipped` list records the per-run decision with a
  reason.
- Never remove an entry for being low-yield; low yield is what `tier` and
  zero-hit cells are for. Remove only what no longer exists.
