---
description: Clean up after a merged PR. Switches to the default branch, pulls, and deletes the merged local feature branch.
subtask: false
agent: general
slash_command: /pr-cleanup
allowed-tools: Bash(uv run --no-sync *)
---

Run `uv run --no-sync invoke repo.pr_cleanup` using the Bash tool.

If it fails (e.g. the PR isn't merged yet, or there are uncommitted changes), show the full output
to the user and ask how they'd like to proceed — do not run further git commands automatically.
