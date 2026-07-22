from invoke import task

from . import ruff, shopify, tests, versioning


@task
def fix(context):
    """Run All Automated Fixes"""
    ruff.fix(context)
    ruff.format(context)
    shopify.fix(context)


@task
def test(context):
    """Run All Tests"""
    tests.actionlint(context)
    tests.pylint(context)
    tests.rufflint(context)
    tests.theme_check(context)
    tests.yamllint(context)


@task
def update(context, dry_run=False, yes=False):
    """Run every version check (libs, python, workflows) — top-level alias for ver.update"""
    versioning.update(context, dry_run=dry_run, yes=yes)
