"""Dawn upstream version listing and upgrade-staging tasks."""

from invoke import task

from modules.dawn import list as dawn_list
from modules.dawn import upgrade as dawn_upgrade
from modules.dawn import version as dawn_version


@task(name="list")
def list_versions(_context):  # noqa: A001  # pylint: disable=redefined-builtin
    """List every version tag published on upstream Shopify/dawn, latest highlighted"""
    dawn_list.main()


@task
def upgrade(_context):
    """Merge the upgraded dawn_vanilla into a feature branch for manual conflict resolution"""
    dawn_upgrade.main()


@task(name="version")
def show_version(_context):
    """Print the Dawn theme version currently checked out on this branch"""
    dawn_version.main()
