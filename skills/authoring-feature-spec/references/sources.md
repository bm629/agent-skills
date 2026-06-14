# Sources — `authoring-feature-spec`

Portable provenance for the method + quality bar the skill body paraphrases. All findings paraphrased, never copied; external reads sanitized (no URLs/commands lifted). Each load-bearing claim has ≥2 independent sources; single-sourced with the paired `reviewing-feature-spec` so author and reviewer share one bar. Distilled 2026-06-14 for the production-grade redesign (v1.2.0).

## Requirement quality (ISO/IEC/IEEE 29148:2018)

- The nine individual-requirement characteristics — **necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct, conforming** — and the set characteristics (complete-coverage, consistent, bounded). The bar instantiates these (cond unambiguous / singular / verifiable / feasible / traceable / implementation-free). Sources: IEEE SA 29148-2018 standard page; CWNP 29148 overview; ReqView 29148 templates.

## EARS (Easy Approach to Requirements Syntax)

- Patterns: **ubiquitous**, **event-driven** (`When`), **state-driven** (`While`), **optional-feature** (`Where`), **unwanted-behavior** (`If…then`), and **complex** (combinations). Constrains free NL to a fixed clause order; maps ~1:1 to Given/When/Then. Sources: Mavin et al. RE'09 / IARIA tutorial; alistairmavin.com official guide; Jama "Adopting EARS"; QRA EARS guide; AWS Kiro (auto-generates EARS-format requirements).

## Use-case flows (Cockburn)

- A 3–11-step main success scenario; **alternate** flows (goal met) vs **exception** flows (goal NOT met); per-step failure brainstorming; precision levels (extension conditions before extension handling). Sources: Cockburn "Writing Effective Use Cases"; Jacobson/Cockburn "Use-Case Foundation"; ModernAnalyst (alternate-vs-exception); BA Times use-case flows.

## Requirements smells

- The catalog: subjective language, ambiguous adverbs/adjectives, non-verifiable/weak terms, comparatives without a referent, loopholes, open-ended lists; ambiguity + verifiability rank most severe + frequent. Sources: Femmer et al. "Requirements Smells"; arXiv "Characterizing Requirements Smells"; NALABS.

## Inputs/outputs & data contract

- I/O as an enforceable contract (schema, required/optional fields, types, validation). Sources: Open Data Contract Standard (ODCS v3) / datacontract.com; OpenAPI request/response schema; Nordic APIs (schema validation vs contract testing).

## State-transition table & decision table

- State-transition table (states × events, dash = illegal transition; initial/terminal named) for stateful features; decision table (conditions × rules → actions) as the completeness device for combinatorial rules. Sources: Wikipedia "State-transition table" + "Decision table"; Guru99 "State Transition Testing".

## Edge cases / boundary-value analysis

- Boundary-value analysis (just below/at/just above each limit; off-by-one) + the standard checklist (null/empty, duplicate/idempotency, concurrency/race, permissions/visibility, limits/overflow); each carries its handling. Sources: GeeksforGeeks BVA; Katalon BVA; freeCodeCamp edge-case testing.

## Acceptance criteria (Given/When/Then, INVEST, probabilistic)

- Given/When/Then (Gherkin) or rule-based; **1–3 per feature, 4+ = split** (INVEST Small+Testable). For probabilistic/ML features, metric-threshold criteria on a named dataset (precision/recall/latency) + low-confidence fallback + data requirements — a deterministic "works"/"accurate" is not a criterion. Sources: Altexsoft, TestQuality, Ranorex, TestRail (G/W/T); Bill Wake INVEST (2003); arXiv "RE for Machine Learning" (1908.04674); AMLAS (data requirements; expected vs desired performance); xenoss (probabilistic acceptance criteria).

## Feature-level non-functional requirements

- The applicable category set (performance, reliability/idempotency, security/authorization, privacy/data-handling, accessibility WCAG 2.2 AA, limits/quotas, compatibility) each with a numeric/checkable target; proportional. Sources: NFR taxonomy practice; W3C WCAG 2.2 AA.

## Traceability (RTM, bidirectional)

- Forward (requirement → feature/test) catches uncovered PRD lines; backward (feature → requirement) catches orphans/scope-creep. Sources: Guru99; TestRail; Perforce; GeeksforGeeks (forward/backward/bidirectional RTM).

## Iteration / amend (living document, change-impact)

- Edit-in-place; version + changelog (who/when/what/why); mark superseded; bidirectional ripple (upstream PRD / internal chain / downstream technical-design+test-plan+api-spec). Sources: Jama "Change Impact Analysis"; requirements-traceability-for-change-impact-analysis papers; Keep-a-Changelog; spec-driven-development change control.

## Feature spec vs PRD (upstream) vs technical-design (downstream)

- Below the PRD (what/why; names features) and above the technical-design (how it's coded; mechanism, schemas, table names). `depends_on` the PRD; implementability/testability bar = "an engineer can build it and a tester can verify it without asking the author." Sources: GeeksforGeeks functional-vs-technical specs; O'Connor (DCU) functional-spec notes; GitHub Spec Kit / AWS Kiro phase split (Requirements → Design → Tasks).
