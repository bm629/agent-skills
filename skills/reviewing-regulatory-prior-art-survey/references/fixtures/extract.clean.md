---
# CLEAN calibration fixture — one extracted instrument, wave 2.
# `as_of` is the consolidation date of the TEXT; `retrieved_at` is when this record fetched it.
schema_version: 1
meta:
  instrument_id: CELEX-32016R0679
  as_of: '2016-05-04'
  retrieved_at: '2026-08-22'
  revision: 1
outcome: extracted
authority: issuing-body-text
instrument:
  title: Regulation (EU) 2016/679 on the protection of natural persons with regard to the
    processing of personal data
  short_name: GDPR
  instrument_type: regulation
  issuing_body: European Parliament and Council
  jurisdiction: EU
  citation: OJ L 119, 4.5.2016, p. 1
  celex: '32016R0679'
  eli: http://data.europa.eu/eli/reg/2016/679/oj
  cfr_citation: null
  standard_number: null
  source_url: https://eur-lex.europa.eu/eli/reg/2016/679/oj
  in_force_date: '2016-05-24'
  applies_from_date: '2018-05-25'
  binding_force: binding
  text_retrievable: full
  access_status: reachable
  applies_because: The product processes personal data of individuals in the EU as part of its
    core scheduling function, which is the material scope condition rather than a statement about
    the sector.
  scoping_evidence: The scope article states the regulation applies to processing of personal data
    wholly or partly by automated means.
requirements:
  - id: CELEX-32016R0679#r1
    obligation_ref: Article 33(1)
    requirement: Notify the supervisory authority of a personal data breach without undue delay
      and, where feasible, not later than the stated period after becoming aware of it.
    verbatim_anchor: not later than 72 hours after having become aware of it
    trigger_condition: becoming aware of the personal data breach
    mandatory: true
    dimension: breach_notification_deadline
    stated_standard: 72 hours
    duration_value: PT72H
    control_ids: []
    evidence_of_compliance: A dated breach register recording awareness time and notification time.
    interpretation_confidence: clear
    requires_counsel: false
    capability_tags:
      - data-protection
  - id: CELEX-32016R0679#r2
    obligation_ref: Article 32(1)
    requirement: Implement technical and organisational measures to ensure a level of security
      appropriate to the risk.
    verbatim_anchor: a level of security appropriate to the risk
    trigger_condition: null
    mandatory: true
    dimension: encryption_strength
    stated_standard: null
    duration_value: null
    control_ids: []
    evidence_of_compliance: null
    interpretation_confidence: ambiguous
    requires_counsel: true
    capability_tags:
      - data-protection
out_of_unit_count: 0
out_of_unit_criterion: Obligations addressed solely to supervisory authorities rather than to
  controllers or processors.
---

# CELEX-32016R0679 — GDPR

## Scope and applicability

Applies because the product processes personal data of individuals in the EU as part of its core
function. That is the material scope condition; the sector the product sits in is not what makes
this bind.

## Requirements

Two obligations were read in unit: a breach-notification deadline with a stated period and a
trigger, and a security obligation whose standard the instrument deliberately does not state.

## What this does not establish

An obligation to secure personal data does not establish which algorithm, which key length or
which control framework. The security article states a risk-appropriate standard and names no
specification, so the record carries a null standard rather than one this survey chose.

Nor does the breach deadline establish what our internal detection latency must be — the clock
starts at awareness, and how quickly we become aware is an engineering decision this instrument
does not speak to.

## Retrieval and limits

Consolidated text retrieved from the issuing body's own resolver, consolidation date 2016-05-04.
No paywall, no access restriction, full text retrievable.
