# `reviewing-visual-prior-art-survey`

Judge a produced visual prior-art artifact — a UI-pattern vocabulary map, a per-angle search
output, an extract record or the convention register and report — against a forty-condition bar single-sourced with `visual-prior-art-survey`. An
acceptance gate, not authoring.

## Why the bar lives here

`references/conditions.md` is the pair's single anchor. The producing skill points at it by name
and restates nothing normative. That arrangement exists because a bar duplicated across both
halves drifts: one document says `kept` counts results, the other says it counts rows, both look
right in isolation, and the disagreement only surfaces when an artifact is graded by the half
that did not write it.

## What it judges

**Mechanical conditions** are marked *(gated)* and discharged by one run of the co-installed
producer's validator. The reviewer does not restate them — duplicating the validator buries the
judgment half in noise.

**Judgment conditions** are the point:

- Is a zero a zero, or a failure wearing one? (C12, the central condition.) The arithmetic of a
  laundered failure reconciles perfectly, so nothing mechanical can see it.
- **Does the cited corpus actually contain the convention claimed?** (C16.) A URL that resolves
  and a plausible release stamp are both checkable by shape; whether the pattern page really
  specifies the keyboard contract asserted is checkable only by a reader who opens it.
- Are `authority` and `prescriptivity` both recorded, and not confused? (C19.) Authority is who
  says it; prescriptivity is whether it binds. Collapsing them puts a design system's preference
  on the same footing as a normative criterion for everyone downstream.
- Do the component and pattern groups describe *this* product's screens, or a generic interface?
- Is `provenance: extracted` honest — did a corpus really supply the term, or is it recall
  wearing a stronger label? The map is built before the search, so `extracted` is a claim that
  something was actually fetched.
- Is `corpus_version` present, meaningful, and distinct from `as_of`? A convention read from a
  three-year-old edition and stamped with today's date is wrong in a way nothing else catches.
- Is a claimed `token_format` DTCG and versioned, so it can be handed on unchanged?
- Was any screenshot gallery reached — including gallery content quoted at one remove through a
  secondary article?

## The domain-neutrality condition

C26 exists because the always-on angles are domain-neutral by construction and the artifact must
not present general convention as domain-specific screen guidance. A record claiming a screen
composition its cited corpus does not address is a finding, even when every field is well-formed:
it is the shape in which a downstream wireframing skill inherits an invented requirement.

## Proportionality is a condition, not a disposition

**C27 — a thin-but-honest artifact is correct output for a narrow UI.** A simple admin console
has few components, the domain-convention angle legitimately returns zeros for many domains, and
a short map with honest reasons is a correct result. Revising it invites padding, which is a
worse artifact than a thin one. The question is never "is there enough here?" but "is what is
missing accounted for?" — revise only on a specific *unrecorded* gap: a query not run and not
explained, a source not attempted and not noted, a candidate dropped without a reason.

## Evidence discipline

Every condition names what counts as grounds: the artifact, its schemas, and the producer's
`source-registry.yaml`. The reviewer's own taste in interfaces is explicitly not evidence — if a
convention seems missing, the finding is that the angle's coverage does not account for it, not
that the reviewer would have designed it differently. An ungrounded finding costs a revise round
and, at the cap, parks correct work.

Findings are reported in one pass. A reviewer who surfaces one problem at a time burns a revise
round per finding and the loop caps out on work that was nearly right.

## Output

Exactly one verdict line — `VERDICT: approve` or `VERDICT: revise` — followed by findings, each
naming its condition number and quoting the artifact text that fails it.

Proven against three planted fixtures shipped by the producer, each of which passes the
deterministic gate and is nonetheless wrong. A blind reviewer run caught all three under the
expected conditions (C12, C16, C19). An earlier blind run additionally surfaced two real defects
in the producer's own fixtures — a candidate attributed to a cell that could not have produced it
(C14) and a design-system record scoped to one component rather than one system (C18) — both
since fixed.

v1.1.0 — EXTRACT + SYNTHESIS waves. Thirteen conditions added, C28–C40.

Over the extract record: the evidence passage must carry the statement's substance rather than
summarise the page (C28); the authority band must match what published the source rather than how
authoritative it reads (C29); an applicability verdict must name the capability-map field it rests
on (C30); a convention that was read and does not bind is kept as `applies: false` rather than
converted into a skip (C31); a skip must say which capabilities it fails to touch in its own terms
(C32); a system's DTCG tokens are carried verbatim, never renamed into project vocabulary (C33);
and one record is one convention source (C34).

Over the register and report: every row must say what the record it cites says (C35); convergence
names its corpora rather than a count (C36); a conflict is stated rather than resolved by dropping
the weaker source (C37); a vacated angle is not reported as a negative result (C38); the report
recommends nothing about what the project should build, because that decision belongs to the
downstream design skill working from the register (C39); and every claim carries its convention id
or corpus (C40).

Proven by a blind pass over eight planted fixtures, each verified gate-clean first so it exercises
the reviewer rather than the validator. All eight were caught under the expected condition, and a
clean control was approved — with its one borderline (a statement clause the quoted passage did not
cover) correctly routed to an observation under C27 rather than raised as a finding. Three fixtures
had to be rebuilt first: two were schema-invalid, so the gate rejected them before any condition was
exercised, and one announced its own defect in a comment, which tests reading rather than judgment.

v1.0.0 — SEARCH wave.
