---
description: Auto-fix Python and Shopify theme linting issues. Use when you want to run ruff --fix, ruff format, and theme-check --auto-correct.
subtask: false
agent: general
slash_command: /fix
allowed-tools: Bash(uv run --no-sync *)
---

Run `uv run --no-sync invoke fix` using the Bash tool, then report the output to the user.
