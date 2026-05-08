# 08 — Go-To-Market & Distribution Strategy

This document defines the complete go-to-market plan, distribution channels, launch timeline, and growth strategy for ETHOS. The GTM strategy is built around one fundamental advantage: Imman.faith's existing audience of 150K+ followers. Every phase of this plan is designed to maximize the leverage of that distribution asset while building independent, sustainable growth loops that compound over time.

---

## 1. Launch Phases

### Phase 1 — Design (Weeks 1-2)

**Objective:** Establish the complete visual and interaction foundation before writing a single line of code.

**Deliverables:**
- Figma wireframes for all screens: Onboarding (8 screens), Home, Daily Anchor, Chat Companion, Profile, Paywall (3-step), Settings
- Complete UI kit: color palette, typography scale, spacing system, component library (buttons, cards, chips, inputs, navigation)
- Brand assets: ETHOS logo (primary, secondary, icon-only), anchor icon, share card templates, notification icon
- Share templates: Verse card template for Instagram Stories, radar chart snapshot template, weekly reflection card
- Onboarding illustration set: Welcome animation, notification priming illustration, radar chart preview

**Key Decisions to Lock:**
- Warm/light aesthetic direction finalized (no dark mode for v1)
- Typography selections (primary + secondary fonts)
- Color values (exact hex codes for all brand colors)
- Icon style (line weight, corner radius, visual tone)
- Share card dimensions and branding placement

**Exit Criteria:** Design system is complete enough that any screen can be built without further design decisions. All stakeholders have reviewed and approved the Figma file.

---

### Phase 2 — Core Build (Weeks 3-6)

**Objective:** Build the functional core of the app — the screens and features a user interacts with on Day 1.

**Week 3-4: Foundation + Onboarding**
- React Native (Expo) project initialization
- Navigation structure (React Navigation or Expo Router)
- Onboarding flow: all 8 screens with local data storage
- Supabase project setup: auth, database schema, Edge Functions
- Basic authentication (email + Apple Sign-In + Google Sign-In)

**Week 5: Daily Anchor (AI Feature)**
- Mood check-in UI (emoji or word selection)
- Claude API integration for verse + explanation + prayer generation
- Prompt engineering: system prompt for Daily Anchor (warm, pastoral, Scripture-grounded, personalized to mood and profile)
- Daily Anchor display screen with share mechanic
- Local caching for offline access to today's anchor

**Week 6: Chat Companion (AI Feature)**
- Chat UI (message bubbles, input field, typing indicator)
- Claude API integration for real-time conversational guidance
- Prompt engineering: system prompt for Chat Companion (empathetic, biblically accurate, never prescriptive on doctrine, always points back to Scripture)
- Free tier enforcement: 3 conversations per day, soft paywall on 4th attempt
- Conversation history storage (Supabase)

**Week 6: Profile Shell**
- Profile screen with user info, identity anchor display, selected growth axes
- Settings screen (account, notifications, subscription management, about)
- Placeholder for radar chart (visual only — data population comes in Phase 4)

**Exit Criteria:** A user can complete onboarding, receive a Daily Anchor, have a chat conversation, and view their profile. The app is functionally usable end-to-end, even if unpolished.

---

### Phase 3 — Monetization + Analytics (Week 7)

**Objective:** Integrate the revenue and data infrastructure that makes the business viable.

**RevenueCat Integration:**
- Install RevenueCat SDK (`react-native-purchases`)
- Configure products in App Store Connect and Google Play Console
- Create offerings (monthly + annual with trial)
- Implement paywall screens (3-step primer from onboarding + secondary triggers)
- Implement subscription status checking (`CustomerInfo`) for feature gating
- Implement restore purchases flow
- Test purchase flow end-to-end in sandbox environment
- Configure server-side receipt validation webhook to Supabase

