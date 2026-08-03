# The bar — numbered conditions

**This file is the single authoritative statement of the quality bar for
`security-prior-art-survey` artifacts.** Both skills' bodies point here and restate nothing
normative. A bar change edits this file first; the two pointers are checked in the same change,
**and every condition cross-reference in `references/sources.md` is swept** — a stale number
there produces findings the producer cannot act on.

**Numbering freezes at ship.** Later waves append conditions **above** the existing set and never
renumber, so anything citing a condition number stays valid.

Each condition gives a `Check:` procedure, then calibration. A finding must name its condition
number and a concrete location. An artifact that violates no condition is approved — yield is
never a gap.

---

## Conditions 1–8 — threat-vocabulary map

**C1 — Scope is translated, not echoed, and every group type is accounted for.**
*Check:* pick two groups and ask whether their terms would return anything in the source they
are aimed at. Product feature names ("receipt upload") almost never do; corpus terms (`CWE-434`,
"unrestricted file upload") do. Then check all six group types — `weakness`, `attack-pattern`,
`control`, `component`, `vendor-product`, `domain-incident` — and confirm each is present or
recorded in the scope guard as an absent type with its reason — and **corroborate each absent
type against the scope context**, the way C5 and C14 corroborate a negative angle verdict. A
reason is not self-justifying.
*Gap:* a group whose terms no named corpus indexes; a type silently missing; or a type recorded
absent on a reason the scope context does not support — an absent `weakness` or `attack-pattern`
type on any software product, or an absent `vendor-product` or `component` type where the scope
names a service or a package. The uncorroborated cases are the more dangerous: the coverage
arithmetic is computed from group types, so an omitted type empties the angle that depends on it
and the resulting search output reports no gap at all — the whole survey can be vacated from the
map side, quietly, and still pass.
*Not a gap:* a small map for a genuinely narrow product, or an absent type the scope context
corroborates.

**C2 — Expansions are real and typed.**
*Check:* every expansion carries a provenance and a relation kind; group sizes are **between
three and the `expansion_cap` the map records** (a per-group ceiling of at most eight, excluding
the canonical term), with any group below three carrying a reason; at least one group shows more
than one relation kind; and if
any expansion claims `probe-discovered` provenance, the probe record names what was probed and
what it surfaced (or records `performed: false` with a reason).
*Gap:* a flat pile of synonyms with no relation typing; every expansion typed `alt-label`, which
is a spelling list rather than an expansion; a `probe-discovered` term with no probe record,
which makes the provenance unfalsifiable. *Not a gap:* a term with genuinely few relatives, or a
reasoned `performed: false`.

**C3 — Negative terms guard ambiguous vocabulary.**
*Check:* find the most cross-domain term in the map and confirm it carries negative terms.
*Gap:* an obviously ambiguous term with none, where a search would demonstrably drag in an
unrelated field. *Not a gap:* an unambiguous term without them.

**C4 — The scope guard is explicit and reasoned.**
*Check:* compare the map's covered surfaces against the caller's scope context; every difference
should appear as a recorded exclusion with a reason.
*Gap:* a scope narrower than the caller's context with no exclusion recorded — silent narrowing.
*Not a gap:* a well-reasoned exclusion you would have argued differently.

**C5 — Source selection is justified.**
*Check:* the map records a **per-angle applicability verdict** — the angle, its precondition,
whether it holds, and why — and every registry source belonging to an angle judged applicable
appears in `sources.active` or in the skip list with a reason. Corroborate a negative verdict
against the scope context the same way C14 does for a not-run angle.
*Gap:* a source silently absent from both lists; an angle dropped with no recorded verdict,
which leaves the decision untraceable; or a negative verdict the scope context contradicts or is
merely silent about where the absent-input policy says run.

