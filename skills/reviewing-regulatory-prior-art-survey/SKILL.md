---
name: reviewing-regulatory-prior-art-survey
description: >
  Use when reviewing an artifact produced by regulatory-prior-art-survey — a regulatory scope map
  or one angle's search output — and deciding whether it can be built on. Judges against numbered
  conditions covering canonical terms the corpus uses, the nine-family sector receipt, per-angle
  verdicts in both directions, verbatim query recording including the headers that made a request
  work, the recorded zero, cause evidence with observable status and redirect targets, the
  four-date separation, authority as a rank and binding force as an orthogonal fact with neither
  ever cutting, the verifiability basis for refusing admission, and the claim-versus-quote boundary that fabricated
  citations cross. Emits exactly one VERDICT approve or revise with findings naming their
  condition. Proportional: it does not revise a thin-but-honest result. WAVE 1 ONLY. Keywords:
  regulatory review, compliance survey review, citation check, survey quality gate.
---

# Reviewing a regulatory prior-art artifact (wave 1)

You are the judgment half of a two-part gate. The deterministic half has already run: shape, enums,
ranges, arithmetic and reconciliation are checked by `validate_regulatory_prior_art.py`, and an
artifact reaching you has passed it at **exit 0**.

**So never report what the validator already checks.** If your finding could have been produced by
the script, it is not a review finding — and repeating it costs a revise round on work that was
correct.

## What you judge

`references/conditions.md` is the single source of the bar. Read it and judge against it. The
producer skill assigns every duty; these conditions say how each is JUDGED and add none of their
own.

## The one failure worth more attention than the rest

A **fabricated citation** — an obligation the instrument's text does not carry, an identifier
nobody resolved, or a `text_retrievable` that is not the state the fetch actually reached, which is C23 and the reachable route to the same lie. C19 and C23 are where that
surfaces, and a finding under either is worth more than three findings under anything else.

## Your evidence, and where it lives

| evidence | where |
| --- | --- |
| the artifact | handed to you in the task |
| **the regulatory scope map** | handed to you alongside a search output — a separate input, not part of the artifact |
| **the scope and classification the producer was handed** | handed to you alongside the map — see below |
| the schemas | `regulatory-prior-art-survey/schemas/` |
| the source registry | `regulatory-prior-art-survey/references/source-registry.yaml` |
| the angle reference | `regulatory-prior-art-survey/references/angles/<angle_id>.md` |

**The scope and classification are handed to you because without them `meta.classification` is
unfalsifiable.** The producer is ordered to transcribe them VERBATIM, precisely so a verdict citing
a value can be checked against what it actually had. Judging every verdict against the producer's
own transcription checks that it is self-consistent and nothing more — a fabricated value reads
exactly like a real one. C5 and C8a both rest on this.

**Three of those six live in the PRODUCER package.** C2 needs the map — its whole test is a
candidate's evidence against the group its `found_by` names. C15 and C23 need the angle reference
and the registry, and deriving an angle's source list from the artifact is circular: an artifact
that omits a source omits it from any list you read off it.

**If you cannot reach what a condition names, say so and emit no verdict on that condition**
rather than downgrading it silently.

**Anything you cannot ground in those six is an OBSERVATION, not a finding** — say it as one,
plainly, and do not attach a condition to it. An ungrounded finding costs a revise round on correct
work — and the number of revise rounds one artifact gets is capped by whatever dispatched you, so
a round spent on an ungrounded finding is a round the real ones do not get.

## Read `outcome` first

It decides which conditions apply at all.

| `outcome` | what is owed | what the coverage conditions expect |
| --- | --- | --- |
| `ran` | cells, and candidates if anything was admitted | every owed (group × source) pair has a cell |
| `not_run` | NOTHING but the verdict it honours | no cells and no candidates is CORRECT |
| `vacated` | cells, their causes, a `vacated.cause` and a `retrieval_summary`; no candidates and no `unadmitted` rows | cells as for `ran`; an empty candidate list is not a gap |

A `not_run` artifact has no cell for any pair, and the deterministic gate REQUIRES that. Reading a
coverage condition against it would revise work the other half of the gate certified.

## Proportionality

A thin result is not a failed result. A lightly-regulated scope yields few instruments, and a
survey that says so honestly is complete. **Revise only on a named gap against a numbered
condition** — never because the artifact could have been longer.

This matters unusually here. It is always possible to name one more instrument that might bind, and
a reviewer who does that pushes the producer toward padding a register with obligations nobody in
scope has — which is worse than the thinness, because an architect acts on it.

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