**Analytics Integration:**
- Install PostHog (or Mixpanel) SDK
- Implement complete event tracking schema (all onboarding events, feature usage, paywall interactions)
- Set up funnel visualizations: onboarding completion funnel, paywall conversion funnel
- Configure user identification (anonymous ID --> authenticated ID linking)
- Set up session replay (PostHog) for UX debugging

**Exit Criteria:** Purchases work end-to-end in sandbox. Analytics events fire correctly for all key user actions. Funnels are visualized in the dashboard.

---

### Phase 4 — Polish (Weeks 8-9)

**Objective:** Add the features that transform ETHOS from functional to delightful and habit-forming.

**Saved Verses:**
- Bookmark functionality on Daily Anchor and Chat responses
- Saved verses screen in Profile
- Share saved verses to Instagram Stories

**Radar Chart:**
- Interactive radar chart visualization on Profile screen
- Data population from onboarding selections and ongoing usage
- Weekly data point calculation based on app engagement and self-assessment
- Blurred state for free tier (paywall trigger after Week 1)

**Share Mechanic:**
- Branded verse card generation (programmatic image creation using react-native-view-shot or similar)
- Share to Instagram Stories with ETHOS branding and subtle CTA
- Radar chart snapshot sharing
- Deep link from shared content back to app (or App Store if not installed)

**Push Notifications:**
- Daily Anchor delivery notification (morning, user-configurable time)
- Weekly snapshot notification (Sunday evening)
- Trial expiration reminder (2 days before trial ends — as promised in onboarding)
- Re-engagement notification for lapsed users (Day 3 and Day 7 after last open)
- Notification preferences in Settings

**Weekly Snapshot:**
- Summary screen shown once per week (Sunday)
- Days active, verses received, chats had, growth axes progress
- Shareable card format
- Pro-only feature (free tier sees blurred version)

**Exit Criteria:** All features are implemented and polished. Share mechanic produces clean, branded images. Push notifications fire reliably. The app feels complete and ready for external users.

---

### Phase 5 — Beta (Weeks 10-11)

**Objective:** Validate the product with real users from the target audience before public launch.

**TestFlight Recruitment:**
- Recruit 50-200 beta testers from Imman's audience
- Recruitment mechanism: Instagram Story with sign-up link (Google Form or Typeform collecting name + email + TestFlight-compatible email)
- Selection criteria: 18-30, active in faith community, iPhone user (TestFlight is iOS-only; Android beta via Google Play internal testing)
- Communicate clearly: "This is a beta. Things will break. Your feedback shapes the final product."

**Beta Testing Protocol:**
- Week 10: Testers onboard and use the app daily for 7 days
- Collect feedback via: in-app feedback button (simple text input), weekly survey (Google Form), direct DM conversations with select testers
- Key questions to answer:
  - Does the onboarding feel right? Where do people drop off?
  - Is the Daily Anchor meaningful? Do people look forward to it?
  - Is the Chat Companion helpful? Are responses biblically grounded?
  - Does the paywall feel fair? Would you pay $9.99/mo or $59.99/yr?
  - What's missing? What would make you use this every day?

**Iteration Priorities:**
- Week 11: Analyze feedback and analytics. Prioritize fixes:
  1. Onboarding drop-off points (any screen with >20% abandonment)
  2. AI response quality issues (theological inaccuracy, tone misses)
  3. Paywall friction (if trial start rate is below 15%)
  4. UX bugs and polish issues reported by testers
- Ship daily updates during beta week to show responsiveness

**ICP Validation:**
- Critical question: Does Imman's audience align with the devout Christian ICP, or does it skew self-improvement?
- Measure: What percentage of beta users are engaged with the Scripture/devotional features vs. the self-improvement framing?
- If audience skews self-improvement, adjust content strategy and possibly onboarding language before public launch

**Exit Criteria:** Onboarding completion >75%. Day 7 retention >25%. At least 10 qualitative testimonials. No critical bugs. Paywall conversion rate measured and baselined.

---

### Phase 6 — Launch (Weeks 12+)

**Objective:** Ship to the App Store, execute the launch content strategy, and begin scaling.

