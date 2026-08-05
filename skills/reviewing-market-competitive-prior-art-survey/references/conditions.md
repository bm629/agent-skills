# The bar — numbered conditions

**This file is the authoritative bar for the pair.** The producing skill points here; where the
two differ, this file wins. Single-sourcing the bar is what stops a producer and a reviewer
drifting into grading the same artifact by different rules.

Each condition is checkable: an artifact meets it or fails it. A condition names what it needs
as **evidence** — anything you cannot ground in the artifact, its schema, or the source registry
is an OBSERVATION, not a finding. An ungrounded finding costs a revise round and, at the cap,
parks correct work.

**Do not restate the deterministic gate.** Conditions marked *(gated)* are already enforced
mechanically; you check them only if the validator was not run. Your value is in the judgment
conditions.

---

## Conditions 1–9 — market vocabulary map

**C1 — Every group type is accounted for.** *(gated)* Present, or listed in
`scope_guard.absent_types` with a reason.

**C2 — The `job-to-be-done` axis genuinely finds substitutes.** The phrasings describe the
user's *need*, not the product's category in other words. A job group that paraphrases the
category is the commonest way a set ends up containing only direct competitors.
*Evidence:* compare the job group's terms against the category group's. *Revise if:* they are
synonyms.

**C3 — Non-consumption is reachable.** "Do it manually", a spreadsheet, an internal script — one
of the job or category groups must be able to surface it, or the scope note must say why the
market has no manual alternative. *Revise if:* absent with no explanation.

**C4 — Negative terms are real exclusions.** *(gated for presence.)* Judge whether they exclude
the collisions this vocabulary will actually hit. `["team building"]` on a
"team collaboration" group is real; `["unrelated"]` is filler.

**C5 — Expansions are honestly typed.** `provenance: extracted` claims a real source used the
term. A map that is entirely `model-knowledge` has not been grounded in anything, and should say
so in its assumptions rather than implying research it did not do.

**C6 — Thin groups are folded or explained, never padded.** *(gated for `short_reason`
presence.)* Judge whether the reason is true — a product-name group legitimately has no sister
terms; a category group with two expansions usually means the category was mis-named.

**C7 — Angle verdicts are grounded in the scope's actual values.** Each reason cites what the
scope says, not a general impression. *Revise if:* a reason reads "seems relevant".

**C8 — Assumptions name a signal, not a rationale.** "The scope names tiered hosted pricing" is
a signal; "it seemed likely" is not.

**C9 — Excluded sources are excluded for their own stated reason.** A source barred by its terms
and one that failed to load are different facts and must not share a cause.

---

## Conditions 10–22 — per-angle search output

**C10 — Queries are recorded as run.** *(gated for presence.)* Judge reproducibility: could you
paste this string into that source and get a comparable result? *Revise if:* a query is
described rather than reproduced.

**C11 — Coverage is complete in both directions.** *(gated.)*

**C12 — A zero and a failure are never conflated.** The central condition. A `reached` cell with
`returned: 0` is a receipt that the search ran. An `unreachable` cell is a failure with a cause.
A `forbidden-by-terms` cell is a *decision*. *Revise if:* any is recorded as another — this is
the defect the whole artifact exists to prevent.

**C13 — Causes are specific.** "Not worth it" is not a cause. "429 after the documented rate
window; two pages kept, tail unread; retried once after backoff" is.

**C14 — `kept` counts distinct candidate rows, not results.** *(gated for arithmetic.)* Judge
whether the number is credible against the queries and the candidates carried.

**C15 — A bound cap says what it dropped, in kind.** *(gated for presence.)* Judge whether
`dropped_note` describes the tail rather than restating that a cap exists.

**C16 — Admission bases hold up.** For `corroborated`, the two angles are genuinely
independent — not the same source reached two ways. For `first-party-resolved`, the quoted
capability actually overlaps the scope. *Revise if:* a quoted capability is marketing language
with no capability in it. **This is the condition a planted defect targets most often.**

**C17 — The `unadmitted` array records every dropped candidate with a real reason.** *(gated for presence.)* A
silent drop makes "we did not look" indistinguishable from "we looked and found nothing".

**C18 — Identity is honest.** *(gated for shape.)* Judge that a minted `WEB-` id was minted
because no registry id exists, not because looking was inconvenient.

**C19 — `authority_band` is recorded on every candidate and never used as a cut.** *(gated for presence.)* *Revise if:*
a candidate appears to have been dropped for low authority rather than for irrelevance.

**C20 — A rating never appears without its denominator.** 4.9 from six and 4.3 from three
thousand are not comparable.

