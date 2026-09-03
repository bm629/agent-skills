# Conditions

Judge every one that applies. Each names the deterministic rule that owns the other half where one
exists — a finding you raise against that rule is noise.

**C1 — The canonical terms are the ones the CORPUS uses**

The `canonical` of each group is the spelling the connector catalogs and descriptor indexes
actually use, not the spelling the scope document happens to prefer. Nango writes `payments`, not
`payment`. A canonical nobody's index carries returns nothing and the coverage grid records it as a
legitimate zero.

*The gate cannot know this: it never fetches. No rule owns it.*

**C2 — The six-axis coverage is honest, and the THREE folded sub-topics are present**

Every axis either carries a group or is in `scope_guard.absent_types` with a reason the capability
map supports (`group-type-accounted` owns the mechanical half). Judge the REASON.

Then the three coverages that have no gating field and fold into an angle:

- **integration CATEGORIES** fold into `a1` — one coverage cell per `category` group;
- **integration PATTERNS** fold into `a2` — the descriptor kind plus `servers[].protocol`;
- **DATA-RESIDENCY** folds into `b3`, which is conditional on `regulatory.applies`.

And the fourth, which is **NOT a fold**: whether the product itself emits webhooks is a qualitative
WIDENER in `b2`'s precondition, recorded in `predicate_omits`. A widener never anchors.

**C3 — Per-angle verdicts are right in BOTH directions**

An angle recorded `holds: true` really is implied by the classification, and an angle recorded
`holds: false` names the DECIDING value. `angle-verdict-complete`, `angle-verdict-unique` and
`always-on-angle-holds` own the mechanical halves; you own whether the reason is TRUE.

**C4 — Queries are recorded VERBATIM, including the filter expression**

A catalog walk that applied a filter records the filter. `queries[]` is what was run, not a
paraphrase of what was meant. A reader must be able to re-run it.

*No rule owns this: the gate cannot tell a verbatim query from a plausible one.*

**C5 — The enumerated-versus-bounded zero is used correctly**

`enumerated: true` means the source was walked as a COMPLETE listing — every entry examined,
whatever term filter was then applied to the results. `false` means the TRAVERSAL was bounded.
`enumerated-required`, `enumerated-zero-is-a-claim` and `enumerated-absent-on-na` own the shape.

**You own the truth of it.** A cell claiming `enumerated: true` against a catalog the producer
paged through and abandoned is a false claim the gate cannot see, and it is the difference between
"this service is absent from Nango" and "we did not find it".

**C6 — Cause evidence is OBSERVABLE**

A non-reached cell's `cause` carries an HTTP status, a redirect target, a challenge body or an auth
wall. `status-needs-cause` owns the presence; you own whether "the site seemed down" is evidence.

**C7 — The four-band authority record is defensible for the page the LOCATOR points at**

`source_authority` is the band of the source the `locator` POINTS AT — the authority of the
EVIDENCE — not the band of the cell that found the row. A candidate discovered in a connector
catalog and quoted from the vendor's own page correctly carries `first-party`.

`authority-band-known` is a REGISTRY rule and owns nothing here: it checks that every registry ROW
carries a band. Whether the candidate's band matches the page its locator points at is yours, and
it needs a fetch.

**C8 — The vendor-host `item_id` really resolves to the vendor**

`host-id-grammar`, `nodomain-id-grammar` and `id-class-matches-id` check the SYNTAX. Whether
`stripe.com` is Stripe's own host, and whether a `NODOMAIN-` slug names a service that genuinely
has no host of its own, needs a request. Yours.

**The case a request cannot settle, stated so you do not have to infer it.** A service whose only
home is a RESERVED or private-use name — `.internal`, `.local`, an RFC 1918 address, an
organisation-internal host — is correctly `NODOMAIN-`, and its `homepage` correctly records that
name. It is not a globally unique registrable identifier, so it cannot serve as a cross-wave join
key, which is the whole reason the `NODOMAIN-` class exists. **And you cannot discharge C7 for it
either**: a `first-party` band on a locator nobody outside that network can fetch is unverifiable by
construction. Record that you could not verify it rather than approving or refusing it on a guess.

**C9 — The OAS and IANA vocabularies are carried VERBATIM, not paraphrased**

`auth_scheme`, `oauth_flow` and `http_scheme` are transcribed from the descriptor. `null` is
correct where the catalog's `auth_mode` has no OAS member — three of the nine map to `null` by
design, and forcing the nearest-looking member asserts a scheme the service does not offer.
`http_scheme` keeps the descriptor's own spelling, including lower-case `bearer`.

