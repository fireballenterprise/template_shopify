# Fireball Enterprise Shopify Theme Template

GitHub template repo for Fireball Enterprise Shopify theme repos. Vendored
[Shopify Dawn](https://github.com/Shopify/dawn) (seeded at `v15.5.0`) + thin caller workflows into
[fireballenterprise/workflows_shopify](https://github.com/fireballenterprise/workflows_shopify).
**Pure content** — no Python, no build tooling. All interactive dev tooling (git/PR workflow,
theme pull/deploy, Dawn upgrade, version bumps) and AI planning live in
[fireball_orchestrator](https://github.com/fireballenterprise/fireball_orchestrator).

## Stamping a New Brand Repo

```sh
gh repo create fireballenterprise/fireball_<brand>_shopify \
  --template fireballenterprise/template_shopify \
  --public --include-all-branches --clone
```

Then in the new repo:

1. **Restore Dawn ancestry** — template stamping squashes every branch to a single parentless
   commit, which breaks the merge-based Dawn flows (`dawn_sync` workflow, `fireball_orchestrator`'s
   `invoke shopify.dawn.upgrade --site=<name>`):

   ```sh
   git remote add dawn https://github.com/Shopify/dawn.git
   git fetch dawn main --no-tags
   git push --force origin refs/remotes/dawn/main:refs/heads/dawn_vanilla
   git fetch origin && git branch -f dawn_vanilla origin/dawn_vanilla
   git fetch dawn refs/tags/v15.5.0:refs/tags/dawn-v15.5.0 --no-tags
   git checkout main
   git merge dawn-v15.5.0 --allow-unrelated-histories -s ours --no-ff -m "chore: graft Dawn v15.5.0 ancestry into main"
   git push origin main
   ```

2. Update `README.md` + `.github/copilot-instructions.md` for the new brand name.
3. **Delete `.github/workflows/publish_release.yml`** — template-only; brand repos release through `release.yml`.
4. Create the `development` branch from `main` (after the graft), make it the **default branch**
   (`gh repo edit <repo> --default-branch development`), and set branch protection on `development` + `main`.
5. Add secrets manually (never via AI): `BOT_PRIVATE_KEY`, `SHOPIFY_CLI_THEME_TOKEN`,
   `SHOPIFY_FLAG_STORE`, `SHOPIFY_THEME_ID_DEV`, `SHOPIFY_THEME_ID_PRD`; variable: `BOT_APP_ID`.
6. Register the new repo as a site in `fireball_orchestrator`'s `tmp/.shopify/config.yml`
   (`repo_local_path`, `store`, `theme.id_dev`, `theme.id_prd`, `theme.token`) so `--site=<name>`
   dev tooling works.

## Branches

- `main` — production theme
- `development` — working branch (dev deploys on push)
- `dawn_vanilla` — pristine upstream Shopify/dawn; synced by the Dawn Sync workflow, merged into `development` manually when upgrading

## Workflows

Thin callers into `fireballenterprise/workflows_shopify`, floating major tag `@v4`. All bump /
deploy / theme-check logic is in that repo's composite actions
(`actions/{bump_version,deploy_theme,theme_check}`).

| Caller | Trigger | Purpose |
|--------|---------|---------|
| `tests.yml` | PR → `development` / `main` | theme-check + yamllint + actionlint |
| `deploy.yml` | push → `development`, manual | bump `VERSION` patch + deploy dev theme (or prd manually) |
| `release.yml` | manual | optional milestone bump, promote → `main`, deploy prd, GitHub Release |
| `dawn_sync.yml` | monthly, manual | sync `dawn_vanilla` with upstream Dawn |
| `publish_release.yml` | push → `main` (VERSION change), manual | **Template repo only** — tags + publishes a Release off `main` (this repo has no `development` branch/store for the normal flow). Delete it in a stamped brand repo. |

## Versioning

Plain `Major.Minor.Patch` on both `development` and `main` — patch bumped per merge to
`development` (by `deploy.yml`), promote-as-is on release. No `v` prefix on release tags. The home
page carries the current version via `snippets/fireball-version.liquid`.
