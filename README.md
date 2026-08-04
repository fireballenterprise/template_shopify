# Fireball Enterprise Shopify Theme Template

GitHub template repo for Fireball Enterprise Shopify theme repos. Vendored [Shopify Dawn](https://github.com/Shopify/dawn) (seeded at `v15.5.0`) plus just enough Python Invoke tooling to run CI (linting, theme-check, versioning, deploy) and thin caller workflows into [fireballenterprise/workflows_shopify](https://github.com/fireballenterprise/workflows_shopify). All interactive dev tooling (git/PR workflow, Shopify theme pull, Dawn upgrade) and AI planning/instructions live in [fireball_orchestrator](https://github.com/fireballenterprise/fireball_orchestrator) instead — this repo (and repos stamped from it) are content + CI/CD only.

## Stamping a New Brand Repo

```sh
gh repo create fireballenterprise/fireball_<brand>_shopify \
  --template fireballenterprise/template_shopify \
  --public --include-all-branches --clone
```

Then in the new repo:

1. Restore Dawn ancestry — template stamping squashes every branch to a single parentless
   commit, which breaks the merge-based Dawn flows (`dawn_sync` workflow, `fireball_orchestrator`'s
   `invoke dawn.upgrade --site=<name>`):

   ```sh
   git remote add dawn https://github.com/Shopify/dawn.git
   git fetch dawn main --no-tags
   # dawn_vanilla = real upstream history (replaces the squashed snapshot)
   git push --force origin refs/remotes/dawn/main:refs/heads/dawn_vanilla
   git fetch origin && git branch -f dawn_vanilla origin/dawn_vanilla
   # graft the vendored Dawn version into main's ancestry without changing content;
   # use the tag matching the theme files main currently carries (see config/settings_schema.json)
   git fetch dawn refs/tags/v15.5.0:refs/tags/dawn-v15.5.0 --no-tags
   git checkout main
   git merge dawn-v15.5.0 --allow-unrelated-histories -s ours --no-ff -m "chore: graft Dawn v15.5.0 ancestry into main"
   git push origin main
   ```

2. Update `pyproject.toml` (`name`, `description`, URLs) and `properties.yml` (`repo.local`, `repo.remote`) by hand for the new repo
3. Delete `.github/workflows/publish_release.yml` — that flow is template-only (no `development` branch/store here to gate a normal release); brand repos release through `release.yml` instead
4. Create the `development` branch from `main` (after the graft), make it the **default branch** (`gh repo edit <repo> --default-branch development` — GitHub Actions only lists and `workflow_dispatch`es workflows from the default branch, so workflow changes take effect before merging to `main`), and set branch protection (deletion/force-push guards on `development` + `main`)
5. Add secrets manually (never via AI): `BOT_PRIVATE_KEY`, `SHOPIFY_CLI_THEME_TOKEN`, `SHOPIFY_FLAG_STORE`, `SHOPIFY_THEME_ID_DEV`, `SHOPIFY_THEME_ID_PRD`; variable: `BOT_APP_ID` (`fireball-actions-bot` is installed org-wide)
6. Run `./setup.sh`
7. Register the new repo as a site in `fireball_orchestrator`'s `tmp/.shopify/config.yml` (`repo_local_path`, `store`, `theme_id_dev`, `theme_id_prd`, `theme_token`) so its `--site=<name>` dev tooling (`repo.*`, `dawn.*`, `shopify.pull`/`shopify.env`) works

## Branches

- `main` — production theme
- `development` — working branch (dev deploys on push)
- `dawn_vanilla` — pristine upstream Shopify/dawn; synced by the Dawn Sync workflow, merged into `development` manually when upgrading

## Workflows

Thin callers only — logic lives in `fireballenterprise/workflows_shopify`, referenced by floating major tag `@v2` (exact tags like `v2.0.0` also exist). `publish_release.yml` is the one exception (see table) — it's template-only, plain YAML, no reusable-workflow call.

| Caller | Trigger | Purpose |
|--------|---------|---------|
| `deploy.yml` | push to `development`, manual | Bump VERSION build + deploy to dev theme (or prd manually) |
| `tests.yml` | PR to `development`/`main` | actionlint, pylint, ruff, theme-check, yamllint |
| `release.yml` | manual | Finalize VERSION, promote to `main`, deploy prd, GitHub Release |
| `dawn_sync.yml` | monthly, manual | Sync `dawn_vanilla` with upstream Dawn |
| `publish_release.yml` | push to `main` (VERSION change), manual | **Template repo only** — tags + publishes a GitHub Release straight off `main`, since this repo has no `development` branch/store to run the normal `release.yml` flow. Delete this file in brand repos stamped from the template. |

## Prerequisites

- [Python](https://www.python.org/) `>=3.14`
- [uv](https://docs.astral.sh/uv/) (dependency/environment management)
- [Shopify CLI](https://shopify.dev/docs/storefronts/themes/tools/cli) (`npm install -g @shopify/cli`)

## Setup

```sh
./setup.sh
```

Creates a `.venv` with `uv`, installs dependencies, and installs the Shopify CLI. `properties.yml` is committed directly (no per-machine stamping) — edit it by hand if `repo.local`/`repo.remote` need to change.

## Versioning

`major.minor.patch-build` in development (e.g. `1.2.0-004`), finalized to `major.minor.patch` on release. NO `v` prefix on release tags. The home page carries the current version as an HTML comment via `snippets/fireball-version.liquid`.
