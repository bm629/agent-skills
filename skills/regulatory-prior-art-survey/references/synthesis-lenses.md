# The synthesis lenses

Run the lenses across the **requirements**, not across the files. Two requirements from one
instrument are one instrument agreeing with itself; group by the `#` prefix to tell.

**Throughout: `requirement` means a LEGAL OBLIGATION, never a product requirement.**

| lens | formula |
| --- | --- |
| **1 · Applicability** | Group by `instrument_id`. State the scope condition that made each apply, its evidence, and its `binding_force`. **An instrument applying IN PART says which part** — and the gate refuses one that does not. |
| **2 · Convergence merge** | Group on `dimension` FIRST, then on `control_ids` where BOTH rows carry them. Control ids are optional and only one angle mints them, so requiring an intersection would mean a law-only survey — the common case here — could never merge anything and the mandates block would be empty. Within a group, resolve to the strictest stated standard **within one ordered dimension in one unit**, and **cite every obligation merged**. |
| **3 · Conflict** | Pairwise within a dimension group where the constraints do not intersect, plus every disagreement on a NON-COMPARABLE dimension, plus every disagreement on NO dimension — who bears a duty, where a system must run — recorded with `dimension: null`. Its own section, `requires_counsel: true`, **escalated and never resolved**. |
| **4 · Timing** | Every obligation carrying a duration, ordered by tightness, each with its `trigger_condition` — the clock's start — and its citation. |
| **5 · Evidence and audit** | Union of `evidence_of_compliance` grouped by system surface, so the architecture learns what must be logged before the logging is designed. |
| **6 · Coverage and absence** *(mandatory)* | Angles run and not run with causes; zero-hit cells; instruments whose text was not retrievable; **jurisdictions not searched, named**. Phrased *"no applicable instrument found across N angles and M registers"* — **never "this product is unregulated"**. |
| **7 · Currency** | Each instrument's `as_of` against today, plus any future `applies_from_date`. An instrument binding in fourteen months is an architecture constraint now. |

## The merge rule, stated once more because it is the dangerous one

A merge resolves to the strictest stated standard **within one ordered dimension in one unit**.

`consent_basis` and `residency_constraint` are **not ordered**. There is no "stricter" consent
basis and no "stricter" residency constraint — two obligations disagreeing there are a conflict, and
the gate refuses a mandate row on either dimension. An earlier design said "merge at the stricter
standard" without that carve-out, which would have produced a single confident answer where the law
gives two incompatible ones.

## Counsel propagates

A mandate merging any obligation whose own record requires counsel requires counsel. The merge
tidied the group; it did not settle the question, and the gate checks this.

## `legal_review_required` is always true

It is a constant, not a judgement. This survey reads instruments; it does not give legal advice,
and a register that could declare itself not needing review would be doing exactly that.

## `capability_tags` are checked against the project first

The synthesis run's first deterministic check validates every tag against the project's
`capability-map.yaml`, before any tally. The portable gate never sees that file.

## The register's fields, one by one

`lineage.extends` names the register a delta amends, and null on an initial run.

An `instruments[]` row carries `applies_part` where the instrument applies in part — the gate
refuses an in-part row that does not say which part.

A `mandates[]` row carries `mandate_id`, its `dimension`, the `merged_standard` in that dimension's
own unit, a `verification_hint` saying how a build phase would CHECK it was met, the
`source_requirement_ids` of every obligation merged, `requires_counsel`, and a `conflict_ref` where
the same dimension also produced one.

A `conflicts[]` row carries `conflict_id`, its `dimension` — null where the obligations disagree on
none of the seven — the `requirement_ids` in tension — at least two, because a conflict is between
obligations — and `why_irreconcilable`.

The `timing[]` block carries one `requirement_id` per deadline; the `evidence[]` block groups
`requirement_ids` by the surface that must produce the evidence.

An `absence[]` entry carries `angles_ran` and `registers_searched` as its receipt, plus
`jurisdictions_not_searched` and `unretrievable_instruments` — both named rather than counted,
because a jurisdiction nobody searched and an instrument nobody could read are different facts from
a search that returned nothing.
