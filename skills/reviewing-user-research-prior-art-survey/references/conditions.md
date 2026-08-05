# Conditions — user-research prior-art, wave 1

**This file is the authoritative bar for the pair.** The producing skill points at it by name and
restates nothing normative. Where the producer and these conditions differ, these win.

Conditions marked *(gated)* are discharged by one run of the co-installed producer's validator
and are not restated in a review; the judgment conditions are the point.

**Your evidence is the artifact, its schemas, and `source-registry.yaml`** — plus, for the search
output, the vocabulary map it was produced from. Not your own knowledge of the literature: if a
study seems missing, the finding is that the angle's coverage does not account for it, not that
you happen to know the citation.

---

## Conditions 1–10 — the research vocabulary map

**C1 — Every axis is accounted for.** *(gated)* Present, or in `scope_guard.absent_types` with a
reason. *Revise if:* an axis is silently missing — it empties every angle depending on it.

**C2 — The population and task groups describe THIS product's users.** They are who will use the
thing and what they will be doing, not a generic interface vocabulary. *Revise if:* the groups
would fit any product in the category equally well.

**C3 — The `method` axis retrieves this literature, rather than restating the topic.** This axis
exists because bibliographic corpora are indexed by study design. A method group whose terms are
really topic terms in disguise ("mobile usability", "kiosk research") retrieves nothing the task
axis did not already reach, and the map has lost the axis it most needs. *Revise if:* no group on
this axis names a study design.

**C4 — Negative terms on `method` groups are real exclusions.** *(gated for presence.)* Judge
whether they exclude the actual collision. "Interview" collides with journalism and with job
interviews; a negative term list that does not name those is decoration. *Revise if:* the terms
exclude nothing the query would have retrieved.

**C5 — Expansions are honestly typed.** `provenance: extracted` claims a real corpus supplied the
term. The map is built BEFORE the search, so unless a probe ran, `model-knowledge` is the honest
value. *Revise if:* `extracted` appears with no probe and no fetched source behind it.

**C6 — Thin groups are folded or explained, never padded.** *(gated for `short_reason`.)* Judge
whether the reason is real. *Revise if:* a group is padded with near-synonyms to clear the floor.

**C7 — Angle verdicts are grounded in the scope's actual values**, not a general impression.
Check BOTH directions: a wrong `holds: false` silently drops an angle, and a wrong `holds: true`
spends a whole cap on literature the scope ruled out. *Revise if:* a reason cites no value from
the scope.

**C8 — Assumptions name a signal, not a rationale.** "No level was declared while `ui.has_ui` is
true" is a signal. "Accessibility matters for this product" is not. *Revise if:* the
`inferred_from` states a motive rather than an observation.

**C9 — The sanitization result is recorded per active source.** *(gated for presence.)* Judge
whether a degraded status carries a cause specific enough to act on.

**C10 — Every source an applicable angle could query has a recorded posture.**
*(gated for presence.)* Judge whether the `access_status` matches what the artifact elsewhere
says about that source — a source recorded `open-access` whose cells are all `forbidden-by-terms`
is one of the two records lying. *Revise if:* the map's posture and the search output's cells
contradict each other.

**Which verdict carries it.** A contradiction between a map and a search output is a finding
against **whichever artifact is under review**, reported against C10 with the other artifact
quoted as the evidence. You are not asked to decide which of the two is wrong — often you cannot
— only to report that they cannot both be right. When reviewing the map, the search output is
evidence; when reviewing the search output, the map is.

---

## Conditions 11–24 — per-angle search output

**A naming deviation, declared rather than glossed.** The schema field is `candidates`, and in
this survey a candidate is one **SOURCE** — a paper, report or article — not a finding. The
sibling surveys' `candidates` are the thing itself; here they are the thing a finding will later
be read out of, because how many findings a source contains is unknowable before the full read.
The conditions below say "source" where the field says `candidate`, and they mean the same row.

