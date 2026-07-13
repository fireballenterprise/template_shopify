# Create a GitHub Actions Bot (GitHub App)
Workflows using the default `GITHUB_TOKEN` cannot push to `development` (PR-required branch)
or create pull requests (org Actions policy). A GitHub App bot issues short-lived tokens that
can bypass branch protection, without a paid seat or a long-lived PAT.

## 1. Create the GitHub App
1. Go to the org: `https://github.com/organizations/fireballenterprise/settings/apps`
2. Click **New GitHub App**
3. Fill in:
   - **GitHub App name**: `fireball-actions-bot`
   - **Homepage URL**: `https://github.com/fireballenterprise/shopify_dawn_theme`
   - **Webhook**: uncheck **Active**
4. Set **Repository permissions**:
   - **Contents**: Read and write
5. **Where can this GitHub App be installed?**: Only on this account
6. Click **Create GitHub App**

## 2. Generate a Private Key
1. On the app's **General** page, note the **App ID**
2. Scroll to **Private keys** → **Generate a private key** (downloads a `.pem` file)

## 3. Install the App on the Repo
Creating the app only registers it — it has no repo access until installed.
1. Open the app's settings page:
   `https://github.com/organizations/fireballenterprise/settings/apps/fireball-actions-bot`
   (or org **Settings** → **Developer settings** → **GitHub Apps** → **Edit** next to the app)
2. In the left sidebar, click **Install App**
3. Click **Install** next to the `fireballenterprise` org
4. On the install screen, select **Only select repositories**
5. Open the **Select repositories** dropdown and pick `shopify_dawn_theme`
6. Click **Install** — GitHub shows the app's permissions (Contents: Read and write); confirm
7. Verify: repo **Settings** → **GitHub Apps** (under Integrations) lists `fireball-actions-bot`

To add/remove repos later: org **Settings** → **Third-party Access** → **GitHub Apps** →
**Configure** next to the app.

## 4. Let the Bot Bypass Branch Protection
In `shopify_dawn_theme` → **Settings** → **Branches** → edit the `development` rule:
1. Under **Require a pull request before merging**, enable
   **Allow specified actors to bypass required pull requests**
2. Add `fireball-actions-bot` to the bypass list

## 5. Add Repo Secret and Variable
In `shopify_dawn_theme` → **Settings** → **Secrets and variables** → **Actions**:
1. **Variables** tab → **New repository variable**: `BOT_APP_ID` = the App ID
2. **Secrets** tab → **New repository secret**: `BOT_PRIVATE_KEY` = full contents of the `.pem`

## 6. Use the Bot Token in Workflows
Generate the token **before** checkout and pass it to checkout as `token` (`deploy.yml`
build_version job, `release.yml` version job):

```yaml
- name: Generate bot token
  id: bot-token
  uses: actions/create-github-app-token@v3
  with:
    app-id: ${{ vars.BOT_APP_ID }}
    private-key: ${{ secrets.BOT_PRIVATE_KEY }}

- uses: actions/checkout@v7
  with:
    ref: development
    token: ${{ steps.bot-token.outputs.token }}
```

Commit with `[skip ci]` and push directly to `development`:

```yaml
git commit -m "chore: bump VERSION to $new_version [skip ci]"
git push origin HEAD:development
```

## Notes
- **`[skip ci]` is the infinite-loop guard**: bot-token pushes trigger workflows (unlike
  `GITHUB_TOKEN` pushes), so an unguarded bump push to `development` would re-run Deploy forever
- **Checkout must receive the bot token**: `actions/checkout` persists its token as an
  `http.extraheader` git config that overrides any token embedded in a push URL — pushing to a
  `https://x-access-token:...@github.com/...` URL after a default checkout still authenticates
  as `github-actions[bot]` and gets 403
- Rotate the key: generate a new `.pem` on the app page, update `BOT_PRIVATE_KEY`, delete the old key
- The app token expires after 1 hour and is scoped to the installed repos only
