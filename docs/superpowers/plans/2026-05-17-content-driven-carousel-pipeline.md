# Content-Driven Carousel Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current `strategist → designer → critic` pipeline with `angles → angle_critic → script+style writer → designer → visual critic` (with bounded revision loop), where brand identity is encoded as prose context that the writer reads to derive per-carousel palette, type pairing, and per-slide layout intent. End state: one live run on `brands/_test/` and one on `brands/ethos/`, both producing carousels via the new pipeline.

**Architecture:** Five-component pipeline, all Claude Opus calls. Hierarchical sampling (10 cheap angles → critic picks 1 → 1 rich writer call). Visual critic loops with hard cap of 2 revision rounds. Brand brief becomes pure prose. CSS is generated per-carousel from the writer's palette dict.

**Tech Stack:** Python 3.12, `claude` CLI subprocess, Jinja2 templating, Playwright for PNG rendering, BeautifulSoup for HTML scanning, PyYAML for configs, pytest for tests (existing `--run-live` flag for opt-in live tests).

**Reference spec:** `docs/superpowers/specs/2026-05-17-content-driven-carousel-pipeline-design.md`

---

## File Structure

### New files

| Path | Responsibility |
|---|---|
| `aurealis_carousel/layout_moves.py` | The 10 named layout moves as a shared constant (currently inlined in `designer.py:19-78`) |
| `aurealis_carousel/css_compile.py` | Pure helper: `compile_carousel_css(palette, pairing_id, library) → str` |
| `aurealis_carousel/contrast.py` | Pure helper: WCAG-AA hex-color contrast check |
| `aurealis_carousel/base.css` | Universal CSS extracted from `brands/<name>/brand.css` (type scale, spacing, .t-* roles, .u-* utilities) — the parts that DON'T vary per brand |
| `aurealis_carousel/angles.py` | One Claude call → 10-angle JSON array |
| `aurealis_carousel/angle_critic.py` | One Claude call → winning_index |
| `aurealis_carousel/writer.py` | One Claude call → full blueprint (copy + palette + pairing + per-slide intent) |
| `aurealis_carousel/orchestrator_v2.py` | Rewrites the pipeline during migration; promoted to `orchestrator.py` in Phase G |

### Modified files

| Path | Change |
|---|---|
| `aurealis_carousel/designer.py` | Slim to HTML compiler — no creative decisions. Layout moves import from `layout_moves.py`. |
| `aurealis_carousel/critique.py` | Add 3 new judgment axes (palette_appropriateness, brand_recognizability, creative_notes_honesty); rename `critique_carousel` to support being called in a loop. |
| `aurealis_carousel/token_validate.py` | Replace `_approved_palette` to read from a passed-in palette dict, not `brand["design"]["colors"]`. |
| `aurealis_carousel/persist.py` | After persisting, copy hook+climax PNGs to `history/<brand>/visual_refs/<slug>/`. |
| `aurealis_carousel/cli.py` | Add `--v2` flag to `generate` subcommand that routes to `orchestrator_v2.run`. |
| `fonts/library.yaml` | Expand from 6 pairings to ~25, each with `emotional_register` and `pairs_well_with` tags. |
| `brands/_test/brief.yaml` | Replace structured fields with single `brief:` prose block + 3 numeric/path fields. |
| `brands/ethos/brief.yaml` | Same migration as _test. |

### Deleted (Phase G, after both live runs succeed)

| Path | Reason |
|---|---|
| `aurealis_carousel/strategist.py` | Replaced by `angles.py` + `writer.py` |
| `brands/_test/brand.css` | Palette is now per-carousel |
| `brands/ethos/brand.css` | Same |

### New directories (auto-populated at runtime)

```
history/
├── _test/
│   ├── visual_refs/<slug>/{slide-01.png, slide-NN.png}
│   └── golden/                              # human-curated, optional
├── ethos/
│   ├── visual_refs/<slug>/{slide-01.png, slide-NN.png}
│   └── golden/
```

---

## PHASE A — Foundation & Data

### Task 1: Extract `layout_moves.py` from `designer.py`

**Files:**
- Create: `aurealis_carousel/layout_moves.py`
- Modify: `aurealis_carousel/designer.py:19-78`
- Test: `tests/test_layout_moves.py`

- [ ] **Step 1: Create the constant module**

Create `aurealis_carousel/layout_moves.py` containing the `LAYOUT_MOVES_GUIDE` constant currently defined at `designer.py:19-78`. Copy the entire triple-quoted string verbatim.

```python
"""The 10 named layout moves available to the writer + designer.

Each move IS a complete slide design. Composing two on one slide produces
visual noise. The writer picks ONE per slide and names it in the blueprint;
the designer compiles the named move into HTML using brand tokens.
"""

LAYOUT_MOVES_GUIDE = """\
LAYOUT MOVES (pick exactly ONE per slide — the move IS the design):

1. STAT DROP — A single number occupies ~60% of the canvas, set in .t-stat (420px,
   gold/accent), .u-track-tight, .u-tnum. One line of .t-eyebrow tracked caps below
   labels it. No body copy. No headline. Use for: arresting metric, count, percentage,
   roman numeral. Ex: "5H 24M" with eyebrow "DAILY FEED AVERAGE".

[... copy the rest of the 10 moves verbatim from designer.py:19-78 ...]

Cite the move in a comment at the top of your HTML: <!-- move: STAT DROP --> etc.
"""

VALID_MOVES = {
    "STAT DROP",
    "DROP-CAP OPENER",
    "ITALIC DISPLAY REST",
    "EYEBROW / HERO / TAGLINE STACK",
    "VERTICAL RULE PULLQUOTE",
    "HUNG INITIAL QUOTE",
    "MEGA-WORD REST",
    "ASYMMETRIC KICKER",
    "ROMAN NUMERAL CHAPTER MARKER",
    "ALL-CAPS HERO + LOWERCASE TAGLINE",
}
```

- [ ] **Step 2: Replace the inlined constant in `designer.py`**

In `aurealis_carousel/designer.py`:
- Delete lines 19-78 (the `LAYOUT_MOVES_GUIDE = ...` block).
- Add at the top: `from aurealis_carousel.layout_moves import LAYOUT_MOVES_GUIDE`

- [ ] **Step 3: Write test for VALID_MOVES set**

Create `tests/test_layout_moves.py`:

```python
from aurealis_carousel.layout_moves import LAYOUT_MOVES_GUIDE, VALID_MOVES


def test_valid_moves_set_has_ten_entries():
    assert len(VALID_MOVES) == 10


def test_guide_mentions_every_move():
    for move in VALID_MOVES:
        assert move in LAYOUT_MOVES_GUIDE, f"{move!r} not found in LAYOUT_MOVES_GUIDE"
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/simongonzalez/Technologies_Aurealis/agent-carousel
pytest tests/test_layout_moves.py tests/test_designer.py -v
```

