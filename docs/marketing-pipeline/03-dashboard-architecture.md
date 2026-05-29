# Dashboard Architecture — `aurealis-dashboard` (MVP)

The complete design spec for the Aurealis marketing command-center dashboard. This doc is self-contained: someone picking it up cold should be able to build the whole thing without further context.

The dashboard lives in its **own repo** (`aurealis-dashboard`) and consumes assets produced by the `agent-carousel` repo. This doc lives inside `agent-carousel/docs/marketing-pipeline/` because (a) it's part of the marketing pipeline series and (b) it documents the *contract* between the two repos.

---

## 0. Scope (read this first)

**This is an MVP**. The dashboard is a CRM-style command center that does exactly four things:

1. **Validate** generated carousels before they go live (preview slides + edit caption/hashtags).
2. **Assign + publish** a carousel to a specific Instagram account with a single button click — publishes immediately, no scheduling.
3. **Track** what's been posted across all accounts.
4. **Measure** how each post performs (IG Insights pulled on a schedule).

What this dashboard explicitly does **not** do (deferred):

- ❌ Auto-scheduling, slot windows, posting time jitter, calendar grids
- ❌ Warming-state machines, daily caps, automatic posting cadence
- ❌ Auto-routing / "suggested account" engines
- ❌ Bulk publish, bulk approve
- ❌ Multi-step approval workflows

**The reviewer is the orchestrator.** They look at the inbox, pick a carousel, edit the caption, pick the account, hit publish. If they want to space posts out across the day, they look at the inbox at different times. If they want to avoid flooding an account, they see "last published 2 hours ago" on the account chip and use judgment.

The "10 anti-pattern rules" from `02-account-strategy.md` (content hash uniqueness, hashtag rotation, etc.) are enforced as **soft warnings** in the UI — never as automatic gates. The reviewer can override anything.

The deferred items aren't bad ideas — they're the right next phase after we know what the MVP actually feels like in practice. See §17 ("future considerations") at the end.

---

## 1. Context — the system this fits into

Aurealis is a multi-brand app studio. The first brand using this pipeline is **ETHOS**, an iOS Christian-men subscription app. Read `01-meta-setup.md` and `02-account-strategy.md` first — they establish the brand voice and the 8-account architecture.

End-to-end pipeline:

```
┌─ agent-carousel repo (already built up to R2 upload) ──────────────┐
│  Carousel skill (Claude, runs 15×/day)                              │
│     ├─ reads cloud-agent/BRAND.md, TOPICS.md, CAROUSEL.md           │
│     ├─ reads cloud-agent/WINNERS.md (last week's winners, weekly    │
│     │   refreshed by the dashboard)                                 │
│     ├─ reads cloud-agent/accounts/<handle>.md (8 profiles)          │
│     └─ generates HTML/CSS slides + metadata.json                    │
│                          ↓                                          │
│  Branch + PR opened automatically                                   │
│                          ↓                                          │
│  GitHub Actions (render-carousels.yml)                              │
│     ├─ Playwright renders slides → JPEGs                            │
│     ├─ Uploads JPEGs + metadata.json to Cloudflare R2               │
│     └─ POSTs to dashboard webhook ─────────────────────┐            │
└────────────────────────────────────────────────────────┼────────────┘
                                                         │
┌─ aurealis-dashboard repo (THIS DOC) ───────────────────▼────────────┐
│  Next.js 16 App Router + Supabase + Clerk + Vercel                  │
│                                                                      │
│  Inbox          drafts pending validation                           │
│  Reviewer       preview slides + edit caption/hashtags +            │
│                 pick account + click PUBLISH NOW                    │
│  Accounts       8 cards, per-account history + analytics            │
│  Performance    leaderboard + patterns across all posts             │
│  System         token health, webhook log, errors                   │
│                                                                      │
│  Publish flow: synchronous server action, ~15-30s                   │
│     → 3-step Meta Graph API carousel publish                        │
│     → writes ig_media_id, permalink to DB                           │
│     → commits carousels/<slug>/published.json to agent-carousel     │
│                                                                      │
│  Vercel Cron: insights.ts  (hourly during 7d window)                │
│  Vercel Cron: winners.ts   (Mondays 06:00 UTC →                     │
│                              commits cloud-agent/WINNERS.md)        │
│  Vercel Cron: token-check  (daily 03:00 UTC → email alerts)         │
└──────────────────────────────────────────────────────────────────────┘
```

### Why two repos

- **`agent-carousel`**: content + creative artifacts + the generation pipeline. Generation history is version-controlled.
- **`aurealis-dashboard`**: operational tooling. Consumer software with auth + DB + uptime.

Cross-repo communication:
- Render workflow → dashboard webhook (one-way, forward).
- Dashboard → `agent-carousel` via GitHub API (commits `published.json` after publish; commits `WINNERS.md` weekly; commits `accounts/<handle>.md` when an account profile is edited).

---

## 2. Goals

**Primary goal**: be the single operating surface for human-in-the-loop carousel publishing. The reviewer opens the dashboard, sees the day's drafts, validates each one, hits publish.

**Specific goals**:

