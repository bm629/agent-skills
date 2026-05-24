# Measurement and Budgets

Loaded during Step 1 of the token-optimization workflow.

## Heuristic estimation

When no tokenizer is available, these rules of thumb are accurate to
roughly ±15%:

| Content type | Rule | Notes |
|---|---|---|
| English prose | `tokens ≈ words × 1.3` | Most reliable for natural language |
| Code (any language) | `tokens ≈ chars / 4` | Includes whitespace and punctuation |
| Mixed code + prose | `tokens ≈ chars / 4` | Use the code rule for safety margin |
| CJK / multi-byte text | `tokens ≈ chars / 2` | Tokenizers treat each character as ~1–2 tokens |
| JSON / structured | `tokens ≈ chars / 3.5` | Brace and quote density inflates count |

For the cost figure, multiply by the per-million-token price of the
model in question. Input and output prices differ — output is typically
3–5× the input price, which is why output trimming (Step 8) often
dominates the savings on chatty agents.

## Exact counts

When precision matters (e.g., guarding against context-window overflow
on a long prompt), call the host provider's count-tokens facility before
the real generation:

- **Anthropic SDK**: `client.messages.count_tokens(...)` returns the
  exact input-token count without consuming generation budget.
- **OpenAI / compatible**: `tiktoken` library locally; `cl100k_base` /
  `o200k_base` encodings depending on model.
- **Google Gemini SDK**: `model.count_tokens(...)` on the request.

These calls are typically free or trivially cheap and are the right tool
when you need to *guarantee* fitting within a window.

## Output-size estimation by complexity

When you need to predict the response window before answering, classify
the prompt and apply a multiplier to the input token count:

| Complexity | Input → output multiplier | Example prompts |
|---|---|---|
| Simple | 3× – 8× | "What is X?", yes/no, single-fact lookup |
| Medium | 8× – 20× | "How does X work?", short walk-through |
| Medium-high | 10× – 25× | Code generation with provided context |
| Complex | 15× – 40× | Multi-part analysis, architecture, comparison |
| Creative | 10× – 30× | Stories, essays, narrative writing |

The product `input_tokens × multiplier` is the *full window*; clamp it
to the model's configured `max_tokens` ceiling. Pick a depth tier
(below) to land inside the window.

## Depth tiers

When the user asks for control over response length, present four tiers
based on the predicted window:

| Tier | Position in window | Target shape |
|---|---|---|
| Essential (25%) | `min + (max-min) × 0.25` | 2–4 sentences; direct answer only |
| Moderate (50%) | `min + (max-min) × 0.50` | 1–3 paragraphs; answer + 1 example |
| Detailed (75%) | `min + (max-min) × 0.75` | Structured response; pros/cons |
| Exhaustive (100%) | `max` | No restriction |

If the user has already chosen a tier earlier in the session, hold it
silently for follow-ups; don't re-ask each turn.

## Bucketed measurement template

When diagnosing where tokens are going, fill in this table for the
current request:

```
Bucket               | Est. tokens | % of total | Optimization layer
---------------------|-------------|------------|--------------------
System / role        |             |            | Step 3 (slim)
Tool definitions     |             |            | Step 3 (drop unused tools)
Conversation history |             |            | Step 4 (compress)
Tool results         |             |            | Step 5 (mask)
Current turn         |             |            | Step 8 (output trim)
Total                |             |            |
```

The dominant bucket dictates which step in the main workflow to focus
on. If two buckets are within 10% of each other, address them in
parallel.

## Pricing-aware reporting

When reporting savings to a user, frame the delta in three ways:

1. **Per-call**: "−40% input, −15% output → ~$0.0028 saved per call"
2. **Per-day** (if usage is known): "≈ $4.20/day at current pace"
3. **Per-month** (extrapolate × 30 only if usage is steady): with the
   caveat that real usage varies and the figure is an estimate

Avoid quoting absolute monthly numbers without noting the assumption —
pricing changes, usage patterns shift, and small estimation errors
amplify across millions of tokens.
