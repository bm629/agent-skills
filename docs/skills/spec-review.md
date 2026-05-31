# spec-review

Adversarial **pre-approval review of a design document** — a spec, design doc,
RFC, ADR, or implementation plan. It hunts recurring gap categories, **verifies
claims against the actual codebase** (citing `file:line`, never fabricating), and
returns findings plus a verdict. Review-only: it never edits the document and
never approves.

## Purpose

The gate between *writing* a design and *signing off* on it. A spec can
confidently describe behavior the code doesn't have, name a command that does the
wrong thing, or quietly assume "one" where reality is "many" — and those gaps
surface late (or in production). `spec-review` makes that pass systematic: a fixed
rubric of gap categories, evidence-grounded verification against the real code,
and a clear `ready-for-approval` / `has-blockers` verdict the human acts on.

## When to activate

- ✅ A spec / design doc / RFC / ADR / implementation plan is about to be approved and you want gaps found first.
- ✅ A document author wants a critical pass before presenting their design for sign-off.
- ✅ An automated workflow needs a consistent pre-approval review step over design documents.

### When NOT to activate

- The artifact is **code / a diff** → use a code-review skill; this reviews *design documents*.
- You are **authoring** the document → use a content/template skill; this only reviews an existing draft.
- A one-line note with no design to evaluate.

## Workflow

1. **Inputs** — a doc path (required) + optional codebase pointers; by default *infer* the modules to verify from the document's own references.
2. **Read** the document fully before judging any part.
3. **Gap-hunt** by the rubric (below).
4. **Verify against code (mandatory)** — for any claim about existing behavior, read/grep the referenced module and cite `file:line`; a suspected-but-unconfirmed gap is marked `unverified`; greenfield (no code yet) → the consistency category is N/A; verification is bounded to referenced modules.
5. **Assemble findings** — each: `{category, location, severity (blocker | important | minor), gap, fix, evidence (file:line | unverified)}`.
6. **Verdict** — `ready-for-approval` or `has-blockers` (blockers listed first).
7. **Optional** — for large/high-risk docs, dispatch a fresh no-memory reviewer with the same rubric and merge findings (graceful inline fallback if unavailable).
8. **Output** — inline by default; an opt-in `review.md` beside the doc. Never edits the document; never approves.

## Rubric — gap categories

`bootstrap & ownership` · `naming honesty` · `scale & limits` · `hidden
assumptions` · `consistency with shipped code` · `idempotency / failure / re-run`
· `security surface` · `necessity & simpler alternatives` · `completeness &
clarity`. The list is extensible; the core categories are never dropped.

## Key guarantees

- **No fabrication.** Every claim about existing behavior is confirmed against the code with a `file:line` citation, or explicitly labelled `unverified`.
- **Review-only.** Never edits the document; never approves or rejects. Findings are a recommendation; the human decides, the author fixes.
- **Greenfield is not a gap;** verification is bounded to referenced modules; `blocker` is reserved for things that genuinely must be fixed before approval.

## Limitations

- One layer of defense, not a substitute for human judgment — it surfaces gaps, it doesn't guarantee a complete design.
- Doc-type-agnostic but tuned for engineering specs/plans; lighter value on non-technical prose.
- Verification quality is bounded by what the referenced code actually exposes.

## License

MIT © 2026 Bhushan Modi.
