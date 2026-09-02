# Writing the regulatory scope map (wave 0)

The map is a SEARCH PROTOCOL, not a survey. Its job is to decide what the eight angles will look
for, which of them run at all, and which sources they may cite. Its load-bearing output is the
`sector_scoping` receipt and the instrument shortlist; the vocabulary axes are what the coverage
grid is keyed on.

## The nine axes

| axis | what a group is | searched by |
| --- | --- | --- |
| `instrument` | a named legal instrument | a1, a2, b1, b2, b3, b5 |
| `sector` | one of the nine sector families | a1 |
| `jurisdiction` | EU, US-federal, US-CA, UK | a1, a2, b2, b4 |
| `obligation-dimension` | retention, consent, breach-notification, access-control, transparency, logging | a2, a3, b1 |
| `control-catalog` | a named catalog or numbered standard | a3, b2, b5 |
| `platform-role` | intermediary / hosting / online-platform / gatekeeper | b3 |
| `transfer-mechanism` | adequacy decision, SCC implementing decision, national mechanism | b4 |
| `model-term` | risk-management system, human oversight, post-market monitoring | b1 |
| `ui-term` | conformance level, success criterion, assistive technology | b2 |

An axis a HOLDING angle needs must be POPULATED or listed in `scope_guard.absent_types`, and
**exactly one of the two** — an axis that is both is a contradiction the validator refuses at
`group-type-accounted`, because a declared absence and a minted group are opposite claims about
the same axis. An
unaccounted axis is indistinguishable from one nobody thought about.

## `canonical` is the term the CORPUS uses — and it is NOT the official title

For an `instrument` group, `canonical` is the short name a regulator would recognise: `GDPR`, not
*Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on…*.

**The official title is never transcribed here.** A title IS a citation, citations are this type's
worst failure mode, and a title copied through three documents is a title nobody re-read. It is
read from the resolved document at extract time, verbatim, once.

## A term sited in two groups is DECLARED, not forbidden

`HIPAA` genuinely belongs to both the health SECTOR vocabulary and the instrument group — a
searcher working either one writes it. Nothing here tells you to drop one.

But `canonical` and every `expansion` name a query, so a term in two groups issues that query in
two CELLS. `item_id` is unique across the whole search output, so whatever both cells surface gets
filed under one and is simply missing from the other, whose `kept` then under-counts with nothing
recording why.

List it, with the group that takes the artifact:

```yaml
  shared_terms:
    - term: HIPAA
      groups: [health, hipaa-security-rule]
      owner: hipaa-security-rule
```

Matching folds case and whitespace. The `owner` must be one of the groups the term actually
reaches, and the term must actually reach two — a declaration for a collision that does not exist
records something that did not happen, and reads as handled exactly like a real one.

## The sector receipt is the half everything downstream consumes

One verdict per family, **all nine, always**: `health`, `financial-payments`, `children-minors`,
`public-sector`, `employment-hr`, `insurance`, `education`, `telecom-critical-infrastructure`,
`export-controlled`. A family silently absent is a validator failure, not a judgment call.

`applies` is `applies | does-not-apply | undetermined`, and **`undetermined` is first-class.** Note
the spelling: bare `yes` and `no` are YAML booleans, so those words cannot be used here — a
producer writing them gets `True` and an error naming neither the field nor the fix.

Admissible evidence is the classification values, the domain free-text, the data-sensitivity level,
and the request context. Anything else is a guess wearing a verdict's clothes.

## Every angle gets a verdict, in both directions

Eight verdicts, including the ones that do not hold. An angle that never ran and an angle that ran
and found nothing are different facts, and only a recorded verdict distinguishes them before the
search wave starts.

**An always-on angle can never be `holds: false`** — it has no precondition to fail, so a false
verdict on one is a producer error the gate refuses rather than a fact about the scope.

A `holds: false` on a conditional angle must name the DECIDING value: "`business.platform.type` is
`none` — the deciding value, falsifying the only leg". A reason that names no scope value cannot be
checked against the classification.

## The probe

Four cheap checks before eight angles are dispatched. Does the EU channel answer under the header
pair? Does the same URI 404 without it? Does the US register resolve by identifier? Did a guidance
index move? A map whose terms reach nothing is a protocol failure, and it is far cheaper to find
here than in eight children.
