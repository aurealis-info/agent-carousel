# 09 — Monetization Strategy

ETHOS monetization is designed around a single principle: **free users should feel the weight of what they're leaving on the table, not the sting of a locked feature.** The free tier delivers real daily value — a personalized verse matched to where you're at, the mood check-in, and a taste of AI-guided conversation. The paid tier unlocks depth: unlimited conversations with the AI, full growth tracking, weekly snapshots, and tools that help a man actually measure his progress. This keeps the product from feeling extractive while building a business that sustains the mission.

The thesis is simple: men will pay for something that makes them better. Not for content. Not for inspiration. For a daily system that holds them accountable to the man they said they wanted to become.

---

## 1. Pricing Model

### Canonical Pricing (Final Spec)

| Plan | Price | Trial | Notes |
|------|-------|-------|-------|
| **Monthly** | $9.99/mo | No trial | Straightforward recurring charge. No hand-holding. |
| **Annual** | $59.99/yr | 7-day free trial | Pre-selected on paywall, labeled **"Save 50%"** |

> **Note:** Earlier MVP documentation referenced $12/mo and $99/yr. Those figures are **superseded** by the Final Spec pricing above. All paywall UI, analytics events, and RevenueCat product IDs should reflect the canonical $9.99/$59.99 pricing.

### Why Annual-Only Trial

The 7-day free trial is offered exclusively on the annual plan. This is intentional:

- **Maximizes upfront LTV collection.** A user who converts after trial pays $59.99 immediately rather than $9.99. Even with higher churn on annual plans, the collected revenue per conversion is dramatically higher.
- **Reduces monthly churn exposure.** Monthly subscribers can cancel after one month ($9.99 collected). Annual subscribers who convert are locked in for a full year.
- **Pre-selection of the annual plan** with the "Save 50%" badge steers the majority of conversions toward the higher-LTV option. Industry benchmarks suggest 60-75% of conversions will choose the pre-selected annual plan when presented this way.
- **No trial on monthly signals commitment.** Men who choose the monthly plan are making a decision right now. No safety net. That self-selection filters for higher-intent users who stick around.

### Subscription Infrastructure

**RevenueCat** handles all subscription management:

- **Receipt validation** — server-side verification of App Store and Google Play receipts, eliminating client-side fraud vectors
- **Subscription status** — real-time entitlement checks so the app always knows whether a user is free, trialing, or paid
- **A/B testing** — native paywall experimentation (price points, trial lengths, copy variants) without app updates
- **Analytics** — MRR, churn, trial conversion, and cohort tracking out of the box
- **Cross-platform** — single source of truth for iOS and Android subscription state

---

## 2. Free vs. Pro Feature Table

| Feature | Free | Pro |
|---------|------|-----|
| **Daily verse** (personalized to your check-in + explanation + prayer) | Unlimited | Unlimited |
| **Mood check-in** (12 tags: Discipline, Courage, Doubt, Lust, Pride, Anxiety, etc.) | Yes | Yes |
| **AI conversations** (guided interpretation, deeper study, real talk) | 3 total (lifetime) | Unlimited |
| **Basic sharing** (verse card to stories/messages) | Yes | Yes |
| **Verse saving from chat** (inline verse cards generated during AI conversations) | No | Yes |
| **Radar chart** (spiritual growth tracking across all 12 dimensions) | Blurred preview | Full access |
| **Weekly snapshots** (week-over-week growth summaries) | No | Yes |
| **Premium share templates** (verse + radar snapshot + progress visuals) | No | Yes |
| **Chat history** (access to past AI conversations) | 3 conversations | Full history |

### Design Rationale

- **Daily verse stays free and unlimited.** This is the core habit loop. A man checks in, gets his verse, starts his day. Gating this kills the daily discipline before he ever hits a paywall.
- **3 lifetime AI conversations is deliberately tight.** Three is enough to experience the depth of AI-guided Scripture interpretation — enough to realize you need it, not enough to rely on it. When the 4th conversation is blocked, the man has already felt the value. The upgrade is a decision to go deeper, not a guess.
- **Blurred radar chart is a visual paywall built on loss aversion.** The user can see that his data is being tracked — the shape is there, the dimensions are labeled, but the details are blurred. His growth is right there. He just can't see it yet. That tension converts.
- **Verse saving from chat is Pro-only** because inline verse cards are a high-value, high-effort feature (AI-generated, contextually matched to his specific situation). Keeping them behind the paywall rewards the men who commit.
- **Weekly snapshots are Pro-only** because they require sustained engagement to generate. By the time a user has enough data for a meaningful snapshot, he's invested enough to understand the value of tracking his growth.

