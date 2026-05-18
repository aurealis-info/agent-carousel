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
    angles_list: list[dict] = []
    for attempt in range(2):
        response = query_json(prompt, max_turns=3)
        angles_list = response.get("angles") or []
        if len(angles_list) >= 5:
            return angles_list
    raise AngleGenerationError(
        f"angle generator returned {len(angles_list)} angles after retry; need >=5"
    )
