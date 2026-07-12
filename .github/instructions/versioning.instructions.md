---
description: "Use when checking or updating dependency version locks or GitHub Actions action-ref pins. Covers the ver.* invoke tasks and their modules."
applyTo: "modules/versioning/**"
---
# Versioning Instructions

## Purpose
Two checks against external sources of truth:
- `ver.libs` — compares `pyproject.toml`'s `[project.dependencies]` against the latest
  published package releases (via `uv pip list [--outdated]`), and rewrites just the version locks
- `ver.workflows` — compares `.github/workflows/*.yml`'s `uses: owner/repo@vN` refs against
  the latest major tag published on GitHub for that action, and rewrites just the ref pins

See `modules/versioning/README.md` for full behavior/data-flow details on each. For upstream
Shopify/dawn version tags and Dawn upgrades, see `dawn.instructions.md` — that's a separate
module (`modules/dawn/`), not part of this one.

## Usage
```sh
uv run --no-sync invoke ver.libs        # check + prompt to update pyproject.toml locks
uv run --no-sync invoke ver.workflows    # check + prompt to update workflow action refs
uv run --no-sync invoke ver.all          # libs + workflows together
uv run --no-sync invoke ver.libs --dry-run   # preview only, never writes (also on workflows/all)
uv run --no-sync invoke ver.libs --yes       # skip the confirmation prompt (also on workflows/all)
```
`/versioning [libs | workflows | all]` runs the same checks and walks through applying them.

## Relationship to Other Workflows
- `ver.libs` only edits `pyproject.toml` — run `uv run --no-sync invoke uv.upgrade`
  (`uv sync`) afterward to actually install the new versions
- `ver.workflows` only edits `.github/workflows/*.yml` — run
  `uv run --no-sync invoke tests.actionlint` afterward to confirm nothing broke

## Module Conventions
- Same conventions as `modules.instructions.md` generally — `main()` entry point per module,
  `subprocess.run([...], cwd=repo_path)` never `shell=True`, output via `modules.common.utils`
- Both `lib.py`/`workflows.py` use `@click.command()` with `--dry-run`/`--yes` options
