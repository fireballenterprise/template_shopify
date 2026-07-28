Gather the branch and diff context:

Run this terminal command:

```
uv run --no-sync invoke repo.pr_diff
```

Using the branch, commit log, and diff above, write a Pull Request description using the canonical
format from `.github/instructions/git.instructions.md` (`## Summary` + `## Changes`).

Then:
- If you were invoked directly by the user (they typed `/pr-notes`), save the notes by running:
  `uv run --no-sync invoke repo.pr_notes_save --content="<the notes>"`
  Report the saved file path to the user — they may copy/paste it into an existing PR description.
- If you are running as a step inside another command (e.g. `/pr`), do not save — just hold the
  composed notes so that command can use them directly.