**C6 — Corpus releases are stamped.**
*Check:* **every entry in `sources.active`** records the release read and an `as_of` — not only
those the producer chose to describe as walked. A continuously-updated source with no release
concept (OSV, GitHub Advisory, KEV) correctly records `release: rolling`. Then apply the tell:
terms carrying corpus-specific identifiers (`CWE-434`, `T1190`, `v5.0.0-1.2.5`) mean that corpus
was read, whatever the provenance labels claim.
*Gap:* either field missing on an active source; or a map full of corpus identifiers with no
read record, no probe record and no stamps — the cheap route is to label everything
`model-knowledge` and owe nothing, and this is what closes it. Not bookkeeping: CWE ships several
releases a year while CAPEC can sit unchanged for years, so an unstamped map cannot be compared
with a later run. *Not a gap:* `release: rolling` on a genuinely rolling source.

**C7 — Assumptions are recorded as assumptions.**
*Check:* anything the absent-input policy forced appears as an assumption with the signal it was
inferred from.
*Gap:* an inferred verification level presented as if the caller had stated it.

**C8 — Nothing is fabricated.**
*Check:* spot-check one cited corpus release and one cited source identifier for existence.
*Gap:* a release or identifier that does not exist.

---

## Conditions 9–21 — per-angle search output (C19 also applies to a vocabulary map)

