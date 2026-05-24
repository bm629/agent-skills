---
name: token-optimization
description: >
  Use when you need to reduce token usage, lower API cost, fit work within a
  context window, or speed up an expensive/slow agent loop. Triggers on
  phrases like "optimize tokens", "reduce token usage", "save on cost",
  "fit in context", "context too long", "running out of tokens", "prompt
  caching", "compact the context", "agent is too expensive", "shrink the
  prompt", "cheaper model", "tokens-per-task". Provides a layered tactic
  catalog — measurement (heuristic counting and budget allocation),
  prompt-side levers (caching, system-prompt diet, tool-definition pruning),
  context management (compression, observation masking, file-system
  offload), agent-loop patterns (parallel tool calls, batch operations,
  model routing by complexity), and output-side controls (depth tiers, stop
  sequences, structured output). Project-agnostic and provider-agnostic;
  works across Claude Code, Codex CLI, Cursor, Gemini CLI, and Copilot.

extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}

version: "1.8.3"

forge:
  status: reviewed
  forged: 2026-05-07
  reviewed: 2026-05-11
---

# Token Optimization

## Overview

Reducing token usage is rarely a single trick — it's a stack of small wins
applied at the right layer. This skill is a triage map: it diagnoses *where*
the tokens are going (system prompt, conversation history, tool results,
agent loops, output verbosity), then points to the matching tactic. The
correct optimization target is **tokens-per-task**, not tokens-per-request:
a one-shot 12k-token prompt that solves the problem beats a 2k-token loop
that takes 30 turns. Apply tactics in order: measure first, then cache,
then compress, then route, then trim output.

## When to activate

- ✅ User says they're hitting context limits, billing surprises, or slow loops
- ✅ User asks how to use prompt caching, compaction, or extended thinking budgets
- ✅ User wants to choose a cheaper model or split work across models
- ✅ Agent itself notices a long-running session crossing roughly 70% context-window utilization (rule-of-thumb trigger; use exact counts when available, heuristic estimate otherwise — trigger earlier on long-running sessions where headroom matters more, later on short tasks)
- ✅ Reviewing a system prompt, CLAUDE.md, or memory file that "feels heavy"

**Do NOT activate when:**
- The topic is a specific tokenizer library (use a `tokenization-*` skill)
- "Token" refers to auth/JWT/payment tokens, or UI design tokens
- The user only wants pricing math (point at provider pricing pages)

## Workflow

Apply the tactics in the order below. Each layer is cheap to try and
independent of the next, so stop as soon as the cost/context goal is met.

### Step 1 — Measure where the tokens go

Before optimizing, locate the cost. For a single request, mentally split
the prompt into five buckets and estimate each:

| Bucket | What it contains | Typical % of total |
|---|---|---|
| System / role | static system prompt, CLAUDE.md, AGENTS.md, memory files | 5 – 40% |
| Tool definitions | tool schemas injected per turn | 5 – 30% |
| Conversation history | prior user/assistant turns | 10 – 50% |
| Tool results | file reads, search output, command stdout | 20 – 70% |
| Current user message + output | this turn's request and reply | 5 – 20% |

Heuristic estimation (no real tokenizer needed):

- English prose: `tokens ≈ words × 1.3`
- Code or mixed: `tokens ≈ chars / 4`
- CJK / multi-byte: `tokens ≈ chars / 2`

Accuracy is roughly ±15%. For exact counts in a Claude / Anthropic SDK
context, use the SDK's `count_tokens` endpoint before the real call. For
detailed budget math (output multipliers, depth tiers), see
[`references/measurement-and-budgets.md`](references/measurement-and-budgets.md).

Output: state which 1–2 buckets dominate. The bucket dictates which step
below to focus on.

### Step 2 — Make the static prefix cacheable

The single biggest win for repeated calls is **prompt caching**: a stable
prefix (system prompt + tool defs + long reference docs) is hashed once
and reused at a heavy discount on subsequent requests within the cache
TTL. To exploit it:

- Place everything stable at the **front** of the prompt; place changing
  content (the user's current question, the latest tool result) at the
  **end**. Cache lookups match by exact prefix.
- Mark the cache breakpoint at the end of the largest stable block. In
  the Anthropic SDK, set `cache_control: {type: "ephemeral"}` on the last
  content block of that prefix.
- Keep the prefix byte-identical between calls. Reordering tool defs,
  inserting timestamps, or shuffling memory files invalidates the cache.
- Group reads in a stable order so file-content blocks reused across
  turns hit the same cache entry.

**When the prefix legitimately needs to change**, never edit an earlier
message in place. Append a new message carrying the updated state
instead — every prior call's cached prefix stays valid.

| Change | Wrong (cache-breaking) | Right (cache-preserving) |
|---|---|---|
| Sandbox / permission mode | edit the earlier permission message | append a new `role=developer` message with the new mode |
| Working directory | edit the earlier environment message | append a new `role=user` message announcing the cwd change |
| Tool list addition | reorder or rewrite earlier tool defs | append at the end; new tools start caching from the next call |
| MCP `tools/list_changed` | hot-reload mid-conversation | defer refresh to a conversation boundary, or accept the miss |

Editing in place rewrites bytes the cache already hashed — every subsequent
call misses. Appending costs only the new message's tokens. (Role names like
`role=developer` / `role=user` above are Anthropic-flavored — use the
equivalent role bucket on other hosts.)

