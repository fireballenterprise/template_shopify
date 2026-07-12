# Shopify Modules

Shopify theme workflow logic invoked by the `shopify.*` invoke tasks (see [tasks/shopify.py](../../tasks/shopify.py)).

| Module | Purpose |
|--------|---------|
| `env.py` | Print `export KEY=value` Shopify CLI env vars (store, token, theme IDs) for shell eval |
| `pull.py` | Pull the live theme from a Shopify store into the local `development` branch |
| `upgrade.py` | Upgrade `dawn_vanilla` from upstream `Shopify/dawn`, then merge into `development` |

## `env.py` — `shopify.env`

Prints `export KEY=value` lines sourced from `properties.yml`, for use with:
```sh
eval "$(uv run --no-sync invoke shopify.env)"
```
A child process can't export env vars into the calling shell directly, so this `eval` form is
the supported way to load them into your current session — there is no separate shell script wrapper.

## `pull.py` — `shopify.pull`

Pulls live theme edits made in the Shopify theme editor down into the local repo.

**Workflow:**
1. Ensure `SHOPIFY_FLAG_STORE` and `SHOPIFY_CLI_THEME_TOKEN` are set (prompts interactively if missing)
2. Confirm current branch is `development` (warns otherwise)
3. Confirm working tree is clean (warns on uncommitted changes)
4. Run `shopify theme pull --store=<store> [--theme=<theme>]`
5. Show a summary of files changed

## `upgrade.py` — `shopify.upgrade`

Merges the latest upstream `Shopify/dawn` release into `dawn_vanilla`, then merges `dawn_vanilla`
into `development`.

**Workflow:**
1. Fetch `upstream` and compare the latest tag against the current `dawn_vanilla` tag
2. Confirm the upgrade (interactive)
3. Checkout `dawn_vanilla`, merge `upstream/main`, push to origin
4. Checkout `development`, merge `dawn_vanilla` (reports conflicts and stops if any)

## Conventions

- Every module exposes a module-level `main()` entry point
- Shell out to `git`/`shopify` via `subprocess.run([...], cwd=repo_path)` — never `shell=True`
- Use `modules.common.cli` for prompts/output and `modules.common.utils` for success/error/warning messages
- Resolve repo config via `modules.common.properties` (`get_repo_local()`, `get_shopify_store()`)
