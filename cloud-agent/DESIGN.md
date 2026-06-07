# DESIGN — How a Slide Looks and Gets Built

This is the design system you build slides against. It's not a blank canvas and not a rigid template — it's **tokens + a type/spacing scale + 2 reference layouts you adapt**. Compose freely *within* the system; a scroll of ETHOS posts should look unmistakably like one brand.

The look: **grounded, editorial, warm** — a well-set magazine page, not a glossy ad. Confident type, generous whitespace, one warm accent, nothing decorative for decoration's sake. Restraint *is* the aesthetic. ("Eggs Theory": belongs to the world he's already trying to live — never fantasy gloss.)

---

## How a slide becomes a file (read this first)

**A slide is an HTML file. That's it.** Open it in a browser; it renders at 1080×1350. Nothing sits between the HTML and what you see — no engine, no preprocessing — just HTML and one shared CSS.

Each slide:
- is a complete `<!doctype html>` document
- loads Google Fonts (Inter + Playfair Display) from the CDN
- links **one** stylesheet: `deck.css` (built once per carousel)
- contains a single `<div class="slide [hook|step]">…</div>` in its body

`deck.css` is built once for the carousel by concatenating the colorway tokens + the base layout classes, then appending any custom classes you need:

```bash
cat themes/brand-dark.css \
    templates/01-editorial-restrained/template.css \
    > deck.css
# then add any custom classes for a new layout to the bottom of deck.css
```

Swap `brand-dark.css` → `brand-light.css` for the light colorway.

> **Frame contract — owned by `template.css`.** Every slide's root element **must** be `<div class="slide [hook|step]">`. The CSS forces that element to a 1080×1350 frame with `96 90` padding and a flex column. The role class (`hook` / `step`) controls vertical alignment. **Don't override `.slide`'s `position`, `width`, `height`, or `padding` in custom CSS** — the frame is system-owned. You own what goes *inside* it.

> **Browser-view surround.** When you open a slide in a browser, you see the 1080×1350 canvas centered against a dark surround (`#161616`). That's by design — the body wrapper isn't part of the slide, just the review frame. Screenshots of `.slide` (Instagram-ready) crop the surround out automatically.

> **PNGs are the pipeline's job, not yours.** Once your deck lands in `carousels/<slug>/`, the CI pipeline (`scripts/render.js`) screenshots each `.slide` to a 1080×1350 PNG via headless Chromium and uploads it. You never render PNGs by hand — your deliverable is the HTML + `deck.css` + `metadata.json`.

---

## Color tokens

Defined in `themes/brand-{dark,light}.css` — never hardcode hex in a slide; always use the variables so a slide works in either colorway.

```css
/* dark */                          /* light */
--c-bg:          #000000;           --c-bg:          #f2ead9;   /* creme */
--c-fg:          #ffffff;           --c-fg:          #000000;
--c-accent:      #d4b668;           --c-accent:      #d4b668;   /* gold — same both */
--c-accent-text: #d4b668;           --c-accent-text: #000000;
--c-on-accent:   #000000;           --c-on-accent:   #000000;
```

Five colors total: gold `#D4B668`, black, white, creme `#F2EAD9`, and charcoal `#262626` (muted, rarely needed). No blues, no second accent.

**Gold-by-role:** gold pops on black but washes out on creme. So:
- **Decoration** (rules, dividers) → `var(--c-accent)` — gold in both colorways.
- **Readable accent** (step label, big number, the slide indicator, arrow points) → `var(--c-accent-text)` — gold on dark, **black on light**.

Use `color: var(--c-accent-text)` for any text/element that must read; `var(--c-accent)` only for decoration. (Tokens already encode this — just pick the right one.)

**When to use which colorway:** neither is the default — **alternate to keep the feed ~50/50 dark/light over time** (see `TOPICS.md`). *Dark* — premium, weighty, nocturnal. *Light* (creme) — calmer, more reflective, "morning." Both are equally on-brand.

---

## Typography

Two faces, mirroring the voice — serif = the moment that arrests, bold sans = the truth delivered flat. Don't add others.

- **Playfair Display** (`--font-heading`) — the editorial moments: hook headline, hook subhead (italic).
- **Inter** (`--font-body`) — the substance: step labels & titles (heavy, ALL-CAPS), body, points, indicator, watermark.
- **Anton** (`--font-display`) — heavy display, optional.

