---
name: dawn
description: Use for listing upstream Shopify/dawn version tags, or merging the already-synced dawn_vanilla into a feature branch and resolving conflicts. Equivalent to /dawn.
---

# Dawn Sync Workflow

Use this file as source of truth: `.github/prompts/dawn.prompt.md`

When the user asks about upstream Dawn versions, or to merge a synced `dawn_vanilla` upgrade into
a feature branch, read that prompt file and follow it.

- `list`: `uv run --no-sync invoke dawn.list` — every upstream Shopify/dawn tag, latest highlighted,
  and what `dawn_vanilla` is currently synced to. Nothing to apply.
- `upgrade`: `uv run --no-sync invoke dawn.upgrade` — merges whatever `origin/dawn_vanilla` already
  contains into the current (or a new `upgrade/dawn-vanilla-v<version>`) feature branch. Does not
  fetch/merge upstream itself.

On merge conflicts, read `.github/instructions/fireball.instructions.md`'s tracking table first —
it lists every hand-written Fireball customization. Resolve each conflict by reading both sides and
finding the `Fireball -` marker comments; never blanket-resolve with `--theirs`/`--ours`.
