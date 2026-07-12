---
name: sync-setup
description: Pull shared tooling updates (modules/, tasks/, .github/, .claude/, config files) from the repo_setup_python skeleton repo into this project, asking about anything ambiguous or conflicting.
argument-hint: no arguments required
agent: agent
---

Locate the shared skeleton repo:

!`uv run --no-sync invoke skeleton.locate_source`

The line above starting with `SKELETON_PATH=` is the resolved local path to the skeleton repo
(cloned to `tmp/skeleton_sync/` if it wasn't found locally).

Compare that skeleton repo against this project and sync it in:

1. **Always exclude** (never touch, even if present in the skeleton): `properties.yml`,
   `README.md`, `LICENSE`, `uv.lock`, `pyproject.toml`, `.claude/settings.local.json`, `.git/`,
   `.venv/`, `__pycache__/`, `.ruff_cache/`, any other cache/build artifact, and anything under
   `logs/` or `tmp/`.
2. **Shared tooling — sync these by default** if present in the skeleton: `modules/`, `tasks/`,
   `.github/instructions/`, `.github/prompts/`, `.github/workflows/`, `.claude/commands/`,
   `.vscode/`, `invoke.yml`, `setup.sh`, `CLAUDE.md`, `.editorconfig`, `.yamllint`. Also look at
   anything else at the skeleton's top level that isn't covered by the exclude list — use judgment
   on whether it's generic tooling or project-specific, and ask the user if genuinely unsure.
3. For each candidate file:
   - Missing in this project → propose adding it.
   - Identical to what's already here → skip silently.
   - Different from what's already here → show a short diff and ask the user whether to overwrite,
     keep the local version, or merge by hand. Do not overwrite silently.
4. Apply only the changes the user approved (plus unambiguous additions/identical-skips), then
   summarize what was added, updated, and skipped.
5. If `.github/prompts/` changed, remind the user to run `uv run --no-sync invoke claude.sync`
   (add `--force` to overwrite hand-crafted `.claude/commands/`) afterward — do not run it
   automatically.

Never modify `pyproject.toml`, `properties.yml`, `README.md`, `LICENSE`, or `uv.lock` even if the
skeleton's versions differ from this project's — those are always project-specific and must be
reconciled by hand.
