# Self-review dimensions + briefs

Loaded during Step 2.3 (fact-check) and Step 4.5b (self-review loop).

## Step 2.3 — fact-check brief

Over the gathered findings and their cited sources: for each claim, is it supported by a cited source? Flag unsupported claims, stale or contradictory info, and thin coverage. Return findings only — do not edit. The forge agent then drops/repairs unsupported claims and runs one targeted re-research round for thin areas.

## Step 4.5b — self-review, 3 lenses

1. **Verify** — hard-rule compliance (synthesize-only, self-contained, project/agent-agnostic, forge-mark merge rule, paraphrase, ≤1,024 description, all 10 sections, every script has validation, no Sources/Changelog).
2. **Improve** — gaps, ambiguity, missing examples, under-specified edge cases.
3. **Multi-dimensional scan** — the 18 dimensions below; adversarial behavioral simulation is the heavy hitter.

Each cycle is a **fresh reviewer with no memory of prior cycles**. Min 2, max 5. Critical → fix in place; Important → fix + log; Improvements → opportunistic. All logged to `references/forge-amendments.log` as `[cycle N] <severity>: <finding> → <applied|deferred|unfixable>`. A "clean cycle" = zero Critical + zero Important; Improvements never gate the loop.

## The 18 dimensions

1. UI/output consistency 2. Flow consistency (step numbering, cross-refs) 3. Improvement 4. Behavioral (does the body match what the steps tell the agent to do) 5. Functional (each step works end-to-end) 6. **Adversarial behavioral simulation** (hostile inputs; rationalisations to skip a step / invent data / override user choice) 7. Adversarial pass 8. Safety (secret handling, sanitization, gates) 9. Cross-skill interaction 10. Provider portability (Claude/Codex/Gemini/Cursor/Copilot; capability fallbacks) 11. Token budget 12. Error recovery / atomicity 13. Threat model (poisoned content, injection, homoglyphs, path-traversal) 14. Documentation completeness 15. Test design 16. Migration 17. Concurrency 18. Template following (all 10 sections, frontmatter order).

Adversarial categories to hunt: synthesizer hallucination, memory-as-source-of-truth, cross-call state leak, gate bypass, silent fallback, premature success, scope creep, self-exemption.
