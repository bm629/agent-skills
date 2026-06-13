# Internationalization & RTL

Depth for the Layout & internationalization conventions method. Make the system localization-ready even if it ships single-locale; a stated single-locale tool may scope this out **explicitly** (never silently).

## Text expansion

Translations run longer — Arabic up to ~**+25%** vs English, German similar. Layouts use **flexible containers**, never fixed-width text; leave headroom in components that hold copy (buttons, labels, badges).

## Logical CSS properties

Use **logical** properties (`margin-inline`, `padding-inline`, `inset-inline`, `border-inline`) instead of physical (`margin-left`/`right`) so layout mirrors automatically for RTL. Bake this into the spacing/layout foundations.

## RTL / bidi

Support right-to-left scripts (Arabic, Hebrew): mirror layout, support bidirectional content. State the mirroring approach in the layout conventions.

## Locale typography

Locale-specific font stacks / type tokens — Latin fonts often don't render Arabic/CJK well; adjust line-height per script.

## Formatting

Locale-aware numbers, dates, currency, and numbering systems.

## Scope (proportional)

A public multi-market product needs the full treatment; a stated single-locale internal tool legitimately scopes i18n out — but the scope-out is **explicit** in the doc, not a silent omission.
