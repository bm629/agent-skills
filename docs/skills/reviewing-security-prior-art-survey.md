# reviewing-security-prior-art-survey

The acceptance gate over `security-prior-art-survey`'s artifacts — a threat-vocabulary map, a
per-angle search output, and an extract record for one source item.

## Purpose

A survey's later waves build on its search wave, so a dishonest coverage record does not stay
contained: it becomes a confidently wrong claim about what threats exist for a product. This
skill is the independent check that stops that.

It judges **research craft, not the security domain**. Whether a particular weakness matters
to this product is a later wave's question; whether the search that surfaced it was real,
bounded as declared, and honestly recorded is this one's.

`references/conditions.md` holds the numbered bar and is the single authoritative statement
of it — the producer's SKILL.md points at it and restates nothing normative, because the
sibling code-survey pair recorded its own bar drifting when it was mirrored across three
places with no named anchor.

## Inputs, and the one that stops the review

| Input | Required | Used for |
|---|---|---|
| The artifact | always | everything |
| The caller's scope context | all kinds | scope-fit, guard honesty, relevance grounding, bail corroboration |
| The vocabulary map the output ran against | search outputs | coverage completeness |
| The producer's source registry | map and search output | applicability, fallbacks, the declared-set check |
| The angle brief | search outputs | boundary and bounding |

The producer package must be co-installed: its validator and schemas are the mechanical half
of the gate and this skill deliberately does not reimplement them. If a search output arrives
**without its vocabulary map**, the review stops rather than proceeding — the validator cannot
run and coverage completeness is uncomputable, so schema-validity, completeness and
query-provenance would all be unassessed at once, which is most of the bar.

## How it judges

Run the deterministic check once, then spend judgment on what a validator structurally cannot
see. Assert independently — a producer's claim that it "covered everything" is not evidence,
the cells are. Spot-check rather than re-derive: sample a few coverage cells and one candidate
against its own query, and deepen only where a probe fails. Collect every finding in one pass
so a single revision round resolves them.

Emit `VERDICT: approve` or `VERDICT: revise`, preceded by any not-assessed statement, followed
by findings each naming its condition number and a concrete location.

## The bar

Thirty numbered conditions — eight for the vocabulary map, thirteen for the search output, eight
for the extract record, and one applying to every kind. Each carries a `Check:` procedure and
explicit gap / not-a-gap calibration. The wave-2 conditions were appended *above* the existing
set with no renumbering, so anything already citing a condition number stays valid.

The conditions that carry the most weight are the ones closing routes to an honest-looking
artifact representing no real work: a missing coverage cell is indistinguishable from a search
that never ran; a failure or a non-attempt written as a reached zero converts "we could not
look" into "there is nothing there" and survives every other check; an angle whose applicable
set was emptied upstream must say so rather than reading as an empty search; an absent group
type needs a reason the scope corroborates, since the coverage arithmetic is computed from
types; and a candidate must actually appear among the results of the query its provenance
names, because identifiers, counts and provenance are all individually authorable and internal
consistency alone cannot distinguish an angle worked from an angle written.

## Calibration

**No false-revise.** A thin-but-honest result in a thin domain meets the bar; yield is never
a gap. Revise only on a named condition and a concrete failure.

**Proportionality is not leniency.** A real named gap in a thin domain is still a gap.

**Probe asymmetry.** Re-probing a source yourself can prove it reachable now, from your host.
It can never prove it was reachable for the producer at their time from theirs — so a
successful probe is never grounds for a finding against an honest `unreachable`.

**State what you could not assess.** A condition skipped for a missing input is reported above
the verdict, never silently dropped.

## Proven, not asserted

The judgment half of this gate was verified by planting defects that **pass the producer's
validator**: a map recording a group type absent on a reason the scope contradicts, and a
search output retyping an unreachable cell as a reached zero with the retrieval summary
cleaned to match. Both are shape-perfect and internally consistent. Both were caught under
the expected conditions with concrete locations — and the run additionally surfaced two
genuine defects in the producer's own reference fixtures, which is the argument for running
this kind of gate at all.

The extract-record conditions hold the line where a deep read can quietly stop being one: a bail
must be a *relevance* bail and a confident one, since uncertainty keeps the item and the
expensive read is cheaper than a missed threat; a tier must follow from evidence the body agrees
with, not from severity; a control must be the source's, with `stated: false` the honest and
common outcome rather than an invitation to invent one; and aliases must not be confused with
related items, which is what stops synthesis merging two threats or reporting one twice.

## Companion

[`security-prior-art-survey`](security-prior-art-survey.md) — the producer whose artifacts
this gate judges, and whose validator and schemas it treats as authoritative.
