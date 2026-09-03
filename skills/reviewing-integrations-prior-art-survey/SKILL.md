---
name: reviewing-integrations-prior-art-survey
description: >
  Use when reviewing an integrations prior-art artifact — an integration vocabulary map or one
  angle's search output — before it is accepted. Judges what a deterministic gate cannot: whether a
  locator host really is the vendor's own, whether an evidence quote supports the claim drawn from
  it, whether an authority band is defensible for the page it points at, whether the capability
  coverage is honest, and whether an admission or an absence was recorded truthfully. Emits exactly
  one verdict, approve or revise, with every finding tied to a numbered condition. WAVE 1 ONLY.
  Keywords: integrations prior art review, connector catalog review, descriptor evidence, vendor
  scope, coverage grid, prior-art reviewer.
extensions:
  claude: {}
  codex: {}
  copilot: {}
  cursor: {}
  gemini: {}
version: "1.0.0"
forge:
  status: reviewed
---

# Reviewing an integrations prior-art artifact

You are the second half of a two-part gate. The first half already ran.

**Do not re-check what the validator refuses.** Every condition below names the rule that owns the
other half where one exists, and a finding you raise against a rule the gate already enforces is
noise that costs the author a cycle. If the gate did not run, say so and stop — a clean gate run is
a precondition of this review, not a substitute for it.

## Your evidence

| source | what it settles |
| --- | --- |
| the artifact under review | everything below |
| the vocabulary map it was produced against | whether the owed grid and the angle verdicts are right |
| the SCOPE and CLASSIFICATION the producer was handed | whether `meta.classification` is a faithful transcription |
| `schemas/*.json` | what each field is FOR, in its `description` |
| `references/source-registry.yaml` | caps, orderings, bands, `complete_listing`, the excluded block |
| `references/angles/<angle>.md` | that angle's mechanism, sources and precondition |

**Six sources.** The scope and classification are on the list because `meta.classification` is a
TRANSCRIPTION, and judged only against itself a fabricated value reads exactly like a real one.

## Conditions

Read `references/conditions.md`. Judge every condition that applies. A condition that does not
apply is recorded as such — silence is not a verdict.

## Your verdict

Emit exactly one line, last:

```
VERDICT: approve
```

or

```
VERDICT: revise
```

`revise` requires at least one finding naming its condition. `approve` with findings attached is a
contradiction; if the findings are real, the verdict is `revise`.

**Do not false-revise honest work.** An artifact that records a small result honestly — three
candidates, an enumerated zero, a vacated angle with observable causes — is a correct artifact. The
survey's job is to record what is there, and a reviewer who treats a small number as a defect
teaches the next producer to pad.
