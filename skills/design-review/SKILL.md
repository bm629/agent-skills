---
name: design-review
description: >
  Use when about to approve a design document — a spec, plan, design doc, RFC, or
  ADR — and you want an adversarial pre-approval review that surfaces gaps before
  sign-off. Hunts a rubric of recurring gap categories (bootstrap & ownership,
  naming honesty, scale, hidden assumptions, consistency-with-shipped-code,
  idempotency/failure, security, necessity, completeness) and, when the document
  is a plan, a plan lens (task granularity, dependency-DAG, coverage-vs-spec,
  exit-criteria testability). Verifies every claim about existing behavior against
  the actual codebase (citing file:line, never fabricating); returns findings
  (category, location, severity, gap, fix, evidence) plus a ready-for-approval /
  has-blockers verdict. Review-only: never edits the document and never approves —
  the human decides, the author fixes. Keywords: design review, spec review, plan
  review, RFC review, ADR, gap analysis, pre-approval check.
extensions:
  claude:
    when_to_use: "Reviewing a spec/plan/design doc/RFC/ADR before approving it"
    allowed-tools: [Read, Grep, Glob, Write]   # Write only for the opt-in review.md (never edits the doc under review)
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "2.0.0"
forge:
  status: reviewed
  forged: 2026-06-01
  reviewed: 2026-06-01
---

## Overview

`design-review` performs an **adversarial pre-approval review** of a design
document — a spec, design doc, RFC, ADR, or implementation plan. It hunts for the
recurring gaps that otherwise surface late (or in production): missing
bootstrap/ownership, misleading names, unconsidered scale, unstated assumptions,
claims that don't match the code, missing failure handling, unexamined security
surface, unjustified complexity, and incompleteness. Critically, it **verifies
claims against the actual codebase** rather than trusting the prose, and it cites
`file:line` evidence so every finding is grounded. It produces a findings report
and a verdict; it **never edits the document and never approves** — that stays
with the human reviewer and the author. Use it as the gate between writing a
design and signing off on it.

## When to activate

- ✅ A spec / design doc / RFC / ADR / implementation plan is about to be approved and you want gaps found first.
- ✅ A document author wants a critical pass before presenting their design for sign-off.
- ✅ An automated workflow needs a consistent pre-approval review step over design documents.

**Do NOT activate when:**

- The artifact is **code / a diff** — use a code-review skill (`requesting-code-review` / `code-review`); this skill reviews *design documents*, not implementations.
- You are **authoring** the document — use a content/template skill to draft it; `design-review` only reviews an existing draft.
- The text is a one-line note or non-structured prose with no design to evaluate.

## Workflow

### Step 1: Receive inputs

- **Required:** a path to the document to review.
- **Optional:** explicit codebase pointers (dirs/modules the design touches). If omitted, **infer** the modules to verify from the document's own references (file paths, command/module names, links it cites).
- **Optional:** an output preference — inline (default) or write a `review.md` beside the document.

### Step 2: Read the document fully

Read the whole document before judging any part. Note its claims about existing behavior, its named commands/files/verbs, its inputs, its scale assumptions, and any code paths it references — these feed Steps 3–4.

### Step 3: Gap-hunt by category

Walk the document against this rubric. The list is **extensible** — add categories as new gap types surface; never drop the core ones.

| Category | The question to ask |
|---|---|
| **Bootstrap & ownership** | For every input the design consumes, *who/what creates it, and in what order?* Is the setup sequence stated? |
| **Naming honesty** | Does each command / file / verb / field do what its name implies, in the order implied? Any misleading name? |
| **Scale & limits** | What happens at 10× / 1000×? Per-item vs whole-collection operations; concurrency; unbounded growth. |
| **Hidden assumptions** | Singular vs plural, one vs many, defaults, "obviously" — are they stated explicitly rather than assumed? |
| **Consistency with shipped code** | Do claims about existing behavior, paths, or interfaces match how the code *actually* behaves? (verified in Step 4) |
| **Idempotency / failure / re-run** | What on re-run, partial failure, crash, retry? Is the operation safe to repeat? |
| **Security surface** | New authz/authn, secrets handling, external calls, destructive actions, untrusted input? |
| **Necessity & simpler alternatives** | Does this need to be built at all? Is there a materially simpler approach the design skipped? |
| **Completeness & clarity** | Are problem/goals/non-goals/alternatives/risks present? Would a first-time reader understand it? Is detail at the right altitude? |

**Plan lens — when the document under review is an implementation/project plan, additionally check** (the 9 categories above still apply):

| Plan check | The question to ask |
|---|---|
| **Task granularity** | Is each leaf task a single concern with **one testable exit check**, and atomic? Flag tasks that bundle concerns (an "and") or lack a stated exit check. |
| **Dependency ordering / DAG** | Do `depends_on` / blocking edges form a valid DAG (no cycles), and does the execution order respect them? |
| **Coverage vs the companion spec** | Does every spec scope item map to ≥1 task, with no task implementing out-of-scope work? |
| **Exit-criteria testability** | Is each phase/task "done" a single testable statement (a command/observation), not subjective? |

