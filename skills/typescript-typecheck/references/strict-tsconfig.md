# Strict `tsconfig` — the full flag set (TypeScript 5.x)

Load this when writing or tightening a `tsconfig`.

## What `strict: true` turns on

`strict` is a meta-flag that enables the whole strict family at once. As of TS 5.x it switches on:

| Flag | What it does |
|---|---|
| `noImplicitAny` | Errors when a value's type is inferred as `any` instead of being annotated. |
| `strictNullChecks` | `null` and `undefined` are their own distinct types — you must handle them explicitly. The single most valuable flag. |
| `strictFunctionTypes` | Function parameter types are checked contravariantly (more correctly). |
| `strictBindCallApply` | `call`/`bind`/`apply` are checked against the function's real signature. |
| `strictPropertyInitialization` | A class property declared but never assigned in the constructor is an error (works with `strictNullChecks`). |
| `noImplicitThis` | Errors on a `this` whose type is an implicit `any`. |
| `useUnknownInCatchVariables` | `catch (e)` types `e` as `unknown`, not `any`. |
| `alwaysStrict` | Parses files in ECMAScript strict mode and emits `"use strict"`. |

These all default per the `strict` switch; setting `strict: false` (or omitting it) turns them all off.

## Recommended flags NOT enabled by `strict`

`strict` is the floor. Add these for a genuinely strict config — each is a real-bug catcher the strict family does not cover:

| Flag | What it does | Notes |
|---|---|---|
| `noUncheckedIndexedAccess` | Adds `undefined` to the result of index-signature and array access (`arr[i]` is `T | undefined`). | The biggest extra safety win; forces you to handle the missing-element case. |
| `noImplicitOverride` | A method that overrides a base-class method must use the `override` keyword. | Prevents silent drift when a base signature changes. |
| `noFallthroughCasesInSwitch` | A non-empty `case` must `break`/`return`/`throw`. | Control-flow completeness. |
| `noImplicitReturns` | Every code path in a function must return a value (when any path does). | Control-flow completeness. |
| `noUnusedLocals` | Errors on unused local variables. | Dead-code. |
| `noUnusedParameters` | Errors on unused parameters; names prefixed with `_` are exempt. | Dead-code. |
| `exactOptionalPropertyTypes` | An optional property `a?: string` no longer accepts an explicit `{ a: undefined }`. | **Add knowingly** — see caveat. |
| `verbatimModuleSyntax` | Emits imports/exports exactly per the `type` modifier you wrote; no import elision. | Requires `import type` on type-only imports. |

### `exactOptionalPropertyTypes` caveat

It is deliberately excluded from `strict`. With it on, `{ a?: string }` means "`a` may be absent" but NOT "`a` may be `undefined`". To allow an explicit `undefined`, widen the type to `a?: string | undefined`. Expect to touch optional-property call sites when enabling it — that churn is why it is opt-in.

### `verbatimModuleSyntax` interplay

It supersedes the deprecated `importsNotUsedAsValues` and `preserveValueImports`. With it on, an import without a `type` modifier is always emitted; an import that uses `import type` is always dropped. A type imported in value position will no longer be elided and can crash at runtime — so type-only imports must be written `import type { Foo } from "..."`. It pairs naturally with `isolatedModules`, which single-file transpilers (esbuild/SWC) require.

## The bundler module block (Vite / esbuild apps)

For an app a bundler consumes, the module-related options are:

```jsonc
{
  "module": "esnext",            // or "preserve"; NOT commonjs
  "moduleResolution": "bundler", // resolve like a bundler does
  "noEmit": true,                // tsc only checks; the bundler emits
  "allowImportingTsExtensions": true, // legal ONLY when noEmit/emitDeclarationOnly
  "verbatimModuleSyntax": true,
  "moduleDetection": "force",    // treat every file as a module
  "isolatedModules": true,       // single-file-transpiler safe
  "jsx": "react-jsx",            // automatic runtime; no `import React`
  "target": "ES2023",
  "lib": ["ES2023", "DOM", "DOM.Iterable"],
  "skipLibCheck": true
}
```

Hard constraints (verified against the TS module docs):

- `moduleResolution: "bundler"` requires `module` to be `esnext` or `preserve` (not `commonjs`). With `module: "preserve"`, `moduleResolution: "bundler"` is implied.
- `allowImportingTsExtensions: true` is only allowed when `noEmit` (or `emitDeclarationOnly`) is set, because `./x.ts` import paths would not resolve in emitted JS. The type-check-only setup satisfies this.
- For a Node library (not bundler-consumed) use `module`/`moduleResolution` `nodenext` instead.

## Shareable base configs

Rather than hand-maintaining the full list, extend a community-maintained base from the `@tsconfig/bases` collection:

- **`@tsconfig/strictest`** — `npm i -D @tsconfig/strictest`, then `"extends": "@tsconfig/strictest"`. It sets, among others: `strict: true`, `exactOptionalPropertyTypes`, `noFallthroughCasesInSwitch`, `noImplicitOverride`, `noImplicitReturns`, `noPropertyAccessFromIndexSignature`, `noUncheckedIndexedAccess`, `noUnusedLocals`, `noUnusedParameters`, `allowUnusedLabels: false`, `allowUnreachableCode: false`, `checkJs`, `esModuleInterop`, `skipLibCheck`, `forceConsistentCasingInFileNames`. (Confirm the current contents against the installed package — bases evolve.) Note `checkJs: true` means any `.js`/`.jsx` in scope is also type-checked; in a pure `.ts`/`.tsx` app that is a no-op, but override `"checkJs": false` if you intentionally keep unchecked JS.
- `extends` accepts a package name (resolved via `node_modules`) or a relative path; your `compilerOptions` override the base.

Recommended pattern: `extends` the strictest base, then layer the bundler module block above on top.

## Worked strict `tsconfig.app.json` (Vite React app)

```jsonc
{
  "extends": "@tsconfig/strictest/tsconfig.json",
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2023",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "noEmit": true,
    "types": ["vite/client"]
  },
  "include": ["src"]
}
```

> This leaf config is referenced by the solution `tsconfig.json` (see `references/vite-split-config.md`) and uses `noEmit: true` — it is type-checked, not emitted. Do **not** add `composite: true` to a `noEmit` app config that is bundled (not consumed by another TS project): `composite` forces declaration emit, which clashes with `noEmit` (TypeScript historically rejected a referenced project disabling emit; current versions allow the create-vite shape, but the simplest robust rule is *`composite` for a project whose `.d.ts` another project imports; `noEmit` for the bundled app leaf*). Reserve `composite: true` for a package that is genuinely imported by another package — see `references/project-references.md`.

> **Verify, don't assume.** A freshly scaffolded `tsconfig.app.json` is not guaranteed to contain `strict: true` (the create-vite template's exact flag set has shifted across versions). Open the generated file and confirm `strict` is present, or `extends` a strictest base as above so it cannot be missing.
