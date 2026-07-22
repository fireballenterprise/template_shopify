---
description: Upgrade Python and/or Dependencies
agent: general
subtask: false
slash_command: /upgrade
allowed-tools: Bash(uv run --no-sync *)
---

# upgrade - Upgrade Python and/or Dependencies

Executes upgrades to Python and/or package dependencies after config changes were reviewed
via `/update`. This performs actual installations and syncs:

- Downloads and installs new Python versions (if updated)
- Rebuilds the virtual environment (if Python changed)
- Runs `uv sync --upgrade` to install updated dependencies

## Arguments

`$ARGUMENTS`

## Workflow

Run exactly ONE of the following with the Bash tool, chosen by the arguments given:

- No arguments (upgrade everything): `uv run --no-sync invoke upgrade`
- `python` (Python only): `uv run --no-sync invoke upgrade.python`
- `libs` (libs only): `uv run --no-sync invoke upgrade.libs`
- `sync` (sync deps without checking for updates): `uv run --no-sync invoke upgrade.sync`

Interpret the exit code: 0 = success (upgrades completed or nothing needed), 2 = cancelled.
On any failure, show the full output to the user and ask how to proceed — do not retry
automatically. If a task tries to prompt interactively and fails because there is no TTY,
tell the user and ask whether they want to run it themselves in a terminal.

## Examples

```bash
# Full workflow
/update                    # Review and update all configs
git diff                    # Review changes
/upgrade                    # Execute upgrades

# Python-only workflow
/update python             # Review and update Python configs
/upgrade python             # Execute Python upgrade

# Libs-only workflow
/update libs               # Review and update lib versions in pyproject.toml
/upgrade libs               # Execute libs upgrade
```
