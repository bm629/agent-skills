# Sources — `authoring-user-guide`

Research provenance for the section set, the Diataxis-keyed authoring method, and the
usability/accuracy bar. Method: `deep-research` (standard). WebFetch was sandbox-denied in
the forge environment, so retrieval fell back to WebSearch with >=2 independent reputable
sources per structural claim (noted; no single-sourcing, no fabrication). External
search-result text was consumed for facts only and screened for prompt-injection (clean —
descriptive documentation terminology, no commands/URLs/tool references lifted into actions).

## Diataxis — the four modes, kept distinct

- Diataxis — Start here / the four documentation types: tutorials, how-to guides,
  reference, explanation (diataxis.fr/start-here). Source of the "mixing the types is the
  most common cause of confusing documentation" claim and the two distinguishing axes.
- Diataxis — Tutorials (diataxis.fr/tutorials): one guaranteed happy path, learn-by-doing,
  success is the author's responsibility, no failure branches.
- Diataxis — Reference (diataxis.fr/reference): neutral, complete, factual; describe don't
  instruct; structure mirrors the product.
- Tom Johnson, "I'd Rather Be Writing" — What is Diataxis (idratherbewriting.com).
  Independent corroboration of the four-mode model.
- ekline — A technical guide to the Diataxis framework. Corroboration of the two axes.
- coderslingo — The 4 Types of Documentation: Diataxis Explained. Corroboration.

## Task-oriented minimalism (Carroll)

- Minimalism (technical communication) — Wikipedia: action-oriented, anchor in the task
  domain, support error recognition/recovery, support reading-to-do/study/locate.
- Minimalism (J. Carroll) — InstructionalDesign.org. Independent corroboration of the
  four principles.
- Archbee — Minimalism in Technical Writing. Practitioner corroboration.

## Procedure mechanics / docs style (two independent authorities)

- Google developer documentation style guide — Procedures, Headings/titles, voice/person
  (developers.google.com/style): numbered steps, one action per step, second person,
  imperative, task-based headings.
- Microsoft Writing Style Guide — Writing step-by-step instructions, Person
  (learn.microsoft.com/style-guide): imperative mood, complete sentences, second person,
  task-based parallel headings. Independent corroboration of the same mechanics.

## End-user-doc section set + troubleshooting

- Docsie — End-User Documentation: Definition, Examples & Best Practices. Section set +
  troubleshooting/FAQ + glossary.
- ProProfs — User Documentation Guide: Types, Tools & Best Practices. Corroboration of the
  section set.
- Scribe — End User Documentation: Tips, Examples and Templates. Corroboration.
- indoc.pro — Writing a great troubleshooting guide for software applications:
  symptom/cause/solution framework, error codes, conditions, workarounds.
- document360 — How to create a Troubleshooting Guide. Corroboration.
- The Good Docs Project — Troubleshooting template. Corroboration of symptom-first
  organization.

## Plain language / readability (the non-technical-audience differentiator)

- Federal Plain Language Guidelines / plainlanguage.gov — purpose-first, ~20-word average
  sentences, minimize definitions (collect in a glossary), active voice, general-audience
  reading level. Source of the plain-language method (cond-10).
- plainlanguage.gov — The Elements of Plain Language. Corroboration (everyday words, short
  paragraphs, locatable key information).

## Accessibility (WCAG 2.2 for a textual help artifact)

- W3C — Web Content Accessibility Guidelines (WCAG) 2.2 — SC 1.1.1 (text alternatives),
  1.3.1 (info & relationships), 1.3.3 (sensory characteristics), 1.4.1 (use of color),
  2.4.4/2.4.9 (link purpose), 2.4.6 (headings & labels). Source of the accessibility checks
  (cond-11). Pixel-contrast/focus-appearance are explicitly the rendered-site/design-system's
  scope, not this textual artifact.

## Information architecture / findability + UI terminology

- Nielsen Norman Group — Information Architecture / findability + discoverability from a
  well-defined IA + navigation; descriptive, specific, mutually-exclusive categories. Source
  of the start-here/findability method (cond-12).
- Google developer documentation style guide — UI elements (refer to a control by its label;
  consistent label text; specific verb buttons); NN/G — UI Copy. Source of the UI-terminology
  discipline (cond-4/cond-5).

## Documentation maintenance / amend

- document360 — Documentation Drift (≈60% of docs outdated within six months;
  stale-worse-than-none; every release triggers a doc review) + Archbee — Single Sourcing in
  Technical Writing. Source of the amend staleness-sweep rationale (cond-9).

## Repo source material (portable)

- Gateway template research: `docs/templates/user-guide/comprehensive/research.md` (the
  section structure this skill composes against, not duplicated — supplied by the template
  tool at author time).
- The single-sourced 12-condition bar is shared with `reviewing-user-guide` (its
  `references/usability-bar.md` carries the per-condition pass/gap signals); produce-side and
  review-side do not drift.
