---
name: punch-it-chewy
description: Push the current feature branch, then draft PR notes and open a Pull Request via gh.
argument-hint: no arguments required
agent: agent
---

First, run the `/docs` audit (see `docs.prompt.md`) and let the user review its checklist and
approve or decline any fixes. Only move on once that's settled.

Then run the push workflow:

!`uv run --no-sync invoke repo.push`

Then follow the `/pr-notes` steps: gather the branch/diff context via `uv run --no-sync invoke repo.pr_diff`,
write a `## Summary` and `## Changes` description, then create the PR with
`uv run --no-sync invoke repo.pr_create --title="<title>" --content="<notes>"`. Report the PR URL
to the user.
