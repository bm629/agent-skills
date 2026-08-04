# `market-competitive-prior-art-survey`

Run the search wave of a systematic market & competitive prior-art survey: who already competes,
what they offer and charge, how users receive them, and which comparable products died — for a
product that does not exist yet.

## The organising idea

**A market with no competitor and a search that never ran produce identical-looking output.**
Everything in this skill exists to keep those apart. A recorded zero is a receipt that the search
happened; an unreachable source is a typed failure carrying its cause; a source excluded on its
terms is a *decision*, not an outage. Three different facts, and the schema refuses to let them
collapse into one.

## Two procedures

**Procedure 1 — the market vocabulary map.** The search protocol, built before any searching.
Five axes: `category` (how directories name the market), `capability` (what the product does),
`job-to-be-done` (how a user phrases the need), `audience-segment`, and `seed-product` (known
incumbents the graph walk starts from). Expansions are SKOS-typed by relation and carry honest
provenance — `extracted` claims a real source used the term, `model-knowledge` says you supplied
it, and a reviewer weighs them differently.

The `job-to-be-done` axis is the substitute-finder, and it is why the map has five axes rather
than two. A competitor set defined by category misses everything that solves the same need a
different way — including non-consumption and "do it by hand in a spreadsheet", which is a real
competitor and frequently the incumbent one.

**Procedure 2 — one search angle.** Eight angles, two always-on (alternatives-graph traversal;
category-and-capability search discovery) and six conditional, each with its own mechanism,
sources, cap sized to the corpus it walks, and a named fallback. Output is a coverage grid of
(group × source) cells, each carrying its queries **verbatim as run** — a paraphrase cannot be
re-run, and a coverage record that cannot be re-run proves nothing.

## What is enforced rather than requested

- **Negative terms are mandatory** on `category` and `seed-product` groups. Products are called
  Notion, Linear, Arc, Ghost, Craft; each matches an enormous amount of unrelated text, and a
  search built from such a group cannot be made precise afterwards. This rule has no analogue in
  surveys of identifier-keyed corpora — it is specific to markets.
- **Coverage completeness in both directions.** Every applicable (group × source) pair owes a
  cell, and no cell may fall outside the applicable set. A missing cell is an unexplained gap; a
  surplus one means the angle worked another angle's channels and inflated its own arithmetic.
- **`kept` reconciles.** It must equal the number of candidate and unadmitted rows naming that
  cell — an unreconciled count is where rows get dropped without a record.
- **The cap belongs to the registry**, sized per corpus, checked in both directions: a run may
  neither raise its own ceiling nor quietly lower it. There is no total queue cap anywhere, so
  the per-angle limit is the only place coverage is deliberately bounded.
- **An always-on angle cannot be switched off** by a map. That is how a survey silently does
  nothing.
- **Every conditional trigger rests on a REQUIRED capability field**, and the registry is checked for it. `trigger_anchor` is a LIST of the required-rooted legs; optional disjuncts are recorded separately as `widening_legs`, because an optional leg beside a required one only ADDS firings while a predicate rooted solely on one fails closed and invisibly. A scalar cannot describe a disjunctive predicate — one angle here rests on two required legs, and naming one of them makes the assertion stop matching the predicate. A fault in the registry exits **2** as a package fault, on both subcommands, rather than 1 as an artifact failure.
  optional field fails closed and invisibly for any map that omitted it — the angle looks
  configured and does nothing.

## The admission rule

Listicles pad. A "top 15 tools" article routinely carries a handful of real products and a tail
of affiliate entries and defunct names, and each filler entry that survives costs a full deep
read later. So a candidate is carried forward only if two independent angles found it, or its
official site resolves and states a capability overlapping the scope. Everything else is
recorded in `unadmitted` with its reason — **never dropped silently**, because a silent drop
makes "we did not look" indistinguishable from "we looked and found nothing", one layer down.

Note that a single-angle run cannot use the corroborated basis at all — it has no sibling
output — so in isolation the cap doubles as a fetch budget.

## Source access is verified, versioned, and part of the contract

Market sources are commercial assets defended by terms and robots directives that move. The
shipped registry records an access status per source, verified by direct fetch of the primary
source, plus an explicit excluded list — G2 (on its Terms of Use, which forbid automated
extraction regardless of what robots permits), Trustpilot, Similarweb and Reddit. The validator
rejects a coverage cell naming an excluded source, and rejects a fallback substituting one.

## The deterministic gate

`validate_market_competitive_prior_art.py`, two subcommands, 46 rules, 105 tests. Shape and
arithmetic only — whether a competitor is real or a relevance line persuades belongs to the
reviewing twin. Exit 0 clean, 1 a rule failed, 2 an input could not be read at all; an input
fault is not an artifact fault and must not send anyone off to edit a file that may be fine.

**A clean gate is not the bar.** Three planted fixtures in `scripts/fixtures/planted/` pass it
and are each wrong: a rate-limited cell rewritten as a searched zero, an admission whose
first-party quote states no capability, and a vocabulary map whose job axis merely paraphrases
its category axis. They exist to prove the reviewing skill's conditions bite, and they are the
reason a green gate should not be mistaken for a good survey.

## Companion

`reviewing-market-competitive-prior-art-survey`. Its `references/conditions.md` is the
authoritative bar for the pair — the producer points at it and restates nothing normative, so
the two halves cannot drift into grading the same artifact by different rules.

v1.0.0 — SEARCH wave. Extract and synthesis ship as later append-only waves.
