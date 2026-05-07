# Typography Playbook

Text-led carousels rely entirely on typographic architecture to convey emotion and authority. The designer applies these principles when laying out each slide; the vision critic checks that the carousel leans on its type system rather than coasting in flat monochrome.

## Font pairings

The strategist picks ONE primary pairing per carousel from `fonts/library.yaml`. Optionally, the strategist may name an `emphasis_font` borrowed from any pairing in the library — the designer applies it to ONE word per slide for hero emphasis.

Pairings exist on three vibe axes (see `fonts/library.yaml` for the full set):
- **Editorial** (Recoleta-Berthold, Avantgarde-Cooper) — opulence + historical credibility, magazine authority.
- **Modern Brutalist** (Inter-Tempting at high weight, Proximanova-Sailors with Sailors aggressive) — high-contrast, immediate attention.
- **Organic / Academic** (Citadel-Helvetica, Opensauce-Peacesans) — warm authority, mentorship.

**Why some pairings fail:** Bebas Neue + Lora — towering industrial sans-serif against delicate low-contrast calligraphic serif. X-heights clash; tonal weight disparity creates schizophrenic identity.

## Scale ratios — the 3:1 hero rule

Hierarchy at 1080×1350 portrait demands extreme mathematical contrast.

- **Minimum 3:1 H1-to-body ratio.** Standard word-processor ratios fail on mobile.
- **Grounded authority** layout: 90pt H1, 30pt body.
- **Brutalist shouty** layout: 120pt H1+, body still 30-32pt.
- **Body never below 30pt** — mobile legibility floor.

## Weight contrast

Pairing ultrabold + light succeeds **only when both weights are from the same family** (e.g., Recoleta-Black + Recoleta-Light). Same-family weight contrast establishes mathematical harmony + instant hierarchy.

Cross-family ultrabold + thin = tacky. Breaks structural unity, signals poor design discipline.

## Letter-spacing (tracking)

- **Eyebrows / kickers / section labels** (especially all-caps) — wide tracking +150 to +200. Injects air; premium aesthetic.
- **Body copy** — zero or slightly negative (-10). Pulls letterforms together; speeds saccadic reading.

## Stylistic treatments — when each elevates vs. cheapens

### Italic
- **Elevates** — isolating a single active verb in a headline; cadence shift.
- **Cheapens** — entire paragraphs in italic; eye strain.

### All-caps
- **Elevates** — brutalist 3-word hooks. High-impact short phrases.
- **Cheapens** — anything longer than one line. Exhausting to read.

### Tracked-out caps
- **Elevates** — small navigational elements ("SWIPE", "PART 1", "THE SOLUTION").
- **Cheapens** — long-form copy.

## Hero word treatment

Single-word visual shift within a monochromatic sentence. The word becomes the emotional anchor of the slide.

**Elevates** when applied to:
- One word per slide (the hero)
- The word that carries the slide's emotional weight (e.g., "DEBT" rendered crimson within a dark headline)
- Climax slides + at least 1-2 body slides per carousel

**Cheapens** when applied to:
- Multiple words arbitrarily (turns slide into a ransom note)
- Words that aren't the emotional anchor (no payoff)

Treatment options for the hero word (designer chooses one or combination):
- **Color shift** — distinct color from brand palette
- **Weight shift** — body 400 → hero 900
- **Size shift** — hero 1.5× surrounding text
- **Italic / all-caps shift**
- **Family shift within primary pairing** — heading font for hero, body font for the rest (or reverse)
- **Family shift via emphasis_font** — pulls a totally different family for ONE word ("Inter / *tempting*" treatment)

**Hero word treatment is expected, not optional.** A carousel of flat monochrome headlines is the default to revise.

## Reference creators

Reference creators known for typographic excellence (study their structural discipline + stylistic choices):

- **@stoicmindset0** — brutalist; high-contrast edge-to-edge sans-serifs; severe inverted palettes.
- **@sahilbloom** — editorial; massive deliberate white space; legible serif headers; clear hierarchy.
- **@thechrisdo** — left-aligned grid discipline; heavy Swiss-style; precise leading; aggressive scale.
- **@daniellepriestley** — organic serifs with soft pastels; rigid alignment for authority.
- **@themetashift** — kinetic type placement; scale shifts that physically guide the eye downward.
- **@nickhimo** — strict 3-zone layout adherence; no overlapping UI elements.
- **@iamashley.nawi** — dramatic typographic color inversion at the CTA bridge.
- **@mate_urbin** — expansive letter-spacing on micro-copy and kickers; premium feel.
- **@gerardadams** — Hero word treatment to anchor long-form copy.
- **@kickass_ux** — modular typographic blocks for digestible educational density.

## Typographic anti-patterns — auto-reject

1. **Centered body text** — Creates ragged left edges; eye searches every line; reading momentum dies.
2. **Inadequate leading** — Line-height so tight that descenders crash into ascenders below.
3. **Orphans and widows** — Single word abandoned on the final line of a paragraph.
4. **Font overloading** — More than 2 type families per carousel (3 max IF emphasis_font is in play).
5. **Low-contrast values** — Medium-grey on dark-grey; ignores accessibility; invisible outdoors.
