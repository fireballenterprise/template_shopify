# Copilot Instructions

This repo is the **Fireball Shopify theme template** — the scaffold new brand repos are stamped
from (see `README.md`). Content and CI/CD only. Theme files live in `assets/`, `config/`,
`layout/`, `locales/`, `sections/`, `snippets/`, `templates/`. All interactive dev tooling (git/PR
workflow, Shopify theme pull, Dawn upgrade, template sync) and AI planning/instructions live in
`fireball_orchestrator` instead — see `topics/shopify/` there, and pass `--site=<name>` to its
`repo.*`/`dawn.*`/`shopify.*` invoke tasks once a new repo stamped from this template is
registered in `tmp/.shopify/config.yml`.

## Invoke Tasks Kept Here (CI-required only)
- `debug.env` — print cwd + sorted env vars
- `tests.actionlint` / `tests.pylint` / `tests.rufflint` / `tests.theme_check` / `tests.yamllint`
- `shopify.deploy --env=dev|prd` / `shopify.env`
- `ver.libs` / `ver.python` / `ver.workflows` / `ver.all` / `ver.update` / `ver.upgrade`
- `ver.project_bump_build` / `ver.project_bump_release`

## Workflows (`.github/workflows/`)
Thin callers into `fireballenterprise/workflows_shopify@v2` — no logic lives in this repo's YAML,
except `publish_release.yml` which is template-only (see below):
- `tests.yml` — PRs into `development`/`main`: actionlint, pylint, ruff, theme-check, yamllint
- `deploy.yml` — push to `development`: bump VERSION build, deploy to dev theme (or `prd` manually)
- `release.yml` — manual: finalize VERSION, promote `development` → `main`, deploy prd, GitHub Release
- `dawn_sync.yml` — manual: sync `dawn_vanilla` with upstream `Shopify/dawn`
- `publish_release.yml` — **template repo only**: this repo has no `development` branch or live
  store, so the normal `release.yml` flow can't run here. Tags + publishes a GitHub Release
  straight off `main` when `VERSION` changes. Brand repos stamped from this template should delete
  this file — they release through `release.yml` instead.
