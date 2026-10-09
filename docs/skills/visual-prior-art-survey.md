# `visual-prior-art-survey`

Run a systematic visual and interaction prior-art survey end to end: what the industry's
documented conventions already prescribe for a product's domain, and what an accessibility
standard actually requires — before any wireframe, design system or hi-fi screen is produced.

## The organising idea

**A domain with no documented convention and a search that never ran produce identical-looking
output.** Everything in this skill exists to keep those apart. A recorded zero is a receipt that
the search happened; an unreachable source is a typed failure carrying its cause; a source
excluded on its terms is a *decision*, not an outage. Three different facts, and the schema
refuses to let them collapse into one.

## The modality lock — documentation, with captures kept apart

This survey mines governed design systems, the ARIA Authoring Practices Guide, WCAG success
criteria, platform human-interface guidelines and the deceptive-pattern corpus. **It does not
survey screenshot galleries**: the galleries — Mobbin, Pttrns, Dribbble, Page Flows, Lapa Ninja —
are subscription products whose terms forbid automated extraction. All five are recorded in the
registry's `excluded` block with a verified date, so a later reader can tell an excluded source
from an overlooked one, and the validator rejects a coverage cell, a fallback, a candidate URL or
a capture naming any of them.

One conditional angle, b6, captures named sites within each site's robots.txt and terms, labelled
**observed, not prescribed** and kept apart everywhere: a pixel shows one firm's choice;
documentation states the rule and its rationale. A capture never binds (`applies: false`), never
enters `conventions`, a lens or a token block, and the register carries it in `observations`.

## Four procedures

**Procedure 1 — the UI-pattern vocabulary map.** The search protocol, built before any searching.
Five axes: `component` (what the screens contain), `pattern` (how they behave),
`screen-archetype` (what kind of screen), `platform-context` (web, iOS, Android, desktop), and
`design-system` (systems already in use or worth walking). Expansions are typed by relation and
carry honest provenance — `extracted` claims a real corpus used the term, `model-knowledge` says
you supplied it from recall, and a reviewer weighs them differently. Because the map is built
*before* the search, `model-knowledge` is the honest default unless a live vocabulary probe ran.

**Procedure 2 — one search angle.** Eight angles, three always-on and five conditional:

| Angle | Trigger | Cap |
| --- | --- | --- |
| a1 design-system documentation traversal | always | 40 |
| a2 interaction-pattern specification traversal (ARIA APG) | always | 35 |
| b1 platform HIG retrieval | conditional | 30 |
| b2 deceptive-pattern and enforcement corpus mining | conditional | 25 |
| b3 accessibility-criterion deep retrieval | always | 90 |
| b4 domain-convention mining | conditional | 20 |
| b5 open-source UI-documentation retrieval | conditional | 20 |
| b6 live-site capture | conditional | 10 |

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
domain-specific screen convention at all**. It reports what systems *prescribe*; b6 adds what a
few named sites *do*, observed and never read as adoption. The reviewing twin has a numbered condition (C26) for an
artifact that overstates this limit away.

**Procedure 3 — deep-read one convention source.** One record per convention source: one design
system, one ARIA pattern, one platform HIG section, one deceptive-pattern type, one WAI tutorial
page. The relevance
bail is taken at the FRONT, before the read, and is the survey's only cut — a bailed source still
ships a record carrying its reason, because an unread source recorded is evidence while a missing
file is indistinguishable from an oversight.

**Procedure 4 — synthesize the register and report.** Five lenses cut across the corpus
(convergence, conflict, applicability, token availability, absence). The output is two files: a
human `report.md` in eight fixed sections, and `convention-register.yaml` — the machine half the
downstream design skill reads, which is also the build-handoff index. A design system's DTCG
tokens are carried per system, verbatim, never blended across systems.

## The deterministic gate

`validate_visual_prior_art.py`, four subcommands, 70 rules, 163 tests. Shape and arithmetic only —
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

v1.1.0 — EXTRACT + SYNTHESIS waves. One record per convention source, then the project-level
convention register and report.

v1.1.1 — the deterministic gate stops blaming the register for a bad `--extracts` path.
`extracts-unreadable` and `extracts-empty` each name their own cause and suppress the row-level
checks; a directory that is empty while nothing cites a record stays green, because those two
facts agree.

v1.2.2 — a required body heading must be a line of its own. The check matched substrings, so `## Statements`
passed for `## Statement`.

v1.2.3 — the body names all four procedures and all four artifacts. It had said two of each, and told
the reader not to use the skill for the deep read or the synthesis it has shipped since v1.1.0.

v1.2.4 — WCAG 2.2 is counted as 86 success criteria, not 87. The 87 included 4.1.1 Parsing, which
the Recommendation lists as obsolete and removed. b3's cap of 90 still clears the corpus.

v1.3.0 — a conditional angle, b6, captures named live sites as observed, never prescribed. It fires
on `ui.complexity: consumer-grade`. `scripts/capture_live_site.py` (standard library plus Chrome or
Chromium, found on PATH or through `CAPTURE_CHROME`, 24 tests) reads robots.txt and the terms, then
records full pages at 320 and 1280
px, light and (where offered) dark, with computed fonts, sizes and colours. Observed rows live in
the register's `observations`, and the report gains section 7 for them. Seven gate rules:
`observed-kept-apart` (which also refuses a capture that binds), `excluded-site`, `capture-file`,
`capture-identity`, `capture-verbatim`, `capture-order` and `one-user-agent`.

v1.4.0 — a WAI tutorial page has an id class, so b3 can carry what it reads from `wai-tutorials`.
`wai-tutorial` ids are `WAI-TUT-<path>`, the page's path under `/WAI/tutorials/` with slashes as
hyphens, and the page's "Updated" date is its release. A tutorial is `normative-standard` and
`descriptive`: W3C says it, but it is informative and binds nothing. One gate rule,
`tutorial-descriptive`, refuses a tutorial candidate or record marked otherwise.
