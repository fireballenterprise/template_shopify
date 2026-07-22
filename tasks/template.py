"""Template sync tasks — pull shared tooling from the parent template repo, or push it upstream."""

from invoke import task

from modules.template import pull as pull_module
from modules.template import push as push_module


@task
def pull(_context):
    """Resolve the local path to the parent template repo (clone from remote if not found locally)"""
    pull_module.main()


@task
def push_diff(_context):
    """Diff this repo's scoped tooling against the parent template repo (ADDED/MODIFIED/DELETED)"""
    push_module.run_diff()


@task
def push_apply(_context, files="", deletes=""):
    """Copy approved files (and apply deletions) to a new branch in the parent template repo, then push it

    files/deletes are comma-separated relative paths, e.g. --files=modules/foo.py,tasks/foo.py
    """
    file_list = [f.strip() for f in files.split(",") if f.strip()]
    delete_list = [d.strip() for d in deletes.split(",") if d.strip()]
    push_module.run_apply(file_list, delete_list)


@task
def push_create_pr(_context, branch, title=None, body=None):
    """Open a PR for `branch` against the parent template repo (gh pr create)"""
    push_module.run_create_pr(branch, title, body)
