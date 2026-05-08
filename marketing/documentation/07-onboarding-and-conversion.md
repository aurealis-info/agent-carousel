# 07 — Onboarding Strategy & Conversion Optimization

This document defines the complete onboarding flow, paywall strategy, and conversion optimization framework for ETHOS. The onboarding is not a formality — it is the single most important experience in the user's journey. It is the storefront, the first impression, and the psychological primer that determines whether a user becomes a paying subscriber or churns before ever seeing the product's value.

---

## 1. Onboarding Philosophy

### Core Principles

Every design decision in the ETHOS onboarding is grounded in proven psychological and product principles drawn from real founder research and successful app case studies.

**Principle 1: Sunk Cost Bias — Longer Onboarding Converts Better**

Counter-intuitively, longer onboarding flows (3+ minutes) with meaningful customization steps increase conversion rates. When a user invests time answering questions and personalizing their experience, they feel psychologically invested in the outcome. Walking away after 3 minutes of effort feels like a loss. This is the Steven Cravotta / Cal AI principle: the more the user puts in, the more they want to get out.

- Target onboarding duration: 3-4 minutes (8 screens)
- Every screen must feel like it adds value, not wastes time
- The user should feel like they are building something, not filling out a form

**Principle 2: Psychological Priming — Walk Through the Problem Before the Solution**

Survey questions are not data collection — they are therapeutic confrontation. When a user selects "Anxious," "Lonely," and "Doubtful" from a list, they have just named their pain. By the time they see the paywall, they are not evaluating a product — they are evaluating a lifeline. This priming effect dramatically increases willingness to pay.

- The onboarding is structured to move from context --> pain --> aspiration --> solution
- Each screen deepens the user's emotional engagement

**Principle 3: The Storefront Analogy**

"Onboarding is your storefront. If it looks bad, people walk past no matter how good the product is inside." (Ross, Starter Story). The visual quality of the onboarding experience must match or exceed the expectations set by the marketing content that brought the user to the app. A beautiful Instagram carousel that leads to a clunky onboarding is a broken promise.

- Every screen must be visually polished — warm tones, clean typography, intentional spacing
- Animations should be smooth and purposeful, not decorative
- The aesthetic must match the warm/light brand direction, not default dark mode

**Principle 4: Progress Bars Increase Completion**

Adding a visible progress indicator increases onboarding completion rates from approximately 74% to approximately 83% (Arthur research). Users need to know how far they've come and how much is left. Uncertainty causes abandonment.

- A progress bar or step indicator appears on every screen from Screen 2 onward
- The bar should advance at a pace that feels fast in the early screens and slow near the end (front-load the easy wins)

**Principle 5: Mascot Integration Increases Trust**

A mascot or consistent visual character increases perceived warmth, reduces the feeling of talking to a cold interface, and builds brand recall (Chris Raroque, Arthur). For ETHOS, this could be an illustrated character, a recurring icon (e.g., an anchor), or a consistent visual motif that appears on every screen.

- The ETHOS anchor icon or a warm illustrated element should appear on every onboarding screen
- It should feel like a companion guiding you, not a brand logo staring at you

**Principle 6: Never Require Login During Onboarding**

Every login wall during onboarding is a conversion cliff. Users should be able to complete the entire onboarding flow, see their personalized plan, and even hit the paywall without creating an account. Store all onboarding data locally using Expo's AsyncStorage or SecureStore. Prompt for account creation after the user has experienced value — not before.

- Onboarding data is stored locally on device
- Account creation happens post-paywall (after the user has decided to stay)
- If the user subscribes, account creation is part of the subscription flow
- If the user enters free tier, account creation is prompted on Day 2 or 3

**Principle 7: One Piece of Information Per Screen**

Cognitive overload kills completion. Every screen should ask for exactly one thing. If you are tempted to combine two questions onto one screen, split them. The slight increase in screen count is more than offset by the decrease in cognitive friction.

- One question, one selection, one input per screen
- Large tap targets, generous whitespace, minimal text
- The user should be able to process each screen in under 5 seconds

---