**C11 — Queries are recorded as run.** *(gated for presence.)* Judge reproducibility: could
someone else run these and get a comparable set? For a corpus walk the query is the traversal —
which index, which sections, the selection criterion. *Revise if:* a query is a paraphrase of an
intent rather than a string that was issued.

**C12 — Coverage is complete in both directions.** *(gated.)*

**C13 — A zero, a failure and a refusal are never conflated.** *The central condition, and it is
a COHERENCE check — read the procedure before applying it.* A `reached` cell with `returned: 0`
asserts the search ran and the corpus held nothing. An `unreachable` or `rate-limited` cell
asserts the search could not complete. A `forbidden-by-terms` cell asserts a decision not to
fetch.

**You cannot verify that a recorded status is true.** Your evidence set is closed, and a
laundered failure that is internally consistent leaves no residue inside it. A condition phrased
as "judge whether it is true" is one you cannot execute, and it passes a competent launderer
silently — which is exactly what happened when this condition was phrased that way. So apply it
as an enumerated coherence test.

**Revise if any of these holds:**

1. **A sibling cell contradicts it.** A zero on a source that another cell in the same artifact
   reached minutes earlier, through the same index, with no intervening cause recorded.
2. **The retrieval summary does not corroborate it.** A non-`reached` cell whose source is absent
   from `degraded_sources`, or a `degraded_sources` entry whose status disagrees with the cell's.
3. **The registry contradicts it.** A zero on a source the registry marks `throttled`, where no
   throttle appears anywhere in the artifact — or a `forbidden-by-terms` cell on a source the
   registry marks reachable, or the reverse.
4. **The cell's own record is incoherent.** A `selection` describing a fetch on a cell that
   reports no retrieval; a cause naming an outage on a cell recorded `reached`; a zero whose
   queries could not have returned zero on the corpus the registry describes.
5. **The map contradicts it.** A source the map records as reached at wave 0 whose every cell is
   `unreachable`, with no cause naming what changed.

**The one outside channel, and its asymmetry.** You may re-probe a source **and cite the result
only when your probe FAILS.** A failed re-probe corroborates the producer and is admissible. A
*successful* re-probe is **not** evidence against them: throttling, rate windows and outages move
minute to minute, and one of this survey's sources runs a globally shared pool whose behaviour
depends on load you cannot see. "I reached it just now" is not a finding, and raising it as one
costs a revise round on work that was honest.

If none of the five holds and no re-probe failed, the cell is coherent and C13 is discharged.
Say so plainly rather than approving in silence — a reader needs to know the condition was
applied, not skipped.

**The limit, stated so nobody mistakes this condition for more than it is.** A zero laundered
*thoroughly* — the cause deleted, a plausible selection written, and the retrieval summary
reconciled to match — is coherent, and no review confined to a closed evidence set can catch it.
That is a property of the evidence set, not a gap in your diligence. What bounds the risk is
elsewhere: the gate forbids counts on a cell that retrieved nothing, so the cheapest route is
closed mechanically; and laundering that survives all five checks requires editing three records
in agreement, which is a different and more deliberate act than a careless miscode. Do not
manufacture a finding to cover the gap — an ungrounded C13 finding costs a revise round on work
that may be honest.

**C14 — Causes are specific.** "Not worth it" is not a cause. "The subject listing returned 503
on three consecutive fetches at the declared spacing" is. *Revise if:* a cause names no
observation.

**C15 — `kept` reconciles.** *(gated for arithmetic.)*

**Do not judge the plausibility of a result count.** That is a claim about the corpus, and you may
neither re-probe it nor substitute your own knowledge of the literature — so there is no evidence
inside the permitted set from which to form the judgment. An earlier wording asked for exactly
that and was unexecutable.

What IS reviewable here is internal: whether the cell's own `selection` accounts for the rows it
carries. A selection stating that N items were shortlisted and fetched, on a cell carrying fewer
than N rows across `candidates` and `unadmitted`, has items that were retrieved and then vanished
— see C20, which owns that check.

