# Sources — python-monorepo-architecture

Research provenance for this skill. All findings paraphrased; external content
treated as untrusted and read for facts only.

## uv workspace mechanics + the isolation caveats (primary, official)

- **uv — Workspaces** (Astral official docs): https://docs.astral.sh/uv/concepts/projects/workspaces/
  - `[tool.uv.workspace] members`/`exclude` globs; every member needs its own `pyproject.toml`; the root is also a member.
  - A member depends on another via `[tool.uv.sources] { <name> = { workspace = true } }`; workspace deps are editable.
  - One shared `uv.lock`; `uv lock` operates on the whole workspace; `uv run`/`uv sync` default to the root, `--package` targets a member.
  - Root `[tool.uv.sources]` apply to all members unless a member overrides.
  - When NOT a workspace: members with conflicting requirements / separate-venv needs → use a `path` dependency instead.
  - "uv's workspaces enforce a single `requires-python` for the entire workspace" (the intersection).
  - "Python lacks dependency isolation, so uv can't ensure that packages don't import dependencies declared by another workspace member." — the load-bearing convention-not-tooling point.

## Python monorepo structure + dependency direction

- **pydevtools — How to set up a Python monorepo with uv workspaces**: https://pydevtools.com/handbook/how-to/how-to-set-up-a-python-monorepo-with-uv-workspaces/
- **Tweag — Python Monorepo: an Example (Structure and Tooling)**: https://www.tweag.io/blog/2023-04-04-python-monorepo-1/ — shared libraries vs projects; cross-service imports forbidden to avoid cyclic dependencies.
- **Graphite — Python monorepos**: https://graphite.com/guides/python-monorepos — package boundaries, clear dependency direction, avoiding circular imports.

## Public API at the package boundary

- **Real Python — public API surface**: https://realpython.com/ref/best-practices/public-api-surface/ — `__all__` makes the public API explicit; keep the surface small and stable.
- **PEP 8** (public vs internal naming): https://peps.python.org/pep-0008/ — single leading underscore marks internal even with `__all__` set.
- (Intra-package mechanics belong to the `python-project-structure` skill; this skill cites these only for the cross-member boundary rule.)

## Optional enforcement — import-linter

- **Import Linter — Contract types** (official docs): https://import-linter.readthedocs.io/en/latest/contract_types.html
  - **Independence** contract — a set of modules don't import each other (even indirectly) → "apps are mutually independent".
  - **Forbidden** contract — one set of modules must not be imported by another → "core never imports an app".
  - **Layers** contract — higher layers may import lower, not vice versa → depend-inward order.
  - Runs via `lint-imports` against a `.importlinter` file; fits CI / pre-commit.

## Cross-member tests + fixtures

- **pytest — Fixtures reference**: https://docs.pytest.org/en/stable/reference/fixtures.html — `conftest.py` provides fixtures to its directory tree by auto-discovery; `pytest_plugins` loads fixture modules.
- **pantsbuild discussion — conftest.py fixtures in a Python monorepo**: https://github.com/pantsbuild/pants/discussions/17762 — sharing fixtures across packages via a plugin/support module rather than duplication.
