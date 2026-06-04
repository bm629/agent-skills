# reviewing-user-flows

Judge a **finished user-flows document** and decide whether a downstream wireframing pass can enumerate every screen from it — an acceptance gate, not authoring. The review half of the user-flows pair; single-sources its bar from the same dossier as `authoring-user-flows`.

## Purpose

A user-flows doc is the navigation/interaction graph — the paths a user takes to accomplish each goal. This skill is the gate that decides whether it's good enough to wireframe from: it judges the doc against a **completeness + walkability bar** and emits a machine-parseable verdict, so produce → review → accept can run as a loop.

## When to activate

- ✅ Judging a finished/draft user-flows doc before it's accepted for wireframing.
- ✅ The review step of a produce→review→accept document loop.

### When NOT to activate

- **Authoring a user-flows doc** → `authoring-user-flows` (the producer revises on findings).
- **Screen layout / wireframes** → `reviewing-wireframes`.
- **Reviewing the upstream PRD** → `reviewing-prd`.

## The completeness + walkability bar

Judges each, pass/gap: every PRD goal/persona **maps** to a flow (no orphans); every flow has a defined **entry + exit/success**; every **decision branch resolves** to a step/flow/exit; every **error state has a recovery** (no dead ends); steps are **unambiguous + walkable**; the **Mermaid diagram and numbered narrative stay in sync**; the **screens index is enumerable**; open questions surfaced. Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + the fix). **Approves** a doc that meets the bar — no false-revise — and **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the doc.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **No false-revise** — approves a walkable doc even if stylistically improvable.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
