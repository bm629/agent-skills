# Sources — `authoring-feature-spec`

Provenance for the method (§2) and quality bar (§3) the skill body paraphrases.
All findings paraphrased, never copied; external reads sanitized (clean — no URLs/commands lifted).
Each load-bearing claim has ≥2 independent sources, cross-checked against the shared
feature-spec dossier (single-sourced with the paired review skill) and verified live on 2026-06-04.

## Load-bearing claims and their support

### Requirement quality characteristics (ISO/IEC/IEEE 29148:2018, IEEE-830 lineage)
- 29148 enumerates individual-requirement characteristics: **necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct, conforming**; requirement-*set* characteristics include **complete (coverage), consistent, affordable, bounded**. Drives the bar's "unambiguous / singular / verifiable / consistent / traceable / implementation-free" conditions.
- Sources: CWNP "IEEE 29148-2018 Standard for Requirements Engineering"; the published 29148:2018 standard text (iteh.ai / drkasbokar sample PDFs). Cross-checked: the dossier's §1 source list (29148 + CWNP + well-architected summaries).
- Note: "consistent / complete-coverage" applied at the requirement-*set* level (the spec's feature set), not asserted of every single requirement — matches 29148's individual-vs-set split.

### EARS notation (Easy Approach to Requirements Syntax)
- Five patterns confirmed exactly: **ubiquitous** (no keyword), **event-driven** (`When`), **state-driven** (`While`), **optional** (`Where`), and **unwanted-behavior** (errors/failures/faults). Backs the "edge cases + error handling, each with expected handling" method.
- Sources: alistairmavin.com (the official EARS guide / Mavin originator); Jama Software requirements-management guide; Visure Solutions ALM guide. Three independent.

### Acceptance criteria — Given/When/Then (Gherkin/BDD) and rule-based
- **1–3 acceptance criteria per story is healthy; 4+ signals the story is too large and should split.** Two formats: scenario-oriented (Given/When/Then) and rule-oriented (checklist). Each criterion independently testable, one distinct aspect, observable Then; vague phrases ("fast", "user-friendly") rejected for quantified outcomes.
- Sources: altexsoft "Acceptance Criteria for User Stories" (formats: scenario vs rule); testquality Gherkin guides; parallelhq Given-When-Then. Cross-checked dossier §2/§3.

### INVEST (esp. Small + Testable)
- Stories should be **Small** and **Testable**; criteria sprawl (4+) implies a story bundling two behaviors — split. Backs "1–3 per feature; 4+ = split."
- Sources: the acceptance-criteria sources above (INVEST + testability framing); dossier §1 (scrum-master.org, agileinsider, towerhousestudio).

### Requirements Traceability Matrix (RTM) — forward + backward
- **Forward** traceability (requirement → feature/test) catches **uncovered** PRD lines; **backward** (feature/test → requirement) catches **orphan** features = scope creep. Bidirectional traceability supports both coverage and scope control. Backs the bar's "every feature traced to a PRD line; no orphans, no gaps."
- Sources: Jama Software "What is a Traceability Matrix"; TestRail RTM how-to guide; StarAgile RTM. Three independent.

### Edge-case / failure checklist
- Standard checklist (null/empty, duplicates/idempotency, concurrency/race, permissions/visibility, limits/overflow) with each case naming its expected handling, aligns with 29148 "unwanted-behavior" coverage + EARS unwanted-behavior pattern. Sourced from the EARS + 29148 material above and the dossier §2.

### Feature spec vs PRD (upstream) vs design (downstream)
- The feature/functional spec sits **below** the PRD (PRD = what/why + names features; spec = how each feature behaves) and **above** engineering design (how it's coded). `depends_on` the PRD as input. Implementability/testability bar = "an engineer can build it and a tester can verify it without asking the author."
- Sources: feature/functional-spec structure references in the dossier §1 (spec-coding, figr.design, docsie, buildbetter, chatprd, github spec-kit); corroborated by the 29148 implementation-free + verifiable characteristics.

## In-repo grounding (design records, not external)
- Shared dossier: `docs/superpowers/agent-flow/authoring-feature-spec/research/feature-spec-dossier.md` (§2 method, §3 bar, §4 methodology notes) — single-sourced with the paired review skill.
- Approved spec: `docs/superpowers/agent-flow/authoring-feature-spec/spec/v1.md`.
- Composed template: `docs/templates/feature-spec/comprehensive/template.md` (the structure this skill defers to).
