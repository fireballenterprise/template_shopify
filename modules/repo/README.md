# Repo Manager Agent

The repo module handles repository-level operations including git synchronization.

## Features

- **Repository Push/Pull**: Full git operations
- **Automated Commits**: Timestamp-based commit messages
- **Error Handling**: Graceful handling of push/pull failures

## Commands

### `/repo push` (alias: `/push`)
Push changes to git remote from any location.

**Workflow:**
1. **Navigate to repository root** - Automatically changes to repo directory
2. **Git pull** - Fetch and merge latest changes from remote
3. **Check for local changes** - Identify uncommitted work with `git status`
4. **Stage all changes** - Run `git add .` if changes detected
5. **Commit with timestamp** - Create commit: `Push repository: Automated commit YYYY-MM-DD HH:MM:SS`
6. **Push to remote** - Upload changes to GitHub
7. **Confirm completion** - Show status summary

**Features:**
- ✅ Works from any directory in the repository
- ✅ Automatic git operations (pull, commit, push)
- ✅ Timestamp-based commit messages
- ✅ Error handling for each push step

**When to Use:**
- **End of session** - Push all work before closing
- **After making changes** - Save work to remote
- **Regular backups** - Keep work synchronized and safe
- **After major changes** - Backup important work immediately

**Error Handling:**
- Git pull failure: Stops execution
- Git push failure: Stops execution with error

**Module:** `modules.repo.push` (via `/repo push`)

### `/repo pull` (alias: `/pull`)
Pull updates from git remote from any location.

**Workflow:**
1. **Check working directory** - Stash local changes if the working tree is dirty
2. **Git pull** - Fetch and merge latest changes from remote (rebase, to handle diverged history)
3. **Restore stash** - Restore stashed changes, if any were made

**Features:**
- ✅ Works from any directory in the repository
- ✅ Stashes and restores local changes automatically around the pull
- ✅ Rebases onto latest remote history instead of merge-committing

**When to Use:**
- **Start of session** - Get latest from git remote
- **After making changes on another device** - Pull updates to local
- **Before starting work** - Ensure you have latest version

**Error Handling:**
- Stash failure: Stops execution
- Git pull failure: Stops execution; restores the stash first if one was made

**Module:** `modules.repo.pull` (via `/repo pull`)

## Branch Maintenance

### `/rebase`
Rebase the current branch onto the remote default branch (`origin/main` or `origin/master`).
Optionally offers to run `/squash` first. Handles stashing local changes and interactive conflict
resolution (ours/theirs/manual) if restoring the stash conflicts.

**Module:** `modules.repo.rebase` (via `/rebase`)

### `/squash`
Anchored squash of every commit down to the repository's root commit into one commit, with an
auto-generated bulleted message. Prompts to review the message, confirm the (irreversible) local
squash, and optionally force-push (`--force-with-lease`).

**Module:** `modules.repo.squash` (via `/squash`)

## Git Integration

### Push/Pull Operations

**Pull Sequence:**
```bash
git status --porcelain  # Check for uncommitted changes, stash if dirty
git pull --rebase       # Fetch and rebase onto remote
git stash pop           # Restore stashed changes, if any
```

**Push Sequence:**
```bash
git pull                # Fetch and merge from remote
git status --porcelain  # Check for changes
git add .               # Stage all changes
git commit -m "Push repository: Automated commit 2025-12-11 01:30:45"
git push                # Upload to remote
```

**Commit Message Format:**
```
Push repository: Automated commit YYYY-MM-DD HH:MM:SS
```

## Configuration

Default settings in `config.yml`:
- `repo_path`: "${repo_local}"

## Permissions Required

- `git_pull` - Pull from remote repository
- `git_push` - Push to remote repository
- `git_commit` - Create commits
- `git_status` - Check repository status
- `directory_access` - Navigate repository directories
- `bash_execute` - Run shell scripts

## Dependencies

- `git` - Version control operations

## Best Practices

1. **Pull/Push Regularly**: Run `/repo pull` at start, `/repo push` at end of sessions
2. **Check Status**: Review git status before push if concerned about changes
3. **Network Aware**: Git operations require network connectivity
4. **Backup Important**: Always push before major changes or deletions

## Workflow Examples

**Cross-Device Workflow:**
```
Device A:
1. /repo pull                # Pull latest before starting
   [work on content]
2. /repo push                # Push changes to remote

Device B (later):
1. /repo pull                # Pull changes from Device A
```

## Related Commands

- `/repo push` - Push all commits to remote (alias: `/push`)
- `/repo pull` - Pull latest changes from remote (alias: `/pull`)

## Files

- `push.py` - Push to git (used by `/repo push`, alias `/push`)
- `pull.py` - Pull from git (used by `/repo pull`, alias `/pull`)
- `config.yml` - Agent configuration
- `README.md` - This file

## Command Aliases

- `/push` → Push to git
- `/pull` → Pull from git
