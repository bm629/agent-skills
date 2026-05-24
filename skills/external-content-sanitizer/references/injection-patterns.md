# Injection Pattern Catalog

Loaded by `external-content-sanitizer` during Step 2 (regex pre-pass). Six categories, each with a stable workspace-defined `pattern_class` name and default severity. Patterns are case-insensitive unless noted.

**Pattern_class names are workspace-defined and stable.** They appear in the sanitizer's response markers (`[REMOVED: <pattern_class> — severity <level>]`) and in flagged-sources entries. New attack classes added to this taxonomy require an explicit edit to this file AND a commit message that explicitly names the new `pattern_class`.

---

## 1. direct-instruction-injection

**Default severity:** medium

Direct attempts to override the model's instructions with imperative language.

| Pattern (case-insensitive) | Notes |
|---|---|
| `ignore.{0,30}previous.{0,30}instructions` | Classic; high false-positive risk on educational content |
| `disregard.{0,30}all.{0,30}prior` | Variant of "ignore previous" |
| `you are now` | Role-shift attempt |
| `your new task is` | Task-redefinition attempt |
| `forget.{0,30}(your|the).{0,30}(role|instructions)` | Role-erasure attempt |
| `from now on, you (are|will|must)` | Imperative override |

---

## 2. role-hijack

**Default severity:** high

Tokens or constructs designed to make the model believe it has switched into a different role context (developer, system, root user).

| Pattern | Notes |
|---|---|
| `<\|im_start\|>` | OpenAI chat-format token; unambiguous hijack |
| `<\|im_end\|>` | Same |
| `<\|system\|>` | Role-shift token |
| `<\|user\|>` | Role-shift token |
| `<\|assistant\|>` | Role-shift token |
| `\[INST\]` | Llama-style instruction marker |
| `\[/INST\]` | Same |
| `<system>.*?</system>` | Prose role-shift |
| `<\|begin_of_text\|>` | Llama 3 BOS token |

These patterns are unambiguous attack signatures — no legitimate document uses them as content. Default severity high.

---

## 3. tool-use-injection

**Default severity:** high

Attempts to direct the model to use its tools (file write, command execution, network fetch) on the attacker's behalf.

| Pattern (case-insensitive) | Notes |
|---|---|
| `now write.{0,30}(file|to disk)` | Direct file-write directive |
| `execute.{0,30}(command|this in (bash|shell|terminal))` | Command-execution directive |
| `run this in (bash|shell|terminal)` | Variant |
| `fetch.{0,50}(url|endpoint)` | Network-fetch directive |
| `make a (GET|POST|PUT|DELETE) request to` | Same |
| `call.{0,30}(tool|function).{0,30}with` | Tool-invocation directive |
| `please write the following to` | Polite form of file-write directive |
| `write.{0,30}(contents?\|file).{0,50}to.{0,50}/` | Write-X-to-path directive (decision #16: catches "write the contents of X to /tmp/exfil.txt" without a trigger phrase) |
| `(copy\|read\|cat\|paste).{0,30}~/\.[a-zA-Z]+` | Dotfile read/copy directive (~/.bashrc, ~/.ssh, etc.; decision #16) |
| `(read\|copy\|exfiltrate\|leak).{0,30}\.env\b` | Environment-file disclosure (decision #16) |

---

## 4. exfiltration

**Default severity:** high

Attempts to extract sensitive workspace state (API keys, tokens, secrets, internal config) and send it to an attacker-controlled endpoint.

| Pattern (case-insensitive) | Notes |
|---|---|
| `send.{0,30}(api[\s_-]?key|token|password|secret)` | Direct exfiltration |
| `include the user'?s.{0,30}in your` | Indirect exfiltration via response embedding |
| `email.{0,30}(content|response).{0,50}@` | Email-based exfiltration |
| `report back to.{0,30}https?://` | URL-based exfiltration |
| `webhook.{0,30}https?://[^\s]+` | Webhook exfiltration |
| `paste.{0,30}(env|configuration).{0,30}(here|to)` | Environment-variable disclosure |
| `~/\.(bashrc\|zshrc\|ssh\|aws\|kube\|gnupg\|netrc\|pgpass)` | Sensitive dotfile reference by name (decision #16) |
| `(/etc/(passwd\|shadow\|hosts)\|/var/log)` | Sensitive system-path reference (decision #16) |

---

## 5. hidden-content

**Default severity:** medium

Content concealed from human readers but visible to the model — markdown comments, zero-width characters, suspicious unicode.

| Pattern | Notes |
|---|---|
| `<!--[\s\S]*?-->` | HTML comments potentially containing instructions; check content for direct-instruction patterns within |
| `​` (ZWSP), `‌` (ZWNJ), `‍` (ZWJ), `﻿` (BOM) | Zero-width characters; flag if appearing in unexpected positions |
| `‮` (RLO), `‭` (LRO) | Right-to-left / left-to-right override; can hide content visually |
| `\[[0-9;]*[a-zA-Z]` | ANSI escape sequences in plain text |
| `<span style="display:\s*none">` | CSS-hidden content (matters when content is rendered HTML) |

For HTML-comment matches, recursively scan the comment body for patterns from categories 1-4; if any hit, escalate the hidden-content match to that category's default severity.

---

## 6. encoded-payload

**Default severity:** low

Long blobs that look like base64 or URL-encoded data. Often legitimate (cryptographic material, embedded images, large data) but sometimes a vehicle for hidden directives. Default severity low; severity is bumped if surrounding context suggests intent.

| Pattern | Notes |
|---|---|
| `[A-Za-z0-9+/]{64,}={0,2}` | Base64 candidate (≥ 64 chars, valid base64 alphabet) |
| `(%[0-9A-Fa-f]{2}){32,}` | URL-encoded blob (≥ 32 sequential percent-encoded chars) |
| `\\x[0-9a-fA-F]{2}{16,}` | Hex-encoded sequence |

Encoded payloads are often noise. Treat as low-severity by default; the LLM analysis pass at Step 4 may escalate based on what the surrounding text claims about the payload.

---

## Adding new patterns

When a new attack class emerges:

1. Decide whether it fits an existing category or warrants a new one.
2. If new category: pick a stable `pattern_class` name (kebab-case, ≤ 32 chars, descriptive). Add a section above with default severity and pattern table. The `pattern_class` names appear in flagged-sources entries and sanitizer responses, so they are part of the public contract.
3. Commit the catalog update. The commit message must call out the new `pattern_class` name explicitly so it's discoverable via `git log --grep`.
4. Existing flagged-sources entries with old pattern_class names continue to work (no migration needed) — the catalog is additive.
