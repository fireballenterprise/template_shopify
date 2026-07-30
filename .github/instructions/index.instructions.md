---
description: "Use when working on overall project structure, conventions, dependencies, or setup. Covers project layout, pyproject.toml, invoke.yml, and general organization."
---
# Project Instructions

## Overview
Python-based project using [Invoke](https://www.pyinvoke.org/) for task automation and [uv](https://docs.astral.sh/uv/) for dependency/environment management. Targets Python `>=3.14`.

## Instruction Files
Operational guidance for this repo is split into focused files under `.github/instructions/`, each
scoped to one concern — load only the ones relevant to the task at hand:
- `index.instructions.md` — this file: project structure, conventions, dependencies, setup (start here)
- `logic.instructions.md` — AI decision architecture, modules/tasks/AI stack, provider hierarchy
- `python.instructions.md` — Python version, style, module/logging/subprocess conventions
- `modules.instructions.md` — Python module architecture and layout conventions
- `tasks.instructions.md` — invoke task runner and Collection wiring (plain CLI automation, no AI)
- `versioning.instructions.md` — `modules/versioning/` package: VERSION bumps and dependency/action version checks
- `dawn.instructions.md` — upstream Shopify/dawn version listing and upgrade conventions
- `shopify.instructions.md` — Shopify theme conventions
- `fireball.instructions.md` — Fireball customization tracking
- `prompts.instructions.md` — AI custom prompts / slash command standards and templates
- `skills.instructions.md` — Agent Skill (SKILL.md) conventions for `.claude/skills/` and `.github/skills/`
- `git.instructions.md` — branch naming and Pull Request description conventions
- `review.instructions.md` — PR/code-review priorities
- `tests.instructions.md` — testing requirements and workflow
- `style.instructions.md` — Markdown style and alphabetical-ordering rules
- `docs.instructions.md` — README and inline-comment conventions

## Project Structure
```
pyproject.toml    # Dependencies, ruff/pylint/pytest config
invoke.yml        # Invoke config (auto_dash_names: false)
setup.sh          # Shell-based setup script (uv venv + uv sync)
properties.yml    # Project configuration (repo path/remote, template path/remote)
template.ignore.yml # Extra paths /template pull must never overwrite, on top of its built-in safety excludes
tests/
  test_check_agents.py # Verify .github/prompts/ mirrors are in sync, called by tests.check_agents
modules/
  common/         # cli.py, properties.py, utils.py, shopify.py, route_utils.py — shared helpers
  dawn/           # list.py, version.py, upgrade.py — list upstream Shopify/dawn tags, print the checked-out version, merge dawn_vanilla upgrades
  repo/           # pull.py, push.py, log.py, squash.py, rebase.py, pr_*.py, route.py — git/PR workflow modules
  setup/          # properties.py — creates/stamps properties.yml, called by setup.sh/setup.ps1
  shopify/        # deploy.py, env.py, pull.py, upgrade.py — Shopify CLI theme sync (not part of the shared template_python repo)
  template/       # ignore.py, naming.py, pull.py, push.py, resolve.py, route.py, scope.py — sync shared tooling with the parent template repo for /template
  versioning/     # libs.py, python.py, workflows.py, upgrade.py, project.py — check pyproject.toml deps & workflow action refs vs. latest releases, bump the repo's VERSION file
tasks/
  __init__.py     # Wires the invoke Collection (dawn, debug, repo, ruff, setup, shopify, template, tests, upgrade, uv, versioning) plus top-level aliases (fix, test, update)
  combos.py       # Top-level aliases: fix, test, update
  dawn.py         # dawn.list, dawn.version, dawn.upgrade
  debug.py        # debug.env — print cwd + sorted env vars
  repo.py         # repo.pull, repo.push, repo.log, repo.squash, repo.rebase, repo.pr_diff, repo.pr_notes_save, repo.pr_create, repo.pr_cleanup
  ruff.py         # ruff.fix, ruff.format
  setup.py        # setup.properties — creates/stamps properties.yml
  shopify.py      # shopify.deploy, shopify.env, shopify.fix, shopify.pull, shopify.upgrade
  template.py     # template.pull, template.pull_copy, template.push_diff, template.push_apply, template.push_create_pr
  tests.py        # tests.actionlint, tests.check_agents, tests.pylint, tests.pytest, tests.rufflint, tests.yamllint, tests.theme_check
  upgrade.py      # upgrade (default), upgrade.python, upgrade.libs, upgrade.sync — installs; run ver.update first
  uv.py           # uv.upgrade_bin, uv.upgrade_libs
  versioning.py   # ver.libs, ver.python, ver.workflows, ver.all, ver.update, ver.upgrade, ver.project_bump_build, ver.project_bump_release
.github/
  instructions/   # Copilot instruction files
  prompts/        # Copilot prompt files (/push, /pull, /squash, /rebase, /fix, /test, /docs, /pr-notes, /pr, /pr-cleanup, /punch-it-chewy, /template, /update, /upgrade, /repo, /setup) — source of truth for slash commands
  workflows/      # tests.yml (reusable), feature_branches.yml, protected_branches.yml
.claude/
  commands/       # Claude Code slash commands, hand-maintained mirror of .github/prompts/ (see prompts.instructions.md)
  skills/         # Claude Code skills (auto-discovered), hand-maintained mirror of .github/prompts/ (see prompts.instructions.md)
.clinerules/
  workflows/      # Cline slash commands, hand-maintained mirror of .github/prompts/ (see prompts.instructions.md)
.vscode/
  extensions.json # Recommended VS Code extensions
  settings.json   # Ruff formatter + Python interpreter settings
addons/
  shopfiy_dawn_theme/ # Shopify Dawn theme addon — see "Addons" in README.md before using
```

## Key Conventions
- `tasks/__init__.py` builds the root `Collection` — all task modules are wired explicitly (no auto-glob loading, unlike the Rake-based sibling project)
- `modules/` are plain importable Python packages (`modules.common`, `modules.repo`, `modules.template`) — imported directly by `tasks/*.py`
- Every `modules/repo/*.py` file exposes a `main()` entry point, runnable standalone via `python -m modules.repo.<name>`
- `invoke.yml` sets `auto_dash_names: false` so task names keep underscores (e.g. `repo.pull`, not `repo.pull-dash`)
- `.github/prompts/` is the source of truth for slash commands; `.claude/commands/`,
  `.claude/skills/`, and `.clinerules/workflows/` mirror it by hand — see `prompts.instructions.md`
- Always run `uv run --no-sync ...`, never bare `uv run ...` — without `--no-sync`, `uv run` re-resolves and may silently upgrade a dependency before the command runs. Any dependency change must go through an explicit `uv sync`/`uv lock` step that the user can review, not an implicit one buried inside a task run
- `addons/<name>/` mirrors the root layout but is not usable from this repo's root — its files must
  be copied into a consuming repo's actual root (root-relative imports, `applyTo` globs, and task
  wiring all assume that). Excluded from `ruff`/`pylint` via `pyproject.toml`
  (`extend-exclude`/`ignore-paths`) for the same reason — see "Addons" in `README.md`