**App Store Submission:**
- Submit to Apple App Store review (allow 2-5 days for review)
- Submit to Google Play Store (typically faster review)
- Ensure all metadata is complete: description, keywords, screenshots, preview video, privacy policy URL, support URL
- App Store rating prompt: trigger after 5 successful Daily Anchor views (not during onboarding, not after paywall)

**ASO Optimization:**
- Title: "ETHOS — Biblical Companion"
- Subtitle: "Daily Verse & Faith Guidance"
- Keywords: christian app, bible companion, daily devotional, faith growth, scripture, prayer, bible study, christian life, spiritual growth, devotion
- Screenshots: 6 screenshots showing (1) Daily Anchor with verse, (2) Chat Companion in action, (3) Radar Chart growth visualization, (4) Onboarding mood selection, (5) Share card on Instagram, (6) Weekly Snapshot
- Preview video: 15-30 second app walkthrough showing the Daily Anchor flow

**Launch Content Push:**
- Coordinate with Imman for a 10+ post content series building to and following launch day
- Launch day: Imman posts a reel announcing ETHOS with a direct App Store link
- First week: Daily content across all formats (carousels, reels, stories, static posts)
- First month: Maintain 5 posts/week cadence with emphasis on user testimonials and real usage moments

**Exit Criteria:** App is live on both stores. Imman launch content is posted. First 1,000 downloads tracked. Day 1 analytics baseline established.

---

## 2. Distribution Channels

### PRIMARY: Imman.faith Audience (150K+ Followers)

**Why this is the primary channel:**
Imman is not a paid endorser or influencer partner. He is the founder and builder of ETHOS. His audience already trusts him. His content already speaks to the target demographic. ETHOS is a natural extension of the value he already provides — not an ad interruption.

**Content Hook — Build-in-Public Series:**
The most effective launch strategy for creator-built products is the build-in-public narrative. Imman documents the journey of building ETHOS — the why, the struggle, the breakthroughs, the setbacks — and his audience follows along. By launch day, they are emotionally invested in the product's success. They are not downloading an app; they are supporting a vision they watched come to life.

Build-in-public content ideas:
- "I'm building an app for the person I'm becoming. Here's why."
- "I showed the first version to 10 people. Here's what they said."
- "This feature almost didn't make it in. I'm glad it did."
- "I almost quit building this last week. Here's what kept me going."
- Culminating: "It's here. ETHOS is live. For the person you're becoming."

**Day-in-the-Life Integration:**
Imman naturally integrates ETHOS into his daily content. Morning routine includes opening the Daily Anchor. A tough moment leads to a Chat Companion conversation. A weekly reflection uses the radar chart. This positions ETHOS as a lived tool, not a product pitch.

**The Signature Line:**
"I'm not yet the person I want to be, but I'm far from who I once was." This is the emotional throughline. It should appear in launch content, the App Store description, and Imman's personal narrative. It captures the transformation journey that ETHOS facilitates.

**RISK: Audience-ICP Alignment**
Imman's audience may skew toward self-improvement males rather than devout practicing Christians. This is the single biggest risk to the launch strategy. Mitigations:
- Beta testing (Phase 5) validates audience alignment before committing to full launch
- If the audience skews self-improvement, adjust content framing to bridge from self-improvement entry point to faith-deepening retention
- Monitor conversion and retention by content source — are users from Imman's audience retaining at the same rate as users from other sources?

---

### IN-APP VIRAL LOOP: The Share Mechanic

**Why this is the secondary channel:**
Paid acquisition is expensive and unprofitable at early stage. Organic viral loops are free and compound over time. The share mechanic turns every engaged user into a distribution channel.

**Verse Card Share Loop:**
1. User receives their Daily Anchor (personalized verse + explanation)
2. User taps "Share" — app generates a branded verse card image
3. User shares to Instagram Stories
4. Friend sees the verse card, notices the ETHOS branding
5. Friend asks "What's ETHOS?" or taps the link
6. Friend downloads ETHOS
7. New user receives their own Daily Anchor
8. Cycle repeats

