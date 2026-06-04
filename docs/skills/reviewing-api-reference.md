# reviewing-api-reference

Judge a **finished, published API reference** and decide whether an integrating client developer can call the API from it — an acceptance gate, not authoring. The review half of the api-reference pair; single-sources its bar from the same dossier as `authoring-api-reference`.

## Purpose

The api-reference is the published consumer documentation a client developer reads to integrate against an API (getting-started, authentication, a per-endpoint reference, shared object types, errors + rate-limits, code samples, a changelog) — derived from, and consistent with, the engineering api-spec contract. This skill is the gate that decides whether it's good enough: it judges the reference against a **usability + contract-consistency bar** and emits a machine-parseable verdict, so produce -> review -> accept can run as a loop.

## When to activate

- Judging a finished/draft published API reference before it's accepted.
- The review step of a produce->review->accept document loop.

### When NOT to activate

- **Authoring an api-reference** -> `authoring-api-reference` (the producer revises on findings).
- **The end-user product guide** -> `reviewing-user-guide`; **the developer adoption guide** -> `reviewing-developer-guide`.
- **The engineering api-spec** (the wire contract) -> `design-review`.

## The usability + contract-consistency bar

Judges each, pass/gap: **getting-started + auth** let a developer make a first call; **every api-spec operation** is documented with purpose + typed params + a **worked example** + its error responses; the reference is **CONSISTENT WITH THE HANDED-IN api-spec** — every endpoint, parameter, shape, and error traces to the contract, with no drift and no fabricated endpoints (the **load-bearing check**); errors + rate-limits documented; code samples present; versioning stated; gaps surfaced. Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + how to fix). **Approves** a reference that meets the bar — no false-revise of a proportionally-sized one — and **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the reference.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **Contract-consistency is load-bearing** — traces every endpoint/shape/error to the handed-in api-spec; drift or a fabricated endpoint is the highest-impact gap.
- **No false-revise** — approves an integrable reference even if stylistically improvable.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
