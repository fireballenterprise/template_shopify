---
name: push
description: Push changes to git remote. Runs invoke fix, invoke test, then commits and pushes.
argument-hint: no arguments required
agent: agent
---

!`uv run --no-sync invoke repo.push`
