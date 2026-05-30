# Dashboard — `aurealis-dashboard` (MVP)

A thin command center between R2 (where rendered carousels arrive) and Instagram (where they get posted). The reviewer opens it, picks a draft, edits caption, picks an account, hits publish. That's it.

Lives in its own repo (`aurealis-dashboard`). This doc is the contract; it sits inside `agent-carousel/docs/marketing-pipeline/` because that's where the rest of the pipeline docs live.

---

## What the dashboard does (and only this)

1. **Inbox** — shows generated carousels waiting to be posted.
2. **Reviewer** — preview slides, edit caption + hashtags, pick one of the 8 Instagram accounts, click **Publish**.
3. **Performance** — see how posted carousels are doing (reach, saves, shares, follows).

No scheduling. No auto-routing. No warming. No `/system` page. No batch operations. The human is the orchestrator.

---

## Pipeline

```
agent-carousel skill (15×/day, autonomous)
   → HTML/CSS slides + metadata.json
   → GitHub Actions renders → JPEGs in R2
   → render workflow POSTs to dashboard /api/webhooks/render
   → draft appears in /inbox
   → reviewer opens, validates, picks account, clicks Publish
   → server action calls Meta Graph API (3 steps, ~15s)
   → carousel goes live on Instagram
   → cron pulls analytics for 7 days
```

Boundary: agent-carousel ends at "JPEG in R2 + webhook fired." Dashboard owns everything after.

---

## Stack

| Layer | Choice |
|---|---|
| Framework | Next.js 16 App Router on Vercel (Fluid Compute, Node 24) |
| Database | Supabase (Postgres) via Vercel Marketplace |
| Auth | Clerk via Vercel Marketplace, 2-email allowlist |
| Image store | Cloudflare R2 (existing, public bucket) |
| Styling | Tailwind + shadcn/ui |
| Meta API client | Plain `fetch` against Graph API v23.0 |

---

## Data model — 4 tables

```sql
create table accounts (
  id              uuid primary key default gen_random_uuid(),
  handle          text unique not null,         -- '@ethos.fight'
  display_name    text not null,
  bio             text,
  link            text,
  ig_user_id      text unique not null,         -- Meta's 17-digit IG ID
  profile_pic_url text,
  created_at      timestamptz not null default now()
);

create type draft_state as enum ('pending', 'published', 'skipped');

create table drafts (
  id                uuid primary key default gen_random_uuid(),
  slug              text unique not null,         -- '2026-05-24-the-man-you-are-at-2-am'
  title             text not null,
  caption           text not null,
  hashtags          text[] not null,
  pillar            text,                          -- from metadata.json, used for analytics filters
  themes            int[],
  slide_image_urls  text[] not null,               -- R2 public JPEG URLs in order
  cover_image_url   text not null,
  state             draft_state not null default 'pending',
  ingested_at       timestamptz not null default now()
);
create index drafts_state_idx on drafts (state, ingested_at desc);

create table publishes (
  id                  uuid primary key default gen_random_uuid(),
  draft_id            uuid not null references drafts(id),
  account_id          uuid not null references accounts(id),
  ig_media_id         text unique,                 -- null if publish failed
  ig_permalink        text,
  caption_as_posted   text not null,
  hashtags_as_posted  text[] not null,
  succeeded           boolean not null,
  error_message       text,
  published_by        text not null,               -- clerk user id
  published_at        timestamptz not null default now()
);
create index publishes_account_idx on publishes (account_id, published_at desc);

create table insights (
  id                bigserial primary key,
  publish_id        uuid not null references publishes(id) on delete cascade,
  fetched_at        timestamptz not null default now(),
  reach             int,
  saves             int,
  shares            int,
  comments          int,
  likes             int,
  follows_from_post int,
  link_clicks       int
);
create index insights_publish_idx on insights (publish_id, fetched_at desc);
```

RLS enabled on all 4 tables; authenticated Clerk session required for everything except webhooks + cron.