## 2. ETHOS 8-Screen Onboarding Flow

### Screen 1 — Welcome

**Visual:** Full-screen warm gradient background (soft gold to cream). ETHOS logo centered. Tagline below: "For the person you're becoming." Single large CTA button: "Begin."

**Content:**
- ETHOS logo (anchor icon + wordmark)
- Tagline: "For the person you're becoming."
- CTA: "Begin"
- No other text, no sign-in link, no skip option

**Psychological Technique: Reaffirming the Decision**

The user just downloaded the app. They made a choice. Screen 1's job is to validate that choice and set a warm, inviting tone. "Begin" is intentionally chosen over "Get Started" or "Sign Up" — it implies the start of a journey, not a transaction. The tagline reminds them why they're here: transformation.

**Technical Notes:**
- Animate the logo with a subtle fade-in (300ms)
- CTA button should have a gentle pulse animation to draw attention
- No navigation bar, no back button — this is the entry point

---

### Screen 2 — Life Context

**Visual:** Clean card layout with 5 selectable options. Progress bar appears (1/7).

**Content:**
- Header: "Where are you right now?"
- Subtext: "This helps us meet you where you are."
- Options (single select, pill-shaped buttons):
  - Student
  - Early career
  - Building something
  - In transition
  - Figuring it out

**Psychological Technique: Segmentation + First Commitment Tap**

This is the user's first interaction beyond "Begin." It is intentionally easy — a single tap from five clear options. The question is non-threatening and non-personal. Its purpose is twofold: (1) segment the user for content personalization, and (2) establish the tapping behavior that carries through the rest of the flow. The first tap is the hardest. After that, momentum carries.

**Technical Notes:**
- Store selection locally (AsyncStorage key: `onboarding_life_context`)
- Selection immediately advances to next screen (no separate "Next" button needed, but include one as fallback)
- "Figuring it out" is the catch-all — ensures no user feels excluded

---

### Screen 3 — Core Struggles

**Visual:** Grid layout with selectable chips/tags. Multi-select with visual feedback (chip fills with color on selection). Progress bar (2/7).

**Content:**
- Header: "What do you carry?"
- Subtext: "Select all that resonate. Be honest — this stays between you and God."
- Options (multi-select, 3-7 selections required):
  - Tempted
  - Lustful
  - Angry
  - Anxious
  - Doubtful
  - Prideful
  - Jealous
  - Work/School pressure
  - Relationship stress
  - Family tension
  - Loneliness
  - Financial pressure
  - Health concerns
- CTA: "Continue" (activates after 3 selections)

**Psychological Technique: Intensity Laddering**

This is the most important screen in the onboarding. The user is being asked to name their pain — not in a clinical intake form, but in a spiritually safe container ("this stays between you and God"). The multi-select format forces them to confront the breadth of their struggle. By selecting 3-7 items, they are psychologically priming themselves to receive a solution. The order of options is deliberate: "Tempted" and "Lustful" appear first because they are the struggles most likely to create urgency and emotional investment.

**Technical Notes:**
- Store selections locally (AsyncStorage key: `onboarding_struggles`)
- Minimum 3, maximum 7 selections enforced with UI feedback
- Chips should animate on selection (scale + color transition, 150ms)
- Consider randomizing order after the first two to reduce selection bias

---

### Screen 4 — Growth Axes

**Visual:** Similar chip/tag layout to Screen 3 but with a different color treatment to signal progression. Progress bar (3/7).

**Content:**
- Header: "What areas of your walk do you want to grow in?"
- Subtext: "Pick 3-5. These become your growth axes."
- Options (multi-select, 3-5 selections):
  - Discipline
  - Self-Control
  - Scripture
  - Purpose
  - Integrity
  - Gratitude
  - Courage
- CTA: "Continue" (activates after 3 selections)

**Psychological Technique: Investment Deepening**

The user has named their pain (Screen 3). Now they are naming their aspiration. This shift from "what weighs you down" to "what you want to grow in" creates an emotional arc within the onboarding itself. The selected growth axes will populate the radar chart in the app — so the user is literally building a personal growth framework. This is not data collection; it is identity construction.

