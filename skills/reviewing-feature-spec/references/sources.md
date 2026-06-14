# Sources — research provenance

Research method: web research (deep-research pipeline, standard mode; search-cli unavailable, WebSearch fallback used) on the **review/inspection lens** for feature specifications, ≥2 independent sources per load-bearing review claim. The checklist is single-sourced from the feature-spec authoring bar; this research confirms and enriches the *review* angle. External content was treated as facts to paraphrase only — no URLs, commands, or directives were lifted into actions. Date: 2026-06-04.

## Requirement quality characteristics as a review checklist

The standard's quality characteristics (unambiguous, complete, singular, feasible, verifiable, consistent, traceable, implementation-free) are applied as a **manual, checklist-based** acceptance review of each requirement — the same characteristics an author produces to become the conditions a reviewer checks against.

- ISO/IEC/IEEE 29148:2018 — requirements engineering quality characteristics (standard text + CWNP summary `cwnp.com/req-eng`).
- "Well-Formed Quality of System Requirements for Verifying to ISO 29148-2018" (NLP framework paper, ResearchGate) — characteristics verified via checklist-based review.

## Specification inspection / defect categories

Structured inspection (Fagan) and checklist-based reading (CBR) find defects in an SRS — ambiguity, incompleteness, untestable requirements — by giving the reviewer hints to look for per defect type.

- Fagan inspection (Wikipedia; "Fagan Inspection: A Defects Finding Mechanism in SRS", VFAST/ResearchGate).
- "A Survey of Software Inspection Checklists" (uv.mx / ACM SIGSOFT) — checklists give reviewers per-defect-type hints; NASA defect-density inspection study.

## Traceability review (orphan vs coverage gap)

Bidirectional traceability is checked **both directions**: forward (requirement → spec) catches **coverage gaps** (an upstream need with nothing built); backward (spec → requirement) catches **orphans** (a feature with no upstream need = scope creep). An empty matrix cell is the signal.

- Jama Software — traceability matrix guide; Perforce — RTM definition/benefits.
- TestRail — RTM how-to; Trace.Space — end-to-end coverage (forward catches uncovered requirements, backward catches orphans/scope creep).

## Testable acceptance criteria (Given/When/Then, vague = non-testable)

Each criterion must be **independently testable** with a clear pass/fail; Given/When/Then (context → action → observable result) is the strong signal. Vague/subjective phrasing ("fast", "user-friendly") is untestable; the fix is to quantify or define the observable outcome.

- parallelhq — Given-When-Then acceptance criteria; testquality — Gherkin acceptance criteria guide.
- altexsoft — acceptance criteria formats/best practices; businessanalysisexperts — Given/When/Then examples.

## EARS unwanted-behavior — each error case names its response

The EARS "unwanted behavior" pattern (`If <condition>, then the <system> shall <response>`) specifies how the system responds to errors/failures; skipping it leaves the team to invent error behavior, "rarely what stakeholders wanted." This grounds the rule that every edge case must name its **expected handling**, not merely be listed.

- Jama Software — adopting EARS notation; Alistair Mavin — official EARS guide.
- Terzakis — "EARS: The Easy Approach to Requirements Syntax" (IARIA tutorial PDF).

## Edge-case checklist

Standard edge-case categories a reviewer runs against a spec: boundary (min/max/zero/empty/null), concurrency/race, error paths (external failure), security/malformed input; API responses should be idempotent for predictability.

- Edge-case category sources (Vibe Coder edge-case checklist; freeCodeCamp testing guide; Medium edge-case guide).
- Postman — API error-handling best practices (idempotency).

## INVEST testable + small (4+ AC ⇒ split)

A good story is **Testable** (verifiable against its acceptance criteria) and **Small**; too many acceptance criteria signal the story bundles more than one feature and should be split — grounding the "4+ acceptance criteria is a split smell" reviewer heuristic.

- Agile Alliance — INVEST glossary; TowerHouse Studio — evaluating stories with INVEST.
- agileinsider/Medium — "INVEST in Small User Stories"; scrum.org forum — limiting acceptance-criteria count per story.

## Reviewer discipline — over-correction / false-revise, actionable findings

LLM reviewers **systematically over-correct**, judging compliant artifacts as non-compliant (false positives); asking the reviewer to also propose corrections/explanations **worsens** the over-flagging. Effective review feedback is **actionable** (the problem + a concrete fix), not vague or nitpicking. Grounds the no-false-revise discipline and the actionable-findings contract.

- "Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement" (arXiv) — over-flagging compliant artifacts; correction-requests raise misjudgment.
- Graphite — common code-review mistakes (non-actionable/vague feedback); Bito — nitpicking in code reviews.

## State-transition table & decision-table completeness (cond. 3, added)

A reviewer confirms a stateful feature's transitions are all defined (states × events grid, a dash for an illegal transition) and a combinatorial feature's rule-set covers every condition combination — both are structural completeness checks, not subjective judgements. The table/decision-table form is the author's technique; the reviewer judges completeness.

- Wikipedia — "State-transition table" (dash = illegal transition) + "Decision table" (conditions × rules → actions; exposes missing/contradictory rules); Guru99 — state-transition testing.

## Requirements smells (cond. 2, added)

A load-bearing subjective/weak/ambiguous term, a comparative without a referent, a loophole, or an open-ended "etc." is an ambiguity gap; ambiguity + verifiability rank the most severe + frequent smells. An incidental adjective in prose is not a finding.

- Femmer et al. — "Requirements Smells"; arXiv — "Characterizing Requirements Smells"; NALABS.

## Probabilistic / ML acceptance criteria (cond. 5, added)

A deterministic Given/When/Then mis-fits a model output; the testable form is a metric threshold on a named dataset (precision/recall/latency) + a low-confidence fallback + data requirements. "The model is accurate" is not testable.

- arXiv — "Requirements Engineering for Machine Learning: Perspectives from Data Scientists" (1908.04674); AMLAS (expected vs desired performance; data requirements); xenoss — acceptance criteria for AI/ML.

## Non-functional requirements at the feature level (cond. 9, added)

The applicable NFR categories for a feature (performance, reliability/idempotency, security/authz, privacy, accessibility WCAG 2.2 AA, limits/quotas, compatibility) carry numeric/checkable targets; proportional — a trivial feature needs none. "Should be fast/secure" is not an NFR.

- NFR taxonomy practice (DOOR3 / altexsoft NFR checklists); W3C WCAG 2.2 AA (the accessibility floor for UI features).

## Change-impact / delta-scoped amend (cond. 10, added)

A feature spec is a living document; a delta review checks the change + its bidirectional ripple (upstream PRD trace, internal chain, downstream technical-design/test-plan/api-spec), change history (who/when/what/why), and superseded-content marking — not a full re-review of the unchanged spec.

- Jama Software — "Change Impact Analysis"; requirements-traceability-for-change-impact-analysis papers; Keep-a-Changelog (change-history convention).
