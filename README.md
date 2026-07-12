# Fireball Enterprise Shopify Theme Template

GitHub template repo for Fireball Enterprise Shopify theme repos. Vendored [Shopify Dawn](https://github.com/Shopify/dawn) (seeded at `v15.5.0`) plus Python Invoke tooling for local linting, git workflow automation, AI Copilot prompts, and thin caller workflows into [fireballenterprise/workflows](https://github.com/fireballenterprise/workflows).

## Stamping a New Brand Repo

```sh
gh repo create fireballenterprise/fireball_<brand>_shopify \
  --template fireballenterprise/template_shopify_theme \
  --public --include-all-branches --clone
```

Then in the new repo:

1. Update `properties.yml` (`repo.local`, `repo.remote`) and `pyproject.toml` (`name`, `description`, URLs)
2. Create the `development` branch from `main` and set branch protection (PRs required into `development` and `main`)
3. Add secrets manually (never via AI): `BOT_PRIVATE_KEY`, `SHOPIFY_CLI_THEME_TOKEN`, `SHOPIFY_FLAG_STORE`, `SHOPIFY_THEME_ID_DEV`, `SHOPIFY_THEME_ID_PRD`; variable: `BOT_APP_ID` (`fireball-actions-bot` is installed org-wide)
4. Remove the weekly `schedule` trigger from `.github/workflows/dawn_sync.yml` (only the template repo auto-syncs; brand repos sync on demand)
5. Run `./setup.sh`

## Branches

- `main` — production theme
- `development` — working branch (dev deploys on push)
- `dawn_vanilla` — pristine upstream Shopify/dawn; synced by the Dawn Sync workflow, merged into `development` manually when upgrading

## Workflows

Thin callers only — logic lives in `fireballenterprise/workflows`, referenced by floating major tag `@1` (no `v` prefix; exact tags like `1.0.0` also exist).

| Caller | Trigger | Purpose |
|--------|---------|---------|
| `deploy.yml` | push to `development`, manual | Bump VERSION build + deploy to dev theme (or prd manually) |
| `tests.yml` | PR to `development` | actionlint, pylint, ruff, theme-check, yamllint |
| `release.yml` | manual | Finalize VERSION, promote to `main`, deploy prd, GitHub Release |
| `dawn_sync.yml` | weekly (template only), manual | Sync `dawn_vanilla` with upstream Dawn |

## Prerequisites

- [Python](https://www.python.org/) `>=3.14`
- [uv](https://docs.astral.sh/uv/) (dependency/environment management)
- [Shopify CLI](https://shopify.dev/docs/storefronts/themes/tools/cli) (`npm install -g @shopify/cli`)

## Setup

```sh
./setup.sh
```

Creates a `.venv` with `uv`, installs dependencies, and installs the Shopify CLI.

## Versioning

`major.minor.patch-build` in development (e.g. `1.2.0-004`), finalized to `major.minor.patch` on release. NO `v` prefix on release tags. The home page carries the current version as an HTML comment via `snippets/fireball-version.liquid`.

## Skeleton Sync

Shared Python tooling (`modules/`, `tasks/`, `.github/`, config files) syncs from [LevonBecker/template_python](https://github.com/LevonBecker/template_python) via `/sync-setup`.