1. **Review velocity**: 15 drafts/day should take ≤ 30 min of human time to triage + publish.
2. **Zero misfires**: every publish requires explicit human click. No background autoposting.
3. **Closed loop**: weekly automatic update of `WINNERS.md` based on actual performance → next week's drafts measurably better.
4. **System legibility**: you can answer "is the pipeline healthy?" in under 30 seconds — token status, last successful publish per account, error count.
5. **Account profile single source of truth**: edit a bio or link in the dashboard, it commits to `cloud-agent/accounts/<handle>.md` so the skill can read it next generation.

### Non-goals (explicit)

See §0. Also:
- **Content creation/editing inside the dashboard.** The slides are HTML/CSS in `agent-carousel`. The dashboard edits caption and hashtags only.
- **Multi-tenant SaaS.** Internal Aurealis tooling only.
- **Mobile native app.** Mobile web is enough.

---

## 3. Stack

| Layer | Choice | Version | Why |
|---|---|---|---|
| Framework | Next.js | 16.x App Router | Vercel-native, server components, route handlers for API + cron |
| Runtime | Fluid Compute on Vercel (default) | — | 300s function timeout (the publish action might take 30s), Node 24 LTS |
| Language | TypeScript | 5.x strict | Shared types across UI, API, cron |
| Database | Supabase (Postgres) | latest | Vercel Marketplace integration |
| Auth | Clerk | latest | Vercel Marketplace; 2-email allowlist; GitHub/Google OAuth |
| Image store | Cloudflare R2 | — | Existing; public bucket; Meta pulls from public URLs |
| Styling | Tailwind CSS + shadcn/ui | latest | Fast, opinionated |
| Forms / validation | React Hook Form + Zod | latest | Shared Zod schemas client + API |
| Email (alerting) | Resend (Vercel Marketplace) | latest | Token expiry warnings, publish failures, weekly digest |
| Meta API client | Plain `fetch` against Graph API v23.0 | — | API is small; no SDK needed |
| GitHub API | Octokit | latest | Writing back `published.json`, `WINNERS.md`, account profile edits |

---

## 4. Data model

Full DDL. 7 tables. Enable RLS on every table.

