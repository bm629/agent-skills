---
name: reviewing-architecture-doc
description: >
  Use when reviewing/judging a finished whole-system architecture document (+ its
  linked ADR files) to decide if an engineer can grasp the system and place a
  feature's TDD within it — an acceptance gate, not authoring. Judges a
  single-sourced 10-condition bar: boundary + external deps + concerns; components
  single-responsibility at whole-system altitude (not api-spec/data-model or
  feature-TDD detail); diagrams ⇄ narrative agree; every significant
  decision a standalone LINKED, immutable ADR (one per file, index in sync, supersede
  not edit); decisions traced + justified; NFR targets realized + tradeoffs named;
  cross-cutting (resilience/security/privacy/observability) addressed; ASRs covered;
  nothing fabricated, claims consistent with the code; amend delta-scoped.
  C4/arc42/ATAM/4+1 are aids judged by outcome. Emits exactly `VERDICT: approve|revise`
  (no false-revise on a thin doc). Not for authoring, the PRD, api-spec/data-model, a
  feature's TDD, or generic design docs/RFCs/standalone-ADRs (use design-review).
extensions:
  claude:
    when_to_use: "judging a finished architecture document (+ its linked ADR files; greenfield or an amend) against the architecture-quality bar and emitting an approve/revise verdict"
    argument-hint: "<the finished architecture doc + its linked ADR files, or the amended doc + its change request>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-14
  reviewed: 2026-06-14
---

# `reviewing-architecture-doc` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished whole-system architecture document (+ its linked ADR files) as an acceptance gate — checking an engineer can grasp the system and a feature's technical-design can place itself within it, then emitting `VERDICT: approve|revise` with actionable findings. Greenfield, or an amend (delta-scoped).

## Overview

