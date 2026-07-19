---
schema_version: 1
repo_id: github__freqtrade__freqtrade
code_repository: https://github.com/freqtrade/freqtrade
verdict: borrow-architecture
score: 9
license: GPL-3.0-only
key_deps:
  - pkg:pypi/ccxt
  - pkg:pypi/sqlalchemy
  - pkg:pypi/pandas
  - pkg:pypi/python-telegram-bot
capability_tags:
  - strategy-engine
  - backtesting
  - exchange-integration
  - trade-persistence
pattern_names:
  - resolver-plugin-loading
  - abstract-strategy-interface
  - mixin-composition
extracted_at: 2026-07-19T00:00:00Z
---
## Core abstractions

Three load-bearing types. `FreqtradeBot` (`freqtrade/freqtradebot.py:73`) is the
orchestrator — `__init__` wires config, exchange, and persistence; `process()`
(`:257`) is the one trading-loop tick, with `enter_positions()` (`:613`) and
`exit_positions()` (`:1309`) as the two sides of the trade lifecycle. `IStrategy`
(`freqtrade/strategy/interface.py:51`) is the user-facing ABC every strategy
subclasses. The `resolvers/` package (`exchange_resolver.py`,
`strategy_resolver.py`, `pairlist_resolver.py`, `protection_resolver.py`,
`freqaimodel_resolver.py`, all over a shared `iresolver.py`) is the dynamic-loading
layer that turns config strings into live objects.

## Architectural pattern

A resolver-based plugin architecture around a single synchronous trading loop.
Every swappable concern — exchange, strategy, pairlist, protection, ML model —
has its own resolver subclassing `iresolver.py`, so the bot core never imports a
concrete implementation; config names it, the resolver loads it. The strategy
contract itself is a template-method ABC: `populate_indicators` /
`populate_entry_trend` / `populate_exit_trend` (`interface.py:229,247,266`) are
the required hooks, and a large set of optional `custom_*` overrides
(`custom_stoploss:442`, `custom_roi:473`, `custom_entry_price:502`,
`custom_stake_amount:621`) let a strategy intervene at precise points without
touching the loop. Composition is via mixins (`IStrategy(ABC, HyperStrategyMixin)`,
`FreqtradeBot(LoggingMixin)`).

## Solved well

Extension without forking: the resolver + ABC pairing means a user drops a strategy
file in and names it in config — no core change, no plugin registry to mutate.
Exchange abstraction is delegated wholesale to `ccxt` rather than re-implemented,
so the exchange layer (`freqtrade/exchange/`) is adapter code, not protocol code.
The optional-hook design degrades gracefully: a minimal strategy implements three
methods; an advanced one overrides fifteen.

## Solved poorly

`freqtradebot.py` is a very large orchestrator module (the trade lifecycle,
position adjustment, and exit logic all live in one class spanning 1300+ lines) —
`process()`, `enter_positions()`, `process_open_trade_positions()`, and
`exit_positions()` are all methods of the same object, so the loop's concerns are
co-located rather than separated. The `populate_buy_trend`/`populate_sell_trend`
pair (`:238,256`) survives alongside the newer `entry`/`exit` naming (`:247,266`)
as a deprecation shim, and `custom_sell` (`:558`) alongside `custom_exit` (`:590`)
— a naming migration carried in the public interface.

## Trusted dependencies

Pinned exactly in `requirements.txt`: `ccxt` (exchange abstraction — the single
highest-leverage dependency choice), `SQLAlchemy` 2.x (trade persistence),
`pandas`/`numpy`/`scipy` (the indicator pipeline), `python-telegram-bot` (the RPC
surface), plus TA libraries (`ta-lib`, `technical`, `ft-pandas-ta`). Split
requirement files (`requirements-dev/-hyperopt/-freqai/-plot.txt`) keep the base
install lean.

## Patterns to borrow

The resolver pattern is the borrowable core: one `iresolver.py` base + a thin
per-concern subclass, config-string → loaded object, no central registry to keep
in sync. Also worth borrowing: the required-hooks + optional-`custom_*`-overrides
shape of `IStrategy` for any user-extensible pipeline, and the split
requirements-file layout for optional heavy extras. (Patterns and file references
only — this repo is GPL-3.0, so its code must not be copied into a
non-GPL codebase.)

## Anti-patterns

Letting the orchestrator class accumulate the whole lifecycle (see Solved poorly)
— the pattern to avoid is a single class owning loop, entry, adjustment, and exit.
Carrying both sides of a rename in the public ABC long-term (buy/sell vs
entry/exit) doubles the surface every implementer must understand.

## Testing approach

100 `test_*.py` files with a `tests/` tree mirroring the package (`tests/exchange`,
`tests/freqtradebot`, `tests/freqai`, `tests/commands`), heavy shared fixtures
(`conftest.py`, `conftest_trades.py`, `conftest_trades_usdt.py`), and a separate
`tests/exchange_online` directory isolating live-network tests from the offline
suite — the isolation of online tests is the notable practice.

## Production setup

Real deployment story: `Dockerfile` + `docker-compose.yml` + a `docker/` directory,
a systemd unit (`freqtrade.service`) with a watchdog variant
(`freqtrade.service.watchdog`), and 10 GitHub Actions workflows (`ci.yml`,
`docker-build.yml`, `deploy-docs.yml`, plus automated dependency/pre-commit
updates and a `zizmor_action.yml` workflow-security scan). Docs are a full mkdocs
site.

## Verdict

borrow-architecture — the resolver-plugin + ABC-strategy-contract architecture is
directly applicable to any config-driven, user-extensible engine, and the
production scaffolding (isolated online tests, systemd + watchdog, workflow
security scanning) is a mature template. Borrow the architecture and patterns, not
the code: GPL-3.0 makes copying implementation a licensing decision, and the
monolithic-orchestrator and dual-naming issues are the parts to leave behind.
