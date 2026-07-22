---
description: "Use when working on overall project structure, conventions, dependencies, or setup. Covers project layout, pyproject.toml, invoke.yml, and general organization."
---
# Project Instructions

## Overview
Shopify Dawn theme fork for Fireball Enterprise (fireballenterprise.com). Uses [Invoke](https://www.pyinvoke.org/) for local task automation and [uv](https://docs.astral.sh/uv/) for dependency/environment management. Targets Python `>=3.14`. Theme files are synced to Shopify via `shopify theme pull/push`; tooling files (modules/, tasks/, .github/) are local-only.

## Project Structure
```
pyproject.toml    # Dependencies, ruff/pylint config
invoke.yml        # Invoke config (auto_dash_names: false)
setup.sh          # Shell-based setup script (uv venv + uv sync)
properties.yml    # Repo path + remote + template config; points to tmp/.shopify/config.yml for Shopify store/theme IDs
assets/           # Theme JS, CSS, images (synced to Shopify)
config/           # Theme settings schema (synced to Shopify)
layout/           # Theme layout files (synced to Shopify)
locales/          # Translation files (synced to Shopify)
sections/         # Theme sections (synced to Shopify)
snippets/         # Theme snippets (synced to Shopify)
templates/        # Theme templates (synced to Shopify)
modules/
  common/         # cli.py, properties.py, route_utils.py, utils.py — shared helpers
  repo/           # pull.py, push.py, log.py, squash.py, rebase.py — git workflow modules
  shopify/        # pull.py, upgrade.py, env.py — Shopify theme workflow modules
  template/       # pull.py, push.py, resolve.py, route.py, scope.py — sync shared tooling with the parent template repo for /template
  versioning/     # libs.py, python.py, workflows.py, upgrade.py, project.py — check pyproject.toml deps, Python version & workflow action refs vs. latest releases; install upgrades; bump the repo's VERSION file
tasks/
  __init__.py     # Wires the invoke Collection (repo, shopify, ruff, template, tests, upgrade, ver, version, fix, test, update)
  repo.py         # repo.pull, repo.push, repo.log, repo.squash, repo.rebase
  shopify.py      # shopify.pull, shopify.upgrade, shopify.fix, shopify.env
  ruff.py         # ruff.fix, ruff.format
  template.py     # template.pull, template.push_diff, template.push_apply, template.push_create_pr
  tests.py        # tests.actionlint, tests.pylint, tests.rufflint, tests.theme_check, tests.yamllint
  upgrade.py      # upgrade (default), upgrade.python, upgrade.libs, upgrade.sync — installs; run ver.update first
  version.py      # version.bump_build, version.bump_release — kept stable for the reusable deploy/release workflows
  versioning.py   # ver.libs, ver.python, ver.workflows, ver.all, ver.update, ver.upgrade, ver.project_bump_build, ver.project_bump_release
  combos.py       # Top-level aliases: fix, test, update
.github/
  instructions/   # Copilot instruction files
  prompts/        # Copilot prompt files (/push, /pull, /test, /fix, /shopify, /pr, etc.)
  workflows/      # GitHub Actions CI workflows
```

## Key Conventions
- Shopify theme dirs (`assets/`, `sections/`, etc.) are synced via Shopify CLI — do not add Python tooling there
- All hand-written customizations on top of stock Dawn are tracked in
  `fireball.instructions.md` — whenever a customization is added, disabled (commented out),
  or removed, update its row in that table in the same change
- `tasks/__init__.py` builds the root `Collection` — every new task module must be imported and wired there explicitly (no auto-glob loading)
- `modules/` are plain importable Python packages (`modules.common`, `modules.repo`, `modules.shopify`) — imported directly by `tasks/*.py`
- `invoke.yml` sets `auto_dash_names: false` so task names keep underscores (e.g. `repo.pull`, not `repo.pull-dash`)

## Dependencies (pyproject.toml)
- `invoke` — task runner
- `ruff` — fast Python linter/formatter
- `pylint` — deep static analysis (10/10 required to pass `invoke test`)
- `yamllint` — YAML linting
- `actionlint-py` — GitHub Actions workflow linting (pip-installed, no Homebrew required)
- `pyyaml` — reads `properties.yml`
- Shopify theme linting uses the `shopify theme check` CLI command (installed via `npm install -g @shopify/cli`) — not a Python dependency
- `gh` (GitHub CLI) — required for `repo.pr_create` / `/pr-notes` / `/punch-it-chewy` (not a pip package; install via Homebrew, must be authenticated)

## Git Branch Architecture
```
upstream/main (Shopify/dawn)
      │
      ▼
dawn_vanilla      # Tracks upstream Shopify Dawn — never customized
      │
      ▼
development       # Integration branch — custom work merged here
      │
      ▼
main              # Production branch — only promoted from development
```
- `dawn_vanilla` — local branch that pulls from `upstream/main` (Shopify's repo). Keeps Shopify's history separate from custom code.
- `development` — active development branch. PRs merge here; deploys to the dev Shopify theme on merge.
- `main` — production branch. Only updated via the Release workflow's `promote` job (manual dispatch of `release.yml`). Deploys to live store.
- `feature/*` — short-lived feature branches; PR targets `development`.
- Upstream Dawn upgrades: `uv run --no-sync invoke shopify.upgrade` fetches `upstream/main` → merges into `dawn_vanilla` → merges into `development`. No manual branch switching needed.

## Running Tasks
```sh
uv run --no-sync invoke              # List all tasks (or: uv run --no-sync invoke -l)
uv run --no-sync invoke test         # Ruff + Pylint + theme-check + yamllint + actionlint
uv run --no-sync invoke fix          # Ruff autocorrect + format + theme-check autocorrect
uv run --no-sync invoke repo.pull    # Pull from git remote (stash → pull → restore)
uv run --no-sync invoke repo.push    # Push to git remote (fix → test → commit → push)
uv run --no-sync invoke repo.log     # Save a session log to logs/
uv run --no-sync invoke repo.pr_diff       # Print current branch's commit log/diff vs. its base branch
uv run --no-sync invoke repo.pr_notes_save # Save PR notes to tmp/pull_requests/ (--content=...)
uv run --no-sync invoke repo.pr_create     # Open a GitHub PR via gh (--title=... --content=...)
uv run --no-sync invoke shopify.pull # Pull live theme from Shopify store → local repo
uv run --no-sync invoke shopify.upgrade # Upgrade dawn_vanilla from upstream Shopify/dawn
uv run --no-sync invoke shopify.env # Print Shopify CLI env var exports (eval "$(uv run --no-sync invoke shopify.env)")
shopify theme push         # Push local theme → Shopify store
uv run --no-sync invoke template.pull           # Resolve the parent template repo's local path for /template
uv run --no-sync invoke template.push_diff      # Diff this repo's scoped tooling against the parent template repo
uv run --no-sync invoke template.push_apply     # Copy approved files/deletions to a new branch upstream and push it
uv run --no-sync invoke template.push_create_pr # Open a PR for that branch against the parent template repo
uv run --no-sync invoke ver.libs      # Check pyproject.toml deps vs. latest releases, update version locks
uv run --no-sync invoke ver.python    # Check the pinned Python version vs. latest stable, update config refs
uv run --no-sync invoke ver.workflows # Check .github/workflows/ action refs vs. latest major versions
uv run --no-sync invoke ver.update    # Run every version check (libs, python, workflows) — same as top-level `update`
uv run --no-sync invoke ver.upgrade   # Install the upgrades reviewed via ver.update — same as top-level `upgrade`
uv run --no-sync invoke upgrade.python # Upgrade Python only (installs, rebuilds .venv)
uv run --no-sync invoke upgrade.libs   # Upgrade libraries only (uv sync --upgrade)
uv run --no-sync invoke version.bump_build   # Dev deploy: new minor's first VERSION build, or next build number
uv run --no-sync invoke version.bump_release # Release: drop the VERSION build suffix
```
