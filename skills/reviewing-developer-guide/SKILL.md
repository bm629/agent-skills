---
name: reviewing-developer-guide
description: >
  Use when reviewing or judging a finished developer guide — the adoption +
  integration narrative for a developer-tool product (SDK, library, CLI,
  framework, API platform). Deciding whether a developer can install, grasp,
  and integrate the tool from the guide alone. A gate, not authoring. Judges it
  against a single-sourced adoptability + accuracy bar: a verifiable first
  success; concepts before the recipes; how-tos cover the handed-in scenarios;
  code samples runnable and accurate to the tool/API (no fabricated endpoints);
  the guide LINKS INTO the api-reference, never duplicates it; Diataxis modes
  correctly typed; gaps surfaced. Names an upstream-accuracy and an
  api-reference-linking check. Emits exactly `VERDICT: approve|revise` plus
  actionable findings; approves a guide meeting the bar (no false-revise),
  revises only on a named gap. Not for authoring it, not for the end-user
  user-guide, not for the endpoint catalog (api-reference review), not for
  engineering design docs (design-review).
extensions:
  claude:
    when_to_use: "judging a finished developer guide against the adoptability + accuracy bar and emitting an approve/revise verdict"
    argument-hint: "<the finished developer guide to review> (+ the handed-in upstreams: feature-spec / api-reference)"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `reviewing-developer-guide` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished developer guide as an acceptance gate — checking a developer can adopt and integrate the tool from it, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of an authoring/judging developer-guide pair. Loaded by a reviewer who holds a **finished developer guide** — the adoption + integration narrative for a developer-tool product (SDK, library, CLI, framework, or API platform): a getting-started, the core concepts, code-centric integration how-tos, an end-to-end tutorial, production best-practices, and pointers out to the api-reference — it judges that guide against one question: **can a developer install the tool, grasp its mental model, and complete the common integration scenarios from this guide alone, with runnable code, where every step matches what the tool actually does?** It applies a fixed **adoptability + accuracy checklist** — the same bar a developer-guide author produces to, so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate: it does **not** author, fix, or rewrite the guide; it judges and returns findings, and the producer revises.

**Single-sourced bar.** The eleven conditions in Step 2 are not invented here. They are the **§4 adoptability + accuracy quality bar** of the shared developer-guide dossier — the same dossier the authoring sibling produces against — so the review-bar and produce-bar are one bar.

**Medium (today).** The guide under review is **markdown** (prose plus fenced install/integration code), not a rendered docs site. The review **method and bar are medium-independent** — a future Figma/Confluence/rendered-docs backend changes only the medium, not what this skill checks.

## When to activate

- A finished developer guide needs an accept/revise decision before it ships to integrating developers.
- You are the independent reviewer / gate for a developer guide a producer just authored.
- Re-judging a revised developer guide after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a developer guide -> use a developer-guide-authoring skill (it produces to the same bar this skill asserts). This skill never writes the guide.
- Reviewing the **end-user product guide** — the consumer-facing help a non-technical user reads -> use a user-guide-review skill. That gate judges end-user usability; this gate judges developer adoptability.
- Reviewing the **api-reference** — the exhaustive endpoint/symbol catalog a developer looks an operation up in -> use an api-reference-review skill. That gate judges catalog completeness and contract-consistency; **this** gate judges the developer **narrative** that links into it.
- Reviewing an **engineering design document** — an architecture spec, design doc, ADR, or RFC -> use a design-review skill that verifies design claims against the codebase. Distinct gate, distinct bar.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole guide with fresh, independent eyes, and gather the upstreams

Read the developer guide end to end as if you were a developer adopting the tool for the first time, without the author's framing. Your stance is a gatekeeper: a finding carries weight only when it shows a developer **cannot adopt or integrate the tool as written**, or where a step **does not match what the tool actually does**.

