# Agent Loop Patterns

Loaded during Steps 6–7 of the token-optimization workflow: model
routing and loop-overhead reduction.

## Why loops dominate cost

In any harness with a tool-use loop, **every iteration re-transmits the
full conversation context**. If the system prompt + tool defs + history
is 30k tokens, a 10-iteration loop costs 300k input tokens regardless of
how small each step is. Cutting iterations is therefore multiplicative
in a way that cutting per-call output is not.

The right mental model: each iteration is "one shot at making
progress". Maximize the work-per-iteration, not the iterations-per-task.

## Model routing decision table

Match the model to the task; the largest model on every call is the
single most common cause of overspend.

| Tier | Tasks | Anthropic model class | Why |
|---|---|---|---|
| Smallest | Status checks, ping/health, classification, single-fact lookup, heartbeat-style background pings | Haiku-class | 10–20× cheaper than mid; latency wins |
| Small | File reads, lints, formatting fixes, autocomplete, schema validation, simple search | Haiku-class | Quality is sufficient |
| Mid | Code generation, single-file debug, test writing, explain-this-code, moderate refactor | Sonnet-class | Sweet spot for most coding work |
| Top | Architecture, multi-step planning, deep refactor across many files, very long context, hard reasoning | Opus-class | Reserve for problems that genuinely need it |

### Routing signals

Inputs to the routing decision:

- **Keyword match** in the user request (status/ping → smallest;
  architect/design/plan → top).
- **Complexity score** (rough 0–10): single fact = 0–2, multi-file
  reasoning = 6–8, system design = 9–10.
- **Context size**: prompts > 100k input tokens may justify the top
  tier purely because the cheaper model would degrade.
- **Tool-call count expected**: many small tool calls → small model.

### Fallback chain

When the chosen tier returns 429/503 or response time blows past a
ceiling, downgrade one step: top → mid → small → smallest. Log the
reason. Surface it to the user when the downgrade would change quality
materially.

## Sub-agent delegation as context isolation

Sub-agents exist to **isolate context**, not to simulate org charts.
The pattern:

1. Main loop has a 50k-token context.
2. Main loop dispatches a sub-agent with a narrow prompt ("find all
   call sites of X and report").
3. Sub-agent reads files, runs greps — *its own* context fills with
   raw output, but that context is discarded when it returns.
4. Sub-agent returns a 500-token synthesis to the main loop.

The main loop never pays for the raw search output. This is the single
biggest reason to use sub-agents on large codebases: not parallelism,
but context-cost isolation.

When NOT to delegate:

- The task needs the full context the parent already has.
- The result is itself huge (sub-agent returns 30k tokens — savings
  evaporate).
- The orchestration overhead exceeds the work done.

## Parallel tool calls

When two tool calls have **no data dependency between them**, issue
both in the *same* assistant turn. The host runs them concurrently and
returns both results in one observation, saving an entire iteration of
context re-transmission.

Examples of parallelizable calls:

- `Read(file_a)` + `Read(file_b)` when both are needed for the next step.
- `Bash(git status)` + `Bash(git diff)` + `Bash(git log)`.
- `grep("pattern", path_a)` + `grep("pattern", path_b)`.

Examples of NOT parallelizable:

- Read a file, then edit it (edit depends on the read).
- Run a test, then read its log (log depends on the test having run).
- Any sequence where the second call's input is the first call's output.

In the Anthropic SDK, this is supported natively via multiple
`tool_use` blocks in a single assistant message. Most modern hosts
(Claude Code, Codex, Cursor) expose it through their tool-use protocol.

## Iteration caps

Set a soft ceiling on retry/iteration loops on a single failing operation, with a clean exit — leave room for legitimately multi-step plans:

```
max_iterations: 5
on_limit_reached: summarize_progress_and_stop
```

Without a cap, a stuck agent burns tokens indefinitely. With a cap, the
worst case is bounded and the user gets a useful summary instead of a
silent timeout.

For genuinely long workflows (e.g., "scan 200 files"), batch in fewer,
larger iterations rather than one-per-item:

| Pattern | Iterations | Context overhead |
|---|---|---|
| One file per iteration × 200 | 200 | catastrophic |
| Ten files per iteration × 20 | 20 | 10× cheaper |
| Sub-agent batches 50 files × 4 | 4 main + 4 sub-agent contexts | cheapest |

## Background and scheduled jobs

If a task takes minutes (a long build, a deploy, a remote training
run), don't keep the model in a polling loop — every poll re-sends the
full context.

- Use the host's background-process primitive (Claude Code's
  `run_in_background`, Codex equivalents). The model checks in only
  when notified.
