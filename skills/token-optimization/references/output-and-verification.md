# Output and Verification

Loaded during Steps 8–9 of the token-optimization workflow: trimming generated output and verifying that the optimization actually moved the dominant bucket. The SKILL.md body has the headline bullets; this file expands the templates, cookbooks, and troubleshooting matrices.

---

## Step 8 — Trim the output

Output tokens are typically priced 3–5× input tokens (provider-dependent). Trimming output usually pays back faster than trimming input. Tactics in priority order:

### 8.1 Depth tiers (offer before answering)

Default behavior most agents accidentally adopt: maximum verbosity for every question. Counter with an explicit depth picker for any answer ≥ 200 words. Phrase the picker once, then default to the smallest tier the user implied.

**Template:**

```
Depth options:
  essential   — 1–3 sentences answering the literal question.
  moderate    — single paragraph (4–8 sentences) with reasoning.
  detailed    — multi-paragraph (~300–500 words) covering edge cases.
  exhaustive  — full coverage including alternatives, gotchas, references.

Default: essential. Reply "moderate" / "detailed" / "exhaustive" to expand.
```

**Heuristic for the default tier** (pick the smallest that fits):

| User signal | Default |
|---|---|
| "what is X?" / "how do I X?" / one-line query | essential |
| "explain X" / "walk me through X" | moderate |
| "compare X and Y" / "design X" | detailed |
| "I'm building X and need to choose between …" | exhaustive |

When in doubt, drop a tier. User can always ask for more.

### 8.2 Cut filler, keep orientation

Strip pure ceremony from every response, but keep one-line orientations that help the reader (e.g., "Updated X to Y because Z"). Common offenders worth stripping:

| Bridge phrase | What to replace it with |
|---|---|
| "Sure! Here is …" | (delete; start at the answer) |
| "I've updated the file." (status only, no why) | (delete; if the *why* matters, use a one-line "Updated X to Y because Z" instead) |
| "Let me know if you need anything else!" | (delete) |
| "I hope this helps!" | (delete) |
| "Great question." / "Excellent point." | (delete) |
| "First, let me explain …" | (start with the explanation) |
| "Before answering, I should note …" | (lead with the answer; caveats follow inline) |

Each bridge phrase = 5–15 wasted output tokens, multiplied by every response. Over a long agent loop this compounds.

### 8.3 Structured output for machine consumption

When the consumer is another tool / parser, JSON or a tool-use schema beats prose every time:

- 30–50% shorter than equivalent prose at the same information density.
- No filler tokens (no "the result is …" wrappers).
- Provider tool-use APIs (Anthropic `tool_use`, OpenAI function-calling) often skip the prose portion entirely on the wire.

**When to use:**

- Any agent-to-agent handoff.
- Any parseable output (lists of files, structured diffs, configuration).
- Any output that will be re-fed to a model in a subsequent turn.

**When NOT to use:**

- Human-facing explanations (prose is more readable).
- Anything where reasoning visibility matters (debugging, code review).

### 8.4 Stop sequences

When a known terminator delimits the useful output, set it as a stop sequence on the API call. The model stops generating immediately on the terminator and you don't pay for the trailing reasoning.

**Common stop sequences by use case:**

| Use case | Stop sequence |
|---|---|
| Code completion (single function) | `\n}\n` or `\nend\n` |
| List-building (until end marker) | `\n---\n` or `\nDONE\n` |
| Q&A with explicit terminator | `\n\nQ:` or `\n[END]` |
| Tool-call extraction | `\n</tool>` |
| Single-line classification | `\n` (literal newline) |

Stop sequences are MOST effective with extended-thinking models — they prevent the model from elaborating after producing the answer.

### 8.5 Cap thinking budgets

For models with extended thinking (Claude Opus / Sonnet 4.x with thinking enabled, GPT-o1, etc.), set an explicit thinking budget. Reserve large budgets for problems that genuinely benefit; cap routine tasks tightly.

**Calibration table:**

| Task type | Thinking budget |
|---|---|
| Classification, status check, single-file edit | 1k tokens |
| Routine debugging, test generation | 2k–4k tokens |
| Multi-file refactor, architecture sketch | 8k–16k tokens |
| Hard math, deep reasoning, novel design | 32k–64k tokens (the model's max) |

Misuse to avoid: setting "max thinking" by default. The model spends the full budget on every task, including trivial ones; you pay for thinking tokens that produce no value.

---

## Step 9 — Verify the win

Optimization without measurement is hope. Re-run the Step 1 measurement after applying tactics; report a structured delta.

### 9.1 Re-measurement template

```
Optimization target: <bucket name from Step 1, e.g., "system prompt">

Before:
  input  tokens: N1   (or estimated: ~N1)
  output tokens: M1   (or estimated: ~M1)
  est cost:      $C1  (per call)

After:
  input  tokens: N2
  output tokens: M2
  est cost:      $C2

Delta:
  input:  -X%   (saved N1 - N2 tokens)
  output: -Y%   (saved M1 - M2 tokens)
  cost:   -$Z   (per call; -$Z * estimated daily calls = -$ZZ/day)
```

CSV-friendly variant for tracking over multiple optimization rounds:

```
round,bucket,before_in,before_out,after_in,after_out,delta_pct,delta_$_per_call
1,sys_prompt,12000,800,4500,800,-58,-0.18
2,tool_defs,4500,800,2800,800,-29,-0.05
3,thinking,2800,800,2800,400,-30_output,-0.06
```

### 9.2 Negligible-delta troubleshooting

If the delta is < 5% on the targeted bucket, the dominant bucket was something else. Re-measure all buckets fresh; the actual cost driver is hiding somewhere you didn't look.

**Common causes when "obvious" optimizations don't move the needle:**

| Symptom | Likely actual culprit |
|---|---|
| Trimmed system prompt by 50%, total tokens dropped 5% | Conversation history or tool definitions are the real bulk |
| Added prompt caching, no cost change visible | Cache breakpoint is invalidated every call (timestamp / random ID at front?) |
| Switched to cheaper model, no cost saving | Loop count went up because cheaper model needed more turns |
| Reduced output tokens, no cost saving | Output was already minor; input is the dominant bucket |
| Compaction added, marginal gain | Conversation already short relative to system prompt |

**Recovery procedure:** redo Step 1 with fresh measurements (don't trust the prior bucket sizes — they may have shifted). Pick a different dominant bucket. Apply Steps 2–8 tactics targeted at that bucket.

### 9.3 Tokens-per-task vs tokens-per-call

Always verify against the **task** target, not the **call** target. A 30% per-call saving that quintuples the loop count is a 350% increase in tokens-per-task.

**Verification method:**

1. Pick a representative end-to-end task (not a single API call).
2. Run it before optimization; log total tokens across all calls.
3. Run the same task after optimization; log total again.
4. Compare totals, not per-call numbers.

If the per-task total didn't move (or got worse), the optimization was a per-call win that hurt the loop. Roll back.

### 9.4 When to call the optimization "done"

Stop when any of these conditions hits:

- The dominant bucket is now within 20% of the next-largest bucket (no single dominant target).
- Each subsequent tactic yields < 5% improvement.
- The optimization itself starts costing more in operator time than the savings buy back per month.
- A fresh measurement shows the workload pattern has shifted (e.g., user behavior changed) — re-baseline before continuing.
