"""Pull the live theme from a Shopify store into the local development branch."""

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local, get_shopify_store, get_shopify_theme_id
from ..common.utils import error, info, success, warning
from .env import ensure_env


def _current_branch(repo_path: Path) -> str:
    """Return the current checked-out branch name."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _confirm_branch(repo_path: Path) -> None:
    """Warn and confirm if the current branch is not 'development'."""
    branch = _current_branch(repo_path)
    if branch == "development":
        return

    warning(f"Current branch is '{branch}', expected 'development'.")
    if not click.is_tty():
        return

    if not click.confirm(f"Continue theme pull onto '{branch}'?", default=False):
        info("Pull cancelled. Switch to development branch first.")
        raise SystemExit(0)


def _confirm_clean(repo_path: Path) -> None:
    """Warn and confirm if there are uncommitted local changes."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "status", "--porcelain"], capture_output=True, text=True, check=True
    )
    if not result.stdout.strip():
        return

    warning("Uncommitted changes detected. Theme pull may overwrite local edits.")
    if not click.is_tty():
        return

    if not click.confirm("Continue anyway?", default=False):
        info("Pull cancelled. Commit or stash your changes first.")
        raise SystemExit(0)


def _show_changes(repo_path: Path) -> None:
    """Print a summary of changes pulled from the store."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "status", "--short"], capture_output=True, text=True, check=True
    )
    if not result.stdout.strip():
        info("No changes — store and local are already in sync.")
        return

    info("Changes pulled from store:")
    for line in result.stdout.splitlines():
        click.echo(f"  {line}")


def _resolve_theme(env: str | None, theme: str | None) -> str | None:
    """Resolve the --theme value to pass to the Shopify CLI from an env shortcut or raw override."""
    if env and theme:
        error("Pass either env or theme, not both.")
    if env:
        try:
            return get_shopify_theme_id(env)
        except ValueError as exc:
            error(str(exc))
    return theme


def main(env: str | None = None, theme: str | None = None) -> None:
    """Pull the live theme from a Shopify store into the local development branch."""
    ensure_env()

    repo_path = get_repo_local()
    store = get_shopify_store()
    resolved_theme = _resolve_theme(env, theme)

    _confirm_branch(repo_path)
    _confirm_clean(repo_path)

    command = ["shopify", "theme", "pull", f"--store={store}"]
    if resolved_theme:
        command.append(f"--theme={resolved_theme}")

    click.echo()
    click.echo(f"Pulling theme{f' {resolved_theme!r}' if resolved_theme else ''} from {store}...")
    click.echo()

    # shopify CLI requires a live TTY for auth and progress output — subprocess without
    # capturing stdio is intentional so it inherits the parent's TTY.
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        error("shopify theme pull failed.")

    click.echo()
    _show_changes(repo_path)
    click.echo()
    success("Review changes above, then run /push to commit and push to git.")


if __name__ == "__main__":
    main()
