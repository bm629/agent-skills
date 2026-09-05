# reviewing-security-prior-art-survey

The acceptance gate over `security-prior-art-survey`'s artifacts — a threat-vocabulary map, a
per-angle search output, an extract record, and the threat register.

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

Thirty-eight numbered conditions — eight for the vocabulary map, thirteen for the search output,
nine for the extract record, seven for the threat register, and one applying to both artifact
kinds. The breakdown is the checkable half: a total corrected on its own summed to thirty-seven
for a revision, because the guard reads the total and cannot see the parts. Each carries a `Check:` procedure and
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

The register conditions guard what synthesis can quietly invent: a threat name coined rather than
bound to a vocabulary, a duplicate row where one vulnerability carries two identifiers, a tier
promoted above its evidence, a control the cited source never prescribed, a coverage receipt that
omits a non-firing angle, and a report issuing mandates in its own voice.

## What 1.3.0 changed, and why

**C38 — an unretrievable item is typed and caused, never dressed as irrelevant.** In the first
live run a reviewer met an extract record skipped as `unavailable`, observed that "C23–30 are
written for extracted records and assume source content is available", and then invented an
acceptance bar of its own. It approved the record, which was the right call on the merits and the
wrong way to reach it: an improvised bar is exactly the drift the single-anchor rule exists to
prevent, and a reviewer with no condition for a shape will always improvise one.

C38 grades that shape the way C11 already grades an `unreachable` coverage cell — a specific
cause, the methods actually tried, relevance stated rather than hedged — and carries the same
probe-asymmetry guard: retrieving the item yourself proves it retrievable now from your host, not
that the producer was dishonest. It is numbered at the end because the bar is append-only, and
cross-referenced from the extract section so it is found where it is needed.

## What 1.4.0 changed

**C5 corroborates in both directions.** It previously asked only that a NEGATIVE angle verdict be
corroborated against the scope. The two directions fail differently and both wave through
cheaply: a wrong negative hides an angle that should have run, while a wrong positive spends a
whole angle on a product the scope already ruled out and fills the register with findings for a
surface that does not exist. A positive verdict is now checked against the field that actually
decides it, and a rationale invoking the absent-input policy for a field the scope does specify
is named as the tell.

## What 1.6.0 changed

**A finding must name the contract it violates.** In a live run a reviewer filed a BLOCKER
demanding the vocabulary map add an `angle_sources` section, without which "the applicable set
cannot be computed". The mapping was never the map's job — it lives in the shipped source
registry, which is why the validator reads both, and the schema forbids the field, so an artifact
that complied would have been invalid. The validator exited 0 on the artifact under review.

The existing rule said not to redefine the producer's schemas. This reviewer did not contradict a
schema; it ADDED to one, which the rule did not cover. Now: the contracts are the schemas, the
registry and the angle briefs, a requirement you cannot point to in one of those is not a
finding, and "the artifact should also carry X" is a design proposal recorded as an observation.
The cost of getting this wrong is concrete — a revise round, and at the cap a park that summons a
human for work that was correct.

## Companion

[`security-prior-art-survey`](security-prior-art-survey.md) — the producer whose artifacts
this gate judges, and whose validator and schemas it treats as authoritative.
