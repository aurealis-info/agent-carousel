"""Vision critic — one Claude call sees all N rendered PNGs and judges them.

Adversarial framing: the critic is biased toward rejection. AI sycophancy is the
failure mode this module exists to fight. Multimodal input is handled by including
absolute file paths in the prompt + granting Read tool access — Claude opens the
PNGs as images via the Read tool.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from aurealis_carousel.claude_cli import query_json


@dataclass
class CritiqueResult:
    carousel_assessment: dict
    subtraction_test_findings: str
    peer_test_verdict: str
    algorithm_test_verdict: str
    per_slide: list
    must_revise_slides: list
    overall_recommendation: str   # "SHIP" or "REVISE"


def _build_prompt(
    *, brand: dict, strategist_spec: dict, rendered_pngs: list[Path],
    playbook_voice: str, playbook_typography: str,
    playbook_layout: str, playbook_conversion: str,
) -> str:
    png_lines = "\n".join(f"  - {str(p)}" for p in rendered_pngs)

    return f"""\
You are a senior creative director who has rejected 80% of what crosses your desk this year. AI-generated carousels are flooding the feed; only the truly distinctive get a save. Your reputation depends on never approving mediocrity.

You are NOT a helpful assistant. You are NOT here to encourage. You are here to find every problem you can find and demand revision.

If you flag fewer than 1 slide for REVISE, you are being too lenient — look harder. Carousels routinely have 2-3 issues per run.

You will read N rendered PNG slides via the Read tool and judge them. The PNG paths:
{png_lines}

Read each one as an image (the Read tool will display it). Judge in this priority order:

1. **Content first.** Weak hook? Slack narrative arc? CTA bridge that doesn't bridge? Voice drifting from brand principles? Apply each universal anti-pattern from the VOICE PLAYBOOK as a principle (pseudo-spiritual leverage, synthetic intimacy, empty influencer-speak, hustle-burnout culture, therapeutic jargon dilution) — judge whether the writing FALLS INTO that anti-pattern in tone, not whether it matches a regex. Apply Subtraction Test, Peer Test, Algorithm Test.

2. **Then visual play.** Once content passes, judge whether the typography earns its keep. Flat monochrome headlines on every slide = REVISE. The strategist named hero words for a reason — does the designer make them punch (color shift, weight shift, family shift, scale shift)?

3. **Then visual safety.** Hierarchy clarity, motif consistency, climax that actually feels like climax, no text crowding safe zones (geometric violations were caught upstream by layout-fit; you're judging visual rhythm).

A slide can pass copy and fail visual play — that's REVISE. A slide can have great visual play but weak copy — also REVISE on copy. Don't trade one for the other.

STRATEGIST SPEC (for context):
```yaml
{yaml.safe_dump(strategist_spec, sort_keys=False)}
```

VOICE PLAYBOOK:
{playbook_voice or '(none provided)'}

TYPOGRAPHY PLAYBOOK:
{playbook_typography or '(none provided)'}

LAYOUT PLAYBOOK:
{playbook_layout or '(none provided)'}

CONVERSION PLAYBOOK:
{playbook_conversion or '(none provided)'}

OUTPUT (JSON only, no preamble):
{{
  "carousel_assessment": {{
    "cohesion": "PASS|REVISE",
    "motif_consistency": "PASS|REVISE",
    "narrative_arc_clarity": "PASS|REVISE",
    "cta_bridge_effectiveness": "PASS|REVISE",
    "type_pairing_appropriateness": "PASS|REVISE"
  }},
  "subtraction_test_findings": "Which slides have padded copy that could survive deflation",
  "peer_test_verdict": "PASS|REVISE",
  "algorithm_test_verdict": "PASS|REVISE",
  "per_slide": [
    {{
      "i": <int>,
      "verdict": "PASS|REVISE",
      "violations": [
        {{
          "category": "hierarchy|fit|taste|content|voice|conversion",
          "severity": "blocking|preferred",
          "specifics": "...",
          "fix_direction": "..."
        }}
      ]
    }}
  ],
  "must_revise_slides": [<i>, ...],
  "overall_recommendation": "SHIP|REVISE"
}}
"""


def critique_carousel(
    *, brand: dict, strategist_spec: dict, rendered_pngs: list[Path],
    playbook_voice: str, playbook_typography: str,
    playbook_layout: str, playbook_conversion: str,
) -> CritiqueResult:
    prompt = _build_prompt(
        brand=brand, strategist_spec=strategist_spec, rendered_pngs=rendered_pngs,
        playbook_voice=playbook_voice, playbook_typography=playbook_typography,
        playbook_layout=playbook_layout, playbook_conversion=playbook_conversion,
    )
    # Each PNG requires a Read tool call; allow generous headroom so the model
    # can Read every slide (one tool call per slide) plus reason and emit JSON.
    response = query_json(prompt, allowed_tools=["Read"], max_turns=20)
    return CritiqueResult(
        carousel_assessment=response["carousel_assessment"],
        subtraction_test_findings=response["subtraction_test_findings"],
        peer_test_verdict=response["peer_test_verdict"],
        algorithm_test_verdict=response["algorithm_test_verdict"],
        per_slide=response["per_slide"],
        must_revise_slides=response["must_revise_slides"],
        overall_recommendation=response["overall_recommendation"],
    )