**Radar Chart Snapshot Loop:**
1. User views their weekly radar chart showing growth across selected axes
2. User taps "Share Snapshot" — app generates a branded radar chart image
3. User shares to Instagram Stories with a caption about their growth journey
4. Friend sees the chart, is intrigued by the growth visualization
5. Friend downloads ETHOS to track their own growth
6. Cycle repeats

**Design Requirements for Viral Loops:**
- Share cards must be beautiful enough that users want to post them (this is non-negotiable — ugly share cards kill viral loops)
- ETHOS branding must be visible but not dominant — the content (verse or chart) is the star
- Include a subtle CTA on every share card: "Get your daily anchor — ethos.app" or similar
- Deep link from share card to App Store (or app if installed) using a universal link

---

### CHRISTIAN COMMUNITIES: Targeted Offline-to-Online Distribution

**Why this channel matters:**
The devout Christian ICP already gathers in physical and digital communities — churches, campus ministries, small groups, Bible studies. These communities are high-trust environments where a recommendation from a peer or leader carries enormous weight. One youth pastor recommending ETHOS to their group of 50 is more valuable than 5,000 ad impressions.

**Target Segments:**
- **Texas and Bible Belt communities** — per Matthew's insight, the religious base is strong and receptive
- **Christian university campuses** — Liberty University, Baylor, Wheaton College, Biola, Dallas Baptist, Samford, among others
- **Megachurch young adult groups** — Elevation, Transformation Church, Hillsong, Vous Church, Church of the Highlands
- **Campus ministries** — Cru (formerly Campus Crusade), InterVarsity, Young Life, Fellowship of Christian Athletes
- **Online Christian communities** — Facebook groups, Discord servers, Reddit communities (r/Christianity, r/TrueChristian)

**Outreach Strategy:**
- Phase 1 (Beta): Seed the app with campus ministry leaders and young adult pastors who can provide feedback and become early advocates
- Phase 2 (Launch): Provide leaders with a "recommend to your group" kit — a short description, App Store link, and 3 reasons to recommend it
- Phase 3 (Scale): Explore church partnership program where leaders get free Pro access in exchange for recommending to their community

---

### APP STORE OPTIMIZATION (ASO)

**Why ASO matters:**
App Store search is a significant discovery channel for faith-based apps. Users actively searching "Christian app," "daily devotional," or "Bible companion" have high intent. Ranking for these keywords drives free, high-quality installs.

**Keyword Strategy:**

Primary keywords (high intent, moderate competition):
- christian app
- bible companion
- daily devotional
- faith growth
- scripture daily

Secondary keywords (niche, lower competition):
- christian journal
- prayer app
- bible study companion
- spiritual growth tracker
- devotional for young adults

Long-tail keywords:
- daily bible verse app
- christian meditation and prayer
- faith companion for young christians
- personalized bible devotional

**Screenshot Optimization:**
- Screenshot 1: Daily Anchor with a compelling verse (hook — must work standalone)
- Screenshot 2: Chat Companion responding to a real struggle (show the AI value)
- Screenshot 3: Radar Chart growth visualization (differentiation — no other app has this)
- Screenshot 4: Onboarding mood selection (personalization story)
- Screenshot 5: Verse share card on Instagram (social proof / virality story)
- Screenshot 6: Weekly Snapshot (habit / progress story)

**Description:**
- First sentence must contain the primary keyword and communicate the core value: "ETHOS is your daily biblical companion — a personalized verse, prayer, and faith-based guidance for the person you're becoming."
- Highlight personalization (mood-based, AI-powered)
- Highlight the two core features (Daily Anchor + Chat Companion)
- Include social proof when available (user count, ratings, testimonials)
- End with tagline: "For the person you're becoming."

---

## 3. Geographic Strategy

### Rationale

