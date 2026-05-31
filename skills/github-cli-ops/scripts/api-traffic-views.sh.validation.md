# Validation — `api-traffic-views.sh`

**What it does:** API fallback — `gh api repos/{owner}/{repo}/traffic/views` (no first-class command).

**Static validation (2026-05-31):**
- `bash -n api-traffic-views.sh` → pass (syntax OK).
- `shellcheck` → not installed in this environment; skipped (re-run when available).
- Guards: `set -euo pipefail`; requires `GH_TOKEN` in env (`: "${GH_TOKEN:?…}"`); validates positional args with `:?` usage messages.

**Auth:** the token is read only from `GH_TOKEN` in the environment (per-call auth, see `references/auth.md`); never printed. No `gh auth switch`.

**Live validation (Phase 2.E, 2026-05-31):** PASS — the operation this script encodes was exercised end-to-end against real github.com (`bm629`) in the guarded live smoke (create -> verify -> delete on a throwaway private repo; per-call `GH_TOKEN`; only the intended repo touched; zero residue).
