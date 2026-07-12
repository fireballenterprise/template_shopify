"""Git workflow tasks (pull, push, log, squash, rebase, pr)."""

from invoke import task

from modules.repo import log as log_module
from modules.repo import pr as pr_module
from modules.repo import pull as pull_module
from modules.repo import push as push_module
from modules.repo import rebase as rebase_module
from modules.repo import squash as squash_module


@task
def pull(_context):
    """Pull updates from git remote (stash → pull --rebase → restore)"""
    pull_module.main()


@task
def push(_context):
    """Push to git remote (fix → test → commit → push)"""
    push_module.main(confirm=False)


@task
def log(_context, title=None, content=None):
    """Save a session log to logs/"""
    log_module.main(title=title, content=content)


@task
def squash(_context):
    """Anchored squash of all commits to root with optional force push"""
    squash_module.main()


@task
def rebase(_context):
    """Rebase onto remote default branch (optionally squash first)"""
    rebase_module.main()


@task
def pr_diff(_context):
    """Show current branch's commit log/diff vs. its detected base branch"""
    pr_module.main()


@task
def pr_notes_save(_context, content=None):
    """Save PR notes to tmp/pull_requests/"""
    pr_module.save_notes(content=content)


@task
def pr_create(_context, title=None, content=None):
    """Open a GitHub PR for the current branch (gh pr create)"""
    pr_module.create_pr(title=title, content=content)
