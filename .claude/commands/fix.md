---
description: Auto-fix Python linting issues. Use when you want to run ruff check --fix and ruff format.
subtask: false
agent: general
slash_command: /fix
allowed-tools: Bash(uv run --no-sync *)
---

Run `uv run --no-sync invoke fix` using the Bash tool, then report the output to the user.
