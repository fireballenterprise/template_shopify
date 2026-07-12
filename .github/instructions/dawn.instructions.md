---
description: "Use when listing upstream Shopify/dawn version tags or upgrading Dawn from upstream. Covers the dawn.* invoke tasks and their modules."
applyTo: "modules/dawn/**"
---
# Dawn Instructions

## Purpose
Three actions, all scoped to upstream `Shopify/dawn`:
- `dawn.list` — lists every tag published on upstream `Shopify/dawn`, sorted, with the latest
  highlighted and compared against what `dawn_vanilla` is currently synced to. Read-only.
- `dawn.version` — prints the Dawn version currently checked out on this branch, per
  `config/settings_schema.json`'s `theme_info.theme_version`. Read-only, no git/network calls.
- `dawn.upgrade` — merges the already-synced `origin/dawn_vanilla` into a feature branch for
  manual conflict resolution: the currently checked-out feature branch if one is already cut,
  otherwise it cuts (or reuses) `upgrade/dawn-vanilla-v<version>` off `origin/development`. The
  target version is read from `origin/dawn_vanilla`'s own `settings_schema.json` — there is no
  version argument. Not read-only — may create a local branch, and merges.

See `modules/dawn/README.md` for full behavior/data-flow details on each.

## Usage
```sh
uv run --no-sync invoke dawn.list                       # list upstream Shopify/dawn tags, latest highlighted
uv run --no-sync invoke dawn.version                    # print the Dawn version on this branch
uv run --no-sync invoke dawn.upgrade                    # merge the synced dawn_vanilla into a feature branch
```
`/dawn [list | upgrade]` runs the same checks and walks through conflict resolution for `upgrade`.

## Relationship to Other Workflows
- `dawn.list` is purely informational — it tells you what `version` value (e.g. `v15.5.0`)
  to pass to the **Upgrade** GitHub Actions workflow (`.github/workflows/upgrade.yml`)
- `dawn.version` reads a different source of truth than `dawn.list` — the checked-out theme's own
  `theme_info.theme_version` versus `dawn_vanilla`'s git tag history — and the two can disagree if
  `development` ever picked up version-bumping content some other way than a `dawn_vanilla` merge
- `dawn.upgrade` assumes the Upgrade workflow has already synced `dawn_vanilla` to the target
  version; it only handles merging that into a `development`-based feature branch

## The Full Dawn Upgrade Workflow
Upgrading Dawn is a three-step process split across CI and local/AI-assisted work, deliberately —
see "Why the Merge-and-PR Step Isn't Automated in CI" below for why step 3 can't be a CI job:

1. **Run `dawn.list`** to see the latest upstream tag and what `dawn_vanilla` is currently on
   (optional — the next step's `version` input defaults to `latest` and resolves it itself).
2. **Run the "Upgrade" GitHub Actions workflow** (`workflow_dispatch`, `version` input = the tag
   from step 1, or leave it as `latest` to have the workflow look up the current latest tag
   itself) — this merges that one pinned upstream tag into `dawn_vanilla` with upstream winning
   any conflict (`dawn_vanilla` is meant to stay a clean mirror, so this part is safe to fully
   automate), and pushes it. Re-running with the same (or already-synced) version is a safe no-op.
3. **Run `dawn.upgrade`** (or `/dawn upgrade`) locally — merges the now-updated
   `origin/dawn_vanilla` into a feature branch: the one currently checked out if you already cut
   one for the upgrade, otherwise `upgrade/dawn-vanilla-v<version>` cut off `origin/development`
   (reused if it already exists). One merge, so conflicts appear in a single pass.
   - Clean merge → run `/push` then `/pr` to open the PR into `development`.
   - Conflicts → resolve each file by hand (or via `/dawn upgrade`'s AI-assisted walkthrough),
     using `fireball.instructions.md`'s tracking table to know what's ours to preserve, then
     `git merge --continue`. Afterwards reconcile the tracking table with the outcome (rows for
     customizations that moved/changed/were dropped), then `/push` and `/pr`.

## Why the Merge-and-PR Step Isn't Automated in CI
An earlier version of `.github/workflows/upgrade.yml` had a second job that did step 3 in CI and
opened the PR automatically. It was removed: `config/settings_data.json` and the `templates/*.json`
files conflict on nearly every real upgrade (they're large, frequently-regenerated JSON), and
several `sections/*.liquid`/`*.json` files conflict whenever upstream touches the same regions as
a Fireball customization — which happens often enough to make full automation unrealistic. Worse,
Fireball's customizations are hand-inserted *inside* Dawn's own files, so a CI job blindly picking
a side (`-X theirs`/`-X ours`) risks silently corrupting either the customization or the upstream
update. A human/AI actually reading each conflict is the safer default; `dawn.upgrade` gets you to
that point quickly without pretending the conflict-resolution step can be skipped.

## Why `dawn.list` Fetches Tags Directly Instead of Reusing `shopify.upgrade`
`modules/shopify/upgrade.py` (the local `shopify.upgrade` invoke task) also compares Dawn versions,
but via a full `git fetch upstream --tags`, which pulls every historical Dawn tag into the local
repo — this previously collided with the `.github/workflows/upgrade.yml` CI job's own fetch when a
Fireball release tag happened to share a name with an old upstream Dawn tag (e.g. `v1.0.0`).
`dawn.list` avoids that entirely by using `git ls-remote` against the upstream URL directly — no
local fetch, no tag namespace collision, safe to run anytime.

## Module Conventions
- Same conventions as `modules.instructions.md` generally — `main()` entry point per module,
  `subprocess.run([...], cwd=repo_path)` never `shell=True`, output via `modules.common.utils`
- None of `list.py`, `version.py`, or `upgrade.py` use `@click.command()`-style options — each
  takes no arguments and stays undecorated (see `modules/dawn/README.md`'s Conventions section
  for why, and why `version.py`'s `parse_theme_version()` is public rather than `_`-prefixed)
