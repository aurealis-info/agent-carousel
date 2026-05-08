# ETHOS — Marketing Documentation Index

> Comprehensive marketing strategy and brand documentation for ETHOS, a biblical companion app for young Christian men (18–25) caught between two failed versions of modern manhood — and called to a third.
>
> **Tagline:** "Become The Man God Intended."

---

## Document Map

| # | Document | Description |
|---|----------|-------------|
| 01 | [ICP & Audience](01-icp-and-audience.md) | Ideal Customer Profile, the ICP tension (Matthew's correction), primary and secondary audiences, persona cards, validation checklist |
| 02 | [Brand Foundation](02-brand-foundation.md) | Brand Stack (purpose, vision, mission, values), personality & archetypes, brand promise & tagline, brand architecture (Aurealis → ETHOS → Imman.faith) |
| 03 | [Visual Identity](03-visual-identity.md) | Dark + gold ("Obsidian & Gold") aesthetic, color palette, typography, imagery guidelines, anti-patterns |
| 04 | [Positioning & Competitive Landscape](04-positioning-and-competitive-landscape.md) | April Dunford positioning framework, competitive matrix (YouVersion, Glorify, Hallow, Pray.com), 2x2 positioning map, USP, differentiators |
| 05 | [Messaging & Voice](05-messaging-and-voice.md) | Voice attributes (Direct, Grounded, Masculine, Honest), tone variations by context, messaging hierarchy, vocabulary bank, copy examples by surface |
| 06 | [Content Strategy](06-content-strategy.md) | Content pillars, topic audit & ICP realignment, content formats (carousels, reels, stories), calendar framework, production workflow |
| 07 | [Onboarding & Conversion](07-onboarding-and-conversion.md) | 8-screen onboarding flow with psychological techniques, 3-step paywall primer, RevenueCat configuration, conversion metrics & tracking |
| 08 | [GTM & Distribution](08-gtm-and-distribution.md) | Launch phases (beta → App Store → scale), distribution channels, geographic strategy, growth loops, pre-launch checklist |
| 09 | [Monetization Strategy](09-monetization-strategy.md) | Pricing ($9.99/mo, $59.99/yr), free vs. Pro feature table, paywall triggers, Phase 2 Leaders premium tier, unit economics |
| 10 | [Creator & Influencer Playbook](10-creator-and-influencer-playbook.md) | Imman (content co-founder) profile & boundaries, creator roster, founding leader recruitment (Phase 2), partnership outreach |

---

## Substantive & Tactical Execution Layer

The strategic docs above define *what* and *why*. The `marketing/guidelines/` folder defines the **substantive layer** (what we say and how we say it) and the **format-specific tactical layer** (how we ship it).

| Doc | Description |
|---|---|
| [General Content Guidelines](../guidelines/GENERAL_CONTENT_GUIDELINES) | The substantive layer — audience reality (the 22yo Christian man caught between feral and domesticated), the foundation (Christ-imparted righteousness, not earned), the 10 substantive themes (governed · kills what's killing him · works · tells truth · strong AND tender · sacrificial leadership · planted in real men · chases God not wife · fights phone · walks humbly), voice characteristics (older brother across the table), voice anti-patterns. Applies across every format. |
| [Carousel Guidelines](../guidelines/CAROUSEL/guidelines.md) | Carousel-specific execution — intention (real value first), 5-slide chassis, format archetypes (Listicle / Mistakes List / Uncomfortable Questions / Problem-Solution / Cultural Lens), hook engineering, copy psychology, engagement mechanics, batched production, success metrics. |
| [Research](../guidelines/Research/) | The bedrock essays the substantive layer was synthesized from — long-form treatments of "what a righteous man in 2026 looks like for a 22yo Christian guy." Return here when in doubt about substance, voice, or how a topic should land. |

Reels, Stories, and Static-post format guidelines will be added under `marketing/guidelines/` as those formats are codified.

Source library: `marketing/Inspiration_Reels/{handle}_{slug}/` — analyzed reference posts from creators in the same niche.

---

## Recommended Reading Order

**Start here — everything depends on these:**
1. **01 — ICP & Audience** — Who we're building for (and the critical ICP correction)
2. **02 — Brand Foundation** — Who we are as a brand
3. **05 — Messaging & Voice** — How we communicate

**Then the strategic layer:**
4. **03 — Visual Identity** — How we look
5. **04 — Positioning & Competitive Landscape** — Where we sit in the market

**Then tactical execution:**
6. **06 — Content Strategy** — What we post and when
7. **07 — Onboarding & Conversion** — How we convert users
8. **09 — Monetization Strategy** — How we make money

**Then distribution and partnerships:**
9. **08 — GTM & Distribution** — How we launch and grow
10. **10 — Creator & Influencer Playbook** — Who we partner with

---

## Source Material Reference

All documentation was built from the following sources:

| Source | Location | Key Content |
|--------|----------|-------------|
| MVP Documentation | `ethosknowledge.../mvp...md` | Product overview, user flows, data models, tech stack |
| MVP Feature Spec (Final) | `ethosknowledge.../MVP FEATURE SPEC — FINAL...md` | Onboarding, Daily Anchor, Chat, Radar Chart, Paywall, Push Notifications |
| Target Audience Feedback | `ethosknowledge.../target audience feedback...md` | Matthew's ICP correction — the most critical strategic input |
| Phase 2 Features | `ethosknowledge.../PHASE 2/` | Faith Journey (skill tree), Leaders Feature |
| Leaders Feature | `ethosknowledge.../Leaders Feature...md` | Premium tier, leader recruitment, rev share model |
| Faith Journey Feature | `ethosknowledge.../FAITH JOURNEY...md` | Duolingo-style paths tied to radar chart axes |
| Content Co-Founder | `ethosknowledge.../Content Co-Founder...md` | Imman.faith profile (Enoch Immanuel Wang) |
| Creators List | `ethosknowledge.../Creators...md` | Potential creator partners |
| Marketing Notes | `ethosknowledge.../MARKETING...md` | Raw content ideas, reference accounts, hooks |
| Social Media Topics | `ethosknowledge.../TOPICS for ETHOS posts...md` | 20 "man of God" content topics |
| Competitive Landscape | `ethosknowledge.../Competitive Landscape...md` | Initial competitor notes |
| App Design (April 4) | `marketing/APPDESIGN/ETHOSdesign_April4.pdf` | Current high-fidelity mockups |
| Onboarding Research | `marketing/ONBOARDING/notebookllmknowledge_onboarding` | Founder research on onboarding psychology |
| Onboarding Reference | `marketing/ONBOARDING/example_images/onboarding1.png` | Glorify onboarding (warm aesthetic reference) |
| IG Carousel Skill | `marketing/aurealis_marketing_skills_simon/ig-carousel-creator/` | 5-slide carousel formula |
| Brand-Building Skill | `~/.claude/skills/brand-building/` | Positioning, voice, visual identity, brand strategy frameworks |
| UI/UX Pro Max Skill | `.agents/skills/ui-ux-pro-max/` | 50+ styles, 161 color palettes, 57 font pairings, 99 UX guidelines, 25 chart types across 10 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, HTML/CSS). Design intelligence for web and mobile UI. |
| Frontend Design Skill | `.agents/skills/frontend-design/` | Anthropic's official skill for distinctive, production-grade frontend interfaces. Builds web components, pages, dashboards, landing pages with high design quality — avoids generic AI aesthetics. |
| Design Taste Frontend | `.agents/skills/design-taste-frontend/` | Taste-skill pack: design-forward frontend with strong visual taste |
| High-End Visual Design | `.agents/skills/high-end-visual-design/` | Taste-skill pack: premium, high-end visual design patterns |
| Industrial Brutalist UI | `.agents/skills/industrial-brutalist-ui/` | Taste-skill pack: raw, industrial brutalist UI aesthetic |
| Minimalist UI | `.agents/skills/minimalist-ui/` | Taste-skill pack: clean minimalist interface design |
| Stitch Design Taste | `.agents/skills/stitch-design-taste/` | Taste-skill pack: stitching design taste into existing projects |
| Redesign Existing Projects | `.agents/skills/redesign-existing-projects/` | Taste-skill pack: redesigning existing projects with better aesthetics |
| Full Output Enforcement | `.agents/skills/full-output-enforcement/` | Taste-skill pack: enforces complete code output (no truncation) |
| shadcn/ui | `.agents/skills/shadcn-ui/` | Complete shadcn/ui component library patterns — installation, config, accessible React components, forms with React Hook Form + Zod, Tailwind theming |
| UI Animation | `.agents/skills/ui-animation/` | Motion and animation — springs, gestures, drag interactions, clip-path reveals, easing, timing, Framer Motion, CSS transitions |
| Web Design Guidelines | `.agents/skills/web-design-guidelines/` | Vercel's Web Interface Guidelines compliance — UI review, accessibility audits, UX checks, design best practices |
| Motion Designer | `.agents/skills/motion-designer/` | Visual motion systems, animation specs, guidance on crafting meaningful movement |
| Stitch: Design MD | `.agents/skills/design-md/` | Google Stitch — synthesize semantic design systems into DESIGN.md files |
| Stitch: Enhance Prompt | `.agents/skills/enhance-prompt/` | Google Stitch — transform vague UI ideas into polished, optimized prompts |
| Stitch: React Components | `.agents/skills/react-components/` | Google Stitch — convert designs into modular Vite + React components |
| Stitch: Remotion | `.agents/skills/remotion/` | Google Stitch — generate walkthrough videos with smooth transitions and overlays |
| Stitch: Design | `.agents/skills/stitch-design/` | Google Stitch — unified entry point for prompt enhancement, design system, and screen generation |
| Stitch: Loop | `.agents/skills/stitch-loop/` | Google Stitch — iteratively build websites with autonomous baton-passing loop |
| Stitch: Taste Design | `.agents/skills/taste-design/` | Google Stitch — premium anti-generic design standards (typography, color, motion) |

---

## Key Strategic Decisions

| Decision | Status | Details |
|----------|--------|---------|
| **Pricing** | Confirmed | $9.99/mo (no trial) \| $59.99/yr (7-day free trial, pre-selected) |
| **Primary ICP** | Confirmed | Young Christian men 18–25 caught between feral (Tate-coded) and domesticated (porn-fed soft) versions of manhood |
| **Visual direction** | Confirmed | Dark + gold ("Obsidian & Gold"). Reversed the earlier "warm/light pivot" recommendation — the masculine ICP correction held, and the visual followed it |
| **Substantive layer** | Codified | `marketing/guidelines/GENERAL_CONTENT_GUIDELINES` — the feral/domesticated/governed framework, the Christ-imparted righteousness foundation, the 10 themes, voice direction |
| **Imman's role** | Defined | Distribution partner, NOT the brand identity |
| **Daily Anchor format** | Confirmed | 1 unified card (verse + explanation + prayer), not 3 separate cards |
| **Chat free limit** | Confirmed | 3 conversations for free tier |
| **Radar chart** | Confirmed | Premium feature, blurred preview for free users after week 1 |

---

## Open Questions & Decisions Pending

- [ ] Content topic realignment — re-audit the 20 "man of God" topics through the 10-theme matrix in `GENERAL_CONTENT_GUIDELINES`
- [ ] Creator vetting — @zaneecarter, @ekevvscrusade, @danielxkwon, @thelogankoch need evaluation; vetting checklist now includes Christ-imparted-righteousness alignment
- [ ] Leaders feature pricing — $29/mo premium tier vs. other options
- [ ] Geographic targeting — Texas/Bible Belt focus for initial marketing spend
- [ ] Reels / Stories / Static format guidelines — codify under `marketing/guidelines/` once we've earned reps

---

*Last updated: 2026-05-07*
