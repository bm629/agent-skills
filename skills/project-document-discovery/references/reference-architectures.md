# Reference Architectures — Capability Identification

Reference file for `project-document-discovery` Phase A Step 2.
Load at the start of Step 2 (capability identification). Do not load in Phase B.

---

## 4-Signal Identification Algorithm

Apply the signals in order. Stop when you have 4–10 L1 candidates. Later signals
supplement earlier ones — do not discard Signal 1 results before trying Signal 2.

### Signal 1 — Domain reference architecture (highest confidence)

Classify the domain using `domain.primary` from the classification you produced in
Step 1. Look up the canonical capability decomposition below.

**If the domain matches a row in the reference table:**
1. ADOPT the canonical L1 list as your starting decomposition.
2. TRIM — remove any area the project idea does not describe or imply.
3. AUGMENT — add any capability the idea names that is missing from the reference list.
4. Proceed to sizing tests.

**If the domain is novel or not in the table:** proceed to Signals 2–4 and use the
reference table only as inspiration.

#### Reference Architecture Table

| Domain | Canonical L1 capability areas |
|---|---|
| `e-commerce` | Catalog · Cart · Checkout · Payments · Orders · Accounts · Search · Admin |
| `fintech/neobank` | Accounts · Payments · Cards · KYC/Identity · Lending · FX · Compliance · Notifications |
| `healthcare` | Patient Records · Scheduling · Clinical · Billing/RCM · Patient Portal · Reporting · Admin |
| `b2b-saas` | Workspace · Identity/Auth · Core Product · Billing · Notifications · Admin · Integrations |
| `marketplace` | Listings · Discovery · Transactions · Reviews · Messaging · Payments · Admin · Trust & Safety |
| `developer-platform` | Repository · CI/CD · Issues · Packages · Deployments · Security · Billing · Admin |
| `edtech` | Courses · Enrollment · Learning · Assessment · Progress · Notifications · Billing · Admin |
| `logistics/delivery` | Orders · Routing · Dispatch · Tracking · Fleet · Delivery · Billing · Admin |
| `social/community` | Profiles · Feed · Messaging · Notifications · Moderation · Groups · Analytics · Admin |
| `productivity-tool` | Workspace · Documents · Collaboration · Integrations · Billing · Admin |

**Reading the table:** each bullet is a candidate L1 capability area name. These are
typical decompositions for a mid-sized product — a small MVP may use 4–5; a mature
product may use all. Trim aggressively for greenfield projects. The names are
suggestions; rename to match the project's vocabulary.

---

### Signal 2 — Pivotal domain events

Extract the most significant state transitions from `idea.md`.
Examples: "Order Placed", "Payment Confirmed", "User Registered", "Item Listed".

**How to use:** Each pivotal event is a boundary. The capability to the **left** of
the event owns what happens before the event fires. The capability to the **right**
owns what happens after. An event that crosses two named areas in your Signal 1 list
confirms the boundary between them.

**Example** (e-commerce):
- "Order Placed" → boundary between Cart (left) and Orders (right)
- "Payment Confirmed" → boundary between Checkout/Orders (left) and Fulfillment (right)
- "Item Reviewed" → boundary between Delivery (left) and Reviews (right)

Use this signal to: (a) validate Signal 1 boundaries, (b) discover missing areas the
reference table omitted, (c) split an over-broad area the idea implies has multiple
distinct state transitions.

---

### Signal 3 — Core domain nouns

Extract the primary nouns from `idea.md`. A noun cluster maps to the capability area
that **custodies** (owns) that entity.

**Procedure:**
1. List every significant noun: Product, Order, User, Payment, Cart, Listing, Review…
2. Group nouns that belong to the same entity cluster (e.g. Cart ↔ CartItem ↔ Coupon).
3. Each cluster → one candidate capability area (the one that owns all entities in the cluster).
4. Nouns that appear in multiple clusters become `refs` (cross-capability references),
   not a reason to merge the clusters.

**Example** (marketplace):
- Listing, ListingPhoto, ListingVariant → Listings capability
- Buyer, SellerProfile → Accounts/Profiles capability
- Transaction, Escrow, Payout → Transactions capability
- Rating, Review → Reviews capability

---

### Signal 4 — Jobs-to-be-done

Map the user's jobs from `idea.md` (what is the user trying to accomplish?).
Each distinct job cluster → one capability area.

**Procedure:**
1. Identify user types (buyer, seller, admin, support agent…).
2. For each user type, list their primary jobs (list a product, search for items,
   complete a purchase, track an order, review a seller…).
3. Group jobs that share the same user motivation and data context.
4. An area that mixes two unrelated jobs should be split.

**Example** (marketplace):
- "I want to list my item for sale" → Listings capability
- "I want to find what I'm looking for" → Discovery/Search capability
- "I want to pay and receive my item" → Transactions + Payments capabilities (separate jobs)
- "I want to know my order status" → Tracking/Orders capability

**Tip:** If Signal 1 gave you a decomposition, use Signal 4 to validate it. A reference
architecture area with no corresponding job in the idea is a candidate for trimming.

---

## Three Sizing Tests

Apply these after identification. Every L1 candidate must pass all three tests.
If a candidate fails any test, split it. If a candidate is ambiguous, add an L2
sub-capability (set `parent` to the L1 id).

### Test 1 — Single-team test

> Can a single cross-functional team own this capability end-to-end — its backlog,
> its data, its API, and its UI — without constant negotiation with another team?

**Pass:** yes, one team, one backlog, one data boundary.
**Fail:** the area mixes concerns that clearly require two separate teams (e.g. a
"Checkout + Fulfillment" area merges pre-payment and post-payment flows that typically
have separate team ownership). Split on the team boundary.

---

### Test 2 — Single-reason-to-change test

