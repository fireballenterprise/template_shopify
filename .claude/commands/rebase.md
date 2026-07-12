---
description: Rebase current branch onto the remote default branch. Optionally runs squash first before rebasing.
subtask: false
agent: general
slash_command: /rebase
allowed-tools: Bash(uv run --no-sync *)
---

Run `uv run --no-sync invoke repo.rebase` using the Bash tool.

If it fails (e.g. merge conflicts during the rebase), show the full output to the user and ask how
they'd like to proceed — do not run further git commands automatically.