```sql
-- ============================================================================
-- ACCOUNTS — the 8 ETHOS sub-niches (kept simple for MVP)
-- ============================================================================
create table accounts (
  id                  uuid primary key default gen_random_uuid(),
  handle              text unique not null,           -- '@ethos.fight'
  display_name        text not null,
  brand               text not null,                  -- 'ethos'
  niche               text not null,                  -- 'fight'
  primary_pillar      text not null,                  -- 'Scripture Applied'|'The Work'|'Real Talk'|'The Vision'
  themes              int[] not null,                 -- referencing 10 BRAND.md themes
  colorway            text not null,                  -- 'dark'|'cream'|'mono'|'bw'|'warm'|...
  bio                 text,
  link_short_url      text,                           -- 'https://link.theethos.app/fight'
  link_destination    text,                           -- final URL
  ig_user_id          text unique,                    -- Meta's 17-digit IG ID
  fb_page_id          text,                           -- Meta's FB Page ID
  profile_pic_url     text,
  paused              boolean not null default false, -- if true, blocks publish to this account
  paused_reason       text,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);
create index accounts_brand_idx on accounts (brand);

-- ============================================================================
-- DRAFTS — one row per generated carousel; ingested via render webhook
-- ============================================================================
create type draft_state as enum (
  'pending',     -- in inbox, awaiting reviewer
  'published',   -- successfully posted to an account
  'skipped'      -- reviewer explicitly chose not to post
);

create table drafts (
  id                  uuid primary key default gen_random_uuid(),
  slug                text unique not null,           -- '2026-05-24-the-man-you-are-at-2-am'
  brand               text not null,
  title               text not null,
  caption             text not null,                  -- AI-generated IG caption
  hashtags            text[] not null,
  pillar              text not null,
  themes              int[] not null,
  title_shape         text,                           -- 'identity_in_action'|'numbered_list'|...
  archetype           text,                           -- 'listicle'|'mistakes_list'|...
  hook_form           text,                           -- 'fragment'|'question'|'declarative'|'command'|'cultural'
  slide_count         int not null,
  slide_image_urls    text[] not null,                -- R2 public JPEG URLs in order
  cover_image_url     text not null,
  metadata_url        text not null,                  -- R2 URL to metadata.json
  content_hash        text not null,                  -- sha256 over normalized text + slide image phashes
  source_pr_url       text,                           -- agent-carousel PR
  source_commit       text,
  state               draft_state not null default 'pending',
  state_reason        text,                           -- for 'skipped'
  ingested_at         timestamptz not null default now(),
  state_changed_at    timestamptz
);
create unique index drafts_content_hash_idx on drafts (content_hash);
create index drafts_state_idx on drafts (state, ingested_at desc);
create index drafts_brand_idx on drafts (brand);

-- ============================================================================
-- PUBLISHES — one row per publish attempt
-- ============================================================================
create table publishes (
  id                  uuid primary key default gen_random_uuid(),
  draft_id            uuid not null references drafts(id),
  account_id          uuid not null references accounts(id),
  attempted_at        timestamptz not null default now(),
  succeeded           boolean not null default false,
  ig_media_id         text,                           -- '17848...'
  ig_permalink        text,                           -- 'https://instagram.com/p/...'
  caption_as_posted   text not null,                  -- the final caption (with reviewer edits)
  hashtags_as_posted  text[] not null,                -- the final hashtags
  duration_ms         int,
  error_code          text,
  error_message       text,
  meta_response       jsonb,                          -- raw response for debugging
  published_by        text not null                   -- clerk user id
);
create index publishes_account_time_idx on publishes (account_id, attempted_at desc);
create index publishes_draft_idx on publishes (draft_id);
create unique index publishes_media_idx on publishes (ig_media_id) where ig_media_id is not null;

-- ============================================================================
-- INSIGHTS — time-series; sampled hourly for 7 days post-publish
-- ============================================================================
create table insights (
  id                  bigserial primary key,
  publish_id          uuid not null references publishes(id) on delete cascade,
  fetched_at          timestamptz not null default now(),
  age_hours           int not null,                   -- hours since publish
  reach               int,
  impressions         int,
  saves               int,
  shares              int,
  comments            int,
  likes               int,
  profile_visits      int,
  follows_from_post   int,
  link_clicks         int,
  raw                 jsonb
);
create index insights_publish_age_idx on insights (publish_id, age_hours);

-- ============================================================================
-- TOKEN HEALTH — periodic check snapshots
-- ============================================================================
create table token_health (
  id                  bigserial primary key,
  checked_at          timestamptz not null default now(),
  expires_at          timestamptz,                    -- null = never (System User token)
  is_valid            boolean not null,
  scopes              text[],
  app_id              text
);

-- ============================================================================
-- WEBHOOK EVENTS — log of incoming Meta + render webhooks
-- ============================================================================
create table webhook_events (
  id                  bigserial primary key,
  received_at         timestamptz not null default now(),
  source              text not null,                  -- 'meta_instagram'|'render'
  kind                text not null,
  payload             jsonb not null,
  signature_valid     boolean,
  processed_at        timestamptz,
  processing_error    text
);
create index webhook_events_recent_idx on webhook_events (received_at desc);

-- ============================================================================
-- WINNERS SNAPSHOTS — precomputed weekly, rendered to WINNERS.md
-- ============================================================================
create table winners_snapshots (
  id                  uuid primary key default gen_random_uuid(),
  computed_at         timestamptz not null default now(),
  window_days         int not null,                   -- typically 30
  top_publishes       uuid[] not null,                -- ordered by composite score
  scores              jsonb not null,                 -- {publish_id: score}
  patterns            jsonb not null,                 -- over-represented dimensions
  markdown            text not null,                  -- the rendered WINNERS.md content
  committed_at        timestamptz,
  commit_sha          text
);

-- ============================================================================
-- AUDIT LOG — every human-triggered mutation
-- ============================================================================
create table audit_log (
  id                  bigserial primary key,
  at                  timestamptz not null default now(),
  actor               text not null,                  -- clerk user id
  action              text not null,                  -- 'draft.publish'|'draft.skip'|'account.edit'|...
  target_table        text not null,
  target_id           text not null,
  before              jsonb,
  after               jsonb
);
create index audit_log_target_idx on audit_log (target_table, target_id, at desc);
```

### Notes on the schema

- **No `assignments` table.** A draft is published directly to an account via a `publishes` row. There's no intermediate "scheduled" state.
- **`drafts.state`** is the inbox filter: `pending` shows up in the inbox; `published` and `skipped` are filtered out (still browsable in account history / draft archive).
- **`drafts.content_hash`** still enforces uniqueness at insert time so duplicate ingestions are rejected. Network-wide same-day duplicate rules are *soft warnings* in the reviewer UI, not hard constraints.
- **`publishes.caption_as_posted` + `hashtags_as_posted`** snapshot the actual posted text. If the reviewer edited the caption, this is what went live. Important for analytics — we score what was actually published, not what the AI originally wrote.
- **`audit_log`** captures every human action. Cheap insurance.

---

## 5. API surface

### Webhooks (no auth, HMAC verified)

| Method | Path | Source | Purpose |
|---|---|---|---|
| POST | `/api/webhooks/render` | `agent-carousel` render workflow | Ingest a new draft after R2 upload |
| POST | `/api/webhooks/meta` | Meta IG webhook | Receive post-publish notifications (content review actions, etc.) |

### Vercel Cron routes (authenticated via `CRON_SECRET`)

| Method | Path | Schedule | Purpose |
|---|---|---|---|
| POST | `/api/cron/insights` | `0 * * * *` | Refresh IG Insights for posts in their 7d window |
| POST | `/api/cron/winners` | `0 6 * * 1` | Compute winners, commit `WINNERS.md` to `agent-carousel` |
| POST | `/api/cron/token-check` | `0 3 * * *` | Verify Meta System User token; email on degradation |

### Server Actions (authenticated via Clerk)