Not all U.S. markets are equal for a Christian faith app. Per Matthew's input: "Market ETHOS heavily in places like Texas where the religious base is strong." Concentrating early marketing efforts in regions with high religiosity increases the probability of product-market fit validation, improves early retention metrics, and builds a dense user base that amplifies viral loops.

### Priority Markets (Tier 1)

| State/Region | Why | Key Cities |
|--------------|-----|------------|
| **Texas** | Largest religious population in the U.S. Strong evangelical community. Multiple Christian universities (Baylor, DBU, ACU). | Houston, Dallas-Fort Worth, San Antonio, Austin |
| **Tennessee** | Bible Belt core. Nashville has a massive Christian music and media ecosystem. | Nashville, Memphis, Knoxville |
| **Georgia** | Atlanta is a hub for Black Christian communities and megachurches. | Atlanta, Savannah |
| **North Carolina** | Strong evangelical presence. Multiple Christian universities. | Charlotte, Raleigh-Durham |
| **Alabama** | Deep religious culture. Samford University. | Birmingham, Huntsville |

### Christian University Towns (Tier 1B)

These towns have a concentrated population of the exact ICP (devout Christians, 18-24, digitally native):

| University | Location | Denomination/Affiliation |
|-----------|----------|-------------------------|
| Liberty University | Lynchburg, VA | Evangelical |
| Baylor University | Waco, TX | Baptist |
| Wheaton College | Wheaton, IL | Evangelical |
| Biola University | La Mirada, CA | Evangelical |
| Dallas Baptist University | Dallas, TX | Baptist |
| Samford University | Birmingham, AL | Baptist |
| Oral Roberts University | Tulsa, OK | Charismatic |
| Cedarville University | Cedarville, OH | Baptist |
| Liberty's online program | National | Evangelical |

### Geo-Targeted Advertising (When Ready)

When paid acquisition begins (post-organic validation), use Instagram's geo-targeting to concentrate ad spend in Tier 1 states and university towns. This approach:
- Maximizes ROI by targeting the highest-receptivity audiences
- Creates local density that amplifies word-of-mouth
- Produces better early metrics (which improves App Store ranking algorithms)

---

## 4. Growth Loops

### Loop 1: Content Loop (Organic — Active from Day 1)

```
User receives Daily Anchor
        |
        v
User shares verse card to Instagram Stories
        |
        v
Friend sees verse card, resonates with the verse
        |
        v
Friend notices ETHOS branding, asks "What's ETHOS?"
        |
        v
Friend downloads ETHOS
        |
        v
New user receives their own Daily Anchor
        |
        v
New user shares... (cycle repeats)
```

**Key Metric:** Share rate (% of daily active users who share at least one verse card per week). Target: >10%.

**Optimization Levers:**
- Make sharing frictionless (one tap to generate card, two taps to post to Stories)
- Make share cards beautiful (users share content that makes them look good)
- Include gentle nudge to share after 3 consecutive days of usage ("Your friends would love this verse. Share it?")

---

### Loop 2: Snapshot Loop (Organic — Active from Week 2+)

```
User views weekly radar chart / growth snapshot
        |
        v
User shares snapshot to Instagram Stories
        |
        v
Friend sees growth visualization, is intrigued
        |
        v
Friend asks about the app / taps the link
        |
        v
Friend downloads ETHOS to track their own growth
        |
        v
New user builds their own radar chart... (cycle repeats)
```

**Key Metric:** Snapshot share rate (% of Pro users who share their weekly snapshot). Target: >15%.

**Optimization Levers:**
- Design the radar chart to be visually distinctive — something people haven't seen from other apps
- Add a "growth streak" or "faith journey" label that users would be proud to share
- Prompt sharing on Sundays (after weekly reflection) when users are most reflective

---

### Loop 3: Creator Loop (Phase 2 — Future)

```
Leader/creator joins ETHOS as a featured guide
        |
        v
Leader brings their audience to ETHOS
        |
        v
Users join for access to their leader's content/community
        |
        v
User engagement and subscriber numbers grow
        |
        v
Other leaders see traction, want to join
        |
        v
More leaders apply to become guides... (flywheel accelerates)
```

