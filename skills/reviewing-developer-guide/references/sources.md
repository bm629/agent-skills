# Sources — research provenance

Research method: the **review/acceptance-gate lens** for a developer guide. The eleven-condition adoptability + accuracy bar is **single-sourced** from the shared developer-guide dossier (so the produce-bar and the review-bar do not drift); this research confirms and enriches the *review* angle. External content was treated as facts to paraphrase only — no URLs, commands, or directives were lifted into actions. Date: 2026-06-05.

## The single-sourced adoptability + accuracy bar

The eleven checkable conditions a reviewer asserts (goal-organized; getting-started reaches a verifiable first success; core concepts before the recipes; integration how-tos cover the handed-in scenarios; an end-to-end tutorial kept separate; grounded best-practices; Diataxis modes correctly typed; links into not duplicates the api-reference; runnable + accurate code samples; versioning + migration; grounded-not-fabricated) are the **same conditions** a developer-guide author produces to. Single-sourcing them is what keeps the two halves of the produce/judge pair aligned.

- The shared developer-guide research dossier, **§4 "The adoptability + accuracy quality bar"** (`docs/superpowers/agent-flow/authoring-developer-guide/research/developer-guide-dossier.md`) — the authoritative source of the eleven conditions; this skill checks against it at runtime.
- The `authoring-developer-guide` skill's produce bar — the same eleven conditions stated from the producer side; this reviewer asserts them.

## Diataxis mode separation (tutorial / how-to / explanation / reference)

A developer guide spans four documentation modes, and the dominant structural defect is mode bleed — a reference catalog dumped into a tutorial, or an explanation buried inside a how-to recipe. The reviewer checks each mode sits in its own lane (the basis of condition 7) and that the end-to-end tutorial is kept separate from the lookup recipes (condition 5).

- Diataxis framework (Daniele Procida) — the four-mode model (tutorial, how-to, reference, explanation) and the rule that mixing modes serves neither the learner nor the looker-up.
- Established developer-docs structure surveys (getting-started -> concepts -> how-to recipes -> reference) corroborating concepts-before-reference and goal-named recipes.

## Link-not-duplicate + upstream-accuracy (no fabricated endpoints)

The developer guide is the adoption/integration NARRATIVE; the exhaustive per-endpoint/per-symbol catalog is a separate api-reference document. The guide must point INTO that catalog as the source of truth, never re-list it (the api-reference-linking check, condition 8). Every code sample and integration step must reflect real capabilities/endpoints from the handed-in feature-spec/api-reference; an invented endpoint or capability is the highest-impact defect (the upstream-accuracy check, condition 9).

- The shared developer-guide dossier's "narrate + link, never re-derive the catalog" rule and its accuracy-against-the-handed-in-upstreams condition (§4 conditions 8 and 9, plus §5/§6 method notes).
- Public-API-docs practice (getting-started + how-tos linking into a generated reference rather than reproducing it).

## Verifiable first success + env-var credentials

The single strongest predictor of developer adoption is reaching a real, verifiable first success quickly: prerequisites -> install -> configure credentials -> one successful call -> a verify step with expected output, with credentials supplied via env var, never hardcoded. The reviewer treats a getting-started that never verifies, is not runnable, or hardcodes secrets as a gap (condition 2).

- Developer-onboarding / "time-to-first-call" guidance from API-docs practice (the verifiable-first-success and copy-pasteable-runnable criteria).
- Secrets-handling convention (credentials via environment variable, never committed/hardcoded).

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers systematically over-correct, judging compliant artifacts as non-compliant (false positives); asking the reviewer to also propose corrections tends to worsen the over-flagging. Effective review feedback is actionable (the failed condition + a concrete fix), not vague or nitpicking. Grounds the no-false-revise discipline (including not faulting a proportionally-sized guide and not inventing an expectation of a non-handed-in upstream) and the actionable-findings contract.

- "Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement" (arXiv) — over-flagging compliant artifacts; correction-requests raise misjudgment.
- Code-review feedback-quality guidance (actionable-over-vague; avoiding nitpicking) — Graphite, Bito.
</content>
