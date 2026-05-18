"""Designer phase — one Claude call per slide returning HTML body.

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
    *, brand: dict, brand_css: str, pairing: dict, emphasis_font: Optional[dict],
    slide: SlideContent, n_total: int, previous_html: Optional[str],
    playbook_typography: str, playbook_layout: str,
    retry_violations: Optional[str] = None,
) -> str:
    emphasis_block = "(none — designer uses primary pairing only)"
    if emphasis_font:
        emphasis_block = (
            f"borrowed from pairing '{emphasis_font['from_pairing']}'; "
            f"family '{emphasis_font['family']}'; "
            f"role: {emphasis_font['role']} (apply to hero word ONLY)"
        )

    sections = [
        f"You are designing slide {slide.i} of {n_total} in an Instagram carousel (1080x1350 portrait).",
        "",
        f"PRIMARY PAIRING: {pairing['id']}",
        f"  heading family: {pairing['heading']['family']}",
        f"  body family:    {pairing['body']['family']}",
        f"  vibe: {pairing['vibe']}",
        "",
        f"EMPHASIS FONT: {emphasis_block}",
        "",
        "BRAND CSS TOKENS (the only color, font, and size values you may use are these CSS variables):",
        "```css",
        brand_css,
        "```",
        "",
        "SLIDE CONTENT:",
        f"  type: {slide.type}",
        f"  headline: {slide.headline}",
        f"  body: {slide.body}",
        f"  label: {slide.label}",
        f"  composition template: {slide.composition}",
        f"  density: {slide.density}",
        f"  hero_word: {slide.hero_word}",
        f"  color_inverted: {slide.color_inverted}",
        "",
        f"PREVIOUS SLIDE HTML (for visual continuity reference):",
        previous_html or "(this is the first slide; no previous HTML)",
        "",
        "TYPOGRAPHY PLAYBOOK:",
        playbook_typography or "(none provided)",
        "",
        "LAYOUT PLAYBOOK:",
        playbook_layout or "(none provided)",
        "",
        LAYOUT_MOVES_GUIDE,
        "",
        "REQUIREMENTS:",
        '- Output ONLY a JSON object: {"html": "<your html body string>"}',
        "- Your HTML goes INSIDE a <div class=\"slide\"> wrapper that is already present; do not include the wrapper",
        "- Use ONLY brand CSS variables for color, font-family, and font-size (no literals)",
        "- Layout primitives (flex, grid, position, transform, inline SVG) are unrestricted",
        "- Honor the composition template intent AND pick exactly ONE layout move from the guide above",
        "- The hero_word, if provided, must receive a distinct typographic treatment — pick TWO of: italic, weight shift, family shift (.t-display-italic), color shift, size shift (e.g. .t-display vs surrounding .t-h1). Color-only is a flat default — combine with italic or weight to make it punch.",
        "- Use the typographic role classes (.t-display, .t-stat, .t-pullquote, .t-eyebrow, .t-scripture-ref, .t-dropcap, .t-mega) over plain font-size literals — the role carries opsz, leading, tracking, and weight as one unit",
        "- For Fraunces variable axes: the role classes already set font-variation-settings 'opsz'. Don't override unless the move requires a deliberate axis shift.",
        "- Tracking utilities are available: .u-track-tight (-0.04em) for ALL CAPS display, .u-track-loose (.18em) for kickers, .u-track-wide (.32em) for scripture-ref / smallcaps, .u-tnum for tabular numerals.",
        "- Text-safe zones: top 135px, sides 86px, bottom 270px",
        "- No background images. Solid brand-color backgrounds only.",
    ]
    if retry_violations:
        sections.append("")
        sections.append(retry_violations)
    sections.append("")
    sections.append("OUTPUT (JSON only, no preamble):")
    return "\n".join(sections)


def generate_slide(
    *, brand: dict, brand_css: str, pairing: dict, emphasis_font: Optional[dict],
    slide: SlideContent, n_total: int, previous_html: Optional[str],
    playbook_typography: str, playbook_layout: str,
) -> DesignerResult:
    retry_violations: Optional[str] = None

    for attempt in range(MAX_RETRIES + 1):
        prompt = _build_prompt(
            brand=brand, brand_css=brand_css, pairing=pairing, emphasis_font=emphasis_font,
            slide=slide, n_total=n_total, previous_html=previous_html,
            playbook_typography=playbook_typography, playbook_layout=playbook_layout,
            retry_violations=retry_violations,
        )
        response = query_json(prompt)
        last_html = response.get("html", "")

        if not last_html.strip():
            retry_violations = (
                "Previous attempt failed validation. Violations:\n"
                "  - [missing-html] response did not include a non-empty 'html' field\n"
                "Regenerate using only brand tokens (CSS variables) for color, "
                "font-family, and font-size. Return JSON {\"html\": \"<your html>\"}."
            )
            continue

        result = check(last_html, brand)
        if result.ok:
            return DesignerResult(html=last_html, retries=attempt, fallback=False)
        retry_violations = result.format_for_retry()

    fallback_html = _safe_minimal_html(slide)
    return DesignerResult(html=fallback_html, retries=MAX_RETRIES + 1, fallback=True)
