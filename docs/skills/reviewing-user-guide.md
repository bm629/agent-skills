# reviewing-user-guide

Judge a **finished end-user guide** and decide whether a real (typically non-technical) user can accomplish every supported goal from it — an acceptance gate, not authoring. The review half of the user-guide pair; single-sources its bar from the same dossier as `authoring-user-guide`.

## Purpose

The end-user guide is the consumer-facing help a product user reads to get things done (getting-started tutorial, task how-tos, conceptual explanation, an end-user feature/config reference, troubleshooting). This skill is the gate that decides whether it's good enough: it judges the guide against a **usability + accuracy bar** and emits a machine-parseable verdict, so produce -> review -> accept can run as a loop.

## When to activate

- Judging a finished/draft end-user guide before it's accepted.
- The review step of a produce->review->accept document loop.

### When NOT to activate

- **Authoring an end-user guide** -> `authoring-user-guide` (the producer revises on findings).
- **The developer adoption/integration guide** -> `reviewing-developer-guide`.
- **The HTTP/SDK endpoint catalog** -> `reviewing-api-reference`.
- **Engineering design docs** (ADR/RFC) -> `design-review`.

## The usability + accuracy bar (12 conditions)

Judges each, pass/gap: every user goal in the **handed-in upstreams** has a how-to (goals from the user-flows when present, else the feature-spec/PRD); the four **Diataxis modes** present and **correctly typed** (a how-to is imperative steps, not a concept dump); the **feature/config reference** complete (the end-user product surface, NOT the HTTP API); every step **accurate** to the product behavior — named by its exact UI label — nothing fabricated; procedure mechanics sound; **troubleshooting** covers the known error states (symptom-keyed); usable by the target audience; gaps surfaced as assumptions; an **amend** reviewed as a scoped, swept, versioned delta (cond-9, n/a greenfield); **plain language / readability** a non-technical reader can follow (cond-10); **accessibility** — meaningful link text, no color-/location-only steps (cond-11, proportional); **findability / start-here** (cond-12). Two overlap guards (cond-10↔cond-7, cond-12↔cond-1/cond-2) stop double-penalizing one defect. Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + how to fix). **Approves** a guide that meets the bar — no false-revise — and **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the guide.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **No false-revise** — approves a usable guide even if stylistically improvable.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
