# Synthesis lenses — the five corpus cuts

Load when running Procedure 4 (synthesis). The extract set (`extract/*.md`) is the corpus; each
lens is a cut ACROSS it, not a walk through it one record at a time. A report that reads as a
list of records has not been synthesized — it has been concatenated.

Every lens output is copied into the register or the report from a record that says it. A claim
that no record supports is the failure these lenses exist to prevent.

## The five lenses

1. **Convergence.** Which conventions more than one corpus states independently. Two corpora
   agreeing is the strongest signal this survey produces, and it is invisible per record — only
   the cut across them shows it. Name the corpora, never just the count.
2. **Conflict.** Where corpora disagree, and which is normative. A W3C recommendation and a
   vendor guideline can prescribe different things for the same component; the register keeps
   both with their `authority`, and the report is where the disagreement is stated plainly. Never
   resolve a conflict by dropping the weaker source — that is a silent editorial decision the
   downstream skill cannot see.
3. **Applicability.** Which conventions bind THIS project, by `applicability.applies` and its
   basis. A convention that does not apply stays in the register with its basis; the report says
   why the surface it governs is absent, so a later reader can tell "not applicable here" from
   "never looked at".
4. **Token availability.** Which surveyed systems publish a usable DTCG token set and which do
   not. This is the type's handoff value: the downstream skill authors THIS project's system from
   the evidence, so it needs to know which sources hand it tokens and which hand it prose.
5. **Absence.** What the survey did NOT find, and whether that is a finding or a limit. An angle
   that vacated for want of a source produced no evidence about the world; an angle that ran and
   found nothing did. The coverage receipt carries the distinction into the register; the report
   states it in words.

## Phrasing an absence claim

Say what was searched and what was not, precisely: "no governed design system was found across
the two corpora a1 covers, at their 2026-04 releases" — not "there are no design systems for
this". The first is a survey result; the second is a claim about the world the survey cannot
support.

## Grounding, not assertion

Every report sentence that makes a claim carries the convention id or corpus it rests on. The
reviewing twin checks this, and it is the difference between a survey and an opinion.
