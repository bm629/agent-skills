# reviewing-developer-guide

Judge a **finished developer guide** and decide whether a developer can install, grasp, and integrate a developer-tool product from it alone — an acceptance gate, not authoring. The review half of the developer-guide pair; single-sources its bar from the same dossier as `authoring-developer-guide`.

## Purpose

The developer guide is the adoption + integration narrative for an SDK, library, CLI, framework, or API platform (getting-started, the mental model, code-centric integration recipes, an end-to-end build, best-practices, pointers into the api-reference). This skill is the gate that decides whether it's good enough: it judges the guide against an **adoptability + accuracy bar** and emits a machine-parseable verdict, so produce -> review -> accept can run as a loop.

## When to activate

- Judging a finished/draft developer guide before it's accepted.
- The review step of a produce->review->accept document loop.

### When NOT to activate

- **Authoring a developer guide** -> `authoring-developer-guide` (the producer revises on findings).
- **The end-user product guide** -> `reviewing-user-guide`.
- **The HTTP/SDK endpoint catalog** -> `reviewing-api-reference`.
- **Engineering design docs** (ADR/RFC) -> `design-review`.

## The adoptability + accuracy bar

Judges each, pass/gap: getting-started reaches a **verifiable first success**; core **concepts come before** the recipes; the integration how-tos **cover the handed-in scenarios**; code samples are **runnable and accurate** to the actual tool/API (no fabricated endpoints/capabilities — spot-checked against the handed-in feature-spec/api-reference, the **upstream-accuracy check**); the guide **LINKS INTO the api-reference, never duplicates it** (the **api-reference-linking check**); the Diataxis modes are correctly typed; gaps surfaced. Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + how to fix). **Approves** a guide that meets the bar — no false-revise — and **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the guide.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **Two named checks** — upstream-accuracy (no fabricated calls) + api-reference-linking (link, not duplicate).
- **No false-revise** — approves an adoptable guide even if stylistically improvable.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