For provider-specific cache mechanics (TTL, minimum block sizes, billing
behavior), see [`references/prompt-caching.md`](references/prompt-caching.md).

### Step 3 — Slim the always-loaded context

Files like `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursorrules`, and
memory indexes are injected on **every** message. A 5,000-token memory
file across 100 messages is 500,000 input tokens of pure overhead.

Targets and trims:

| File | Target budget | Common bloat to remove |
|---|---|---|
| Top-level instruction file (CLAUDE.md / AGENTS.md) | < 1,500 tokens | restating defaults, long framework lists, paragraph examples |
| Memory index | < 3,000 tokens | inline content; keep one-line pointers per entry |
| Per-skill instructions | < 5,000 tokens | duplicated explanations across skills |

Slimming rules:

1. **Cut defaults.** "You are a helpful assistant", "write clean code" —
   the model already does these.
2. **Merge overlapping bullets.** "Be concise" + "don't be verbose" +
   "keep responses short" → one bullet.
3. **Move examples to references.** Examples bloat the always-loaded
   payload; put them in on-demand `references/<topic>.md` files.
4. **Bullets, not paragraphs.** Shorter and parsed more reliably.
5. **Drop unused agents/skills.** If a memory entry hasn't been
   referenced in two weeks, it's a candidate for removal.
6. **Audit MCP-style tool servers.** Each enabled server injects its tool
   defs into every turn — ten servers with 5–10 tool defs each is easily
   5,000+ tokens of per-turn overhead. Audit the enabled list against actual
   use — disable servers that haven't been called in the last few sessions
   before reaching for harder optimizations. A working ceiling of around 10
   enabled per project keeps overhead in check, but capability trumps the
   count: keep what the task needs. Prefer a CLI binary when an equivalent
   exists (e.g., `gh` over a GitHub MCP server).

### Step 4 — Compress conversation history

Long sessions accumulate stale turns. Apply a tiered compression policy
when the history bucket dominates Step 1's accounting:

- Last 3–5 turns: keep verbatim.
- Turns 6–10: keep decisions and conclusions, drop intermediate reasoning.
- Older than that: one-line summary per turn — but keep verbatim any turn
  whose specific reasoning is still load-bearing for the current task.
- Failed tool calls past the fix: drop the failure noise; keep the fix.
- Large file reads superseded by edits: keep only the final state.

Pin the **primary objective** at the top of any compressed prompt so the
model never loses the goal during compression. Never prune system
instructions or safety headers. For the structured-summary template and
artifact-trail rules, see
[`references/context-management.md`](references/context-management.md).

**Anti-anxiety calibration.** Frontier models with context-window awareness
sometimes *underestimate* remaining context and start rushing — premature
summaries, shortcut decisions, "let me finalize" mid-task. Counter it with:

- Aim to stay well below the window cap on long sessions (e.g., budget ~200k
  of a 1M window for active context). The headroom is a soft buffer for the
  model's confidence, not a hard ceiling — extend it when the task genuinely
  needs more.
- Include an explicit budget statement near the start of the compressed
  snapshot (not in the cacheable static prefix — that would break Step 2's
  discipline): "Context budget: ~180k tokens remaining. Continue working at
  full depth."
- If you spot mid-task wrap-up signals (sudden summary, "let me finalize")
  while real work clearly remains, re-state the budget rather than letting
  the model self-direct. If the wrap-up is correct — task done or context
  genuinely tight — let it finalize.

This is model-side behavior, not host-side — applies on any host running
a context-aware model.

### Step 5 — Mask verbose tool observations

Tool output is the largest unbounded source of tokens. Replace verbose
results with **observation references** the model can re-fetch on demand:

- Successful file read → `[read src/foo.ts: 312 lines, exports: a,b,c]`
- Successful search → `[grep "X": 7 hits in 4 files: …]`
- Long command stdout → keep first/last 5 lines + exit code
- Screenshots / images → resize to the lowest resolution that still works
  for the task. 1280×720 is usually the sweet spot for UI screenshots;
  bump up to 1920×1080 or higher for dense text / OCR work where
  legibility is load-bearing — full 4K is ~5× more tokens than needed
  for typical UI work.

