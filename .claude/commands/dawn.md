---
description: List upstream Shopify/dawn version tags, or merge the upgraded dawn_vanilla into a feature branch and help resolve conflicts. Pass 'list' or 'upgrade'.
subtask: false
agent: general
slash_command: /dawn
---

If $ARGUMENTS doesn't already specify it, ask the user: do you want to `list` available Dawn
versions, or `upgrade` (merge the already-synced `dawn_vanilla` into a feature branch)?

## `list`

Run `uv run --no-sync invoke dawn.list` using the Bash tool and show the output to the user as-is.
It lists every upstream Shopify/dawn tag with the latest highlighted, and what `dawn_vanilla` is
currently synced to. Nothing to apply — stop here for this case.

## `upgrade`

1. If unclear, confirm with the user that `dawn_vanilla` has already been synced to the target
   version via the "Upgrade" GitHub Actions workflow (`.github/workflows/upgrade.yml`) — this
   command only merges whatever `origin/dawn_vanilla` already contains, it doesn't fetch/merge
   upstream itself and takes no version argument.
2. Check the branch state with `git branch --show-current` (and `git branch --list` if needed):
   - If the user already cut a feature branch for this upgrade, make sure it's checked out —
     the task merges into the **current** feature branch.
   - If on `development`/`main`/`dawn_vanilla`, the task cuts (or reuses)
     `upgrade/dawn-vanilla-v<version>` off `origin/development` itself.
   - If the current feature branch is clearly for unrelated work in progress, ask the user
     before merging an upgrade into it.
3. Run `uv run --no-sync invoke dawn.upgrade` using the Bash tool.
4. If it reports a clean merge (or that `dawn_vanilla` is already merged), there's nothing more
   to do — tell the user to run `/push` then `/pr` to open the PR into `development`.
5. If it reports conflicts, read `.github/instructions/fireball.instructions.md`'s tracking table
   first — it lists every hand-written Fireball customization, its files, and its status. Then
   work through each conflicted file:
   - Look at both sides of the conflict (`<<<<<<<` / `=======` / `>>>>>>>` markers) and find the
     `Fireball -` marker comments to identify what's ours.
   - Where the tracking table plus the diff make the right resolution clear (e.g. upstream
     changed code adjacent to a marked Fireball block — keep both, re-inserting our block into
     upstream's new structure), resolve it yourself and summarize what you did per file.
   - Where it's genuinely ambiguous — upstream deleted or rewrote something we customized, or a
     file Dawn deleted upstream that we've modified (e.g. `.vscode/*`, `translation.yml`) — ask
     the user whether to keep ours, take upstream's, or hand-merge, rather than assuming.
   - After resolving a file, `git add` it. Once all conflicts are resolved, run
     `git merge --continue` using the Bash tool.
6. After the merge is committed, reconcile `fireball.instructions.md`'s tracking table with what
   actually happened: update rows whose customization moved, changed shape, or was dropped during
   resolution, and add a row (plus `Fireball -` marker) for anything new — same standing rule as
   any other customization change.
7. Run `/push` then `/pr` to open the PR into `development`.

Never use `git checkout --theirs`/`--ours` or `-X theirs`/`-X ours` to blanket-resolve conflicts
here — Fireball customizations are hand-inserted inside Dawn's own files, so each conflict needs
an actual read, not a side-picking shortcut.
