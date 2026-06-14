---
name: reviewing-developer-guide
description: >
  Use when reviewing or judging a finished or amended developer guide — the
  adoption + integration narrative for a developer-tool product
  (SDK/library/CLI/framework/API platform). Decides whether a developer can
  install, integrate, and operate the tool from the guide alone. A gate, not
  authoring. Judges it against a single-sourced 14-condition adoptability +
  accuracy bar: a signposted start-here + a verifiable first success; concepts
  before recipes; how-tos cover the handed-in scenarios; samples runnable +
  accurate to the CURRENT tool (no fabricated/stale endpoints); LINKS INTO the
  api-reference, never duplicates it; Diataxis modes typed; a troubleshooting
  path; an amend reviewed delta-scoped. Emits exactly `VERDICT: approve|revise`
  + actionable findings; approves a guide meeting the bar (no false-revise on a
  thin one), revises only on a named gap. Not for authoring it, the end-user
  user-guide, the endpoint catalog (api-reference review), or engineering
  design docs (design-review).
extensions:
  claude:
    when_to_use: "judging a finished or amended developer guide against the adoptability + accuracy bar and emitting an approve/revise verdict"
    argument-hint: "<the finished/amended developer guide to review> (+ the handed-in upstreams: feature-spec / api-reference; on an amend, the change request + changed upstreams)"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-14
---

# `reviewing-developer-guide` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished (or amended) developer guide as an acceptance gate — checking a developer can adopt, integrate, and operate the tool from it, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of an authoring/judging developer-guide pair. Loaded by a reviewer who holds a **finished developer guide** — the adoption + integration narrative for a developer-tool product (SDK, library, CLI, framework, or API platform): a signposted start-here, a getting-started, the core concepts, code-centric integration how-tos, an end-to-end tutorial, production best-practices, a troubleshooting path, and pointers out to the api-reference — it judges that guide against one question: **can a developer install the tool, grasp its mental model, complete the common integration scenarios, recover from the common errors, and operate it in production from this guide alone, with runnable code, where every step matches what the tool actually does?** It applies a fixed **adoptability + accuracy checklist** — the same bar a developer-guide author produces to, so produce-bar and review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate: it does **not** author, fix, or rewrite the guide; it judges and returns findings, and the producer revises.

**Single-sourced bar.** The fourteen conditions in Step 2 are not invented here. They are the adoptability + accuracy bar `authoring-developer-guide` produces to (its Step-5 self-check, 1:1) — distilled in `references/adoptability-bar.md` — so the review-bar and produce-bar are one bar.

**Medium (today).** The guide under review is **markdown** (prose plus fenced install/integration code), not a rendered docs site. The review **method and bar are medium-independent** — a future Figma/Confluence/rendered-docs backend changes only the medium, not what this skill checks.

## When to activate

- A finished developer guide needs an accept/revise decision before it ships to integrating developers.
- You are the independent reviewer / gate for a developer guide a producer just authored.
- Re-judging a revised developer guide after a prior `revise` verdict.
- **Judging an AMEND** — a delta on an already-shipped guide (e.g. the tool shipped a new version) — delta-scoped (cond-12).

**Do NOT activate when:**

- Authoring or repairing a developer guide -> use `authoring-developer-guide` (it produces to the same bar this skill asserts). This skill never writes the guide.
- Reviewing the **end-user product guide** — the consumer-facing help a non-technical user reads -> use a user-guide-review skill. That gate judges end-user usability; this gate judges developer adoptability.
- Reviewing the **api-reference** — the exhaustive endpoint/symbol catalog -> use an api-reference-review skill. That gate judges catalog completeness + contract-consistency; **this** gate judges the developer **narrative** that links into it.
- Reviewing an **engineering design document** — an architecture spec, design doc, ADR, or RFC -> use `design-review` (it verifies design claims against the codebase). Distinct gate, distinct bar.
- Checking template/section conformance -> a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole guide with fresh, independent eyes, and gather the upstreams