This is *masking*, not *deleting*: the underlying file/command is still
addressable, the model just doesn't carry the bytes through every turn.

### Step 6 — Route to the right model

Match model to task complexity. Reaching for the largest model on every
call is the most common single source of overspend.

| Task | Suggested tier |
|---|---|
| Status checks, pings, classification, simple lookups | smallest/cheapest tier (e.g., Haiku-class) |
| File reads, autocomplete, lints, formatting, single-file edits | small tier |
| Multi-file edits, debugging, test generation | mid tier (e.g., Sonnet-class) |
| Architecture, multi-step planning, deep refactors, very long context | top tier (e.g., Opus-class) |

Keep a fallback chain (top → mid → small) for rate-limit or latency
backoff. When sub-agents are available, **delegate** narrow searches and
file scans to a cheaper-model sub-agent and return only the synthesis to
the main loop — the main loop never pays for the raw search output.

### Step 7 — Cut agent-loop overhead

Each loop iteration re-transmits the full conversation context. Reducing
iterations is multiplicative.

- **Batch tool calls.** Issue independent tool calls in **parallel** in
  one assistant turn, not sequentially across turns.
- **Combine small tasks.** Process N files in one iteration instead of
  spawning N iterations.
- **Set iteration caps.** Cap retries on a single failing operation
  (e.g., ~5) with a clean "summarize and stop" exit, while leaving room
  for legitimately multi-step plans to run their length.
- **Avoid speculative reads.** Read what the task needs, not "everything
  related". Use `glob`/`grep` to narrow before opening files.
- **Background long jobs.** Don't keep the model in a polling loop on a
  multi-minute task — schedule a wake-up or use the host's background
  primitive.

For platform-specific patterns (parallel tool calls in the Anthropic SDK,
sub-agent delegation in Claude Code, Task tools in Codex), see
[`references/agent-loop-patterns.md`](references/agent-loop-patterns.md).

### Step 8 — Trim the output

Output tokens are typically priced higher than input. Tactics:

- **Depth tiers.** Offer "essential / moderate / detailed / exhaustive"
  before answering long-form questions; default to the smallest tier the
  user clearly implied. When intent is ambiguous, err one tier higher
  rather than under-answering.
