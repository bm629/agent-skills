# Sources — `reviewing-user-guide`

This skill is the **review** half of the end-user-guide pair. Its quality bar is
**single-sourced** with the authoring sibling — the 12 conditions in this skill's Workflow
Step 2 are the same conditions, numbered identically, that `authoring-user-guide` produces
to (its Step-10 self-check), so the produce-bar and the review-bar cannot drift. The bar in
depth lives in `references/usability-bar.md` (the per-pair single source); it does NOT run
an independent research pass. The authorities below ground the bar.

## Single source of the bar (primary)

- **`references/usability-bar.md`** — the 12-condition bar with per-condition pass/gap
  signals + worked findings + the two overlap guards (cond-10↔cond-7, cond-12↔cond-1/cond-2).
  This is the single source `authoring-user-guide` produces to and this skill judges against.

## Underlying authorities (what grounds each condition)

- **Diataxis framework** (diataxis.fr — start-here, tutorials, how-to, reference,
  explanation) — the four documentation modes and the core claim that **mixing the modes is
  the most common cause of confusing documentation**; grounds the "present AND correctly
  typed" check (cond. 2) and the reference-completeness rule (cond. 3).
- **Google developer documentation style guide** (/procedures, /ui-elements) and **Microsoft
  Writing Style Guide** (step-by-step instructions; describing UI interactions) — two
  independent authorities for procedure mechanics (numbered steps, one action per step,
  second person, present tense, imperative voice, task-based headings — cond. 5) and for the
  UI-terminology rule (refer to a control by its exact label, consistently — cond. 4).
- **Carroll's minimalism** (task-oriented documentation) — anchor in the user's real tasks,
  support error recognition + recovery, cut what doesn't serve the task; grounds the
  usability-by-audience check (cond. 7) and the symptom-first troubleshooting (cond. 6).
- **Federal Plain Language Guidelines / plainlanguage.gov** — purpose-first, ~20-word
  sentences, define/glossary jargon, no unexplained acronym, general-audience reading level;
  grounds plain-language/readability (cond. 10), judged by outcome not a score.
- **W3C — WCAG 2.2** (SC 1.1.1 / 1.3.1 / 1.3.3 / 1.4.1 / 2.4.4 / 2.4.6) — meaningful link
  text, heading hierarchy, color- and sensory-independent instructions, text alternatives;
  grounds accessibility (cond. 11). Pixel-contrast/focus-appearance are explicitly the
  rendered-site / design-system's scope, NOT judged here.
- **Nielsen Norman Group — Information Architecture** — findability + discoverability from a
  well-defined IA + navigation; descriptive, specific, mutually-exclusive categories; grounds
  the start-here/findability check (cond. 12).
- **document360 (Documentation Drift) + Archbee (single-sourcing)** — ≈60% of docs outdated
  within six months, stale-worse-than-none; grounds the amend staleness-sweep (cond. 9).
- **User-guide practitioner sources** (ProProfs, Docsie, document360, indoc.pro,
  thegooddocsproject) — the canonical end-user section set and the symptom → cause → fix
  troubleshooting shape (cond. 3, cond. 6).

## Reviewer-discipline evidence (no-false-revise)

- The bar is an **assertable pass/fail checklist** — a condition is a gap only on a *named,
  real* deficiency. This grounds the no-false-revise / no-false-approve discipline and the
  proportionality rule (a thin product's guide is correctly small; cond-9/10/11/12 collapse
  on a thin guide). The well-documented reviewer tendency to over-correct (especially when
  also asked to propose fixes) is why the skill repeatedly calibrates against manufactured
  nits, and why the two overlap guards forbid double-penalizing one defect.

## Sibling skills as structural source material (synthesize-only)

- `reviewing-design-system`, `reviewing-user-flows`, `reviewing-feature-spec`,
  `reviewing-developer-guide` — forge-made review siblings in the same document-skill
  library. Used as **source material** for the shared review-skill shape (the
  `VERDICT: approve|revise` contract, the judge-never-author separation, the
  "judge against the handed-in upstreams / a not-produced upstream is never a revise trigger"
  rule, the proportionality calibration). Paraphrased, never copied; this skill's bar is the
  per-pair `usability-bar.md`, not theirs.

## Provenance note

An earlier forge-time "shared user-guide dossier" exists in the producing repo's research
tree; it predates the angle-discovery method and has been **superseded** as the bar's source
by `references/usability-bar.md` (the per-pair single source distilled from the production-
grade redesign's dossiers). External research text consumed for facts only, screened for
prompt-injection (clean — descriptive documentation terminology).
</content>