**C16 — A bound cap says what it dropped, in kind.** *(gated for presence.)* Judge whether the
note lets a reader tell what kind of source was lost. *Revise if:* it says only that the cap bound.

**C17 — A crawl-delayed cell's `selection` is a real selection.** *(gated for presence.)* Three
of this survey's sources declare a delay, and for those cells the selection IS the method. Judge
whether it names both what was shortlisted and what was identified and deliberately not fetched,
with a criterion a reader could apply. *Revise if:* the selection records only what was fetched —
the un-fetched remainder is the part that makes the coverage honest.

**C18 — Every admitted source's full text was actually retrievable.** The first conjunct of this
survey's admission rule. `admission.full_text_url` must point at full text reached without a
paywall and without bypassing one. *Revise if:* the URL is a landing page, an abstract, a
publisher page behind a wall, **or an anchor into a summary or abstract section of an otherwise
full-text page** — a fragment aimed at a summary is how a record built from the summary acquires
a full-text-looking citation.

**C19 — Every admitted source STATES A METHOD.** The second conjunct, and the one this survey
turns on.

**The half you can review:** `admission.method_stated` must READ AS A STUDY DESIGN rather than a
topic. "benchmark usability test, sample size stated in the article" is a design; "self-service
checkout usability" is what the source is about. A title stating a result is not a method.
*Revise if:* the field paraphrases the subject rather than the procedure.

**The half you cannot:** whether the source *itself* names that design is outside your evidence
set — reaching the source is not something this bar admits, and a producer who invented a
plausible-sounding design is indistinguishable from one who read it. That check belongs to the
extract wave, which does the full read. Do not raise it here; an ungrounded finding costs a
revise round on work that may be honest.

**C20 — The `unadmitted` array carries a real reason for every dropped source, and every
shortlisted item is accounted for.** *(gated for presence of the reason; the accounting is not
gated.)* Judge whether the reason is the true one. `abstract-only` is the expected commonest
value; a source dropped as "not relevant" that plainly is relevant hides a coverage decision.

**The accounting half is this condition's, and nothing else's.** A `selection` that says N items
were shortlisted and fetched, on a cell carrying fewer than N rows across `candidates` and
`unadmitted`, has items that were retrieved and then vanished from the record. The gate cannot
see it — `kept` reconciles against the rows that exist, not against the shortlist the prose
declares — and it is exactly the silent drop this survey exists to prevent, one level in. *Revise
if:* a reason is a category label with no content, or the shortlist count exceeds the rows the
cell carries with no explanation of the difference.

**C21 — Identity is resolver-scoped and honest.** *(gated for shape.)* Judge that a DOI is the
work's actual DOI and an arXiv id its actual id, not a plausible-looking string. *Revise if:* an
identifier appears to have been constructed rather than read.

**C22 — A `web` candidate carries its url.** *(gated.)* A DOI and an arXiv id each have a
resolver behind them; a web id has nothing.

**C23 — A shared-pool throttle is not read as an outage — or as a zero.** `semantic-scholar`
documents a globally shared unauthenticated pool subject to throttling under load. A 429 there is
a normal operating condition: `rate-limited` with that cause is correct, `unreachable` overstates
it, and `reached, returned: 0` is C13's failure. *Revise if:* the cell's status misrepresents
which of the three happened.

**Applies only to angles whose sources include it.** For an artifact from an angle that never
touches that source, C23 is INAPPLICABLE — say so rather than recording it satisfied, and do not
route an ordinary crawl-delay 429 from another source here. That failure is C13's.

**C24 — Nothing was reached in breach of a source's terms, or on the wrong host.** Two sources in
this registry have a website that refuses this survey and an API that does not. Judge the cell's
`source_id`, not the corpus name — reaching the website because you recognised the corpus is a
breach the output will not otherwise show. *Revise if:* a cell names the excluded half of a split
source, or an excluded source at all.

---

## Conditions 25–26 — both artifact kinds

**C25 — Novelty is phrased as a search result.** "No published research found across N angles and
M terms", never "there is no research". *Revise if:* the artifact asserts absence as fact.

