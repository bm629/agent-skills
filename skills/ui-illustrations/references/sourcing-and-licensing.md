# Sourcing and licensing

Load when picking an illustration source, checking license terms, or handling
attribution / generated-art questions.

## The landscape (2026)

| Source | Style | Animated? | License posture (snapshot 2026-07-11 — RE-CHECK AT ADOPTION) |
|---|---|---|---|
| **unDraw** | One consistent flat family, hundreds of concepts, on-site primary-color picker | No | Commercial + modification OK; **no attribution**; NO pack redistribution, NO competing service, NO AI-training use |
| **Storyset (Freepik)** | Several families (Rafiki/Bro/Amico/Pana), richer scenes, on-site color + animation editor | Yes (animated SVG/Lottie export) | Free tier: commercial OK **with visible attribution** ("Designed by Freepik" + link, clearly findable); a paid Freepik-company subscription removes it (the terms currently name Flaticon Premium while help docs say Freepik Premium — confirm which on the live terms at adoption); no resale/redistribution, no trademark/logo use |
| **LottieFiles free (Lottie Simple License)** | Community-made motion assets, mixed styles | Yes (Lottie JSON) | Commercial + modification OK; no required attribution (credit encouraged); **modifications are share-alike**; no compiling into competing collections. Marketplace assets carry different paid terms — check per asset |
| Icon systems (lucide, Heroicons…) | Glyphs, not scenes | — | Different asset class — not illustration; use the icon convention |
| Paid/custom (ui8 packs, commissioned) | Anything | Either | Per-vendor terms; strongest style control; named for awareness |
| AI-generated | Unbounded | Either | Caveats: style drift across generations, licensing/provenance ambiguity, uncanny details in character art. A deliberate choice, not the default |

## The decision path

1. Static product-UI illustration → **unDraw** (style consistency + zero obligations).
2. Animation earns its place (an empty state worth delight, onboarding) → **LottieFiles**
   (no attribution) or **Storyset** (if the richer scene style fits and attribution is
   acceptable or a paid seat exists).
3. Nothing fits the concept → nearest in-family metaphor beats an off-family exact match
   (style rule); custom/commissioned art when the product outgrows libraries.

## The record-the-license practice (durable; terms drift)

License terms on free platforms change — the table above is a dated snapshot. At
adoption time:

1. Open the source's **live license page** and confirm the terms.
2. Record next to the asset — an `assets/illustrations/LICENSES.md` with one line per
   asset: filename, source URL, license name/summary, attribution required (and where
   it ships), date checked.
3. If attribution is required, wire it **now** (visible, findable — a credits/about
   surface linked from where the art appears satisfies "clear and visible"; a buried
   footnote does not) — it is a shipping requirement.

## Attribution mechanics (when required)

- Expected form (Freepik/Storyset): the phrase they specify (e.g. "Designed by
  Freepik") with a link, in a location an end user can actually find.
- One consolidated credits line/page covering all assets from a source is fine;
  per-image captions are not required unless the license says so.
- Removing attribution = moving to the paid tier or swapping the asset — never just
  deleting the credit.

## What every listed source prohibits

- Redistributing the assets as packs/collections or building a competing library.
- (unDraw explicitly) using assets to train AI models.
- (Storyset/Freepik) use in trademarks/logos.

Using assets *inside your product* is what these licenses exist for; the traps are all
about re-publishing the assets themselves.
