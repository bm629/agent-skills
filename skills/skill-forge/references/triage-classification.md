# Triage classification

Loaded during Step 1 to decide cache / improve / create, rate confidence, detect breadth, and guard against self-forge.

## Buckets

- **cache** — the topic IS an existing **forge-made** skill's subject AND its body already covers the asked aspect (confirm against the body, not the one-line description). Confirm the file exists and parses, then return it; skip research.
- **improve** — the topic is a feature/syntax/sub-part of an existing **forge-made** skill's subject. Research only the delta; append (never delete).
- **create** — the topic is a separate installable tool/library/framework/standard, or no related skill exists.

Rule of thumb: **same thing, different aspect → improve; different thing → create.**

## Confidence

| Situation | Confidence | Action |
|---|---|---|
| 0 candidates | high | create |
| 1 candidate, topic clearly within its scope | high | improve (if forge-made) |
| 1 candidate, topic clearly distinct | high | create |
| 1 candidate, scope debatable | low | ask upfront (Step 1.5) |
| 2+ candidates, one clearly most specific | high | improve/create per the test |
| 2+ roughly equal, or phrasing vague | low | ask upfront |

Low confidence → present merge-into-A / merge-into-B / create-new **before** any research.

## Forge-mark gate

Resolve a matching local skill by its `forge:` block:

- **Forge-made + covers the aspect** → cache (confirm it exists and parses, return it).
- **Forge-made + missing the aspect** → improve (append in place).
- **Third-party (no `forge:` block)** → return it as-is (confirm it exists and parses) with an advisory that it is not forge-made and cannot be extended in place; a knowledge gap is filled by re-invoking skill-forge on that specific sub-topic to forge a separate scoped skill. Never modify a third-party skill.

## Name-clash on create

Chosen slug already exists: same domain → reroute to improve; genuinely different thing sharing the name → abort `F9`, ask for a new name. Never overwrite.

## Recursive-forge guard

After normalisation, before classifying: refuse (`F3`) topics whose slug contains `skill-forg` or `meta-forg` (substring), or matches an alias (`skill-forge`, `skillforge`, `skill-builder`, `skill-creator`, `meta-skill`, …). To improve skill-forge, edit its `SKILL.md` directly.

## Breadth → multi-skill fan-out

If the topic names a stack/suite or multiple distinct tools (e.g. "MERN stack", "AWS"), it is not one atomic skill → switch to the fan-out flow. Use `task_context` (or ask) to recommend the specific skills.

## Normalisation

`re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')[:64]`; the result must match `^[a-z0-9-]{1,64}$` and be non-empty, else `F-INVALID-TOPIC` (empty → "topic must contain ASCII letters/digits"; path chars present → "rejected path-traversal").

## Worked examples

- "Python pattern matching" → improve `python` (a feature of the language).
- "uv" → create (separate tool, even though Python-adjacent).
- "FastAPI dependency injection", no `fastapi` skill yet → create `fastapi`.
- "Django ORM", candidates `django` + `database` equally relevant → low confidence → ask.
- "MERN stack" → breadth → fan-out.