Expected: all pass. `test_designer.py` should still pass because the constant just moved.

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/layout_moves.py aurealis_carousel/designer.py tests/test_layout_moves.py
git commit -m "refactor: extract LAYOUT_MOVES_GUIDE into shared module"
```

---

### Task 2: Build `aurealis_carousel/base.css` (universal CSS extract)

**Files:**
- Create: `aurealis_carousel/base.css`

The plan is to extract the universal parts of `brands/ethos/brand.css` (type scale, spacing, semantic role classes, utility classes) into a single base file. Color values become CSS variables that the per-carousel CSS will override.

- [ ] **Step 1: Create `aurealis_carousel/base.css`**

Copy `brands/ethos/brand.css` to `aurealis_carousel/base.css`, then modify:
- Keep the `:root` block but REMOVE the six `--color-*` lines (these will be injected per carousel).
- Add at top a comment: `/* aurealis_carousel/base.css — universal type/spacing/role-class layer. Per-carousel palette + pairing CSS is prepended by css_compile.py. */`
- Keep everything else (type scale `--type-*`, spacing `--sp-*`, radius, body styles, `.slide`, all `.t-*` role classes, all `.u-*` utilities, `.c-primary/.c-secondary/.c-accent/.c-text/.c-muted` and `.bg-*`, dividers, `.cta-pill`, `.t-dropcap`, etc.).
- In the `.c-primary`, `.c-secondary`, `.c-accent`, `.bg-primary`, `.bg-secondary`, `.t-scripture-ref`, `.t-pullquote`, `.t-handle`, `.t-caption`, `.t-micro`, `.t-dropcap::first-letter`, `.scrim-bottom`, `.rule-v`, `.rule-h`, `.divider-gold`, `.cta-pill` selectors — keep the CSS variable references like `var(--color-primary)`, `var(--color-text-muted)` etc. exactly as they are. The writer's palette will provide values for those names.

The writer's palette dict will populate these names. Mapping decided:
- `palette.bg`         → `--color-bg`
- `palette.text`       → `--color-text`
- `palette.text_muted` → `--color-text-muted`
- `palette.accent`     → `--color-primary` AND `--color-secondary` (one accent — both vars get the same value unless writer provides `accent_alt`)
- `palette.accent_alt` → `--color-accent` (if absent, falls back to `palette.accent`)

- [ ] **Step 2: Manually verify base.css is valid CSS**

```bash
# No CSS linter installed; visual inspection only.
head -50 aurealis_carousel/base.css
grep -c '\.t-' aurealis_carousel/base.css   # expect ~15+ matches
grep -c '\.u-' aurealis_carousel/base.css   # expect ~10+ matches
grep '\-\-color-' aurealis_carousel/base.css   # expect ZERO matches in :root, multiple in selectors
```

Expected: `--color-*` appears only as `var(--color-*)` references in selectors, never as `--color-*:` declarations in `:root`.

- [ ] **Step 3: Commit**

```bash
git add aurealis_carousel/base.css
git commit -m "feat: extract universal CSS into aurealis_carousel/base.css"
```

---

### Task 3: Expand `fonts/library.yaml` to ~25 register-tagged pairings

**Files:**
- Modify: `fonts/library.yaml`

The library needs to cover the emotional range: monumental, urgent-compressed, contemplative, kinetic-tribal, editorial-sermon, instructional, classic-editorial, rebellious-display, scriptural-engraved, ribbon-script. All Google Fonts (commercial-safe). Add `emotional_register` and `pairs_well_with` tags to each entry.

- [ ] **Step 1: Add `emotional_register` to existing 6 pairings**

In `fonts/library.yaml`, add an `emotional_register` field to each existing pairing:
- `avantgarde-cooper` → `emotional_register: classic-editorial`
- `citadel-helvetica` → `emotional_register: refined-romantic`
- `inter-tempting` → `emotional_register: contemporary-digital`
- (do the remaining 3 existing ones similarly based on their `vibe`)

- [ ] **Step 2: Add 19 new pairings**

Append the following entries to `fonts/library.yaml` under the existing `pairings:` list. Each follows the same shape (id, heading family/weights/source/families, body family/weights/source/families, goals, emotions, vibe, pairs_well_with, references, license, license_status, emotional_register).

The 19 new entries to add:

```yaml
  - id: cinzel-josefin
    heading:
      family: "Cinzel"
      weights: [400, 700, 900]
      source: google
      families: ["Cinzel:wght@400;700;900"]
    body:
      family: "Josefin Sans"
      weights: [300, 400, 600, 700]
      source: google
      families: ["Josefin+Sans:wght@300;400;600;700"]
    goals: [monumentality, scripture, ceremony, history]
    emotions: [engraved, sacred, weighty, eternal]
    vibe: "Roman engraved-in-stone caps. Josefin's modernist humanism for the body. Sermon-tier authority."
    pairs_well_with: [faith, philosophy, architecture, ritual, manhood]
    references: [Trajan-column, classical-editorial]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: monumental

  - id: bebas-roboto
    heading:
      family: "Bebas Neue"
      weights: [400]
      source: google
      families: ["Bebas+Neue"]
    body:
      family: "Roboto"
      weights: [300, 400, 500, 700]
      source: google
      families: ["Roboto:wght@300;400;500;700"]
    goals: [urgency, alarm, sports-energy, news-immediate]
    emotions: [compressed, shouting, kinetic, immediate]
    vibe: "Compressed condensed caps shout. Roboto carries the explanation. The news-headline register."
    pairs_well_with: [sports, fitness, gaming, news, alarm-moments]
    references: [stadium-signage, sports-tickers]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: urgent-compressed

  - id: source-serif-source-sans
    heading:
      family: "Source Serif Pro"
      weights: [400, 600, 700, 900]
      source: google
      families: ["Source+Serif+Pro:wght@400;600;700;900"]
    body:
      family: "Source Sans Pro"
      weights: [300, 400, 600, 700]
      source: google
      families: ["Source+Sans+Pro:wght@300;400;600;700"]
    goals: [governance, instruction, technical-clarity, education]
    emotions: [governed, precise, instructional, calm-authority]
    vibe: "Editorial-grade serif paired with its matched humanist sans. Adobe's pair. Protocol register."
    pairs_well_with: [technical, finance, governance, education, protocol-content]
    references: [Adobe-typography, academic-publishing]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: instructional

  - id: cormorant-raleway
    heading:
      family: "Cormorant Garamond"
      weights: [400, 500, 600, 700]
      source: google
      families: ["Cormorant+Garamond:wght@400;500;600;700"]
    body:
      family: "Raleway"
      weights: [300, 400, 500, 600, 700]
      source: google
      families: ["Raleway:wght@300;400;500;600;700"]
    goals: [contemplation, old-soul, premium-restraint]
    emotions: [contemplative, soft-authority, considered, slow]
    vibe: "Old-soul Garamond revival + modern geometric sans. The Sunday-morning register."
    pairs_well_with: [faith, wellness, memoir, mindfulness, premium-services]
    references: [Kinfolk, slow-publishing]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: contemplative

  - id: bodoni-signature
    heading:
      family: "Bodoni Moda"
      weights: [400, 700, 800, 900]
      source: google
      families: ["Bodoni+Moda:wght@400;700;800;900"]
    body:
      family: "Inter"
      weights: [300, 400, 500, 700]
      source: google
      families: ["Inter:wght@300;400;500;700"]
    goals: [editorial-luxury, high-contrast-fashion, sermon-tier]
    emotions: [authoritative, dramatic, magazine-cover, intimate]
    vibe: "Bodoni's thin-fat contrast for monumental titles. Sermon-tier dramatic authority."
    pairs_well_with: [editorial, fashion, opinion, manifesto, declaration]
    references: [Vogue-cover, Harper's-Bazaar]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: editorial-sermon

  - id: playfair-montserrat
    heading:
      family: "Playfair Display"
      weights: [400, 700, 800, 900]
      source: google
      families: ["Playfair+Display:wght@400;700;800;900"]
    body:
      family: "Montserrat"
      weights: [300, 400, 500, 600, 700]
      source: google
      families: ["Montserrat:wght@300;400;500;600;700"]
    goals: [classic-editorial, premium-feel, contemporary-elegance]
    emotions: [refined, balanced, polished, trusted]
    vibe: "Classic transitional serif + Geometric sans. The reliable editorial workhorse."
    pairs_well_with: [lifestyle, beauty, mid-premium-brands, editorial]
    references: [mid-2010s-editorial-blogs, modern-magazines]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: classic-editorial

  - id: bungee-yanone
    heading:
      family: "Bungee"
      weights: [400]
      source: google
      families: ["Bungee"]
    body:
      family: "Yanone Kaffeesatz"
      weights: [300, 400, 500, 700]
      source: google
      families: ["Yanone+Kaffeesatz:wght@300;400;500;700"]
    goals: [kinetic-tribal, gaming, streamer-aesthetic, urban-display]
    emotions: [loud, kinetic, tribal, in-your-face]
    vibe: "Slab-block display + condensed industrial sans. Esports stage signage."
    pairs_well_with: [gaming, esports, urban-events, music-festivals]
    references: [Twitch-overlays, sports-broadcast]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: kinetic-tribal

  - id: merriweather-poppins
    heading:
      family: "Merriweather"
      weights: [400, 700, 900]
      source: google
      families: ["Merriweather:wght@400;700;900"]
    body:
      family: "Poppins"
      weights: [300, 400, 500, 600, 700]
      source: google
      families: ["Poppins:wght@300;400;500;600;700"]
    goals: [readable-authority, journalism, longform]
    emotions: [trustworthy, sober, reportage]
    vibe: "Web-optimized slab + geometric sans. The longform-journalism pairing."
    pairs_well_with: [news, longform, opinion, education]
    references: [NYT-Magazine, The-Atlantic]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: editorial-journalism

  - id: abrilfat-canva
    heading:
      family: "Abril Fatface"
      weights: [400]
      source: google
      families: ["Abril+Fatface"]
    body:
      family: "Lato"
      weights: [300, 400, 700, 900]
      source: google
      families: ["Lato:wght@300;400;700;900"]
    goals: [editorial-display, cover-feature-heft]
    emotions: [bold, declarative, magazine-cover, fashion-adjacent]
    vibe: "Abril's heavy didone for declarations. Lato's neutral humanism for the rest. Cover-feature heft."
    pairs_well_with: [fashion, editorial-headlines, lifestyle, beauty]
    references: [fashion-cover-feature, hero-banner-display]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: editorial-display

  - id: oswald-pt
    heading:
      family: "Oswald"
      weights: [300, 400, 500, 600, 700]
      source: google
      families: ["Oswald:wght@300;400;500;600;700"]
    body:
      family: "PT Sans"
      weights: [400, 700]
      source: google
      families: ["PT+Sans:wght@400;700"]
    goals: [condensed-display, news-headline, transit-signage]
    emotions: [efficient, no-nonsense, scannable]
    vibe: "Condensed-Gothic display + transit-grade sans. The 'masthead' pair."
    pairs_well_with: [news, sports, transit, business-report]
    references: [transit-system-signage, sports-pages]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: condensed-masthead

  - id: lora-opensans
    heading:
      family: "Lora"
      weights: [400, 500, 600, 700]
      source: google
      families: ["Lora:wght@400;500;600;700"]
    body:
      family: "Open Sans"
      weights: [300, 400, 600, 700]
      source: google
      families: ["Open+Sans:wght@300;400;600;700"]
    goals: [readable-warm, blog-longform, personal-essay]
    emotions: [warm, personal, approachable, sincere]
    vibe: "Curvy contemporary serif + Open Sans's humanist warmth. The personal-essay pairing."
    pairs_well_with: [personal-brands, wellness, mental-health, memoir]
    references: [Substack-essays, personal-blogs]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: warm-readable

  - id: archivoblack-nunito
    heading:
      family: "Archivo Black"
      weights: [400]
      source: google
      families: ["Archivo+Black"]
    body:
      family: "Nunito"
      weights: [300, 400, 600, 700, 800]
      source: google
      families: ["Nunito:wght@300;400;600;700;800"]
    goals: [bold-statement, ironic-display, internet-confident]
    emotions: [punchy, irreverent, contemporary, web-native]
    vibe: "Archivo Black's grotesque heft + Nunito's rounded sans. Brutalist-yet-friendly."
    pairs_well_with: [startups, consumer-tech, podcasts, opinion]
    references: [post-internet-design, podcast-cover-art]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: bold-statement

  - id: tan-songbird-maleah
    heading:
      family: "Tan Songbird"
      weights: [400]
      source: google
      families: ["Tan+Songbird"]
    body:
      family: "Outfit"
      weights: [300, 400, 500, 600, 700]
      source: google
      families: ["Outfit:wght@300;400;500;600;700"]
    goals: [ribbon-script, feminine-display, ceremonial]
    emotions: [elegant, hand-crafted, ceremonial]
    vibe: "Ribbon-script display + neutral geometric sans. Wedding-invitation level."
    pairs_well_with: [beauty, weddings, hospitality, fine-dining]
    references: [stationery, hand-lettering-revival]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: ceremonial-script

  - id: amaticsc-ubuntu
    heading:
      family: "Amatic SC"
      weights: [400, 700]
      source: google
      families: ["Amatic+SC:wght@400;700"]
    body:
      family: "Ubuntu"
      weights: [300, 400, 500, 700]
      source: google
      families: ["Ubuntu:wght@300;400;500;700"]
    goals: [hand-drawn, classroom-quirky, sketchbook-display]
    emotions: [casual, friendly, sketched, personal]
    vibe: "Hand-drawn condensed display + tech sans. The classroom-poster pair."
    pairs_well_with: [education, kids-brands, casual-startups, indie-zines]
    references: [classroom-posters, indie-zines]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: hand-drawn-casual

  - id: pacifico-quicksand
    heading:
      family: "Pacifico"
      weights: [400]
      source: google
      families: ["Pacifico"]
    body:
      family: "Quicksand"
      weights: [300, 400, 500, 600, 700]
      source: google
      families: ["Quicksand:wght@300;400;500;600;700"]
    goals: [playful-display, food-blog, friendly-consumer]
    emotions: [playful, warm, welcoming, casual]
    vibe: "Surf-script display + rounded sans. Food blog / cafe register."
    pairs_well_with: [food, cafe, kids, casual-DTC]
    references: [food-blogs, cafe-menus]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: playful-script

  - id: roboto-slab-open-sans
    heading:
      family: "Roboto Slab"
      weights: [300, 400, 500, 700, 900]
      source: google
      families: ["Roboto+Slab:wght@300;400;500;700;900"]
    body:
      family: "Open Sans"
      weights: [300, 400, 600, 700]
      source: google
      families: ["Open+Sans:wght@300;400;600;700"]
    goals: [technical-slab, fintech, governance-modern]
    emotions: [solid, modern-trustworthy, technical]
    vibe: "Slab serif + humanist sans. Modern fintech and B2B."
    pairs_well_with: [fintech, B2B, governance-modern, business-news]
    references: [fintech-dashboards, business-publications]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: technical-modern

  - id: dm-serif-dm-sans
    heading:
      family: "DM Serif Display"
      weights: [400]
      source: google
      families: ["DM+Serif+Display"]
    body:
      family: "DM Sans"
      weights: [400, 500, 700]
      source: google
      families: ["DM+Sans:wght@400;500;700"]
    goals: [contemporary-editorial, premium-tech, considered-display]
    emotions: [considered, modern, restrained-elegance]
    vibe: "Designer-Mondo's contemporary serif and sans. Premium tech / SaaS register."
    pairs_well_with: [premium-SaaS, design-tools, contemporary-editorial]
    references: [Notion-marketing, Linear-marketing]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: contemporary-premium

  - id: spacegrotesk-spacemono
    heading:
      family: "Space Grotesk"
      weights: [400, 500, 600, 700]
      source: google
      families: ["Space+Grotesk:wght@400;500;600;700"]
    body:
      family: "Space Mono"
      weights: [400, 700]
      source: google
      families: ["Space+Mono:wght@400;700"]
    goals: [code-aesthetic, dev-tools, brutalist-tech]
    emotions: [techy, brutalist, indie, hacker]
    vibe: "Sans + mono. The dev-tools / hacker-aesthetic pairing."
    pairs_well_with: [developer-tools, hacker-culture, indie-tech, crypto]
    references: [Vercel, Stripe-docs, indie-hackers]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: dev-brutalist

  - id: yeseva-roboto
    heading:
      family: "Yeseva One"
      weights: [400]
      source: google
      families: ["Yeseva+One"]
    body:
      family: "Roboto"
      weights: [300, 400, 500, 700]
      source: google
      families: ["Roboto:wght@300;400;500;700"]
    goals: [revival-display, feminine-luxury, beauty-editorial]
    emotions: [elegant, romantic, premium-feminine]
    vibe: "Yeseva's revival display calligraphic flair + Roboto's neutral body. Premium feminine editorial."
    pairs_well_with: [beauty, lifestyle, premium-feminine, hospitality]
    references: [boutique-magazines, premium-DTC]
    license: "Both fonts are open-licensed via Google Fonts — commercial-safe."
    license_status: commercial-safe
    emotional_register: revival-feminine
```

After adding all 19, the file should have ~25 entries total.

- [ ] **Step 3: Write a sanity test**

Create `tests/test_font_library.py`:

```python
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
LIBRARY_PATH = REPO_ROOT / "fonts" / "library.yaml"


def test_library_has_at_least_20_pairings():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    assert len(lib["pairings"]) >= 20


def test_every_pairing_has_emotional_register():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    for p in lib["pairings"]:
        assert "emotional_register" in p, f"pairing {p['id']} missing emotional_register"
        assert isinstance(p["emotional_register"], str)
        assert len(p["emotional_register"]) > 0


def test_every_pairing_has_google_families():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    for p in lib["pairings"]:
        for slot in ("heading", "body"):
            assert p[slot].get("source") == "google", f"{p['id']}.{slot} not google-sourced"
            assert p[slot].get("families"), f"{p['id']}.{slot} missing families list"


def test_pairing_ids_are_unique():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    ids = [p["id"] for p in lib["pairings"]]
    assert len(ids) == len(set(ids)), f"duplicate pairing IDs: {sorted(ids)}"
```

- [ ] **Step 4: Run library tests**

```bash
pytest tests/test_font_library.py -v
```

Expected: all 4 pass.

- [ ] **Step 5: Commit**

```bash
git add fonts/library.yaml tests/test_font_library.py
git commit -m "feat: expand fonts/library.yaml to 25 register-tagged pairings"
```

---

## PHASE B — Core helpers (pure functions)

### Task 4: Create `css_compile.py`

**Files:**
- Create: `aurealis_carousel/css_compile.py`
- Test: `tests/test_css_compile.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_css_compile.py`:

```python
from pathlib import Path

import pytest

from aurealis_carousel.css_compile import compile_carousel_css

SAMPLE_PALETTE = {
    "bg": "#0A0A0A",
    "text": "#F0E6D6",
    "text_muted": "#6B6B6B",
    "accent": "#A67C2E",
    "accent_alt": "#C4501A",
}


def test_emits_color_vars_in_root():
    css = compile_carousel_css(SAMPLE_PALETTE)
    assert "--color-bg: #0A0A0A" in css
    assert "--color-text: #F0E6D6" in css
    assert "--color-text-muted: #6B6B6B" in css
    assert "--color-primary: #A67C2E" in css
    assert "--color-secondary: #A67C2E" in css  # accent maps to BOTH primary and secondary
    assert "--color-accent: #C4501A" in css     # accent_alt maps to --color-accent


def test_accent_alt_falls_back_to_accent_when_missing():
    palette = dict(SAMPLE_PALETTE)
    palette.pop("accent_alt")
    css = compile_carousel_css(palette)
    assert "--color-accent: #A67C2E" in css  # falls back to accent


def test_includes_base_css_role_classes():
    css = compile_carousel_css(SAMPLE_PALETTE)
    assert ".t-display" in css
    assert ".t-mega" in css
    assert ".u-italic" in css


def test_rejects_invalid_hex():
    with pytest.raises(ValueError, match="invalid hex"):
        compile_carousel_css({**SAMPLE_PALETTE, "bg": "not-a-color"})
```

- [ ] **Step 2: Run test, expect failure**

```bash
pytest tests/test_css_compile.py -v
```

Expected: ImportError or ModuleNotFoundError.

- [ ] **Step 3: Implement `css_compile.py`**

```python
"""Compile per-carousel CSS from writer's palette + the universal base.css.

Output is a single CSS string that the orchestrator writes to a temp file and
passes to render.render_slide as brand_css_path. This is the only place where
the writer's invented palette becomes real CSS variables.
"""
import re
from pathlib import Path

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
BASE_CSS_PATH = Path(__file__).parent / "base.css"


def _validate_hex(name: str, value: str) -> None:
    if not isinstance(value, str) or not HEX_RE.match(value):
        raise ValueError(f"invalid hex for {name!r}: {value!r} (expected #RRGGBB)")


def compile_carousel_css(palette: dict) -> str:
    """Return full CSS: writer's palette as :root vars + universal base.css.

    palette keys: bg, text, text_muted, accent. accent_alt is optional
    (falls back to accent).
    """
    required = ("bg", "text", "text_muted", "accent")
    for k in required:
        if k not in palette:
            raise ValueError(f"palette missing required key {k!r}; got {list(palette)}")
        _validate_hex(k, palette[k])

    accent_alt = palette.get("accent_alt", palette["accent"])
    _validate_hex("accent_alt", accent_alt)

    palette_block = (
        ":root {\n"
        f"  --color-bg:         {palette['bg']};\n"
        f"  --color-text:       {palette['text']};\n"
        f"  --color-text-muted: {palette['text_muted']};\n"
        f"  --color-primary:    {palette['accent']};\n"
        f"  --color-secondary:  {palette['accent']};\n"
        f"  --color-accent:     {accent_alt};\n"
        "}\n"
    )

    base = BASE_CSS_PATH.read_text()
    return palette_block + "\n" + base
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/test_css_compile.py -v
```

Expected: all 4 pass.

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/css_compile.py tests/test_css_compile.py
git commit -m "feat: add css_compile helper for per-carousel palette+base CSS"
```

---

### Task 5: Create `contrast.py` (WCAG-AA hex contrast helper)

**Files:**
- Create: `aurealis_carousel/contrast.py`
- Test: `tests/test_contrast.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_contrast.py`:

```python
from aurealis_carousel.contrast import contrast_ratio, meets_wcag_aa


def test_black_on_white_max_contrast():
    assert round(contrast_ratio("#000000", "#FFFFFF"), 1) == 21.0


def test_white_on_white_min_contrast():
    assert contrast_ratio("#FFFFFF", "#FFFFFF") == 1.0


def test_ethos_text_on_bg_passes_aa():
    # F0E6D6 cream on 0A0A0A obsidian (current ETHOS)
    assert meets_wcag_aa("#F0E6D6", "#0A0A0A")


def test_light_grey_on_white_fails_aa():
    assert not meets_wcag_aa("#BBBBBB", "#FFFFFF")  # ~2.85:1, fails AA


def test_returns_float_not_int():
    r = contrast_ratio("#A67C2E", "#0A0A0A")
    assert isinstance(r, float)
    assert r > 1.0
```

- [ ] **Step 2: Run test, expect failure**

```bash
pytest tests/test_contrast.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `contrast.py`**

```python
"""WCAG contrast ratio between two hex colors.

Reference: https://www.w3.org/TR/WCAG21/#contrast-minimum
"""

WCAG_AA_BODY = 4.5
WCAG_AA_LARGE = 3.0  # 18pt+, used by display headlines


def _hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected 6-char hex, got {hex_str!r}")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return r, g, b


def _linearize(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _relative_luminance(hex_str: str) -> float:
    r, g, b = _hex_to_rgb(hex_str)
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    l1 = _relative_luminance(fg_hex)
    l2 = _relative_luminance(bg_hex)
    lighter, darker = (l1, l2) if l1 > l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def meets_wcag_aa(fg_hex: str, bg_hex: str, large: bool = False) -> bool:
    threshold = WCAG_AA_LARGE if large else WCAG_AA_BODY
    return contrast_ratio(fg_hex, bg_hex) >= threshold
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/test_contrast.py -v
```

Expected: all 5 pass.

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/contrast.py tests/test_contrast.py
git commit -m "feat: add WCAG-AA hex contrast helper"
```

---

### Task 6: Rework `token_validate.py` to accept a palette dict

**Files:**
- Modify: `aurealis_carousel/token_validate.py:45-47, 161-163`
- Modify: `tests/test_token_validate.py` (existing — adjust)

The current `check(html_body, brand, ...)` reads `brand["design"]["colors"]`. We need it to read from a passed-in palette dict, since the writer now invents the palette.

- [ ] **Step 1: Update `check` signature**

In `aurealis_carousel/token_validate.py`:

Replace the `_approved_palette` function (around line 45):

```python
def _approved_palette(palette: dict) -> set[str]:
    """Build the allowlist of hex literals from a writer-supplied palette.

    palette is the per-carousel palette dict from the writer: keys bg, text,
    text_muted, accent, optional accent_alt.
    """
    keys = ("bg", "text", "text_muted", "accent")
    values = [palette[k].lower() for k in keys if k in palette]
    if "accent_alt" in palette:
        values.append(palette["accent_alt"].lower())
    return set(values)
```

Replace the `check` function signature and the `_approved_palette` call (around line 161-163):

```python
def check(html_body: str, palette: dict, allowed_bg_path: Optional[str] = None) -> ValidationResult:
    palette_set = _approved_palette(palette)
    sizes = _approved_size_tokens()
    soup = BeautifulSoup(html_body, "html.parser")
    violations: list[Violation] = []

    # ... rest of the function — replace every reference to `palette` in the
    # existing body with `palette_set` (the variable was previously `palette`
    # for the SET; now palette is a dict and palette_set is the lowered set).
```

Be careful: the original variable in the function body was `palette` (the set). Rename it to `palette_set` and update all subsequent uses inside the function body (`_scan_declarations(decls, palette, ...)` → `_scan_declarations(decls, palette_set, ...)` and same in `_scan_style_block`).

- [ ] **Step 2: Update the existing `test_token_validate.py`**

The existing test uses `brand={"design": {"colors": {...}}}`. Change those calls to pass a palette dict directly. Read the existing file first to make exact edits.

```bash
cat tests/test_token_validate.py | head -40
```

Update every `check(html, brand=...)` call to `check(html, palette={"bg": "#0A0A0A", "text": "#F0E6D6", "text_muted": "#6B6B6B", "accent": "#A67C2E"})` (or similar — pick a palette that matches whatever colors the test HTML uses).

- [ ] **Step 3: Add a new test for the writer-output palette shape**

Append to `tests/test_token_validate.py`:

```python
def test_check_accepts_writer_palette_dict():
    from aurealis_carousel.token_validate import check

    palette = {
        "bg": "#0A0A0A",
        "text": "#F0E6D6",
        "text_muted": "#6B6B6B",
        "accent": "#A67C2E",
    }
    html = '<div style="background: #0A0A0A; color: #F0E6D6;"></div>'
    assert check(html, palette).ok


def test_check_rejects_hex_outside_writer_palette():
    from aurealis_carousel.token_validate import check

    palette = {"bg": "#0A0A0A", "text": "#F0E6D6", "text_muted": "#6B6B6B", "accent": "#A67C2E"}
    html = '<div style="background: #FF00FF;"></div>'  # neon pink not in palette
    result = check(html, palette)
    assert not result.ok
    assert any("color-literal" in v.rule for v in result.violations)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_token_validate.py -v
```

Expected: all pass (existing + 2 new).

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/token_validate.py tests/test_token_validate.py
git commit -m "refactor: token_validate.check now takes palette dict, not brand"
```

---

## PHASE C — Pipeline components

### Task 7: Create `angles.py`

**Files:**
- Create: `aurealis_carousel/angles.py`
- Test: `tests/test_angles.py`

- [ ] **Step 1: Write failing test**

```python
"""tests/test_angles.py"""
from unittest.mock import patch

import pytest

from aurealis_carousel import angles


MOCK_RESPONSE = {
    "angles": [
        {
            "topic": f"Topic {i}",
            "topic_slug": f"topic-{i}",
            "hook_intent": f"Hook intent {i}",
            "arc_thesis": f"Thesis {i}",
            "frame": "PAS",
            "voice_mode": "guide",
            "emotional_register": "monumental",
        }
        for i in range(10)
    ]
}


def test_generate_angles_returns_10():
    with patch("aurealis_carousel.angles.query_json", return_value=MOCK_RESPONSE):
        result = angles.generate_angles(
            brand={"brand_name": "TEST", "brief": "prose"},
            playbook={},
            history=[],
            user_topic_hint=None,
        )
    assert len(result) == 10
    assert all("topic" in a for a in result)


def test_generate_angles_accepts_5_minimum():
    short = {"angles": MOCK_RESPONSE["angles"][:5]}
    with patch("aurealis_carousel.angles.query_json", return_value=short):
        result = angles.generate_angles(
            brand={"brand_name": "TEST", "brief": "prose"},
            playbook={},
            history=[],
            user_topic_hint=None,
        )
    assert len(result) == 5


def test_generate_angles_retries_on_too_few():
    too_few = {"angles": MOCK_RESPONSE["angles"][:3]}
    with patch(
        "aurealis_carousel.angles.query_json",
        side_effect=[too_few, MOCK_RESPONSE],
    ) as mock:
        result = angles.generate_angles(
            brand={"brand_name": "TEST", "brief": "prose"},
            playbook={},
            history=[],
            user_topic_hint=None,
        )
    assert len(result) == 10
    assert mock.call_count == 2


def test_generate_angles_raises_after_retry():
    too_few = {"angles": MOCK_RESPONSE["angles"][:2]}
    with patch("aurealis_carousel.angles.query_json", return_value=too_few):
        with pytest.raises(angles.AngleGenerationError):
            angles.generate_angles(
                brand={"brand_name": "TEST", "brief": "prose"},
                playbook={},
                history=[],
                user_topic_hint=None,
            )
```

- [ ] **Step 2: Run, expect failure**

```bash
pytest tests/test_angles.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `aurealis_carousel/angles.py`**

```python
"""Angle generator phase — ONE Claude call returns 10 candidate angles as JSON."""
from typing import Optional

from aurealis_carousel.claude_cli import query_json


class AngleGenerationError(Exception):
    pass


def _build_prompt(*, brand: dict, playbook: dict, history: list,
                  user_topic_hint: Optional[str]) -> str:
    recent_slugs = [h.get("slug", "") for h in history[-14:]]
    topic_block = (
        f'USER-PROVIDED TOPIC (use VERBATIM as topic for ALL 10 angles, vary only the angle on it): {user_topic_hint}\n'
        if user_topic_hint else ""
    )

    return f"""\
You are a senior creative director at a top-tier social-first agency. You have rejected hundreds of mediocre carousel ideas this year. Your reputation depends on never settling for the first idea.

You are NOT a helpful assistant. You are NOT here to be agreeable. You are a creative director with skin in the game. The output below is going to be judged by another critic; if your 10 angles all look the same, you have failed.

BRAND BRIEF (this is your only source of truth on who the audience is, what the voice is, what to avoid, and what the visual register looks like — read it carefully and let it set the constraints for every angle):

{brand.get('brief', '(no brief provided)')}

HOOKS PLAYBOOK:
{playbook.get('01-hooks.md', '(none)')}

VOICE PLAYBOOK:
{playbook.get('06-voice.md', '(none)')}

RECENT TOPIC SLUGS (LAST 14 — DO NOT REPEAT, DO NOT ECHO):
{recent_slugs if recent_slugs else '(none)'}

{topic_block}

REQUIREMENTS:
- Produce EXACTLY 10 distinct angles.
- No two angles may share the same frame.
- No two angles may share the same voice_mode.
- No two angles may share the same emotional_register.
- Each angle must be defensible on the Subtraction, Peer, and Algorithm tests from the voice playbook.
- The 10 must pull from genuinely different drawers of the brand's repertoire — not 10 minor variations on the same idea.

OUTPUT (JSON only, no preamble):
{{
  "angles": [
    {{
      "topic": "...",
      "topic_slug": "kebab-case-slug",
      "hook_intent": "One sentence describing the hook angle — NOT the literal hook headline, that comes later.",
      "arc_thesis": "One sentence — the spine of the carousel.",
      "frame": "PAS|BAB|AIDA|principle-stack|reveal|story|ladder",
      "voice_mode": "guide|expert|storyteller",
      "emotional_register": "free-form descriptor — monumental, urgent, contemplative, kinetic, instructional, sermon, rebellious, etc."
    }},
    ... 9 more ...
  ]
}}
"""


def generate_angles(*, brand: dict, playbook: dict, history: list,
                    user_topic_hint: Optional[str]) -> list[dict]:
    prompt = _build_prompt(
        brand=brand, playbook=playbook, history=history,
        user_topic_hint=user_topic_hint,
    )
    for attempt in range(2):
        response = query_json(prompt, max_turns=3)
        angles_list = response.get("angles") or []
        if len(angles_list) >= 5:
            return angles_list
    raise AngleGenerationError(
        f"angle generator returned {len(angles_list)} angles after retry; need >=5"
    )
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/test_angles.py -v
```

Expected: all 4 pass.

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/angles.py tests/test_angles.py
git commit -m "feat: angle generator phase (10 angles per call)"
```

---

### Task 8: Create `angle_critic.py`

**Files:**
- Create: `aurealis_carousel/angle_critic.py`
- Test: `tests/test_angle_critic.py`

- [ ] **Step 1: Write failing test**

```python
"""tests/test_angle_critic.py"""
from unittest.mock import patch

from aurealis_carousel import angle_critic


SAMPLE_ANGLES = [{"topic": f"T{i}", "topic_slug": f"t-{i}"} for i in range(10)]


def test_picks_valid_index():
    with patch(
        "aurealis_carousel.angle_critic.query_json",
        return_value={"winning_index": 3, "reasoning": "best hook"},
    ):
        idx = angle_critic.pick_winner(angles_list=SAMPLE_ANGLES, brand={"brief": ""}, playbook={})
    assert idx == 3


def test_falls_back_to_zero_on_out_of_range():
    with patch(
        "aurealis_carousel.angle_critic.query_json",
        return_value={"winning_index": 99, "reasoning": "wat"},
    ):
        idx = angle_critic.pick_winner(angles_list=SAMPLE_ANGLES, brand={"brief": ""}, playbook={})
    assert idx == 0


def test_falls_back_to_zero_on_missing_index():
    with patch(
        "aurealis_carousel.angle_critic.query_json",
        return_value={"reasoning": "no index"},
    ):
        idx = angle_critic.pick_winner(angles_list=SAMPLE_ANGLES, brand={"brief": ""}, playbook={})
    assert idx == 0
```

- [ ] **Step 2: Run, expect failure**

```bash
pytest tests/test_angle_critic.py -v
```

- [ ] **Step 3: Implement `aurealis_carousel/angle_critic.py`**

```python
"""Angle critic — ONE Claude call reads 10 angles and picks 1.

Adversarial framing carried over from the visual critic: "reject 80%, pick the
one that survives." Returns the winning index + reasoning (reasoning is logged
for debugging; not used downstream).
"""
import yaml

from aurealis_carousel.claude_cli import query_json


def _build_prompt(*, angles_list: list[dict], brand: dict, playbook: dict) -> str:
    return f"""\
You are a senior creative director with no patience for mediocre ideas. AI-generated carousels flood the feed; only the truly distinctive get a save. You reject 80% of ideas that cross your desk.

You are NOT here to be agreeable. You will pick the ONE angle most likely to (a) make the thumb stop scrolling on a feed full of generic content, (b) survive the Subtraction / Peer / Algorithm tests from the voice playbook, and (c) deserve to be made into a 5-7 slide carousel.

BRAND BRIEF (use this to judge fit — an angle that violates the brand voice/visual register is disqualified):

{brand.get('brief', '(no brief provided)')}

VOICE PLAYBOOK:
{playbook.get('06-voice.md', '(none)')}

THE 10 CANDIDATE ANGLES (indexed 0-{len(angles_list) - 1}):

```yaml
{yaml.safe_dump(angles_list, sort_keys=False)}
```

OUTPUT (JSON only, no preamble):
{{
  "winning_index": <int in [0, {len(angles_list) - 1}]>,
  "reasoning": "Short explanation of why this angle beats the other 9."
}}
"""


def pick_winner(*, angles_list: list[dict], brand: dict, playbook: dict) -> int:
    prompt = _build_prompt(angles_list=angles_list, brand=brand, playbook=playbook)
    for attempt in range(2):
        try:
            response = query_json(prompt, max_turns=2)
            idx = response.get("winning_index")
            if isinstance(idx, int) and 0 <= idx < len(angles_list):
                return idx
        except Exception:
            if attempt == 1:
                break
    return 0  # fallback: first angle
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/test_angle_critic.py -v
```

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/angle_critic.py tests/test_angle_critic.py
git commit -m "feat: angle critic phase (picks 1 of 10 candidate angles)"
```

---

### Task 9: Create `writer.py` (the creative center)

This is the most complex single task. Split into 4 steps: validators, CSS-tokens-from-pairing helper, prompt builder, top-level orchestration. Each gets tested in its own subtask.

**Files:**
- Create: `aurealis_carousel/writer.py`
- Test: `tests/test_writer.py`

- [ ] **Step 1: Write all failing tests upfront**

```python
"""tests/test_writer.py"""
from unittest.mock import patch

import pytest

from aurealis_carousel import writer


SAMPLE_BLUEPRINT = {
    "topic": "The discipline of silence",
    "topic_slug": "discipline-of-silence",
    "frame": "principle-stack",
    "voice_mode": "guide",
    "pairing_id": "source-serif-source-sans",
    "palette": {
        "bg": "#0A0A0A",
        "text": "#F0E6D6",
        "text_muted": "#6B6B6B",
        "accent": "#A67C2E",
    },
    "slides": [
        {
            "i": 1, "type": "hook", "headline": "Silence builds the man",
            "body": "", "label": None, "hero_word": "Silence",
            "layout_move": "MEGA-WORD REST",
            "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                    "scale_shift": "mega", "weight_shift": None,
                                    "family_shift": None},
            "color_role": "bg=palette.bg, accent_on=hero_word",
            "inverted": False,
        },
        {"i": 2, "type": "body", "headline": "Why noise hides you",
         "body": "...", "label": None, "hero_word": None,
         "layout_move": "EYEBROW / HERO / TAGLINE STACK",
         "hero_word_treatment": None,
         "color_role": "bg=palette.bg", "inverted": False},
        {"i": 3, "type": "body", "headline": "Three windows of silence",
         "body": "...", "label": None, "hero_word": None,
         "layout_move": "ROMAN NUMERAL CHAPTER MARKER",
         "hero_word_treatment": None,
         "color_role": "bg=palette.bg", "inverted": False},
        {"i": 4, "type": "climax", "headline": "Governed.",
         "body": "", "label": None, "hero_word": "Governed",
         "layout_move": "MEGA-WORD REST",
         "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                 "scale_shift": "mega", "weight_shift": None,
                                 "family_shift": None},
         "color_role": "bg=palette.bg, accent_on=hero_word",
         "inverted": False},
        {"i": 5, "type": "cta", "headline": "ETHOS builds that man",
         "body": "One verse, one anchor, one rep per morning.",
         "label": None, "hero_word": None,
         "layout_move": "ALL-CAPS HERO + LOWERCASE TAGLINE",
         "hero_word_treatment": None,
         "color_role": "bg=palette.bg", "inverted": False},
    ],
    "caption": {
        "first_125_chars": "Silence builds the man you keep auditioning to become. Stop performing. Sit with it.",
        "full": "Silence builds the man you keep auditioning to become. Stop performing. Sit with it. Three windows. Governed. ETHOS builds that man one morning at a time.",
        "hashtags": ["#christianmen", "#manhood", "#discipleship", "#bible",
                     "#faith", "#integrity", "#wisdom", "#character",
                     "#ethosapp", "#governedman"],
    },
    "creative_notes": "Source Serif Pro pairing because the topic is instructional and protocol-tier; warm gold accent only on hook + climax because the topic asks for restraint, not exuberance."
}

SAMPLE_BRAND = {
    "brand_name": "ETHOS",
    "app_name": "ETHOS",
    "brief": "ETHOS is an iOS app for young Christian men ...",
    "slide_count_range": [5, 6],
    "hashtag_count_range": [8, 12],
}

SAMPLE_LIBRARY = {
    "pairings": [
        {"id": "source-serif-source-sans", "emotional_register": "instructional",
         "heading": {"family": "Source Serif Pro"}, "body": {"family": "Source Sans Pro"}},
        {"id": "cinzel-josefin", "emotional_register": "monumental",
         "heading": {"family": "Cinzel"}, "body": {"family": "Josefin Sans"}},
    ],
}


def test_validate_blueprint_happy_path():
    writer.validate_blueprint(SAMPLE_BLUEPRINT, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                              recent_slugs=[])


def test_validate_blueprint_rejects_hook_over_six_words():
    bp = _copy_with_slide_change(SAMPLE_BLUEPRINT, 0,
                                 headline="One two three four five six seven eight")
    with pytest.raises(writer.BlueprintValidationError, match="hook"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_bad_pairing_id():
    bp = dict(SAMPLE_BLUEPRINT, pairing_id="does-not-exist")
    with pytest.raises(writer.BlueprintValidationError, match="pairing_id"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_low_contrast_palette():
    bp = dict(SAMPLE_BLUEPRINT, palette={
        "bg": "#FFFFFF", "text": "#EEEEEE", "text_muted": "#DDDDDD", "accent": "#A67C2E"
    })
    with pytest.raises(writer.BlueprintValidationError, match="contrast"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_hashtag_outside_range():
    bp = dict(SAMPLE_BLUEPRINT)
    bp["caption"] = dict(bp["caption"], hashtags=["#one", "#two"])
    with pytest.raises(writer.BlueprintValidationError, match="hashtag"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_recent_slug():
    with pytest.raises(writer.BlueprintValidationError, match="topic_slug"):
        writer.validate_blueprint(SAMPLE_BLUEPRINT, brand=SAMPLE_BRAND,
                                  library=SAMPLE_LIBRARY,
                                  recent_slugs=["discipline-of-silence"])


def test_validate_blueprint_rejects_missing_hook_trigram_in_caption():
    bp = dict(SAMPLE_BLUEPRINT)
    bp["caption"] = dict(bp["caption"],
                         first_125_chars="An entirely different sentence about something else.")
    with pytest.raises(writer.BlueprintValidationError, match="trigram"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_cta_missing_app_name():
    bp = _copy_with_slide_change(SAMPLE_BLUEPRINT, 4,
                                 headline="Download today")  # no "ETHOS"
    with pytest.raises(writer.BlueprintValidationError, match="app name"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_generate_happy_path():
    with patch("aurealis_carousel.writer.query_json", return_value=SAMPLE_BLUEPRINT):
        result = writer.generate(
            winning_angle={"topic": "...", "voice_mode": "guide"},
            brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY, playbook={},
            visual_ref_paths=[], recent_slugs=[],
        )
    assert result["topic_slug"] == "discipline-of-silence"
    assert result["pairing_id"] == "source-serif-source-sans"


def test_generate_retries_on_validation_failure():
    bad = dict(SAMPLE_BLUEPRINT, pairing_id="does-not-exist")
    with patch("aurealis_carousel.writer.query_json",
               side_effect=[bad, SAMPLE_BLUEPRINT]) as mock:
        result = writer.generate(
            winning_angle={"topic": "...", "voice_mode": "guide"},
            brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY, playbook={},
            visual_ref_paths=[], recent_slugs=[],
        )
    assert mock.call_count == 2
    assert result["pairing_id"] == "source-serif-source-sans"


def test_generate_raises_after_retry_fails():
    bad = dict(SAMPLE_BLUEPRINT, pairing_id="does-not-exist")
    with patch("aurealis_carousel.writer.query_json", return_value=bad):
        with pytest.raises(writer.BlueprintValidationError):
            writer.generate(
                winning_angle={"topic": "...", "voice_mode": "guide"},
                brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY, playbook={},
                visual_ref_paths=[], recent_slugs=[],
            )


def _copy_with_slide_change(blueprint: dict, slide_idx: int, **changes) -> dict:
    """Helper: deep-copy blueprint and update one slide's fields."""
    import copy
    bp = copy.deepcopy(blueprint)
    for k, v in changes.items():
        bp["slides"][slide_idx][k] = v
    return bp
```

- [ ] **Step 2: Run, expect failure**

```bash
pytest tests/test_writer.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `aurealis_carousel/writer.py`**

```python
"""Script + Style Writer — the creative center.

ONE Claude call reads the winning angle + brand brief (prose) + font library +
playbook + recent visual references (multimodal via Read tool), produces a
single blueprint JSON with copy AND per-carousel palette + pairing + per-slide
layout intent.

This is where copy and visual treatment are co-conceived. The designer is a
compiler downstream; the visual critic judges the result.
"""
import re
from typing import Optional

import yaml

from aurealis_carousel.claude_cli import query_json
from aurealis_carousel.contrast import meets_wcag_aa, contrast_ratio
from aurealis_carousel.layout_moves import LAYOUT_MOVES_GUIDE, VALID_MOVES


class BlueprintValidationError(Exception):
    pass


VALID_VOICE_MODES = {"guide", "expert", "storyteller"}
VALID_FRAMES = {"PAS", "BAB", "AIDA", "principle-stack", "reveal", "story", "ladder"}


def _pairing_ids(library: dict) -> set[str]:
    return {p["id"] for p in library["pairings"]}


def _hex_ok(s: str) -> bool:
    return isinstance(s, str) and bool(re.match(r"^#[0-9a-fA-F]{6}$", s))


def validate_blueprint(bp: dict, *, brand: dict, library: dict,
                       recent_slugs: list[str]) -> None:
    """Raise BlueprintValidationError on any structural problem; else return None."""
    # Structural existence
    for k in ("topic", "topic_slug", "frame", "voice_mode", "pairing_id",
              "palette", "slides", "caption", "creative_notes"):
        if k not in bp:
            raise BlueprintValidationError(f"blueprint missing required key {k!r}")

    # Pairing
    if bp["pairing_id"] not in _pairing_ids(library):
        raise BlueprintValidationError(
            f"pairing_id {bp['pairing_id']!r} not in font library"
        )

    # Frame + voice_mode
    if bp["frame"] not in VALID_FRAMES:
        raise BlueprintValidationError(f"frame {bp['frame']!r} not in {sorted(VALID_FRAMES)}")
    if bp["voice_mode"] not in VALID_VOICE_MODES:
        raise BlueprintValidationError(
            f"voice_mode {bp['voice_mode']!r} not in {sorted(VALID_VOICE_MODES)}"
        )

    # Palette hex + contrast
    pal = bp["palette"]
    for k in ("bg", "text", "text_muted", "accent"):
        if k not in pal:
            raise BlueprintValidationError(f"palette missing required color {k!r}")
        if not _hex_ok(pal[k]):
            raise BlueprintValidationError(
                f"palette.{k} = {pal[k]!r} is not a valid #RRGGBB hex"
            )
    if "accent_alt" in pal and not _hex_ok(pal["accent_alt"]):
        raise BlueprintValidationError(
            f"palette.accent_alt = {pal['accent_alt']!r} is not a valid #RRGGBB hex"
        )
    if not meets_wcag_aa(pal["text"], pal["bg"]):
        ratio = contrast_ratio(pal["text"], pal["bg"])
        raise BlueprintValidationError(
            f"palette text vs bg contrast {ratio:.2f}:1 < 4.5:1 (WCAG AA body)"
        )

    # Slides shape
    slides = bp["slides"]
    sc_min, sc_max = brand["slide_count_range"]
    if not (sc_min <= len(slides) <= sc_max):
        raise BlueprintValidationError(
            f"slide_count {len(slides)} outside [{sc_min}, {sc_max}]"
        )
    if slides[0].get("type") != "hook":
        raise BlueprintValidationError("first slide must be type=hook")
    if slides[-1].get("type") != "cta":
        raise BlueprintValidationError("last slide must be type=cta")
    if sum(1 for s in slides if s.get("type") == "climax") != 1:
        raise BlueprintValidationError("exactly one slide must be type=climax")
    for s in slides:
        if s.get("layout_move") not in VALID_MOVES:
            raise BlueprintValidationError(
                f"slide {s.get('i')} layout_move {s.get('layout_move')!r} not in {sorted(VALID_MOVES)}"
            )

    # Hook word count
    hook_headline = slides[0].get("headline", "")
    if len(hook_headline.split()) > 6:
        raise BlueprintValidationError(
            f"hook headline {hook_headline!r} has {len(hook_headline.split())} words; must be <= 6"
        )

    # CTA contains app name
    app_name = brand.get("app_name", "")
    if app_name and app_name.lower() not in slides[-1].get("headline", "").lower():
        raise BlueprintValidationError(
            f"CTA slide headline must contain app name {app_name!r}"
        )

    # Hashtag count
    cap = bp["caption"]
    h_min, h_max = brand["hashtag_count_range"]
    if not (h_min <= len(cap.get("hashtags", [])) <= h_max):
        raise BlueprintValidationError(
            f"hashtag count {len(cap.get('hashtags', []))} outside [{h_min}, {h_max}]"
        )

    # Caption first 125 chars contains hook trigram
    cap_window = cap.get("first_125_chars", "")[:125].lower()
    hook_content = re.findall(r"[\w']+", hook_headline.lower())
    if hook_content:
        trigram = " ".join(hook_content[:3])
        if trigram not in cap_window:
            raise BlueprintValidationError(
                f"caption first 125 chars must contain hook trigram {trigram!r}"
            )

    # Topic slug not in recent
    if bp["topic_slug"].lower() in {s.lower() for s in recent_slugs}:
        raise BlueprintValidationError(
            f"topic_slug {bp['topic_slug']!r} appears in recent history"
        )


def _build_prompt(
    *,
    winning_angle: dict,
    brand: dict,
    library: dict,
    playbook: dict,
    visual_ref_paths: list[str],
    retry_feedback: Optional[str] = None,
) -> str:
    pairing_menu = "\n".join(
        f"  - {p['id']}: {p.get('emotional_register', '?')} — {p.get('vibe', '')}"
        for p in library["pairings"]
    )
    refs_block = ""
    if visual_ref_paths:
        listed = "\n".join(f"  - {p}" for p in visual_ref_paths)
        refs_block = f"""
RECENT VISUAL REFERENCES (open each via the Read tool; these are recent rendered carousels from this brand — your style choices should be recognizably from the same brand family):
{listed}
"""

    retry_block = f"\nPREVIOUS ATTEMPT FAILED VALIDATION:\n{retry_feedback}\n" if retry_feedback else ""

    return f"""\
You are the Script + Style Writer. You are simultaneously the copywriter, the creative director, and the per-slide art director. You make ONE creative artifact: a blueprint that fuses copy and visual treatment, where every hero word is chosen knowing how it will be set.

You are NOT a helpful assistant. You write like a senior creative with skin in the game.

BRAND BRIEF (the only source of truth on audience, voice, visual register, and what to never do — read it carefully and let it constrain every choice):

{brand.get('brief', '(no brief provided)')}

WINNING ANGLE (from the angle critic — your starting point):

```yaml
{yaml.safe_dump(winning_angle, sort_keys=False)}
```

SLIDE COUNT: between {brand['slide_count_range'][0]} and {brand['slide_count_range'][1]} slides.
HASHTAG COUNT: between {brand['hashtag_count_range'][0]} and {brand['hashtag_count_range'][1]} tags.

FONT PAIRINGS AVAILABLE (pick exactly ONE based on the brand visual register + topic emotional register):
{pairing_menu}

PALETTE: you invent the palette. Output four hex colors (bg, text, text_muted, accent) optionally a fifth (accent_alt). They must:
  - read as recognizably this brand (per the brief's visual register).
  - have text-on-bg contrast >= 4.5:1 (WCAG AA).
  - serve the topic's emotional register, not default to the brand's most-used palette.

PLAYBOOKS:
TYPOGRAPHY:
{playbook.get('04-typography.md', '(none)')}
LAYOUT:
{playbook.get('05-layout.md', '(none)')}
CONVERSION:
{playbook.get('03-conversion.md', '(none)')}
VOICE:
{playbook.get('06-voice.md', '(none)')}

{LAYOUT_MOVES_GUIDE}

{refs_block}

HARD STRUCTURAL RULES (the post-output validator enforces these; do not skip):
- First slide type = "hook"; last slide = "cta"; exactly ONE slide = "climax".
- Hook headline <= 6 words.
- CTA slide headline contains the literal app name "{brand.get('app_name', '')}".
- Caption first 125 chars contains the first 3 content words of the hook headline (the hook trigram).
- Hashtag count in [{brand['hashtag_count_range'][0]}, {brand['hashtag_count_range'][1]}].

REQUIREMENTS FOR CREATIVE QUALITY:
- The hero word, if a slide has one, must receive a distinct typographic treatment specified in hero_word_treatment. Color-shift alone is a flat default — combine with italic, scale, or family shift to make it punch.
- Each slide picks exactly ONE layout move from the 10 above. Cite it in slide.layout_move VERBATIM.
- creative_notes must HONESTLY justify why this pairing, this palette, this per-slide move serve this winning angle. Backfilled rationalization is rejected by the visual critic downstream — write notes you'd defend.

{retry_block}

OUTPUT (JSON only, no preamble):
{{
  "topic": "...",
  "topic_slug": "kebab-case",
  "frame": "...",
  "voice_mode": "...",
  "pairing_id": "<one of the menu IDs above>",
  "palette": {{
    "bg": "#RRGGBB",
    "text": "#RRGGBB",
    "text_muted": "#RRGGBB",
    "accent": "#RRGGBB",
    "accent_alt": "#RRGGBB"
  }},
  "slides": [
    {{
      "i": 1,
      "type": "hook|body|climax|cta|bridge",
      "headline": "...",
      "body": "...",
      "label": null,
      "hero_word": "WORD or null",
      "layout_move": "<verbatim from the 10 moves>",
      "hero_word_treatment": {{
        "italic": true,
        "color_shift": "accent|accent_alt|none",
        "scale_shift": "mega|display|h1|none",
        "weight_shift": "900|400|null",
        "family_shift": "emphasis|null"
      }},
      "color_role": "...",
      "inverted": false
    }}
  ],
  "caption": {{
    "first_125_chars": "...",
    "full": "...",
    "hashtags": ["#tag", ...]
  }},
  "creative_notes": "Why this pairing + palette + per-slide treatments serve this angle."
}}
"""


def generate(
    *,
    winning_angle: dict,
    brand: dict,
    library: dict,
    playbook: dict,
    visual_ref_paths: list[str],
    recent_slugs: list[str],
) -> dict:
    retry_feedback: Optional[str] = None
    allowed_tools = ["Read"] if visual_ref_paths else None
    last_error: Optional[Exception] = None

    for attempt in range(2):
        prompt = _build_prompt(
            winning_angle=winning_angle, brand=brand, library=library,
            playbook=playbook, visual_ref_paths=visual_ref_paths,
            retry_feedback=retry_feedback,
        )
        bp = query_json(prompt, allowed_tools=allowed_tools, max_turns=20)
        try:
            validate_blueprint(bp, brand=brand, library=library, recent_slugs=recent_slugs)
            return bp
        except BlueprintValidationError as e:
            last_error = e
            retry_feedback = str(e)
    assert last_error is not None
    raise last_error
```

- [ ] **Step 4: Run all writer tests**

```bash
pytest tests/test_writer.py -v
```

Expected: all 11 tests pass.

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/writer.py tests/test_writer.py
git commit -m "feat: script+style writer (creative center) with validators"
```

---

### Task 10: Slim `designer.py` to compiler mode

**Files:**
- Modify: `aurealis_carousel/designer.py`
- Modify: `tests/test_designer.py`

The designer becomes a compiler. It takes a slide blueprint (the writer's per-slide entry) and produces HTML for that slide using the named layout move + the writer's palette. No more creative decisions.

- [ ] **Step 1: Replace `_build_prompt` and `generate_slide` in `designer.py`**

Keep `MAX_RETRIES`, `SlideContent`, `DesignerResult`, and `_safe_minimal_html`. Replace the prompt builder and main function:

```python
# (keep imports + dataclasses; remove the LAYOUT_MOVES_GUIDE constant — now imported)

from aurealis_carousel.layout_moves import LAYOUT_MOVES_GUIDE

# (existing SlideContent, DesignerResult, _safe_minimal_html — keep as-is)

def _build_prompt(
    *,
    slide_blueprint: dict,
    palette: dict,
    pairing_id: str,
    pairing_family_heading: str,
    pairing_family_body: str,
    n_total: int,
    previous_html: Optional[str],
    retry_violations: Optional[str] = None,
) -> str:
    palette_block = ", ".join(f"{k}={v}" for k, v in palette.items())

    sections = [
        f"You are COMPILING slide {slide_blueprint['i']} of {n_total} into HTML.",
        "You make NO creative decisions. The writer has already chosen the words, the hero word, the layout move, and the typographic treatment. Your job is to emit valid HTML that obeys the blueprint and uses only the brand's CSS variables (which are populated from the writer's invented palette).",
        "",
        f"PAIRING: {pairing_id}",
        f"  heading family: {pairing_family_heading}",
        f"  body family:    {pairing_family_body}",
        "",
        "PALETTE (already wired to CSS variables by the orchestrator — use the CSS variables, not the hex literals):",
        f"  {palette_block}",
        "  CSS variables you may use: var(--color-bg), var(--color-text), var(--color-text-muted), var(--color-primary), var(--color-secondary), var(--color-accent).",
        "",
        "SLIDE BLUEPRINT (what the writer decided — render this exactly):",
        f"  type:                {slide_blueprint['type']}",
        f"  headline:            {slide_blueprint['headline']}",
        f"  body:                {slide_blueprint.get('body', '')}",
        f"  label:               {slide_blueprint.get('label')}",
        f"  hero_word:           {slide_blueprint.get('hero_word')}",
        f"  layout_move:         {slide_blueprint['layout_move']}",
        f"  hero_word_treatment: {slide_blueprint.get('hero_word_treatment')}",
        f"  color_role:          {slide_blueprint.get('color_role')}",
        f"  inverted:            {slide_blueprint.get('inverted', False)}",
        "",
        "PREVIOUS SLIDE HTML (for visual continuity reference):",
        previous_html or "(this is the first slide; no previous HTML)",
        "",
        LAYOUT_MOVES_GUIDE,
        "",
        "REQUIREMENTS:",
        '- Output ONLY a JSON object: {"html": "<your html body string>"}',
        '- Your HTML goes INSIDE a <div class="slide"> wrapper that is already present; do not include the wrapper.',
        "- Use ONLY CSS variables for color and font-family. Never use raw hex literals.",
        "- Use the typographic role classes (.t-display, .t-mega, .t-stat, .t-h1, .t-h2, .t-h3, .t-pullquote, .t-eyebrow, .t-scripture-ref, .t-dropcap, .t-body, .t-body-lg, .t-body-sm) and utilities (.u-track-tight, .u-track-loose, .u-track-wide, .u-italic, .u-caps, .u-lower, .u-tnum).",
        "- The hero_word_treatment dict tells you exactly which shifts to apply to the hero word — apply them exactly.",
        f"- Cite the layout move in a comment at the top: <!-- move: {slide_blueprint['layout_move']} -->",
        "- Text-safe zones: top 135px, sides 86px, bottom 270px.",
        "- No background images. Solid brand-color backgrounds only.",
        "",
    ]
    if retry_violations:
        sections.append(retry_violations)
        sections.append("")
    sections.append("OUTPUT (JSON only, no preamble):")
    return "\n".join(sections)


def compile_slide(
    *,
    slide_blueprint: dict,
    palette: dict,
    pairing_id: str,
    pairing: dict,                # full pairing dict from font library (for family names)
    n_total: int,
    previous_html: Optional[str],
) -> DesignerResult:
    """Compile one slide blueprint into HTML."""
    from aurealis_carousel.token_validate import check

    retry_violations: Optional[str] = None

    for attempt in range(MAX_RETRIES + 1):
        prompt = _build_prompt(
            slide_blueprint=slide_blueprint,
            palette=palette,
            pairing_id=pairing_id,
            pairing_family_heading=pairing["heading"]["family"],
            pairing_family_body=pairing["body"]["family"],
            n_total=n_total,
            previous_html=previous_html,
            retry_violations=retry_violations,
        )
        response = query_json(prompt)
        last_html = response.get("html", "")

        if not last_html.strip():
            retry_violations = (
                "Previous attempt failed validation. Violations:\n"
                "  - [missing-html] response did not include a non-empty 'html' field\n"
                "Regenerate using only CSS variables for color and font-family."
            )
            continue

        result = check(last_html, palette)
        if result.ok:
            return DesignerResult(html=last_html, retries=attempt, fallback=False)
        retry_violations = result.format_for_retry()

    # Fallback — use SlideContent shape from blueprint for the safe minimal layout
    fallback_slide = SlideContent(
        i=slide_blueprint["i"], type=slide_blueprint["type"],
        headline=slide_blueprint.get("headline", ""),
        body=slide_blueprint.get("body", ""),
        label=slide_blueprint.get("label"),
    )
    return DesignerResult(html=_safe_minimal_html(fallback_slide),
                          retries=MAX_RETRIES + 1, fallback=True)
```

Also delete the OLD `generate_slide` function (the one with `brand=, brand_css=, pairing=, emphasis_font=, slide=SlideContent, ...` signature). Keep `compile_slide` as the new entry point.

- [ ] **Step 2: Update `tests/test_designer.py`**

Read the existing file. The existing tests call the old `generate_slide`. Replace those with calls to `compile_slide` and pass a slide blueprint dict instead of SlideContent. Where existing tests use `brand_css`, replace with `palette`.

```bash
cat tests/test_designer.py
```

Expected pattern: any test that mocks `query_json` and calls `generate_slide(...)` should be updated to call `compile_slide(slide_blueprint=..., palette=..., pairing_id=..., pairing=..., n_total=..., previous_html=...)`. Where the old test passed `brand={"design": {"colors": {...}}}`, replace with `palette={"bg": "#0A0A0A", ...}`.

- [ ] **Step 3: Run designer tests**

```bash
pytest tests/test_designer.py -v
```

Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add aurealis_carousel/designer.py tests/test_designer.py
git commit -m "refactor: designer is now an HTML compiler from writer blueprint"
```

---

### Task 11: Expand `critique.py` with new judgment axes + loop support

**Files:**
- Modify: `aurealis_carousel/critique.py`
- Modify: `tests/test_critique.py`

- [ ] **Step 1: Update `CritiqueResult` dataclass**

In `aurealis_carousel/critique.py`, replace `CritiqueResult` to include the new axes:

```python
@dataclass
class CritiqueResult:
    carousel_assessment: dict   # now includes palette_appropriateness,
                                # brand_recognizability, creative_notes_honesty
    subtraction_test_findings: str
    peer_test_verdict: str
    algorithm_test_verdict: str
    per_slide: list
    must_revise_slides: list
    overall_recommendation: str   # "SHIP" or "REVISE"
```

(Just add fields if your IDE auto-completes; the schema in `critique_carousel` is what enforces it.)

- [ ] **Step 2: Update `_build_prompt`**

Find the JSON schema in `_build_prompt` (in the current `critique.py:73-101` region). Add the three new keys to `carousel_assessment`:

```python
# In the docstring shown to Claude inside _build_prompt:
#
# "carousel_assessment": {
#   "cohesion": "PASS|REVISE",
#   "motif_consistency": "PASS|REVISE",
#   "narrative_arc_clarity": "PASS|REVISE",
#   "cta_bridge_effectiveness": "PASS|REVISE",
#   "type_pairing_appropriateness": "PASS|REVISE",
#   "palette_appropriateness": "PASS|REVISE",       // does the writer-invented palette serve the topic+brand?
#   "brand_recognizability": "PASS|REVISE",          // does this look like the brand's recent carousels?
#   "creative_notes_honesty": "PASS|REVISE"          // do the writer's notes honestly justify the choices?
# }
```

Update the prompt text to mention these three new axes explicitly and to instruct the critic to consult the writer's `creative_notes` (which means the prompt needs to receive it).

Add a new parameter to `_build_prompt` and `critique_carousel`: `writer_creative_notes: str` and `palette: dict`. Inject them into the prompt:

```python
# (excerpt — add to the prompt body)
WRITER'S CREATIVE NOTES (the writer's own justification for the pairing + palette + per-slide moves — judge whether this reads as honest or as backfilled rationalization):
{writer_creative_notes}

WRITER-INVENTED PALETTE (judge whether these colors serve the topic and read as on-brand):
{yaml.safe_dump(palette, sort_keys=False)}
```

- [ ] **Step 3: Update test_critique.py mocked responses**

Open `tests/test_critique.py`, find the mocked `critique_carousel` responses, and add the three new keys to the `carousel_assessment` block of each mock. Also update calls to `critique_carousel` to pass the new `writer_creative_notes` and `palette` kwargs.

```bash
cat tests/test_critique.py
```

- [ ] **Step 4: Add a new test for the writer-notes axis**

Append:

```python
def test_critic_flags_dishonest_creative_notes():
    from unittest.mock import patch
    from aurealis_carousel import critique
    mock_response = {
        "carousel_assessment": {
            "cohesion": "PASS",
            "motif_consistency": "PASS",
            "narrative_arc_clarity": "PASS",
            "cta_bridge_effectiveness": "PASS",
            "type_pairing_appropriateness": "PASS",
            "palette_appropriateness": "PASS",
            "brand_recognizability": "PASS",
            "creative_notes_honesty": "REVISE",
        },
        "subtraction_test_findings": "...",
        "peer_test_verdict": "PASS",
        "algorithm_test_verdict": "PASS",
        "per_slide": [],
        "must_revise_slides": [1],
        "overall_recommendation": "REVISE",
    }
    with patch("aurealis_carousel.critique.query_json", return_value=mock_response):
        result = critique.critique_carousel(
            brand={"brief": ""},
            strategist_spec={},
            rendered_pngs=[],
            playbook_voice="", playbook_typography="",
            playbook_layout="", playbook_conversion="",
            writer_creative_notes="post-hoc fluff",
            palette={"bg": "#000000", "text": "#FFFFFF", "text_muted": "#888888", "accent": "#FF0000"},
        )
    assert result.overall_recommendation == "REVISE"
    assert 1 in result.must_revise_slides
```

- [ ] **Step 5: Run critique tests**

```bash
pytest tests/test_critique.py -v
```

- [ ] **Step 6: Commit**

```bash
git add aurealis_carousel/critique.py tests/test_critique.py
git commit -m "feat: critic adds palette/brand/notes-honesty axes; takes writer notes"
```

---

### Task 12: Modify `persist.py` to save visual references

**Files:**
- Modify: `aurealis_carousel/persist.py`
- Modify: `tests/test_persist.py`

After persisting metadata + history, copy the rendered hook slide (slide 1) and the climax slide PNG to `history/<brand_name>/visual_refs/<topic_slug>/`. The climax slide index needs to be inferred from the per-slide types (which the orchestrator passes via a new input).

- [ ] **Step 1: Add fields to PersistInputs**

In `aurealis_carousel/persist.py`, add to `PersistInputs`:

```python
@dataclass
class PersistInputs:
    # ... existing fields ...
    slide_types: list[str] = None       # NEW: per-slide type strings, used to find climax
    visual_refs_root: Optional[Path] = None  # NEW: history/<brand>/visual_refs/ (orchestrator builds it)
```

Add a finalize step:

```python
def _save_visual_refs(inputs: PersistInputs) -> None:
    if not inputs.visual_refs_root or not inputs.slide_types:
        return
    ref_dir = inputs.visual_refs_root / inputs.topic_slug
    ref_dir.mkdir(parents=True, exist_ok=True)

    # hook = slide 0
    if inputs.slide_paths:
        hook_dest = ref_dir / inputs.slide_paths[0].name
        hook_dest.write_bytes(inputs.slide_paths[0].read_bytes())

    # climax = first slide whose type == "climax"
    try:
        climax_idx = next(i for i, t in enumerate(inputs.slide_types) if t == "climax")
        climax_src = inputs.slide_paths[climax_idx]
        climax_dest = ref_dir / climax_src.name
        climax_dest.write_bytes(climax_src.read_bytes())
    except (StopIteration, IndexError):
        # no climax tagged or out of range; skip — not fatal
        pass


def finalize(inputs: PersistInputs) -> None:
    # ... existing logic (caption, metadata, history append, auto-commit) ...
    _save_visual_refs(inputs)
```

- [ ] **Step 2: Add test for visual refs save**

Append to `tests/test_persist.py`:

```python
def test_persist_saves_visual_refs(tmp_path):
    from aurealis_carousel.persist import finalize, PersistInputs

    # Create fake slide PNGs
    slide1 = tmp_path / "slide-01.png"
    slide1.write_bytes(b"\x89PNG\r\nfake-hook")
    slide4 = tmp_path / "slide-04.png"
    slide4.write_bytes(b"\x89PNG\r\nfake-climax")

    visual_refs = tmp_path / "visual_refs"
    history_path = tmp_path / "history.yaml"
    output_dir = tmp_path / "outputs"

    inputs = PersistInputs(
        brand_name="TEST", topic="t", topic_slug="t-slug",
        scripture_lane=None, verse=None,
        frame="PAS", voice_mode="guide",
        type_pairing_id="x", emphasis_font=None,
        arc_thesis="", motif="",
        composition_pattern=[],
        slide_count=4,
        slide_paths=[slide1, tmp_path/"slide-02.png", tmp_path/"slide-03.png", slide4],
        slide_types=["hook", "body", "body", "climax"],
        caption="cap",
        hashtags=[],
        warnings={}, retries={},
        output_dir=output_dir,
        history_path=history_path,
        repo_root=tmp_path,
        auto_commit=False,
        visual_refs_root=visual_refs,
    )

    # slide-02 and 03 don't need to exist for visual_refs save (only hook + climax)
    for p in inputs.slide_paths[1:-1]:
        p.write_bytes(b"x")

    finalize(inputs)

    saved = list((visual_refs / "t-slug").iterdir())
    saved_names = {p.name for p in saved}
    assert "slide-01.png" in saved_names
    assert "slide-04.png" in saved_names
```

- [ ] **Step 3: Run persist tests**

```bash
pytest tests/test_persist.py -v
```

- [ ] **Step 4: Commit**

```bash
git add aurealis_carousel/persist.py tests/test_persist.py
git commit -m "feat: persist saves hook + climax PNGs to visual_refs/<slug>/"
```

---

## PHASE D — Wire-up

### Task 13: Create `orchestrator_v2.py`

**Files:**
- Create: `aurealis_carousel/orchestrator_v2.py`
- Test: `tests/test_orchestrator_v2.py`

- [ ] **Step 1: Write integration test (mocked Claude)**

```python
"""tests/test_orchestrator_v2.py"""
from pathlib import Path
from unittest.mock import patch

import yaml


def _write_minimal_brand(tmp_path: Path, name: str = "_smoketest"):
    brand_dir = tmp_path / "brands" / name
    brand_dir.mkdir(parents=True)
    (brand_dir / "brief.yaml").write_text(yaml.safe_dump({
        "brand_name": name,
        "app_name": "TestApp",
        "brief": "Test brand for orchestrator integration. Voice is plain. Visuals are minimal monochrome with a single warm gold accent.",
        "slide_count_range": [5, 5],
        "hashtag_count_range": [8, 12],
    }))
    return brand_dir


def test_orchestrator_v2_wires_full_pipeline(tmp_path, monkeypatch):
    """Smoke-test: mocked Claude responses for every phase; verify pipeline runs end-to-end and produces PNG paths."""
    from aurealis_carousel import orchestrator_v2

    # Mocks for each phase
    mock_angles = {"angles": [
        {"topic": "T", "topic_slug": "t", "hook_intent": "h",
         "arc_thesis": "a", "frame": "PAS", "voice_mode": "guide",
         "emotional_register": "monumental"} for _ in range(10)
    ]}
    mock_critic = {"winning_index": 0, "reasoning": "best"}
    mock_blueprint = {
        "topic": "T", "topic_slug": "t",
        "frame": "PAS", "voice_mode": "guide",
        "pairing_id": "<PICK-AN-ID-FROM-LIBRARY>",
        "palette": {"bg": "#0A0A0A", "text": "#F0E6D6",
                    "text_muted": "#6B6B6B", "accent": "#A67C2E"},
        "slides": [
            {"i": 1, "type": "hook", "headline": "T", "body": "", "label": None,
             "hero_word": "T", "layout_move": "MEGA-WORD REST",
             "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                     "scale_shift": "mega", "weight_shift": None,
                                     "family_shift": None},
             "color_role": "x", "inverted": False},
            {"i": 2, "type": "body", "headline": "Two", "body": "...",
             "label": None, "hero_word": None,
             "layout_move": "EYEBROW / HERO / TAGLINE STACK",
             "hero_word_treatment": None, "color_role": "x", "inverted": False},
            {"i": 3, "type": "body", "headline": "Three", "body": "...",
             "label": None, "hero_word": None,
             "layout_move": "ROMAN NUMERAL CHAPTER MARKER",
             "hero_word_treatment": None, "color_role": "x", "inverted": False},
            {"i": 4, "type": "climax", "headline": "Govern.", "body": "",
             "label": None, "hero_word": "Govern",
             "layout_move": "MEGA-WORD REST",
             "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                     "scale_shift": "mega", "weight_shift": None,
                                     "family_shift": None},
             "color_role": "x", "inverted": False},
            {"i": 5, "type": "cta", "headline": "Download TestApp",
             "body": "tag", "label": None, "hero_word": None,
             "layout_move": "ALL-CAPS HERO + LOWERCASE TAGLINE",
             "hero_word_treatment": None, "color_role": "x", "inverted": False},
        ],
        "caption": {
            "first_125_chars": "T - hook tagline",
            "full": "T - hook tagline full",
            "hashtags": ["#a", "#b", "#c", "#d", "#e", "#f", "#g", "#h"],
        },
        "creative_notes": "Plain test mock"
    }
    # Patch in the first available pairing id from the library
    import yaml as _yaml
    lib = _yaml.safe_load((Path(__file__).parent.parent / "fonts" / "library.yaml").read_text())
    mock_blueprint["pairing_id"] = lib["pairings"][0]["id"]

    mock_designer = {"html": '<div class="t-mega" style="color: var(--color-text);">T</div>'}
    mock_critic_visual = {
        "carousel_assessment": {
            "cohesion": "PASS", "motif_consistency": "PASS",
            "narrative_arc_clarity": "PASS", "cta_bridge_effectiveness": "PASS",
            "type_pairing_appropriateness": "PASS",
            "palette_appropriateness": "PASS", "brand_recognizability": "PASS",
            "creative_notes_honesty": "PASS",
        },
        "subtraction_test_findings": "", "peer_test_verdict": "PASS",
        "algorithm_test_verdict": "PASS", "per_slide": [],
        "must_revise_slides": [], "overall_recommendation": "SHIP"
    }

    brand_dir = _write_minimal_brand(tmp_path)
    monkeypatch.setattr(orchestrator_v2, "BRANDS_DIR", tmp_path / "brands")
    monkeypatch.setattr(orchestrator_v2, "HISTORY_DIR", tmp_path / "history")

    # Stub render to not actually launch Chromium
    def fake_render(*, slide_body, brand_css_path, slide_shell_path, output_path, pairing_font_faces=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x89PNG\r\nfake")
        return output_path
    monkeypatch.setattr(orchestrator_v2.render_mod, "render_slide", fake_render)

    call_counter = {"n": 0}
    def fake_query_json(prompt, **kw):
        call_counter["n"] += 1
        # Route by content of prompt — crude but works for a smoke test
        if "10 distinct angles" in prompt or "ANGLE GENERATOR" in prompt.upper() or '"angles"' in prompt.lower():
            return mock_angles
        if "CANDIDATE ANGLES" in prompt or "winning_index" in prompt:
            return mock_critic
        if "Script + Style Writer" in prompt or "SCRIPT" in prompt and "WRITER" in prompt:
            return mock_blueprint
        if "COMPILING slide" in prompt:
            return mock_designer
        if "carousel_assessment" in prompt or "must_revise_slides" in prompt:
            return mock_critic_visual
        return mock_designer  # fallback — designer is the most-called

    monkeypatch.setattr("aurealis_carousel.angles.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.angle_critic.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.writer.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.designer.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.critique.query_json", fake_query_json)

    paths = orchestrator_v2.run(brand_name="_smoketest", output_root=tmp_path / "outputs")
    assert len(paths) == 5
    for p in paths:
        assert p.exists()
```

- [ ] **Step 2: Run, expect failure**

```bash
pytest tests/test_orchestrator_v2.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `aurealis_carousel/orchestrator_v2.py`**

```python
"""Content-driven carousel pipeline.

Replaces orchestrator.py (the strategist-based pipeline). Wires:
  1. angles.generate_angles -> 10 candidate angles
  2. angle_critic.pick_winner -> 1 chosen index
  3. writer.generate -> full blueprint JSON
  4. designer.compile_slide -> HTML per slide
  5. render.render_slide -> PNG per slide
  6. critique.critique_carousel -> SHIP|REVISE
  7. (loop) re-compile flagged slides up to 2 revision rounds
  8. persist.finalize -> caption.txt + metadata.yaml + history append +
     visual_refs save

All Claude calls run on Opus per the spec (claude_cli default model).
"""
import tempfile
from pathlib import Path
from typing import Optional

import yaml

from aurealis_carousel import angle_critic as angle_critic_mod
from aurealis_carousel import angles as angles_mod
from aurealis_carousel import critique as critique_mod
from aurealis_carousel import css_compile
from aurealis_carousel import designer as designer_mod
from aurealis_carousel import font_faces
from aurealis_carousel import persist as persist_mod
from aurealis_carousel import render as render_mod
from aurealis_carousel import writer as writer_mod

REPO_ROOT = Path(__file__).parent.parent
BRANDS_DIR = REPO_ROOT / "brands"
FONTS_LIBRARY = REPO_ROOT / "fonts" / "library.yaml"
PLAYBOOK_DIR = REPO_ROOT / "playbook"
TEMPLATE_SHELL = REPO_ROOT / "templates" / "slide-shell.html"
HISTORY_DIR = REPO_ROOT / "history"
MAX_REVISION_ROUNDS = 2


def _load_playbook() -> dict[str, str]:
    pb: dict[str, str] = {}
    if PLAYBOOK_DIR.exists():
        for f in PLAYBOOK_DIR.glob("*.md"):
            pb[f.name] = f.read_text()
    return pb


def _collect_visual_refs(brand_visual_refs_root: Path, max_carousels: int = 5) -> list[str]:
    """Return absolute paths of PNGs in the most recent <=max_carousels visual_refs subdirs,
    plus any in the golden/ dir."""
    paths: list[str] = []
    if brand_visual_refs_root.exists():
        subdirs = sorted(
            [d for d in brand_visual_refs_root.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )[:max_carousels]
        for d in subdirs:
            paths.extend(str(p.resolve()) for p in sorted(d.glob("*.png")))
    golden = brand_visual_refs_root.parent / "golden" if brand_visual_refs_root.name == "visual_refs" else None
    if golden and golden.exists():
        paths.extend(str(p.resolve()) for p in sorted(golden.glob("*.png")))
    return paths


def run(
    *,
    brand_name: str,
    user_topic_hint: Optional[str] = None,
    output_root: Optional[Path] = None,
    history_path: Optional[Path] = None,
    auto_commit: bool = False,
) -> list[Path]:
    """Run the v2 pipeline end-to-end; return list of slide PNG paths."""
    output_root = Path(output_root) if output_root else REPO_ROOT / "outputs"
    history_path = (Path(history_path) if history_path
                    else HISTORY_DIR / f"{brand_name}.yaml")
    brand_history_dir = HISTORY_DIR / brand_name
    visual_refs_root = brand_history_dir / "visual_refs"

    brand = yaml.safe_load((BRANDS_DIR / brand_name / "brief.yaml").read_text())
    library = yaml.safe_load(FONTS_LIBRARY.read_text())
    playbook = _load_playbook()

    history = (yaml.safe_load(history_path.read_text()) or []) if history_path.exists() else []
    recent_slugs = [h.get("slug", "") for h in history[-14:]]

    # PHASE 1 — Angles
    angles_list = angles_mod.generate_angles(
        brand=brand, playbook=playbook, history=history,
        user_topic_hint=user_topic_hint,
    )

    # PHASE 2 — Angle critic
    winning_idx = angle_critic_mod.pick_winner(
        angles_list=angles_list, brand=brand, playbook=playbook,
    )
    winning_angle = angles_list[winning_idx]

    # PHASE 3 — Writer
    visual_refs = _collect_visual_refs(visual_refs_root)
    blueprint = writer_mod.generate(
        winning_angle=winning_angle, brand=brand, library=library,
        playbook=playbook, visual_ref_paths=visual_refs,
        recent_slugs=recent_slugs,
    )

    # Resolve pairing object + build font-faces block
    pairing = next(p for p in library["pairings"] if p["id"] == blueprint["pairing_id"])
    pairing_font_faces = font_faces.build_font_faces(
        pairing, emphasis_font=None, repo_root=REPO_ROOT, library=library,
    )

    # Compile per-carousel CSS to a temp file
    carousel_css = css_compile.compile_carousel_css(blueprint["palette"])
    output_dir = output_root / brand_name / blueprint["topic_slug"]
    output_dir.mkdir(parents=True, exist_ok=True)
    css_tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".css", delete=False, dir=output_dir
    )
    css_tmp.write(carousel_css)
    css_tmp.close()
    brand_css_path = Path(css_tmp.name)

    # PHASE 4 — Designer (one call per slide)
    slide_paths: list[Path] = []
    warnings: dict = {}
    retries: dict = {}
    previous_html: Optional[str] = None

    for slide in blueprint["slides"]:
        des = designer_mod.compile_slide(
            slide_blueprint=slide,
            palette=blueprint["palette"],
            pairing_id=blueprint["pairing_id"],
            pairing=pairing,
            n_total=len(blueprint["slides"]),
            previous_html=previous_html,
        )
        if des.fallback:
            warnings[f"slide_{slide['i']}"] = "designer_fallback"
        if des.retries:
            retries[f"designer_slide_{slide['i']}"] = des.retries

        png_path = output_dir / f"slide-{slide['i']:02d}.png"
        try:
            render_mod.render_slide(
                slide_body=des.html,
                brand_css_path=brand_css_path,
                slide_shell_path=TEMPLATE_SHELL,
                output_path=png_path,
                pairing_font_faces=pairing_font_faces,
            )
        except Exception as e:
            warnings[f"slide_{slide['i']}_render_error"] = str(e)[:200]
            raise

        slide_paths.append(png_path)
        previous_html = des.html

    # PHASE 5 — Visual critic + bounded revision loop
    crit = None
    for round_n in range(1 + MAX_REVISION_ROUNDS):  # initial + up to 2 revisions
        try:
            crit = critique_mod.critique_carousel(
                brand=brand,
                strategist_spec={
                    "topic": blueprint["topic"],
                    "topic_slug": blueprint["topic_slug"],
                    "frame": blueprint["frame"],
                    "voice_mode": blueprint["voice_mode"],
                    "type_pairing_id": blueprint["pairing_id"],
                    "narrative_arc": {"slides": blueprint["slides"]},
                },
                rendered_pngs=slide_paths,
                playbook_voice=playbook.get("06-voice.md", ""),
                playbook_typography=playbook.get("04-typography.md", ""),
                playbook_layout=playbook.get("05-layout.md", ""),
                playbook_conversion=playbook.get("03-conversion.md", ""),
                writer_creative_notes=blueprint.get("creative_notes", ""),
                palette=blueprint["palette"],
            )
        except Exception as e:
            warnings[f"critic_round_{round_n}_error"] = str(e)[:200]
            break

        if crit.overall_recommendation == "SHIP" or not crit.must_revise_slides:
            break
        if round_n == MAX_REVISION_ROUNDS:
            warnings["critic_revision_cap_hit"] = (
                f"Auto-shipped after {MAX_REVISION_ROUNDS} revision rounds; "
                f"still flagged slides: {list(crit.must_revise_slides)}"
            )
            break

        # Revise flagged slides
        for revise_i in crit.must_revise_slides:
            try:
                idx = next(
                    k for k, s in enumerate(blueprint["slides"]) if s["i"] == revise_i
                )
            except StopIteration:
                continue
            slide = blueprint["slides"][idx]
            # We don't persist HTML between runs, so revisions don't get the
            # visual-continuity reference — acceptable trade-off.
            rev = designer_mod.compile_slide(
                slide_blueprint=slide,
                palette=blueprint["palette"],
                pairing_id=blueprint["pairing_id"],
                pairing=pairing,
                n_total=len(blueprint["slides"]),
                previous_html=None,
            )
            if rev.fallback:
                warnings[f"slide_{slide['i']}_round_{round_n + 1}"] = "designer_fallback"
            png_path = slide_paths[idx]
            render_mod.render_slide(
                slide_body=rev.html,
                brand_css_path=brand_css_path,
                slide_shell_path=TEMPLATE_SHELL,
                output_path=png_path,
                pairing_font_faces=pairing_font_faces,
            )

    # PHASE 6 — Persist
    slide_types = [s["type"] for s in blueprint["slides"]]
    composition_pattern = [s.get("layout_move", "") for s in blueprint["slides"]]
    inputs = persist_mod.PersistInputs(
        brand_name=brand_name,
        topic=blueprint["topic"],
        topic_slug=blueprint["topic_slug"],
        scripture_lane=None,
        verse=None,
        frame=blueprint["frame"],
        voice_mode=blueprint["voice_mode"],
        type_pairing_id=blueprint["pairing_id"],
        emphasis_font=None,
        arc_thesis=winning_angle.get("arc_thesis"),
        motif=winning_angle.get("emotional_register"),
        composition_pattern=composition_pattern,
        slide_count=len(slide_paths),
        slide_paths=slide_paths,
        caption=blueprint["caption"]["full"],
        hashtags=blueprint["caption"]["hashtags"],
        warnings=warnings,
        retries=retries,
        output_dir=output_dir,
        history_path=history_path,
        repo_root=REPO_ROOT,
        auto_commit=auto_commit,
        slide_types=slide_types,
        visual_refs_root=visual_refs_root,
    )
    persist_mod.finalize(inputs)

    # Clean up temp CSS file (it's already been used by render)
    brand_css_path.unlink(missing_ok=True)

    return slide_paths
```

- [ ] **Step 4: Run orchestrator_v2 test**

```bash
pytest tests/test_orchestrator_v2.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/orchestrator_v2.py tests/test_orchestrator_v2.py
git commit -m "feat: orchestrator_v2 wires angles->critic->writer->designer->critique loop"
```

---

### Task 14: Add `--v2` flag to CLI

**Files:**
- Modify: `aurealis_carousel/cli.py`

- [ ] **Step 1: Add flag and conditional routing**

In `aurealis_carousel/cli.py`, update `cmd_generate`:

```python
def cmd_generate(args) -> int:
    if args.v2:
        from aurealis_carousel.orchestrator_v2 import run as run_v2
        paths = run_v2(
            brand_name=args.brand,
            user_topic_hint=args.topic,
            output_root=Path(args.output_root) if args.output_root else None,
            history_path=Path(args.history_path) if args.history_path else None,
            auto_commit=args.auto_commit,
        )
    else:
        paths = run(
            brand_name=args.brand,
            user_topic_hint=args.topic,
            output_root=Path(args.output_root) if args.output_root else None,
            history_path=Path(args.history_path) if args.history_path else None,
            auto_commit=args.auto_commit,
        )
    print(f"Generated {len(paths)} slides:")
    for p in paths:
        print(f"  {p}")
    return 0
```

In `build_parser`, add the flag:

```python
gen.add_argument("--v2", action="store_true",
                 help="Use the content-driven pipeline (orchestrator_v2). Default uses legacy.")
```

- [ ] **Step 2: Verify with --help**

```bash
cd /Users/simongonzalez/Technologies_Aurealis/agent-carousel
python -m aurealis_carousel.cli generate --help
```

Expected: `--v2` listed in help output.

- [ ] **Step 3: Commit**

```bash
git add aurealis_carousel/cli.py
git commit -m "feat: CLI --v2 flag routes to content-driven pipeline"
```

---

## PHASE E — Brand migrations

### Task 15: Convert `brands/_test/brief.yaml` to prose format

**Files:**
- Modify: `brands/_test/brief.yaml`

- [ ] **Step 1: Replace the entire `brands/_test/brief.yaml` content**

```yaml
brand_name: "_test"
app_name: "TestApp"

brief: |
  TestApp is a neutral utility for decisive professionals. Reader psychology:
  they want clarity, not options. They're done with overthinking and want to
  decide quickly. They distrust hype and reward direct, unembellished writing.

  Voice: expert and calm. No fluff. Treat the reader as smart. Imperative
  verbs over hedging. Concrete examples over abstractions. Never use
  motivational-poster language ("you've got this," "level up,"
  "game-changer"). Never use synthetic intimacy ("hey friend," "between us").
  Never use hustle-coded language.

  Lines the brand never crosses: never promise outcomes; never invoke fear of
  missing out; never use shame as a motivator.

  Visual register: crisp editorial. High-contrast black on white, with a
  single muted accent color per carousel. Minimal, restrained, modernist.
  Sans-serif default with serif accents for emphasis only. Never neon, never
  pastel, never playful scripts. The visual mood is "thoughtful productivity
  tool, not lifestyle brand."

  CTA bridge: TestApp helps you stop overthinking and decide in 60 seconds.

  Carousel norms: 3-5 slides per carousel. Hashtags 8-12 total, mixing broad
  productivity tags with niche decision-science tags. Rotate frames and
  voice modes across recent carousels.

slide_count_range: [3, 5]
hashtag_count_range: [8, 12]
```

Note: no `content_guidelines_files` for the _test brand (there's no `marketing/` content for it).

- [ ] **Step 2: Verify file is valid YAML**

```bash
python -c "import yaml; print(yaml.safe_load(open('brands/_test/brief.yaml').read())['brand_name'])"
```

Expected: prints `_test`.

- [ ] **Step 3: Commit**

```bash
git add brands/_test/brief.yaml
git commit -m "feat: migrate brands/_test/brief.yaml to prose-context format"
```

(Do NOT delete `brands/_test/brand.css` yet — Phase G cleanup task.)

---

### Task 16: Convert `brands/ethos/brief.yaml` to prose format

**Files:**
- Modify: `brands/ethos/brief.yaml`

- [ ] **Step 1: Replace the entire file content**

Replace the whole file with this exact content:

```yaml
brand_name: ETHOS
app_name: ETHOS

brief: |
  ETHOS is an iOS app for young Christian men 18-25 caught between two
  failure modes of modern manhood — feral (Tate-coded, appetitive,
  rage-bait) and domesticated (porn-fed, soft, performative, no spine).
  They want a third thing: the governed man. ETHOS is the daily
  discipleship practice that builds him — one verse, one identity anchor,
  one rep per morning, matched to where the reader actually is.

  Reader psychology: they want to be the kind of man their future children
  will respect. They're tired of streaks they cannot keep. They're done
  auditioning and want to actually be him. They worry "she can tell, they
  all can tell." They want a path that's neither Tate nor soft.

  Voice: older brother across the table at 10pm — not a parent, not a
  cheerleader, not a TED talk. Direct, grounded, masculine, honest.
  Imperative verbs. Spatial and building metaphors. Scripture as weapon,
  not decoration — cite when it cuts. Identity language over behavior
  language ("become him" beats "do this"). Apex, not alpha. Ruthless with
  self, gentle with others.

  Voice to never fall into: pseudo-spiritual leverage (the universe
  rewards, blessed, manifest, divine alignment). Synthetic intimacy
  (bestie, let's dive in). Empty influencer-speak (level up, game-changer).
  Hustle-grindset Christianity (rise and grind, 5 AM club). Therapy-jargon-
  as-truth (hold space, lean into, your journey). Tate-coded language
  (alpha, high-value man, king). Domesticated church-camp (brother in
  Christ, let go and let God). Pinterest-Christian sentiment (you are
  enough, God has a plan). Prosperity easy-answers (trust God and it'll
  work out).

  Lines the brand never crosses: prosperity-gospel framing; shame as
  motivator; favorable comparison to other Christian apps; any single
  creator framed as the brand identity; accidentally recruiting the feral
  or domesticated audience (the faith signal must be legible in the hook);
  Pinterest-Christian aesthetic.

  Visual register: obsidian + warm gold. Editorial, cinematic — like a
  feature in a print magazine for men, not a content library to browse.
  Dark backgrounds, restrained palettes, high contrast. Serifs lead;
  condensed sans support. Never pastels, never neon, never playful scripts.
  One accent per carousel; never two competing accents. A weapon picked up
  for the day.

  CTA bridge: "ETHOS builds that man one morning at a time. One verse, one
  identity anchor, one rep — matched to where you actually are." The app's
  surfaces the carousel can close on include Daily Anchor (verse +
  reflection + prayer — the primary close), AI Companion (chat that won't
  lie about Scripture), Streaks (consistency), 12-Tag Check-In (daily
  growth input), Weekly Snapshot (12-axis reflection), Radar Chart (premium
  growth viz), Onboarding Identity Anchors, Saved Verses.

  Carousel norms: 5-slide chassis is standard, up to 6 when a topic earns
  it. Hashtags 8-12, mixing broad faith tags with niche
  biblical-masculinity tags, avoiding prosperity / hustle / Tate-coded
  tags. Rotate voice modes and format archetypes across recent carousels
  rather than repeating.

slide_count_range: [5, 6]
hashtag_count_range: [8, 12]
content_guidelines_files:
  - marketing/guidelines/GENERAL_CONTENT_GUIDELINES
  - marketing/guidelines/CAROUSEL/guidelines.md
```

- [ ] **Step 2: Verify YAML loads**

```bash
python -c "import yaml; b = yaml.safe_load(open('brands/ethos/brief.yaml').read()); print(b['brand_name'], b['slide_count_range'])"
```

Expected: prints `ETHOS [5, 6]`.

- [ ] **Step 3: Commit**

```bash
git add brands/ethos/brief.yaml
git commit -m "feat: migrate brands/ethos/brief.yaml to prose-context format"
```

(Do NOT delete `brands/ethos/brand.css` yet.)

---

## PHASE F — Live runs

### Task 17: Live run on `_test` brand

- [ ] **Step 1: Verify dependencies are installed**

```bash
which claude            # Anthropic claude CLI
python -c "import playwright"
python -c "import jinja2, bs4, yaml"
```

Expected: all present. If claude is missing: install Claude Code first; this pipeline is unusable without it.

- [ ] **Step 2: Run the v2 pipeline against _test**

```bash
cd /Users/simongonzalez/Technologies_Aurealis/agent-carousel
python -m aurealis_carousel.cli generate _test --v2
```

Expected: terminates successfully with output like `Generated 3-5 slides:` followed by absolute paths.

- [ ] **Step 3: Inspect the output**

```bash
ls outputs/_test/
# Find the most recent topic dir
LATEST=$(ls -t outputs/_test/ | head -1)
ls -la "outputs/_test/$LATEST/"
cat "outputs/_test/$LATEST/metadata.yaml"
cat "outputs/_test/$LATEST/caption.txt"
```

Expected:
- Directory exists with N PNG files (`slide-01.png` ... `slide-NN.png`).
- `metadata.yaml` includes `composition_pattern` listing layout moves used.
- `caption.txt` has the full caption + hashtags.

Open a slide to eyeball:

```bash
open "outputs/_test/$LATEST/slide-01.png"
```

- [ ] **Step 4: Verify visual_refs were saved**

```bash
ls -la "history/_test/visual_refs/$LATEST/" 2>&1
```

Expected: 1-2 PNG files (slide-01 always, plus the climax slide if there was one and the slug matches the `LATEST` variable above — note the slug-vs-output-dir-name may differ; if the orchestrator writes to `outputs/<brand>/<topic_slug>` and visual_refs are also keyed by topic_slug, they should match).

- [ ] **Step 5: Commit the test run outputs (optional, for review)**

```bash
git add outputs/_test/ history/_test/
git commit -m "test: first v2 pipeline live run on _test brand"
```

- [ ] **Step 6: Note any failures + fix iteratively**

If the run failed at any phase: open `outputs/_test/<slug>/metadata.yaml` and read the `warnings` block. Common failure modes:
- `palette text vs bg contrast` — writer picked a bad palette; check the prompt; consider tightening the visual_context prose.
- `pairing_id not in font library` — writer hallucinated a pairing; check that the prompt shows the menu.
- `designer_fallback` for some slides — the designer hit its retry cap; check `outputs/.../slide-NN.png` to see if the fallback layout is acceptable.

Iterate on the writer/designer prompts as needed and re-run until at least one full carousel renders without `designer_fallback` warnings.

---

### Task 18: Live run on `ethos` brand

- [ ] **Step 1: Run v2 pipeline against ethos**

```bash
cd /Users/simongonzalez/Technologies_Aurealis/agent-carousel
python -m aurealis_carousel.cli generate ethos --v2
```

Expected: terminates successfully, produces 5-6 slides.

- [ ] **Step 2: Compare against current pipeline**

To compare, run the OLD pipeline on the same topic (or any topic):

```bash
python -m aurealis_carousel.cli generate ethos
LATEST_V1=$(ls -t outputs/ethos/ | head -1)
LATEST_V2=$(ls -td outputs/ethos/*/ | head -2 | tail -1)
echo "V1: $LATEST_V1"
echo "V2: $LATEST_V2"
open "outputs/ethos/$LATEST_V1/slide-01.png"
open "outputs/ethos/$LATEST_V2/slide-01.png"
```

Eyeball comparison: does the v2 slide look distinct from the v1 slide? Does it use a different pairing? Different palette tones? If they look identical, the writer prompt isn't pulling enough variation from the visual_context prose — iterate.

- [ ] **Step 3: Commit run outputs**

```bash
git add outputs/ethos/ history/ethos/
git commit -m "test: first v2 pipeline live run on ethos brand"
```

- [ ] **Step 4: Stop here — Phase G cleanup is gated on user review of both runs**

Do not proceed to Phase G until the user reviews the rendered carousels and approves promoting v2 to the default pipeline.

---

## PHASE G — Cleanup (gated on Phase F approval)

### Task 19: Delete `strategist.py` and legacy code paths

**Files:**
- Delete: `aurealis_carousel/strategist.py`
- Delete: `aurealis_carousel/orchestrator.py` (will be replaced)

- [ ] **Step 1: Verify no remaining imports reference strategist**

```bash
grep -rn "from aurealis_carousel.strategist" aurealis_carousel/ tests/
grep -rn "import strategist" aurealis_carousel/ tests/
```

Expected: NO matches. If any: those modules need updating.

- [ ] **Step 2: Delete files**

```bash
git rm aurealis_carousel/strategist.py
git rm aurealis_carousel/orchestrator.py
git rm tests/test_strategist.py
git rm tests/test_orchestrator.py        # the old one; v2 replaces it
git rm tests/test_orchestrator_live.py   # the old live test; v2 replaces it
```

- [ ] **Step 3: Commit deletions**

```bash
git commit -m "chore: remove legacy strategist + orchestrator (replaced by v2)"
```

---

### Task 20: Delete per-brand `brand.css` files

**Files:**
- Delete: `brands/_test/brand.css`
- Delete: `brands/ethos/brand.css`
- Delete: `brands/lokin/brand.css` (if exists)

- [ ] **Step 1: Verify all brands have prose-format briefs**

```bash
for b in brands/*/; do
  python -c "import yaml; b=yaml.safe_load(open('$b/brief.yaml').read()); assert 'brief' in b, '$b is not yet migrated'"
done
```

Expected: no errors.

- [ ] **Step 2: Delete the CSS files**

```bash
git rm brands/_test/brand.css
git rm brands/ethos/brand.css
git rm brands/lokin/brand.css 2>/dev/null || true
```

- [ ] **Step 3: Commit**

```bash
git commit -m "chore: remove per-brand brand.css (palette is now per-carousel)"
```

---

### Task 21: Promote `orchestrator_v2.py` → `orchestrator.py` and remove `--v2`

**Files:**
- Rename: `aurealis_carousel/orchestrator_v2.py` → `aurealis_carousel/orchestrator.py`
- Rename: `tests/test_orchestrator_v2.py` → `tests/test_orchestrator.py`
- Modify: `aurealis_carousel/cli.py` (remove `--v2`)

- [ ] **Step 1: Rename**

```bash
git mv aurealis_carousel/orchestrator_v2.py aurealis_carousel/orchestrator.py
git mv tests/test_orchestrator_v2.py tests/test_orchestrator.py
```

- [ ] **Step 2: Update CLI**

In `aurealis_carousel/cli.py`:
- Delete the `if args.v2: ... else: ...` branch in `cmd_generate`. Replace with a single call to the now-default `orchestrator.run(...)`.
- Delete the `gen.add_argument("--v2", ...)` line.
- The `from aurealis_carousel.orchestrator import run` at the top still works because we renamed v2 → orchestrator.

- [ ] **Step 3: Update doctor + any reference to legacy fields in CLI**

`cmd_doctor` currently reads `brief.get('voice', {}).get('voice_mode', {}).get('default')` etc. — those structural fields no longer exist. Simplify `cmd_doctor`:

```python
def cmd_doctor(args) -> int:
    brand_dir = BRANDS_DIR / args.brand
    if not brand_dir.exists() or not (brand_dir / "brief.yaml").exists():
        print(f"Brand '{args.brand}' not found at {brand_dir}", file=sys.stderr)
        return 5
    brief = yaml.safe_load((brand_dir / "brief.yaml").read_text())
    print(f"Brand: {args.brand}")
    print(f"  app_name:           {brief.get('app_name')}")
    print(f"  slide_count_range:  {brief.get('slide_count_range')}")
    print(f"  hashtag_count_range:{brief.get('hashtag_count_range')}")
    print(f"  brief length:       {len(brief.get('brief', ''))} chars")
    if not brief.get('brief'):
        print("  WARNING: brief is empty or missing")
        return 5
    return 0
```

- [ ] **Step 4: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add aurealis_carousel/orchestrator.py aurealis_carousel/cli.py tests/test_orchestrator.py
git commit -m "chore: promote orchestrator_v2 -> orchestrator; remove --v2 flag"
```

- [ ] **Step 6: Final smoke run**

```bash
python -m aurealis_carousel.cli generate _test
python -m aurealis_carousel.cli generate ethos
```

Expected: both succeed without `--v2` flag.

---

## Notes for the executing engineer

1. **TDD discipline**: every task with code has a failing-test → implementation → passing-test pattern. Don't skip the failing-test step — the failure confirms the test actually exercises the new code.

2. **Frequent commits**: every task ends with a commit. Don't bundle multiple tasks into one commit. If a task is too big to commit cleanly, it should have been split.

3. **The writer prompt is the most important prompt in the system** (Task 9). After the first live run on _test, expect to iterate on this prompt before the run on ethos. The writer is the creative center; everything else compiles its decisions.

4. **The `brands/_test/` brand is your testbed**. Use it freely to iterate. Don't iterate on ethos until _test produces an acceptable carousel.

5. **Phase G is gated**. After Phase F, STOP and let the user review. Phase G deletes legacy code and is irreversible without `git revert`.

6. **Don't skip the `--run-live` test conventions**. Existing tests use the `--run-live` flag for tests that hit real Claude. If you write new end-to-end tests during this work, mark them `@pytest.mark.live` so they don't run in normal CI.
