# Conditions

Judge every one that applies. Each names the deterministic rule that owns the other half where one
exists — a finding you raise against that rule is noise.

**C1 — The canonical terms are the ones the CORPUS uses**

The `canonical` of each group is the spelling the connector catalogs and descriptor indexes
actually use, not the spelling the scope document happens to prefer. A canonical nobody's index
carries returns nothing and the coverage grid records it as a legitimate zero.

**The one exception, and it runs the other way.** Where a catalog's spelling differs from the
capability map's, the UPSTREAM spelling is recorded and the catalog's becomes an EXPANSION — the
join with the capability map is what `category` exists for. Nango's index writes `payment`; the map
records `payments` and carries `payment` as an expansion, so both the join and the query work. An
earlier version of this condition had that example backwards.

*The gate cannot know this: it never fetches. No rule owns it.*

**C2 — The six-axis coverage is honest, and the THREE folded sub-topics are present**

Every axis either carries a group or is in `scope_guard.absent_types` with a reason the capability
map supports (`group-type-accounted` owns the mechanical half). Judge the REASON.

Then the three coverages that have no gating field and fold into an angle:

- **integration CATEGORIES** fold into `a1` — one coverage cell per `category` group;
- **integration PATTERNS** fold into `a2` — the descriptor KIND is the evidence, plus AsyncAPI's `servers[].protocol` where the descriptor is AsyncAPI -- OpenAPI's Server Object has no `protocol`, so for an OpenAPI descriptor the kind plus the operation shape is what there is;
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

`group-term-unqueried` owns COMPLETENESS — every term a group declares must be asked on that
group's cells. *You own FIDELITY: the gate cannot tell a verbatim query from a plausible one.*

**C5 — The enumerated-versus-bounded zero is used correctly**

`enumerated: true` means the source was walked as a COMPLETE listing — every entry examined,
whatever term filter was then applied to the results. `false` means the TRAVERSAL was bounded.
`enumerated-required`, `enumerated-zero-is-a-claim` and `enumerated-absent-on-na` own the shape.

**You own the truth of it.** A cell claiming `enumerated: true` against a catalog the producer
paged through and abandoned is a false claim the gate cannot see, and it is the difference between
"this service is absent from Nango" and "we did not find it".

**C6 — Cause evidence is OBSERVABLE**

A non-reached cell's `cause` carries an HTTP status, a redirect target, a challenge body or an auth
wall. `status-needs-cause` owns the presence and `cell-source-skipped` refuses a cell against a
source the map skipped; you own whether "the site seemed down" is evidence.

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