---

## 3. Paywall Triggers (Priority Order)

| # | Trigger | When It Fires | Expected Conversion Share | Rationale |
|---|---------|---------------|---------------------------|-----------|
| 1 | **End of onboarding (3-step primer)** | First app open, after completing the onboarding flow | ~50% | Highest-intent moment. The man has just answered honest questions about where he's at, selected his tags, and seen a preview of what ETHOS delivers. He's invested. The trial offer is the natural next step — not an interruption, but an invitation to commit. |
| 2 | **4th AI conversation attempt** | After all 3 free conversations have been used (lifetime cap) | ~30% | The man has experienced the AI's value and is actively seeking more. He's mid-struggle, mid-question, mid-growth — and the gate appears at the exact moment he wants to go deeper. This is a "moment of need" paywall. |
| 3 | **Blurred radar chart tap** | After week 1 (enough data to populate the chart) | ~15% | Users who reach this point are engaged and curious about their growth. They've been checking in daily, and now they want to see the pattern. The blurred preview creates a "so close" tension that drives conversion. |
| 4 | **"Upgrade" in Profile** | Anytime (passive, always available) | ~5% | Catch-all for men who decide to upgrade on their own schedule. Low conversion share but zero friction — it should always be there. |

### Paywall UX Guidelines

- **Always show the annual plan pre-selected** with the "Save 50%" badge prominently displayed.
- **Use masculine, direct copy as the default.** No soft invitations. No pastel language. The man just completed onboarding or hit his conversation limit — he's already engaged. The copy meets him where he is:
  - Post-onboarding: **"You showed up. Now go deeper."**
  - 4th conversation block: **"You've been doing the work. Don't stop here."**
  - Blurred radar chart: **"Your growth is being tracked. See the full picture."**
  - Profile upgrade: **"Unlock the full system."**
- **Never interrupt the daily verse flow** with a paywall. The daily verse is the discipline engine. Gating it would break the one habit that keeps men coming back.
- **Paywall dismissal should be clean.** A single "Not yet" link. No guilt trips, no countdown timers, no manipulative urgency. The audience is men pursuing faith — respect and directness are non-negotiable. Dark patterns undermine trust, and trust is the entire product.

---

## 4. Phase 2 Monetization — Leaders Feature

### The Core Insight

> **"Men don't pay for content. They pay for access to men who've walked the path."**

This is the strategic foundation of Phase 2. Rather than expanding the paywall to gate more features, ETHOS introduces a **premium human layer** — men who embody "the man God intended." Leaders, fathers, entrepreneurs, pastors who have built something real and are willing to mentor the next generation of men coming up behind them.

This shifts the monetization model from **restrictive** ("you've run out of conversations") to **aspirational** ("learn from men who've already become what you're building toward").

### Leaders Premium Tier

| Detail | Specification |
|--------|---------------|
| **Price** | $29/mo (in addition to base Pro subscription) |
| **Revenue share** | 70/30 favoring leaders |
| **Target segment** | Engaged Pro users who want human mentorship beyond AI guidance — men ready for direct accountability and real-world wisdom |

### Leader Interaction Types

| Interaction | Format | Details |
|-------------|--------|---------|
| **Async Q&A** | Text-based, in-app | 48-hour response window. Users submit real questions about what they're facing; leaders respond on their own schedule. Keeps the bar low for leader participation while delivering high-impact guidance. |
| **Monthly group calls** | Live video/audio | 60 minutes, 10-20 men per session. Intimate enough to feel like iron sharpening iron, scalable enough to be worth the leader's time. |
| **Content library** | On-demand | Frameworks, courses, and templates created by leaders. Evergreen material on fatherhood, discipline, leadership, marriage, career — content that continues delivering value without ongoing leader effort. |

### Why This Works

