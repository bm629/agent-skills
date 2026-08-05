# Synthesis report — structure guide

Load when running Procedure 4 (synthesis). The report (`report.md`) is the project-level human
half of the survey; `convention-register.yaml` is its machine half and the build-handoff index.
The survey ships both, and neither substitutes for the other: the register is what a downstream
skill reads, the report is what a person reads before trusting it.

## The seven sections are FIXED

The coordinator's synthesis brief demands exactly these, in this order, so guide and brief cannot
drift.

1. **Survey scope.** What was surveyed and how: the angles that ran, the corpora reached at which
   versions, and the date. A reader who cannot tell what was covered cannot use anything below.
2. **Coverage and absence** *(second on purpose — it is what a reader checks before trusting the
   rest)*. Per angle: ran, vacated, or not run, each non-`ran` outcome with its cause. State
   plainly which surfaces the survey says nothing about.
3. **Conventions that bind.** The applicable conventions (lens 3), grouped by what they govern,
   each carrying its canonical id, corpus and version, and authority band.
4. **Where corpora agree.** The convergence result (lens 1), naming the corpora that agree
   independently — the strongest signal this survey produces.
5. **Where corpora conflict.** The conflict result (lens 2): the disagreement, both positions,
   and which is normative. Never resolved by dropping a source.
6. **Token availability.** The token result (lens 4): which surveyed systems publish a usable
   DTCG 2025.10 token set, carried per system in the register, and which publish prose only.
7. **Amendments changelog** *(delta runs)*. One dated entry per delta run: what changed, what was
   added, and what a prior run claimed that this one corrects.

## What does not go in the report

No recommendation about what THIS project should build. The survey reports what the corpora say
and whether it binds; choosing the project's own conventions is the downstream design skill's
job, working from the register. A report that picks the project's design system has quietly
replaced the decision it was supposed to inform.

## Grounding

Every claim carries the convention id or corpus it rests on. An unattributed sentence in a
survey report is an opinion wearing a citation's clothes, and the reviewing twin treats it as a
finding.