Pull in the **handed-in upstreams** (typically a feature-spec and, for an API platform, an api-reference) — Step 2's accuracy and coverage conditions are checked *against* them. Identify the **product archetype** the guide is sized to (a thin single-purpose CLI vs. a broad API platform); the bar scales with it. Note the spots where a code sample, an integration step, or an api-reference pointer is load-bearing — those are what the checklist scrutinizes.

### Step 2: Run the adoptability + accuracy checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have ordered the sections differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). These eleven conditions are the single-sourced bar (the shared dossier's §4); do not add private ones.

1. **Goal-organized.** The guide is framed around what the developer can build/accomplish, with recipes named by goal — not a flat list of endpoints. *Gap* when it is an endpoint dump with no adoption narrative.
2. **Getting-started reaches a verifiable first success.** Prerequisites -> install -> configure credentials -> one real successful call -> a **verify** step with the expected output. The path is runnable and copy-pasteable, demonstrates real value (not a bare hello-world), and uses **env-var** credentials, never hardcoded secrets. *Gap* when there is no verify step, the first call is not runnable, or credentials are hardcoded.
3. **Core concepts present and BEFORE the recipes.** The mental model — client object, domain nouns, lifecycle, environments — is explained as understanding-oriented content, ahead of the integration recipes, not as a parameter list. *Gap* when concepts are absent, or buried after / inside the recipes so a reader hits code before the model.
4. **Integration how-tos cover the common scenarios** in the handed-in upstreams. One goal-named, code-centric, independently-followable recipe per common scenario the upstreams describe; runnable code; links into the reference for full options. *Gap* when a common scenario present in the handed-in feature-spec/api-reference has no recipe (a coverage hole).
5. **An end-to-end tutorial builds one small real thing** start to finish, kept **separate** from the section-4 lookup recipes (correct How-to vs Tutorial typing). *Gap* when there is no end-to-end build, or the tutorial and the recipes are fused.
6. **Best-practices grounded in real usage.** Auth/secrets, retryable-vs-fatal error handling, retries + idempotency + backoff, pagination, rate limits — each a recommended pattern plus a snippet, not an option dump. *Gap* when production concerns are absent or are a bare list of options with no recommendation.
7. **Diataxis modes correctly typed and separated.** Tutorial / how-to / explanation / reference each sit in their own mode; no mode bleeds into another (no reference catalog dumped into the tutorial, no explanation buried inside a recipe). *Gap* when modes are confused — e.g. the getting-started is actually a reference dump, or concepts are smeared across recipes.
8. **Links into — never duplicates — the api-reference.** The exhaustive endpoint/symbol catalog is **pointed to** as the source of truth, not re-listed inside the guide. *Gap* when the guide reproduces the endpoint/symbol catalog inline instead of linking it (this is the **api-reference-linking** check — see Step 3).
9. **Code samples runnable + accurate to the actual tool/API.** Every sample reflects **real** capabilities/endpoints from the handed-in feature-spec/api-reference; credentials via env var; nothing contradicts the upstream contract. *Gap* when a sample calls an endpoint, method, or capability that does **not** exist in the upstreams — a fabrication (this is the **upstream-accuracy** check — see Step 3).
10. **Versioning + migration stated.** The version scheme, deprecation policy/timelines, a changelog link, and per-major-jump before/after migration notes are present (sized to the archetype). *Gap* when a versioned tool ships no versioning/migration guidance.
11. **Grounded, not fabricated.** Capabilities/endpoints/code reflect the upstreams; genuine gaps are surfaced as **explicit assumptions/open-questions** rather than invented endpoints, capabilities, or code paths. *Gap* when a missing answer was fabricated to look complete instead of flagged.

**Two named checks** (they sharpen conditions 8 and 9 and are the highest-impact ones):

