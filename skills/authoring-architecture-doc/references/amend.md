# amend — amending an approved architecture doc (the delta path)

Load when handed an approved architecture doc + a change request. The architecture doc is a living document — it evolves by delta, not rewrite. Two things make the architecture-doc amend distinctive: (1) the **ADR supersede convention IS the amend mechanism** (immutable accepted records), and (2) the ripple is **downward-broad** — to the fleet of per-feature technical-design docs.

## Scope unit
One amendment touches a single: architecturally-significant **decision** (→ a new superseding ADR) / a component responsibility or topology edge / an integration boundary + contract / an NFR target's realizing mechanism / a cross-cutting stance (resilience/security/observability).

## Method

1. **Scope the change** to the affected element; edit in place, preserving stable section/decision IDs + review history. Do NOT regenerate the whole doc.
2. **Change decisions via supersede — never edit an accepted ADR.** Write a NEW ADR that supersedes the old one (old Status → "superseded by NNNN" + reciprocal "supersedes NNNN" note). Rewriting an accepted ADR is the cardinal amend defect — it destroys the decision history.
3. **Keep the decisions index in sync.** After a supersede, the index reflects the new ADR + the superseded status; no dangling/duplicate index rows.
4. **Re-make the internal chain.** Re-check: does the topology still hold; do the diagrams still agree with the prose; do the NFR realizations still meet the targets; are the affected boundaries' failure semantics still stated?
5. **Bump the doc's own version + changelog** (who / when / what / why — the produced doc's Version, distinct from the skill's semver).
6. **Analyze the ripple:**
   - **Upstream:** a requirement-driven change means the PRD/product-direction is amended FIRST (the spec→plan→impl order). A structure with no driver after the change is newly-orphaned.
   - **Internal:** the re-made chain above.
   - **Downstream-broad (the distinctive one):** the fleet of per-feature **technical-design docs** that located themselves within the changed structure (each may need its own amend), plus the **api-spec / data-model / deployment / release-runbook** the change touches. Flag each — never silently leave them stale.

## What the reviewer checks on a delta
`reviewing-architecture-doc` runs a delta-scoped review (not a full re-review): the in-scope decisions meet the bar, the supersede convention was followed (no accepted ADR rewritten), the index is in sync, the version + changelog are present, and the downward ripple (esp. the dependent TDD fleet) is flagged.
