---
description: Repo operations (push, pull)
subtask: false
agent: general
slash_command: /repo
allowed-tools: Bash(uv run --no-sync *)
---

!`uv run --no-sync python -m modules.repo.route "$ARGUMENTS"`
