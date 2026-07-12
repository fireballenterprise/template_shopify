"""Test tasks (ruff, pylint, yamllint, actionlint, Shopify theme-check)."""

from invoke import task


@task
def actionlint(context):
    """Run Action Lint"""
    print("\n------------")
    print("Action Lint")
    print("------------\n")
    context.run("actionlint")


@task
def pylint(context):
    """Run PyLint on Entire Repo"""
    print("\n------------")
    print("Pylint Lint")
    print("------------\n")
    context.run("pylint --verbose --rcfile=pyproject.toml .")


@task
def rufflint(context):
    """Run Ruff Linter on Entire Repo"""
    print("\n------------")
    print("Ruff Lint")
    print("------------\n")
    context.run("ruff check .")


@task
def theme_check(context):
    """Run Shopify Theme Check"""
    print("\n------------")
    print("Shopify Theme Check")
    print("------------\n")
    context.run("shopify theme check")


@task
def yamllint(context):
    """Run Yaml Linter on Entire Repo"""
    print("\n------------")
    print("Yaml Lint")
    print("------------\n")
    context.run(
        """
        yamllint --list-files -c .yamllint . &&
        echo '------------' &&
        echo -e &&
        yamllint -f parsable -c .yamllint .
        """
    )
