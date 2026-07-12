---
description: Push the current feature branch, then draft PR notes and open a Pull Request via gh.
subtask: false
agent: general
slash_command: /punch-it-chewy
allowed-tools: Bash(uv run --no-sync *)
---

First, run the `/docs` audit and let the user review its checklist and approve or decline any
fixes it finds. Only move on to the steps below once that's settled.

Run the push workflow: run `uv run --no-sync invoke repo.push` using the Bash tool. If it fails,
show the full output to the user, explain which stage failed, and ask how they'd like to proceed —
do not continue to the PR steps below.

Then follow the `/pr` steps: gather the branch/diff context via `uv run --no-sync invoke repo.pr_diff`,
write a `## Summary` and `## Changes` description, then create the PR with
`uv run --no-sync invoke repo.pr_create --title="<title>" --content="<notes>"`. Report the PR URL
to the user.
