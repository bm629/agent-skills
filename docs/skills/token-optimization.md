# token-optimization

> Diagnostic + tactic catalog for reducing token usage. Spans all 5
> token-budget layers. Provider-agnostic; works across Claude Code,
> Codex CLI, Cursor, Gemini CLI, and Copilot.

**Skill file:** [`skills/token-optimization/SKILL.md`](../../skills/token-optimization/SKILL.md)
**Version:** 1.8.3

## Purpose

Reducing token usage is rarely a single trick — it's a stack of small
wins applied at the right layer. This skill is a **triage map**: it
diagnoses *where* the tokens are going, then points to the matching
tactic.

The correct optimization target is **tokens-per-task**, not
tokens-per-request. A one-shot 12k-token prompt that solves the
problem beats a 2k-token loop that takes 30 turns.

## When to activate

- ✅ User says they're hitting context limits, billing surprises, or slow loops
- ✅ User asks how to use prompt caching, compaction, or extended thinking budgets
- ✅ User wants to choose a cheaper model or split work across models
- ✅ The agent itself notices a long-running session crossing ~70%
  context-window utilization (rule-of-thumb trigger)
- ✅ Reviewing a system prompt, CLAUDE.md, or memory file that "feels heavy"

### When NOT to activate

- The topic is a specific tokenizer library — use a `tokenization-*` skill
- "Token" refers to auth / JWT / payment tokens, or UI design tokens
- The user only wants pricing math — point them at provider pricing pages

## The 5-layer model

Tokens go to one of five places. The skill diagnoses which one
dominates *before* applying tactics:

| Bucket | What it contains | Typical % of total |
|---|---|---|
| System / role | static system prompt, CLAUDE.md, AGENTS.md, memory files | 5 – 40% |
| Tool definitions | tool schemas injected per turn | 5 – 30% |
| Conversation history | prior user/assistant turns | 10 – 50% |
| Tool results | file reads, search output, command stdout | 20 – 70% |
| Current user message + output | this turn's request and reply | 5 – 20% |

Apply tactics in order: **measure first, then cache, then compress,
then route, then trim output.**

## Workflow (5 steps)

The skill's `## Workflow` section walks through these layers in order:

1. **Measure where the tokens go** — heuristic budget estimate
   (`tokens ≈ words × 1.3` for prose; `tokens ≈ chars / 4` for code).
   Decide which bucket is the leak.

2. **Cache the heavy static stuff** — prompt caching (Anthropic-style),
   system-prompt slimming, tool-definition pruning. See
   [`references/prompt-caching.md`](../../skills/token-optimization/references/prompt-caching.md).

3. **Compress conversation history** — summarize older turns, mask
   verbose tool observations, offload artifacts to the file system
   instead of inlining. See
   [`references/context-management.md`](../../skills/token-optimization/references/context-management.md).

4. **Optimize the agent loop** — parallel tool calls, batch operations,
   route complex tasks to powerful models and trivial ones to fast/
   cheap models. See
   [`references/agent-loop-patterns.md`](../../skills/token-optimization/references/agent-loop-patterns.md).

5. **Trim output** — depth tiers (one-line vs paragraph vs full),
   stop sequences, structured output instead of prose, brief answers
   to brief questions. See
   [`references/output-and-verification.md`](../../skills/token-optimization/references/output-and-verification.md).

For measurement details and budget allocation patterns, see
[`references/measurement-and-budgets.md`](../../skills/token-optimization/references/measurement-and-budgets.md).

## Worked example: a session at 70% context

Concrete diagnostic walk-through:

1. **Measure.** Sum the 5 buckets. Suppose:
   - System: 4k (CLAUDE.md + AGENTS.md = heavy)
   - Tools: 6k (many MCP tools loaded)
   - History: 80k (long conversation)
   - Tool results: 50k (lots of file reads)
   - Current + output budget: ~50k remaining
   - Total used: ~140k of 200k = 70%

2. **Highest leverage at this state**: history compression. 80k is
   conversation history — much of it is stale exploration. Compact
   the older turns into a single summary turn.

3. **Second leverage**: tool results. 50k is partly redundant file
   reads (same file fetched 4× across the session). Offload large
   blobs to disk and reference by path going forward.

4. **System / tools are smaller wins**: only 10k combined. Worth a
   pass later, but not the right target today.

5. **Don't trim output prematurely**: at 70% used, you still have 60k
   of room; output is not the bottleneck.

## Tactic catalog (high level)

The skill organizes tactics by layer. Each reference file goes deep:

| Layer | Tactics | Reference |
|---|---|---|
| Measurement | Heuristic counting, bucket attribution, budget allocation | `measurement-and-budgets.md` |
| System / tools | Prompt caching, system prompt diet, tool def pruning | `prompt-caching.md` |
| History / results | Compression, observation masking, file-system offload | `context-management.md` |
| Agent loops | Parallel calls, batch operations, model routing by complexity | `agent-loop-patterns.md` |
| Output | Depth tiers, stop sequences, structured output | `output-and-verification.md` |

## Per-agent considerations

The SKILL.md declares empty extensions blocks for all 5 agents:

```yaml
extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
```

This is intentional — the skill is **purely a strategy document**.
There are no agent-specific tool restrictions, runtime hooks, or
config knobs needed. The same content applies across all providers.

## Reference files bundled with the skill

| File | Purpose | Load when |
|---|---|---|
| [`measurement-and-budgets.md`](../../skills/token-optimization/references/measurement-and-budgets.md) | Heuristic token counting; per-bucket budget allocation patterns | Step 1 (measure) |
| [`prompt-caching.md`](../../skills/token-optimization/references/prompt-caching.md) | Anthropic + cross-provider prompt caching strategies | Step 2 |
| [`context-management.md`](../../skills/token-optimization/references/context-management.md) | Compaction patterns, observation masking, file-system offload | Step 3 |
| [`agent-loop-patterns.md`](../../skills/token-optimization/references/agent-loop-patterns.md) | Parallel calls, batch operations, model routing | Step 4 |
| [`output-and-verification.md`](../../skills/token-optimization/references/output-and-verification.md) | Output sizing, stop sequences, structured output | Step 5 |

## Why this skill exists

Existing skills in the token-optimization space tackle **one layer
each** — prompt caching alone, or context window management alone,
or output sizing alone. None of them provide a **diagnostic triage
that spans all 5 layers** with an explicit measure-first workflow.

This skill is the **strategy map**. Use it before reaching for any
specific tactic — the right tactic depends entirely on which bucket
your tokens are leaking from.

For installation, see [`docs/installation.md`](../installation.md).
