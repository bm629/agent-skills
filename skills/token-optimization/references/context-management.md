# Context Management

Loaded during Steps 3–5 of the token-optimization workflow: slimming
always-loaded files, compressing conversation history, and masking
verbose tool observations.

## Slimming always-loaded instruction files

Files like `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursorrules`, and
project memory indexes are **multiplied by every turn**. A 5,000-token
instruction file across a 100-message session is 500,000 input tokens of
overhead — likely larger than the actual work.

### Audit checklist

Walk through the file with these questions:

1. **Is this a default behavior?** "Be helpful", "write clean code",
   "follow best practices" — strike them; they're already true.
2. **Is this redundant with another bullet?** Merge synonyms into one.
3. **Is this an example?** If yes, move it to a `references/<topic>.md`
   loaded only when the relevant skill activates.
4. **Is this referenced anywhere?** If a section hasn't been used in two
   weeks, archive it.
5. **Is this a paragraph that could be a bullet?** Convert.
6. **Is this an enumeration of frameworks/tools?** Replace with a single
   adaptive rule ("adapts to the project's stack").

### Target budgets

| File | Target | Rationale |
|---|---|---|
| Top instruction file (CLAUDE.md / AGENTS.md / etc.) | < 1,500 tokens | Loaded every turn |
| Sub-agent / persona file | < 800 tokens | Loaded every turn when active |
| Memory index | < 3,000 tokens | One-line pointers per entry, no inline content |
| Per-skill SKILL.md body | < 5,000 tokens | Move detail to references/ |

### Anti-patterns to remove

- "You are an expert in [long list]." → adapt to the project's stack.
- Three rules saying the same thing in different words. → one rule.
- Worked examples inline. → move to `references/`.
- Catch-all "if in doubt, ask the user" reminders. → already a default.

## Compressing conversation history

When the conversation-history bucket dominates measurement, apply tiered
compression:

| Age | Treatment |
|---|---|
| Last 3–5 turns | Verbatim — the model needs the immediate context |
| Turns 6–10 | Decisions and conclusions only; drop intermediate reasoning |
| Older | One-line summary per turn |
| Failed tool calls past the fix | Drop the failure, keep the working result |
| File reads superseded by edits | Drop the old read, keep the latest state |
| Long Bash output | Keep first/last 5 lines + exit code |

### Structured-summary template

When generating a compressed snapshot, use this shape so nothing
load-bearing is silently dropped:

```markdown
# Session Snapshot — <timestamp>
> Original ~N tokens → compressed ~M tokens (saved X%)

## Primary objective
<the goal that drives all turns>

## Key decisions
- <decision 1, with the constraint that motivated it>
- <decision 2>

## Active artifacts
- <file path>: <one-line summary of current state>
- <file path>: <one-line summary>

## Pending work
- <todo 1>
- <todo 2>

## Recent context (verbatim, last 3–5 turns)
<last few turns, full text>
```

### Hard rules during compression

- **Never prune the system prompt or safety constraints.** Loss-of-context
  jailbreaks are a real failure mode.
- **Pin the primary objective at the top of the new prompt** so the model
  can't drift after compression.
- **Preserve the artifact trail.** If a file was read, then edited, then
  re-read, the latest state is canonical, but record that an edit
  happened — otherwise the model may re-read again to "verify".
- **Don't compress within the active turn.** Compress between turns, not
  mid-task.

## Masking verbose tool observations

Tool output is the largest unbounded token source. Once a result has
been *consumed* (the model used it to make a decision), replace the raw
output with a short reference the model can re-fetch on demand:

| Tool | Raw output | Masked reference |
|---|---|---|
| File read | full file content | `[read src/foo.ts: 312 lines, exports: a,b,c — re-read with Read]` |
| grep / search | every match line | `[grep "X": 7 hits in 4 files — re-run if needed]` |
| Bash command | full stdout | `[bash <cmd>: exit=0, head/tail kept — re-run if needed]` |
| Web fetch | full HTML | `[fetched <url>: title, key headings — re-fetch if needed]` |
| Database query | full result set | `[query: 1428 rows, schema: …, sample: …]` |

The model still has the *address* (path, URL, command) to re-fetch — it
just doesn't carry the bytes through every subsequent turn.

## Image and screenshot tokens

Vision input is unusually expensive per "token" because images are
encoded into hundreds-to-thousands of tokens depending on resolution.

| Resolution | Approx. tokens (Claude vision) | Use case |
|---|---|---|
| 3840 × 2160 (4K) | ~1,600 | Almost never necessary |
| 1920 × 1080 | ~900 | Detail-rich diagrams |
| 1280 × 720 | ~500 | UI element detection, OCR — sweet spot |
| 1024 × 768 | ~400 | General OCR |
| 800 × 600 | ~300 | Minimum viable for OCR |
| 640 × 480 | ~200 | Layout-only checks |

Resize before sending. For browser-automation workflows (Playwright,
Puppeteer, MCP browser tools), set the viewport to 1280×720 by default
and only escalate when the task fails at that resolution.

## File-system as cold context

For long-horizon work, the file system is the cheapest possible "memory":

- Plans and decisions: write to `plan.md` or a checkpoint file. The
  model re-reads only the relevant section on demand.
- Sub-agent communication: shared files instead of message-passing
  through context.
- Scratch pads for tool output: dump big results to a temp file and pass
  the *path* between turns.

This is the **filesystem-as-memory** pattern — strictly cheaper than
keeping the same content in the conversation history, because each turn
only pays for what it reads.
