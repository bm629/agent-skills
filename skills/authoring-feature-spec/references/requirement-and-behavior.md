# Reference — requirement expression & behavior

Depth for the skill body's behavior + acceptance method: the 29148 quality model, EARS patterns, the requirements-smell catalog, and the use-case flow discipline. Load when writing or sharpening a feature's behavior + acceptance criteria.

## ISO/IEC/IEEE 29148 — the quality model the bar instantiates

A well-formed requirement holds nine characteristics. The skill's conditions are an instance of them; use the vocabulary to diagnose *why* a requirement is weak.

| Attribute | Meaning | Skill condition it maps to |
|---|---|---|
| Necessary | needed; removing it leaves a gap | traces to a PRD need (an un-needed feature is an orphan) |
| Appropriate | right abstraction; **no implementation detail** | observable, implementation-free behavior |
| Unambiguous | one interpretation only | unambiguous + no-vague rule |
| Complete | states everything needed; no load-bearing TBD | complete I/O + states |
| Singular | one requirement, one idea | singular + consistent |
| Feasible | achievable within constraints | feasible + plannable |
| Verifiable | provable by test/inspection/demo | testable acceptance criteria |
| Correct | accurately states a real need | traces to the actual PRD line |
| Conforming | follows the standard/template pattern | the template tool's concern |

Don't add a "29148 section" — it's grounding, not a checklist row.

## EARS — the patterns

Constrain each behavior statement to a fixed clause order + keyword set. An EARS sentence maps ~1:1 to a Given/When/Then criterion (the `When/While/If` → Given+When, the `shall` → Then).

| Pattern | Template | Use for |
|---|---|---|
| Ubiquitous | `The <system> shall <response>.` | an always-active property |
| Event-driven | `When <trigger>, the <system> shall <response>.` | a response to a discrete event |
| State-driven | `While <state>, the <system> shall <response>.` | behavior active during a state |
| Optional-feature | `Where <feature included>, the <system> shall <response>.` | behavior only when a feature/config is present |
| Unwanted-behavior | `If <unwanted condition>, then the <system> shall <response>.` | error / guard behavior |
| Complex | `While <state>, when <trigger>, the <system> shall <response>.` | compound conditions |

A behavior that won't fit a pattern is usually two requirements (split) or is missing its trigger/condition. EARS is the *preferred* phrasing — the reviewer judges the outcome (unambiguous + clear trigger + response), never "is it literally EARS".

## Requirements-smell catalog

Scan each requirement + acceptance criterion; rewrite any **load-bearing** hit to a quantifiable/observable statement. (An incidental adjective in prose is not a finding.)

| Smell | Examples | Why it fails |
|---|---|---|
| Subjective language | user-friendly, easy, seamless, intuitive | semantics not objectively defined |
| Ambiguous adverbs/adjectives | almost, quickly, recently, normally | unspecified by nature |
| Non-verifiable / weak | sufficient, adequate, as far as possible, minimal, optimize | imprecise extent — not verifiable |
| Comparative w/o referent | faster, better, more secure | no baseline to measure against |
| Loophole | if possible, as appropriate, where feasible | lets the builder skip the requirement |
| Open-ended | etc., and so on, including but not limited to | the set is not enumerated → incomplete |

Ambiguity + verifiability are the most severe + frequent smells, so this is the highest-yield self-edit.

## Use-case flow discipline

The method for the behavior section:

- **Main success scenario** — a single path where the goal succeeds, ~**3–11 steps**, each step "actor does X → system responds (observable) Y". More than ~11 steps signals the feature is too big (split).
- **Alternate flows** — a *different* path where the actor's goal is **still met** (e.g. an equivalent route). Both are success; both belong.
- **Exception flows** — a path where the goal is **NOT met** (e.g. a precondition fails). Each names the failure + the system's handling. This alternate-vs-exception distinction is the load-bearing one.
- **Failure brainstorming** — at each main-scenario step ask "what can fail/vary here?"; include only the failures the system must detect + handle. This is the disciplined way to *generate* the edge-case set, not recall it.
- **Precision levels** — list the extension *conditions* (the set of branches) before the extension *handling steps*, so the branch set is complete before each is detailed.

## Worked micro-example (behavior → EARS → acceptance)

- Behavior (EARS event-driven): "When an invoice becomes 3 days past due and is unpaid, the system shall email the client the reminder template and log a `reminder_sent` event."
- Exception flow (EARS unwanted-behavior): "If the email provider returns 5xx, then the system shall retry 3× with exponential backoff and, on final failure, mark `reminder_failed` and surface it in the dashboard."
- Acceptance (G/W/T falls out of the EARS): "Given an unpaid invoice 3 days overdue, when the daily job runs, then exactly one reminder email is sent and a `reminder_sent` event is recorded."
