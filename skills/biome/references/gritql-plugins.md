# Authoring custom rules — GritQL plugins

Load when writing a custom lint rule that no built-in rule covers. Biome v2 lets you express custom checks as GritQL plugins (`.grit` files) without building a Rust rule.

## Register the plugin

In `biome.json`, list plugin file paths under `plugins`:

```jsonc
{ "plugins": ["./plugins/no-object-assign.grit"] }
```

Files must use the `.grit` extension. Plugins currently target **JavaScript and CSS only**.

## GritQL pattern basics

A plugin matches a code structure and reports a diagnostic. Core syntax:

- `$variable` — captures a node; `$args` / `$...` — variadic, matches a list of nodes (e.g. call arguments).
- `pattern as $name` — bind the whole matched node to `$name` (use it as the diagnostic `span`).
- `$var <: pattern` — constrains `$var` to match `pattern`.
- backticks wrap a literal code pattern, e.g. `` `Object.assign($args)` ``.
- `where { ... }` — attach constraints and actions.
- `register_diagnostic(...)` — report a violation.

## Complete example — flag `Object.assign()`

```grit
`Object.assign($args)` as $call where {
    register_diagnostic(
        span = $call,
        message = "Prefer object spread instead of `Object.assign()`"
    )
}
```

The backtick pattern matches the call expression; `as $call` binds the whole match so the diagnostic underlines the entire call (not just the callee). `$args` is the variadic matcher for the call arguments.

## `register_diagnostic(...)`

| Arg | Required | Notes |
|---|---|---|
| `span` | yes | The syntax node to attach the diagnostic to. |
| `message` | yes | The diagnostic text. |
| `severity` | no | `hint` \| `info` \| `warn` \| `error` (default `error`). |

## Limitations

- Target languages: JavaScript and CSS only (currently).
- Prefer a built-in rule (the rule groups in `config.md`) when one fits; use a plugin only for genuinely project-specific checks.
- GritQL evolves; verify advanced pattern syntax against the current Biome docs.