**C9 — Coverage is complete against the contract.**
*Check:* compute the applicable set as (map groups whose types the registry marks applicable to
`meta.angle_id`) × (`sources.active` ∩ the registry's sources for that angle), and confirm a
cell exists for each pair.
*Exemption:* if the artifact records the angle as **not-run**, it correctly carries no coverage
cells at all and C9 is satisfied by C14 instead. Four of eight angles are conditional, so this
is routine. Never fault a not-run artifact for missing cells — that pressure is exactly what
drives a producer to fabricate them.
*The empty-set case:* if the applicable set computes empty while the angle's precondition held,
the artifact must say so as a `vacated` record naming which factor was empty and the map entry
responsible — an absent group type, or every source skipped. **Then check that map entry against
the scope context yourself**; accepting the blame-tag at face value lets a bogus map decision
launder into an approved empty angle. A bare zero-cell output here is a gap: it reads as an
honest empty search while concealing that the angle was hollowed out upstream, and C9 would
otherwise pass vacuously over an empty set.
*Gap:* a missing cell on an angle that DID run; or an empty applicable set presented as an
ordinary empty result. An absent cell is indistinguishable from a search that never ran.

**C10 — A reached zero is the honest shape, and is never itself a defect.**
*Check:* this is C9's calibration rather than a second completeness test. Confirm that `reached`
cells with count 0 are treated as the successful outcome they are — the search ran and the
corpus held nothing — and that the artifact does not apologise for them, pad around them, or
convert them into something that looks busier.
*Gap:* a producer that clearly suppressed or dressed up empty results. A pair that is simply
missing is C9's gap, not this one — do not file both for the same cell.

**C11 — Non-reached outcomes are typed, never written as zeros.**
*Check:* every cell carries a status. For each `unreachable`, `partial`,
`embargoed-placeholder`, `content-withheld` or `not-attempted` cell, confirm a cause is present,
and for `unreachable` that the registry's fallbacks were tried.

`not-attempted` and `content-withheld` carry extra burden, because both are always available to
a producer and neither can be disproved. For `not-attempted`, the cause must name the **specific**
bound — a budget or time limit reached, or why this pair in particular was unproductive — and
must be consistent with the pairs that WERE attempted. A blanket "judged unproductive" repeated
across cells is not a cause; it is the absence of one. Check the proportions in the retrieval
summary: an angle whose applicable set is majority `not-attempted`, or a source `not-attempted`
across every group, should have been a not-run angle or a skipped source in the map, and is a gap
unless the cause is genuinely source-specific. For `content-withheld`, the cell must record what
triggered it — the item's identifier or URL and the guardrail's classification — and whether it
was routed to notes for a human; without that it is a strictly cheaper exit than the
`unreachable` route this bar already hardened.

Then cross-check the two records
against each other: **the retrieval summary lists every source whose cells are not all
`reached`**, so reconcile it against the cells. A source in the summary whose cells all say
`reached, 0`, or a non-`reached` cell for a source the summary omits, is the discrepancy this
condition exists to catch.
*Gap:* a failure or a non-attempt recorded as a zero — this converts "we could not look" or "we
did not look" into "there is nothing there" and survives every other check. Also a gap:
`unreachable` with no fallbacks tried, which makes the label the cheap exit from a merely slow
source; or a retrieval summary that disagrees with the cells.
*Not a gap:* a genuine `reached` zero, which is exactly what C10 wants.
*Probe asymmetry:* re-probing a source yourself can prove it **reachable now**, from your host;
it can never prove it was reachable for the producer at their time from their host. Never file a
C11 finding against an honest `unreachable` on the strength of your own successful probe — raise
it as an observation.

**C12 — Cells are reproducible.**
*Check:* each carries **every query as run** — a pair worked with a broad pass and two narrow
ones records three — plus a timestamp and a count or a cause. Then check the queries came from
the right place: **a cell's queries use its own group's canonical term or expansions, and honour
that group's negative terms.** The map is the sole source of query terms. At least one recorded
query per cell is a **broad pass** over the group's canonical term: an angle of nothing but
hyper-narrow queries returns honest zeros everywhere while having covered nothing, and the
no-false-revise rule would otherwise oblige you to approve it.
*Gap:* a paraphrased or reconstructed query; a `reached` cell with no count; a cell whose
recorded queries cannot plausibly account for its count, which is what a single narrow query
beside a broad-pass total looks like; or a cell whose queries are unrelated to the group it is a
cell for — that cell covered nothing, whatever its count says, and it is the quietest way to
make a map decorative.

**C13 — Coverage claims survive a spot-check.**
*Check:* sample cells and confirm the recorded query plausibly yields the recorded status and
count against the named source. Then sample one **candidate** and confirm it appears among the
results of the query its found-by names. That second check is what separates a real search from
a plausible one: identifiers exist, counts are authorable, and found-by is authorable, so
internal consistency alone cannot distinguish an angle worked from an angle written.
*Gap:* a probe that contradicts the record; or a candidate absent from its own query's results,
which is fabrication rather than drift. *Not a gap:* a count you cannot reproduce exactly —
sources drift. Flag it as an observation and say what would settle it.

**C14 — An unmet precondition is reported as not-run with a true cause.**
*Check:* the angle appears as not-run with a cause, **and** the cause is corroborated by the
scope context — if it claims no named package set exists, the scope context must agree.
*Gap:* an angle that could not run appearing as a zero-hit; a not-run cause the scope context
contradicts, which is a free pass to skip an expensive angle; or a not-run cause resting on the
scope context being **silent**, where the absent-input policy directs that angle to run anyway.
Silence is not a negative answer, and the policy exists precisely because treating it as one
drops whole control families invisibly.

**C15 — Candidates are grounded, and identified as their source class allows.**
*Check:* each carries the identifier form its class actually has — a registry `<DATABASE>-<ENTRY>`
id, an ATT&CK technique id, a **version-pinned** control id, an incident record id with its date,
or, for a disclosure-class item with no registry id, a stable URL plus published title plus
retrieval date. Plus the source's own title, an authority band from the allowed set, found-by
provenance **naming every cell it came from** (each as group id, source id, query), and one line
of relevance tied to the caller's scope. An item several groups surfaced against one source is
recorded once with all its cells listed, not duplicated per cell. Spot-check one candidate's identifier for existence.
Because this wave applies no relevance cut, `retained under the no-cut rule; scope link unclear`
is a legitimate and preferred relevance line for an item that ranked inside the cap without
obviously touching the scope — it is honest, and the alternative is an invented connection that
leaves no trace. Its overuse across most candidates is an observation, not a gap.
*Gap:* a registry-shaped identifier invented for an item whose corpus issues none — the failure
mode when a rigid id rule meets a write-up or a conference talk; a bare control id with no
version pin; invented relevance, or relevance that merely restates the title; a candidate whose
identifier does not resolve.

**C16 — Point-in-time signals are stamped.**
*Check:* every EPSS score, KEV membership claim, or other time-varying signal carries its read
date.
*Gap:* an unstamped forward-looking probability — downstream it becomes durable truth.

**C17 — The angle boundary held, and nothing was deep-read.**
*Check:* candidates trace to this angle's sources, cross-angle leads sit in notes, no candidate
carries analysis that could only come from opening the item up, and the list is not padded —
near-duplicate entries, or obviously off-domain rows inflating the count.
*Gap:* candidates plainly from another angle's sources; an extraction-depth summary, which is a
later wave's work done early and unreviewed; or padding. Note the interaction with the no-cut
rule: an item kept because relevance cuts are forbidden is not padding, and it will say so in
its relevance line. Padding is duplication and off-domain filler, not honest breadth.

**C18 — Bounding is honest.**
*Check:* the declared cap was applied and what it dropped is recorded; each candidate carries its
value for the angle's ordering signal (CAPEC Likelihood Of Attack, EPSS percentile, KEV
membership, or whatever the brief names); **and the drop record carries those values too**, so
the tail can actually be compared against the kept set rather than the comparison being asserted.
*Gap:* a truncated set presented as exhaustive; a dropped tail that ranks above part of the
kept set. *Not a gap:* a result set below the cap, or an ordering signal a source genuinely does
not expose — recorded as unavailable rather than left blank.