- **Upstream-accuracy check** (condition 9). Spot-check the integration steps and code samples against the handed-in feature-spec / api-reference. An **invented capability or endpoint** is the highest-impact defect and a named gap. If an upstream is **absent** — e.g. a non-API CLI has no api-reference to check against — flag the missing upstream as an **assumption** and judge adoptability on what was handed in; absence of an upstream is **not** itself a revise trigger.
- **Api-reference-linking check** (condition 8). The guide must point **into** the api-reference as the source of truth and never re-list the catalog. Inline re-listing of the endpoint/symbol catalog is a gap; a clear pointer is a pass.

**Proportionality.** "Adopt and integrate from it" scales with the product. A thin single-purpose CLI's guide legitimately **collapses sections it does not need** — fewer recipes, lighter concepts, no migration matrix — and that is correct sizing, not a gap. A broad API platform expands the recipes and migration notes. Judge **a first verifiable success plus a correct production integration**, not section count or word count. A small, complete guide that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity. (Conditions 2 and 9 still bind at any size: the first call must verify, and no sample may fabricate.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A developer can install the tool, grasp its model, and complete the common integration scenarios from this guide alone, with runnable code, and every step matches what the tool actually does. Approve even if you can imagine stylistic improvements; the bar is adoptability + accuracy, not perfection or maximalism.
- **revise** — one or more conditions have a real, named gap that blocks adoption or integration: no verifiable first success, concepts after the recipes, a missing recipe for a handed-in scenario, a **fabricated** endpoint/capability, the catalog duplicated instead of linked, confused Diataxis modes, or a fabricated answer.

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Upstream-accuracy (cond. 9), the "Send a message" recipe: it calls `client.messages.schedule(at=...)`, but the handed-in api-reference has no scheduling endpoint or `schedule` method. Fix: replace with a real capability from the api-reference, or, if scheduling is genuinely intended but undocumented, surface it as an open-question rather than shipping an invented call.

> **revise** — Api-reference-linking (cond. 8), the "Reference" appendix: the guide re-lists all 40 endpoints with parameter tables, duplicating the api-reference. Fix: replace the inline catalog with a pointer to the api-reference as the source of truth, keeping only the handful of endpoints the recipes actually use.

A bad finding is vague and unactionable:

