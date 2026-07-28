---
description: Run all tests and linters. Use when you want to run ruff, pylint, yamllint, and actionlint.
subtask: false
agent: general
slash_command: /test
allowed-tools: Bash(uv run --no-sync *)
---

Auto-fix first: run `uv run --no-sync invoke fix` using the Bash tool.

Then run all tests: run `uv run --no-sync invoke test` using the Bash tool.

If all tests pass, report success and stop.

If any tests fail:
- For Ruff offenses that survived the auto-fix: show the remaining failures and ask the user how they would like to proceed.
- For Pylint offenses (must score 10.00/10): show the offending lines and ask the user how they would like to proceed.
- For YAML lint failures: show the offending lines and ask the user how they would like to proceed.
- For actionlint failures: show the offending workflow file and line, and ask the user how they would like to proceed.
- For any other failures: show the full error output and ask the user how they would like to approach fixing it.
