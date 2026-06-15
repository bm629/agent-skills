# Method depth — `authoring-user-guide`

The depth behind the SKILL.md method. The body carries each angle as concise method; this
file carries the how-to a producer loads when authoring a section whose method they want in
full. Grounded in established end-user-docs practice (Diataxis, the Federal Plain Language
Guidelines, WCAG 2.2, NN/G information architecture, task-oriented minimalism) — see
`sources.md` for provenance.

## Plain language / readability (cond-10)

The audience is **typically non-technical** and the artifact is **read, not run**, so
comprehensibility is load-bearing for "can a real user accomplish the goal".

- **Purpose-first.** State what the section is for and the bottom line up front; most
  important information at the beginning, background later.
- **Short sentences, everyday words.** Prefer short/medium sentences (~20-word average);
  active voice; everyday inclusive words; short paragraphs; segment so key information is
  locatable.
- **Define jargon on first use; no unexplained acronym.** Expand every acronym on first use
  AND define it in the glossary; rewrite to eliminate the need for most definitions; collect
  the unavoidable terms in the glossary (the single definition source).
- **Judged by OUTCOME, not a score.** A Flesch-Kincaid / grade-level number is an authoring
  aid, never the gate — the bar is whether a non-technical reader can follow the guide.
- **Overlap guard vs cond-7.** A jargon/readability defect is cond-10; an unfollowable-flow
  or missing-prerequisite defect is cond-7 (usability). Don't double-judge jargon under
  cond-7.

## Accessibility for a textual help artifact (cond-11)

WCAG 2.2 criteria an author controls **in the markdown text itself** (proportional — n/a
when there are no links/images/color cues):

- **Meaningful link text** (SC 2.4.4 / 2.4.9): a link's purpose is clear from its text — no
  bare "click here" / "read more".
- **Heading hierarchy** (SC 1.3.1 / 2.4.6): headings describe topic/purpose and nest in
  order (no skipped levels).
- **Color-independent instructions** (SC 1.4.1): never convey a step by color alone ("click
  the **green** button") — name the control.
- **Sensory/location-independent instructions** (SC 1.3.3): don't rely on shape/size/visual
  location alone ("the button on the **right**") — name the control.
- **Alt-text intent** (SC 1.1.1): describe each screen in words so a reader who can't see the
  linked wireframe still understands it.
- **Out of scope (the design-system / rendered docs-site owns it):** pixel contrast ratios,
  focus appearance, rendered search — not judged in this textual artifact (the
  wireframes→design-system division of labor).

## Information architecture / start-here findability (cond-12)

A user guide is a **multi-document set** (tutorial + several how-tos + explanation +
reference + troubleshooting + glossary). Findability + discoverability are the result of a
well-defined IA + navigation (NN/G).

- **The §1 start-here signpost.** Route a brand-new reader to the tutorial (§2), a
  task-seeker to the matching how-to (§3), a look-up to the reference (§5), a stuck user to
  troubleshooting (§6) — so a reader finds their entry point without already knowing the
  product.
- **Navigable, mutually-exclusive sections.** Each goal's section is locatable; sections are
  descriptive, specific, and mutually exclusive so the reader navigates without hesitation.
- **Overlap guard vs cond-1/cond-2.** Findability is whether the reader can *locate* the
  start-here + their goal's section — distinct from cond-1 (the guide is *organized* by goal)
  and cond-2 (the modes are correctly *typed*). Trivially holds for a one-page guide; do not
  re-flag under cond-12 a defect already caught by cond-1/cond-2.

## UI terminology consistency (cond-4/cond-5)

- Refer to a control by its **exact label** as the product shows it ("Select **Create**"),
  using the **design-system's** component/term names where one exists.
- The same command/name appears the **same way everywhere** — across every step and every
  screen; a name that appears more than once always appears identically.
- Prefer specific verb labels ("Create"/"Delete") over generic ones — match the product.
- Why load-bearing: a step that says "click Save" when the button reads "Apply" can't be
  mapped to the screen by a non-technical user — a label mismatch is a cond-4 accuracy gap.

## Task-oriented minimalism (aid)

Carroll's minimalism: action-focused not descriptive; simple language; anchor in the user's
real task; cut anything that doesn't serve the task; present a concise overview + the primary
steps, defer edge cases. Treat an **error as a teachable moment** that troubleshooting
exploits (don't try to eliminate errors — support recovery). Judged via the cond-2/cond-5/
cond-6 outcomes, never as a named technique to demand.

## The amend staleness-sweep procedure (cond-9)

A user guide is the **most amend-driven** end-user doc because its subject — the product's
user-visible surface — moves constantly (~60% of docs are outdated within six months; stale
help is "worse than no article" because it breaks user trust). It is a **leaf** artifact: no
document is produced from the user guide, so the ripple is **upstream-driven staleness sweep
+ internal coherence**, with no derived-doc downstream.

1. **Scope the change unit** — a how-to / a reference entry / a getting-started step / a
   screen description / a troubleshooting entry / a glossary term / an explanation claim.
   **Edit, don't rewrite** the whole guide.
2. **Upstream staleness sweep (dominant).** For each changed/removed/renamed capability,
   find **every** guide location that referenced it — across ALL modes (steps, reference
   entries, screen/wireframe links, troubleshooting, glossary, explanation) — and re-make
   each accurate to the current product. A step left describing a removed/renamed feature is
   **fabrication-by-staleness** — the highest-impact defect.
3. **Re-make internal coherence.** The tutorial still runs end-to-end on the new behavior;
   the Diataxis modes stay typed (no step leaked into explanation during the edit); the
   reference still mirrors the product; cross-links + glossary intact.
4. **Version + changelog.** Bump the guide's own Doc version + add a revision-history entry
   (what changed, when, why) — distinct from the product's version and any skill semver.
5. **Mark superseded / removed.** Delete or mark a removed feature's how-to (note the
   replacement); note a renamed setting's old name once for searchers, then retire it.
   Nothing the guide describes silently dangles.

Amend is detected **by input signal** (an existing guide + a change request + the changed
upstreams handed in); on a greenfield first build cond-9 is n/a.
</content>