Defined in `app/actions/`. The dashboard's whole mutation surface:

- `publishDraft(draftId, accountId, { captionOverride?, hashtagsOverride? })` — **the key action**. Synchronous. Performs the 3-step Meta carousel publish, writes a `publishes` row, sets `drafts.state = 'published'`, commits `published.json` to `agent-carousel`. Returns `{ ig_media_id, permalink }` or throws.
- `skipDraft(draftId, reason)` — sets `drafts.state = 'skipped'`.
- `editAccount(accountId, fields)` — updates DB and commits a change to `cloud-agent/accounts/<handle>.md` via Octokit.
- `pauseAccount(accountId, reason)` / `unpauseAccount(accountId)`.

### REST (authenticated, read-only)

- `GET /api/drafts?state=pending`
- `GET /api/accounts/:handle/timeline?days=30`
- `GET /api/performance/leaderboard?window=30d`
- `GET /api/system/health`

---

## 6. Pages — UI structure

App Router structure (`app/`):

```
app/
├─ (auth)/
│  └─ sign-in/[[...sign-in]]/page.tsx       Clerk
├─ (dashboard)/
│  ├─ layout.tsx                            Top nav, user menu
│  ├─ page.tsx                              "Today" overview (default landing)
│  ├─ inbox/page.tsx                        Drafts pending validation
│  ├─ inbox/[draftId]/page.tsx              Single draft reviewer (with PUBLISH NOW)
│  ├─ accounts/page.tsx                     8-card grid
│  ├─ accounts/[handle]/page.tsx            Single account drill-in
│  ├─ accounts/[handle]/edit/page.tsx       Edit account profile (commits to repo)
│  ├─ performance/page.tsx                  Leaderboard + patterns
│  ├─ performance/post/[publishId]/page.tsx Single post deep-dive
│  └─ system/page.tsx                       Token health, webhook log, errors
└─ api/                                     (routes from §5)
```

### Page: `/` ("Today")

The default landing. Answers "what's going on right now":

- **Inbox count**: pending drafts (link → `/inbox`)
- **Today's publishes**: count + 4 most recent thumbnails
- **8 account chips**: handle, last published timestamp ("2h ago"), paused state if any
- **Health flags**: token status, any unprocessed webhooks, last cron success times
- **Top 3 posts last 7d** (by composite score) — quick reminder of what's resonating

### Page: `/inbox`

Vertical list of pending draft cards, default sort by `ingested_at desc`. Each card:

- Cover slide image thumbnail (left, ~120px)
- Title + caption truncated
- Pillar / theme / shape badges
- Ingested time ago
- **Two actions**: "Review →" (opens reviewer) and "Skip" (modal asks for reason)

No batch operations. One draft at a time.

### Page: `/inbox/[draftId]` — the reviewer

The most important page. This is where every publish happens.

Layout: 2 columns.

**Left column — slide preview**:
- All N slides displayed at native aspect (1080×1350), scrollable vertically or in a horizontal carousel toggle.
- Click → modal zoom.
- Each slide shows its index (1/6, 2/6, ...).

**Right column — validation + publish**:

1. **Metadata header (read-only)**: title, pillar, themes, title_shape, archetype, hook_form, slide_count, ingested_at, source PR link.

2. **Caption editor**: large textarea, pre-filled with `draft.caption`. Character counter (2200 max). On focus, shows soft hints:
   - Has the app been named before the CTA slide?
   - Caption looks like another recent caption? (loose similarity check)
   No blocking — just visual flags.

3. **Hashtag editor**: chip-style. Pre-filled with `draft.hashtags`. Add/remove inline. Shows **soft warning** if this exact set has been used in the last 7 days across the network.

4. **Account picker**: 8 buttons, each showing handle + last-published-ago + warning chips:
   - 🟡 if last publish to this account was < 4 hours ago
   - 🔴 if this account is paused
   - The picker doesn't block — just informs.

5. **"PUBLISH NOW" button**: large, prominent. Disabled until an account is picked and caption is non-empty. On click:
   - Show modal: "Publishing to @ethos.fight — this takes ~15-30 seconds"
   - Spinner with current step ("Creating slide containers... 3/6")
   - On success: confirmation modal with permalink + "View post on Instagram" + "Back to inbox"
   - On failure: error modal with the Meta error message + "Retry" + "Mark as skipped"

6. **Skip action**: secondary button. Modal asks for reason ("off-brand", "duplicate of recent", "low quality", custom).

Design constraint: the publish action is intentionally synchronous + modal-blocking. The reviewer should feel they're doing one thing at a time. If the publish takes 45s and they navigate away, the action still completes — but the UX nudges them to wait so they see the outcome.

### Page: `/accounts`

8 cards in a 2×4 grid. Each card:

- Profile pic, handle, display name, niche tagline
- **Last published**: thumbnail + timestamp ("2 hours ago — 'The man you are at 2 AM'")
- **Posted in last 24h** count
- **7d composite score sparkline**
- **Paused state** if any
- Click → `/accounts/[handle]`

### Page: `/accounts/[handle]`

Per-account deep dive:

- **Header**: handle, profile pic, bio (read-only here; edit on a separate page), link short URL → final URL
- **History**: all publishes, paginated. Each row: thumb, caption truncated, posted time, reach, saves, follows, composite score (when available). Click → `/performance/post/[publishId]`.
- **Performance summary**: 30d composite score trend, top hashtag groups by per-post engagement, best-performing pillars for this account.
- **Configuration**: colorway, themes, bio, link. "Edit" → `/accounts/[handle]/edit`.
- **Health**: last successful publish, last failed publish (with error), Meta token assertion for this account's connection.

### Page: `/accounts/[handle]/edit`

Form to edit account profile. On save:
- Updates `accounts` row
- Commits a change to `agent-carousel/cloud-agent/accounts/<handle>.md` via Octokit (so the skill reads it next generation)
- Audit log entry

Show a banner: "Saving will commit to agent-carousel as user@email — change appears in next skill generation."

### Page: `/performance`

- **Leaderboard**: top N publishes by composite score in window (7d / 30d / 90d). Filter by account / pillar / shape / hook form.
- **Pattern view**: bar charts showing over/under-representation in winners by pillar, shape, hook form, slide count. The same patterns get rendered to `WINNERS.md` weekly.
- Click any row → `/performance/post/[publishId]`.

### Page: `/performance/post/[publishId]`

Single post deep-dive:
- All N slides as images
- Caption + hashtags as posted (with diff vs original draft if reviewer edited)
- Account context
- Maturation chart: reach / saves / shares / follows-from-post over the 7d insights window
- Composite score at each measurement age
- Link to IG permalink

### Page: `/system`

- **Token health**: System User token expires_at, scopes, last check. "Re-check now" button.
- **Webhook events**: last 50, filterable by source.
- **Cron health**: last run + outcome of each of the 3 cron routes.
- **Errors**: failed publishes from last 7 days, with retry option (re-runs `publishDraft` with same inputs).
- **Audit log**: last 200 human actions, who did what when.

---

## 7. The publish flow — `publishDraft` server action

The heart of the dashboard. Pseudocode:

```
publishDraft(draftId, accountId, { captionOverride?, hashtagsOverride? }):
  1. Authorize: verify caller has Clerk session
  2. Load draft + account from DB
  3. Pre-flight (soft warnings already shown in UI; hard checks here):
     a. draft.state == 'pending'  (refuse re-publish)
     b. account.paused == false
     c. account.ig_user_id present
     d. all slide_image_urls reachable (HEAD request)
  4. Render final caption = captionOverride ?? draft.caption
     Render final hashtags = hashtagsOverride ?? draft.hashtags
     Concatenate caption + ("\n\n" + hashtags joined by spaces with #)
  5. Begin synchronous Meta API publish:
     a. For each slide_image_url:
        POST {ig_user_id}/media with image_url + is_carousel_item=true
        → get container_id
        Poll GET {container_id}?fields=status_code every 2s up to 30s
        Until status_code == 'FINISHED'
     b. POST {ig_user_id}/media with
        media_type=CAROUSEL, children=<ids>, caption=<final>
        → get parent_container_id
        Poll until FINISHED
     c. POST {ig_user_id}/media_publish with creation_id=<parent_container_id>
        → get ig_media_id
  6. INSERT publishes row (succeeded=true, ig_media_id, ig_permalink, ...)
  7. UPDATE drafts SET state='published', state_changed_at=now()
  8. Commit carousels/<slug>/published.json to agent-carousel via Octokit
  9. INSERT audit_log row
  10. Return { ig_media_id, permalink }

On any failure in step 5:
  - INSERT publishes row with succeeded=false, error_code, error_message
  - drafts.state stays 'pending' (reviewer can retry or skip)
  - throw — UI shows error modal
```

Timing budget: most carousels publish in 8-15s. Polling timeout cap is 60s total. Vercel Function timeout is 300s — plenty of headroom.

---

## 8. Cron jobs — exact behaviors

### `/api/cron/insights` (hourly)

```
1. SELECT publishes p
   WHERE p.succeeded = true
   AND age(p.attempted_at) < interval '7 days'
   AND NOT EXISTS (
     SELECT 1 FROM insights i
     WHERE i.publish_id = p.id
     AND age(i.fetched_at) < interval '50 minutes'
   )
2. For each, GET /{ig_media_id}/insights?metric=reach,impressions,saves,
   shares,comments,likes,profile_visits,follows_from_post,link_clicks
3. INSERT insights row with computed age_hours
4. Backoff on rate limit
```

### `/api/cron/winners` (Monday 06:00 UTC)

```
1. Window: last 30 days, latest insights snapshot per publish
2. Composite score:
   score = (saves/reach)*3 + (shares/reach)*2 + (follows/reach)*8
         + (comments/reach)*1 + (link_clicks/reach)*4
3. Identify top quintile → winner=true
4. Extract patterns (over-representation vs baseline) per dimension:
   pillar, title_shape, hook_form, slide_count, account, posting hour bucket
5. (Optional v2) text n-gram analysis on winning hooks — defer to single LLM
   call: "Here are 30 winning hooks. What pattern do they share?"
6. Render markdown from a template (see §10)
7. INSERT winners_snapshots row
8. Commit cloud-agent/WINNERS.md to agent-carousel via Octokit (direct push to main)
9. Email digest of top 10 + patterns to allowlist
```

