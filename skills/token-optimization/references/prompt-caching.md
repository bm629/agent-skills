# Prompt Caching

Loaded during Step 2 of the token-optimization workflow. Provider-specific
mechanics; the *principle* (stable prefix → cheap reuse) is universal.

## The mental model

Cached prompt prefixes work like a content-addressed key/value store: the
provider hashes the cached portion of your prompt, and on the next request
that begins with the *byte-identical* prefix it serves the KV state from
cache instead of re-encoding it. You pay a small write surcharge once and
a heavy read discount thereafter, for a TTL-bounded window.

Any change inside the cached region — even a whitespace tweak, a swapped
tool ordering, or a date string — invalidates that prefix and all longer
prefixes built on it.

## What to cache

Best candidates are **stable**, **large**, and **reused** content:

- The system prompt and any always-loaded instructions
- Tool definitions (schemas tend to be hundreds of tokens each)
- Long reference documents the agent re-reads across turns
- Few-shot examples that don't change per request
- Memory / convention files injected on every turn

Bad candidates:

- The current user message (changes every turn — put it after the cache)
- The latest tool result (changes every turn)
- Anything containing a timestamp, random ID, or per-request variable

## Where to place the cache breakpoint

Order the prompt in **decreasing stability**, then mark the breakpoint at
the *end* of the largest stable block:

```
[ system prompt           ]
[ tool definitions        ]
[ long reference docs     ]   ← cache breakpoint here
[ conversation history    ]
[ current user message    ]
```

In the Anthropic SDK, set `cache_control: {type: "ephemeral"}` on the
last content block of the stable section. Multiple breakpoints are
allowed (newer blocks fall through to older cached prefixes), but each
breakpoint adds bookkeeping — start with one.

## TTL and minimum size

Provider-specific; verify against current docs before committing:

- Anthropic ephemeral cache: 5-minute TTL by default; 1-hour cache also
  available with different pricing. Minimum block size applies (rough
  order: ~1024 tokens for Sonnet/Opus, ~2048 for Haiku — confirm before
  relying).
- The cache is per-organization, per-model, per-region. Switching models
  means re-warming.
- A read on a near-expired cache entry usually refreshes it for the same
  TTL window; a long idle gap drops the entry.

## Cache hit verification

After enabling caching, look for a hit-rate signal in the API response:

- Anthropic: `usage.cache_read_input_tokens` and
  `usage.cache_creation_input_tokens` on the response. The first should
  grow on subsequent calls; the second should be near zero except on
  cache writes.
- A hit rate below ~50% on a workload that should reuse prefixes means
  something is invalidating the cache. Common culprits below.

## Common cache-invalidation traps

1. **Timestamps or request IDs at the top.** Move them to the user
   message at the end.
2. **Tool definition reordering.** SDKs sometimes serialize tool lists
   in different orders — pin the order explicitly.
3. **Whitespace drift.** Auto-formatters that touch the system prompt
   between calls invalidate the cache. Pin the exact bytes.
4. **Conditional content.** A flag that "only adds X when Y" inside the
   cached region produces two different prefixes; lift the conditional
   *outside* the cache or move it to the end.
5. **Memory file edits.** If the host injects a `MEMORY.md` that you
   edited mid-session, the cache breaks. Either freeze memory for the
   duration of a session or keep memory after the breakpoint.
6. **Multi-region failover.** A failover to a different region warms a
   cold cache.

## When NOT to cache

- One-shot prompts with no plausible reuse.
- Prefixes shorter than the provider's minimum cache block — the write
  surcharge isn't recouped.
- Highly variable system prompts that change per user / per task.
- When the cache write cost is paid more often than the read benefit —
  audit hit rate before scaling caching out widely.

## Other provider equivalents

- **OpenAI**: implicit prompt caching on long stable prefixes; no manual
  breakpoint, but ordering still matters (stable prefix first).
- **Google Gemini**: explicit `cachedContent` / context caching with TTL.
- **Cursor / Claude Code / Codex**: typically pass the underlying SDK's
  caching through; check the host's documentation for any wrapper that
  controls breakpoint placement.

The host-agnostic rule holds across all of these: **stable first, mutable
last, byte-identical between calls.**
