# Account Strategy — 8 ETHOS Sub-Niches, Routing, and the Performance Feedback Loop

Companion to `01-meta-setup.md`. This doc covers the **what** and **why** of the account architecture, not the Meta API mechanics.

---

## The model

15 unique carousels generated per day → distributed across **8 ETHOS Instagram accounts** → **no carousel ever posted twice**. Every account is promoting the same app. The variance is in **angle, audience, and visual signature** — not in the content itself.

This is fundamentally different from a "cross-poster" — it's a multi-pronged top-of-funnel. Each account farms a different slice of the Christian-men audience, runs its own A/B test, and feeds signal back into a shared generation skill.

**The strategic asset isn't the dashboard or the publisher. It's the closed loop:** posts → analytics → winning patterns → updated guidelines → next-day's posts. Six months of this beats six years of gut-driven content.

---

## Why 8 accounts (the math)

At 2 posts/account/day (the behavioral soft limit — Meta's API hard limit is 100/24h but it doesn't matter):

| Accounts | Daily slots | Posture |
|---|---|---|
| 6 | 12 | Tight — bad days break the queue |
| **8** | **16** | **Healthy, 1 slot of slack — recommended** |
| 10 | 20 | Generous, lets you reject 25% of drafts |
| 12+ | 24+ | Too many for early differentiation |

**Launch with 8.** Add #9 and #10 once you know which angles convert.

---

## The 8 sub-niches

Each account maps to a primary **pillar** (from `cloud-agent/TOPICS.md`) and 1–3 of the 10 **themes** (from `cloud-agent/BRAND.md`). All 8 share ETHOS voice — older brother across the table at 10 PM with coffee. The differentiation is *what slice of his life this account speaks to first.*

| # | Handle (proposed) | Primary pillar | Lead themes | Colorway | One-line positioning |
|---|---|---|---|---|---|
| 1 | `@theethos` | All 4, rotating | All 10 | Dark serif (current) | The flagship. Neither feral nor domesticated. The free man. |
| 2 | `@ethos.scripture` | Scripture Applied | 1 (self-rule), 2 (kill it) | Cream / classical serif | Scripture for the man trying to walk it, not just quote it. |
| 3 | `@ethos.discipline` | The Work | 3 (he works), 1 (self-rule) | Industrial mono | Get built. The 20s are for becoming the man people count on. |
| 4 | `@ethos.real` | Real Talk | 2 (kill it), 4 (same guy everywhere), 5 (hard on self) | Dark serif | Hard truths a brother would say. Conviction, never contempt. |
| 5 | `@ethos.brotherhood` | Real Talk | 7 (planted in real men), 4 | Earthy / warm | Two or three real men. Not a Discord. Not a podcast. |
| 6 | `@ethos.fight` | The Work + Scripture | 9 (fights the phone), 2 (kill it) | Stark B/W | His generation's war: porn, the scroll, the 2 AM tab. |
| 7 | `@ethos.becoming` | The Vision | 6 (leads), 8 (chases God not a wife), 10 (humble) | Warm cream / editorial | The man worth becoming. The man worth marrying. |
| 8 | `@ethos.daily` | Cross-pillar | All 10 (rotation) | Mixed, aesthetic-led | One read. One thought. Daily. Single-verse + quote formats. |

### Per-account profile template

Each account needs its own profile doc in `cloud-agent/accounts/<handle>.md` so the carousel skill can read it at generation time. Template:

```markdown
# @ethos.fight

## Audience slice
He has a porn problem. Or a scroll problem. He knows the verses. He's tried
the filters. He's tired. He wants out, not a sermon.

## Pillars (weighted)
- The Work (60%)
- Scripture Applied (30%)
- Real Talk (10%)
- The Vision (0%) — almost never; this account is about the war, not the vision

## Themes lead order
1. Theme 9 — fights the phone
2. Theme 2 — kills what's killing him
3. Theme 1 — self-rule
(Other themes: surface only if explicitly tied to the war.)

## Voice tilt (within ETHOS voice)
Even more direct. Shorter sentences. Less abstract. Concrete actions a man
takes tonight. The audience here is fighting — give him orders he can run with.

## Title shapes (weighted)
- Identity in action: 50%
- The mechanism: 30%
- Reframe / myth-buster: 20%
- Numbered list: rare (high-save but soft for this account)

## Colorway
Stark B/W. No gold accents. Wood-cut feel.

## Bio
The war you don't talk about.
2-minute reps for the man done with it.
DM "out" for the link ↓

## Link-in-bio
Routes to ethos app onboarding flow B (recovery-framed first session)

## Hashtag pools (rotate; never repeat the same set)
Pool A (faith): #christianmen, #faithoverfear, #manofgod, #soberlife, #freedom
Pool B (men): #brotherhood, #integrity, #disciplineequalsfreedom
Pool C (tactical): #habitstacking, #2ammethod, #thefight
(Pull 8–12 per post by sampling across pools.)

## Anti-patterns specific to this account
- No vision/aspirational carousels — wrong audience, wrong moment in his life.
- No "becoming the man worth marrying" framing — premature for this user.
- Never minimize the addiction or talk down to him.
```