> Does this capability change for exactly ONE business reason?

**Pass:** adding a new payment method only touches Payments; adding a new product type
only touches Catalog.
**Fail:** a single business requirement (e.g. "add subscriptions") requires changes to
Billing, Notifications, and Orders simultaneously → those three are too entangled; one
of them needs to absorb subscriptions or a new Subscriptions area is warranted.

---

### Test 3 — Authoring-turn test

> Can the scope statement of this capability be stated in one sentence WITHOUT the
> word "and" connecting two unrelated concerns?

**Pass:** "Catalog manages product listings — items, variants, and pricing; does NOT
handle inventory levels or order fulfillment."
**Fail:** "Orders and Fulfillment manages order lifecycle and shipment coordination and
warehouse picking." — three concerns, two "and"s. Split into Orders + Fulfillment.

**When a capability fails Test 3 but Tests 1–2 pass:** add an L2 sub-capability rather
than a full split. Set `parent` to the L1 id. The L1 scope statement becomes the
aggregate; the L2 records carry the atomic scope statements.

---

## Capability Count Guidance

| Count | Interpretation |
|---|---|
| < 4 | Too coarse — areas are over-broad; each likely fails Test 3 |
| 4–6 | Typical for a focused MVP or internal tool |
| 7–10 | Typical for a consumer product or multi-persona platform |
| > 10 | Over-decomposed — merge areas with strong coupling; stop adding L1s, add L2s instead |

**Target:** 4–10 L1 capability areas per project. Below 4 = likely under-decomposed;
above 10 = the manifest will produce too many document sets. If you have 11–12, look
for two areas that share a team and merge them.

---

## Seam Contract Filling Guide

After identifying capability areas, fill the seam contract fields for each record.
The brief for Phase A Step 2 requires ALL required fields and recommends all optional
fields where information is available in `idea.md`.

### `owns` — entity custody

List the primary entities this capability custodies (creates, persists, and is the
authoritative source for). Use `kebab-case` names. Minimum 1.

```yaml
# Checkout capability owns:
owns: [order-draft, payment-intent, applied-coupon]
```

### `refs` — cross-capability entity references

List entities this capability reads but does NOT own. Use `{capability-id}.{entity-name}`
dot-notation. These become FK references in the data model.

```yaml
# Checkout refs Cart's items and Catalog's product:
refs: [cart.line-items, catalog.product]
```

### `publishes` and `consumes` — domain event contracts

Events use `{capability-id}.{event-name}` dot-notation. Use past-tense event names.

```yaml
# Checkout publishes when state changes:
publishes: [checkout.order-placed, checkout.payment-initiated]
# Checkout consumes from upstream capabilities:
consumes: [inventory.stock-reserved, payments.payment-confirmed]
```

### `entry_points` and `exit_points` — navigation seam

Entry points: how users or systems ARRIVE at this capability.
Exit points: where users GO after completing a flow here.
These seed the wireframes for cross-capability navigation contracts.

```yaml
# Cart entry/exit:
entry_points:
  - "Product detail page — Add to cart button"
  - "Persistent cart badge in top nav"
exit_points:
  - "Proceed to Checkout CTA → Checkout capability"
  - "Continue shopping → back to Catalog"
```

### `depends_on` — DAG ordering

List capability IDs that must be processed BEFORE this capability in the document DAG.
Used for produce-docs ordering (feature-spec of a depends_on capability is produced first).

```yaml
# Checkout depends on Cart and Catalog being specced first:
depends_on: [cart, catalog, payments]
```

### Fan-out flags — document generation triggers

| Flag | Set to `true` when… | Documents generated |
|---|---|---|
| `has_ui` | the capability has any screen, modal, or UI surface | `wireframes-{id}` + `user-flows-{id}` + (if ui_complexity) `hi-fi-{id}` |
| `has_api` | the capability exposes or consumes an HTTP/async API | `api-spec-{id}` |
| `has_persistence` | the capability owns data that must be stored durably | `data-model-{id}` |
| `has_model` | the capability trains or serves an ML model | `model-card-{id}` (and selects the system `eval-plan`) |

Set the relevant flags for typical full-stack capabilities. A pure event-relay capability
may have `has_ui: false, has_api: true, has_persistence: false`. Set `has_model: true` only
for capabilities that own a model artifact (its training/serving), not those merely consuming
predictions.

### `ui_complexity` — hi-fi threshold

| Value | When to use |
|---|---|
| `simple` | Admin tables, settings pages, dashboards with no interaction complexity |
| `moderate` | Standard CRUD forms with validation, multi-step flows |
| `complex` | Rich interactions, drag-and-drop, real-time updates, configurators |
| `consumer-grade` | Public-facing consumer UX; high visual polish and brand expression required |

Hi-fi (`hi-fi-{id}`) is generated only when `has_ui: true` AND `ui_complexity` in
`["complex", "consumer-grade"]`. Simple and moderate capabilities get wireframes only.

### `impl_complexity` — technical-design threshold

Backend/algorithmic implementation complexity — distinct from `ui_complexity` (UI
richness). A polished but CRUD-only capability is `simple` here regardless of how rich
its screens are; its design is fully captured by feature-spec + data-model + api-spec.

| Value | When to use |
|---|---|
| `simple` | Trivial CRUD/config: thin pass-throughs, settings, basic forms-to-DB with no real logic |
| `moderate` | Standard service logic: validation, orchestration of a few steps, typical business rules |
| `complex` | Non-trivial algorithms, concurrency, state machines, performance-critical paths, intricate integrations |

Technical-design (`technical-design-{id}`) is generated when `impl_complexity` in
`["moderate", "complex"]`. A `simple` (or unset) capability gets no TDD — there is no
bespoke implementation design to record beyond its feature-spec/data-model/api-spec.
