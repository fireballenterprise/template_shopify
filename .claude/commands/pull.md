---
description: Pull updates from git remote. Stashes local changes, pulls with rebase, then restores stash.
subtask: false
agent: general
slash_command: /pull
allowed-tools: Bash(uv run --no-sync *)
---

Run `uv run --no-sync invoke repo.pull` using the Bash tool.

If it fails, show the full output to the user and ask how they'd like to proceed — do not retry or
run further git commands automatically.