**Technical Notes:**
- Store selections locally (AsyncStorage key: `onboarding_growth_axes`)
- These selections directly map to the radar chart axes displayed in the app
- Minimum 3, maximum 5 selections enforced
- Use a slightly different color palette from Screen 3 to signal progression (e.g., move from warm amber to soft sage)

---

### Screen 5 — Identity Anchor

**Visual:** Full-width text input field with a warm placeholder. Soft keyboard opens on screen load. Progress bar (4/7).

**Content:**
- Header: "What kind of person are you becoming?"
- Subtext: "Write it down. Make it real."
- Input placeholder (grayed): "A man who leads with integrity..."
- Secondary CTA: "Skip for now" (small, below the input)
- Primary CTA: "Continue" (activates when input has 5+ characters)

**Psychological Technique: Commitment Psychology**

This is the peak investment moment. The user is asked to articulate their aspirational identity in their own words. Writing something down — even a few words — activates a commitment mechanism that is qualitatively different from tapping a pre-set option. The user has now co-created their ETHOS experience. They have written their aspiration. Walking away from the app now means walking away from a statement they made to themselves. The "Skip for now" option is included to prevent drop-off, but the design should encourage completion (placeholder text, prominent input field, warm encouragement).

**Technical Notes:**
- Store input locally (AsyncStorage key: `onboarding_identity_anchor`)
- Character minimum of 5 to activate CTA (prevents empty submissions)
- Auto-focus the input field on screen mount
- If skipped, store `null` and surface the prompt again on Day 3 as a profile completion nudge
- Keyboard should push the CTA button above the fold (KeyboardAvoidingView)

---

### Screen 6 — Notification Permission (Primed)

**Visual:** Custom illustration of a phone receiving a verse notification at sunrise. Warm colors, golden light. Progress bar (5/7).

**Content:**
- Header: "Your anchor is delivered every morning."
- Subtext: "Allow notifications so you never miss it."
- Animated illustration: phone screen showing a Daily Anchor notification with a sunrise background
- Primary CTA: "Allow Notifications" (triggers system dialog)
- Secondary CTA: "Not now" (small, below)

**Psychological Technique: Permission Priming**

Never show the system notification dialog cold. A custom priming screen that explains the value of notifications before requesting permission increases opt-in rates from approximately 25% to 50%+. The user sees why notifications matter (their daily anchor, delivered every morning) before the system dialog appears. If they tap "Allow Notifications," the native iOS/Android permission dialog fires immediately. If they tap "Not now," the system dialog is deferred — and can be re-prompted later with a different value proposition.

**Technical Notes:**
- Do NOT trigger the system notification dialog on screen mount
- Only trigger it when the user taps "Allow Notifications"
- If user taps "Not now," store `notification_primed: false` and schedule a re-prompt at a later engagement point (e.g., after first Daily Anchor is viewed)
- Use `expo-notifications` for permission handling
- Track priming screen impressions vs. system dialog triggers vs. opt-in rate

---

### Screen 7 — Your Plan Is Ready

**Visual:** Animated reveal of the user's personalized profile. Mini radar chart outline built from their selected growth axes. Identity anchor statement displayed below. Progress bar (6/7).

**Content:**
- Header: "Your plan is ready."
- Subtext: "Built for the person you're becoming."
- Visual elements:
  - Mini radar chart showing the selected growth axes as labeled points (axes are labeled but chart is empty — it fills as they use the app)
  - Identity anchor statement (if provided on Screen 5) displayed in a styled card
  - Selected struggles shown as small tags below
- CTA: "Let's go"

**Psychological Technique: Endowed Progress Effect**

The user has invested 3+ minutes answering questions. Screen 7 pays off that investment by showing them that something was built for them. The radar chart, the identity statement, the struggle tags — all of it is their data, reflected back in a beautiful, personalized format. This creates the endowed progress effect: the user feels they have already started their journey. The empty radar chart implies progress yet to be made — and the app is the tool that fills it. Walking away now means walking away from a plan that was made specifically for them.