**C21 — Vendor claims are attributed, not asserted.** Marketing copy is evidence of positioning,
not of capability.

**C22 — Aggregator or directory rank is never reported as market share.**

---

## Conditions 23–26 — both artifact kinds

**C23 — Point-in-time facts carry `as_of`.** Pricing especially: roughly a third of B2B SaaS
competitors change pricing in any given week, so an undated price is wrong by default rather
than by exception.

**C24 — Novelty is phrased as a search result.** "No competitor found across N angles and M
terms", never "there is no competitor". *Revise if:* the artifact asserts absence as fact.

**C25 — Dead competitors, where present, are dated and their cause quoted not inferred.** A
discontinuation with no date cannot be reasoned about. If the notice gives no reason, the record
must say so rather than supplying one.

**C26 — Nothing was fetched in breach of a source's terms.** *(gated for the excluded list.)*
Judge the borderline: an allowlist-gated source reached outside its allowlist fails this even if
the registry lists it.

---

## Condition 27 — proportionality

**C27 — A thin-but-honest artifact is correct output for a thin scope.**

**Do not revise for thinness alone.** A market with few competitors, a vocabulary with few
credible expansions, an angle with a genuine zero — each is a correct result, and revising it
invites padding, which is a worse artifact than a thin one. Revise only when a specific gap is
*unrecorded*: a query not run and not explained, a source not attempted and not noted, a
candidate dropped without a reason.

The question is never "is there enough here?" It is "is what is missing accounted for?"

---

## Conditions 28–34 — extract record (wave 2)

**C28 — The positioning is the vendor's claim, reported as a claim.** *Revise if:* a marketing line
is restated as a finding, or the record endorses a capability the vendor merely asserts. Every
vendor describes itself favourably; laundering that into evidence is this wave's central failure.

**C29 — The tier is argued from overlap, not from impression.** A `direct` row names the
capabilities it shares and the argument is in `## Overlap`. *Revise if:* the tier rests on the
product being well known, or on category adjacency the record never connects to the scope.

**C30 — Commercial facts carry the date they were true.** *Revise if:* pricing, funding or
ownership appears without `as_of`, or the report repeats a figure without carrying its date
forward — a landscape is read months after it is written.

**C31 — A rating is reported with its denominator.** *Revise if:* a score stands alone. 4.8 from six
reviews and 4.8 from six thousand are different facts, and only one is a signal.

**C32 — A dead product is recorded as dead, with a date.** *Revise if:* a discontinued or acquired
product is recorded as `live`, or its status carries no dated evidence — the dated failure is the
highest-value fact in the survey.

**C33 — First-party beats an aggregator on a commercial conflict.** *Revise if:* a stale aggregator
figure is carried over the vendor's own current page without the conflict being noted.

**C34 — One record is one product.** *Revise if:* the same product appears twice under different
names rather than as `aliases`, or two products share a record.

---

## Conditions 35–40 — competitor register + report (wave 2)

**C35 — Every register row says what the record it cites says.** The gate checks the file exists;
you check the claim matches. *Revise if:* a row's tier, pricing or lifecycle differs from its
record.

**C36 — Segments are argued, not asserted.** *Revise if:* products are clustered with no stated
basis, or a segment name appears that no row's fields support.

**C37 — White space is phrased as a search result.** *Revise if:* the report says nobody has built
something, rather than that no surveyed product covers it across the angles that ran.

**C38 — A vacated angle is not reported as a negative result.** *Revise if:* an angle that could not
search is presented as having found nothing — those are different claims about the market.

**C39 — The report recommends no position, price or feature set for this product.** It reports the
landscape. *Revise if:* it picks the positioning, names a price point, or specifies the MVP — those
belong to the downstream document working from the register.

**C40 — Every claim carries its product id or source, and every commercial claim its date.**
*Revise if:* a sentence makes a claim with nothing attached to it.

---

## Applying the bar

1. Run the deterministic gate first if it has not been run. Its failures are not your findings —
   they are the producer's to fix before review.
2. Walk the judgment conditions in order.
3. For each finding, name the condition number and quote the artifact text that fails it.
4. Emit exactly one verdict line: `VERDICT: approve` or `VERDICT: revise`.
5. On `revise`, list every finding — a reviewer who reports one problem at a time costs a revise
   round per finding, and the loop caps out on correct work.

**Your evidence is the artifact, its schemas, and `source-registry.yaml`.** Not your own
knowledge of the market: if you believe a competitor is missing, the finding is that the angle's
coverage does not account for it, not that you happen to know the name.
