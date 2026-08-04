# The bar — numbered conditions

**This file is the authoritative bar for the pair.** The producing skill points here; where the
two differ, this file wins. Single-sourcing the bar is what stops a producer and a reviewer
grading the same artifact by different rules.

Each condition is checkable: an artifact meets it or fails it. A condition names its
**evidence** — anything you cannot ground in the artifact, its schemas, or the source registry is
an OBSERVATION, not a finding. An ungrounded finding costs a revise round and, at the cap, parks
correct work.

**Do not restate the deterministic gate.** Conditions marked *(gated)* are enforced
mechanically; check them only if the validator was not run. Your value is the judgment half.

---

## Conditions 1–9 — UI-pattern vocabulary map

**C1 — Every group type is accounted for.** *(gated)* Present, or in `scope_guard.absent_types`
with a reason.

**C2 — The component and pattern groups describe THIS product's screens.** They are what the
normative angle selects contracts by, so a generic widget catalogue is worse than a short honest
one. *Revise if:* groups name components the scope never implies.

**C3 — Screen archetypes are named, or their absence is explained.** Without them the
domain-convention angle has nothing to query and the survey silently narrows to generic
convention. *Revise if:* absent with no scope note.

**C4 — Negative terms on `design-system` groups are real exclusions.** *(gated for presence.)*
Judge whether they exclude the collisions the name will actually hit — `carbon emissions` is
real; `unrelated` is filler. Their absence on other group types is correct, not an omission.

**C5 — Expansions are honestly typed.** `provenance: extracted` claims a real corpus used the
term. A map that is entirely `model-knowledge` has not been grounded and should say so in its
assumptions rather than implying research it did not do.

**C6 — Thin groups are folded or explained, never padded.** *(gated for `short_reason`.)* Judge
whether the reason is true — a design-system name legitimately has no sister terms.

**C7 — Angle verdicts are grounded in the scope's actual values**, not a general impression.
*Revise if:* a reason reads "seems relevant".

**C8 — Assumptions name a signal, not a rationale.** "No level was declared and the downstream
consumer requires AA unconditionally" is a signal; "AA seemed sensible" is not.

**C9 — The sanitization result is recorded per active source.** *(gated for presence.)* This is
the only place the posture is checkable — a coverage cell has no field for it.

---

## Conditions 10–22 — per-angle search output

**C10 — Queries are recorded as run.** *(gated for presence.)* Judge reproducibility: for a
corpus walk, could someone else reach the same set from what is written? *Revise if:* a
traversal is described rather than reproduced.

**C11 — Coverage is complete in both directions.** *(gated.)*

**C12 — A zero, a failure and a refusal are never conflated.** The central condition. A
`reached` cell with `returned: 0` is a receipt the search ran; an `unreachable` cell is a failure
with a cause; a `forbidden-by-terms` cell is a *decision*. *Revise if:* any is recorded as
another — this is the defect the artifact exists to prevent.

**C13 — Causes are specific.** "Not worth it" is not a cause. "Two pattern pages returned
incomplete documents on both attempts; the index read normally" is.

**C14 — `kept` reconciles.** *(gated for arithmetic.)* Judge whether the number is credible
against the queries and the rows carried.

**C15 — A bound cap says what it dropped, in kind.** *(gated for presence.)* Judge whether
`dropped_note` describes the tail rather than restating that a cap exists.

**C16 — Every candidate's cited corpus actually contains the convention claimed.** The condition
a planted defect targets most often. A resolvable URL and a plausible release are not evidence
that the corpus says what the record says it says. *Revise if:* the relevance line asserts a
contract the cited page does not carry.

**C17 — The `unadmitted` array carries a real reason for every dropped candidate.** *(gated for presence.)* A silent drop makes
"we did not look" indistinguishable from "we looked and found nothing".

**C18 — Identity is corpus-scoped and honest.** *(gated for shape.)* Judge that a design-system
record covers one SYSTEM with its catalog in the body — not one record per component, which
would produce hundreds of rows for one governed system.

**C19 — `authority` and `prescriptivity` are both recorded and are not confused.** Authority is
*who says it*; prescriptivity is *whether it binds*. A design system stating a rule in imperative
prose is still `descriptive`. *Revise if:* a system's opinion is marked `normative`.

**C20 — `corpus_version` is present and meaningful, and distinct from `as_of`.** *(gated for
presence.)* `as_of` is when you read it; `corpus_version` is which release you read. Judge that
the version identifies a release rather than restating the fetch date — every corpus here
versions independently, so the two are different facts and a record carrying only one is not
re-checkable.

**C21 — A claimed `token_format` is DTCG and versioned.** *(gated.)* Judge whether the claim
matches what the cited system actually publishes.

**C22 — No screenshot-gallery source was reached.** *(gated for the excluded list.)* Judge the
borderline: a gallery's content quoted from a secondary article is still gallery content.

---

## Conditions 23–26 — both artifact kinds

**C23 — Novelty is phrased as a search result.** "No documented convention found across N angles
and M terms", never "there is no convention". *Revise if:* the artifact asserts absence as fact.

**C24 — Nothing was fetched in breach of a source's terms.** Judge the borderline, not only the
excluded list.

**C25 — Secondary commentary is never the citation.** A gallery, index or listicle may seed a
candidate; the record must cite the system's own documentation. *Revise if:* an index's summary
stands in for the source.

**C26 — The domain-neutrality limit is not overstated away.** The artifact must not present
general convention as domain-specific screen guidance. *Revise if:* a record claims a screen
composition the cited corpus does not address.

---

## Condition 27 — proportionality

**C27 — A thin-but-honest artifact is correct output for a narrow UI.**

**Do not revise for thinness alone.** A simple admin console has few components, the
domain-convention angle legitimately returns zeros for many domains, and a short map with honest
reasons is a correct result. Revising it invites padding, which is a worse artifact than a thin
one. Revise only when a specific gap is *unrecorded*: a query not run and not explained, a source
not attempted and not noted, a candidate dropped without a reason.

The question is never "is there enough here?" It is "is what is missing accounted for?"

---

## Applying the bar

1. Run the deterministic gate first if it has not run. Its failures are the producer's to fix
   before review, not your findings.
2. Walk the judgment conditions in order.
3. For each finding, name the condition number and quote the artifact text that fails it.
4. Emit exactly one verdict line: `VERDICT: approve` or `VERDICT: revise`.
5. On `revise`, list every finding in one pass — a reviewer who reports one problem at a time
   costs a revise round per finding, and the loop caps out on correct work.

**Your evidence is the artifact, its schemas, and `source-registry.yaml`.** Not your own taste in
interfaces: if you believe a convention is missing, the finding is that the angle's coverage does
not account for it, not that you would have designed it differently.
