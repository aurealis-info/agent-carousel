"""Strategist phase — one Claude call returns full creative spec as JSON.

Hard rules enforced post-output (see spec §6 hard rules 1-14).
"""
import re
from dataclasses import dataclass
from typing import Optional

import yaml

from aurealis_carousel.claude_cli import query_json

VALID_VOICE_MODES = {"guide", "expert", "storyteller"}
VALID_COMPOSITIONS = {"billboard", "split-screen", "staircase", "monolith", "bullseye"}
VALID_FRAMES = {"PAS", "BAB", "AIDA", "principle-stack", "reveal", "story", "ladder"}


class ValidationError(Exception):
    pass


@dataclass
class StrategistResult:
    topic: str
    topic_slug: str
    frame: str
    voice_mode: str
    type_pairing_id: str
    emphasis_font: Optional[dict]
    creative_strategy_notes: str
    narrative_arc: dict
    caption: dict
    slide_count: int


def _pairing_ids(font_library: dict) -> set[str]:
    return {p["id"] for p in font_library["pairings"]}


def _parse_hashtag_range(brand: dict) -> tuple[int, int]:
    rule = brand.get("product", {}).get("hashtags", {}).get("stack_rule", "8-12 total")
    m = re.search(r"(\d+)\s*-\s*(\d+)", rule)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 8, 12


def _build_prompt(brand, font_library, history, user_topic_hint, playbook) -> str:
    pairings = "\n".join(
        f"- {p['id']}: {p['vibe']} (goals: {p['goals']})"
        for p in font_library["pairings"]
    )
    forbidden_pairings = brand.get("type_pairings", {}).get("forbidden", [])
    allowed_pairings = [p["id"] for p in font_library["pairings"] if p["id"] not in forbidden_pairings]
    default_pairing = brand.get("type_pairings", {}).get("default", allowed_pairings[0])
    forbidden_modes = brand.get("voice", {}).get("voice_mode", {}).get("forbidden", [])
    allowed_modes = [m for m in VALID_VOICE_MODES if m not in forbidden_modes]
    default_mode = brand.get("voice", {}).get("voice_mode", {}).get("default", "guide")
    h_min, h_max = _parse_hashtag_range(brand)
    sc = brand.get("narrative", {}).get("slide_count", {"min": 5, "max": 9})
    banned_words = brand.get("voice", {}).get("banned_words", [])
    recent_topics = [h.get("slug", "") for h in history[-14:]]
    user_topic_block = (
        f"USER-PROVIDED TOPIC (use VERBATIM as the carousel's topic): {user_topic_hint}\n"
        if user_topic_hint else ""
    )

    return f"""\
You are a senior creative director at a top-tier social-first agency. You have rejected hundreds of mediocre carousels this year — only the truly distinctive get a save. Your reputation depends on never letting a weak carousel through.

Apply the Subtraction Test, the Peer Test, and the Algorithm Test to every line you write (see VOICE PLAYBOOK below).

You are NOT a helpful assistant. You are a creative director with skin in the game.

BRAND: {brand['brand_name']}
APP CTA BRIDGE: "{brand['app']['cta_bridge_phrase']}"

VOICE PRINCIPLES:
{yaml.safe_dump(brand['voice']['principles'])}

BRAND-SPECIFIC HARD-REJECT WORDS (do NOT use these literal words/phrases):
{yaml.safe_dump(banned_words) if banned_words else '(none)'}

VOICE MODES AVAILABLE: {allowed_modes}
DEFAULT VOICE MODE FOR THIS BRAND: {default_mode}

TYPE PAIRINGS AVAILABLE (pick one based on topic emotion):
{pairings}

DEFAULT (BRAND ANCHOR): {default_pairing}
FORBIDDEN PAIRINGS FOR THIS BRAND: {forbidden_pairings if forbidden_pairings else '(none)'}

SLIDE COUNT RANGE: [{sc['min']}, {sc['max']}]; sweet spot {sc.get('sweet_spot', 7)}
HASHTAG COUNT RANGE: [{h_min}, {h_max}]
HASHTAG STACK RULE: "{brand.get('product', {}).get('hashtags', {}).get('stack_rule', '')}"

RECENT TOPIC SLUGS (LAST 14 — DO NOT REPEAT):
{recent_topics if recent_topics else '(none)'}

{user_topic_block}

HOOKS PLAYBOOK:
{playbook.get('01-hooks.md', '(none)')}

NARRATIVE PLAYBOOK:
{playbook.get('02-narrative.md', '(none)')}

CONVERSION PLAYBOOK:
{playbook.get('03-conversion.md', '(none)')}

VOICE PLAYBOOK:
{playbook.get('06-voice.md', '(none)')}

REQUIREMENTS:
- Hook (slide 1 headline) ≤ 6 words
- slides[0].type == "hook"; slides[-1].type == "cta"
- Exactly one slide with type "climax"; place at midpoint OR N-1
- density alternates loud/quiet; never 3 consecutive loud
- Caption.first_125_chars contains the hook trigram (3 consecutive content words from hook)
- CTA slide.headline contains "{brand['app']['name']}"
- Hashtag count in [{h_min}, {h_max}]
- type_pairing_id ∈ {allowed_pairings}
- voice_mode ∈ {allowed_modes}
- composition ∈ {sorted(VALID_COMPOSITIONS)} for every slide
- emphasis_font: null OR {{"from_pairing": "<library-id>", "family": "<family-name>", "role": "hero-word-only"}}

OUTPUT (JSON only, no preamble):
{{
  "topic": "...",
  "topic_slug": "kebab-case",
  "frame": "PAS|BAB|AIDA|principle-stack|reveal|story|ladder",
  "voice_mode": "guide|expert|storyteller",
  "type_pairing_id": "...",
  "emphasis_font": null,
  "creative_strategy_notes": "Why this frame, voice, pairing, and (if any) emphasis font",
  "narrative_arc": {{
    "thesis": "...", "motif": "...", "climax_position": "midpoint|N-1",
    "slides": [...]
  }},
  "caption": {{
    "first_125_chars": "...", "full": "...", "hashtags": ["#tag", ...]
  }}
}}
"""