`oas-auth-vocabulary`, `oauth-flow-needs-oauth2`, `http-scheme-needs-http` and
`http-scheme-vocabulary` own membership. You own whether the value matches the descriptor.

**C10 — The claim-versus-quote boundary holds**

`evidence_quote` is verbatim from the `locator`. `claim` is what this survey asserts from it. The
claim must be supported by the quote and must not exceed it.

**ONE quote, from ONE page — the page the `locator` names.** A quote that splices a docs page and
its linked descriptor is not verbatim from the locator, however true both halves are, because a
reader following the locator cannot find the string. If the descriptor is the evidence, the
descriptor is the locator.

*No rule owns this. A rule joining the two would refuse exactly the honest case.*

**C11 — The two-conjunct admission test was applied, and applied correctly**

A candidate is admitted only where BOTH hold: it has a first-party home the producer resolved, AND
a corpus row was retrieved for it. A service asserted only by a listicle, a blog post or a
search-result snippet belongs in `unadmitted[]` with `reason_class: no-first-party-home` (conjunct
a) or `no-retrievable-corpus-row` (conjunct b).

**And the carve-out: admission does NOT test whether a public API exists.** A domain-expected
service with no public API is a RISK a later wave reports, not an absence. An artifact that dropped
such a service has deleted the finding the architecture document most needs.

*Neither conjunct is decidable by a gate that never fetches. No rule owns it.*

**C12 — The capability coverage is complete**

Every capability in the capability map maps to at least one `category` group or is in
`scope_guard.excluded[]` with its reason. **This is a second pass**: the coordinator's keyword-map
ticket owns the deterministic set-difference, and nothing in the producer's validator can see
`capability-map.yaml`. Judge the EXCLUSION REASONS.

**If `capability-map.yaml` was not handed to you, say so and judge only the reasons.** The
set-difference is not derivable from the artifact, and a condition recorded as "passed" when it was
merely unjudgeable is worse than one recorded as unjudgeable.

**C13 — `category` sits in the seeded vocabulary, or carries its provenance**

`category` is a frozen-but-extensible VOCABULARY, not an enum, so no rule can close it. A value
outside the seeded union is legal and must carry its provenance in `notes[]`. A value invented
silently is not.

**The seed is in the producer package**, at
`integrations-prior-art-survey/references/category-vocabulary.md`. Judge against that. If the
survey used a value outside it, the value is legal and must carry its provenance in `notes[]`.

**C14 — `present_on[]` is the COMPLETE membership (a1 only)**

Every catalog that listed the service, including the one that won `found_by`. The FOUR
`present-on-*` rules own registry membership, reachedness, the found_by inclusion, and that the
field is a1's alone. **You own
whether the list is complete** — a catalog the producer walked, that carried the service, and that
is missing from this list, is the one wave-1 observation wave 2 cannot recover.

**C15 — A cap that was HIT records an ordering a reader could re-apply**

`bound.ordering` is the registry's signal verbatim, or the applied ordering with a real
`ordering_deviation`. `dropped_note` says what fell off the end. `cap-matches-registry`,
`cap-respected`, `bound-hit-needs-note`, `ordering-matches-registry` and
`ordering-deviation-contradicts` own the shape.

**You own whether the deviation's REASON is true** — "the catalog's category rank was not exposed
on this run" is checkable; "we preferred alphabetical" is a choice dressed as a constraint.

**C16 — An `unadmitted` row's `reason_class` fits what actually happened**

`duplicate-of` is for two distinct NAMES resolving to one canonical host. A cross-catalog re-find of
an already-recorded service is `present_on[]` ALONE and is never an unadmitted row — recording it as
one changes the `kept` arithmetic without changing what was found.

**C17 — The sanitization posture is recorded, and recorded as a POSTURE**

This type's corpus is descriptor and registry `description` fields — free text written by third
parties, and the highest concentration of attacker-controlled prose of any prior-art type. A `modified` status carries a cause
saying what was neutralised -- and `sanitization-cause` and `cell-sanitization-cause` already
refuse a missing one, so do NOT raise that half.

**A COUNT is a finding against the artifact.** It goes stale the moment the corpus moves and invites
the next reader to treat a smaller number as an improvement.

**C18 — The result is PROPORTIONATE, and a small honest result is correct**

Three candidates from a narrow scope is a result. An enumerated zero is evidence. A `vacated` angle
with observable causes is an honest record of a bad run.

**Do not raise a finding whose substance is "this seems thin."** If the coverage grid is complete,
the causes are observable and the admissions are justified, the artifact is correct however few rows
it carries. A reviewer who treats a small number as a defect teaches the next producer to pad, and
padding is the failure this survey exists to prevent.
