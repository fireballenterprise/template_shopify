---
description: "Use when adding, changing, or removing Fireball customizations on top of stock Dawn. Tracks every hand-written customization and its current status."
applyTo: "{assets,config,layout,locales,sections,snippets,templates}/**"
---
# Fireball Customizations

Tracking table for every hand-written Fireball customization layered on top of stock Dawn.
See `shopify.instructions.md` → "Fireball Customization Markers" for the comment-marker
convention that makes these findable in code.

## Maintaining This Table
- **Add a row** whenever a new customization lands (marker comment in code + row here)
- **Status lifecycle**:
  - `Active` — live in the theme
  - `Disabled` — commented out in code but kept for reference; note where/why
  - Removed completely from code → **delete the row** from this table
- Keep rows **alphabetical** by customization name
- Third-party app files (loyalty, chat widgets, etc.) are not tracked here — we don't own them

## Customizations
| Customization | Purpose | Files | Status | Notes |
|---------------|---------|-------|--------|-------|
| BCPO uploaded file preview | Show a thumbnail (or "Uploaded file" link) for customer-uploaded custom barcode files in the cart page and cart drawer | `sections/main-cart-items.liquid`, `snippets/cart-drawer.liquid` | Active | Two marked blocks per file (image vs. non-`/uploads/` property branch) |
| Bundle color pickers (featured product) | Bundle picker on the home-page Featured Product section | `sections/featured-product.liquid` (~line 414) | Disabled | Render block commented out; snippet itself still Active via product form |
| Bundle color pickers (product form) | Per-color variant pickers for products tagged `7-Color-Bundles`, inside the real product form | `snippets/fireball-bundle-colors.liquid`, `snippets/buy-buttons.liquid` | Active | An older commented-out copy of the render sits just above the active one in `buy-buttons.liquid` |
| Chat country filter | Hide the Shopify chat bubble unless visitor country is US, CA, GB, DE, or MX | `layout/theme.liquid` (script near end of `<body>`) | Active | Uses `localization.country.iso_code` + polling for the chat button |
| Coming Soon badge | "Coming Soon..." card badge for products tagged `Coming Soon` | `snippets/card-product.liquid`, `assets/badge-coming-soon.css` | Active | ⚠ `badge-coming-soon.css` is not loaded by any `stylesheet_tag` — badge renders unstyled |
| Dark mode | Manual light/dark toggle with localStorage persistence | `assets/fireball-dark-mode.css`, `layout/theme.liquid` (CSS link + toggle script), `sections/header.liquid` (toggle button) | Disabled | All three hookup points commented out; CSS file kept for reference |
| Earned points message | "You'll earn N Fireball Points" line in cart totals, with VIP-tier multipliers from customer tags | `snippets/fireball-earned-points.liquid`, `sections/main-cart-footer.liquid`, `assets/base.css` (`.fireball-earned-points`) | Active | Base rate 10 pts/$1; tiers Flame/Blaze/Inferno/Firestorm via `VIP:*` tags |
| Featured product image click | Clicking the Featured Product image goes to the product page instead of opening the zoom modal | `sections/featured-product.liquid` (script after media modal) | Active | Intercepts `.product__modal-opener` / `.product__media-toggle` clicks |
| Inbox hidden on mobile | Hide the Shopify Inbox chat bubble on screens ≤767px | `assets/fireball-inbox.css`, `layout/theme.liquid` (stylesheet include) | Active | |
| New badge | Red "New" card badge for products tagged `New`, with pulse animation | `snippets/card-product.liquid`, `assets/badge-new.css`, `layout/theme.liquid` (stylesheet include) | Active | |
| Social links open in new tab | Footer social links get `target="_blank"` + `rel="noopener noreferrer"` | `layout/theme.liquid` (script near end of `<body>`) | Active | |
| Strict variant media filter | Product media gallery only shows media attached to the selected variant (or unattached media) | `snippets/product-media-gallery.liquid` | Active | Marked `FIREBALL CHANGE ... END FIREBALL CHANGE` |
| Theme version stamp | HTML comment with the deployed theme version on the home page (view source to verify which build is live) | `snippets/fireball-version.liquid`, `layout/theme.liquid` (render in `<head>`) | Active | Version string restamped by the `version.bump_*` tasks (`modules/version/bump.py`); deploy/release workflows stage the snippet alongside VERSION |
| VIP loyalty tiers section | Custom "Fireball VIP Tiers" section: tier cards + comparison table | `sections/fireball-loyalty-tiers.liquid` | Active | Used by `templates/page.essential-loyalty.json` |

## Installed Apps (Add-ons)
Full list from the Shopify admin Apps page (verified 2026-07-08). Handles come from
`shopify://apps/...` references in the theme (app embeds in `config/settings_data.json`,
app blocks in `templates/*.json`); admin-only apps have no theme footprint. Each app has a
config doc in `docs/addons/` — keep both the row and the doc updated when an app is added,
disabled, or uninstalled (uninstalled → delete the row and the doc).

| App | Handle | Theme Footprint | Status | Doc |
|-----|--------|-----------------|--------|-----|
| Essential Loyalty | `essential-loyalty` | App embed + app blocks in `templates/page.essential-loyalty.json` | Active | `docs/addons/essential-loyalty.md` |
| Flow | — | None (admin-only) | Active | `docs/addons/flow.md` |
| Forms | `forms` | App embed | Active | `docs/addons/forms.md` |
| Judge.me Reviews | `judge-me-reviews` | App embed + app block in `templates/product.json` | Active | `docs/addons/judge-me-reviews.md` |
| Kin Custom | — | None (admin-only) | Active | `docs/addons/kin-custom.md` |
| Messaging (formerly Shopify Email) | — | None (admin-only) | Active | `docs/addons/messaging.md` |
| Printful | — | None (admin-only) | Active | `docs/addons/printful.md` |
| Printify: Print on Demand | — | None (admin-only) | Active | `docs/addons/printify.md` |
| RT: Size Chart, Size Guide | `rt-size-chart-size-guide` | App embed | Active | `docs/addons/rt-size-chart-size-guide.md` |
| Shippo - Simplified Shipping | — | None (admin-only) | Active | `docs/addons/shippo.md` |
| Store Migration | — | None (admin-only) | Active | `docs/addons/store-migration.md` |
| Theme Access | — | None (admin-only) | Active | `docs/addons/theme-access.md` |
| Translate & Adapt | — | None (admin-only) | Active | `docs/addons/translate-and-adapt.md` |
| VO Product Options (BCPO) | `vo-product-options` | App embed | Active | `docs/addons/vo-product-options.md` |
| Zendrop - Dropshipping & POD | — | None (admin-only) | Active | `docs/addons/zendrop.md` |

## Sales Channels
Channels from the admin "Sales channels" list (verified 2026-07-08). Channels install
separately from apps — Inbox lives here, not in Installed apps. Each channel has a doc in
`docs/sales_channels/`; same lifecycle as apps (removed → delete the row and the doc).

| Channel | Theme Footprint | Status | Doc |
|---------|-----------------|--------|-----|
| Agentic | None | Active | `docs/sales_channels/agentic.md` |
| Facebook & Instagram | None | Active | `docs/sales_channels/facebook-instagram.md` |
| Inbox | Chat app embed (`inbox` handle) | Active | `docs/sales_channels/inbox.md` |
| Online Store | The entire theme (this repo) | Active | `docs/sales_channels/online-store.md` |
| Point of Sale | None | Active | `docs/sales_channels/point-of-sale.md` |
| Shop | None | Active | `docs/sales_channels/shop.md` |
| TikTok | None | Active | `docs/sales_channels/tiktok.md` |
