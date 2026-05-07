# Aurealis Carousel — Text-First Instagram Carousel Generator

Generates brand-disciplined, text-first Instagram carousels for any app, with vision-based feedback. Runs locally, from inside Claude Code, or autonomously on Anthropic Routines.

## What it does

- **Strategist** writes the full creative spec for a carousel: topic, narrative arc, voice mode, type pairing, hero words, caption + hashtags.
- **Designer** generates per-slide HTML body using the brand's CSS sandbox + chosen font pairing.
- **Token validator** rejects anything that uses off-palette colors, off-list fonts, or off-scale type sizes — the brand's design system is mechanically enforced.
- **Renderer** composes the slide via Playwright → 1080×1350 PNG with proper local-font loading.
- **Layout-fit validator** measures every text element's bounding box vs. Instagram safe zones (top 135px, sides 86px, bottom 270px) + cramming + hero ratio + size minimums.
- **Vision critic** sees all rendered PNGs at once with strict adversarial framing — biased toward rejecting mediocrity.
- **Persist** writes caption.txt + metadata.yaml + history append + optional auto-commit + push.

No AI image generation. All visual interest comes from typography + color + composition + the 6 universal font pairings.

## Architecture

```
strategist (1 call) → for each slide:
  designer → token_validate → render → layout_check
→ critique (1 multimodal call sees all PNGs)
→ if must_revise_slides: 1 revision pass
→ persist
```

Total Claude calls per carousel: ~7-12 in the happy path.

## Install (local)

```bash
git clone git@github.com:aurealis-info/agent-carousel.git
cd agent-carousel
python3.12 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/playwright install chromium
```

## Usage

```bash
# Generate today's carousel for a brand
aurealis-carousel generate ethos

# With a specific topic
aurealis-carousel generate ethos --topic "Decisiveness at 5am"

# For autonomous runs (commits + pushes after success)
aurealis-carousel generate ethos --auto-commit

# Other commands
aurealis-carousel list-brands
aurealis-carousel doctor ethos
aurealis-carousel preview <slug-substring>
```

## Adding a new brand

1. Create `brands/<brand>/brief.yaml` (use `brands/ethos/` as full example, `brands/_test/` as minimal).
2. Create `brands/<brand>/brand.css` with the brand's design tokens (color palette + type scale).
3. Initialize `history/<brand>.yaml` with `[]`.
4. `aurealis-carousel doctor <brand>` validates everything is wired.

No code changes needed. The engine is brand-agnostic.

## Three execution surfaces

| Surface | When to use |
|---|---|
| Local CLI (`aurealis-carousel generate`) | Manual one-offs, debugging, creative iteration |
| Claude Code skill (`/carousel`) | "Make me one now" from inside any Claude Code session |
| Anthropic Routine | Autonomous daily runs — runs on Anthropic's cloud, no local machine needed |

All three run the same engine. Brand consistency comes from voice + design tokens + brand-specific banned words; not from rigid template enforcement.

## Tests

```bash
.venv/bin/pytest -v                      # unit + mocked-Claude tests
.venv/bin/pytest --run-live -v           # also run live tests against `_test` brand
```

## Spec & plan

- Spec: `docs/specs/2026-05-07-text-first-carousel-v2-design.md`
- Plan: `docs/plans/2026-05-07-text-first-carousel-v2-implementation.md`
- Research source: `docs/research/2026-05-07-deep-research-source.md`