### `/api/cron/token-check` (daily 03:00 UTC)

```
1. GET https://graph.facebook.com/debug_token?
     input_token=<TOKEN>&access_token=<APP_ID>|<APP_SECRET>
2. INSERT token_health row
3. If is_valid=false OR (expires_at IS NOT NULL AND
   expires_at < now()+interval '30 days'):
   send email to allowlist
```

---

## 9. Webhook contract — `agent-carousel` → dashboard

After R2 upload completes, the render workflow makes one POST.

### Request

```http
POST https://dashboard.aurealis.app/api/webhooks/render
Content-Type: application/json
X-Aurealis-Signature: sha256=<hex>
X-Aurealis-Timestamp: <unix>

{
  "slug": "2026-05-24-the-man-you-are-at-2-am",
  "brand": "ethos",
  "metadata": { ...metadata.json contents... },
  "slide_image_urls": [
    "https://r2.aurealis.app/carousels/2026-05-24-.../slide-01.jpg",
    ...
  ],
  "metadata_url": "https://r2.aurealis.app/carousels/2026-05-24-.../metadata.json",
  "source_pr_url": "https://github.com/aurealis-info/agent-carousel/pull/42",
  "source_commit": "4d3b40b..."
}
```

### Signature

`X-Aurealis-Signature` is `sha256` HMAC of `{timestamp}.{body}` using shared secret `RENDER_WEBHOOK_SECRET`. Reject if timestamp older than 5 min or signature doesn't match.

### Dashboard behavior

1. Verify signature + timestamp freshness
2. Insert `webhook_events` row
3. Compute `content_hash` (sha256 over normalized caption + perceptual hashes of all slides)
4. Reject if `content_hash` exists (return 409)
5. Insert `drafts` row with `state='pending'`
6. Return 200 with `{ "draft_id": "..." }`

### Render workflow changes (in `agent-carousel`)

Add to `render-carousels.yml`:

```yaml
- name: Notify dashboard
  if: success()
  env:
    DASHBOARD_URL: ${{ secrets.DASHBOARD_WEBHOOK_URL }}
    SHARED_SECRET: ${{ secrets.RENDER_WEBHOOK_SECRET }}
  run: node scripts/notify-dashboard.js
```

`scripts/notify-dashboard.js` reads carousel metadata + R2 URLs and POSTs them. Retry 3× with backoff; if all fail, fail the job (R2 has the files; ingestion can be retriggered manually with `--folder <slug>`).

---

## 10. Writing back to `agent-carousel`

The dashboard commits in three cases via Octokit + a fine-grained PAT or GitHub App installation token (env: `AGENT_CAROUSEL_GITHUB_TOKEN`):

| Trigger | Path | Mode |
|---|---|---|
| `publishDraft` success | `carousels/<slug>/published.json` | Direct push to main |
| `winners` cron weekly | `cloud-agent/WINNERS.md` | Direct push to main |
| `editAccount` server action | `cloud-agent/accounts/<handle>.md` | Direct push to main |

Commit author: `Aurealis Dashboard <dashboard@aurealis.app>`.

Commit messages:
- `ops: publish <slug> to <handle> (ig_media_id=<id>)`
- `auto: refresh WINNERS.md (window=30d, top10)`
- `config: update accounts/<handle>.md via dashboard (user=<email>)`

### `published.json` schema

```json
{
  "carousel_slug": "2026-05-24-the-man-you-are-at-2-am",
  "account_handle": "@ethos.fight",
  "ig_media_id": "17848...",
  "ig_permalink": "https://www.instagram.com/p/...",
  "published_at": "2026-05-24T18:32:15Z",
  "caption_as_posted": "...",
  "hashtags_as_posted": ["...", "..."],
  "published_by": "user@email.com"
}
```

### `WINNERS.md` template

See `02-account-strategy.md` §"The WINNERS.md contract" for the full structure. Rendered by the winners cron from a template + the snapshot data.

---

## 11. Meta API integration details

Read `01-meta-setup.md` for prerequisites (System User token, App Review, etc.).

Base: `https://graph.facebook.com/v23.0`

| Purpose | Method + Path |
|---|---|
| Create child container | `POST /{ig-user-id}/media` (image_url, is_carousel_item=true) |
| Create parent CAROUSEL container | `POST /{ig-user-id}/media` (media_type=CAROUSEL, children, caption) |
| Poll container status | `GET /{container-id}?fields=status_code` |
| Publish | `POST /{ig-user-id}/media_publish` (creation_id) |
| Insights | `GET /{ig-media-id}/insights?metric=...` |
| Publishing limit | `GET /{ig-user-id}/content_publishing_limit` |
| Token debug | `GET /debug_token?input_token=...&access_token=APP_ID|APP_SECRET` |

### Polling

