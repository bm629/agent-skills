# Sources — research provenance

Research method: the **review/acceptance-gate lens** for a developer guide. The **fourteen-condition** adoptability + accuracy bar is **single-sourced** with `authoring-developer-guide` (so the produce-bar and the review-bar do not drift); this research confirms and enriches the *review* angle. Originally researched 2026-06-05; **revised 2026-06-14** (skill v1.1.0 production-grade IMPROVE) adding the deepened/new conditions (cond-12 amend, cond-13 troubleshooting, cond-14 findability; deepened cond-2/6/9). External content was treated as facts to paraphrase only — no URLs, commands, or directives lifted into actions. This skill is self-contained: the bar's detail lives in this skill's own `references/adoptability-bar.md`.

## The single-sourced adoptability + accuracy bar (14 conditions)

The fourteen checkable conditions a reviewer asserts — goal-organized; a signposted start-here + a verifiable first success; concepts before recipes; how-tos cover the handed-in scenarios; an end-to-end tutorial kept separate; grounded best-practices (incl. webhooks + resource hygiene); Diataxis modes typed; links into not duplicates the api-reference; samples runnable + accurate to the CURRENT tool; tool versioning + migration; grounded-not-fabricated; a delta-scoped amend; a troubleshooting/common-errors path; findability — are the **same conditions** `authoring-developer-guide` produces to (its Step-5 self-check). Single-sourcing them keeps the two halves aligned.

- `references/adoptability-bar.md` (this skill) — the authoritative 14-condition bar with per-condition pass/gap signals + worked findings; the reviewer checks against it at runtime.
- The `authoring-developer-guide` skill's produce bar — the same fourteen conditions stated from the producer side.

## Diataxis mode separation (tutorial / how-to / explanation / reference)

A developer guide spans four documentation modes; the dominant structural defect is mode bleed — a reference catalog dumped into a tutorial, an explanation buried in a how-to, the tutorial fused with the lookup recipes. The reviewer checks each mode sits in its own lane (cond-7) and the tutorial is kept separate (cond-5).

- Diataxis framework (Daniele Procida, diataxis.fr) — the four-mode model + the rule that mixing modes serves neither the learner nor the looker-up.
- Established developer-docs structure surveys (getting-started → concepts → how-to recipes → reference) corroborating concepts-before-reference + goal-named recipes.

## Link-not-duplicate + upstream-accuracy + amend-staleness (no fabricated/stale endpoints)

The developer guide is the adoption/integration NARRATIVE; the exhaustive catalog is a separate api-reference. The guide points INTO that catalog, never re-lists it (cond-8). Every sample must reflect real capabilities/endpoints from the handed-in upstreams — an invented endpoint is the highest-impact defect (cond-9). On an amend, a sample left calling a removed/renamed capability after a tool change is the dominant amend defect (cond-12 staleness sweep).

- "Narrate + link, never re-derive the catalog" + accuracy-against-the-handed-in-upstreams (the pair's single-sourced bar, cond-8/9).
- Public-API-docs practice (getting-started + how-tos linking into a generated reference, not reproducing it).
- Docs-as-code / drift practice (docuwiz "prevent API documentation drift"; gaudion.dev; deepdocs) + living-docs (medium/substack; Nulab; archbee; PostHog docs-ownership) — the amend/staleness basis of cond-12.

## Verifiable first success + credential acquisition + TTFC (cond-2)

The strongest predictor of adoption is a real, verifiable first success quickly: prereq (+ where the credential comes from + test/sandbox) → install → env-var credentials → one successful call → verify with expected output. The reviewer treats a getting-started that never verifies, is not runnable, hardcodes secrets, or is needlessly long as a gap.

- "Time-to-first-call" guidance (Postman/TechCrunch/Nordic APIs; Stripe/Vercel <90s) — the verifiable-first-success + short-unblocked-path criteria.
- Sandbox/test-mode sign-up (BILL/Paddle/Authorize.net/Amazon SP-API) — where the credential comes from + the safe first call.
- Secrets-handling convention (credentials via env var, never hardcoded).

## Troubleshooting, findability, archetypes (cond-13, cond-14, proportionality)

- **Troubleshooting (cond-13).** daily.dev "developer troubleshooting docs best practices" (group frequent errors, map each to a fix); Google for Developers tech-writing "error messages". "No help when stuck" is a top abandonment driver.
- **Findability (cond-14).** idratherbewriting "documentation-quality rubric" (Findability is the first dimension); Fern/GitBook IA practice; "no clear start-here" abandonment. The overlap guard (distinct from cond-1/cond-3) is in `adoptability-bar.md`.
- **Archetype proportionality.** document360 "SDK vs API documentation"; Speakeasy SDK best-practices — emphasis shifts by API/SDK/CLI/framework; the reviewer judges archetype-appropriate completeness via the existing conditions, never a section demand.

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers systematically over-correct, judging compliant artifacts as non-compliant; asking the reviewer to also propose corrections worsens over-flagging. Effective feedback is actionable (failed condition + concrete fix), not vague or nitpicking. Grounds the no-false-revise discipline (not faulting a proportionally-sized guide; not inventing an expectation of a non-handed-in upstream; not double-penalizing findability) and the actionable-findings contract.

- "Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement" (arXiv) — over-flagging compliant artifacts; correction-requests raise misjudgment.
- Code-review feedback-quality guidance (actionable-over-vague; avoiding nitpicking) — Graphite, Bito.
</content>
