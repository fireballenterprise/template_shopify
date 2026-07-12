# Repo Modules

Git workflow logic invoked by the `repo.*` invoke tasks (see [tasks/repo.py](../../tasks/repo.py)).

| Module | Purpose |
|--------|---------|
| `pull.py` | Pull from git remote (stash → `pull --rebase` → restore stash) |
| `push.py` | Push to git remote (`invoke fix` → `invoke test` → commit → push) |
| `log.py` | Save a timestamped session log markdown file to `logs/` |
| `squash.py` | Anchored squash of all commits to root, with optional force push |
| `rebase.py` | Rebase onto the remote default branch, with optional squash-first and interactive conflict resolution |
| `pr.py` | Detect the PR base branch (`development`/`main`), print commit/diff context, save PR notes to `tmp/pull_requests/`, and open the PR via `gh` (targets this fork explicitly with `--repo`, since `gh` otherwise defaults to the upstream `Shopify/dawn` parent) |

## Conventions

- Every module exposes a module-level `main()` entry point (also runnable via `python -m modules.repo.<name>`) — `pr.py` additionally exposes `save_notes()` and `create_pr()` for its two other invoke tasks
- Shell out to `git` via `subprocess.run(..., cwd=repo_path)` — never `shell=True`
- Use `modules.common.cli` for output/prompts and `modules.common.utils` for success/error/warning messages
- Resolve the repository path via `modules.common.properties.get_repo_local()`

**Workflow:**
1. Prompt: *"Run squash before rebasing? [y/N]"*
   - If yes → delegates to `Repo::Squash.run` and returns
2. `git fetch --prune`
3. Auto-detect base branch (`origin/main` → `origin/master` → `origin/HEAD`)
4. `git rebase <base>`

**When to Use:**
- To bring a branch up to date with main before merging
- After squashing — rebase to apply cleanly on top of remote

**Invoke task:** `uv run --no-sync invoke repo.rebase`
**Prompt:** `/rebase`

---

## `log.py` — session logging

Save a markdown session log to `logs/` with a timestamped filename.

**Workflow:**
1. Prompt for a log title (if not provided)
2. Generate filename: `YYYYMMDDHHMM_slug.md`
3. Write log template to `logs/` (creates directory if needed)

**Log Template:**
```markdown
# <title>

Date: <ISO 8601 timestamp>

## Summary
## Code Changes
## Validation
## Notes
```

**When to Use:**
- End of a coding session — record what was done
- After a significant change — document the work

**Invoke task:** `uv run --no-sync invoke repo.log`

---

## `pr.py` — PR notes and creation via `gh`

Detects the base branch (`development` or `main`), gathers commit/diff context, and opens a PR
with the GitHub CLI. Requires `gh` to be installed and authenticated (not a pip dependency).

**When to Use:**
- `/pr-notes` — draft (and optionally save) a PR description without pushing or opening a PR
- `/punch-it-chewy` — push, then draft notes and open the PR in one step

**Invoke tasks:** `uv run --no-sync invoke repo.pr_diff`, `repo.pr_notes_save`, `repo.pr_create`
**Prompts:** `/pr-notes`, `/punch-it-chewy`

Note: this project's hand-crafted `/pr` command uses the `create_pull_request` tool directly
instead of this module — it's kept separate since it already handles this repo's fork-specific
targeting (base repo `fireballenterprise/shopify_dawn_theme`, base branch `development`).
