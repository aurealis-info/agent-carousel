# Meta Setup — Instagram Content Publishing for Aurealis

End-to-end checklist for going from zero to a working `instagram_content_publish` permission on a System User token, with one Meta App publishing to multiple IG Business accounts across multiple brands.

Strategy: **multiple sub-niche accounts per brand** (e.g. 4× ethos: `ethos`, `ethos.quotes`, `ethos.shorts`, `ethos.verses`). 15 carousels/day, 2 posts/account/day soft limit.

Expect: ~2 hours hands-on, plus **1–2 weeks waiting** on Meta App Review.

---

## Phase A — Business Portfolio (one-time, ~15 min)

The Portfolio is the umbrella that owns Pages, IG accounts, the Meta App, and the System User token. Everything else nests inside it.

- [ ] Go to https://business.facebook.com/ → **Create Account** (skip if Aurealis Portfolio already exists)
- [ ] Business name: `Aurealis`
- [ ] Add a payment method (Business Settings → Billing) — required even if you're not running ads; some flows refuse without it
- [ ] Business Settings → **Business Info** → confirm tax ID / address are filled in (needed for App Review)
- [ ] Record the Business Portfolio ID (Business Settings → Business Info, top of page)

---

## Phase B — Facebook Pages + IG Business accounts (per account, ~10 min each)

Each IG account needs its own FB Page in the Business Portfolio. The Page can be empty — IG just requires the link.

Do this for every IG account: `ethos`, `ethos.quotes`, `ethos.shorts`, `ethos.verses` (and same pattern for lokin etc. when you start them).

For each account:

- [ ] Create the FB Page in the Portfolio: Business Settings → **Accounts → Pages → Add → Create a new Page**. Category: "Brand". Name should match or mirror the IG handle.
- [ ] On the phone (or via web), convert the IG account to **Business** (Settings → Account type → Switch to Professional → Business). **Don't pick Creator** — Content Publishing API requires Business.
- [ ] In the IG app: Settings → **Business → Connected accounts → Facebook** → link to the FB Page you just made
- [ ] Back in Business Settings → **Accounts → Instagram Accounts → Add → Connect your Instagram Account** → confirm the IG account is now listed and linked to the right Page
- [ ] Record the IG account ID — fetch via Graph API once Phase C is done, or look it up in Meta Business Suite. Format: 17-digit number.

**Brand strategy reminder for 4× same-brand**: sub-accounts must look like real sub-niches, not clones of each other. Differentiate by name, profile pic, bio, link, and **never post the same carousel to two sub-accounts on the same day**. The dashboard will enforce this with a daily uniqueness check per content_hash + brand.

---

## Phase C — Meta App (one-time, ~20 min)

One Meta App publishes to all accounts. Don't make one app per account.

- [ ] Go to https://developers.facebook.com/apps → **Create App**
- [ ] Use case: **Other** → Type: **Business**
- [ ] App name: `Aurealis Publisher`
- [ ] In the app dashboard, add product: **Instagram → Set Up** (specifically "Instagram API with Facebook Login" — *not* "Instagram API with Instagram Login"; the FB Login path is what supports multi-account via System User tokens)
- [ ] Add product: **Facebook Login for Business** (only needed during initial OAuth; System User token replaces this in production)
- [ ] App Settings → **Basic** → fill in: Privacy Policy URL, Terms of Service URL, App Icon (1024×1024), Category. **App Review will reject without all four.**
- [ ] App Settings → Basic → **Verify Business** — links the App to your Business Portfolio. Required for advanced permissions.
- [ ] Record `App ID` and `App Secret`

---

## Phase D — System User + non-expiring token (one-time, ~10 min)

System User tokens **do not expire**. This is the credential the publisher uses 24/7. Regular user tokens (even long-lived) expire in 60 days — don't use them for automation.

