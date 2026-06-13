# Validation: create-site.sh

- **Method**: syntax check (`bash -n`); commands verified against the official `netlify` CLI docs (`assets/cli-index.md`).
- **Tools**: `bash -n` (clean); shellcheck not installed — skipped. (The `netlify` CLI is not installed locally — not run live.)
- **Date**: 2026-06-12
- **Exit codes**: `bash -n`: 0.

## Captured output

`bash -n` clean. Runs `netlify sites:create --name <name> [--account-slug <slug>] --disable-linking --json` — the verified create-site command; `--json` for machine output; `--disable-linking` so it does not touch a working dir. Returns the site as JSON; the id is the `id` field (`sites:create --json` returns the id under `id`, not `site_id` — `.site_id` is null on create). Live-verified 2026-06-13 (create → deploy → poll-ready → cleanup against api.netlify.com).

## Caveats

- Run live 2026-06-13 (Phase 2.D smoke): create-site → deploy → status → cleanup all green.
- REST fallback documented in the comment (`netlify api createSite` / `POST /sites`).