- **Cut filler, keep orientation.** Skip pure throat-clearing ("Sure, here
  is …", "Great question!"). A one-line orientation ("Updated X to Y
  because Z") is fine and often helpful — the goal is to cut filler, not
  strip context.
- **Structured output for machine consumption.** JSON / tool-use schemas
  are usually shorter than equivalent prose and don't need filler.
- **Stop sequences.** When a known terminator delimits the useful output,
  set it; the model stops generating once reached.
- **Cap thinking.** For models with extended thinking, set an explicit
  thinking budget (e.g., 1k–4k tokens for routine tasks; reserve larger
  budgets for genuinely hard problems).

For depth-tier templates, bridge-phrase strip list, stop-sequence
cookbook, and thinking-budget calibration tables, see
[`references/output-and-verification.md`](references/output-and-verification.md).

### Step 9 — Verify the win

Before declaring success, re-measure with the same buckets from Step 1
and report a delta:

```
Before: input=N1, output=M1, est cost C1
After:  input=N2, output=M2, est cost C2
Delta:  -X% input, -Y% output, -$Z per call
```

If the delta is negligible, the dominant bucket was different from what
you optimized — go back to Step 1 with fresh measurements.

For the full re-measurement template (incl. CSV variant for tracking
multiple optimization rounds), the negligible-delta troubleshooting
matrix, tokens-per-task vs tokens-per-call verification method, and
"when to call optimization done" exit conditions, see
[`references/output-and-verification.md`](references/output-and-verification.md).

**Expected ranges.** Use these as calibration points, not guarantees:

- Compaction: 50–70% reduction at <5% quality loss.
- Masking: 60–80% reduction in masked observations.
- Prefix cache hit rate: ≥ 70% on stable workloads.

If your delta is at the upper end of these ranges, you're in the
diminishing-returns zone for that tactic on typical workloads — further wins
come from layering, not from squeezing one lever harder.

## Cross-agent invocation

The tactics above are agent-agnostic; the *commands* to apply them differ per
host runtime. Use this table to translate a tactic into the host you're in.

| Tactic | Claude Code | Codex CLI | Cursor | Gemini CLI | Copilot CLI |
|---|---|---|---|---|---|
| Reset context (Step 4) | `/clear` | `/clear` | New chat | `/clear` | New session |
| Manual compaction (Step 4) | `/compact` | manual summary only | n/a | n/a | n/a |
| Auto-compaction threshold (Step 4) | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=<pct>` (env) | n/a | n/a | n/a | n/a |
| Switch model (Step 6) | `/model sonnet\|opus\|haiku` | `--model <id>` flag | model picker | `/model <id>` | `--model <id>` |
| Subagent / delegated model (Step 6) | `CLAUDE_CODE_SUBAGENT_MODEL=<id>` (env) | per-Task model arg | n/a | sub-agent config | n/a |
| Cap thinking budget (Step 8) | `MAX_THINKING_TOKENS=<n>` (env) | reasoning-effort flag | n/a | thinking config | n/a |
| Token spend check (Steps 1, 9) | `/cost` | session footer | status bar | `/stats` | `gh copilot usage` |
| Prefix cache (Step 2) | automatic + `cache_control` SDK flag | automatic on exact prefix | automatic | implicit context cache | via provider |

Notes:

- Env vars apply to the host runtime's settings file (e.g.,
  `~/.claude/settings.json`'s `env` block for Claude Code). Other hosts have
  their own settings location.
- `n/a` means the feature is not exposed on that host's CLI surface today —
  the underlying tactic may still apply via direct provider SDK use.
- MCP-style tool servers count against tool-definition tokens on every host
  that supports them. Keep enabled count modest (around 10 per project is a
  reasonable working ceiling); see Step 3 for the broader instruction-file diet.

## Rules

**Hard rules (never violate):**

- Never prune system instructions, safety headers, or compliance text
  during compression — context-loss jailbreaks are a real risk.
- Never invalidate a stable prefix unintentionally (e.g., by injecting
  a timestamp or random ID at the front). If a value must vary per call,
  put it at the end.
- Tokens-per-task is the optimization target, not tokens-per-request.
  Don't celebrate a 30% per-call saving that quintuples the loop count.
- Don't remove an instruction just because the model "should know it" if
  doing so changes user-visible behavior. Verify with a real example.

**Preferences (override-able):**

- Apply tactics in the listed order; stop as soon as the goal is met.
- Prefer reference-fetch (file paths the model can re-read) over
  inline-dumping large content.
- For repeated calls, optimizing the cacheable prefix usually beats any
  other single change.
- When unsure between two tactics, pick the one that makes the prompt
  shorter at the *start* (caching benefits) over the *end*.

## Output

This skill produces a diagnosis and a prioritized tactic list — not a
mechanical rewrite. The expected hand-off is:

1. A bucketed measurement of current token usage (Step 1).
2. The 2–3 tactics from Steps 2–8 most likely to move the dominant bucket.
3. Concrete proposed edits (system-prompt diff, cache-breakpoint
   placement, model-routing rule, etc.) for the user to accept or reject.
4. A re-measurement after changes are applied (Step 9).

The abstract consumer is **whichever agent runtime is hosting this
session** (Claude Code, Codex, Cursor, Gemini CLI, Copilot). Tactics that
reference provider-specific features (cache_control, thinking budgets,
sub-agents) carry their own provider tag in the reference files.

## Progressive disclosure

Heavy detail lives in subfolders, loaded only on demand:

- [`references/measurement-and-budgets.md`](references/measurement-and-budgets.md)
  — load during Step 1. Heuristic-vs-exact estimation, complexity-based
  output multipliers, depth-tier math.
- [`references/prompt-caching.md`](references/prompt-caching.md)
  — load during Step 2. Cache-breakpoint placement, TTL, minimum block
  sizes, invalidation triggers, debugging cache misses.
- [`references/context-management.md`](references/context-management.md)
  — load during Steps 3–5. Slimming rules with examples, structured
  summary template for compaction, observation-masking patterns, image
  resolution guidance.
- [`references/agent-loop-patterns.md`](references/agent-loop-patterns.md)
  — load during Steps 6–7. Model-routing decision table, parallel
  tool-call pattern, sub-agent delegation, iteration caps, background
  job patterns.
- [`references/output-and-verification.md`](references/output-and-verification.md)
  — load during Steps 8–9. Depth-tier picker template + default-tier
  heuristic, bridge-phrase strip list, structured-output rules of
  thumb, stop-sequence cookbook by use case, thinking-budget
  calibration table, re-measurement template (incl. CSV variant),
  negligible-delta troubleshooting matrix, "when to call
  optimization done" exit conditions.

No `assets/` or `scripts/` ship in v1. Token estimation is heuristic and
described inline; if a project later wants exact counts, call the host
provider's `count_tokens` endpoint directly.

## Body budget

Soft targets — not hard caps. Grow the body when the topic genuinely
warrants it; move overflow to `references/<topic>-extras.md` rather
than truncating signal.

- `description`: agentskills.io spec caps this at 1,024 chars; that one
  is an external hard limit, not a soft target.
- Body: aim for ~500 lines / ~5,000 tokens as a comfortable read.
- Total file size: stay well below ~30,000 chars so the body still
  parses cleanly when re-rendered as a Copilot custom agent.