- `.github/instructions/fireball.instructions.md` tracks this repo's own hand-written Shopify
  theme customizations — every clone of `template_shopify` (this repo, under the
  `fireballenterprise` GitHub org) is a Fireball-brand Shopify site, so the filename stays
  `fireball.instructions.md` in every one of them; each repo keeps its own separate tracking
  table (not synced content). Listed in `template.ignore.yml` so `/template pull` never
  overwrites it

## Dependencies (pyproject.toml)
- `invoke` — task runner
- `ruff` — fast Python linter/formatter
- `pylint` — deep static analysis (10/10 required to pass `invoke test`)
- `pytest` / `pytest-cov` — unit tests (`tests/`, e.g. `test_check_agents.py`)
- `yamllint` — YAML linting
- `actionlint-py` — GitHub Actions workflow linting (pip-installed, no Homebrew required)
- `pyyaml` — reads `properties.yml`

## External Tools
- `gh` (GitHub CLI) — required for `repo.pr_create` / `/pr` / `/punch-it-chewy` (not a pip package; install via Homebrew)

## Running Tasks
```sh
uv run --no-sync invoke          # List all tasks (or: uv run --no-sync invoke -l)
uv run --no-sync invoke test     # ruff + pylint + pytest + yamllint + actionlint + check_agents + theme_check
uv run --no-sync invoke fix      # Ruff autocorrect + format
uv run --no-sync invoke repo.pull   # Pull from git remote (stash → pull --rebase → restore)
uv run --no-sync invoke repo.push   # Push to git remote (fix → test → commit → push)
uv run --no-sync invoke repo.log    # Save a session log to logs/
uv run --no-sync invoke repo.squash # Anchored squash all commits to root + optional force push
uv run --no-sync invoke repo.rebase # Rebase onto remote default branch (optionally squash first)
uv run --no-sync invoke repo.pr_diff       # Print current branch's commit log/diff vs. its base branch
uv run --no-sync invoke repo.pr_notes_save # Save PR notes to tmp/pull_requests/ (--content=...)
uv run --no-sync invoke repo.pr_create     # Open a GitHub PR via gh (--title=... --content=...)
uv run --no-sync invoke repo.pr_cleanup    # Switch to the default branch, pull, and delete the merged local feature branch
uv run --no-sync invoke template.pull           # Resolve the parent template repo's local path for /template
uv run --no-sync invoke template.pull_copy      # Clobber-copy tracked files from a local template repo into this project
uv run --no-sync invoke template.push_diff      # Diff this repo's scoped tooling against the parent template repo
uv run --no-sync invoke template.push_apply     # Copy approved files/deletions to a new branch upstream and push it
uv run --no-sync invoke template.push_create_pr # Open a PR for that branch against the parent template repo
uv run --no-sync invoke ver.libs    # Check pyproject.toml deps vs. latest releases, update version locks
uv run --no-sync invoke ver.python  # Check the pinned Python version vs. latest stable, update config refs
uv run --no-sync invoke ver.all     # Run every version check (libs, workflows)
uv run --no-sync invoke ver.update  # Run every version check (libs, python, workflows) — same as top-level `update`
uv run --no-sync invoke ver.project_bump_build   # Dev build: new minor's first VERSION build, or next build number
uv run --no-sync invoke ver.project_bump_release # Release: drop the VERSION build suffix
uv run --no-sync invoke ver.upgrade    # Install the Python/library upgrades reviewed via ver.update — same as top-level `upgrade`
uv run --no-sync invoke upgrade.python # Upgrade Python only (installs, rebuilds .venv)
uv run --no-sync invoke upgrade.libs   # Upgrade libraries only (uv sync --upgrade)
uv run --no-sync invoke upgrade.sync   # Sync dependencies without checking for updates first
uv run --no-sync invoke uv.upgrade_libs # Install the versions currently locked in pyproject.toml (uv sync)
uv run --no-sync invoke dawn.list       # List every upstream Shopify/dawn tag, latest highlighted
uv run --no-sync invoke dawn.version    # Print the Dawn theme version currently checked out
uv run --no-sync invoke dawn.upgrade    # Merge the upgraded dawn_vanilla into a feature branch for manual conflict resolution
uv run --no-sync invoke shopify.deploy  # Push local theme to Shopify (--env=dev or --env=prd)
uv run --no-sync invoke shopify.env     # Print `export KEY=value` Shopify CLI env vars
uv run --no-sync invoke shopify.fix     # Auto-correct Shopify theme-check offenses
uv run --no-sync invoke shopify.pull    # Pull live theme from Shopify store to local branch (--env=dev/prd or --theme=<name_or_id>)
uv run --no-sync invoke shopify.upgrade # Upgrade dawn_vanilla from upstream Shopify/dawn, then merge into development
```
