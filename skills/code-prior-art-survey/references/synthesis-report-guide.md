# Synthesis report — structure guide

Load when running Procedure 4 (synthesis). The report (`report.md`) is the project-level
living artifact: created by request 1, amended by delta runs. Author the eleven sections
**in this order**; each is grounded in the lenses (`synthesis-lenses.md`), not asserted.

1. **Survey scope.** What was surveyed and how: the capability areas covered, the angles
   run, the follow-up vocabulary wave (if any), and the keyword-map revision. Sets the
   boundary the reader judges every later claim against.
2. **Capability coverage** *(placed second — it is what a build planner reads first)*. The
   per-capability rollup (lens 7): `borrow` / `borrow-partial` / `original` per capability,
   with the search evidence behind every `original` (angles run, terms, recorded zeros,
   probe result) and the precise-claim phrasing. This traces back to the project's own
   approved scope (the capability map).
3. **Load-bearing abstractions.** The entity-convergence result (lens 1): the abstractions
   ≥70% of the corpus carries, with the repos that evidence each.
4. **Recommended architectural pattern.** The pattern-consensus result (lens 2): the
   ≥60%-adopted pattern the design takes unless overridden, with the override conditions.
5. **Trusted dependencies.** The dependency-consensus result (lens 3): the deps used by 5+
   high-quality repos, as purl ids, with the repos that de-risk each.
6. **Systemic failure modes.** The failure-aggregation result (lens 4): the multi-repo
   failure modes to design for upfront, each with the repos/issues that surface it.
7. **Borrow-vs-build matrix.** The per-subsystem matrix (lens 5). Deliberately distinct from
   §2: this is per SUBSYSTEM (how the system decomposes); §2 is per CAPABILITY (what the
   project committed to deliver). A capability can span subsystems.
8. **Gaps and open problems.** The gaps result (lens 6): what no repo handles well, each
   named as an innovation opportunity or a risk flag, with evidence.
9. **Top-5 seed repos.** The five highest-value repos to study first (by refined score +
   borrow verdict), each with a one-line why.
10. **Recommended ADRs.** The architecture decisions that follow from the borrow-vs-build
    matrix (§7) — each ADR must FOLLOW from the matrix, not float free of it.
11. **Amendments changelog** *(delta runs)*. One dated entry per delta run: which
    capabilities were net-new, which sections changed. Empty (or "request 1 — full run") on
    the first run.

## Delta amendments

A delta run reads the existing `report.md` + the `borrow-index.yaml` (which carries every
prior repo's verdict/score/tags, so the lenses re-tally across old+new repos without
re-reading old extract prose), amends only the affected sections, and appends a §11 dated
entry. Never silently rewrite an unaffected section.

## Grounding, not assertion

Every conclusion traces to extraction files — the numeric lens thresholds
(`synthesis-lenses.md`) make each spot-checkable. A section that states a conclusion the
lens tally does not support is a review failure (`reviewing-code-prior-art-survey`,
synthesis conditions). Precise language throughout: an evidenced finding, never an
overclaim.
