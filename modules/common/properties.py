"""Properties management for shopify_dawn_theme."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


def _expand_path(value: str) -> Path:
    """Expand ~ and environment variables (e.g. $HOME) in a properties.yml path value."""
    return Path(os.path.expandvars(os.path.expanduser(value)))


def is_ci() -> bool:
    """Return True when running inside GitHub Actions."""
    return os.environ.get("GITHUB_ACTIONS", "").lower() == "true"


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    """
    Find repository root by searching upward for properties.yml.

    Works from any subdirectory within the repository.

    Returns:
        Path to repository root.

    Raises:
        FileNotFoundError: If properties.yml cannot be found.
    """
    # Start from current file location
    current = Path(__file__).resolve()

    # Search upward from current file location
    for parent in [current.parent.parent.parent] + list(current.parents):
        props_file = parent / "properties.yml"
        if props_file.exists():
            return parent

    # Also try from current working directory
    current_cwd = Path.cwd().resolve()
    for parent in [current_cwd] + list(current_cwd.parents):
        props_file = parent / "properties.yml"
        if props_file.exists():
            return parent

    msg = "Could not find repository root (properties.yml not found)"
    raise FileNotFoundError(msg)


@lru_cache(maxsize=1)
def get_properties() -> dict[str, Any]:
    """
    Load properties.yml with singleton pattern (cached).

    Returns:
        Dictionary with all repository properties.

    Raises:
        FileNotFoundError: If properties.yml does not exist.
    """
    repo_root = get_repo_root()
    props_file = repo_root / "properties.yml"

    with props_file.open() as f:
        return yaml.safe_load(f)


def get_repo_local() -> Path:
    """
    Get repo local path as Path object.

    Returns:
        Path to local repository.
    """
    props = get_properties()
    return _expand_path(props["repo"]["local"])


def get_repo_remote() -> str:
    """
    Get repo remote URL.

    Returns:
        Remote repository URL.
    """
    props = get_properties()
    return props["repo"]["remote"]


def get_shopify_local_config_path() -> Path:
    """
    Get the local path to the gitignored Shopify config file.

    A relative path is resolved against this repo's root.

    Returns:
        Path to the local Shopify config file.
    """
    props = get_properties()
    local = _expand_path(props["shopify"]["local_config"])
    return local if local.is_absolute() else get_repo_root() / local


@lru_cache(maxsize=1)
def get_shopify_local_config() -> dict[str, Any]:
    """
    Load the gitignored Shopify config file (token path, store, theme IDs), cached.

    Kept out of properties.yml (and out of git) since it identifies the store
    and both theme IDs.

    Returns:
        Dictionary with the local Shopify config.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    config_file = get_shopify_local_config_path()
    if not config_file.is_file():
        msg = (
            f"Local Shopify config not found: {config_file}\n"
            "Create it with 'local_theme_token', 'store', 'theme_id_dev', and 'theme_id_prd' keys."
        )
        raise FileNotFoundError(msg)

    with config_file.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_shopify_local_theme_token() -> Path:
    """
    Get the local path to the Shopify Theme Access token file.

    A relative path is resolved against this repo's root.

    Returns:
        Path to the token file.
    """
    local = _expand_path(get_shopify_local_config()["local_theme_token"])
    return local if local.is_absolute() else get_repo_root() / local


def get_shopify_store() -> str:
    """
    Get the Shopify store domain.

    Reads from the SHOPIFY_FLAG_STORE env var in CI (set from a secret), or from the
    local Shopify config file otherwise.

    Returns:
        Shopify store domain (e.g. "mystore.myshopify.com").
    """
    if is_ci():
        return os.environ["SHOPIFY_FLAG_STORE"]
    return str(get_shopify_local_config()["store"])


def get_shopify_theme_id_dev() -> str:
    """
    Get the Shopify development theme ID.

    Reads from the SHOPIFY_THEME_ID_DEV env var in CI (set from a secret), or from the
    local Shopify config file otherwise.

    Returns:
        Development theme ID.
    """
    if is_ci():
        return os.environ["SHOPIFY_THEME_ID_DEV"]
    return str(get_shopify_local_config()["theme_id_dev"])


def get_shopify_theme_id_prd() -> str:
    """
    Get the Shopify production (live) theme ID.

    Reads from the SHOPIFY_THEME_ID_PRD env var in CI (set from a secret), or from the
    local Shopify config file otherwise.

    Returns:
        Production theme ID.
    """
    if is_ci():
        return os.environ["SHOPIFY_THEME_ID_PRD"]
    return str(get_shopify_local_config()["theme_id_prd"])


def get_shopify_theme_id(env: str) -> str:
    """
    Get the Shopify theme ID for an environment shortcut.

    Args:
        env: Either "dev" or "prd".

    Returns:
        The resolved theme ID.

    Raises:
        ValueError: If env is not "dev" or "prd".
    """
    if env == "dev":
        return get_shopify_theme_id_dev()
    if env == "prd":
        return get_shopify_theme_id_prd()
    msg = f"Unknown Shopify environment {env!r} — expected 'dev' or 'prd'."
    raise ValueError(msg)


def get_skeleton_local() -> Path:
    """
    Get the local path to the shared skeleton repo (repo_setup_python), used by /sync-setup.

    A relative path is resolved against this repo's root.

    Returns:
        Path to the skeleton repository.
    """
    props = get_properties()
    local = _expand_path(props["skeleton"]["local"])
    return local if local.is_absolute() else get_repo_root() / local


def get_skeleton_remote() -> str:
    """
    Get the skeleton repo's remote (e.g. "github.com/LevonBecker/repo_setup_python").

    Returns:
        Remote repository reference, without a URL scheme.
    """
    props = get_properties()
    return props["skeleton"]["remote"]
