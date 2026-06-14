# Sources — `reviewing-technical-design`

Research provenance for the review method and the 11-condition implementability
bar. The bar is single-sourced with `authoring-technical-design` (the reviewer
judges exactly what the author produces to). External content was descriptive
(genre structure, quality criteria) — no commands, URLs, or tool references were
lifted into actions.

## The design-doc / RFC genre and its quality bar

- **Malte Ubl, "Design Docs at Google"** (industrialempathy.com) — the anatomy
  the bar judges: context/scope, goals/non-goals, the actual design, alternatives
  considered (a fixed section focused on trade-offs), cross-cutting concerns
  (security/privacy/observability). The implementability standard: an engineer
  can build from it without re-deriving the design.
- **The Pragmatic Engineer (Gergely Orosz)** — common cross-company RFC/design-doc
  sections (problem, solution, detailed design, alternatives, testing, rollout,
  risks, open questions); the review/sign-off culture these docs sit in.
- **Mike Cvet, "Goals and Failure Modes for RFCs and Technical Design Documents"**
  (Better Programming) — the failure-modes framing the cond-6 check rests on.

## Traceability + single source of truth (cond-1, cond-4)

- **Requirements-traceability (RTM) practice** — forward (requirement→design) +
  backward (design→requirement) trace; an orphan design element and an uncovered
  requirement are both defects. Basis for cond-1.
- **Single-source-of-truth / API-design guidance** (Speakeasy "Documentation Best
  Practices in REST API Design"; Google Cloud API Design Guide) — duplicating a
  contract across docs is the canonical drift failure; reference the owning spec.
  Basis for cond-4 (reference-not-duplicate).

## Failure modes, observability, rollout (cond-6, cond-7, cond-9)

- **FMEA practice** — each failure carries detection + effect + mitigation;
  basis for the failure-with-handling check.
- **Observability practice** (logs / metrics / traces; alerting on the dominant
  failure mode) — the signals that detect the failures and arm rollback; basis
  for cond-7 and the cond-9 measurable-trigger check.
- **Squarespace RFC rollout/timeline + RFC change-plan/rollback models +
  feature-flag rollout practice** — phasing/flag + a documented revert with
  measurable triggers; basis for cond-9.

## Amend lifecycle (cond-11)

- **RFC/ADR lifecycle practice** — "Status: Superseded by NNN" + reciprocal
  note; status→date table; ADR proposed/accepted/deprecated/superseded states;
  IETF updates/obsoletes. Basis for the delta-scoped, versioned, superseded-
  marked amend review.

## Reviewer discipline (no-drift, no-false-revise)

- **Single-sourced review practice** (the producing/judging pair pattern, shared
  with `reviewing-prd` / `reviewing-feature-spec`) — the reviewer judges exactly
  the conditions the author produces to; inventing a condition the author
  doesn't target is the cardinal drift.
- **Reviewer-overcorrection evidence** — reviewers asked to find problems tend to
  over-flag sound work; the no-false-revise + proportionality rules guard a thin
  but complete design from a manufactured gap. Note the cross-skill nuance:
  rollout/observability/testing are *invented* conditions for a feature-spec but
  *real* conditions for a TDD — the bar is doc-type-specific.