---

## Pages — only 3

### `/inbox`

List of drafts where `state='pending'`, newest first. Each row: cover thumbnail, title, caption preview, "Review →" link, "Skip" button.

### `/inbox/[draftId]` — the reviewer

Two columns.

**Left**: all N slides previewed at native aspect (1080×1350). Scroll or click-to-zoom.

**Right**:
- Caption textarea (pre-filled, 2200 char counter)
- Hashtag input (chip-style or comma-separated, your call)
- Account dropdown (8 options from `accounts` table)
- **PUBLISH** button — disabled until account picked

On publish: modal blocks with "Publishing… ~15s." On success: confirmation with IG permalink. On failure: error message + retry button.

### `/performance`

List of published carousels, filterable by account. Each row shows: thumbnail, posted-when, account, reach, saves, shares, follows. Click a row → full slide preview + caption + metrics over time.

That's all three pages.

---

## The one server action — `publishDraft`

```
publishDraft(draftId, accountId, captionEdit?, hashtagsEdit?):
  1. Verify Clerk session
  2. Load draft + account; reject if draft.state != 'pending' or account missing ig_user_id
  3. Final caption = (captionEdit ?? draft.caption) + "\n\n" + hashtags joined as #tag
  4. For each slide_image_url:
     POST {ig_user_id}/media (image_url, is_carousel_item=true) → container_id
     Poll GET {container_id}?fields=status_code every 2s up to 30s until FINISHED
  5. POST {ig_user_id}/media (media_type=CAROUSEL, children=ids, caption=final) → parent_id
     Poll until FINISHED
  6. POST {ig_user_id}/media_publish (creation_id=parent_id) → ig_media_id
  7. Insert publishes row (succeeded=true, ig_media_id, permalink, caption_as_posted, ...)
  8. Update drafts.state = 'published'
  9. Return { ig_media_id, permalink }

On any failure in steps 4–6:
  - Insert publishes row (succeeded=false, error_message)
  - Draft stays 'pending' — reviewer can retry
  - Throw — UI shows error modal
```

Typical run: 10-15 seconds. Vercel Function timeout is 300s — no concern.

---

## Webhook contract — `agent-carousel` → dashboard

After R2 upload completes, the render workflow POSTs:

```http
POST /api/webhooks/render
Content-Type: application/json
X-Aurealis-Signature: sha256=<hex>
X-Aurealis-Timestamp: <unix>

{
  "slug": "2026-05-24-the-man-you-are-at-2-am",
  "title": "...",
  "caption": "...",
  "hashtags": ["..."],
  "pillar": "Real Talk",
  "themes": [4],
  "slide_image_urls": ["https://r2.../slide-01.jpg", ...],
  "cover_image_url": "https://r2.../slide-01.jpg"
}
```

Signature: `sha256` HMAC of `{timestamp}.{body}` using `RENDER_WEBHOOK_SECRET`. Reject if timestamp older than 5 min.

Dashboard inserts a `drafts` row and returns `200 { draft_id }`. On duplicate slug (re-render), return existing row.

### Change to `agent-carousel`

Add a final step to `.github/workflows/render-carousels.yml`:

```yaml
- name: Notify dashboard
  if: success()
  env:
    DASHBOARD_URL: ${{ secrets.DASHBOARD_WEBHOOK_URL }}
    SHARED_SECRET: ${{ secrets.RENDER_WEBHOOK_SECRET }}
  run: node scripts/notify-dashboard.js
```

`scripts/notify-dashboard.js` reads the rendered carousel's `metadata.json`, constructs the payload, computes the HMAC, POSTs. Retry 3× with backoff.

---

## Cron — `/api/cron/insights` (hourly)

For each `publishes` row with `succeeded=true` and `published_at` within the last 7 days, fetch IG Insights and insert a row:

