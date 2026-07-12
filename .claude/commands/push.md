---
description: Push changes to git remote. Runs invoke fix, invoke test, then commits and pushes.
subtask: false
agent: general
slash_command: /push
allowed-tools: Bash(uv run --no-sync *)
---

Run `uv run --no-sync invoke repo.push` using the Bash tool. This runs fix, test, commit, and push.

If it fails at any stage (fix, test, commit, or push), show the full output to the user, explain
which stage failed, and ask how they'd like to proceed — do not retry automatically.
