---
description: "Use when checking or updating dependency version locks or GitHub Actions action-ref pins. Covers the ver.* invoke tasks and their modules."
applyTo: "modules/versioning/**"
---
# Versioning Instructions

## Purpose
Three checks against external sources of truth, plus the repo's `VERSION`-file bump (`project.py`,
also reachable as `version.bump_build`/`version.bump_release` — see `version.instructions.md`) and
the installs that follow (`upgrade.py`):
- `ver.libs` — compares `pyproject.toml`'s `[project.dependencies]` against the latest
  published package releases (via `uv pip list [--outdated]`), and rewrites just the version locks
- `ver.python` — compares the pinned Python version against the latest stable 3.x release, and
  rewrites the config file references (does not install)
- `ver.workflows` — compares `.github/workflows/*.yml`'s `uses: owner/repo@vN` refs against
  the latest major tag published on GitHub for that action, and rewrites just the ref pins

See `modules/versioning/README.md` for full behavior/data-flow details on each. For upstream
Shopify/dawn version tags and Dawn upgrades, see `dawn.instructions.md` — that's a separate
module (`modules/dawn/`), not part of this one.

## Usage
```sh
uv run --no-sync invoke ver.libs        # check + prompt to update pyproject.toml locks
uv run --no-sync invoke ver.python      # check + prompt to update the pinned Python version
uv run --no-sync invoke ver.workflows    # check + prompt to update workflow action refs
uv run --no-sync invoke ver.all          # libs + workflows together
uv run --no-sync invoke ver.update       # libs + python + workflows together (same as top-level `update`)
uv run --no-sync invoke ver.libs --dry-run   # preview only, never writes (also on python/workflows/update)
uv run --no-sync invoke ver.libs --yes       # skip the confirmation prompt (also on python/workflows/update)

uv run --no-sync invoke ver.project_bump_build    # dev deploy: new minor's first build, or next build number
uv run --no-sync invoke ver.project_bump_release  # release: drop the build suffix

uv run --no-sync invoke ver.upgrade      # install the upgrades reviewed above (same as top-level `upgrade`)
```
`/versioning [libs | workflows | all]` runs the read-only libs/workflows checks. `/update [libs |
python | workflows]` runs all three (including Python) and walks through applying them; `/upgrade`
executes the actual installs afterward.

## Relationship to Other Workflows
- `ver.libs` only edits `pyproject.toml` — run `uv run --no-sync invoke upgrade.libs`
  (`uv sync --upgrade`) afterward to actually install the new versions
- `ver.python` only edits config file references — run `uv run --no-sync invoke upgrade.python`
  afterward to install the new Python and rebuild `.venv`
- `ver.workflows` only edits `.github/workflows/*.yml` — run
  `uv run --no-sync invoke tests.actionlint` afterward to confirm nothing broke

## Module Conventions
- Same conventions as `modules.instructions.md` generally — `main()` entry point per module,
  `subprocess.run([...], cwd=repo_path)` never `shell=True`, output via `modules.common.utils`
- `libs.py`/`python.py`/`workflows.py` use `@click.command()` with `--dry-run`/`--yes` options
