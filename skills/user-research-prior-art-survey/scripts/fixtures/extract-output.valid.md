---
schema_version: 1
meta:
  source_id: DOI-10.1145/3313831.3376283
  as_of: '2026-08-05'
  revision: 1
outcome: extracted
source:
  title: Understanding Progressive Disclosure in Settings Interfaces
  url: https://doi.org/10.1145/3313831.3376283
  venue: CHI 2020
  study_date: '2020-04'
  study_design: controlled-study
  sample_size: 240
  effect_size: d=0.42
  access_status: open-access
findings:
  - id: DOI-10.1145/3313831.3376283#f1
    claim: >
      Collapsing rarely-used settings behind a disclosure control reduced time-to-task on the
      primary setting without measurable cost to discovery of the hidden ones.
    certainty: high
    transferability:
      level: moderate
      reason: >
        Measured on desktop settings panels with a general-consumer population; the mechanism
        plausibly carries to other progressive-disclosure surfaces but was not tested on mobile.
    population: general consumers recruited via panel, n=240
    platform_context: desktop web, 2020
    effect_verbatim: d=0.42 on time-to-task, 95% CI [0.16, 0.68]
  - id: DOI-10.1145/3313831.3376283#f2
    claim: >
      Participants located hidden settings faster when the disclosure control carried a label
      naming the category than when it carried only an icon.
    certainty: high
    transferability:
      level: moderate
      reason: >
        Same desktop population and platform as the primary finding; label-versus-icon effects
        are well replicated elsewhere but not tested here beyond this surface.
    population: general consumers recruited via panel, n=240
    platform_context: desktop web, 2020
    effect_verbatim: mean 4.1s vs 6.8s, p < .01
---

## Method

Between-subjects controlled study, n=240, desktop web. Two manipulations: a flat settings panel
against a progressive-disclosure variant (time-to-task on the primary setting, plus discovery of
the hidden settings), and within the disclosure variant, a labelled control against an icon-only
one (time to locate a hidden setting).

## Findings

Two findings are recorded above: the time-to-task effect and the label-versus-icon effect.

## Transferability

Both were measured on desktop with a general-consumer population; neither was tested on mobile,
which is why both carry moderate rather than high transferability.
