# Planted defects — the judgment half of the gate

These artifacts are **deliberately wrong in ways the deterministic validator cannot see**. Both
exit 0 against `validate_security_prior_art.py`. That is the point: a gate demonstrated only on
good input proves nothing about the half of it that is judgment, so the reviewing skill is
proven by being handed these and asked to rule.

Regenerate them from the valid fixtures whenever those change, so the two stay in step.

## `threat-vocabulary-map.silent-narrowing.yaml`

Derived from the valid map by deleting the `vendor-product` group and recording that type as
absent with the reason *"the product does not depend on any third-party service"*, then flipping
the vendor-advisory angle's verdict to not-applicable.

Shape-perfect: every group type is accounted for, the absent type carries a reason, and the
angle verdict is present. Only a reader holding the scope context can see that the scope names a
hosted payments provider, so the reason is false and an entire angle has been emptied from the
map side.

**Expected ruling:** revise, naming the scope-translation condition for the uncorroborated absent
type and the source-selection condition for the contradicted angle verdict.

## `search-output.failure-as-zero.yaml`

Derived from the valid search output by retyping the `unreachable` cell as `reached` with a zero
count, clearing its cause and fallbacks, and emptying the retrieval summary to match — then
adding a note admitting the corpus "was slow all session and timed out repeatedly".

Shape-perfect and internally consistent: the summary agrees with the cells, the counts add up,
and every schema rule passes. The lie is visible only by reading the notes against the cells.

**Expected ruling:** revise, naming the failure-status condition — both for the failure written
as a zero and for the summary omitting a source the artifact elsewhere admits was degraded.

## Gate result, 2026-08-03

Both were caught, each under the expected condition and with concrete locations. The reviewer
additionally found the internal tell in the first artifact — a vendor-advisory source sitting in
the active list while that angle was declared inapplicable — which was not planted.

It also surfaced two genuine defects in the *valid* fixtures, since fixed: registry sources
belonging to applicable angles appeared in neither the active nor the skipped list, and a
candidate's relevance line asserted the product resolves dependencies from a public registry when
the scope states no dependency set has been chosen. A fixture the reviewer would revise is a poor
exemplar, so both were corrected and these planted files regenerated from the corrected originals.

---

# Wave 2 — extract records

## `extract-output.tier-contradicts-body.md`

Derived from the valid extraction by claiming `tier: 1` on a `matching-incident`, while the
body's evidence section states that the incident corpora record no exploitation at all.

Shape-perfect: the tier-strength rule is satisfied because `matching-incident` is a legitimate
tier-1 evidence kind, and every schema rule passes. The contradiction is only visible by reading
the frontmatter against the body.

**Expected ruling:** revise, naming the tier-evidence condition.

## `extract-output.uncertain-bail.md`

A relevance bail whose rationale hedges throughout — "probably does not apply", "might affect
the upload path", "seemed unlikely to be worth the read" — while clearing the rationale length
floor and every structural rule.

**Expected ruling:** revise, naming the bail-integrity condition. Uncertainty *keeps* the item;
the expensive read is cheaper than a missed threat, and this is the only cut in the survey.

## Gate result, 2026-08-03

Both caught under the expected conditions. The uncertainty bail drew two findings rather than
one: the hedging, and separately the cost-based reasoning ("not worth the read"), which is an
effort judgment rather than a relevance verdict and is exactly what the condition excludes.

The clean extraction was **approved** — no false-revise — with one non-blocking observation that
its `surfaces` field named "document rendering", which the caller's scope never states. That was
a fair catch on a fixture meant to be exemplary, so the surface was narrowed to the scope's own
term and the render path moved to preconditions where it was already correctly hedged.

---

# Wave 3 — threat registers

## `threat-register.authored-control.yaml`

Derived from the valid register by replacing one row's control with a mandate the survey wrote
itself — antivirus scanning, isolated buckets, signed URLs — while keeping the original source
reference bolted on. Schema-valid: `stated: true` with text and a reference string.

**Expected ruling:** revise under the control-attribution condition and, separately, under the
manufactured-authority condition — the "MUST" needs its own fix even after re-attribution.

## `threat-register.coined-name.yaml`

Derived by renaming a row to a product-flavoured phrase ("Sneaky self-approval loophole in the
expenses flow") pinned to an attack-pattern identifier whose title is something else.

**Expected ruling:** revise under the threat-naming condition. A coined name means the same
threat carries a different name each request and the living register can never merge.

## Gate result, 2026-08-03

Both caught. The authored control drew two findings rather than one — the reviewer separated
re-attributing the control from removing the mandate voice, which is right: fixing the citation
alone would leave a "MUST" resting on the survey's authority.

It also found a real defect in the register the fixtures call valid, verified against both
catalogs: `naming_ref: CAPEC-639` paired with a `name` that is verbatim the title of **CWE**-639.
The two catalogs number independently, so 639 resolves in both — CAPEC-639 is "Probe System
Files", nothing to do with authorization bypass. A number that resolves in the wrong catalog is
the sharpest version of this failure, because nothing about it looks wrong. Corrected to CWE-639
and the planted files regenerated from the corrected baseline.