**C19 — Sanitization is recorded per source, and no source came from the content.
APPLIES TO BOTH ARTIFACT KINDS — load it on a map review too.**
*Check:* every source the artifact records reading carries a sanitization record — applied,
unavailable with what that degraded, or withheld. This includes a **vocabulary map**, which
reads corpora to stamp releases and to run probes and is exposed to the same content as a search
output; **a source stamped in `sources.active` counts as read** and owes its record, since you
cannot stamp a release you did not fetch. Then the checkable half of the injection question: every source read appears in the
declared set — **for a search output, the angle brief or the registry for that angle; for a map,
the registry**. A source that appears nowhere in the declared set arrived from somewhere, and
the most likely somewhere is a page that suggested it.
*Gap:* a source read with no sanitization record; a source outside the declared set; or any
executed snippet or method step that plainly came from retrieved content rather than the brief.
This corpus is adversarial by construction, so this is not a formality.

**C20 — Novelty is phrased with its receipt.**
*Check:* if the output asserts nothing was found, it says so as "no documented prior art found
across N angles and M terms", not as a novelty claim.
*Gap:* an unqualified "this is novel" or equivalent. No survey sees private or unpublished work,
and a zero-candidate output is the most tempting place to overclaim.

---

**C21 — No silent relevance cut, and notes carry the leads.**
*Check:* per cell, `kept` equals `returned` unless the angle's cap truncated the tail — and where
it did, **each dropped item names the cell it came from**, so the per-cell difference reconciles
against the drop record. Without that, a capped angle is unjudgeable: you can neither confirm a
delta nor fault it, and a relevance cut launders as cap truncation. **Then reconcile the two records: every cell's `kept` is accounted
for by candidates whose found-by names that cell.** Cells claiming eight kept across ten pairs
beside three recorded candidates is the failure this catches, and nothing else does. Finally
confirm the notes hold what the method routes there: vocabulary discovered mid-run, dead ends,
and cross-angle leads.
*Gap:* a cell where fewer candidates were kept than returned with no cap accounting for the
difference — that is a relevance judgment this wave is not authorised to make, and it is
invisible without the two counts. Also a gap: an artifact whose narrative mentions a lead or a
dead end that never reached the notes.
*Not a gap:* an empty notes block on a run that genuinely surfaced nothing worth routing.

---

## Conditions 23–30 — extract record (one source item)

**C23 — The bail is a relevance bail, and it is confident.**
*Check:* a skipped record's rationale names what was checked and why **none** of it is touched,
and `checked_scope` lists real scope elements. Read the rationale for hedging — "probably not",
"unlikely to", "might affect" — and for a bail resting on anything other than relevance.
*Gap:* an uncertainty-worded bail, because uncertainty **keeps** the item and the expensive read
is cheaper than a missed threat; a bail because a control looks already handled, which needs an
architecture that does not exist yet; a bail because the severity looks low, which is the
tiering's job downstream; or a rationale that restates the verdict ("not relevant") instead of
giving one.
*Not a gap:* a confident, specific bail on a genuinely unrelated item — that is the cut working.