### Step 4: Verify claims against the code (mandatory)

For any finding that asserts something about **existing** behavior, paths, or interfaces, **read/grep the referenced module and confirm it** — then cite `file:line`. This is the difference between a grounded review and a guess.

- A finding asserting an inconsistency **must quote/point at the real code** (`path:line`).
- A gap you suspect but cannot confirm is marked **`unverified`** explicitly — never asserted as fact (this enforces "no fabrication").
- **Greenfield:** if the document describes brand-new behavior with no existing code to check, the *consistency* category is **N/A** — absence of code to verify is **never itself a blocker**.
- **Bound the work:** verify only the modules the document references; do not scan the whole tree.

### Step 5: Assemble findings

Each finding:

```
- [severity] <category> — <location in the doc>
  Gap: <what is missing/wrong/unstated>
  Fix: <concrete suggested resolution>
  Evidence: <path:line> | unverified
```

**Severity:** `blocker` (must resolve before approval — wrong/missing in a way that breaks the design or its premises) · `important` (should resolve — real gap, not fatal) · `minor` (nice to fix).

### Step 6: Verdict

End with one line: **`ready-for-approval`** (no blockers) or **`has-blockers`** (list the blockers first, then important, then minor). The verdict is a recommendation to the human — not an approval.

### Step 7 (optional): Independent pass for large / high-risk docs

For a large or high-stakes document, dispatch a **fresh reviewer with no prior context** (a subagent) given the same rubric, then merge its findings (de-duplicated). If subagent dispatch is unavailable, **fall back** to a second inline pass and say so. This mirrors the value of a fresh set of eyes; it is optional, not required.

### Step 8: Output

- **Inline by default:** return the findings + verdict to the caller.
- **Opt-in:** if requested, write a `review.md` beside the document.
- **Never edit the document. Never approve.** Recommend; the author applies, the human decides.

## Rules

**Hard rules (never violate):**

- **Verify before asserting (no fabrication).** Any claim about existing behavior is confirmed against the code with a `file:line` citation, or it is labelled `unverified`. Never invent a gap.
- **Review-only.** Never edit the document; never approve or reject it. Output is findings + a verdict recommendation; the human owns the decision and the author owns the fix.
- **Greenfield is not a gap.** Absence of code to verify against is never, by itself, a blocker.
- **Bound verification** to the modules the document references — do not scan the whole repository.
- **Severity honesty.** Reserve `blocker` for things that genuinely must be fixed before approval; do not inflate.

**Preferences (override-able):**

- The category rubric is extensible — add categories as new recurring gap types emerge.
- Surface blockers first; keep the report scannable; collapse minors if numerous.
- Prefer one concrete suggested fix per finding over open-ended commentary.

## Gotchas

- **Trusting the prose.** A spec can confidently describe behavior the code doesn't have. The whole value is Step 4 — verify against the code; a review that skips it is just opinion.
- **Greenfield mis-flagged.** On a brand-new-system doc there is nothing to verify against; flagging "couldn't verify X" as a problem is wrong — mark consistency N/A.
- **Whole-tree scan.** Trying to verify against the entire codebase is slow and noisy; bound it to referenced modules.
- **Over-flagging.** Listing every nitpick as a blocker buries the real ones. Severity discipline keeps the verdict meaningful.
- **Detail mistaken for completeness.** Lots of detail is not the same as a complete design; conversely, terse-but-complete is fine. Judge whether the *decisions* are present, not the word count.

## Anti-patterns

- **"It probably doesn't match the code" without checking.** Fabricated or unverified gaps stated as fact — forbidden; verify or mark `unverified`.
- **"I'll just fix the doc while I'm here."** Editing the document is out of scope; review-only.
- **"Looks good to me."** Rubber-stamping — skimming and approving without running the rubric or verifying claims.
- **"Let me approve it."** Deciding the outcome; the skill recommends, the human approves.
- **"Let me grep the entire repo to be safe."** Unbounded verification; stay within referenced modules.

## Output

A **findings report** (inline by default; optional `review.md`): zero or more findings in the Step-5 shape, ordered by severity, followed by a one-line `ready-for-approval` | `has-blockers` verdict. The artifact is a **recommendation consumed by the document's author and the human approver** at the approval gate — never an approval, never an edited document.

## Related

- `requesting-code-review` / `code-review` — the analogous capability for **code/diffs**; `design-review` is the design-document counterpart that runs *before* code exists.
- A content/template skill — authors the document that this skill reviews (authoring vs reviewing are distinct).
- Fits the spec → plan → implement discipline as the pre-approval gate over the spec (and plan).

## Progressive disclosure

- `references/sources.md` — research provenance for the rubric. Load only if auditing where the categories came from.

This skill ships no `scripts/` or `assets/`; it runs via `Read` / `Grep` / `Glob` and (optionally) a subagent dispatch.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens.