Build all 8 of these. They become inputs to the generation pipeline; the dashboard renders previews of them as account cards.

---

## Content routing — how a generated carousel reaches an account

Three viable models, in the order you'll likely use them:

### Phase A — Reviewer-assigned (launch through ~week 8)

Generation creates 15 drafts/day with `pillar`, `theme`, `title_shape`, `archetype` metadata. Dashboard inbox lists all 15. Human reviewer reads each and assigns to an account.

**Why this first**: you don't know yet which account converts on which content type. Manual routing teaches you. Every assignment is a hypothesis ("I think this discipline-themed listicle works on `@ethos.discipline`"). The performance data is the test result.

### Phase B — Auto-suggest, human-confirm (week 8 → 24)

Dashboard shows top 2 suggested accounts per draft, based on past performance for matching `pillar × theme × shape`. Reviewer accepts or overrides. Speed up without losing control.

The suggestion engine is just a lookup:

```
score(draft, account) =
    avg_winner_score_over_last_30d(
      where account = account
      and pillar = draft.pillar
      and theme in draft.themes
    ) * historical_count_weight
```

### Phase C — Auto-route, human-veto (week 24+)

Dashboard auto-assigns, posts to a "scheduled" queue. Reviewer only intervenes for fliers or experiments. Eventually fully autonomous except for a daily 15-minute glance.

**Don't skip Phase A.** Auto-routing without human-graded data is just round-robin with extra steps.

---

## Anti-pattern rules — the 8-accounts-same-app discipline

Even with unique content, 8 accounts pointing at one app can still trip Meta's clustering detector. Rules:

1. **Same content_hash never posted twice across the network, ever.** Dashboard computes a stable hash of carousel text + slide image perceptual hashes. Refuses to schedule a duplicate, even across accounts and time.
2. **Same hashtag block never posted twice within a 7-day rolling window across the network.** Pools per account, sampled fresh per post.
3. **Don't cross-follow your own accounts in the first 90 days.** Meta cluster detection looks at follow graphs. After 90 days, light cross-follows from `@theethos` (the flagship) to 2–3 of the sub-niches is fine; do not have all 8 follow each other.
4. **Don't tag your own accounts in posts** for the first 90 days. Same reason.
5. **Vary link-in-bio destinations.** Use a redirector (e.g. short.io or your own `link.theethos.app`) with one short link per account. They can all land on the same app store page eventually — but the immediate URLs differ. This breaks the "all 8 link to the same exact URL" pattern.
6. **Stagger posting windows.** Don't have all 8 accounts post at exactly 9 AM ET. Each account gets its own slot windows (e.g. `@ethos.scripture` posts 6:30 AM ± 30 / 7 PM ± 30; `@ethos.fight` posts 11 PM ± 30 / 6 AM ± 30 — meet the user when his fight is happening).
7. **Different bios, different profile pics, different highlight covers.** No template-cloned profiles. The dashboard's "account positioning" page makes deviation visible.
8. **Account warming**: a new account that posts 2/day from day one is bot-shaped. Schedule below.
9. **Per-account CTA rotation.** Same `comment_trigger` ("comment 'seen'") across 8 accounts looks like a single bot. Each account gets a small bank of CTAs that vary the trigger word, the bridge phrasing, and the "what you'll get" promise.
10. **Never post the same carousel on the same calendar day across two accounts**, even after a rewrite. The dashboard enforces this with a "post-day uniqueness per content_hash root" check.

---

## The performance feedback loop (the moat)

This is the most important system in this whole architecture. Most social media operations run blind. You'll have a closed loop where this week's winners shape next week's drafts.

### The loop

```
Day 0       Generation creates carousel with metadata: pillar, themes,
            title_shape, archetype, slide_count, hook_form, cta_form,
            account_id (assigned via routing)

Day 0       Publish (publisher, jittered window)

Day 1-7     Analytics poller fetches IG Insights daily for each published
            media. Stored in Supabase analytics table:
            - reach, impressions, saves, shares, comments, likes
            - profile_visits, follows_from_post, link_clicks
            - sampled at +24h, +48h, +72h, +168h post-publish

Day 8       Composite "winner score" computed for each post (see below).
            Top quintile (top 20%) gets winner=true.

Day 8       Pattern extractor runs over last 30 days of winners:
            - which pillars over-represented?
            - which title shapes?
            - which hook forms (question / fragment / declarative / cultural)?
            - which slide counts (5 / 6 / 7)?
            - which account?
            - which posting time bucket?
            - any text n-grams over-represented in winning hooks?

Day 8       Writes cloud-agent/WINNERS.md — top 10 carousels of last 7d
            with extracted patterns. Auto-committed by analytics workflow.

Day 8+      Carousel skill reads WINNERS.md as input at generation time.
            INSTRUCTIONS.md tells it to weight toward winning patterns
            without copying them.
```