**Key Metric:** Leader-driven installs per creator per month. Target: >500 for top-tier creators.

**Prerequisite:** Phase 2 community features (leader profiles, group devotionals, leader-led content). Do not build this until Phase 1 metrics validate the core product.

---

### Loop 4: Build-in-Public Loop (Pre-Launch — Active Now)

```
Imman documents building ETHOS on Instagram
        |
        v
Audience follows the journey, feels emotionally invested
        |
        v
Launch day arrives — audience is primed to download
        |
        v
High launch-day downloads create App Store momentum
        |
        v
App Store momentum drives organic discovery
        |
        v
New users who discover via App Store validate the product
        |
        v
Positive metrics attract more distribution partners... (flywheel)
```

**Key Metric:** Pre-launch email waitlist size. Target: >1,000 signups before launch day.

**Optimization Levers:**
- Post build-in-public content 2-3x per week in the lead-up to launch
- Create a landing page with email waitlist (simple — name + email + "Notify me when ETHOS launches")
- Share milestones: "We just hit 500 on the waitlist" creates social proof and FOMO

---

## 5. Pre-Launch Checklist

This checklist must be completed before the public launch of ETHOS. Every item is required unless explicitly marked as optional.

- [ ] **App Store listing ready** — Title, subtitle, keywords, description, screenshots (6), preview video (15-30s), privacy policy URL, support URL, age rating, category (Lifestyle or Reference)
- [ ] **Google Play listing ready** — Same as above, adapted for Play Store requirements (feature graphic, short description, content rating questionnaire)
- [ ] **TestFlight beta group recruited** — 50-200 testers from Imman's audience. iOS only for TestFlight; Android testers via Google Play internal testing track.
- [ ] **Beta feedback collected and addressed** — Onboarding drop-off points fixed. AI response quality validated. Paywall conversion baselined. Critical bugs resolved.
- [ ] **Imman content series planned** — 10+ posts (mix of carousels, reels, stories) building narrative from "I'm building this" to "It's here." Content calendar drafted, assets created, captions written.
- [ ] **Share templates designed** — Verse card template (branded, beautiful, Story-sized). Radar chart snapshot template. Weekly reflection card template. All exportable as images from within the app.
- [ ] **Landing page with email waitlist** — Simple, warm-branded page at ethos.app (or equivalent domain). Name + email collection. Auto-responder confirming signup. "You'll be first to know when ETHOS launches."
- [ ] **Press kit with brand assets** — Downloadable ZIP containing: ETHOS logo (SVG, PNG, dark/light variants), app icon, 6 high-resolution screenshots, founder headshot + bio, positioning statement, tagline, one-paragraph product description, contact email.
- [ ] **Instagram account for ETHOS established** — Handle secured. Profile photo (logo), bio written, link in bio to landing page. 5-10 posts published before launch day to establish visual identity and avoid the "empty profile" problem.
- [ ] **PostHog/Mixpanel analytics tracking configured** — All onboarding events firing correctly. Funnels built and verified. Session replay enabled (PostHog). User identification working (anonymous to authenticated linking).
- [ ] **RevenueCat subscription setup and tested** — Products configured in both App Store Connect and Google Play Console. Offerings set up in RevenueCat. Purchase flow tested in sandbox. Webhook to Supabase configured and tested. Restore purchases working.
- [ ] **Push notification copy and schedule ready** — Daily Anchor notification (morning, configurable time). Trial expiration reminder (2 days before end). Weekly snapshot notification (Sunday). Re-engagement notifications (Day 3 and Day 7). All copy written, reviewed, and loaded into notification scheduling system.
- [ ] **Legal review complete** — Privacy policy reviewed and published. Terms of service reviewed and published. App Store privacy nutrition labels completed. COPPA compliance verified (app targets 18+, must not collect data from under-13 users). Auto-renewal terms clearly disclosed per App Store guidelines.
- [ ] **Customer support ready** — Support email configured and monitored. FAQ page drafted covering: how to cancel subscription, how to restore purchases, how to change notification settings, how data is used. In-app "Contact Support" link in Settings.

