# Enforcement and tooling

## Default: convention-only

TSDoc compliance is a **convention** by default. A code linter/formatter such as Biome lints and formats *code*; it does **not** validate doc-comment *content* against the TSDoc spec. (The closest Biome gets is `useSingleJsDocAsterisk`, a formatting rule about leading asterisks, plus tracking `{@link}` references when computing unused imports — neither checks TSDoc conformance.) So the standard is upheld by this skill's discipline plus review, with no extra tooling and no second linter.

## Optional CI validation: `eslint-plugin-tsdoc`

For a project that wants CI to mechanically validate doc-comment syntax, the official tool is **`eslint-plugin-tsdoc`** (maintained by Microsoft as part of the TSDoc project). It exposes a single rule, **`tsdoc/syntax`**, which validates that a doc comment conforms to the TSDoc spec (e.g. flags an unrecognized tag, a missing `@param` hyphen, `@return` instead of `@returns`).

Minimal flat-config sketch:

```js
// eslint.config.js
import tsdoc from "eslint-plugin-tsdoc";

export default [
  {
    files: ["**/*.ts", "**/*.tsx"],
    plugins: { tsdoc },
    rules: {
      "tsdoc/syntax": "warn",
    },
  },
];
```

Legacy `.eslintrc` form: add `"eslint-plugin-tsdoc"` to `plugins` and set `"tsdoc/syntax": "warn"`.

### The trade-off — read before adopting

`eslint-plugin-tsdoc` **requires ESLint**. A project that deliberately uses a single fast linter (e.g. Biome, chosen precisely to avoid running ESLint + Prettier) would, by adopting this plugin, **reintroduce ESLint alongside that linter** — exactly the two-linter situation a single-tool setup was meant to avoid. That is a real cost: a second toolchain, a second config, a second CI step, and overlapping responsibilities.

So this is an **opt-in pointer, not the default**. Adopt `tsdoc/syntax` only when CI syntax-validation of doc-comments is an explicit, accepted requirement and the team has decided the second linter is worth it. Otherwise stay convention-only.

## Out of scope (pointers only)

- **TypeDoc** — the tool that **consumes** TSDoc comments to generate an HTML/Markdown API documentation site. TSDoc comments are TypeDoc's *input*; this skill writes those comments. Setting up and configuring a generated doc site is a separate concern and is out of scope here (a one-line pointer, not a tutorial) — disproportionate for a small app.
- **Storybook** — an interactive component-catalog / docs tool. Also out of scope; a pointer only, not part of the doc-comment convention.