### The composite winner score

Starting formula (tune empirically):

```
score = saves_per_reach * 3
      + shares_per_reach * 2
      + (follows_from_post / reach) * 8
      + comments_per_reach * 1
      + link_clicks_per_reach * 4
```

**Why these weights:**
- `saves` and `shares` are the strongest IG amplification signals → algorithm shows the post to more people.
- `follows_from_post` is the actual top-of-funnel conversion — weighted highest.
- `link_clicks` is the bottom-of-funnel signal (he tapped the bio link). Heavy weight because it's downstream of the CTA working.
- `comments` is positive but easy to game with engagement-bait. Light weight.
- Reach-normalized everywhere so a 500k post doesn't crush a 5k post that converted way better per impression.

Reach itself is *not* in the score. A wide-reach post that nobody saved is not a winner — it's noise that the algorithm gave a chance to and that didn't convert. We're optimizing for **per-impression quality**, not for raw eyeballs.

### The `WINNERS.md` contract

Written automatically by the analytics workflow, lives in the repo, read by the carousel skill at every generation. Format:

```markdown
# WINNERS — Top performing carousels (auto-generated, do not edit)

> Last updated: 2026-06-05 by analytics poller. Window: last 30 days.

## Top 10 carousels by composite score

1. score=4.21 — @ethos.fight — "The man you are at 2 AM" — 2026-05-24
   pillar=Real Talk, themes=[4], shape=Identity in action, slides=6
   hook=fragment ("The man you are at 2 AM."), cta=comment "seen"

2. score=3.87 — @ethos.discipline — "5 things he does before 8 AM" — 2026-05-26
   pillar=The Work, themes=[1,3], shape=Numbered list, slides=7
   hook=numbered ("5 things..."), cta=comment "begin"

[...8 more]

## Patterns over-represented in winners (last 30d)

- **Pillar weighting**: Real Talk +38% over baseline, The Work +22%,
  Scripture Applied +5%, The Vision −18%.
- **Title shapes**: "Identity in action" +44%, "Numbered list" +28%,
  "Reframe / myth-buster" +12%, "The mechanism" −8%, "Paradox" −22%.
- **Slide count**: 6 slides +31%, 5 slides +18%, 7+ slides −15%.
- **Hooks**: fragment-style (no verb) +29%, question-style +14%,
  declarative +2%, command-style −34%.
- **Accounts pulling weight**: @ethos.fight 2.4x avg, @ethos.discipline 1.6x,
  @ethos.scripture 0.7x.
- **Time-of-publish**: 6–8 AM ET +21%, 6–9 PM ET +18%, midday −12%.

## Recommended bias for next 7 days (skill should weight toward, not copy)

- Lean into Real Talk + The Work pillars.
- Default to 6 slides unless topic genuinely needs more.
- Prefer fragment hooks; deprioritize command hooks.
- Identity-in-action and Numbered-list shapes are over-indexing — alternate.
- @ethos.scripture is under-performing — investigate angle (audience too narrow?
  scripture too long-form for IG? bio needs rework?).
```

### Closing the loop in the skill

Add one line to `cloud-agent/INSTRUCTIONS.md`:

> Before generating, read `WINNERS.md`. Treat it as last week's evidence. Bias toward winning patterns without imitating winners directly. If your topic naturally calls for a deprecated shape, override the bias — judgment beats statistics on individual decisions.

The "without imitating" caveat matters. Statistical drift toward winners is good. Mode collapse to one winning template is the death of the brand voice.

---

## Account creation + warming (operational)

The collaborator handling Meta setup will also be the one creating these accounts. Checklist:

### Per-account creation (~30 min each)

