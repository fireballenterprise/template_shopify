# Setup Module
One-time and idempotent repo bootstrapping helpers, called by `setup.sh`.

## Commands
```sh
uv run --no-sync invoke setup.properties
```

## What It Does
`properties.yml` is gitignored — it holds machine-specific local paths, so
`modules/setup/properties.py` creates it fresh on first run and only ever rewrites specific keys in
place afterward rather than treating the whole file as disposable:

1. If `properties.yml` doesn't exist, creates it from a built-in template (`_TEMPLATE` in the module).
2. Detects this repo's actual path on disk and its git `origin` remote (if any).
3. Rewrites only `repo.local` and `repo.remote` in place, targeting those specific keys by name —
   every comment and the rest of the file's formatting survives untouched. Also strips any stale
   sections left over from an older template version (e.g. a legacy `screenshots:` block).

Safe to re-run any time: `uv run --no-sync invoke setup.properties`. Re-run it after moving the repo
on disk, renaming it, or pointing it at a new fork — it just re-stamps the same fields with freshly
detected values.

`template.*` can't be fully auto-detected (only the initial guess is) and is left alone once set —
edit it by hand if it needs to point elsewhere.

## Why Not a Placeholder Token?
An earlier version used a literal token (e.g. `PATH_TO_REPO`) that got search-and-replaced. That only
works once — after the token is replaced with a real path, a second run has nothing left to find.
Targeting the YAML key by name works every time, regardless of what value is currently there, which is
what makes re-running after a move/rename safe.

## Files
- `properties.py` — creates/stamps `properties.yml` (used by `inv setup.properties`)
- `README.md` — this file