Each slide loads them from Google Fonts CDN:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&display=swap" rel="stylesheet">
```

### Type scale (the sizes the system uses)

| Element | Font | Weight | Size / line-height | Color | Notes |
|---|---|---|---|---|---|
| Hook headline | Playfair | 700 | 112px / 1.0 | `--c-fg` | the scroll-stopper |
| Hook subhead | Playfair *italic* | 400 | 46px / 1.25 | `--c-fg` @ .82 | faith-signal / frame |
| Accent rule | — | — | 210×5px | `--c-accent` | decoration |
| Step label | Inter | 800 | 46px | `--c-accent-text` | UPPERCASE — `STEP 1`, `TIP 1`, `QUESTION 1`, etc. |
| Step title | Inter | 800 | 58px / 1.03 | `--c-fg` | UPPERCASE |
| Step body line | Inter | 400 | 37px / 1.32 | `--c-fg` | one beat per line |
| Step point (→) | Inter | 500 | 37px | text `--c-fg`, arrow `--c-accent-text` | |
| Step closing | Inter | 600 | 39px | `--c-fg` | the sendable line |
| Slide indicator | Inter | 700 | 30px | `--c-accent-text` | letter-spaced, top-left |
| Watermark | Inter | 600 | 24px | `--c-fg` @ .38 | letter-spaced, bottom-right |

**Note on the step label:** the *class* is `step-label`. The *text* adapts to the title shape — "STEP 1" is the default, but "TIP 1" works for tip listicles, "QUESTION 1" for `3 questions only a brother can ask`, "TRAIT 1" for traits lists, "VERSE 1" for verses, etc. Match the label to the title shape so the deck reads as one piece.

---

## Spacing & layout

- **Canvas:** 1080 × 1350 (4:5). **Margins:** 96px top/bottom, 90px sides (`.slide` padding — already enforced by `template.css`).
- **Left-aligned, editorial.** One dominant element per slide; let it breathe. Crowding kills the premium feel.
- **Chrome on every slide** (don't omit): the indicator top-left, the watermark bottom-right. Both are positioned `absolute` so they sit in the same spot regardless of the slide's content.

---

## Chrome (on every slide)

```html
<div class="indicator">02 / 06</div>          <!-- top-left; NN / total -->
<div class="watermark">ETHOS</div>            <!-- bottom-right; always present -->
```
The watermark stays on the value slides too — it's what ties the brand to the value when a man goes looking for who made this. Keep it quiet (it's already faded at .38). The watermark is **brand chrome, not copy** — it's the one place the brand name appears, and it stays on every slide.

---

## The 2 reference layouts (adapt these)

The full classes live in `templates/01-editorial-restrained/template.css` (concatenated into `deck.css`). Here's the shape of each — write your real content into them. Every slide is wrapped in the standard HTML doc shell described at the top of this file.

> **These two layouts (hook, step) belong to the `01-editorial-restrained` (teaching) template.** The list format's **cover** and **list-item** layouts + their type scale ship with the `02-editorial-list` template (built next) and aren't documented here yet.

### 1. Hook
```html
<div class="slide hook">
  <div class="indicator">01 / 06</div>
  <h1 class="hook-headline">A godly man still gets angry.</h1>
  <div class="rule"></div>
  <p class="subhead">He just knows what to do with it.</p>
  <div class="watermark">ETHOS</div>
</div>
```

### 2. Step (one tip per slide — the workhorse)
```html
<div class="slide step">
  <div class="indicator">02 / 06</div>
  <div class="step-content">
    <div class="step-head">
      <span class="step-label">Step 1</span>
      <h2 class="step-title">Name it before it names you</h2>
    </div>
    <div class="step-body">
      <p>Anger is a signal, not a sin.</p>
      <p>Before you react, ask what it's pointing at.</p>
    </div>
    <ul class="step-points">
      <li>Name the thing underneath it.</li>
      <li>Then decide — don't just react.</li>
    </ul>
    <p class="step-closing">Name it before it names you.</p>
  </div>
  <div class="watermark">ETHOS</div>
</div>
```

---

## Building a carousel

1. Pick the colorway → build `deck.css` (tokens + `template.css` + any extras).
2. For each slide, write a complete HTML file (full doctype, Google Fonts link, `<link rel="stylesheet" href="deck.css">`) adapting the layout for its role (hook / one per step). Fill real copy; keep the chrome; keep within the type scale.
3. Open each HTML in a browser and review. Build `contact.html` (an iframe grid of all slides) for at-a-glance review.
4. Walk the checklist in `INSTRUCTIONS.md`.

**You may create new layouts** when a topic needs one — a full-bleed statement slide, a two-column comparison, a pull-quote. The rules when you do: use the **tokens** (never raw hex), stay on the **type scale** (don't invent sizes), keep the **margins** and the **chrome**, and use **`--c-accent-text`** for anything that must read. New arrangement, same system.

---

## Guardrails

- **1080 × 1350**, always. Content must fit the frame — watch for overflow and clipped text.
- **Tokens, not hex.** Every color via a `var(--c-*)` so the slide survives a colorway swap.
- **Two faces only** (Playfair + Inter). No new typefaces.
- **Keep the chrome** (indicator + watermark) on every slide.
- **Don't invent brand colors or break the scale.** Vary layout and content, not the system. Consistency is what makes the feed unmistakably ETHOS.
- **Don't put the frame contract anywhere but `template.css`.** If you find yourself adding 1080×1350 sizing or `.slide` padding to a per-slide style block, you're building a slide that depends on something outside the documented system. Stop.
