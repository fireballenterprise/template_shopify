# Dawn Module

Lists upstream Shopify/dawn version tags, prints the Dawn version currently checked out on this
branch, and merges the upgraded `dawn_vanilla` into a feature branch for manual conflict
resolution. Does not install anything, and never auto-resolves conflicts or opens a PR on its own.

## Usage

```sh
uv run --no-sync invoke dawn.list     # list upstream Shopify/dawn tags, latest highlighted
uv run --no-sync invoke dawn.version  # print the Dawn version on this branch
uv run --no-sync invoke dawn.upgrade  # merge the synced dawn_vanilla into a feature branch
```

## `list.py` — `dawn.list`

1. Lists every semver tag published on upstream `Shopify/dawn` via `git ls-remote --tags --refs`
   (no clone/auth needed), sorted numerically.
2. Resolves the tag the local `dawn_vanilla` branch currently points to (`git describe --tags`)
   and marks it inline, alongside the latest upstream tag.
3. Prints the exact `version` value (e.g. `v15.5.0`) to pass to the **Upgrade** GitHub Actions
   workflow (`.github/workflows/upgrade.yml`) to sync `dawn_vanilla` to the latest release.

This is read-only — it doesn't fetch, merge, or push anything. It exists purely to answer "what's
the latest Dawn version, and what am I currently on?" before running the Upgrade workflow.

```
uv run --no-sync invoke dawn.list
  ↓
modules/dawn/list.py
  ↓
git ls-remote --tags Shopify/dawn   +   git describe --tags dawn_vanilla   →   printed list
```

## `version.py` — `dawn.version`

Reads `config/settings_schema.json`'s `theme_info.theme_version` and prints it — the same field
Shopify's theme editor reads to show the version in the admin. Read-only, no git/network calls.

This can drift from what `dawn_vanilla` is tagged at (per `dawn.list`) if `development` ever picks
up version-bumping content some other way than a straight `dawn_vanilla` merge — the two are
different sources of truth (checked-out theme content vs. git tag history) and aren't guaranteed
to agree if something upstream of the normal upgrade flow touched this file.

```
uv run --no-sync invoke dawn.version
  ↓
modules/dawn/version.py
  ↓
config/settings_schema.json theme_info.theme_version   →   printed version
```

## `upgrade.py` — `dawn.upgrade`

1. Refuses to run if the working tree has uncommitted changes.
2. Fetches `origin/development` and `origin/dawn_vanilla`, then reads the target version from
   `origin/dawn_vanilla`'s `config/settings_schema.json` (via `version.py`'s
   `parse_theme_version()`) — whatever the Upgrade workflow synced is what gets merged; there is
   no version argument.
3. Resolves the branch to merge into: the currently checked-out feature branch if one is already
   cut (anything other than `development`/`main`/`dawn_vanilla`), otherwise it cuts
   `upgrade/dawn-vanilla-v<version>` off `origin/development` — or reuses that branch if it
   already exists locally.
4. If `origin/dawn_vanilla` is already an ancestor of the branch, reports there's nothing to
   merge and stops — safe to re-run.
5. Merges `origin/dawn_vanilla` into the branch (`--no-ff`, **no `-X theirs`/`-X ours`**), so
   real conflicts stop the merge rather than getting silently resolved — and it's a single merge,
   so all conflicts appear in one pass instead of commit-by-commit like a rebase.
6. Clean merge → prints a success message and tells you to run `/push` then `/pr`.
   Conflicts → prints the conflicted file list and points at `fireball.instructions.md`'s
   tracking table for what Fireball customizations must be preserved, plus the
   `git add` / `git merge --continue` steps.

This assumes the **Upgrade** GitHub Actions workflow has already synced `dawn_vanilla` to the
target version — it only handles merging that content into a `development`-based feature branch.
See `dawn.instructions.md`'s "Why the Merge-and-PR Step Isn't Automated in CI" section for why
this is a local/AI-assisted step rather than a second CI job.

```
uv run --no-sync invoke dawn.upgrade
  ↓
modules/dawn/upgrade.py
  ↓
current feature branch, or git checkout -b upgrade/dawn-vanilla-v<version> origin/development
git merge --no-ff origin/dawn_vanilla   →   clean, or stops with conflicts to resolve by hand
```

## Conventions

- Every module exposes a module-level `main()` entry point
- None of the three files use `@click.command()`-style options — each `main()` takes no
  arguments and stays undecorated, matching `modules/shopify/upgrade.py`'s pattern for
  simple-argument modules
- `version.py`'s `parse_theme_version()` is deliberately public (no leading `_`) since
  `upgrade.py` imports it directly — everything else in these files is a private (`_`-prefixed)
  helper
- Shell out via `subprocess.run(..., cwd=repo_path)` — never `shell=True`
- Use `modules.common.utils` (`success`/`error`/`warning`/`info`) for all console output
