# Inbox
Shopify Inbox — the storefront live-chat widget (formerly Shopify Chat / Ping). Installs as
a sales channel, so it appears here rather than in the admin "Installed apps" list. Distinct
from the **Messaging** app (`docs/addons/messaging.md`), which is the renamed Shopify Email
for email/SMS campaigns.

## Channel Details
| Field | Value |
|-------|-------|
| Theme embed handle | `inbox` |
| Theme embed | `shopify://apps/inbox/blocks/chat` (app embed in `config/settings_data.json`) |
| Status | Active |

## Related Fireball Customizations
- **Chat country filter** — script in `layout/theme.liquid` hides the chat bubble unless the
  visitor's country is US, CA, GB, DE, or MX
- **Inbox hidden on mobile** — `assets/fireball-inbox.css` hides the chat bubble on screens
  ≤767px (loaded from `layout/theme.liquid`)

## Configuration
<!-- TODO: capture chat appearance, availability hours, saved replies, AI/instant answers setup -->
