# Classification schema reference (capability_map v2)

Reference for `project-document-discovery` Phase A Step 1. The 10 model-provided
classification clusters + the 10 derived `prior_art_triggers`. **Load at Step 1.**
Single-sourced with `schemas/capability-map.schema.json` (the deterministic gate)
and `reviewing-document-discovery`. Enum tokens are research-grounded; emit them
**verbatim**. The schema is **strict** — unknown cluster fields are rejected, and the
`[required]` / `[trigger]`-input fields below must be present.

---

## The 10 clusters

### 1. `archetype`  *(required: primary)*
- `primary` `[required]` enum (no canonical standard — a pragmatic synthesis): `web-app · api-service · cli-tool · data-pipeline · mobile-app · library-sdk · desktop-app · embedded-iot · ml-service · browser-extension · game · infra-platform · agent-automation`
- `secondary` list of the same; `lifecycle_stage`: `incubate · invest · sustain · sunset`

### 2. `domain`  *(required: audience)*
- `primary` free-text (e-commerce, fintech, …); `secondary` list
- `audience` `[required][trigger:user_research]`: `b2c · b2b · b2b2c · developer · internal`
- `consumer_facing`, `open_to_public`: bool

### 3. `regulatory`  *(required: applies)*
- `applies` `[required][trigger:regulatory]`: bool
- `frameworks` list; per-regime flag groups (open): `data_privacy {gdpr,ccpa,coppa,pipeda}`, `financial {pci_dss,aml_kyc,mifid2,sec_cftc,mica}`, `health {hipaa,fda_samd,iec_62304,gxp}`, `government {fedramp,fisma,section_508}`, `safety_critical {iec_61508,iso_26262,do_178c}`, `ai_governance {eu_ai_act_risk}`, `export_control {itar,ear}`, `standards {soc2,iso_27001,wcag_level}`, `supply_chain {sbom_required}`

### 4. `scale`  *(required: concurrency, real_time, availability_target, geo_distribution, data_volume — all trigger:scale inputs)*
- `concurrency`, `throughput`: `low · medium · high · extreme`
- `real_time`: `none · soft · near · hard`
- `availability_target`: `"99.0" · "99.9" · "99.95" · "99.99" · "99.999"` (the nines ladder)
- `consistency`: `eventual · strong · linearizable`
- `geo_distribution`: `single-region · multi-region · global · edge`
- `data_volume`: `small · medium · large · extreme`
- `burst_traffic`, `latency_sensitive`, `stateful`: bool

### 5. `security`
- `asvs_level`: `1 · 2 · 3` (OWASP ASVS)
- `data_sensitivity`: `{ level: public·internal·confidential·restricted, has_pii, has_phi, has_payment_data, has_credentials, has_biometric, classified_data }`
- `auth_complexity`: `none · simple · mfa · sso-federated · zero-trust`
- `authz_complexity`: `none · rbac · abac · multi-tenant-isolation`
- `external_attack_surface` {has_public_api, has_file_upload, has_webhooks, accepts_user_content}; `supply_chain_risk` low·medium·high; `pen_test_required` bool

### 6. `integrations`  *(required: expected, complexity — trigger:integrations inputs)*
- `expected`: bool; `complexity`: `none · minimal · moderate · complex`
- `categories` {payments, identity, communication, data_providers, analytics, …}; `patterns` {synchronous_rest, async_messaging, batch_etl, streaming, sdk_embedded}; `third_party_list` list

### 7. `ui`  *(required: has_ui, complexity)*
- `has_ui` `[required][trigger:visual]`: bool
- `complexity` `[required][trigger:user_research]`: `none · minimal · simple · complex · consumer-grade`
- `target_users`: `developer · internal · business-user · consumer · mixed`
- `accessibility {required_level: A·AA·AAA}`; `mobile`, `i18n`, `multi_tenancy_ux`, `design_system` flag groups

### 8. `data_ml`  *(required: ml_involvement)*
- `ml_involvement` `[required][trigger:ml]`: `none · uses-pre-trained · fine-tunes · trains-from-scratch · multi-model`
- `has_data_pipeline` bool; `pipeline_type`: `none · batch · streaming · lambda · kappa · lakehouse`; `data_volume_class`: `none · transactional · analytical · big-data`
- `model_serving` bool; `eu_ai_act {applies, risk_level: unacceptable·high·limited·minimal}`; `model_governance`, `data_governance`, `responsible_ai` flag groups

### 9. `infrastructure`
- `deployment_model`: `local · cloud · multi-cloud · hybrid · on-premises-option · edge`
- `compute_paradigm`: `serverless · container · vm · bare-metal · managed-service · mixed`
- `cloud_providers`, `managed_services` lists; `multi_region`, `edge_computing`, `on_premises_option`, `iac_required` bool; `data_residency`, `observability`, `dr` flag groups

### 10. `business`  *(required: platform)*
- `model`: `saas · marketplace · ecommerce · open-source · internal-tool · platform · api-product · consumer-app · enterprise-software`
- `platform` `[required]`: `{ type: none·marketplace·app-store·dev-platform·social-network·payments-network·data-platform·media (trigger:platform_ecosystem), two_sided, network_effects, third_party_developers }`
- `open_source {is_oss, license_type (SPDX id), has_cla}`; `distribution`, `commercialization` flag groups

---

## `prior_art_triggers` — author the 10 booleans (do NOT omit)

After classifying clusters 1–10, **compute and emit** `prior_art_triggers` by applying these formulas to the classification you just produced. The deterministic validator recomputes them and FAILS on any mismatch, so apply them faithfully. Absent input ⇒ not-in-set ⇒ that disjunct is false.

```
code               = true                                          (always)
visual             = ui.has_ui
market_competitive = true                                          (always)
user_research      = (ui.has_ui AND domain.audience in {consumer, b2c, b2b2c})
                     OR ui.complexity in {complex, consumer-grade}
security           = true                                          (always)
ml                 = data_ml.ml_involvement != "none"
regulatory         = regulatory.applies
scale              = scale.concurrency in {high, extreme}
                     OR scale.real_time in {near, hard}
                     OR scale.availability_target in {"99.99", "99.999"}
                     OR scale.geo_distribution in {multi-region, global, edge}
                     OR scale.data_volume in {large, extreme}
integrations       = integrations.expected AND integrations.complexity in {moderate, complex}
platform_ecosystem = business.platform.type != "none"
```

Emit all 10 as booleans (plus optional `_derived: true`):
`code, visual, market_competitive, user_research, security, ml, regulatory, scale, integrations, platform_ecosystem`.

These gate the downstream Prior Art Phase (one research job per flag set true). Do not confuse this block (the boolean gates) with the prior-art research itself (a later phase).