This skill is the *review* half of a producing/judging architecture-doc pair. Loaded by a reviewer who holds a **finished whole-system architecture document + its linked ADR files**, it judges them against one question: **can a new engineer grasp the system's structure and the *why* of its major decisions, and can a feature's technical-design locate itself within the architecture, without asking the author?** It applies a fixed **10-condition architecture-quality checklist** (the same bar an architecture-doc author produces to — `authoring-architecture-doc`'s Step-7 — so the produce-bar and the review-bar do not drift), then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the doc; it judges and returns findings, and the producer revises.

**It judges TWO artifacts: the architecture doc AND its linked ADR files.** Condition 4 (the ADR mechanism — index⇄files sync + per-ADR quality + no-rewrite) is **unverifiable from the doc alone** — the reviewer needs the linked ADR files (or the `adr/` directory). If they were not handed in, flag cond-4 as **unverifiable** and say so; never fabricate their content.

The bar is **single-sourced** with the author. The author's *techniques* — the C4 view choice, arc42 section framing, ATAM tradeoff analysis, 4+1 views, the Mermaid diagram form — are **aids the reviewer judges by OUTCOME** (is the boundary drawn? are decisions linked + traced? is each NFR target realized?), never conditions to demand. **But note the boundary:** the ADR mechanism (cond-4), NFR-realization (cond-6), and the system-level observability stance (cond-7) ARE real, load-bearing conditions for an architecture doc — they are *not* "invented" conditions. What stays an aid is the *technique* (C4/arc42/ATAM/4+1/diagram-choice), not the *outcome* (a linked ADR, a realized target, a named operability signal).

## When to activate

- A finished architecture doc needs an accept/revise decision before engineers build within it (or before a feature's technical-design is placed within it).
- You are the independent reviewer / gate for an architecture doc a producer just authored.
- Re-judging a revised architecture doc after a prior `revise` verdict.
- Reviewing an **amend** — an approved architecture doc + a change request — as a delta-scoped review (cond-10).

**Do NOT activate when:**

- Authoring or repairing an architecture doc → use `authoring-architecture-doc`. This skill never writes the doc.
- Reviewing the **upstream PRD / product direction** (what/why, the NFR targets) → use a PRD-review skill. **This** gate judges *how the whole system is structured*, one layer down.
- Reviewing **one feature's technical-design** (a TDD — how one feature is built within the architecture) → use `reviewing-technical-design`, one altitude lower.
- Reviewing the **api-spec or data-model** themselves (the wire contract / persisted schema) → those are their own documents this architecture doc references, with their own gates.
- Reviewing a **generic / ad-hoc engineering design doc, RFC, standalone ADR, spec, or plan** (one not produced as the doc-library `architecture-doc` artifact) → use `design-review`, which verifies design claims against the codebase across those types. **This** gate is for the doc-library architecture-doc artifact — identified **authoritatively** by the `template: architecture-doc` frontmatter; a `# Architecture:` heading is a fallback signal only when frontmatter is absent (a generic doc that merely titles itself "Architecture" without the stamp stays with `design-review`; a standalone ADR not part of an architecture-doc artifact also stays with `design-review`).
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole architecture with fresh, independent eyes — with the ADR files at hand

Read the architecture doc end to end as if encountering the system for the first time, without the author's framing. Your stance is a gatekeeper for everyone who builds within the system: a finding carries weight only when it shows a reader **cannot grasp the structure or place a feature within it** without re-deriving something the doc should have settled. **Keep the linked ADR files open** (cond-4 needs them) plus the upstream PRD / product direction (cond-8 traces against it) and the api-spec / data-model the doc references (cond-2 altitude check). **Is this an amend?** If you were handed a change request / delta against an existing doc, run the delta-scoped path (cond-10 active; scope the review to the changed decisions/structure + their ripple). On a greenfield first build no change request is present — cond-10 is n/a.

### Step 2: Run the architecture-quality checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have structured it differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). The conditions are the single-sourced bar; do not add private ones.

The capability-boundary checklist item (below) applies ONLY when a `capability_record` was injected into the authoring invocation and is available as review context. When absent, treat it as n/a — do not penalise a document for lacking capability-boundary markers when no boundary was defined.

1. **Context, boundary + concerns covered.** A new reader can state what the system is and is not responsible for: the boundary (in / explicitly-out + owner) is explicit, every actor + external dependency is named, a context diagram agrees with the prose, and every identified stakeholder concern is framed by some section/view. *Gap* on an implied boundary, an unnamed external dependency, or a named concern no section addresses. *(Non-collapsing baseline: the boundary + the external set are always stated — their absence hides integration risk.)*
2. **Structure + altitude.** Every major component is named once with a single responsibility + kind (no unexplained boxes); the topology states direction + protocol/style per edge; integration boundaries name a contract owner; the doc stays at **whole-system altitude** — major interfaces + data stores named structurally, NOT every endpoint (api-spec), every table (data-model), or one feature's implementation (TDD). *Gap* on a god-component, an unexplained box, an edge with no direction/protocol, or altitude slip into endpoint/table/feature detail. *(Non-collapsing baseline: one-responsibility-per-component + altitude.)*
3. **Diagrams ⇄ narrative in sync.** Every box/arrow in a diagram appears in the prose and vice-versa; diagrams read standalone; a runtime/deployment view is present where load-bearing. *Gap* on a diagram element the prose never explains (or a prose component the diagram omits), or a multi-service/multi-env system with no deployment view. *(Collapse: a trivial system needs few/no diagrams; the sync rule holds wherever a diagram exists.)*
4. **The ADR mechanism (the signature condition).** Every significant decision is a **standalone, LINKED ADR file** (one decision per file) — not inline-embedded in the doc; the decisions index ⇄ ADR files are in sync (live links both ways, superseded entries marked); and **no accepted ADR is rewritten** (a change is a new superseding ADR). *Gap* on a decision pasted inline instead of a linked ADR, an ADR bundling two decisions, a dangling/missing index link, or an accepted ADR edited in place (history destroyed). *(Non-collapsing baseline: a rewritten accepted ADR is broken at any size; a thin system simply has fewer ADRs. Unverifiable if the ADR files were not handed in — flag, do not fabricate.)*
5. **Significant decisions traced + justified.** Each significant choice/decision (runtime, datastore, messaging, hosting, trust model — the costly-to-change ones) names its **driver** (a requirement / NFR / ASR) and a **real (non-strawman) alternative** with the trade-off it lost on. *Gap* on a load-bearing choice with no driver, or no considered alternative ("we chose X" by assertion). "Team default" is acceptable *if stated*. *(Non-collapsing baseline — the trade-off discipline holds at any size.)*
6. **NFR realization + tradeoffs.** Every NFR target the PRD names has a **realizing mechanism** (not a restated target); for a load-bearing target it is **measurable** (a quality-attribute scenario with a response-measure); quality-attribute tradeoffs are named + resolved where two attributes conflict. *Gap* on a restated target with no mechanism, a "highly available" claim with an undiscussed single point of failure, or a clear tension (latency vs consistency, cost vs availability) never named. *(Collapse: a thin system with no hard NFR keeps this light; a mechanism serving no target is over-engineering.)*
7. **Cross-cutting concerns addressed where the system has the surface.** A resilience stance per integration boundary (timeout/retry/circuit-breaker/fallback/degrade); security (trust boundaries / authn-authz / secrets / untrusted input); privacy where sensitive data flows; and a **system-level observability strategy** (the golden-signal / health / SLO-monitoring posture that makes the system operable). *Gap* on an external dependency with no slow/down stance, an external-facing system with no trust boundary, or a multi-service system with no observability strategy. *(Collapse: a single-process tool with no external deps legitimately collapses most of this; any external dependency that EXISTS gets a failure stance, any external surface a security stance.)*
8. **Requirements / ASR coverage.** Every architecturally-significant requirement has a realizing structure/decision (no uncovered ASR); no major structure exists with no driver (no orphan). Usable downstream: a feature's technical-design can place itself within the architecture without asking the author. *Gap* on an ASR with no realizing structure, or a component/subsystem serving no requirement. *(Collapse: a one-requirement system traces trivially.)*
9. **Assumptions explicit + grounded, not fabricated; consistent with the real system.** Genuine unknowns are surfaced as assumptions / open questions, not papered as settled fact; nothing (a topology, a benchmark, a vendor claim, a rationale) is invented to look complete; and **claims about what the system IS are verified against the real code/topology** (cite `file:line`; mark **unverified** where unconfirmable) — the consistency-with-the-shipped-system check `design-review` formerly provided. *Gap* on a falsely-complete read, a fabricated limit/mechanism, or a claim about existing behaviour that contradicts the code. *(Greenfield clause — non-collapsing baseline of no-fabrication, BUT: when there is no existing code/system to verify against (a brand-new system, or a fictional/example doc), the consistency check is **N/A and never a blocker** — mark it unverified, do not false-revise.)*
10. **(Amend only) delta is well-scoped, ripple-clean, versioned.** When reviewing a change against an existing architecture doc: the delta meets conditions 1–9 **on the elements it touched**; decisions changed via a **new superseding ADR** (no accepted ADR rewritten) with the **index in sync**; the changed structure still traces to a driver (or an upstream-PRD-amend-needed is flagged); the **downward-broad ripple** is handled (the dependent per-feature technical-design fleet + the api-spec/data-model/deployment/runbook the change touches are named); the doc's own version is bumped + a changelog (who/when/what/why) present. *Gap* on an un-scoped delta, a rewritten accepted ADR, an out-of-sync index, an un-flagged ripple, or missing change history. *(Collapse: on a greenfield first build this condition is n/a — do NOT full-re-review an unchanged doc, and do NOT demand a changelog on a first draft.)*

11. **Capability coverage (n/a when no capability records):** all active capabilities appear as named components; `depends_on` DAG reflected in dependency diagram.

**Proportionality.** "Graspable + placeable without re-deriving" scales with the system. A thin product legitimately collapses what it does not need — one component → no topology; single-process → no deployment view; no external dep → no resilience matrix; no hard NFR → light §6; no sensitive data → no privacy; first draft → no changelog. Judge **completeness-of-decisions** + the surface-area floor, not word count or template-section presence. A small, complete architecture that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A new engineer can grasp the system and place a feature's design within it without re-deriving the architecture; the major decisions are justified + recorded. Approve even if you can imagine stylistic improvements; the bar is graspability + buildability, not perfection.
- **revise** — one or more conditions have a real, named gap (an unnamed external dependency, an unexplained box, a decision embedded inline instead of a linked ADR, a rewritten accepted ADR, an NFR target restated with no mechanism, an external dependency with no failure stance, an orphan structure, a fabricated claim, an un-scoped/ripple-broken amend, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — ADR mechanism (cond. 4), §7 + body: the "we chose PostgreSQL over DynamoDB" decision is written inline in §5 with its full context/alternatives/consequences, not recorded as a linked ADR. Fix: move it to a standalone `adr/0003-datastore.md` (Nygard shape), and link it from the §7 decisions index — so the decision is independently addressable and the index is the single source.

A bad finding is vague and unactionable:

> The decisions section could be tightened up. *(Which decision? Why does it fail the bar? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the doc. The producer revises.
- **Single-sourced bar.** Judge against the ten conditions in Step 2 — the same bar the author (`authoring-architecture-doc` Step-7) produces to. Do not invent extra conditions or apply a stricter private standard.
- **Aids are judged by outcome, never demanded.** C4/arc42/ATAM/4+1 framing, the diagram-type choice, are the author's *techniques* — judge whether the boundary is drawn / decisions linked + traced / each target realized, NEVER "you didn't use C4 / draw a 4+1 process view / run ATAM." (ADR-mechanism/NFR-realization/observability OUTCOMES are real conditions cond-4/6/7 — only the techniques are aids.)
- **The ADR mechanism is load-bearing (cond. 4).** A decision embedded inline instead of a linked ADR, or a rewritten accepted ADR, is a real gap (un-addressable decisions / destroyed history), not a style nit. It needs the linked ADR files to verify — flag unverifiable if absent, never fabricate.
- **Verify claims against the system (cond. 9) — with the greenfield clause.** A claim about what the system IS is confirmed against the real code/topology (`file:line`) or marked `unverified`; never invent a gap. When there is no code/system to verify against (brand-new or fictional doc), consistency is N/A and never a blocker.
- **No false-revise.** A doc that meets every applicable condition is approved, even a thin one for a small system. Revise only on a real, named gap. A thin architecture legitimately omits a deployment view, messaging, a separate observability section, a changelog.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Judge against the upstreams the document was given.** Assess the doc against its `depends_on` set + the docs/ADR-files it references. A **not-produced** upstream is **never** a revise trigger. A doc that **ignored a produced upstream** it should have referenced **is** a fair finding.
- **Amend is delta-scoped.** When handed a change against an existing doc, review the delta + its ripple (cond-10) — do NOT full-re-review the unchanged architecture, and do NOT demand a changelog on a greenfield first draft.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of graspability.** Every section can be present and the system still un-graspable (an ambiguous decomposition, unnamed externals, decisions buried inline). Judge whether a reader can *grasp the system + place a feature within it*, not whether the *template is filled*.
- **The decision embedded inline.** A doc with a rich "Technology choices" section looks thorough — but if the significant decisions are pasted inline with full context/consequences instead of standalone linked ADRs, cond-4 fails (un-addressable, un-supersedable). This is the architecture-doc's signature gap and the one generic `design-review` misses.
- **The rewritten accepted ADR.** An accepted ADR edited in place (rather than superseded by a new one) destroys the decision history — a cond-4 gap even when the new content is "better."
- **The restated NFR target.** "99.9% uptime" copied from the PRD with no redundancy/failover mechanism is restating, not realizing (cond. 6).
- **Treating the ADR-mechanism/NFR/observability as invented conditions.** For a *feature-spec* these would be inventing conditions — but for an architecture doc they are the bar (cond-4/6/7). Do not under-review them.
- **Verifying a fictional doc against code.** A dogfood/example architecture doc describes a system that doesn't exist — cond-9's consistency check is N/A there (greenfield clause); flagging "couldn't verify" as a gap is wrong.
- **Inventing conditions (the cardinal drift).** Adding a private requirement the bar does not carry ("you must use the C4 model / draw a 4+1 process view / run an ATAM") drifts the review-bar off the produce-bar. The techniques are judged by outcome only.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct. A condition is a gap only on a *named, real* deficiency, not a decision you'd have made differently.
- **False-revise on a thin system.** A small system's architecture doc is correctly short; collapsed sections it doesn't need (no deployment view, no messaging, no separate observability, no changelog) are not gaps.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — an inline-embedded decision or an unnamed external dependency waved through becomes a defect or a mid-build scramble.
- **Nit-pick revise.** Blocking on wording, diagram style, or nice-to-haves dressed up as gaps. Revise is for real graspability/buildability blockers only.
- **Silent rewrite.** "It was easier to just fix the architecture" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** Adding a requirement the bar does not carry (a named framework, a diagram-type demand) — the dominant drift this gate guards against.
- **Full-re-reviewing an amend.** Re-judging the whole unchanged architecture on a small delta — review the delta + its ripple (cond. 10), proportionally.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one architecture document (+ its linked ADR files):

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the architecture for building within; `revise` returns the findings to the producer for a bounded revision pass. **Medium:** the artifact judged is a **textual-markdown** architecture doc + Mermaid diagrams + linked ADR files today; the bar is medium-independent.

## Related

- **`authoring-architecture-doc`** — the produce half of the pair; it writes the architecture doc to the same 10-condition bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- **`reviewing-technical-design`** — the gate one altitude **down**, for one feature's technical-design (which locates itself within this architecture). Distinct doc, distinct bar.
- A **PRD-review** skill — the gate one layer **up**, for the product requirements (what/why, the NFR targets). Distinct doc, distinct bar.
- A **`design-review`** skill — the gate for *generic* engineering design docs, RFCs, **standalone ADRs**, specs, and plans (it verifies claims against the codebase). This skill is the dedicated reviewer for the doc-library **architecture-doc** artifact + its linked ADR files; `design-review` does not gate that artifact.
- An **api-spec / data-model**, where they exist — the contracts the architecture references structurally; cond-2 checks the doc stays at altitude (references, not enumerates) them.
- An **architecture-doc / ADR template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/architecture-quality-bar.md` — the ten checklist conditions expanded with per-condition pass/gap signals and worked finding examples (the boundary+concerns coverage check, the altitude test, the diagram-sync check, the ADR-mechanism signals [embedded-decision + rewritten-accepted-ADR + index-sync], the driver+alternative test, the realization-per-target + measurable-scenario signals, the cross-cutting/observability signals, the ASR-coverage check, the verify-against-reality + greenfield signals, and the delta-scoped-amend signals). Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method (C4/arc42/ISO 42010, ADR practice, SEI quality-attribute scenarios + ATAM, resilience patterns, living-architecture-documentation).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ~500 lines / 5,000 tokens (soft target — quality takes precedence; flag if consistently over 700 lines / 7,000 tokens) — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
