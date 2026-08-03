# Synthesis — the threat register and the report

`schemas/threat-register.schema.json` is the contract for the machine half. This guide covers
both halves and the judgment between them.

Synthesis is where a pile of per-item extractions becomes something an architect can act on. Two
jobs: **name threats** so the same threat is recognisable across projects and across delta runs,
and **collapse duplicates** so one vulnerability carrying two database identifiers does not
appear as two threats.

## Naming: bind to an external vocabulary, in this order

1. **An attack pattern**, where one fits. Attack-pattern catalogs operate at exactly the level a
   register works at — "an approver can approve their own claim" is a recognisable pattern — and
   they carry stable identifiers.
2. **A weakness class**, where no pattern fits but a weakness does.
3. **An organisational threat-event catalog**, and only for genuinely organisational threats. A
   product with a human support flow can legitimately carry a phishing-against-support-staff
   row. Do not reach for this level to name an application threat: those catalogs sit at
   operational granularity — "craft phishing attacks that coax an unwitting employee to divulge
   login credentials" — which cannot express a feature-level threat.

Never coin a phrase. A name invented here means the same threat gets three different names in
three requests, and the living register can never merge.

## Collapsing duplicates

An extraction's `aliases` field names other identifiers for **the same item**; `related` names
neighbours. Collapse on aliases only.

Where several extractions collapse into one row, cite all of them in `evidence` and prefer the
most authoritative for any quoted control — five blog restatements of one advisory become one
row citing the advisory, not five rows or one row citing a blog.

Do **not** collapse on `related`. A parent weakness class and a specific vulnerability are two
different things, and merging them loses the specific one.

## The tier of a row

Take the strongest tier among the extractions the row cites, and carry that extraction's
evidence. A row is tier 1 only if some cited extraction is tier 1 — synthesis never promotes.

## Controls

Carry the control the evidence prescribes, attributed to its source. Where several cited
extractions prescribe different controls, record the most specific and note the others in the
report; where none prescribes any, `stated: false` — and the report says so plainly rather than
substituting generic advice.

Control-standard references are **version-pinned** (`v5.0.0-1.2.5`). A bare chapter-section
number silently means something else after the standard's next release, which for a living
register amended over months is a real corruption risk.

## The report's six sections

1. **Coverage receipt** — what was searched, what returned zero, which angles did not fire and
   why, which corpus releases were read, every default the absent-input policy supplied, **and
   every item that was judged relevant but could not be read**. This is what makes an absence
   provable, and it goes first because a reader must know the shape of the search before
   trusting any finding in it.

   The last of those is easy to lose and the most damaging to lose. An extract record skipped
   as `unavailable` or `withdrawn` is **not** the same as one skipped as `irrelevant`: the item
   applies to this product and nobody could read it. It carries no evidence, so it never becomes
   a register row — which means the receipt is the ONLY place it can appear, and an omission
   here makes an unread threat indistinguishable from one that does not apply. List each with
   its identifier and the cause carried from its record, in `coverage_receipt.unretrievable` in
   the register and in prose in the report. The validator fails a register whose extracts
   include such an item that the receipt does not name.

   Angle-level outcomes do not cover this. An angle can run, reach every source and still
   surface an item that later proves unretrievable at deep-read time; the angle's own record
   says `ran` and is correct.

   **Carry each angle's outcome from its own artifact; never re-characterise it.** An angle
   that ran and whose every source refused it is `ran` with zero-reached cells — not `not_run`,
   and not `vacated`. Those are three different facts: `not_run` means the precondition failed
   and nothing was attempted, `vacated` means the applicable set computed empty, and a `ran`
   angle with nothing to show is a search that happened and returned nothing. Summarising the
   third as either of the first two destroys the distinction the whole survey is built to keep,
   and it does it in the one document a reader trusts to describe the search. Put the cause in
   the `cause` field beside the outcome; do not encode it by changing the outcome. The validator
   reconciles the receipt against the search outputs when it is given them.
2. **The tier-ordered register** — the rows, strongest evidence first.
3. **Surface concentration** — which product surfaces attract the most rows and the
   highest-tier ones. This is the section that tells an architect where to spend.
4. **Control consolidation** — which single controls close the most rows. Usually a handful of
   decisions cover a long tail of threats, and this is where that shows.
5. **Dependency surface covered and not covered** — explicit, because a partial supply-chain
   pass looks identical to a complete one from the outside.
6. **Test-plan handoff** — what must be simulated, per row that warrants it.

## What the report must not do

**It must not write mandates in its own voice.** Every control it carries belongs to a cited
source. The architecture doc owes an answer to every tier-1 and tier-2 row — adopt, or record
why not — and that obligation is the register's teeth. A "MUST" written here on the survey's own
authority rests on nothing a reader can check, and manufactures exactly the authority the
evidence-first tiering was adopted to avoid.

**It must not claim novelty.** Where a surface turned up nothing, the phrasing is "no documented
prior art found across N angles and M terms". No survey sees private or unpublished work.

**It must not present a point-in-time finding as durable.** Dependency findings are a snapshot;
ongoing coverage is a continuous dependency audit in the build pipeline, not a re-run of this
survey.

## The changelog

Opened at request 1, not on first amendment. The freshness rule that decides whether a later
request re-runs the supply-chain angles reads the last-run date from here, and a register
without an entry gives it nothing to read.