> The code examples could be more thorough. *(Which sample? What is wrong with it? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling (`_parse_verdict`) parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the guide. The producer revises.
- **Single-sourced bar.** Judge against the eleven conditions in Step 2 — the shared dossier's §4, the same bar the author produces to. Do not invent extra conditions or apply a stricter private standard.
- **No false-revise.** A guide that meets every applicable condition is approved, even a thin one for a single-purpose tool. Proportional sizing that still reaches a first success and covers the handed-in scenarios is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **A fabricated endpoint/capability is a gap, not grounding.** A code sample or integration step that calls something absent from the handed-in upstreams fails condition 9 — this is the highest-impact defect. A real gap should be flagged as an assumption/open-question, not papered over with an invented call.
- **The catalog must be linked, not duplicated.** A guide that re-lists the endpoint/symbol catalog inline instead of pointing into the api-reference fails condition 8.
- **First success must verify.** The getting-started must reach a runnable, verifiable first successful call with an expected-output check and env-var (not hardcoded) credentials (condition 2).
- **Concepts before recipes.** The mental model must precede the integration how-tos (condition 3); a guide that throws code before the model fails it.
- **Judge against the upstreams the guide was given.** Assess accuracy and coverage against the handed-in upstreams (the feature-spec / api-reference the project produced). A **not-handed-in** upstream is **never** a revise trigger — flag it as an assumption and judge adoptability on what you have. But a guide that **ignored a handed-in upstream** (a scenario in the feature-spec with no recipe, a sample contradicting the api-reference) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first (fabrication, no first success), then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of adoptability.** Every section can be present and a developer still unable to integrate (the first call doesn't verify, a sample fabricates an endpoint, concepts sit after the recipes). Judge whether a developer can *adopt and integrate*, not whether the *template is filled*.
- **The fabricated endpoint hiding in a runnable-looking sample.** A code sample can read perfectly and call a method or endpoint the tool does not have. It looks authoritative but breaks the moment a developer runs it. Spot-check every load-bearing sample against the handed-in api-reference/feature-spec (cond. 9) — this is the dominant high-impact defect.
- **The catalog re-listed inline.** A guide can helpfully reproduce all the endpoints with parameter tables — and now it is a second, drifting copy of the api-reference. The guide must link the catalog, not duplicate it (cond. 8). Easy to wave through because it looks thorough.
- **Concepts smuggled into the recipes.** The mental model gets explained piecemeal inside the how-tos, so there is no concepts-before-reference section — a reader hits code before the model (cond. 3). Reads complete; isn't.
- **Diataxis mode bleed.** The "getting-started tutorial" is actually a reference dump, or the end-to-end tutorial is fused with the lookup recipes. Each mode must stay in its lane (cond. 7); mixed modes read fine but serve neither the learner nor the looker-up.
- **Missing-upstream over-flagging.** A non-API CLI has no api-reference, so there is nothing to link or accuracy-check the way an API platform has. That absence is an **assumption to note**, not a revise — do not invent an expectation of an upstream the project never produced.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems — especially one also asked to suggest fixes — tends to over-correct, judging sound guides as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on a section you'd have written differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a proportionally-sized guide.** A thin single-purpose tool's guide is correctly small — a couple of recipes, light concepts, no migration matrix. That is right-sizing, not under-coverage. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the archetype.
- **Confusing this with the user-guide or api-reference gate.** A developer guide is the developer adoption **narrative**. A user-guide judges end-user (non-technical) usability; an api-reference judges the endpoint/symbol catalog. Don't apply an end-user-usability or a catalog-completeness bar to the developer narrative.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch guides no developer can integrate from; a fabricated endpoint or a first-call that never verifies waved through becomes a developer stuck on step one.
- **Nit-pick revise.** Blocking on section-order taste, prose style, or nice-to-haves dressed up as gaps. Revise is for real adoptability/accuracy blockers only.
- **Silent rewrite.** "It was easier to just fix the sample" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a Postman collection / a video") drifts the review-bar off the produce-bar and causes spurious revises. Judge the eleven conditions only.
- **Maximalism.** Demanding the full broad set of recipes and a migration matrix from a thin single-purpose tool's guide. The bar is a first verifiable success plus the handed-in scenarios covered, not the largest possible guide.
- **Skipping the upstream spot-check.** Approving code samples on plausibility alone without checking them against the handed-in api-reference/feature-spec. The accuracy check is the highest-impact dimension; never skip it.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one developer guide:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce->review loop: `approve` accepts the guide for shipping to integrating developers; `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **developer-guide-authoring** skill — the produce half of the pair; it writes the guide to the same adoptability + accuracy bar this skill judges against. Pairing them single-sources the bar (the shared dossier's §4) so produce and review do not drift.
- A **user-guide-review** skill — the gate for the end-user product guide (the consumer-facing help a non-technical user reads). Distinct doc, distinct audience, distinct bar; this skill judges developer adoptability, not end-user usability.
- An **api-reference-review** skill — the gate for the exhaustive endpoint/symbol catalog. Distinct doc, distinct bar; this skill judges the developer narrative that **links into** that catalog, not the catalog itself.
- A **design-review** skill — the gate for engineering design documents (architecture specs, design docs, ADRs, RFCs), which verifies claims against the codebase. Distinct gate, distinct bar; not for a developer guide.
- A **developer-guide template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/sources.md` — research provenance for the review method: the single-sourced adoptability + accuracy quality bar (the shared developer-guide dossier's §4), the Diataxis-mode-separation criterion, the link-not-duplicate rule, and the reviewer-overcorrection evidence behind the no-false-revise discipline. Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the skill listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
</content>
</invoke>