---

## 6. Post-Launch Growth Priorities

### Month 1: Fix the Funnel

**Primary Focus:** Day 7 retention (>30%) and onboarding completion (>80%).

**Why these metrics:**
- Day 7 retention is the strongest early predictor of long-term retention. If users are not coming back after 7 days, no amount of marketing will save the product.
- Onboarding completion determines how many users even get the chance to experience the product. Every percentage point of completion improvement has a multiplicative effect on all downstream metrics.

**Actions:**
- Analyze onboarding funnel daily. Identify any screen with >15% drop-off and investigate.
- Watch PostHog session replays of users who abandon onboarding. Look for confusion, hesitation, or rage taps.
- Monitor Daily Anchor engagement: Are users opening the notification? Are they reading the full verse + explanation? Are they sharing?
- Monitor Chat Companion quality: Review a sample of 50 conversations per week. Flag any responses that are theologically inaccurate, tone-deaf, or unhelpful.
- Collect qualitative feedback via in-app feedback button and direct outreach to active users.

**Success Criteria for Month 1:**
- Onboarding completion >80%
- Day 1 retention >40%
- Day 7 retention >30%
- No critical theological accuracy issues in AI responses
- At least 50 qualitative feedback responses collected

---

### Month 2: Optimize Conversion

**Primary Focus:** Paywall conversion rate optimization. Begin A/B testing.

**Actions:**
- Run first A/B test: paywall pricing. Test current pricing ($9.99/mo, $59.99/yr) against one variant (e.g., $7.99/mo, $49.99/yr). Measure trial start rate and trial-to-paid conversion.
- Run second A/B test: paywall copy. Test current headers/subtext against 2 variants. Measure click-through on each paywall step.
- Analyze secondary paywall triggers: Which trigger converts best? Is the 4th chat attempt trigger driving upgrades? Is the blurred radar chart effective?
- Begin tracking share rate: What percentage of DAU shares a verse card or snapshot per week? If <5%, investigate friction in the share flow.
- Start collecting App Store reviews: Trigger rating prompt for users who have opened the app >5 times and viewed >5 Daily Anchors. Positive reviews improve App Store ranking.

**Success Criteria for Month 2:**
- Trial start rate >20% (of paywall views)
- Trial to paid conversion >50%
- At least one A/B test completed with statistically significant results
- Share rate measured and baselined
- App Store rating >4.5 with >50 reviews

---

### Month 3: Scale (If Metrics Are Healthy)

**Primary Focus:** Expand distribution beyond Imman's audience. Begin building independent growth channels.

**Prerequisites (must be true before scaling):**
- Day 30 retention >15%
- Paywall conversion rate stable and optimized
- Unit economics positive (LTV > CAC, even if CAC is currently $0 from organic)
- No outstanding product quality issues

**Actions:**
- **Add more content creators:** Identify 3-5 Christian creators with audiences of 10K-50K who align with the ETHOS brand and ICP. Offer free Pro access in exchange for honest usage and content creation. Do not pay for posts — authenticity is more valuable than reach.
- **Christian podcast outreach:** Identify 5-10 podcasts with audiences matching the ICP. Explore sponsorship or guest appearance opportunities for Imman.
- **Community seeding:** Share ETHOS in 10-20 Christian online communities (Facebook groups, Discord servers, Reddit). Share genuinely — "I've been using this app and it's helping my walk" — not promotional spam.
- **Consider first paid acquisition experiment:** If organic is healthy and unit economics are positive, test a small Instagram ad budget ($500-1,000) geo-targeted to Tier 1 states. Measure CAC and compare to organic cohort retention.