Container status: `IN_PROGRESS` | `FINISHED` | `ERROR` | `EXPIRED`. Poll every 2s, max 30s per container. Carousels (no video) almost always `FINISHED` by first or second poll.

### Error categories

| Error | Strategy |
|---|---|
| Image URL not reachable | Fail fast, show error modal, ask reviewer to verify R2 or re-render |
| Container `ERROR` status | Retry once with fresh container; if still errors, surface to reviewer |
| 429 rate limit | Wait per `Retry-After`, retry once, then fail with explicit message |
| 5xx | Retry with exponential backoff (1s, 4s, 16s), then fail |
| Token invalid | Hard fail. Alert. Block all further publishes until token refreshed. |
| Permission missing | Fail with explicit "this account isn't connected — see /system" message |

---

## 12. Auth — Clerk setup

Install via Vercel Marketplace → auto-provisions `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`. Enable GitHub + Google OAuth.

### Allowlist

In Clerk Dashboard → Restrictions:

```
allowlist:
  - <your-email>
  - <collaborator-email>
```

No role distinction for MVP — both users can do everything.

### Middleware

```ts
// middleware.ts
import { clerkMiddleware } from '@clerk/nextjs/server';
export default clerkMiddleware();
export const config = {
  matcher: ['/((?!_next|.*\\..*|api/webhooks/|api/cron/).*)']
};
```

Public surfaces (excluded above): webhooks (HMAC), cron routes (CRON_SECRET), static assets.

---

## 13. Repo layout

```
aurealis-dashboard/
├─ app/
│  ├─ (auth)/
│  ├─ (dashboard)/
│  └─ api/
├─ components/                shadcn/ui + custom
├─ lib/
│  ├─ db.ts                   Supabase client (server + browser)
│  ├─ meta/
│  │  ├─ client.ts            Graph API fetch wrapper
│  │  ├─ publish.ts           3-step carousel publish
│  │  ├─ insights.ts          fetch + parse insights
│  │  └─ webhook.ts           verify Meta webhook signature
│  ├─ github/
│  │  └─ commit.ts            Octokit helpers
│  ├─ scoring/
│  │  ├─ composite.ts         winner score
│  │  └─ patterns.ts          pattern extraction
│  ├─ uniqueness/
│  │  └─ checks.ts            content_hash + hashtag soft warnings
│  └─ env.ts                  zod-validated env vars
├─ supabase/
│  ├─ migrations/             SQL migrations
│  └─ seed.sql                seed 8 accounts (idempotent)
├─ scripts/
│  └─ seed-accounts.ts        re-runnable account seed
├─ tests/
│  ├─ scoring.test.ts
│  └─ uniqueness.test.ts
├─ vercel.ts                  cron schedules
├─ next.config.ts
├─ tsconfig.json
├─ package.json
├─ .env.example
└─ README.md
```

### `vercel.ts`

```ts
import { type VercelConfig } from '@vercel/config/v1';

export const config: VercelConfig = {
  framework: 'nextjs',
  crons: [
    { path: '/api/cron/insights',    schedule: '0 * * * *' },
    { path: '/api/cron/winners',     schedule: '0 6 * * 1' },
    { path: '/api/cron/token-check', schedule: '0 3 * * *' }
  ]
};
```

---

## 14. Environment variables

```
# Database
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=          server-only

# Auth
CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=

# Meta Graph API
META_APP_ID=
META_APP_SECRET=                    debug_token + webhook verification only
META_SYSTEM_USER_TOKEN=             non-expiring publisher token
META_API_VERSION=v23.0
META_WEBHOOK_VERIFY_TOKEN=

# R2 (read-only for the dashboard)
R2_PUBLIC_BASE_URL=                 https://r2.aurealis.app

# GitHub (writeback to agent-carousel)
GITHUB_APP_INSTALLATION_TOKEN=
AGENT_CAROUSEL_REPO=aurealis-info/agent-carousel
AGENT_CAROUSEL_BRANCH=main

# Webhook secrets
RENDER_WEBHOOK_SECRET=
CRON_SECRET=

# Email (Resend)
RESEND_API_KEY=
ALERT_TO_EMAILS=                    comma-separated
```

---

## 15. Setup checklist (cold start, ~5 days)

### Day 1 — provisioning
- [ ] Create GitHub repo `aurealis-info/aurealis-dashboard`
- [ ] `npx create-next-app@latest aurealis-dashboard --typescript --tailwind --app`
- [ ] Push initial commit, create Vercel project, link to repo
- [ ] Install Vercel Marketplace integrations: Supabase, Clerk, Resend
- [ ] Run Supabase migrations in `supabase/migrations/`
- [ ] Configure Clerk: enable GitHub OAuth, set 2-email allowlist
- [ ] Set Meta/R2/GitHub/webhook env vars in Vercel

### Day 2 — ingest + publish core
- [ ] `lib/meta/client.ts` (fetch wrapper)
- [ ] `lib/meta/publish.ts` (3-step + polling)
- [ ] `app/api/webhooks/render/route.ts` (HMAC verify, insert draft)
- [ ] `app/actions/publishDraft.ts`
- [ ] Add `scripts/notify-dashboard.js` to agent-carousel
- [ ] Add render webhook step to `render-carousels.yml`
- [ ] **Smoke test**: trigger fake render webhook locally → draft inserts → call publishDraft via curl → carousel posts to a test IG account

