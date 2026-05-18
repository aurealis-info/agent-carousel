"""Designer phase — HTML compiler from writer blueprint.

Takes a slide blueprint (per-slide entry from the writer) and compiles HTML for
that slide using the named layout move + the writer's palette.  No creative
decisions are made here.

Validates output against token validator; retries once with violations on rejection;
falls back to safe-minimal layout after two failures.
"""
from dataclasses import dataclass
from typing import Optional

from aurealis_carousel.claude_cli import query_json
from aurealis_carousel.layout_moves import LAYOUT_MOVES_GUIDE
from aurealis_carousel.token_validate import check

MAX_RETRIES = 1   # 1 retry = 2 total attempts before fallback


@dataclass
class SlideContent:
    i: int
    type: str
    headline: str
    body: str = ""
    label: Optional[str] = None
    composition: str = "monolith"
    density: str = "loud"
    hero_word: Optional[str] = None
    color_inverted: bool = False


@dataclass
class DesignerResult:
    html: str
    retries: int
    fallback: bool


def _safe_minimal_html(slide: SlideContent) -> str:
    """Fallback layout: centered headline + body. Token-validator-clean by construction."""
    parts = [
        '<div style="position: absolute; inset: 0; display: flex; flex-direction: column; '
        'justify-content: center; align-items: center; padding: var(--sp-7) var(--sp-6); '
        'text-align: center;">',
        f'  <h2 class="t-h1" style="margin-bottom: var(--sp-4);">{slide.headline}</h2>',
    ]
    if slide.body:
        parts.append(f'  <p class="t-body" style="max-width: 800px;">{slide.body}</p>')
    parts.append('</div>')
    return "\n".join(parts)


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
    pairing: dict,
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
