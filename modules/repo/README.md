# Repo Module

Git workflow and Pull Request automation — pull, push, rebase, squash, session logs, and PR
creation. Shared logic used by both `invoke repo.*` tasks and the `/repo`, `/push`, `/pull`,
`/rebase`, `/squash`, `/pr`, `/pr-notes`, `/pr-cleanup` slash commands.

## Usage

```sh
uv run --no-sync invoke repo.pull          # Stash → pull --rebase → restore
uv run --no-sync invoke repo.push          # Fix → test → commit → push (handles new feature branches too)
uv run --no-sync invoke repo.log           # Save a session log to logs/
uv run --no-sync invoke repo.squash        # Anchored squash of all commits to root + optional force push
uv run --no-sync invoke repo.rebase        # Rebase onto remote default branch (optionally squash first)
uv run --no-sync invoke repo.pr_diff       # Print current branch's commit log/diff vs. its base branch
uv run --no-sync invoke repo.pr_notes_save # Save PR notes to tmp/pull_requests/ (--content=...)
uv run --no-sync invoke repo.pr_create     # Open a GitHub PR via gh (--title=... --content=...)
uv run --no-sync invoke repo.pr_cleanup    # Switch to the default branch, pull, and delete the merged local feature branch
```

`/repo <subcommand> [args]` (`modules/repo/route.py`) is the AI-facing entrypoint for the same
functions — `/repo push`, `/repo pull`, `/repo pr_diff`, `/repo pr_notes`, `/repo pr_create`,
`/repo pr_cleanup`, `/repo rebase`, `/repo squash`. `/push` and `/pull` are direct aliases for
`/repo push`/`/repo pull`.

## Files

- `push.py` — stash → pull (falls back to `--rebase` on divergence, or pushes with `-u` if the
  branch has no upstream yet) → restore stash → commit → push. Runs `invoke fix`/`invoke test`
  first and stops if tests don't pass. Used by `/push` and `invoke repo.push`
- `pull.py` — stash → `git pull --rebase` → restore stash. Used by `/pull` and `invoke repo.pull`
- `log.py` — saves a timestamped session log markdown file to `logs/`
- `squash.py` — anchored squash of every commit down to the repo's root commit into one, with an
  auto-generated bulleted message; optional `--force-with-lease` push
- `rebase.py` — rebases the current branch onto the remote default branch (`origin/main` or
  `origin/master`), optionally squashing first; handles stashing and interactive conflict
  resolution if restoring the stash conflicts
- `pr_diff.py` — detects the current branch's base/default branch and prints its commit log + diff
  vs. that base, for use when drafting a PR description. Exposes `PROTECTED_BRANCHES` and
  `current_branch()`/`detect_base_branch()`, shared by `push.py`, `pr_notes.py`, `pr_create.py`, and
  `pr_cleanup.py`
- `pr_notes.py` — saves drafted PR notes markdown to `tmp/pull_requests/`
- `pr_create.py` — opens a GitHub Pull Request for the current branch via `gh pr create`, assigned
  to the calling user (`--assignee @me`); reports the existing PR's URL instead of erroring if one
  is already open
- `pr_cleanup.py` — after a PR is merged on GitHub: confirms the merge via `gh pr view`, switches to
  the detected default branch, pulls, then force-deletes the local feature branch
- `route.py` — `/repo <subcommand> [args]` argument dispatch, used by the AI-facing `/repo` command
- `README.md` — this file