- **For users:** Access to men they look up to — leaders, fathers, entrepreneurs who've walked through what they're walking through now. Lived experience, direct accountability, and real-world wisdom that AI cannot replicate.
- **For leaders:** A monetized channel to mentor at scale without building their own platform. Revenue share makes participation profitable. ETHOS handles tech, payments, and community moderation. These are men who want to pour into the next generation — ETHOS gives them the infrastructure to do it.
- **For ETHOS:** Dramatically higher ARPU from the Leaders segment ($29/mo = $348/yr vs. $59.99/yr base). Network effects — more leaders attract more men, more men attract more leaders. The platform becomes the place where serious Christian men go to grow.

### Phase 2 Timeline

See Section 3 of the Creator & Influencer Playbook (Document 10) for the full Founding Leader recruitment rollout.

---

## 5. Unit Economics

### Backend Cost Estimates

| Scale | Supabase | OpenAI / Claude API | Total Estimated Cost |
|-------|----------|---------------------|----------------------|
| **1K daily active users** | ~$5-15/mo | ~$10-25/mo | **~$15-40/mo** |
| **10K daily active users** | ~$25-75/mo | ~$75-225/mo | **~$100-300/mo** |

These estimates assume:
- Supabase Pro plan with usage-based scaling
- Average 2-3 AI conversation messages per active user per day (paying users)
- Claude/OpenAI API costs at ~$0.01-0.03 per chat exchange (input + output tokens)
- Daily verse generation batched and cached based on tag combinations (not per-request)

### Revenue Per Paying User

| Plan | Annual Revenue | Notes |
|------|----------------|-------|
| **Annual** | $59.99/yr | Single upfront payment |
| **Monthly** | $119.88/yr | $9.99 x 12 (assumes full year retention) |
| **Blended average** | ~$60/yr | Conservative estimate assuming 70% annual, 30% monthly with churn |

### Conversion Scenarios

| Total Users | Conversion Rate | Paying Users | Avg Revenue/User | Estimated ARR |
|-------------|-----------------|--------------|-------------------|---------------|
| 10,000 | 12% | 1,200 | ~$60 | **~$72,000** |
| 25,000 | 12% | 3,000 | ~$60 | **~$180,000** |
| 50,000 | 12% | 6,000 | ~$60 | **~$360,000** |
| 100,000 | 12% | 12,000 | ~$60 | **~$720,000** |

### Phase 2 Leaders Impact on ARPU

The Leaders premium tier ($29/mo = $348/yr) significantly increases ARPU for users in that segment. Even if only 5-10% of Pro users upgrade to Leaders access:

| Scenario | Base Pro Users | Leaders Users | Blended ARPU | ARR Impact |
|----------|----------------|---------------|--------------|------------|
| 50K total, 12% Pro, 5% Leaders | 5,700 | 300 | ~$74 | **~$446K** (vs. $360K base) |
| 50K total, 12% Pro, 10% Leaders | 5,400 | 600 | ~$88 | **~$531K** (vs. $360K base) |

### Margin Profile

At scale (10K+ DAU), backend costs remain under $300/mo while revenue from even modest conversion rates exceeds $6K/mo. This yields **gross margins above 95%** on the base subscription — a strong SaaS profile. The primary cost centers will be:

- Apple/Google platform fees (15-30% of subscription revenue)
- Leader revenue share (70% of Leaders tier revenue)
- Marketing and user acquisition
- Team salaries

---

## 6. Success Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Trial start rate** (% of paywall views that start trial) | >20% | Measures paywall effectiveness. If fewer than 20% of men who see the paywall start a trial, the copy, design, or timing needs work. The masculine framing should outperform generic spiritual copy — if it doesn't, the positioning is off. |
| **Trial to paid conversion** (% of trial starts that convert to paid) | >50% | Measures value delivery during the trial period. If users don't convert after 7 days of full access to the radar chart, unlimited conversations, and weekly snapshots, the product isn't demonstrating enough value. |
| **Free to paid (overall)** (% of all users who become paying) | 10-15% | The core business viability metric. Below 10% at scale, the business model doesn't work. Above 15% is exceptional for a consumer subscription app. |
| **Day 7 retention** (% of new users who return on day 7) | >30% | Indicates whether ETHOS is forming a daily discipline. The check-in + verse loop is designed to drive this — if D7 is below 30%, the habit loop is broken. |
| **Verses saved per user (week 1)** | >3 | Leading indicator for long-term retention. Men who save verses are building a personal collection — creating investment in the app that makes leaving feel like losing something. |
| **Share rate** (% of users who share 1+ item in first 30 days) | >10% | Organic distribution health. Sharing is ETHOS's primary growth channel. The dark, masculine share templates should perform well in Instagram stories and group chats. If fewer than 10% share, the mechanic needs redesign or the templates aren't worth posting. |

