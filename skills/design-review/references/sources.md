# Sources — design-review

Research provenance for the review rubric. The core gap-categories (bootstrap &
ownership, naming honesty, scale & limits, hidden assumptions,
consistency-with-shipped-code, idempotency/failure, security surface) were
derived empirically from real design-doc review catches; the web research below
corroborated them and added two lenses (necessity & simpler alternatives;
completeness & clarity).

## Web research (accessed 2026-06-01; sanitized via external-content-sanitizer — clean)

- The Pragmatic Engineer — Engineering Planning with RFCs, Design Documents and ADRs — https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs
- The Pragmatic Engineer — Companies Using RFCs or Design Docs (examples) — https://blog.pragmaticengineer.com/rfcs-and-design-docs/
- Fuchsia — RFC best practices — https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/best_practices
- Mike Cvet (Better Programming) — Goals and Failure Modes for RFCs and Technical Design Documents — https://medium.com/better-programming/goals-and-failure-modes-for-rfcs-and-technical-design-documents-c4ee1d1da6ff
- Practica — The 7 Best Articles on Software Design Docs — https://practicahq.com/skill/software-design-docs

## What the research corroborated / added

- Reviewers assess: problem statement + *why build it at all*, goals/non-goals, success metrics, solution overview, alternatives, risks — and look for simpler approaches, design flaws, and edge cases. → corroborates the rubric; motivates the **necessity & simpler alternatives** and **completeness & clarity** lenses.
- Appropriate level of detail (too much detail obscures trade-offs); enough context for a first-time reader; distinguish firm commitments from illustrative examples; clear review outcome / sign-off. → folded into **completeness & clarity** and the verdict.

Minimum-corroboration note: the two added lenses appear across multiple reputable sources (Pragmatic Engineer, Fuchsia, Practica); the seven core categories are project-experience-derived and intentionally kept as the extensible core.