**Technical Notes:**
- Animate the radar chart outline drawing itself (SVG path animation, 800ms)
- Pull all data from local storage (growth axes, identity anchor, struggles)
- If identity anchor was skipped, omit that card and adjust layout
- The radar chart here is a preview — the full interactive version appears in the Profile tab

---

### Screen 8 — Paywall (3-Step Primer)

The paywall is not a single screen — it is a 3-step psychological sequence designed to minimize perceived risk and maximize trial starts.

**Step 1: "We want you to try ETHOS for free"**

**Visual:** Warm, inviting screen. No pricing visible. ETHOS logo. Simple message.

**Content:**
- Header: "We want you to try ETHOS for free."
- Subtext: "Experience your Daily Anchor and Chat Companion with no commitment."
- CTA: "Try now for $0"
- No pricing details, no plan comparison, no fine print

**Psychological Technique:** The first step removes all commercial friction. The user is not being asked to buy anything. They are being asked to try something for free. "$0" is explicit — it removes ambiguity. This step exists solely to get a "yes" tap before any money is discussed.

---

**Step 2: "We'll send you a reminder"**

**Visual:** Same warm aesthetic. Calendar icon or notification illustration.

**Content:**
- Header: "We'll send you a reminder before your free trial ends."
- Subtext: "You won't be charged anything today. We'll notify you 2 days before your trial expires."
- CTA: "Continue"

**Psychological Technique:** This step addresses the #1 objection to free trials: "I'll forget to cancel and get charged." By explicitly promising a reminder, ETHOS removes the perceived risk of the trial. The user now feels safe to proceed because they believe they are in control.

---

**Step 3: Actual Paywall with Pricing**

**Visual:** Clean pricing comparison. Annual plan pre-selected and visually highlighted with a "Save 50%" badge. Warm background. Restore Purchases link in fine print.

**Content:**
- Header: "Choose your plan."
- Plan options:

  **Monthly — $9.99/mo**
  - No free trial
  - Billed monthly
  - "Full access to Daily Anchor and Chat Companion"
  - Purpose: Anchor price. Makes the annual plan look like a deal.

  **Annual — $59.99/yr** (pre-selected, highlighted)
  - 7-day free trial included
  - Billed annually after trial
  - "Save 50% — that's just $4.99/mo"
  - Badge: "MOST POPULAR" or "BEST VALUE"

- CTA: "Start Free Trial" (for annual) or "Subscribe" (for monthly)
- Secondary CTA: "Maybe Later" (small, below pricing — dismisses to free tier)
- Fine print: "Restore Purchases" link, terms of service, auto-renewal disclosure

**Psychological Technique:** The 3-step primer (Cal AI model) progressively reduces perceived risk. By step 3, the user has already said "yes" twice to free/low-commitment offers. The pricing screen feels like a natural next step, not a sudden ask. The annual plan is pre-selected and highlighted because: (1) the 7-day trial lowers the barrier, (2) "Save 50%" triggers loss aversion, and (3) the monthly plan's lack of trial makes it feel less generous by comparison. This nudge architecture maximizes annual subscriptions, which dramatically improves LTV.

**Technical Notes:**
- Implement all three steps as a single component with internal state management
- Use RevenueCat for all subscription logic: product fetching, purchase handling, receipt validation
- Track conversion through each step: Step 1 view --> Step 1 tap --> Step 2 view --> Step 2 tap --> Step 3 view --> Plan selection --> Purchase attempt --> Purchase success/failure
- "Maybe Later" stores `paywall_dismissed: true` and enters the user into the free tier
- "Restore Purchases" calls RevenueCat's restore method

---

## 3. Paywall Strategy

### Pricing Architecture

| Plan | Price | Trial | Billing | Purpose |
|------|-------|-------|---------|---------|
| Monthly | $9.99/mo | None | Monthly recurring | Anchor price. Makes annual look like a steal. Catches impulse buyers who don't want annual commitment. |
| Annual | $59.99/yr ($4.99/mo effective) | 7-day free trial | Annual recurring | Primary conversion target. Trial lowers barrier. 50% savings vs. monthly drives selection. Maximizes upfront LTV. |