**C26 — No wave-2 judgment leaked into wave 1.** Certainty, transferability, study date,
population and effect size are finding-level and turn on the full read, which has not happened.
A relevance line may describe why a source looks promising; it may not grade the evidence.
*Revise if:* the artifact assigns a certainty or asserts a finding transfers.

---

## Condition 27 — proportionality

**C27 — A thin-but-honest artifact is correct output for a thinly-researched domain.**

**Do not revise for thinness alone.** Most product scopes have very little published research
addressing them directly; several angles legitimately return zeros, and a short map with honest
reasons is a correct result. Revising it invites padding, which is a worse artifact than a thin
one. Revise only when a specific gap is *unrecorded*: a query not run and not explained, a source
not attempted and not noted, a candidate dropped without a reason.

The question is never "is there enough here?" It is "is what is missing accounted for?"

---

## Conditions 28–34 — extract container (wave 2)

**C28 — The claim is the source's finding, checkable against the method it reports.** *Revise if:*
the claim asserts something the stated method could not have measured, or generalises a result
beyond what was tested.

**C29 — Certainty matches the recorded facts, and the facts match the source.** The gate re-derives
the level, so a mismatch never reaches you — what you check is the input: does the source really
report that design, that sample size, that effect size? *Revise if:* a fact was recorded to reach
a level the source does not support.

**C30 — Transferability carries a reason a reader can weigh, and is not a restatement of
certainty.** *Revise if:* the reason paraphrases the method, or a high-certainty finding from a
different population and platform is marked highly transferable with no argument.

**C31 — Effect and sample sizes are the source's own numbers.** *Revise if:* a figure is converted,
rounded, pooled, or restated in a measure the source did not use.

**C32 — Every finding in the container is genuinely distinct.** One source, N findings — but two
records restating the same result at different granularity are one finding. *Revise if:* the
container inflates its count by splitting one result.

**C33 — Population, platform and study date describe the study, not the project.** *Revise if:*
the fields record who the survey is FOR rather than who the study measured.

**C34 — A skip is confident, and its detail names what was checked.** *Revise if:* the detail
restates the cause code, or the skip reads as uncertainty — uncertainty keeps the source.

---

## Conditions 35–40 — evidence register + report (wave 2)

**C35 — Every register row says what its container says.** *Revise if:* a row's claim, certainty
or transferability differs from the record it cites.

**C36 — Convergence is across INDEPENDENT sources.** Two findings sharing a source prefix are one
study agreeing with itself. *Revise if:* agreement is claimed across findings from the same source.

**C37 — A contradiction is explained by what differs, not resolved by preference.** *Revise if:*
one of two disagreeing findings is dropped, or the disagreement is settled without noting the
difference in population, platform or date.

**C38 — Certainty is never averaged, and a claim is reported at the certainty of its evidence.**
*Revise if:* levels are pooled into a summary, or a claim supported only at `low` is stated
without that qualification.

**C39 — The report recommends no design for this product.** It reports what has been measured and
how far it carries. *Revise if:* it specifies the interface — that belongs to the downstream
document working from the register.

**C40 — Absence is phrased as a search result, and access barriers are stated.** *Revise if:* the
report says there is no research on something, or a paywalled or blocked source is silently
omitted rather than recorded as a limit on the survey.

---

## Applying the bar

1. Run the deterministic gate first if it has not run. Its failures are the producer's to fix
   before review, not your findings.
2. Walk the judgment conditions in order.
3. For each finding, name the condition number and quote the artifact text that fails it.
4. Emit exactly one verdict line: `VERDICT: approve` or `VERDICT: revise`.
5. On `revise`, list every finding in one pass — a reviewer who reports one problem at a time
   costs a revise round per finding, and the loop caps out on correct work.

Anything you cannot ground in the artifact, its schemas or the registry is an **OBSERVATION**,
not a finding. An ungrounded finding costs a revise round and, at the cap, parks correct work.
