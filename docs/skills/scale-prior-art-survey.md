# `scale-prior-art-survey`

Establish how comparable systems actually behaved under load — before the architecture commits to
a datastore, a topology or a capacity plan the published evidence does not support.

**All four kinds.** The scale vocabulary map, one angle's search output, one source's episodes,
and the scale envelope index a later ADR is written against.

## The organising idea

What ages in a scale claim is not the argument. It is the **hardware and managed-service
generation underneath it**. A 2016 result on spinning disks is not wrong; it is un-transferable,
and an undated one cannot even be placed.

So admission requires a stated version or date as a hard conjunct alongside a resolvable URL, and
every episode carries a `transferability{level, reason}` that is **never folded into
`confidence`**. Those two fields are the type's founding risk made structural: a high-confidence
measurement three bands above this project is LOW transferability, and saying so is the design
working rather than a complaint about the source.

## Ten angles, three always-on

`a1` first-party engineering narratives · `a2` peer-reviewed systems literature · `a3` the
operational canon — these three run on every survey this type triggers. Then seven conditional:
`b1` tail-latency, `b2` geo-distribution and consistency, `b3` incidents and post-mortems, `b4`
capacity envelopes, `b5` independent benchmarks, `b6` inference serving, `b7` multi-tenancy.

**The smoke floor is FOUR, and that is a declared deviation.** Every disjunct of the type trigger
fires at least one conditional angle, so 3 always-on + 1 is the cheapest legitimate run. There is
no way under it: a minimum-enum map fires no disjunct and the survey never runs at all.

## Every cap was MEASURED, and the measurement changed one of them

- **`a3` = 184, and it is a UNION.** 44 (SRE Book) + 30 (SRE Workbook) + 44 (Azure Cloud Design
  Patterns) + 66 (GCP Architecture Framework). The cap rose from 25, because a cap below an
  angle's enumerable set truncates a corpus it could have walked. The AWS Builders' Library is
  excluded from the count: its listing is not isolable by fetch, and a cap cannot be sized against
  what cannot be counted.
- **`b3` = 30, a BUDGET below a measured FLOOR of 104.** Two of six listings yielded 104
  load-caused entries and two more are unbounded time series. No number clears the corpus, which
  is exactly why b3's blast-radius-then-recency ordering is load-bearing rather than decorative.
- **`b7` = 20, a BUDGET over an UNCOUNTABLE corpus.** Neither corpus its sizing names can be
  counted, and each says why in the registry.

## The load-band table, and the honest negative

The classification schema gives band NAMES and no boundaries, so this pair owed a table. Two live
searches found no published numeric boundary for `concurrency` or `data_volume` — the sources
define them by simultaneity and by context, and give incompatible figures for the same word — and
`real_time`'s bands are distinguished by the CONSEQUENCE of missing a deadline, not its length.

All three go in a MACHINE-READABLE `unsourced_dimensions` list, not in prose, because the
validator reads it to know what to skip. `availability_target` is the one sourced dimension: its
enum members are numeric literals, so the enum is the table.

`geo_distribution` is deliberately NOT in that list. It is skipped by CONSTRUCTION — non-ordinal,
so no adjacent pair exists — and collapsing the two mechanisms is what would make a later
discovery invisible.

## What the deterministic gate checks

**117 rules**, with ids per CLAUSE rather than per family, each mapped to the plan task that owns it in
`references/rule-owners.yaml`, and the key set asserted EQUAL to the ids an AST walk yields.

The exit contract is tested per rule: `schema` is exit 1 because an artifact failing a schema that
LOADED is what its author repairs; `schema-unavailable` is exit 2 because an unloadable schema
FILE is ours. The registry and angle-block families are exit 2 for the same reason.

**The synthesis gate takes TWO inputs and refuses to run on one.** Every `evidence[]` id must
resolve to an extracted episode, and the FROZEN extraction queue is reconciled against the records
on disk in BOTH directions — a row that produced no file, and a file no row asked for. Nothing
else can see either: the index and the records show only what exists. So omitting `--extracts` or
`--queue` prints its own SKIP line and exits 1 rather than passing quietly, and passing one that
is UNUSABLE names its own cause and exits 2 — the artifact's author did not write those files, a
sibling wave did. A flag that is silently ignorable is a lie in the CLI; a flag whose ABSENCE is
silently tolerated is the same lie one move later; and a flag whose contents are unreadable must
not be reported as the artifact being wrong.

That last one is checked as a MATRIX rather than a list — every sibling-wave input (`--keyword-map`,
the extracts directory, each record in it, `--queue`) crossed with every unusable shape (missing,
wrong kind of path, unparseable, parsing to a non-mapping, empty, partially unreadable) — under one
invariant: every finding such a run emits is a package fault. Enumerating the flags mechanically
and the shapes from memory is how two of those shapes shipped, one of them turning six citations
that resolve into six that reportedly do not.

**There is deliberately no rule that every record be CITED.** One was built and removed the same
day. The quality filter ranks and never cuts, the synthesis agent does not own the wave-2 records,
and the escape the rule offered — re-record it as `outcome: skipped` — is schema-forbidden to keep
its content, so its cheapest route to exit 0 was padding an area with a record that does not
support it. The queue is the manifest; the index is not.

**32 registry rows in a fallback FOREST, walked rather than described** — nine terminals declare
`fallback: null` with a rationale, because requiring every row to name a fallback in a finite graph
guarantees a cycle by pigeonhole. It did: the first draft had seven.

## What it deliberately does NOT check

It never fetches. Whether a URL resolves to what the row claims, whether a quote supports its
claim, whether `configuration_stated: true` is honest, whether `primary_dimension` names the
dimension the episode actually measured — none is decidable without a request. That last one is
**demoted from the validator by design**: no signal-to-dimension mapping exists upstream, so a
rule deciding it would be deterministic on an invention. The reviewing twin carries it, and if
that condition does not, nothing does.

## Install

```
npx skills add bm629/agent-skills@scale-prior-art-survey
npx skills add bm629/agent-skills@reviewing-scale-prior-art-survey
```