### Why Annual-Only Trial

Offering the free trial exclusively on the annual plan is a deliberate strategic choice:

1. **Maximizes LTV per trial start.** If a user converts from a trial, they pay $59.99 upfront instead of $9.99. This is 6x the immediate revenue per conversion.
2. **Reduces monthly churn.** Annual subscribers are locked in for 12 months. Monthly subscribers churn at ~10-15%/month in consumer apps. Annual plans smooth revenue and improve retention metrics.
3. **Creates urgency on the monthly plan.** Without a trial, the monthly plan feels like a bigger commitment — which pushes users toward the annual plan with its "try first" safety net.

### RevenueCat Configuration

- **Products:** Two products in App Store Connect and Google Play Console — `ethos_monthly` ($9.99/mo) and `ethos_annual` ($59.99/yr with 7-day trial)
- **Offerings:** Single offering with both products. Annual is the "default" (pre-selected in UI).
- **Billing grace period:** Enabled. 16 days for annual, 6 days for monthly. This gives users time to fix payment issues before losing access — reducing involuntary churn.
- **Subscription status:** Check `CustomerInfo` on app launch to gate Pro features.
- **Receipt validation:** Server-side via RevenueCat webhook to Supabase Edge Function. Never trust client-side receipt validation alone.
- **A/B testing:** Use RevenueCat's Experiments feature to test paywall variants (pricing, copy, number of primer steps, trial length).

### Free Tier Boundaries

| Feature | Free | Pro |
|---------|------|-----|
| Daily Anchor | Unlimited | Unlimited |
| Chat Companion | 3 conversations total | Unlimited |
| Radar Chart | Blurred after Week 1 | Full access |
| Verse Saving | No | Yes |
| Weekly Snapshot | No | Yes |
| Share Cards | Basic | Branded + custom |

The free tier is intentionally generous on the Daily Anchor (the habit-forming hook) and restrictive on Chat (the high-value, high-cost feature). This ensures free users still get daily value (reducing churn) while feeling the friction that motivates upgrade.

---

## 4. Secondary Paywall Triggers

The onboarding paywall is the primary conversion point, but not the only one. Secondary triggers catch users who dismissed the initial paywall but have since experienced enough value to reconsider.

| Trigger | When It Fires | UX Treatment | Expected Conversion Share |
|---------|---------------|--------------|--------------------------|
| **End of onboarding (3-step primer)** | First app open, after Screen 7 | Full 3-step primer sequence | ~50% of all conversions |
| **4th chat attempt** | After 3 free conversations used (lifetime) | Soft blocker: "You've used your 3 free conversations. Unlock unlimited chat with Pro." Shows pricing. | ~30% of all conversions |
| **Blurred radar chart tap** | After Week 1, when user taps their radar chart | Overlay: "See your full growth journey. Upgrade to Pro." Shows pricing. | ~15% of all conversions |
| **"Upgrade" in Profile settings** | Anytime the user navigates to Profile > Upgrade | Standard pricing screen (no primer needed — user initiated) | ~5% of all conversions |

### Design Principles for Secondary Paywalls:
- Never feel punitive. The tone is always "here's what's waiting for you," not "you can't have this."
- Always show a glimpse of the gated content (blurred radar chart, partial chat response) before the paywall. The user must feel the value before being asked to pay.
- Every secondary paywall has a "Maybe Later" escape. Never trap the user.
- Track each trigger's conversion rate independently. If a trigger converts at <1%, consider removing it or changing the timing.

---

## 5. Visual Design for Onboarding

### Aesthetic Direction

The ETHOS onboarding must reflect the warm, light aesthetic pivot — not dark mode. The brand direction is intentionally warm, inviting, and aspirational. Think morning light, not midnight ambition.

**Reference:** Glorify's onboarding is the closest existing reference to the target feel:
- Warm tones (soft gold, cream, light sage)
- Gold accent color for CTAs and highlights
- Seed/plant growth metaphor (growth, patience, cultivation)
- Light backgrounds (never pure white — always warm off-white or cream)
- Generous whitespace
- Rounded corners, soft shadows, no hard edges

