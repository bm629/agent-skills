# The Vite split-config layout + the type-check scripts

Load this when setting up a Vite TypeScript app's type-check gate.

## Why three tsconfig files

A Vite TS app's code runs in two different environments — the browser (`src/`, needs the DOM lib) and Node (`vite.config.ts` and other build tooling, needs the Node lib). One tsconfig cannot describe both, so the scaffold splits them and ties them together with project references:

- **`tsconfig.json`** — the *solution* file. It contains almost nothing: `"files": []` and a `"references"` array pointing at the two leaf configs. It is the entry point for `tsc -b`.
- **`tsconfig.app.json`** — the app/browser config: `src/`, DOM lib, `moduleResolution: "bundler"`, `noEmit`. (See `references/strict-tsconfig.md` for the strict version.)
- **`tsconfig.node.json`** — the build-tooling config: `vite.config.ts`, Node lib, `composite: true`.

### The solution `tsconfig.json`

```jsonc
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

### `tsconfig.node.json` (the build-tooling leaf — Node environment)

```jsonc
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "target": "ES2023",
    "lib": ["ES2023"],
    "module": "nodenext",       // build tooling runs in Node, not the bundler
    "types": ["node"],
    "noEmit": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "skipLibCheck": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

> Both leaf configs use `noEmit: true` and **neither is `composite`** — they are pure type-check targets. A solution `tsconfig.json` can reference `noEmit` projects in current TypeScript; `tsc -b` walks them and checks each. Reserve `composite: true` for a package whose emitted `.d.ts` another package imports (see `references/project-references.md`), not for these bundled/no-emit leaves. The Node leaf uses `module: "nodenext"` (it runs in Node), while the app leaf uses the bundler block.

## The scripts

In `package.json`:

```jsonc
{
  "scripts": {
    "build": "tsc -b && vite build",
    "typecheck": "tsc -b --noEmit"
  }
}
```

- `build` runs the type-check (`tsc -b`) *before* the bundle. The `-b` (build mode) flag is what makes `tsc` honor the `references` graph and check `vite.config.ts` too — a bare `tsc` would not.
- `typecheck` is the **standalone gate** — the same `tsc -b` check with no build. This is what CI runs (see `references/ci-gate.md`). Keeping it separate from `build` means CI fails on a type error even when the bundle would have succeeded.

> The leaf configs set `noEmit`, so `tsc -b` here produces no JS — it is type-checking only. (`--noEmit` on the script is belt-and-suspenders given `noEmit` in the configs.) The build artifacts come from `vite build`, not from `tsc`.

## `vite-plugin-checker` — the dev complement

`vite-plugin-checker` runs `tsc` (and optionally ESLint, Biome, Stylelint, `vue-tsc`) in a worker thread during `vite dev`/`vite build`, overlaying type errors in the browser and printing them in the terminal as you edit — fast feedback without leaving the dev server.

```ts
// vite.config.ts
import { defineConfig } from "vite";
import checker from "vite-plugin-checker";

export default defineConfig({
  plugins: [checker({ typescript: true })],
});
```

> **It is a complement, not the gate.** `vite-plugin-checker` gives developer-loop and editor feedback; it does not replace the authoritative `tsc --noEmit` step in CI. Use both: the plugin for speed while coding, the `typecheck` script for the enforced gate. A green dev server is not proof CI will pass.
