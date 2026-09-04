# Copilot Instructions

This repo is the **Fireball Shopify theme template** — the scaffold new brand repos are stamped
from (see `README.md`). **Pure content**: theme files in `assets/`, `config/`, `layout/`,
`locales/`, `sections/`, `snippets/`, `templates/`. No Python, no `tasks/`, no `pyproject.toml`.

All dev tooling — git/PR workflow, Shopify theme pull/deploy, Dawn upgrade, version bumps — runs
from **`fireball_orchestrator`** against a stamped repo's checkout: `--site=<name>` on its
`repo.*` / `shopify.*` invoke tasks once the new repo is registered in `tmp/.shopify/config.yml`.

## CI — `.github/workflows/` (thin callers into `fireballenterprise/workflows_shopify@v4`)
| workflow | trigger | does |
|---|---|---|
| `tests.yml` | PR → `development` / `main` | `shopify theme check` + `yamllint` + `actionlint` |
| `deploy.yml` | push → `development` (or manual) | bump `VERSION` patch, `shopify theme push` to the dev theme (`prd` on manual dispatch) |
| `release.yml` | manual | optional milestone bump, promote `development` → `main`, deploy prd, GitHub Release |
| `dawn_sync.yml` | manual / monthly | sync `dawn_vanilla` with upstream `Shopify/dawn` |
| `publish_release.yml` | **template repo only** | this repo has no `development` branch or live store, so `release.yml` can't run here — tags + publishes off `main` when `VERSION` changes. **Delete this file in a stamped brand repo.** |

The bump + deploy + theme-check logic lives in `workflows_shopify`'s composite actions
(`actions/{bump_version,deploy_theme,theme_check}`), not in this repo.