**C24 — The item was read, not skimmed into a record.**
*Check:* the "what the source says" section restates the item in the producer's own words and
the body's specifics (preconditions, affected versions, the control's wording) could only come
from the item itself.
*Gap:* an abstract pasted or lightly reworded; a body that would read identically for any item
in that corpus. *Not a gap:* a short body for a genuinely short registry record.

**C25 — The tier follows from its evidence.**
*Check:* tier 1 or 2 carries evidence with a reference and a read date, and the evidence
actually supports the tier: catalog membership or a matching incident for tier 1, a
proof-of-concept or a high probability score for tier 2. Then read the body's evidence section
against the frontmatter — they must agree.
*Gap:* a tier the evidence does not support; a tier-1 claim whose body admits no incident was
found; severity used to justify a tier, when severity orders items *within* a tier and never
moves one between tiers. *Not a gap:* tier 3 with no evidence at all — that is what tier 3
means, and most control-standard output is legitimately tier 3.

**C26 — Severity is recorded as published, per system and version.**
*Check:* each entry carries its system and version; nothing collapses two scoring systems into
one number; the body does not compare scores across versions.
*Gap:* a bare score; a cross-version comparison presented as a like-for-like judgment.
*Not a gap:* an empty severity list for an item whose source publishes no score.

**C27 — The control is the source's, not the producer's.**
*Check:* where `stated` is true, the text is quoted or closely paraphrased and the reference
says where. Where `stated` is false, the body says so plainly.
*Gap:* a control with no source reference; a control the cited source does not actually
prescribe; generic security advice standing in for a stated remedy. *Not a gap:* `stated:
false` — a source that prescribes nothing is a common, honest outcome, and inventing a control
to fill the space is the worst single thing this record can do.

**C28 — Aliases and related are not confused.**
*Check:* every alias names **this same item** under another identifier; everything in related
names a neighbour. No identifier appears in both.
*Gap:* a parent weakness class listed as an alias, which makes synthesis merge two distinct
threats; or a second identifier for the same vulnerability listed as related, which makes it
report one threat twice.

**C29 — The record says what it does not establish.**
*Check:* the section exists and draws a real boundary — reproducibility versus exposure, an
incident elsewhere versus this product, a weakness in a component versus a component this
product has chosen.
*Gap:* the section missing, or filled with something that is not a limit ("further research
recommended"); or a body elsewhere overclaiming in a way this section then fails to walk back.

**C30 — Surfaces are named from the caller's scope.**
*Check:* every entry in `surfaces` is a surface the scope context describes, in the scope's own
terms.
*Gap:* a generic surface ("web application") standing in for a named one; a surface the scope
does not have, which is a relevance failure that survived the bail.

---

## Condition 22 — both artifact kinds

**C22 — The artifact is schema-valid.**
*Check:* the producer's validator exits 0 for the artifact's kind. This condition exists so a
mechanical failure has a number to cite, since every finding must name one.
*Gap:* any FAIL line. Report the validator's output verbatim. A mechanical failure **may** moot
fine-grained judgment this round — if the artifact will clearly be regenerated, say so and stop
rather than spending judgment on it; if the failures are narrow and the rest is reviewable,
carry on and collect the remaining findings in the same pass. That discretion is the one
exception to collecting every finding before deciding.
*Not assessable:* if the producer package ships without its validator, report C22 as not
assessed above the verdict rather than hand-checking what the validator owns.

---

## Applying the bar

- Run the producer's validator once before spending judgment. A mechanical failure may moot
  fine-grained review this round.
- Collect every finding in one pass.
- Report any condition you could not assess for missing input, above the verdict.
- Approve what meets the bar. Proportionality cuts both ways: a thin honest result passes, and a
  real named gap in a thin domain still fails.
- On a revised artifact, judge the delta and confirm prior findings were addressed rather than
  reworded.
