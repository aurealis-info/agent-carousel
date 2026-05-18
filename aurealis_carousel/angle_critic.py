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
