Gather the branch and diff context:

Run this terminal command:

```
uv run --no-sync invoke repo.pr_diff
```

Using the branch, commit log, and diff above, write a Pull Request description (same as `/pr-notes`,
but do NOT save it to a file this time — just hold it in context). Use the canonical PR format
from `.github/instructions/git.instructions.md` (`## Summary` + `## Changes`).

Then create the pull request:
1. Note the `Base branch:` value printed above.
2. Draft a concise PR title (under 70 characters) summarizing the change.
3. Run:
   `uv run --no-sync invoke repo.pr_create --title="<title>" --content="<notes>"`
4. Report the PR URL to the user.

If a PR already exists for this branch, `repo.pr_create` reports its URL instead of erroring —
just relay that to the user.
