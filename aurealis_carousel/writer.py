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
        # Normalize move name: strip spaces around slashes so VALID_MOVES is the
        # canonical form (the LAYOUT_MOVES_GUIDE selection-guide section uses
        # a hyphen-form that doesn't match the numbered-list form exactly).
        move_normalized = re.sub(r"\s*/\s*", " / ", s.get("layout_move", "")).strip()
        if move_normalized not in VALID_MOVES:
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
- layout_move per slide must be VERBATIM one of: STAT DROP, DROP-CAP OPENER, ITALIC DISPLAY REST, EYEBROW / HERO / TAGLINE STACK, VERTICAL RULE PULLQUOTE, HUNG INITIAL QUOTE, MEGA-WORD REST, ASYMMETRIC KICKER, ROMAN NUMERAL CHAPTER MARKER, ALL-CAPS HERO + LOWERCASE TAGLINE.

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
