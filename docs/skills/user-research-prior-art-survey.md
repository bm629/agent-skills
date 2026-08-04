# `user-research-prior-art-survey`

Run the search wave of a systematic published-user-research prior-art survey: what has already
been studied about the people who will use a product, what those studies found, and how much of
it is retrievable at all — for a product that does not exist yet.

## The organising idea

**A domain with no published research and a search that never ran produce identical-looking
output.** Everything in this skill exists to keep those apart. A recorded zero is a receipt that
the search happened; an unreachable source is a typed failure carrying its cause; a source
refused on its terms is a *decision*. Three different facts, and the schema refuses to let them
collapse into one.

This type adds a fourth that the siblings do not have: **a throttle**. One of its sources
documents a globally shared unauthenticated pool that rate-limits under load, so a 429 there is a
normal operating condition rather than an outage — and it is the single most tempting thing to
write down as an empty result set.

## Two procedures

**Procedure 1 — the research vocabulary map.** The search protocol, built before any searching.
Four axes: `user-population` (who was studied), `task` (what they were doing), `method`, and
`component`.

The `method` axis is the one that makes this survey work, and it has no analogue in the sibling
types. Bibliographic corpora are indexed **by study design**, so "diary study", "think aloud",
"task completion rate" and "controlled experiment" reach work that no topic term will. A method
group whose terms are really topic terms in disguise retrieves nothing the task axis did not
already reach, and the map has lost the axis it most needs.

`component` exists for a narrower reason: assistive-technology research is indexed by widget —
"screen reader" plus "combobox", never "screen reader" plus "browsing" — so an accessibility
angle querying on tasks alone returns advocacy instead of interaction evidence.

**Procedure 2 — one search angle.** Seven angles, two always-on:

| Angle | Trigger | Cap |
| --- | --- | --- |
| a1 open scholarly-index retrieval | always | 60 |
| a2 practitioner-research corpus retrieval | always | 12 |
| b1 regulated-domain research retrieval | conditional | 30 |
| b2 assistive-technology research retrieval | conditional | 18 |
| b3 platform usage-research retrieval | conditional | 20 |
| b4 human-AI interaction guideline retrieval | conditional | 25 |
| b5 developer-experience research retrieval | conditional | 8 |

The caps are sized per corpus. a1 walks an effectively unbounded index and is budgeted; a2's 12
is bounded by a 60-second declared crawl delay, so twelve fetches is roughly ten minutes of
retrieval before anything is read; b5's 8 is the smallest in the registry because that angle
walks **one published survey**, not an index, and anything larger would be padding from a corpus
that does not exist.

## The admission rule, and why it has two conjuncts

A source is carried forward only when **its full text is retrievable without bypassing a paywall
AND it states a method**. Both halves are load-bearing, and they fail in opposite directions:

- Full text without a stated method admits practitioner argument — fully retrievable, persuasive,
  and reporting no study. The record that follows has nothing to weigh.
- A stated method behind a paywall admits a record built from an abstract, which reads exactly
  like one grounded in the method section. That is the survey's central failure one layer along.

Everything else is recorded in `unadmitted` with its reason; `abstract-only` is the expected
commonest one. The gate catches one form of the second failure mechanically: a candidate admitted
on retrieved full text whose source the map records as `paywalled-abstract-only` is a
contradiction between two records, and one of them is wrong.

**Following a resolver to the full text is part of the mechanism, not an excursion.** a1's
backbone index returns metadata only, so admission is unsatisfiable through that angle's declared
sources unless this is stated. The resolved publisher or repository takes no coverage cell — the
cell records the search — and is recorded in `admission.full_text_url`.

## Source access is verified, split by host, and part of the contract

Every source was checked at its own robots file, terms page or API documentation, and the
registry records who verified what and when. Two findings shaped the design:

- **Two corpora are split across hosts that answer differently, and the permitted half is not the
  same for both.** Europe PMC's website refuses this survey while its REST API does not; arXiv is
  the reverse — its API host is `Disallow: /` outright while the listing and abstract paths are
  expressly allowed at a 15-second crawl delay. Each half is a separate registry entry, and a
  cell must name the host it reached rather than the corpus.
- **arXiv's own two instruments contradict each other.** The published API Terms of Use permit
  metadata retrieval at one request per three seconds and require an acknowledgement string,
  while robots forbids the same host. The registry does not adjudicate it: the allowed listing
  paths carry the same records, so the survey reaches those and files the conflict as examined.

A corpus with a free and a gated half is split the same way, so each entry carries the posture
that is actually true of it.

## Crawl delay changes the method, not just the pace

Three sources declare a delay (60s, 15s, 10s). A delayed source crawled breadth-first spends the
whole run on retrieval and reads nothing, so those cells must select from an index first and
record **both** what was shortlisted and what was identified and deliberately not fetched. The
un-fetched remainder is what makes the coverage honest — without it a reader cannot tell a narrow
corpus from a truncated one. The gate requires the selection wherever a delay is declared and the
cell actually retrieved something; it deliberately does not demand one from a cell that never got
a response, because that would push a run to invent a selection it did not make.

## What is enforced rather than requested

- **Counts belong only to a cell that retrieved something.** `returned` and `kept` are forbidden
  on a `rate-limited` or `unreachable` cell, because such a cell carrying `returned: 0` is one
  field-rename from a laundered failure.
- **The angle precondition is compared against the registry**, not left to a reviewer's eye.
- **Coverage completeness in both directions**, and `kept` reconciles against the rows naming
  each cell.
- **Every conditional trigger rests on a REQUIRED capability field**, with optional disjuncts
  recorded separately as widening legs — an optional leg only adds firings, but a predicate
  rooted solely on one fails closed and invisibly.
- **`returned` counts records HANDED BACK, never a paged index's match total**, and a
  traversal shared across cells apportions rather than repeating — the two readings differ by
  six orders of magnitude, and only one makes the arithmetic mean anything.
- **`unadmitted` holds the sources that reached the admission check and failed it**, not every
  screened record, so `kept` stays a carried-forward count rather than a screening tally.
- **A candidate carries no certainty or transferability.** Both turn on the full read, which is
  the extract wave's; a wave-1 artifact that grades its evidence has invented a value nothing can
  check. The schema has nowhere to put them, and a test asserts it.

## The deterministic gate

`validate_user_research_prior_art.py`, two subcommands, 48 rules, 110 tests. Shape and arithmetic
only. Exit 0 clean, 1 a rule failed, 2 an input could not be read at all.

A fault in the package's own source registry exits **2** as well, on both subcommands. The registry ships inside the package, so a defect in it is a package fault rather than a fault in the artifact under test — reporting it at exit 1 sent a caller off to edit a map that was perfectly fine, and only one of the two subcommands ever checked it.

**A clean gate is not the bar.** Three planted fixtures in `scripts/fixtures/planted/` pass it and
are each wrong: a throttled cell rewritten as a searched zero while the retrieval summary still
records the throttle, an admission whose URL anchors into a summary and whose method is really a
topic, and a crawl-delayed selection that records only what it fetched.

Every rule was additionally checked by a mutation audit — each rule's emission neutered in turn,
confirming a test goes red. 49 of 49 caught.

## Companion

`reviewing-user-research-prior-art-survey`. Its `references/conditions.md` is the authoritative
bar for the pair — the producer points at it and restates nothing normative, so the two halves
cannot drift into grading the same artifact by different rules.

v1.0.0 — SEARCH wave. Extract and synthesis ship as later append-only waves.
