# The seeded `category` vocabulary

`category` on a candidate is a **frozen-but-extensible VOCABULARY**, not an enum. No rule can close
it, and calling it an enum would promise a closed set this type cannot close.

Four sites judge against this list — the absent-input policy, the reviewing twin's C13, the schema's
`category` description, and the map guide's `category` axis. It ships here so all four can.

Everything below is TRANSCRIBED from the two named sources. An earlier version of this file was
written from memory and got all three of its claims wrong: two of the five classification keys were
invented, three measured members were missing, and the tie-break was stated backwards.

## Source 1 — the five classification keys

From `project-document-discovery/references/classification-schema.md:45`, verbatim:

`payments` · `identity` · `communication` · `data_providers` · `analytics`

## Source 2 — the measured Nango taxonomy

The coordinator recorded 981 providers over 31 categories on 2026-08-22, naming nineteen by count:

`productivity` 200 · `dev-tools` 134 · `marketing` 100 · `crm` 88 · `communication` 67 · `hr` 67 ·
`e-commerce` 59 · `analytics` 58 · `accounting` 53 · `support` 46 · `ticketing` 42 · `erp` 38 ·
`payment` 38 · `ats` 35 · `mcp` 30 · `social` 30 · `design` 27 · `iam` 24 · `legal` 24

**Re-measured 2026-09-03** — 990 providers, still 31 categories. The nineteen above all survive with
small drift, and these twelve complete the set:

`other` 58 · `popular` 36 · `knowledge-base` 22 · `video` 19 · `invoicing` 18 · `storage` 18 ·
`surveys` 14 · `banking` 14 · `cms` 13 · `sports` 12 · `gaming` 6 · `search` 2

Command: fetch `providers.yaml`, `Counter(c for v in rows.values() for c in v["categories"])`.

## Where the two disagree, the UPSTREAM spelling wins

`payments`, not `payment`. The coordinator states the reason and it is not stylistic: *"the join
with the capability map is what the field exists for"* — a candidate recorded under the catalog's
spelling cannot be joined to the capability that motivated the survey.

So the catalog's `payment` is a spelling you will SEE and must not RECORD. Carry it as an
`expansions` entry on the `payments` group instead, which is what the calibration map does.

**An earlier version of this file said the opposite**, and a test pinned the wrong half. Both the
type spec and the coordinator spec decide for upstream.

## Using a value that is not here

Legal, and the point of "extensible". Record it and put its provenance in `notes[]` — which catalog
or descriptor used it, and where you read it. **A value invented silently is not legal; a value
observed in the corpus and sourced is.**

`scheduling` is the worked example: it is in neither source, it is what the calibration scope
actually integrates around, and the calibration fixture records it WITH its provenance note.