**Success Criteria for Month 3:**
- Total downloads >5,000
- MRR >$2,000
- At least one distribution channel beyond Imman producing measurable installs
- If paid acquisition tested: CAC < $5

---

## 7. Future Paid Acquisition (When Ready)

### When to Start Paid Acquisition

Paid acquisition should begin only when all of the following conditions are met:

1. **Organic growth validates product-market fit.** If users acquired organically (Imman's audience, viral loops, community seeding) are retaining and converting, the product works. Paid acquisition amplifies what already works — it does not fix what doesn't.

2. **Unit economics are positive.** The lifetime value (LTV) of a paying subscriber must exceed the cost to acquire them (CAC) by at least 3x for sustainable growth. With an annual plan at $59.99/yr and assuming 60% annual retention, LTV is approximately $90-100. CAC must be below $30 (ideally below $10) for healthy economics.

3. **Conversion funnel is optimized.** Spending money to drive users into an unoptimized funnel is burning cash. Onboarding completion, paywall conversion, and Day 7 retention should all be at or above target before scaling spend.

### Channel Strategy

| Channel | Priority | Why | Creative Approach |
|---------|----------|-----|-------------------|
| **Instagram Ads** | Primary | The ICP lives here. Visual format matches ETHOS brand. Precise targeting available. | Carousel ads mirroring organic content. Reel ads showing real app usage moments. |
| **TikTok** | Secondary | Growing Christian content community. Short-form video performs well for app installs. | Behind-the-scenes, transformation stories, verse-of-the-day format. |
| **Christian Podcast Sponsorships** | Secondary | High trust, captive audience, excellent for faith-based products. | Host-read ad with personal endorsement. "I've been using ETHOS in my own walk..." |
| **YouTube Pre-Roll** | Tertiary | Target pre-roll on sermon content, Christian music videos, faith-based creators. | 15-second non-skippable ad showing Daily Anchor in action. |
| **Google App Campaigns** | Tertiary | Captures high-intent search traffic ("Christian app," "daily devotional app"). | Automated creative optimization by Google. Provide assets, let the algorithm target. |

### Targeting Parameters

**Demographics:**
- Age: 18-30
- Location: Tier 1 states (Texas, Tennessee, Georgia, North Carolina, Alabama) + Christian university towns

**Interest Targeting (Instagram/Facebook):**
- Christianity
- Bible
- Church
- Faith
- Prayer
- Jesus
- Gospel
- Worship music
- Christian podcasts

**Behavioral Targeting:**
- Engaged with Christian content creators
- Downloaded other faith-based apps
- Attend church regularly (Facebook behavioral data)

**Lookalike Audiences (once you have data):**
- Lookalike of paying subscribers (highest value)
- Lookalike of users with >30 day retention (highest quality)
- Lookalike of users who share verse cards (highest viral potential)

### Creative Guidelines for Paid Ads

**Do:**
- Show the app solving a real moment of emotional or spiritual tension
- Use warm, natural lighting consistent with the ETHOS brand
- Feature real people (or Imman) in authentic settings
- Lead with the struggle, not the solution (first 3 seconds)
- Include a clear, simple CTA: "Download ETHOS — link in bio" or "Get your daily anchor"

**Don't:**
- Use aggressive sales language ("Limited time!" / "Act now!")
- Promise outcomes the app can't deliver ("This app will change your life")
- Use stock footage or inauthentic settings
- Lead with the product — lead with the problem
- Use dark or edgy aesthetics that contradict the brand

### CAC Target

- **Target CAC: < $5** (given $59.99/yr LTV on annual plan)
- **Maximum acceptable CAC: $15** (still profitable with annual retention)
- **Action threshold: If CAC exceeds $10 for two consecutive weeks, pause spend and optimize creative/targeting before resuming**
- **Monthly budget cap for first experiment: $1,000-2,000**
- **Scale criteria: If CAC < $5 and ROAS > 3x for 30 consecutive days, increase budget by 50% monthly**

---

*Last updated April 4, 2026.*
