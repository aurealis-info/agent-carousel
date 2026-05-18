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

2. DROP-CAP OPENER — One paragraph of .t-body, with .t-dropcap on the wrapper so
   the first letter renders at .t-mega gold. No separate headline. The drop cap IS
   the design. Use sparingly — once per carousel max, typically slide 2.

3. ITALIC DISPLAY REST — Full-bleed quiet slide. ONE italic phrase set in
   .t-display-italic (168px, weight 400, italic), centered or left-aligned with
   generous breathing room. Optional .t-scripture-ref label below in tracked caps.
   Use for: scripture, thesis statement, single declarative truth.

4. EYEBROW / HERO / TAGLINE STACK — Three vertical zones with deliberate weight-leap
   rhythm: tiny .t-eyebrow caps (top), heavy .t-display or .t-h1 (middle), light
   .t-body-lg .u-italic .u-lower (bottom). Drumbeat → impact → echo.

5. VERTICAL RULE PULLQUOTE — Italic .t-pullquote (72px, italic, with 2px gold left
   rule, 36px padding-left). .t-scripture-ref label below in tracked caps. The
   scripture move. No headline above it — the quote IS the slide's voice.

6. HUNG INITIAL QUOTE — Oversized opening " or ' at .t-mega (240px) gold weight
   900, offset into the left margin. Body of the quote starts where the regular
   margin would be in .t-h2 italic. Magazine cover-feature move.

7. MEGA-WORD REST — One word set in .t-mega (240px), .u-track-tight, kerned tight.
   The full stop is mandatory and is part of the typography. No body. No subhead.
   Use for: one-word verdicts, identity claims, climaxes. Ex: "GOVERNED.", "RISE.",
   "FAST.", "ENOUGH."

8. ASYMMETRIC KICKER — Slide-number or section name set vertically along the left
   edge in .t-eyebrow (rotated -90deg via transform, .u-track-wide). Headline sits
   to its right in .t-h1 or .t-display. Forces the layout off the default centered
   axis. Reads "printed and bound."

9. ROMAN NUMERAL CHAPTER MARKER — Each non-hook slide opens with a Roman numeral
   ("I", "II", "III", "IV", "V") set in .t-h1 or .t-display gold weight 400, top-left.
   Slide title beneath in .t-h1 or .t-h2. Establishes the carousel as a chaptered
   document.

10. ALL-CAPS HERO + LOWERCASE TAGLINE — Hero in .t-display ALL CAPS (.u-caps
    .u-track-tight), tagline immediately beneath in .t-body-lg lowercase italic
    (.u-italic .u-lower), no caps. The case-leap is the whole design — masculine
    declaration → quiet underline.

SELECTION GUIDE:
- Hook slide (slide 1): MEGA-WORD REST | EYEBROW/HERO/TAGLINE STACK | ALL-CAPS HERO+TAGLINE
- Stat / data slide:    STAT DROP
- Scripture / quote:    ITALIC DISPLAY REST | VERTICAL RULE PULLQUOTE | HUNG INITIAL QUOTE
- Body / value tip:     DROP-CAP OPENER | EYEBROW/HERO/TAGLINE STACK | ROMAN NUMERAL CHAPTER
- Climax / verdict:     MEGA-WORD REST | ITALIC DISPLAY REST
- Bridge:               EYEBROW/HERO/TAGLINE STACK | ROMAN NUMERAL CHAPTER
- CTA:                  ALL-CAPS HERO+TAGLINE | EYEBROW/HERO/TAGLINE STACK

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
