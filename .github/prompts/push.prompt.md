---
name: push
description: Push changes to git remote. Runs invoke fix, invoke test, then commits and pushes.
argument-hint: no arguments required
agent: agent
---

Run the push workflow:

!`uv run --no-sync python -m modules.repo.push`

If it fails at any stage (fix, test, commit, or push), show the full output to the user, explain
which stage failed, and ask how they'd like to proceed — do not retry automatically.
