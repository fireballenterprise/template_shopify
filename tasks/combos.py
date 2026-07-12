from invoke import task

from . import ruff, shopify, tests


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