### Day 3 — inbox + reviewer UI
- [ ] `app/(dashboard)/layout.tsx` + nav
- [ ] `app/(dashboard)/inbox/page.tsx` + draft card
- [ ] `app/(dashboard)/inbox/[draftId]/page.tsx` reviewer (2 columns, caption editor, hashtag editor, account picker, PUBLISH NOW button + modal)
- [ ] Wire publish button → `publishDraft` server action + status modal
- [ ] **End-to-end test**: real generated draft → review → edit caption → pick account → publish → confirm on IG

### Day 4 — accounts + performance
- [ ] `app/(dashboard)/accounts/page.tsx` (8 cards)
- [ ] `app/(dashboard)/accounts/[handle]/page.tsx`
- [ ] `app/(dashboard)/accounts/[handle]/edit/page.tsx` + Octokit commit
- [ ] `app/api/cron/insights/route.ts`
- [ ] `app/(dashboard)/performance/page.tsx` + `post/[publishId]/page.tsx`
- [ ] `lib/scoring/composite.ts`

### Day 5 — winners loop + system + polish
- [ ] `lib/scoring/patterns.ts`
- [ ] `app/api/cron/winners/route.ts` → commits `WINNERS.md` to agent-carousel
- [ ] Add `cloud-agent/INSTRUCTIONS.md` line telling the skill to read `WINNERS.md`
- [ ] `app/api/cron/token-check/route.ts` + Resend email on degradation
- [ ] `app/(dashboard)/system/page.tsx`
- [ ] `app/(dashboard)/page.tsx` ("Today" overview)
- [ ] Audit log on every server action

---

## 16. Security considerations

- **Service role key is server-only.** Never imported in client components.
- **RLS on all tables** from day one. Service role bypasses; authenticated user required for everything else.
- **HMAC verify every webhook**. 5-min timestamp replay protection.
- **Cron routes** require `CRON_SECRET` header (Vercel Cron sends automatically).
- **GitHub token** fine-grained, scoped to `agent-carousel` repo, contents write only.
- **Meta System User token** server-only. Never to the browser.
- **Audit log** captures `published_by` for every publish — this is the audit trail for an irreversible action.

---

## 17. Future considerations (deferred, not now)

These are the scope cuts made for MVP. Capture them so we don't lose the thinking when we revisit:

- **Auto-scheduling**: posting time windows per account, jittered times within a window, queued publish runs via cron. Implement when the reviewer is tired of manually spacing posts across the day.
- **Warming state machine**: per-account ramp from new → normal posting cadence over 4 weeks. Implement after launching 2+ brand-new accounts and seeing the manual warming feel painful.
- **Auto-routing / suggested account**: model that predicts the best account for a draft based on past performance. Implement after 30+ days of data shows clear per-account preferences.
- **Bulk approve**: select N drafts, assign each to suggested account, publish staggered. Implement if the reviewer starts wanting to spend < 15 min/day on the dashboard.
- **Slot windows + drag-to-reschedule schedule page**: the calendar view from the previous draft of this doc. Implement alongside auto-scheduling.
- **A/B experimentation framework**: deliberately route similar content to two accounts to isolate a single variable. Phase 4.
- **Hashtag pool management UI**: per-account pools as first-class objects with usage analytics. Currently editable as inline JSON via the account edit page.
- **CTA bank rotation**: per-account templates that get sampled instead of using the AI-generated one verbatim. Implement when CTA fatigue shows up in analytics.

The recommended trigger for revisiting: **the reviewer says "I'm spending too long on the dashboard" or "I keep flooding @ethos.X."** That's the signal to add the next layer of automation.

---

## 18. Glossary

- **Draft** — a generated, rendered, R2-uploaded carousel awaiting human validation.
- **Publish** — a single Meta API publish attempt; one row in `publishes`.
- **Insight** — a time-series snapshot of metrics for a publish.
- **Winner** — a publish in the top quintile by composite score in the rolling window.
- **Content hash** — sha256 over normalized caption + slide perceptual hashes; the uniqueness key.
- **System User token** — Meta's non-expiring server-side credential for publishing.
- **Composite score** — weighted, reach-normalized engagement metric used to rank publishes.
- **Reviewer** — the human (you or your collaborator) who validates and publishes drafts.

---

## 19. Reading order for the implementer

1. This doc (architecture) — §0 first to internalize the MVP scope cut
2. `01-meta-setup.md` (Meta side — even if someone else does the clicks, the implementer needs to know the credentials and the App Review status)
3. `02-account-strategy.md` (positioning + the 8 accounts + the feedback loop — the *why*)
4. `agent-carousel/cloud-agent/BRAND.md`, `TOPICS.md`, `CAROUSEL.md` (brand voice — what the dashboard operates on)
5. `agent-carousel/scripts/render.js` (the current render pipeline — to understand the webhook contract from the other side)
6. Build per the day-by-day checklist in §15.