**A MULTI-PRODUCT vendor's host is the same host for every one of its products.** `google.com` is
as much Google Calendar's as Google Maps Platform's, so an `item_id` at vendor scope cannot separate
them and a wave-2 join on it merges the two. The scope is the VENDOR by design (stated in this package's `SKILL.md` step 21, "Write each candidate at VENDOR scope"), so this is
correct rather than a defect — but say in `notes[]` WHICH product the row is about whenever the
vendor ships more than one that the survey could have found. A reviewer cannot infer it and a later
wave cannot recover it.

**The case a request cannot settle, stated so you do not have to infer it.** A service whose only
home is a RESERVED or private-use name — `.internal`, `.local`, an RFC 1918 address, an
organisation-internal host — is correctly `NODOMAIN-`, and its `homepage` correctly records that
name. It is not a globally unique registrable identifier, so it cannot serve as a cross-wave join
key, which is the whole reason the `NODOMAIN-` class exists. **And you cannot discharge C7 for it
either**: a `first-party` band on a locator nobody outside that network can fetch is unverifiable by
construction. Record that you could not verify it rather than approving or refusing it on a guess.

**C9 — The OAS and IANA vocabularies are carried VERBATIM, not paraphrased**

`auth_scheme`, `oauth_flow` and `http_scheme` are transcribed from the descriptor. `null` is
correct where the catalog's `auth_mode` has no OAS member — the `null` rows in the producer's own table say which, and the
table is in the producer's `references/absent-input-policy.md`. Forcing the nearest-looking member
asserts a scheme the service does not offer. The nine are a COVERAGE table, not the whole catalog:
measured 2026-09-03 they cover 919 of 990 rows, and a mode outside them records `null` WITH the
catalog's own value in `notes[]`.
`http_scheme` keeps the descriptor's own spelling, including lower-case `bearer`.

`oas-auth-vocabulary`, `oauth-flow-needs-oauth2`, `http-scheme-needs-http` and
`http-scheme-vocabulary` own membership. You own whether the value matches the descriptor.

**C10 — The claim-versus-quote boundary holds**

`evidence_quote` is verbatim from the `locator`. `claim` is what this survey asserts from it. The
claim must be supported by the quote and must not exceed it.

**Interpretation is allowed; assertion about the world is not.** A `claim` may connect the quote to
the scope — "the address-to-coordinate step this scope's territory matching depends on" is reading
the evidence for a reader, and that is what `claim` is for. It may NOT assert an empirical fact the
quote does not carry: "the system a contractor is most likely to run" is a market-share claim, and
no quote about an API establishes it. The test is whether a reader could disagree with you about the
WORLD rather than about the reading.

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

Every catalog this run OBSERVED listing the service, including the one that won `found_by`.

**It is a record of what the run saw, not of what the catalogs contain.** A source whose traversal
was bounded — `enumerated: false`, a cap or a cursor — and stopped short of the entry is correctly
ABSENT from the list, and demanding it would demand an observation nobody made. The calibration
fixture depends on exactly this reading: four candidates omit `pipedream-components`, whose listing
is API-capped at 1,000 and never reached them, while `acuity-scheduling` sorts inside the cap, was
observed, and IS listed. The FOUR
`present-on-*` rules own registry membership, reachedness, the found_by inclusion, and that the
field is a1's alone. **You own
whether the list is complete** — a catalog the producer walked, that carried the service, and that
is missing from this list, is the one wave-1 observation wave 2 cannot recover.

`found-by-precedence` owns which SOURCE won the attribution; you own which GROUP did, and whether
the membership list is complete.

**C15 — A cap that was HIT records an ordering a reader could re-apply**

`bound.ordering` is the registry's signal verbatim, or the applied ordering with a real
`ordering_deviation`. `dropped_note` says what fell off the end. `cap-matches-registry`,
`cap-respected`, `bound-hit-needs-note`, `ordering-matches-registry` and
`ordering-deviation-contradicts` own the shape.

**You own whether the deviation's REASON is true.** "The catalog paginated and stopped exposing its
own entry order past page 4, so the tail was ranked by name alone" is checkable — you can ask
whether that source paginates and whether the artifact's own cells show the stop. "We preferred
alphabetical" is a choice dressed as a constraint.

**Check the registry before you accept an example, including this one.** THREE earlier versions of
this paragraph failed that test: the first cited a "category rank" the registry records as never
having existed; the second cited a per-category-count tie-break no angle declares; the third
described a candidate whose group has no declaration index, which `candidate-group-known` and
`row-cell-unknown` make impossible — every `found_by` names a declared group and a recorded cell,
so no row can lack a position. **An example describing a state the gate forbids is the same
unfalsifiable-reason defect this condition is about, one level up**, and it took three revisions to
stop producing one.

**The two ordering shapes.** SIX angles — `a2`, `a3`, `b1`, `b2`, `b3`, `b4` — key on the map's own
group declaration order. `a1` and `b5` key on their SOURCE's own listing order. A deviation reason
is judged against the shape the angle under review actually uses; an earlier revision of this
paragraph said every ordering had been re-derived onto declaration order, which was never true of
those two.

**C16 — An `unadmitted` row's `reason_class` fits what actually happened**

`duplicate-of` is for two distinct NAMES resolving to one canonical host. A cross-catalog re-find of
an already-recorded service is `present_on[]` ALONE and is never an unadmitted row — recording it as
one changes the `kept` arithmetic without changing what was found — and `kept-matches-rows` owns
that arithmetic, so you own only whether the reason_class FITS.

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

**C19 — `meta.classification` is a faithful TRANSCRIPTION of the scope the producer was handed**

Every angle verdict is judged against the classification (C3), so a fabricated classification
satisfies C3 by construction: the verdicts agree with it perfectly, and the whole applicability
record is unfalsifiable. This condition is the only place that asks whether the classification
itself is real.

Compare `meta.classification` field by field with the scope document you were given. A value that
does not appear in the scope, or contradicts it, is a finding here — the deciding values are the
ones the angle verdicts lean on: `integrations.expected`, `integrations.complexity`,
`archetype.primary`, `scale.real_time`, `regulatory.applies` and `data_ml.ml_involvement`.

**If the scope was NOT supplied to you, say so and record the condition unjudgeable** — the same
treatment C12 gives an evidence source you could not reach. Do not approve the transcription on the
grounds that it looks plausible; a fabricated value reads exactly like a real one, which is why this
condition exists.

**This condition was missing.** The evidence table declared the scope and classification as a source
whose job was "whether `meta.classification` is a faithful transcription", and no numbered condition
asked it — so a reviewer who caught a fabricated classification had no condition to name, and
`revise` requires one.

**C20 — The probe note NAMES each check and what it returned**

The probe is three requests, not a feeling: two always-on terminal fetches and one service-name
resolution. Its whole purpose is that three cheap checks beat eight children dispatched against a
vocabulary that reaches nothing.

`probe-record` checks only that `ran` is present and the note is non-empty. **A map that made ONE
request and wrote `note: ok` passes the gate at exit 0**, and until this condition existed no
reviewer had one to name. Judge the note: it must say which channels were reached, and what each
returned — a count, a status code, or an observable failure.

**A zero or a refusal is a finding about the CORPUS, not a failed probe.** "apis-guru returned 200
with 2,529 descriptors; the vendor-docs resolution returned 403" is a complete note. What is not
complete is a note that reports fewer checks than the guide's three without saying why, or that
reports none of them individually.

**`ran: false` needs the reason in the note**, and a map that skipped the probe entirely has
dispatched every angle against an unverified vocabulary — say so as a finding, because the cost of
that mistake is paid by every child.

**C21 — The record is read from the FIRST-PARTY source, and `source_authority` says which**

The deep read is the point of this phase. A record whose facts are a connector catalog's summary of
a vendor — its auth mode, its category, its "supports webhooks" flag — is a restatement, and
`source_authority` must then say `connector-catalog`, not `first-party`.

Lens 3's denominator counts the first-party-verified records, so a band inflated here inflates a
published convention. *The gate never fetches: it takes the band at face value. You own whether the
band is true, and the evidence quotes are where you check it.*

**C22 — The complexity COMPONENTS are the ones the record's own facts support**

`complexity-1` owns the arithmetic — the score must equal its four components. **You own whether
each weight is right**, and the record carries everything you need to check it: `auth_w` against the
recorded `auth_scheme` and `oauth_flow`, `event_w` against `emits_webhooks`, `webhook_spec` and
`webhook_signing`, `norm_w` against whether a unified-API vendor already normalises this service,
`sandbox_w` against `sandbox`.

The score is published with its components precisely so a reader can disagree with a weight rather
than with the ranking. A component nobody checks makes that transparency decorative, and a service
scoring 4 or more gets its own milestone — so a wrong weight moves a milestone.

**C23 — A bail's cause is the TRUE one, and it is observable**

`bail-1` and `bail-2` own the shape: a `skipped` record carries its `skip` block and no `service`
block. **You own whether the cause is the real one.** A service with a public API declined as having
none deletes a finding; a service declined as access-gated when the producer simply did not try is
the same deletion with a better excuse.

The `detail` must name what was actually checked — the URL that returned what, the page that asked
for a sales call. A cause with no observation behind it is a judgement wearing a typed value's
clothes.

**C24 — The body sections carry attributed, dated, quoted evidence**

`body-sections-1` and `body-sections-2` own presence: the three sections exist. **You own their
content.** `## Evidence` must quote the first-party source, attribute the quote, and carry the date
the quote was true; `## Integration surface` must bound its list rather than restate a vendor's
whole product catalogue; `## Cost to integrate` must name the components the complexity score sums,
so the score can be audited from the record alone.

A quote that does not support the claim above it is the same defect C10 names on the search output,
one artifact later.

**C25 — `rate_limit_documented: unchecked` means nobody looked, and the record says so**

The field is three-state deliberately: `documented`, `undocumented`, `unchecked`. A boolean here
would assert "not documented" wherever the truth is "nobody looked", and that is the failure the
third state exists to prevent.

**Judge which state is true.** `undocumented` is a claim about the vendor and needs the observation
behind it — the reference page that carries no numbers. `unchecked` is a claim about the survey and
is always honest. A record that writes `undocumented` because the producer did not reach the page
has converted its own gap into a finding about someone else.

**C26 — Both of lens 1's denominators are what was REACHED, not what was attempted**

`synthesis-2` and `synthesis-4` own the bound — neither ratio may exceed one. **You own the
denominators themselves.** `presence_denominator` is the catalogs actually walked, and
`a3_directories_reached` is the comparable products' directories actually reached — not the number
attempted, and not the number the map declared.

A denominator inflated to what was attempted deflates every ratio and moves services out of the
table-stakes set; deflated to the hits, it moves everything in. The register's `priority` is
re-derived from these two ratios, so a wrong denominator is a wrong build handoff, not a wrong
sentence.

**C27 — The auth base rate is a real measurement, with its source and its date**

Lens 4 reports the domain's auth distribution against a base rate, because "mostly OAuth2" is
unreadable without one. The base rate carries a `source` and an `as_of`, and it must be a
measurement someone could repeat — a catalog walked on a stated date, with its own denominator.

**A base rate carried over from an earlier survey without re-measuring is a finding**, and so is one
whose denominator does not match the catalog it names. *No rule owns this: the validator does not
fetch and cannot re-measure. It checks that the domain distribution sums to its own denominator,
and deliberately does not apply that sum to the base rate, which names the measured schemes and
need not be exhaustive.*

**C28 — Absence claims are search results, and their named limits are the true ones**

`absence-1` owns the receipt: every claim names the angles that ran and the terms searched. **You
own the phrasing and the limits.** "No third-party service for X surfaced across the angles that ran
and the terms searched, at their 2026-08 state" is a search result. "No integration exists" is a
claim about the world that no survey can support.

`named_limits` must carry the ones that actually bound this run — the commercial catalog's paging
bound where it was hit, the sources whose terms could not be verified. A limit list copied forward
without checking whether it bound THIS run is a receipt for someone else's search.

**C29 — `capability_tags` were checked against the project's capability map, before any tally**

The synthesis child's first deterministic check validates every tag against the project's
`capability-map.yaml`. **Confirm it ran and say what it returned.** *No rule owns this: the portable
validator structurally cannot see the project's scope files, so this belongs to the owning ticket's
QA — and a condition nobody discharges is a check nobody runs.*

A tag outside the map means either the tag is invented or the map is incomplete, and those are
different findings with different owners. Say which.

**C30 — The report does not re-score the register, and does not pick the roadmap**

`report.md` is the human half of one artifact pair. Every figure in it carries the extract record it
came from, and `complexity.score`, `priority` and `availability` are the register's — restating one
differently in prose leaves a reader with two answers and no way to tell which is current.

**And the report stops at the ecosystem.** Which integrations THIS product should build, and in what
order, is the downstream document's job working from the register. A report that picks the roadmap
has quietly replaced the decision it was meant to inform, and it does so in the voice of a survey.