Read the developer guide end to end as if you were a developer adopting the tool for the first time, without the author's framing. Your stance is a gatekeeper: a finding carries weight only when it shows a developer **cannot adopt, integrate, or operate the tool as written**, or where a step **does not match what the tool actually does**.

Pull in the **handed-in upstreams** (typically a feature-spec and, for an API platform, an api-reference) — Step 2's accuracy and coverage conditions are checked *against* them. Identify the **product archetype** (a thin single-purpose CLI vs. a broad API platform); the bar scales with it. **On an amend**, also gather the **change request + the changed upstreams** — cond-12 is checked against them. Note the spots where a code sample, an integration step, or an api-reference pointer is load-bearing — those are what the checklist scrutinizes.

### Step 2: Run the adoptability + accuracy checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have ordered the sections differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). These fourteen conditions are the single-sourced bar (`references/adoptability-bar.md`); do not add private ones. Each is **proportional** — a thin tool legitimately collapses what it doesn't need (see Proportionality).

1. **Goal-organized.** Framed around what the developer can build/accomplish, recipes named by goal — not a flat list of endpoints. *Gap* when it is an endpoint dump with no adoption narrative.
2. **Getting-started reaches a verifiable first success.** Prerequisites (incl. **where the credential comes from** — the signup-to-key path — and steering the first call through **test/sandbox** mode) -> install -> configure credentials -> one real successful call -> a **verify** step with the expected output. Runnable + copy-pasteable; demonstrates real value (not a bare hello-world); uses **env-var** credentials, never hardcoded; the path is **short + unblocked** (minimize steps to the first verified success — the TTFC intent, judged as "short + unblocked", never a stopwatch). *Gap* when there is no verify step, the first call is not runnable, credentials are hardcoded, or the path is needlessly long/blocked.
3. **Core concepts present and BEFORE the recipes.** The mental model — client object, domain nouns, lifecycle, environments — explained as understanding-oriented content, ahead of the integration recipes, not a parameter list. *Gap* when concepts are absent, or buried after / inside the recipes.
4. **Integration how-tos cover the common scenarios** in the handed-in upstreams. One goal-named, code-centric, independently-followable recipe per common scenario; runnable code; links into the reference for full options. *Gap* when a common scenario present in the handed-in feature-spec/api-reference has no recipe (a coverage hole).
5. **An end-to-end tutorial builds one small real thing** start to finish, kept **separate** from the section-4 lookup recipes (correct How-to vs Tutorial typing). *Gap* when there is no end-to-end build, or the tutorial and the recipes are fused.
6. **Best-practices grounded in real usage.** Auth/secrets, retryable-vs-fatal error handling, retries + idempotency + backoff, pagination, rate limits, **webhooks** (where the tool emits them — signature/replay/ordering), **resource hygiene** (client reuse/pooling/timeouts) — each a recommended pattern plus a snippet, not an option dump. *Gap* when production concerns are absent or a bare option list with no recommendation.
7. **Diataxis modes correctly typed and separated.** Tutorial / how-to / explanation / reference each in its own mode; no mode bleeds into another. *Gap* when modes are confused (the getting-started is a reference dump; concepts smeared across recipes; tutorial fused with recipes).
8. **Links into — never duplicates — the api-reference.** The exhaustive endpoint/symbol catalog is **pointed to** as the source of truth, not re-listed inside the guide. *Gap* when the guide reproduces the catalog inline (the **api-reference-linking** check — Step 3).
9. **Code samples runnable + accurate to the actual/CURRENT tool/API.** Every sample reflects **real** capabilities/endpoints from the handed-in feature-spec/api-reference; env-var credentials; nothing contradicts the upstream contract; the guide states the tool version the samples target. *Gap* when a sample calls an endpoint/method/capability that does **not** exist in the upstreams — a fabrication (the **upstream-accuracy** check — Step 3). (The reviewer has no tool-version oracle beyond the handed-in upstream; "is the stated version current" is NOT a greenfield check — the freshness teeth live in cond-12.)
10. **Tool versioning + migration stated.** The version scheme, deprecation policy/timelines, a changelog link, and per-major-jump before/after migration notes (sized to the archetype). *Gap* when a versioned tool ships no versioning/migration guidance.
11. **Grounded, not fabricated.** Capabilities/endpoints/code reflect the upstreams; genuine gaps are surfaced as **explicit assumptions/open-questions** rather than invented endpoints, capabilities, or code paths. *Gap* when a missing answer was fabricated to look complete. (Disambiguation from cond-9: cite **cond-9** for a fabricated *endpoint/method in a sample* — the sample-vs-upstream accuracy check; cite **cond-11** for a fabricated *answer/assumption* where a gap should have been surfaced — don't double-list one defect on both.)
12. **Delta-scoped amend (only when amend-mode).** Active ONLY when a **change request + changed upstreams** are handed in (the input signal); on a greenfield first build it is **n/a**. Judge the CHANGE, not the whole unchanged guide: the delta meets the bar on the blocks it touched (changed samples runnable + accurate to the CURRENT tool); the **upstream-staleness sweep is complete** — no sample/recipe/pointer left calling a removed/renamed capability (the highest-impact amend defect); internal coherence holds (concepts-before-recipes, the tutorial still runs); the guide's own version is bumped + a changelog row present; superseded/deprecated content is marked. *Gap* when a stale sample survives, the change history is missing, or superseded content was silently deleted. (Do NOT re-review untouched, still-accurate recipes.)
13. **Troubleshooting / common-errors path present.** A self-serve path for the frequent, knowable failures (symptom -> cause -> fix; an error-code table where the tool has codes; a short FAQ), beyond getting-started's 2–3 first-call failures. *Gap* when a developer hitting a frequent, knowable error has nowhere in the guide to resolve it. **Proportional** — a thin single-purpose tool legitimately folds this into getting-started; that is not a gap. NOT "is there a section literally named Troubleshooting".
14. **Findable — a signposted start-here + a reader-journey order.** A first-time reader can locate the start-here and the section for their goal **without already knowing the API**. *Gap* when there is no orientation / no start-here so a new reader cannot find where to begin. **Proportional** — a one-page guide is trivially findable (not a gap). **Overlap guard (load-bearing):** cond-14 is about *navigation/findability* — do NOT raise it for a defect already caught by cond-1 (goal-*organization*) or cond-3 (concepts-*ordering*); fail cond-14 only when the orientation/start-here itself is missing or unfollowable, never to double-penalize an endpoint-dump (cond-1) or concepts-after-recipes (cond-3).

**Three named checks** (the highest-impact ones):

- **Upstream-accuracy check** (cond-9). Spot-check the integration steps + code samples against the handed-in feature-spec / api-reference. An **invented capability or endpoint** is the highest-impact defect and a named gap. If an upstream is **absent** (a non-API CLI has no api-reference), flag it as an **assumption** and judge adoptability on what was handed in; absence of an upstream is **not** a revise trigger.
- **Api-reference-linking check** (cond-8). The guide must point **into** the api-reference and never re-list the catalog. Inline re-listing is a gap; a clear pointer is a pass.
- **Amend staleness-sweep check** (cond-12, amend-mode only). After a tool change, no guide location may still reference a removed/renamed capability. A surviving stale sample is the dominant amend defect.

**Proportionality.** "Adopt, integrate, and operate from it" scales with the product. A thin single-purpose CLI's guide legitimately **collapses sections it does not need** — fewer recipes, lighter concepts, troubleshooting folded into getting-started, no migration matrix, a trivially-findable single page — and that is correct sizing, not a gap. A broad API platform expands recipes, webhooks, troubleshooting, and migration notes. Judge **a first verifiable success plus a correct production integration**, not section count or word count. A small, complete guide that satisfies every *applicable* condition **passes**. (Conditions 2 and 9 still bind at any size: the first call must verify, and no sample may fabricate.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A developer can install the tool, grasp its model, complete the common integration scenarios, recover from the common errors, and operate it in production from this guide alone, with runnable code, every step matching the tool. Approve even if you can imagine stylistic improvements; the bar is adoptability + accuracy, not perfection or maximalism.
- **revise** — one or more conditions have a real, named gap that blocks adoption/integration/operation: no verifiable first success, concepts after the recipes, a missing recipe for a handed-in scenario, a **fabricated or stale** endpoint/capability, the catalog duplicated instead of linked, confused Diataxis modes, no troubleshooting path for a tool that needs one, an unfindable start-here, an amend that left a stale sample, or a fabricated answer.

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Upstream-accuracy (cond. 9), the "Send a message" recipe: it calls `client.messages.schedule(at=...)`, but the handed-in api-reference has no scheduling endpoint or `schedule` method. Fix: replace with a real capability from the api-reference, or surface scheduling as an open-question rather than shipping an invented call.

> **revise** — Amend staleness-sweep (cond. 12): the guide bumped to SDK v3 but the "Refund a charge" recipe still calls `Client(key=...)`, removed in v3. Fix: sweep all samples to `Client.from_env()`; mark the v2 form superseded.

A bad finding is vague and unactionable:

> The code examples could be more thorough. *(Which sample? What is wrong with it? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else. Downstream tooling (`_parse_verdict`) parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the guide. The producer revises.
- **Single-sourced bar.** Judge against the fourteen conditions in Step 2 (`references/adoptability-bar.md`, the same bar the author produces to). Do not invent extra conditions or apply a stricter private standard.
- **No false-revise.** A guide that meets every applicable condition is approved, even a thin one for a single-purpose tool. Proportional sizing that still reaches a first success + covers the handed-in scenarios is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **cond-14 never double-penalizes.** Do not raise findability (cond-14) for a defect already caught by cond-1 (goal-organization) or cond-3 (concepts-ordering); fail cond-14 only on a missing/unfollowable start-here.
- **A fabricated OR stale endpoint/capability is a gap, not grounding** (cond-9 / cond-12). A sample calling something absent from the handed-in upstreams (or removed by a tool change) is the highest-impact defect.
- **The catalog must be linked, not duplicated** (cond-8).
- **First success must verify** (cond-2) — runnable, verifiable first call + expected output + env-var (not hardcoded) credentials.
- **Concepts before recipes** (cond-3).
- **Amend is delta-scoped** (cond-12) — review the change + the staleness sweep + the change history, NOT the whole unchanged guide; do not false-revise a clean small amend for not re-justifying untouched recipes.
- **Judge against the upstreams the guide was given.** A **not-handed-in** upstream is **never** a revise trigger — flag it as an assumption. But a guide that **ignored a handed-in upstream** (a scenario with no recipe, a sample contradicting the api-reference) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first (fabrication/stale, no first success), then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of adoptability.** Every section can be present and a developer still unable to integrate (the first call doesn't verify, a sample fabricates an endpoint, concepts sit after the recipes). Judge whether a developer can *adopt + integrate + operate*, not whether the *template is filled*.
- **The fabricated endpoint hiding in a runnable-looking sample.** Spot-check every load-bearing sample against the handed-in api-reference/feature-spec (cond. 9) — the dominant high-impact defect.
- **The stale sample after a tool change.** On an amend, a sample left calling a removed/renamed capability reads fine and breaks on run — the dominant amend defect (cond. 12). Run the staleness sweep.
- **The catalog re-listed inline.** A guide can helpfully reproduce all the endpoints with parameter tables — now it is a second, drifting copy (cond. 8). Easy to wave through because it looks thorough.
- **Concepts smuggled into the recipes.** The mental model gets explained piecemeal inside the how-tos, so a reader hits code before the model (cond. 3). Reads complete; isn't.
- **Diataxis mode bleed.** The "getting-started tutorial" is actually a reference dump, or the tutorial is fused with the lookup recipes (cond. 7). Mixed modes read fine but serve neither the learner nor the looker-up.
- **Double-penalizing findability.** Raising cond-14 for an endpoint-dump (that is cond-1) or concepts-after-recipes (that is cond-3) inflates the review. cond-14 is only the missing/unfollowable start-here.
- **Troubleshooting over-flagging.** A thin single-purpose tool folds common errors into getting-started — that is right-sizing, not a missing cond-13. Demand a dedicated troubleshooting section only when the tool's error surface warrants it.
- **Missing-upstream over-flagging.** A non-API CLI has no api-reference to link or accuracy-check — an **assumption to note**, not a revise.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct, judging sound guides defective. A condition is a gap only on a *named, real* deficiency, not on a section you'd have written differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a proportionally-sized guide.** A thin single-purpose tool's guide is correctly small. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the archetype.
- **Confusing this with the user-guide or api-reference gate.** A developer guide is the developer adoption **narrative**; don't apply an end-user-usability or a catalog-completeness bar to it.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming + approving to avoid a revise loop — the gate exists to catch guides no developer can integrate from; a fabricated endpoint or a first-call that never verifies waved through becomes a developer stuck on step one.
- **Nit-pick revise.** Blocking on section-order taste, prose style, or nice-to-haves dressed up as gaps. Revise is for real adoptability/accuracy blockers only.
- **Silent rewrite.** "It was easier to just fix the sample" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a Postman collection / a video / a literal Troubleshooting heading") drifts the review-bar off the produce-bar. Judge the fourteen conditions only — the technique angles (docs-as-code/CI, IA technique, an a11y checklist, archetype overlays, the rubric) are AIDS judged by outcome, never demanded.
- **Maximalism.** Demanding the full broad set of recipes, webhooks, a migration matrix, and a dedicated troubleshooting section from a thin single-purpose tool's guide. The bar is a first verifiable success + the handed-in scenarios covered, not the largest possible guide.
- **Skipping the upstream / staleness spot-check.** Approving code samples on plausibility alone. The accuracy (cond-9) + amend-staleness (cond-12) checks are the highest-impact dimensions; never skip them.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one developer guide:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce->review loop: `approve` accepts the guide for shipping to integrating developers; `revise` returns the findings to the producer for a bounded revision pass.

## Related

- `authoring-developer-guide` — the produce half of the pair; it writes the guide to the same 14-condition adoptability + accuracy bar this skill judges against. Pairing them single-sources the bar (`references/adoptability-bar.md`) so produce + review do not drift.
- A **user-guide-review** skill — the gate for the end-user product guide (non-technical). Distinct doc, distinct audience, distinct bar; this skill judges developer adoptability, not end-user usability.
- An **api-reference-review** skill — the gate for the exhaustive endpoint/symbol catalog. Distinct doc, distinct bar; this skill judges the developer narrative that **links into** that catalog.
- A **design-review** skill — the gate for engineering design documents (architecture specs, design docs, ADRs, RFCs), which verifies claims against the codebase. Distinct gate, distinct bar; not for a developer guide.
- A **developer-guide template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/adoptability-bar.md` — the single-sourced 14-condition adoptability + accuracy bar (the same bar `authoring-developer-guide` produces to): per-condition pass/gap signals + worked findings, including the new cond-12 (amend staleness-sweep), cond-13 (troubleshooting), cond-14 (findability + the overlap guard), and the deepened cond-2/6/9. Load to apply the bar in detail.
- `references/sources.md` — research provenance for the review method: the single-sourced adoptability + accuracy bar, the Diataxis-mode-separation criterion, the link-not-duplicate rule, the amend staleness-sweep, and the reviewer-overcorrection evidence behind the no-false-revise discipline. Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the skill listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
</content>
