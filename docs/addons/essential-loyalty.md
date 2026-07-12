# Essential VIP Loyalty Program
Loyalty points and VIP tier program (Fireball Points). Customers earn points per dollar spent,
with tier multipliers driven by `VIP:*` customer tags.

## App Details
| Field | Value |
|-------|-------|
| Handle | `essential-loyalty` |
| Status | Active |
| Theme embed | `shopify://apps/essential-loyalty/blocks/theme-extension` (app embed in `config/settings_data.json`) |

## Theme Footprint
- App embed enabled in `config/settings_data.json`
- App blocks in `templates/page.essential-loyalty.json` (loyalty landing page)

## Related Fireball Customizations
- **VIP loyalty tiers section** — `sections/fireball-loyalty-tiers.liquid` renders the tier
  cards + comparison table on the loyalty page
- **Earned points message** — `snippets/fireball-earned-points.liquid` shows "You'll earn N
  Fireball Points" in cart totals; tier multipliers read `VIP:Flame` / `VIP:Blaze` /
  `VIP:Inferno` / `VIP:Firestorm` customer tags (base rate 10 pts/$1)

## Configuration
<!-- TODO: capture app settings here (earn rates, tier thresholds, rewards, customer tag mapping) -->
- Tier names: Spark (base), Flame, Blaze, Inferno, Firestorm
- Earn rates mirrored in `snippets/fireball-earned-points.liquid`: 10 / 12.5 / 15 / 17.5 / 20 pts per $1
  — **keep the snippet in sync if rates change in the app**
