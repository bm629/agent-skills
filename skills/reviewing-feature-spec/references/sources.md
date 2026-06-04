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
