# authoring-release-runbook

Author a **release/deployment runbook** — the go-to-production operational procedure a deploying or on-call engineer follows to ship a system to production safely and verifiably: prerequisites and sign-offs, pre-deploy checks, the deploy procedure, post-deploy verification, the rollback procedure, and on-call/escalation plus monitoring pointers. The how-to (an SRE/operational method + an executability/safety bar), composed with a separate release-runbook template tool and a deep-research capability; targets a textual markdown artifact (numbered copy-paste-safe steps + fenced command/check snippets + verification tables + linked monitors).

## Purpose

A release runbook is the procedure that turns a built, tested system into a running production release without the deployer having to re-derive it under pressure. This skill carries the producer's judgment — not the section list — guiding a producer to ground the runbook in established SRE/operational practice, derive the deploy steps from the architecture-doc's deployable components plus the technical-design's rollout, derive the verification from the test-plan's exit criteria, write idempotent copy-paste-safe steps each with an expected result, default the deploy strategy to blue-green (overridable to the strategy the project warrants — rolling, canary, recreate), and give every forward change a documented revert with rollback triggers. The bar to clear: an engineer unfamiliar with the system can deploy, confirm success, and roll back safely from the runbook alone, with no secret inlined and nothing fabricated.

## When to activate

- Authoring a production release/deployment runbook from the handed-in upstreams (typically architecture-doc + technical-design + test-plan).
- Specifying the deploy procedure, pre/post checks, rollback, and escalation/monitoring of a go-to-production release.
- Filling a release-runbook template with researched, executable, decision-complete per-step content.

### When NOT to activate

- **The CI/CD pipeline configuration / automation** (a cicd-plan and its YAML) -> a separate delivery concern; the runbook documents the manual + verification + rollback procedure around the pipeline, not the automation.
- **The QA/verification strategy + test cases** -> `authoring-test-plan` (the runbook reuses its exit criteria for verification).
- **An incident response / post-mortem** -> the runbook is the pre-planned procedure, not the after-the-fact retrospective.
- **The architecture / engineering design it references** -> `authoring-architecture-doc` / `authoring-technical-design`.
- **Reviewing a finished runbook** -> `reviewing-release-runbook`.

## Workflow

Take the section structure from the release-runbook template tool (don't invent an outline). Read the full handed-in `depends_on` set; derive the deploy steps from the architecture-doc's components and the technical-design's rollout, and the post-deploy verification from the test-plan's exit criteria. Research to ground the runbook in established operational practice (idempotent copy-paste-safe steps, an explicit verification gate per step, rollback triggers and a documented revert for every forward change, secrets-by-reference). Choose the deploy strategy — blue-green by default, overridden when the upstream design implies rolling/canary/recreate. Then fill each section to method: prerequisites and sign-offs; pre-deploy checks with a go/no-go gate; the ordered deploy procedure with an expected result per step; post-deploy verification/smoke reusing the test-plan exit criteria; a complete, reverse-ordered rollback with trigger conditions and re-verification; concrete on-call/escalation and monitoring pointers. Reference secrets by their store, never inline a token. Surface any missing upstream (e.g. an absent monitoring pointer) as an explicit assumption rather than fabricate. Self-check against the executability/safety bar before handoff.

## Output

A comprehensive release runbook meeting the **executability/safety bar** (executable by an unfamiliar engineer; every step has an expected result/verification; a go/no-go gate; a complete and safe rollback with a revert for every forward change and measurable triggers; concrete escalation + monitoring pointers; no secret inlined; nothing fabricated — commands/hosts trace to an upstream or are flagged as assumptions). Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same bar a runtime `reviewing-release-runbook` gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **Executable + idempotent** — copy-paste-safe steps, each with an expected result; no ambiguous prose.
- **Complete + safe rollback** — a documented revert for every forward change, with trigger conditions and re-verification.
- **Strategy-aware** — blue-green default, overridable to the strategy the project warrants.
- **Secrets by reference, never fabricated** — references the secret store; surfaces gaps as assumptions; never inlines a token or invents a host/command.
- **Single-sourced bar** — shared with `reviewing-release-runbook` via the pair dossier, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
