---
name: pr-cleanup
description: Clean up after a merged PR — switch to the default branch, pull, and delete the merged local feature branch.
argument-hint: no arguments required
agent: agent
---

!`uv run --no-sync invoke repo.pr_cleanup`