```
GET https://graph.facebook.com/v23.0/{ig_media_id}/insights?
    metric=reach,saves,shares,comments,likes,follows_from_post,link_clicks
    &access_token=<META_SYSTEM_USER_TOKEN>
```

Vercel cron config in `vercel.ts`:

```ts
import { type VercelConfig } from '@vercel/config/v1';
export const config: VercelConfig = {
  framework: 'nextjs',
  crons: [{ path: '/api/cron/insights', schedule: '0 * * * *' }]
};
```

That's the only cron.

---

## Meta API — endpoints used

Base: `https://graph.facebook.com/v23.0`. All requests authenticated with `META_SYSTEM_USER_TOKEN`.

| Purpose | Method + Path |
|---|---|
| Create child container | `POST /{ig-user-id}/media` |
| Create carousel parent | `POST /{ig-user-id}/media` (with `media_type=CAROUSEL`) |
| Poll container status | `GET /{container-id}?fields=status_code` |
| Publish | `POST /{ig-user-id}/media_publish` |
| Insights | `GET /{ig-media-id}/insights?metric=...` |

Image URLs must be public JPEGs (R2 bucket is public; render pipeline outputs JPEG — both done). See `01-meta-setup.md` for getting `ig-user-id` per account and the System User token.

---

## Env vars

```
# Supabase (auto-provisioned by Vercel Marketplace)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

# Clerk (auto-provisioned)
CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=

# Meta
META_SYSTEM_USER_TOKEN=
META_API_VERSION=v23.0

# Webhook
RENDER_WEBHOOK_SECRET=

# Cron auth (Vercel sets this automatically)
CRON_SECRET=
```

---

## Build order (3 days)

**Day 1 — provisioning + ingest**
- Create `aurealis-info/aurealis-dashboard` repo, `create-next-app`, deploy to Vercel
- Add Supabase + Clerk via Marketplace; run the SQL above; seed 8 accounts (handle + ig_user_id)
- Configure Clerk allowlist (you + collaborator)
- Build `/api/webhooks/render` (HMAC verify, insert draft)
- Add `scripts/notify-dashboard.js` to agent-carousel; wire into render workflow
- **Smoke test**: trigger fake webhook locally → draft row appears

**Day 2 — reviewer + publish**
- Build `/inbox` page (list pending drafts)
- Build `/inbox/[draftId]` reviewer page (slides left, caption/hashtags/account picker/PUBLISH button right)
- Implement `publishDraft` server action (3-step Meta carousel publish + polling)
- **End-to-end test**: real generated draft → review → edit caption → publish → confirm on IG

**Day 3 — performance**
- Build `/api/cron/insights` (hourly poller for 7-day window)
- Build `/performance` page (list of published carousels with metrics, filterable by account, click for detail)

That's the MVP. Three days for a working pipeline.

---

## What we deliberately left out

| Cut | Bring back when |
|---|---|
| Auto-scheduling, slot windows, posting time jitter | Reviewer says "I'm tired of manually spacing posts" |
| Warming state machine per account | We launch a brand-new account and want to ramp it slowly |
| Auto-routing / "suggested account" | We have 60+ days of data and clear per-account performance patterns |
| Bulk publish / bulk approve | Daily reviewer time exceeds 30 minutes |
| `/accounts` management page (edit bios, etc.) | We need to change an account profile and don't want to touch the DB |
| `/system` page (token health, webhook log, errors) | A real outage makes us wish we had it |
| Audit log (who published what when) | Two reviewers need to investigate a misfire |
| Writing `published.json` back to agent-carousel | We want repo-side history independent of the DB |
| `WINNERS.md` auto-commit + skill consumption | 30+ days of insights show clear winning patterns worth feeding back |
| `/today` overview page | Day-of-launch feel demands more glance-ability |
| Soft warning UX (last-published-Xh-ago chips, hashtag dedupe) | We actually flood an account or repeat a hashtag set |
| Token expiry alerts | A publish fails because the token expired |

Capture the idea, name the trigger, defer until it fires. Build only what you need today.