- [ ] Business Settings → **Users → System Users → Add**
- [ ] Name: `aurealis-publisher`. Role: **Admin** (needed to manage Pages; Employee role can't publish)
- [ ] Assign assets to the System User:
  - [ ] **Pages**: add every FB Page from Phase B, role = Full control (`Manage Page`)
  - [ ] **Apps**: add the Aurealis Publisher app, role = Develop app
- [ ] On the System User row, click **Generate New Token** → select the Aurealis Publisher app → scopes:
  - [ ] `instagram_basic`
  - [ ] `instagram_content_publish`
  - [ ] `instagram_manage_insights` (for analytics later)
  - [ ] `pages_show_list`
  - [ ] `pages_read_engagement`
  - [ ] `business_management`
- [ ] **Copy the token immediately** — Meta will never show it again. Save to a password manager.
- [ ] Validate the token at https://developers.facebook.com/tools/debug/accesstoken/ — should say `Expires: Never` and list the scopes above

Token format: starts with `EAA...`, ~200 chars. Store in `aurealis-info/authentification/meta-system-user-token.txt` (private repo).

---

## Phase E — App Review (the slow part, 5–14 days)

`instagram_content_publish` is an Advanced permission. Without App Review, the token works only for accounts owned by people with a role on the app (fine for testing, not for production at 15/day across many accounts).

- [ ] App dashboard → **App Review → Permissions and Features**
- [ ] Request: `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`, `business_management`
- [ ] For `instagram_content_publish` you must submit:
  - [ ] A **screencast** (2–4 min) showing: user signs into your dashboard, sees a draft carousel, clicks publish, the carousel appears on the IG account
  - [ ] Step-by-step text instructions matching the screencast
  - [ ] Reason text: "Aurealis is a multi-brand content studio. Our editorial team uses this dashboard to review AI-generated carousel drafts, edit captions, assign to brand-managed Instagram Business accounts, and publish on a controlled schedule. The instagram_content_publish permission is required to programmatically post carousels to Instagram Business accounts we own."
- [ ] Submit. First review typically comes back in 3–7 days, often with rejections that read like nitpicks — Meta's review is heuristic. Common rejection reasons + fixes:
  - "We couldn't see the permission being used" → re-record with the network panel open so they can see the API call
  - "Use case is not clear" → re-record with a voiceover explicitly naming the permission
  - "App is not publicly accessible" → make sure your dashboard URL is reachable without VPN; Meta reviewers are usually in India/Philippines
- [ ] Once approved, the permission is active for **all IG accounts the Portfolio owns**, including ones added later. No re-review per account.

While waiting, you can fully test with accounts owned by app developers (add yourself as a Tester in App Roles), so don't sit idle — Phase F can run in parallel.

---

## Phase F — Smoke test publish (~30 min)

Sanity-check the token + the 3-step carousel flow before any code is written.

- [ ] Pick one test IG account (ideally a throwaway one, not your main ethos)
- [ ] Get its `IG_USER_ID`:
  ```
  GET https://graph.facebook.com/v23.0/me/accounts?access_token=<TOKEN>
  ```
  Find the Page, then:
  ```
  GET https://graph.facebook.com/v23.0/<PAGE_ID>?fields=instagram_business_account&access_token=<TOKEN>
  ```
  → returns `instagram_business_account.id` = your `IG_USER_ID`
- [ ] Pick 2 public JPEG URLs (any public image works — even a Cloudflare R2 URL)
- [ ] Create child container 1:
  ```
  POST https://graph.facebook.com/v23.0/<IG_USER_ID>/media
    image_url=<url1>
    is_carousel_item=true
    access_token=<TOKEN>
  ```
  → returns `{id: "child1"}`
- [ ] Same for child 2 → `child2`
- [ ] Create parent:
  ```
  POST .../media
    media_type=CAROUSEL
    children=child1,child2
    caption=Test
    access_token=<TOKEN>
  ```
  → returns `{id: "parent"}`
- [ ] Publish:
  ```
  POST .../media_publish
    creation_id=parent
    access_token=<TOKEN>
  ```
  → returns `{id: "media123"}` and the carousel is live
- [ ] Check `GET .../<IG_USER_ID>/content_publishing_limit` — confirms you used 1/100 for the 24h window

If this works end-to-end, the Meta side is done. Everything from here is our code.

---

## Outputs (what the dashboard/publisher will need)

After all phases, these are the values the publisher reads at runtime:

| Name | Where it lives | Example |
|---|---|---|
| `META_SYSTEM_USER_TOKEN` | Vercel env (production), GitHub secret (CI) | `EAA...` |
| `META_APP_ID` | Vercel env | `1234567890` |
| `META_APP_SECRET` | Vercel env (used only for token debug + webhook verification) | `abc...` |
| `META_API_VERSION` | code constant | `v23.0` |
| Per-account: `ig_user_id`, `fb_page_id`, `handle`, `brand`, `pillar`, `warming_state`, `daily_cap`, `slot_windows` | Supabase `accounts` table | — |

---

## Critical gotchas specific to your strategy

1. **PNG → JPEG**: Meta only accepts JPEG. The render pipeline outputs `.jpg` at quality 92 (done).
2. **Token leaks are catastrophic**: a System User token never expires, so a leak gives someone forever-access to publish on every account. Store only in Vercel env + `aurealis-info` (private), never in the agent-carousel repo, never in logs.
3. **App Review is per-permission, not per-account**: get `instagram_content_publish` approved once, all current and future Portfolio-owned accounts are covered.
4. **Don't switch any IG account back to Personal even briefly** — Meta sometimes invalidates the IG-Page link and you have to redo the connection.
5. **Sub-niche similarity = de-rank**: 4× ethos accounts that look like reposts of each other will all get throttled together. Variant generation isn't a nice-to-have, it's required infrastructure. See `02-account-strategy.md` (next doc).
6. **Webhook for failure visibility**: subscribe the app to `instagram` webhooks → you'll get notified when a publish fails post-acceptance (e.g., Meta retroactively rejects content). Without this you only know a post died by checking IG manually.

---

## Checkpoint

When all of A–F are done you'll have:

- One Business Portfolio with ≥1 FB Page per IG account
- One Meta App with `instagram_content_publish` approved
- One System User token that publishes to any current or future account in the Portfolio
- A proven smoke-test carousel posted to a real IG account

That's the moment the dashboard + publisher work becomes pure code with no more Meta UI clicking.
