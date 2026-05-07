# Layout Playbook

The designer applies these layout principles per slide. The layout-fit validator enforces the safe-zone geometry mechanically; this playbook governs the creative decisions inside the safe zone.

## The 3 zones of eye-tracking

At 4:5 portrait (1080×1350), the eye scans the canvas in a Z-pattern, dividing space into three cognitive zones:

- **Zone 1 — Upper-Middle Quadrant.** The anchor point. Eye lands here first immediately after swipe. **Headline / primary hook / key thesis goes here.**
- **Zone 2 — Center-Left.** Informational corridor. As the eye drops from the headline, it tracks the left margin. **Body copy / bullets / explanatory text aligns here.**
- **Zone 3 — Bottom-Right.** Exit terminal. The eye prepares to leave the slide. **Swipe cues, page numbers, or arrows anchor here.**

## Safe zones — Instagram UI overlays

The 1080×1350 canvas is plagued by IG UI overlays. Ignoring safe zones means critical text gets violently obscured.

- **Top 10% (~135-220px)** — DEAD. Username, profile picture, audio overlay sit here.
- **Sides 8% (~60-90px)** — padding buffer. Text past this margin feels crushed against bezel; claustrophobic.
- **Bottom 20% (~270-450px)** — DEAD. Caption preview + engagement icons (like, comment, share) + carousel progress dots overlay the bottom.

**Grid cropping rule:** Instagram crops 4:5 portrait down to 1:1 (1080×1080) for the profile grid preview. **All hook text must be vertically centered within the central 1080×1080 region** to prevent decapitation on the profile view.

## Asymmetric vs. centered alignment

- **Centered** projects stillness, formality, finality. Mathematically appropriate ONLY for: extremely brief quote slides, the climax slide (sometimes), and the final CTA slide.
- **Asymmetric (strictly left-aligned)** projects momentum, logic, informational density. The western eye reads left-to-right; a strong left-aligned vertical axis creates an invisible load-bearing wall that grounds text. Allows rapid consumption of large paragraphs without eye strain.

**Default to asymmetric left-aligned.** Reserve centered for the few cases above.

## White space discipline

Negative space is an active design element, not absence of content.

- **Quote / profound-statement slides** — ~60% white space. Elevates the text; projects premium positioning.
- **High-density educational slides** — minimum 30% white space, deployed as margins, gutters, paragraph leading. Prevents intimidating wall-of-text.

Whitespace is more often too little than too much in beginner work.

## Quiet vs. loud pacing

Carousel pacing requires aggressive modulation of visual volume.

- **Loud slide** — massive H1, edge-to-edge text, hero-word emphasis, accent color.
- **Quiet slide** — abundant white space, single sentence, calm.

A 10-slide carousel of all-loud slides exhausts optical processing by slide 4. The layout MUST alternate. After a high-density loud slide, a quiet reset slide gives the reader breathing room before the next data injection.

**Hard rule:** never stack 3+ loud slides consecutively.

## Dividers, kickers, section labels

Text-only carousels risk monotony. Architectural framing fixes this:

- **Dividers** — hairline rules spanning the safe zone width. Visual anchors between paragraphs or above kickers.
- **Kickers / eyebrows** — small, heavily tracked-out (+150 to +200) all-caps labels above the headline. Signal "this is what kind of content this is."
- **Section labels** — sequential top-band labels (e.g., "PART 3: EXECUTION"). Maintain frame continuity across slides; orient the reader through the swipe sequence.

## Five composition templates

The strategist names ONE composition per slide from this enum. Each has a defined "best used for" semantics.

### TEMPLATE 1 — Billboard
- **Geometry:** 80% top-heavy H1 text, 20% negative space at the bottom.
- **Best for:** Slide 1 hooks. Generates maximum thumb-stopping power in the feed.

### TEMPLATE 2 — Split-Screen
- **Geometry:** Harsh horizontal or vertical line dividing the canvas exactly at 50%.
- **Best for:** Comparison slides (Myth vs. Fact, Do This vs. Not That, Before / After).

### TEMPLATE 3 — Staircase
- **Geometry:** Staggered text blocks shifting from top-left to bottom-right.
- **Best for:** Process slides. Subconsciously guides the eye diagonally down.

### TEMPLATE 4 — Monolith
- **Geometry:** Strict left-aligned block covering the canvas, bounded by deep margins.
- **Best for:** High-density educational slides 3-6. Maximum readability for dense content.

### TEMPLATE 5 — Bullseye
- **Geometry:** Dead-center horizontal and vertical alignment, often with inverted background.
- **Best for:** Climax slide N-1, final CTA slide. Demands total focus; maximum visual weight.

## Layout anti-patterns — auto-reject

1. **Ignoring grid cropping** — Hook text outside the central 1080×1080 square gets truncated on the profile grid preview.
2. **Inconsistent horizon lines** — Y-axis of headline shifts arbitrarily across slides; text "jumps" jarringly during swipe.
3. **Margin violations** — Text bleeding into the bottom 270-450px dead zone; rendered illegible behind IG overlays.
