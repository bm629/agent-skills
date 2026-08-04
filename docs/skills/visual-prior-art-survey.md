# `visual-prior-art-survey`

Run the search wave of a systematic visual and interaction prior-art survey: what the industry's
documented conventions already prescribe for a product's domain, and what an accessibility
standard actually requires — before any wireframe, design system or hi-fi screen is produced.

## The organising idea

**A domain with no documented convention and a search that never ran produce identical-looking
output.** Everything in this skill exists to keep those apart. A recorded zero is a receipt that
the search happened; an unreachable source is a typed failure carrying its cause; a source
excluded on its terms is a *decision*, not an outage. Three different facts, and the schema
refuses to let them collapse into one.

## The modality lock — documentation, never screenshots

This survey mines governed design systems, the ARIA Authoring Practices Guide, WCAG success
criteria, platform human-interface guidelines and the deceptive-pattern corpus. It never touches
a screenshot gallery, and that is a defining decision rather than a limitation. Two independently
sufficient grounds:

- The galleries — Mobbin, Pttrns, Dribbble, Page Flows, Lapa Ninja — are subscription products
  whose terms exist to prevent exactly this kind of automated extraction.
- Decisively, **a screenshot is not extractable into the markdown artifact the downstream
  wireframing skill consumes.** A pixel asserts "the navigation is on the left". Documentation
  states the position, the breakpoints, the density tokens, the rationale and the component
  contract. Only the second can be handed on.

The second ground is the durable one: it would still hold if every gallery opened its doors
tomorrow. All five are recorded in the registry's `excluded` block with a verified date, so a
later reader can tell an excluded source from an overlooked one, and the validator rejects a
coverage cell or a fallback naming any of them.

## Two procedures

**Procedure 1 — the UI-pattern vocabulary map.** The search protocol, built before any searching.
Five axes: `component` (what the screens contain), `pattern` (how they behave),
`screen-archetype` (what kind of screen), `platform-context` (web, iOS, Android, desktop), and
`design-system` (systems already in use or worth walking). Expansions are typed by relation and
carry honest provenance — `extracted` claims a real corpus used the term, `model-knowledge` says
you supplied it from recall, and a reviewer weighs them differently. Because the map is built
*before* the search, `model-knowledge` is the honest default unless a live vocabulary probe ran.

**Procedure 2 — one search angle.** Seven angles, two always-on and five conditional:

| Angle | Trigger | Cap |
| --- | --- | --- |
| a1 design-system documentation traversal | always | 40 |
| a2 interaction-pattern specification traversal (ARIA APG) | always | 35 |
| b1 platform HIG retrieval | conditional | 30 |
| b2 deceptive-pattern and enforcement corpus mining | conditional | 25 |
| b3 accessibility-criterion deep retrieval | conditional | 90 |
| b4 domain-convention mining | conditional | 20 |
| b5 open-source UI-documentation retrieval | conditional | 20 |

The caps are deliberately non-uniform, sized to the corpus each angle walks. b3's 90 exists
because WCAG's success-criteria set is enumerable and a cap below an angle's enumerable set
truncates a corpus it could have covered completely — a uniform cap would have silently cut it.

Output is a coverage grid of (group type × source) cells, each carrying its queries **verbatim as
run**. For a corpus walk the query *is* the traversal: which index, which pages, selected by what
criterion — a paraphrase cannot be re-run, and a coverage record that cannot be re-run proves
nothing.

## What is enforced rather than requested

- **Negative terms are mandatory on `design-system` groups only.** Carbon, Spectrum, Polaris,
  Primer and Fluent each match an enormous amount of unrelated text. The rest of this corpus is
  keyed by stable identifiers — WCAG criterion numbers, APG pattern names — where exclusions
  would be noise, so the requirement is scoped to the axis that needs it.
- **Coverage completeness in both directions.** Every applicable cell owes a record, and no cell
  may fall outside the applicable set. A missing cell is an unexplained gap; a surplus one means
  the angle worked another angle's channels and inflated its own arithmetic.
- **`kept` reconciles** against the candidate and unadmitted rows naming that cell.
- **The cap belongs to the registry**, checked in both directions: a run may neither raise its
  own ceiling nor quietly lower it.
- **Every conditional trigger rests on a REQUIRED capability field.** The registry records the
  required-rooted legs as `trigger_anchor` and the optional disjuncts separately as
  `widening_legs` — an optional leg only ever *adds* firings, but a predicate rooted solely on
  one fails closed and invisibly, so the angle looks configured and does nothing.
- **An always-on angle cannot be switched off** by a map — and, less obviously, cannot be
  starved either. Wave 0's `active` source list intersects every later angle's applicable set, so
  a source left `skipped` is a source no angle can query. The map procedure checks that each
  `holds: true` angle still has an active source, because an always-on angle forced to `vacated`
  is the survey silently doing nothing.

## Authority and prescriptivity are different questions

Every candidate records **who says it** (`authority`: normative-standard, published-system,
platform-guideline, secondary-commentary) and **whether it binds** (`prescriptivity`: normative
or descriptive), plus its `corpus_version`. A design system's opinion stated in imperative prose
is not normative; a WCAG success criterion is. Neither is cut — authority ranks, it never
excludes — but downstream must be able to tell them apart, and a single collapsed "credibility"
field would make that impossible.

A claimed `token_format` must be DTCG and versioned, because the downstream consumer reads DTCG
and an unversioned or proprietary claim cannot be handed on unchanged.

## The domain-neutrality limit, stated up front

The always-on angles are domain-neutral by construction: governed design systems and the
interaction specifications deliberately say nothing about what a freight load-board or a
claims-adjudication screen contains. Domain screen conventions arrive only through the
conditional domain-convention angle, so for a simple UI this survey legitimately returns **no
domain-specific screen convention at all**. It also reports what systems *prescribe*, never what
shipped products actually *do* — adoption and divergence are exactly what a screenshot corpus
would have supplied and this one cannot. The reviewing twin has a numbered condition (C26) for an
artifact that overstates this limit away.

## The deterministic gate

`validate_visual_prior_art.py`, two subcommands, 44 rules, 111 tests. Shape and arithmetic only —
whether a cited corpus really contains the convention claimed belongs to the reviewing twin. Exit
0 clean, 1 a rule failed, 2 an input could not be read at all; an input fault is not an artifact
fault and must not send anyone off to edit a file that may be fine.

A fault in the package's own source registry exits **2** as well, on both subcommands. The registry ships inside the package, so a defect in it is a package fault rather than a fault in the artifact under test — reporting it at exit 1 sent a caller off to edit a map that was perfectly fine, and only one of the two subcommands ever checked it.

**A clean gate is not the bar.** Three planted fixtures in `scripts/fixtures/planted/` pass it
and are each wrong: a degraded cell rewritten as a searched zero, a relevance line asserting a
keyboard contract the cited pattern page does not carry, and a W3C normative pattern demoted to
`authority: published-system` / `prescriptivity: descriptive`. They exist to prove the reviewing
skill's conditions bite, and they are the reason a green gate should not be mistaken for a good
survey.

## Companion

`reviewing-visual-prior-art-survey`. Its `references/conditions.md` is the authoritative bar for
the pair — the producer points at it and restates nothing normative, so the two halves cannot
drift into grading the same artifact by different rules.

v1.0.0 — SEARCH wave. Extract and synthesis ship as later append-only waves.