- Schedule a wake-up rather than sleeping with poll loops.
- For genuinely fire-and-forget tasks, exit the loop entirely and let
  the user re-engage when the task completes.

## Extended-thinking budgets

Models with extended thinking (e.g., Anthropic `thinking` block) charge
for thinking tokens. Set an explicit budget:

| Task class | Suggested `budget_tokens` |
|---|---|
| Routine code edit, lookup, formatting | 1,024 or off |
| Standard debug, single-file refactor | 2,048 – 4,096 |
| Complex architecture, multi-step planning | 8,192 – 16,384 |
| Genuinely hard reasoning (proof, deep analysis) | 32,000+ |

Defaults are usually generous; explicit budgets prevent runaway
thinking on simple tasks.

## Streaming and stop sequences

- **Streaming** does not reduce tokens but improves perceived latency
  and lets you cancel early when the output goes off-track. Cancel
  early to save output tokens.
- **Stop sequences**: when the useful output ends with a known
  delimiter (e.g., a closing tag, a sentinel string), set it as a stop
  sequence. Generation halts immediately.

## Claude Code-specific operational levers

When the host is Claude Code specifically, several settings move the
needle without any prompt-engineering work:

### `~/.claude/settings.json`

```json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

| Setting | Default | Recommended | Effect |
|---|---|---|---|
| `model` | varies | `sonnet` | Sonnet handles most coding work; switch to Opus only for complex reasoning. |
| `MAX_THINKING_TOKENS` | high (~32k) | `10000` | Caps extended-thinking budget; hidden output cost drops sharply. Set to `0` for trivial sessions. |
| `CLAUDE_CODE_SUBAGENT_MODEL` | inherits main | `haiku` | Sub-agent (Task) runs on Haiku — exploration, file reads, summarization at a fraction of the cost. |

### Slash commands during a session

| Command | When to use |
|---|---|
| `/clear` | Between unrelated tasks — stale context is paid every subsequent turn |
| `/compact` | At logical task boundaries (after exploration, after a milestone, before switching focus) |
| `/cost` | Check current session spend |
| `/model sonnet \| opus \| haiku` | Switch mid-session to match the next task's complexity |

**When to `/compact`**: after exploration before implementation, after a
milestone, after debugging before new work, before a major context
shift. **When NOT to**: mid-implementation of related changes, during
active debugging, during a multi-file refactor.

### Extended-thinking toggles

- **Alt+T** (Linux/Windows) or **Option+T** (macOS): toggle thinking on/off
- **Ctrl+O**: show thinking output (verbose mode)

Turning thinking off entirely for routine work is often the single
biggest win on simple sessions.

### MCP server hygiene

Each enabled MCP server injects its tool definitions on every turn.
Common rule of thumb: keep fewer than ~10 enabled per project.

- Run `/mcp` to see active servers and their context footprint.
- Disable unused servers (e.g., a default `memory` server you don't
  actually consume) via `/mcp`. Settings-file edits don't unload an
  already-running server in the live session.
- Prefer CLI tools (`gh`, `aws`, `kubectl`) over MCP equivalents when
  the CLI exists — the CLI doesn't pay per-turn schema overhead.

### Agent Teams (experimental)

Agent Teams spawns multiple independent context windows in parallel —
each teammate pays its own context cost. Use only when parallelism
clearly adds value (multi-module work, parallel reviews). For
sequential work, sub-agents (Task tool) are more token-efficient
because they isolate context without duplicating it.

### Auto-compaction overrides

Some Claude Code builds expose `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`.
Community reports indicate it can only *lower* the compaction
threshold, so values below default tend to make compaction fire
*earlier* than expected. If behavior surprises you, remove the
override and rely on manual `/compact` at planned breakpoints.

## Batch API

For non-interactive workloads (evaluation runs, bulk data processing),
the **batch API** typically provides a ~50% discount with a 24-hour
SLA. If real-time isn't required, batch the work — the discount is
larger than any prompt-engineering optimization can match.