### Secondary Metrics to Track

| Metric | Target | Notes |
|--------|--------|-------|
| Chat messages per session | 4-6 | Too few = not engaging. Too many = AI dependency concern. The AI should guide, not become a crutch. |
| Daily verse open rate | >60% of DAU | Are men engaging with the core feature daily? This is the heartbeat of the app. |
| Paywall dismissal rate | <80% | If 80%+ dismiss without action, paywall timing or copy is off. Test different masculine copy variants. |
| Monthly churn (paid) | <8% | Consumer app benchmark. Identity-tied apps (faith, fitness, self-improvement) often see lower churn — the subscription feels like part of who they are. |
| Tag check-in completion rate | >70% of sessions | Are men actually being honest about where they're at? If the check-in rate drops, the tags may need refinement or the UX is creating friction. |
| Net Promoter Score | >50 | High bar, but men in faith communities talk. Word of mouth in church groups, group chats, and accountability circles is the highest-leverage growth channel. |

---

## 7. Pricing Experimentation Plan

All experiments run through **RevenueCat's paywall experimentation** feature, which allows server-side A/B tests without requiring app updates.

### Experiment 1: Annual Price Point

| Variant | Price | Hypothesis |
|---------|-------|------------|
| Control | $59.99/yr | Current canonical pricing |
| Variant A | $49.99/yr | Lower price increases trial starts enough to offset per-user revenue loss |
| Variant B | $69.99/yr | Higher price doesn't materially reduce conversion, increasing LTV |

**Primary metric:** Revenue per paywall view (not conversion rate alone — a lower price with higher conversion could still lose on revenue).

### Experiment 2: Monthly Price Point

| Variant | Price | Hypothesis |
|---------|-------|------------|
| Control | $9.99/mo | Current canonical pricing |
| Variant A | $7.99/mo | Psychological pricing below $8 increases monthly plan selection |
| Variant B | $12.99/mo | Tests price elasticity at the upper bound. Men paying $12.99 may retain better due to commitment bias — they chose the higher price, so they take it more seriously. |

**Primary metric:** Monthly plan selection rate and 90-day retention.

### Experiment 3: Trial Length

| Variant | Trial | Hypothesis |
|---------|-------|------------|
| Control | 7-day | Current standard |
| Variant A | 3-day | Shorter trial creates urgency. Men either commit or they don't — 3 days forces a faster decision. |
| Variant B | 14-day | Longer trial allows deeper habit formation. Two full weeks of daily check-ins and the radar chart builds enough data for a compelling weekly snapshot, making the "full picture" paywall argument stronger. |

**Primary metric:** Trial-to-paid conversion rate. Secondary: D30 retention of converted users.

### Experiment 4: Paywall Copy

| Variant | Copy Style | Example |
|---------|------------|---------|
| Control | Masculine / direct | "You showed up. Now go deeper." |
| Variant A | Feature-focused | "Unlimited conversations. Full growth tracking. The complete system." |
| Variant B | Challenge-based | "Most men quit here. You're not most men." |

**Primary metric:** Trial start rate. The masculine copy aligns with the "Become The Man God Intended" brand identity, but feature-focused copy may perform better with users who need specifics. Challenge-based copy tests whether competitive framing increases conversion among the target demographic.

### Experimentation Rules

- **Minimum sample size:** 500+ paywall views per variant before declaring a winner.
- **Minimum duration:** 1 full week per test (to account for day-of-week variation in usage patterns).
- **Statistical significance:** 95% confidence level before rolling out a winner.
- **One test at a time** on the same paywall surface. Running multiple overlapping tests on the same screen creates confounding variables.
- **Document every test** — hypothesis, variants, results, and decision — in a shared experimentation log.

---

*Last updated April 4, 2026.*