def _validate(response: dict, brand: dict, font_library: dict, history: list) -> StrategistResult:
    arc = response["narrative_arc"]
    slides = arc["slides"]
    sc = brand.get("narrative", {}).get("slide_count", {"min": 5, "max": 9})
    if not (sc["min"] <= len(slides) <= sc["max"]):
        raise ValidationError(f"slide_count {len(slides)} outside [{sc['min']}, {sc['max']}]")

    hook_words = slides[0]["headline"].split()
    if len(hook_words) > 6:
        raise ValidationError(f"hook has {len(hook_words)} words; must be ≤ 6")

    if slides[0]["type"] != "hook":
        raise ValidationError("first slide must be type=hook")
    if slides[-1]["type"] != "cta":
        raise ValidationError("last slide must be type=cta")

    climax_count = sum(1 for s in slides if s["type"] == "climax")
    if climax_count != 1:
        raise ValidationError(f"exactly 1 climax slide required; got {climax_count}")

    valid_modes = {"guide", "expert", "storyteller"}
    forbidden_modes = brand.get("voice", {}).get("voice_mode", {}).get("forbidden", [])
    allowed_modes = valid_modes - set(forbidden_modes)
    if response["voice_mode"] not in allowed_modes:
        raise ValidationError(f"voice_mode {response['voice_mode']!r} not in allowed {sorted(allowed_modes)}")

    pairing_ids = _pairing_ids(font_library)
    forbidden_pairings = set(brand.get("type_pairings", {}).get("forbidden", []))
    if response["type_pairing_id"] not in pairing_ids - forbidden_pairings:
        raise ValidationError(f"type_pairing_id {response['type_pairing_id']!r} not in library or is forbidden")

    for slide in slides:
        if slide.get("composition") not in VALID_COMPOSITIONS:
            raise ValidationError(f"slide {slide['i']} composition {slide.get('composition')!r} invalid")

    # density alternation: never 4+ consecutive loud
    loud_streak = 0
    for s in slides:
        if s.get("density") == "loud":
            loud_streak += 1
            if loud_streak >= 4:
                raise ValidationError("density: 4+ consecutive 'loud' slides")
        else:
            loud_streak = 0

    cta = slides[-1]
    if brand["app"]["name"].lower() not in cta["headline"].lower():
        raise ValidationError(f"CTA slide headline must contain app name '{brand['app']['name']}'")

    h_min, h_max = _parse_hashtag_range(brand)
    if not (h_min <= len(response["caption"]["hashtags"]) <= h_max):
        raise ValidationError(f"hashtag count {len(response['caption']['hashtags'])} outside [{h_min}, {h_max}]")

    # Brand banned-words check (literal whole-word, case-insensitive)
    banned = brand.get("voice", {}).get("banned_words", [])
    text_blob = " ".join([
        response["topic"],
        " ".join(s.get("headline", "") + " " + s.get("body", "") + " " + (s.get("label") or "") for s in slides),
        response["caption"]["full"],
    ]).lower()
    for word in banned:
        if re.search(rf"\b{re.escape(word.lower())}\b", text_blob):
            raise ValidationError(f"brand banned word/phrase {word!r} appears in copy")

    # Caption first 125 chars contains hook trigram (3 consecutive content words)
    cap_window = response["caption"]["first_125_chars"][:125].lower()
    hook_content = re.findall(r"\w+", slides[0]["headline"].lower())
    if hook_content:
        trigram = " ".join(hook_content[:3])
        if trigram not in cap_window:
            raise ValidationError(f"caption first 125 chars must contain hook trigram {trigram!r}")

    # Topic not in recent 14 (compare slugs, case-insensitive)
    recent_slugs = {h.get("slug", "").lower() for h in history[-14:]}
    if response["topic_slug"].lower() in recent_slugs:
        raise ValidationError(f"topic_slug {response['topic_slug']!r} appears in recent history")

    return StrategistResult(
        topic=response["topic"],
        topic_slug=response["topic_slug"],
        frame=response["frame"],
        voice_mode=response["voice_mode"],
        type_pairing_id=response["type_pairing_id"],
        emphasis_font=response.get("emphasis_font"),
        creative_strategy_notes=response["creative_strategy_notes"],
        narrative_arc=arc,
        caption=response["caption"],
        slide_count=len(slides),
    )


def generate_strategy(*, brand, font_library, history, user_topic_hint, playbook) -> StrategistResult:
    prompt = _build_prompt(brand, font_library, history, user_topic_hint, playbook)
    response = query_json(prompt, allowed_tools=["Read"])
    return _validate(response, brand, font_library, history)