- [ ] **Phone number**. Meta requires SMS verification. Real SIM is safest. Google Voice numbers sometimes accepted, sometimes rejected — try, fall back to a real number per account if rejected. Budget: $5–15/month per dedicated SIM via Mint Mobile etc. With 8 accounts, plan for 8 numbers.
- [ ] **Profile**: handle (per table above), display name, profile photo (distinct — don't reuse the ETHOS mark across all 8), bio (per the per-account profile doc), link-in-bio short URL.
- [ ] **Convert to Business** (Settings → Account → Switch to Professional → Business). Required for Content Publishing API. **Don't choose Creator** — Content Publishing API explicitly requires Business.
- [ ] **Connect to its dedicated FB Page** in the Aurealis Business Portfolio (see `01-meta-setup.md` Phase B).
- [ ] **Add to Business Settings → Instagram Accounts** under the Aurealis Portfolio so the System User token can publish to it.
- [ ] **Record the IG user ID** (17-digit) and add to Supabase `accounts` table.

### Warming schedule (per new account)

A brand-new IG account that goes from 0 → 2 posts/day looks bot-shaped. Ramp:

| Week | Posts/day | Other activity |
|---|---|---|
| 0 (set-up) | 0 posts | Fill out bio + 6 highlights stub. Follow 50–100 relevant accounts manually. Like + comment thoughtfully on 10–20 posts/day. |
| 1 | 1 post every other day (3 total) | Continue manual likes/comments. Engage authentically with comments on your posts. |
| 2 | 1/day | Add Stories occasionally. Reply to every DM. |
| 3 | 1/day, occasional 2/day | Most engagement still manual. |
| 4+ | 2/day standard | Normal cadence. |

Dashboard enforces the schedule per-account: `accounts.warming_state ∈ {new, warming-w1, warming-w2, warming-w3, normal}`. Publisher reads `daily_cap` from this state.

### Account cluster hygiene

Each account should look like a real person/brand built it, not like one of eight clones:

- [ ] Distinct first 9 grid posts — don't drop 9 carousels in the first hour. Spread over week 1–2.
- [ ] At least 3 distinct highlight covers per account.
- [ ] At least one Story/week to look human-active.
- [ ] Real-feeling first 10 comments — don't leave them at zero forever; comment manually if needed.

---

## Dashboard requirements derived from this strategy

The dashboard is no longer just "review + publish." Surfaces it must have:

### Inbox (drafts)
- 15 drafts/day. Preview slides as images. Caption visible + editable.
- Each draft shows `pillar`, `themes`, `title_shape`, `archetype`, `slide_count`.
- "Assign to account" picker; in Phase B, shows top-2 auto-suggestions with scores.
- "Edit caption" inline. "Edit hashtags" — picks from per-account pools, validates against 7d uniqueness.
- "Approve & schedule" → places in queue at the next available slot for that account.

### Accounts view
- 8 account cards. Each shows: handle, bio, link, profile pic, today's slots (filled / empty), warming state, token health, 7d composite score, 7d follower delta, last published post.
- "Pause account" toggle (in case of an outage, shadow-ban suspicion, or a misfire).

### Schedule view
- Calendar grid: next 7 days × 8 accounts = 112 slots.
- Filled slots show carousel thumbnail; empty slots show what they need.
- Drag-to-reschedule.

### Performance view
- Leaderboard: top carousels by composite score, filterable by account / pillar / shape / window.
- Per-account performance trend (7d, 30d, 90d).
- Pattern view — which pillars/shapes/hook forms are over-indexing this window.
- "Promote pattern" button → when you see a clear winner pattern, this writes a recommendation into `WINNERS.md` for the next generation cycle.

### Token & health
- Meta System User token expiry check (should always say "never").
- Per-account: rate limit remaining, last successful publish, last failed publish + reason.
- Webhook event log (Meta sends `instagram` webhook events on success/failure).

### Skill control
- Read-only view of `cloud-agent/WINNERS.md`.
- Trigger a manual regeneration (one extra carousel) — calls the carousel skill.
- View `cloud-agent/accounts/<handle>.md` per account, with edit capability that opens a PR.

---

## What's out of scope here (for later docs)

- The publisher's exact algorithm for the 3-step Meta carousel call, polling, error handling, retry — covered when we build Phase 1 publisher.
- The dashboard's data model and Supabase schema — covered when we scaffold the dashboard.
- Pattern extraction algorithm details — likely Python in a Vercel Function, possibly an LLM call for n-gram clustering. Designed when analytics is built.
- The full A/B experimentation framework (e.g. intentionally posting two near-identical themes to two accounts to isolate a single variable) — Phase 4 work, only meaningful once baseline analytics are flowing.

---

## Checkpoint

When this strategy is implemented, the system runs like this:

1. **Morning**: carousel skill generates 15 drafts, reading `BRAND.md`, `TOPICS.md`, `CAROUSEL.md`, `WINNERS.md`, and the 8 `accounts/*.md` profiles. Pushes PR.
2. **Render**: GitHub Actions renders JPEGs to R2.
3. **Inbox**: drafts appear in the dashboard. Reviewer (you) spends 15–30 min: read, assign, tweak captions, approve.
4. **Publish**: publisher cron picks ripe items, jittered times, posts via Meta Graph API.
5. **Measure**: analytics poller pulls IG Insights daily for 7 days post-publish.
6. **Learn**: weekly winner-pattern extraction updates `WINNERS.md`.
7. **Compound**: tomorrow's drafts are better than yesterday's because the skill reads what won.

That's the loop. Everything else is infrastructure to make this loop reliable.
