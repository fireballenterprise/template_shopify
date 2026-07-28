---
description: Run tests, audit docs for drift (/docs), push the current feature branch, then draft PR notes and open a Pull Request via gh.
subtask: false
agent: general
slash_command: /punch-it-chewy
allowed-tools: Bash(uv run --no-sync *)
---

First, follow the `/test` steps to run all tests and linters, auto-fixing what can be fixed. Do not
continue until tests pass — if they don't, show the failures and ask the user how they'd like to
proceed.

Then follow the `/docs` steps to audit the repo for doc/AI-config drift against recent changes and
fix anything stale.

Then follow the `/push` steps (fix, test, commit, and push — this commit picks up any doc edits
from the step above). If it fails at any stage, show the full output to the user, explain which
stage failed, and ask how they'd like to proceed — do not continue to the PR steps below.

Then follow the `/pr` steps: gather the branch/diff context via `uv run --no-sync invoke repo.pr_diff`,
write a `## Summary` and `## Changes` description, then create the PR with
`uv run --no-sync invoke repo.pr_create --title="<title>" --content="<notes>"`. Report the PR URL
to the user.
