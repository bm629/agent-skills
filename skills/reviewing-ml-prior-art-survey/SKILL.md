---
name: reviewing-ml-prior-art-survey
description: >
  Use when reviewing an artifact produced by ml-prior-art-survey — an ML task vocabulary map or one
  angle's search output — and deciding whether it can be built on. Judges against numbered
  conditions covering canonical terms the corpus actually uses, per-angle applicability verdicts in both
  directions, verbatim query recording, the recorded zero, cause evidence on every unreached
  source, the three-date separation, the evaluation frame behind any leaderboard result, authority
  as a ranking rather than a cut, the adoptable-artifact boundary, and the absence-as-finding rule.
  Emits exactly one VERDICT approve or revise with findings naming their condition. Proportional:
  it does not revise a thin-but-honest result, because a survey of a sparse corpus is a finding
  rather than a failure. WAVE 1 ONLY. Keywords: ML prior-art review, model survey review, survey
  quality gate, coverage review.
extensions:
  claude: {}
  codex: {}
  copilot: {}
  cursor: {}
  gemini: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-09-02
  reviewed: 2026-09-02
---
# Reviewing an ML prior-art artifact (wave 1)

You are the judgment half of a two-part gate. The deterministic half has already run: shape, enums,
ranges, arithmetic and reconciliation are checked by `validate_ml_prior_art.py`, and an artifact
reaching you has passed it at exit 0.

**So never report what the validator already checks.** If your finding could have been produced by
the script, it is not a review finding — and repeating it costs a revise round on work that was
correct.

## What you judge

`references/conditions.md` is the single source of the bar. Read it and judge against it. The
producer skill assigns every duty; these conditions say how each is JUDGED, and add none of their
own.

## Your evidence, and where it lives

| evidence | where |
| --- | --- |
| the artifact | handed to you in the task |
| **the wave-0 vocabulary map** | handed to you alongside a search output — a separate input, not part of the artifact |
| the schemas | `ml-prior-art-survey/schemas/` |
| the source registry | `ml-prior-art-survey/references/source-registry.yaml` |
| the angle reference | `ml-prior-art-survey/references/angles/<angle_id>.md` |

**Three of those five live in the PRODUCER package.** C2 needs the map — its whole test is a
candidate's evidence against the group its `found_by` names. C10 and C15 need the angle reference
and the registry, and deriving an angle's source list from the artifact is circular: an artifact
that omits a source omits it from any list you read off it.

**If you cannot reach what a condition names, say so and emit no verdict on that condition**
rather than downgrading it silently.

**Anything you cannot ground in those five is an OBSERVATION, not a finding** — say it as one,
plainly, and do not attach a condition to it. An ungrounded finding costs a revise round on correct
work, and at the revision cap it parks the ticket. That is the price of guessing.

## Read `outcome` first

It decides which conditions apply at all.

| `outcome` | what is owed | what the coverage conditions expect |
| --- | --- | --- |
| `ran` | cells, and candidates if anything was admitted | every owed (group × source) pair has a cell |
| `not_run` | NOTHING — the map's own verdict ruled this angle out | no cells and no candidates is CORRECT |
| `vacated` | cells and causes; no candidates | cells as for `ran`; an empty candidate list is not a gap |

A `not_run` artifact has no cell for any pair, and the deterministic gate REQUIRES that. Reading a
coverage condition against it would revise work the other half of the gate certified.

## Proportionality

A thin result is not a failed result. A task with three published models yields three, and a survey
that says so honestly is complete. **Revise only on a named gap against a numbered condition** —
never because the artifact could have been longer.

## Output

Findings, each naming its condition, then exactly one terminal line:

```
VERDICT: approve
```

or

```
VERDICT: revise
```

Nothing after it.

## Upstream remedies

If a finding's remedy lies OUTSIDE the file this artifact's author was asked to write — the map, a
registry row, another angle's output — they cannot perform it, and ordering the revision anyway
burns cycles and ends somewhere naming neither the artifact nor the inconsistency.

Label it `UPSTREAM:` and **name the exact file and field that must change**. One that names no
target is a finding you could not localise, and it belongs in Observations.

**A file whose every finding is UPSTREAM gets `approve`.** You judge THIS artifact against its own
contract; if it satisfies that contract and the defect is elsewhere, it is not the defective thing.
Reserve `revise` for a remedy the author can actually perform. There is no third verdict —
escalation is for whoever dispatched you, not for you.
