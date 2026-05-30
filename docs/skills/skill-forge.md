# skill-forge

> Self-learning meta-skill. When an agent hits a knowledge gap on a
> topic — a library, framework, tool, or domain — skill-forge researches
> it and synthesizes a focused, portable `skills/<slug>/SKILL.md`,
> creating a new skill or improving a related one it made earlier. Broad
> topics that span several skills fan out into multiple skills, forged in
> parallel. Self-contained; every external dependency is capability-
> referenced with a built-in fallback.

**Skill file:** [`skills/skill-forge/SKILL.md`](../../skills/skill-forge/SKILL.md)
**Version:** 1.0.0

## Purpose

skill-forge turns a knowledge gap into a reusable, portable skill. Invoked with a `topic` (and an optional `task_context`), it:

- **Finds** existing published skills to use as *source material* (never installed verbatim).
- **Researches** the topic on the web, then **verifies** the findings against their cited sources (a fact-check pass).
- **Synthesizes** a new `SKILL.md` following the canonical 10-section `standard` template — or **improves** a related skill it made earlier (append-only).
- **Self-reviews** the result across 18 dimensions before returning it.

Every skill it produces is project-agnostic and agent-agnostic, carries a `forge:` mark so it can be improved later, and is returned inline for immediate same-turn use.

## When to activate

- ✅ An agent or user hits a knowledge gap on a specific topic/library/framework/tool/domain and wants a reusable skill.
- ✅ "Research X and turn it into a skill."
- ✅ Extending a related forge-made skill with new coverage (improve mode).
- ✅ A broad topic that should become several focused skills (multi-skill fan-out).

### When NOT to activate

- The topic is project-specific and can't be generalized — write a project-local note instead.
- The topic is `skill-forge` itself or a self-recursion alias — the recursive-forge guard refuses.
- The topic is too vague to name a concrete subject — refine it first.

## Workflow (8 steps)

| Step | Role |
|---|---|
| 0 Resolve workspace root | Find the workspace marker; abort cleanly if run outside it. |
| 1 Topic triage | Recursive-forge guard + slug normalize; decide **cache / improve / create** (cache + improve apply only to `forge:`-marked skills); name-clash → `F9`; low confidence → ask upfront; breadth → fan-out. |
| 2 Acquire (find → research → verify) | Discover existing skills as source material, research the web, fact-check findings against their sources. Synthesize-only. |
| 3 Synthesis | Assemble the 10-section SKILL.md (everything paraphrased); portability + description-injection guards. |
| 4 Write to disk | Self-contained write; script validation gate; 6-check verification gate; **min-2/max-5 fresh-reviewer** self-review loop. |
| 5 Return inline | Hand the finished SKILL.md back for same-turn use. |
| 6 Caller-file log (optional) | Append a learning-log entry to a passed agent file (idempotent). |
| 7 Done | |

A broad topic (e.g. "MERN stack") triggers the **multi-skill fan-out**: ask for task context, recommend a task-tailored skill list, confirm, then forge each via a parallel worker (≤5 at a time).

## Key guarantees

- **Synthesize-only** — found skills are source material; skill-forge always writes its own forge-marked skill, never installs a third party's verbatim.
- **Self-contained output** — everything a generated skill needs lives under `skills/<slug>/`; nothing outside is touched.
- **Capability-based dependencies** — discovery, research, reviewer, sanitizer, and verification deps are referenced by *capability* with a built-in fallback; no hard dependency on any named skill.
- **Honest posture** — never commits on its own (prints a commit hint); external reads are sanitized; untrusted topic/task input is treated as data.
- **Human approval is the final gate** — every generated skill ships `forge.status: unreviewed`.

## Limitations

- **Probabilistic** — the workflow is instructions an LLM follows, not enforced code.
- **Research accuracy bounded by sources** — the verify pass + self-review reduce but don't eliminate confidently-wrong web findings.
- **Self-review cost** — up to 5 fresh-reviewer cycles per skill.
- **No instantiation of the host** — it writes skill files + returns content; landing/committing is the human's call.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
