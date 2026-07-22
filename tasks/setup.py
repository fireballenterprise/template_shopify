"""Repo bootstrap tasks — called by setup.sh, safe to re-run any time."""

from invoke import task


@task
def properties(context):
    """Create/stamp properties.yml with this machine's repo path and git remote"""
    # Shelled out (not a direct properties_module.main() call) so its @cli.command() argparse
    # wrapper sees a clean argv — called in-process, it would instead parse invoke's own argv
    # (e.g. "setup.properties") and fail as an unrecognized argument.
    context.run("python -m modules.setup.properties")