### Specific Design Specifications

**Typography:**
- Headers: Bold, 24-28pt, warm dark brown or deep charcoal (never pure black)
- Subtext: Regular, 14-16pt, medium gray
- CTA buttons: Semi-bold, 16-18pt, white on gold/warm accent color

**Color Palette:**
- Background: Warm cream (#FFF8F0 or similar)
- Primary accent: Soft gold (#D4A853 or similar)
- Secondary accent: Muted sage (#8FA68A or similar)
- Text: Deep charcoal (#2C2C2C)
- Subtext: Medium warm gray (#7A7A7A)

**Spacing:**
- Minimum 24px padding on all sides
- 16px between selectable chips/options
- 32px between header text and interactive elements
- 48px between interactive elements and CTA button

**Progress Bar:**
- Appears from Screen 2 onward
- Thin (4px height), warm gold fill color
- Positioned at the very top of the screen, below the status bar
- Smooth animation between steps (300ms transition)

**Animations:**
- Screen transitions: Horizontal slide (left to right), 300ms duration
- Selection feedback: Scale up 1.05x + color fill, 150ms
- Radar chart (Screen 7): SVG path draw animation, 800ms
- CTA button: Gentle pulse when active (opacity 0.8 --> 1.0, 1000ms loop)

---

## 6. Conversion Metrics & Tracking

### Target Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Onboarding completion** | >80% | Industry benchmark for well-designed 8-screen flows with progress bars. Below 80% indicates UX friction. |
| **Notification opt-in (with priming)** | >50% | Priming doubles cold opt-in rates (~25%). Below 50% suggests the priming screen isn't compelling enough. |
| **Trial start rate (paywall views)** | >20% | Of users who see the paywall, 20%+ should start a trial. The 3-step primer is designed to exceed this. |
| **Trial to paid conversion** | >50% | Users who start a 7-day trial and do not cancel. Below 50% indicates the trial experience isn't delivering enough value. |
| **Day 1 retention** | >40% | User returns the day after first open. The Daily Anchor notification is the primary D1 retention mechanism. |
| **Day 7 retention** | >30% | User returns 7 days after first open. Indicates the daily habit is forming. |
| **Day 30 retention** | >15% | User returns 30 days after first open. Indicates sustained value delivery. |

### Tracking Implementation

**Analytics Tool: PostHog or Mixpanel**

Both platforms support the step-by-step funnel tracking required for onboarding optimization. Selection criteria:

| Criteria | PostHog | Mixpanel |
|----------|---------|---------|
| Pricing | Free tier generous for early stage | Free tier adequate |
| Funnel analysis | Strong | Strong |
| Session replay | Yes (valuable for debugging onboarding drop-off) | Limited |
| Self-hosted option | Yes (data privacy advantage) | No |
| React Native SDK | Yes | Yes |

Recommendation: Start with PostHog for the session replay capability. Being able to watch actual user sessions through the onboarding flow is invaluable for identifying friction points.

**Event Tracking Schema:**

Every screen in the onboarding flow emits events:

```
onboarding_started               -- Screen 1 loaded
onboarding_screen_viewed         -- {screen_number, screen_name}
onboarding_life_context_selected -- {selection}
onboarding_struggles_selected    -- {selections[], count}
onboarding_growth_axes_selected  -- {selections[], count}
onboarding_identity_anchor       -- {provided: true/false, length}
onboarding_notification_primed   -- {action: "allow" | "not_now"}
onboarding_notification_system   -- {granted: true/false}
onboarding_plan_viewed           -- Screen 7
onboarding_paywall_step          -- {step: 1|2|3}
onboarding_plan_selected         -- {plan: "monthly" | "annual"}
onboarding_purchase_attempted    -- {plan, price}
onboarding_purchase_completed    -- {plan, price, trial: true/false}
onboarding_purchase_failed       -- {plan, error}
onboarding_paywall_dismissed     -- "Maybe Later" tapped
onboarding_completed             -- User enters the app (free or paid)
```

**RevenueCat Analytics:**

RevenueCat provides subscription-specific analytics that complement the product analytics tool:

- Monthly Recurring Revenue (MRR)
- Active subscribers by plan
- Trial start rate and trial conversion rate
- Churn rate by plan and cohort
- Revenue per user
- Subscription status changes (new, renewal, cancellation, billing issue)

### A/B Testing Priority

Test these variables first, in order of expected impact:

1. **Paywall pricing** — Test $7.99/mo vs. $9.99/mo vs. $12.99/mo. Test $49.99/yr vs. $59.99/yr vs. $69.99/yr. Price sensitivity varies dramatically by audience.
2. **Number of onboarding screens** — Test 6 screens vs. 8 screens vs. 10 screens. More screens = more investment, but also more drop-off risk.
3. **Copy variants** — Test different headers and subtext on Screens 3, 5, and the paywall. Small copy changes can move conversion 10-20%.
4. **Trial length** — Test 3-day vs. 7-day vs. 14-day trial on the annual plan.
5. **Paywall primer steps** — Test 2-step vs. 3-step vs. direct paywall (no primer).

---

## 7. Common Pitfalls

### Pitfall 1: Login Wall During Onboarding

**The mistake:** Requiring email/password creation before the user can proceed through onboarding.

**Why it kills conversion:** Every form field is friction. Email + password is two form fields + a mental decision ("do I trust this app with my email?"). This is the single most common reason for onboarding abandonment in mobile apps.

**The fix:** Store all onboarding data locally using Expo's AsyncStorage or SecureStore. The user completes the entire onboarding, hits the paywall, and enters the app without ever creating an account. Account creation is prompted later — after the user has experienced value — as a data backup / cross-device sync feature, not a gate.

### Pitfall 2: Privacy Policy Mismatch

**The mistake:** Collecting personal data during onboarding (struggles, identity statements) without proper privacy disclosures, or having a privacy policy that doesn't match what data is actually collected.

**Why it's dangerous:** Apple's App Store Review Guidelines (Section 5.1.1) require that apps clearly describe what data they collect and how it's used. A mismatch between the privacy policy and actual data collection can result in App Store rejection — which can delay launch by days or weeks.

**The fix:** Before submitting to the App Store, audit every piece of data collected during onboarding and ensure it is listed in: (1) the App Store privacy nutrition label, (2) the in-app privacy policy, and (3) any GDPR/CCPA disclosures if applicable. Be especially careful with the identity anchor free-text input and the struggle selections — these are sensitive personal data.

### Pitfall 3: Skipping the Primed Notification Screen

**The mistake:** Triggering the iOS/Android system notification dialog without a custom priming screen first.

**Why it halves opt-in rate:** When the system dialog appears cold (without context), users reflexively tap "Don't Allow." This is a one-shot opportunity on iOS — once denied, the app can only redirect to Settings, which almost no user does. A priming screen that explains the value of notifications before the system dialog appears doubles opt-in rates from ~25% to 50%+.

**The fix:** Always show Screen 6 (the custom priming screen) before triggering the system dialog. Only call `Notifications.requestPermissionsAsync()` after the user taps "Allow Notifications" on the priming screen. If they tap "Not now," defer the system dialog entirely and re-prompt at a later engagement point.

### Pitfall 4: Punitive Paywall Tone

**The mistake:** Making the paywall feel like a punishment for not paying. Language like "You've been blocked" or "Upgrade to continue" or showing a hard lock icon creates a negative emotional association.

**Why it hurts conversion:** The user's last emotional impression before making a purchase decision should be positive and aspirational, not frustrated and constrained. A paywall that feels punitive creates resentment, not desire.

**The fix:** Frame every paywall interaction as an invitation, not a restriction. Instead of "You've used your free chats," try "You've had 3 great conversations today. Unlock unlimited chats to keep going." Instead of a lock icon, use an open door or a gentle gradient that suggests there's more waiting. The tone should always be: "Here's what's available to you" — not "Here's what you can't have."

---

*Last updated April 4, 2026.*
