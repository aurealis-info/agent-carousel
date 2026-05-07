"""Layout-fit validator — pure Python + Playwright DOM measurement.

Renders the same slide HTML the screenshot would render, but extracts bounding
rects + computed styles via page.evaluate to apply 9 mechanical layout rules.
Runs AFTER token validator and BEFORE vision critic.
"""
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from jinja2 import Template
from playwright.sync_api import sync_playwright

CANVAS_W, CANVAS_H = 1080, 1350
TOP_SAFE = 135
BOTTOM_SAFE = 1350 - 270   # = 1080
LEFT_SAFE = 86
RIGHT_SAFE = 1080 - 86     # = 994
GRID_CROP_TOP = 135        # central 1080x1080 in 1080x1350 canvas
GRID_CROP_BOTTOM = 1215    # 135 + 1080
MIN_BODY_PX = 30
MIN_HEADLINE_PX = 88
HERO_RATIO_MIN = 3.0
CRAMMING_MIN_GAP_PX = 16


@dataclass
class LayoutViolation:
    rule: str
    detail: str
    element_html: str = ""


@dataclass
class LayoutFitResult:
    ok: bool
    violations: list[LayoutViolation] = field(default_factory=list)

    def format_for_retry(self) -> str:
        if not self.violations:
            return ""
        lines = ["Previous attempt did not fit the safe-zone geometry. Layout-fit violations:"]
        for v in self.violations:
            lines.append(f"  - [{v.rule}] {v.detail}")
        lines.append(
            "Reposition the offending element(s). Text-safe zones: top 135px, "
            "sides 86px, bottom 270px. Headlines >= 88px font-size; body >= 30px; "
            "hero ratio >= 3:1 (largest headline / largest body)."
        )
        return "\n".join(lines)


# JS executed inside the rendered page to extract every text element's measurements.
EXTRACT_JS = r"""
() => {
  const TEXT_TAGS = ["H1","H2","H3","H4","H5","H6","P","SPAN","DIV","STRONG","EM","I","B","A","LI","DT","DD"];
  const elements = [];
  for (const el of document.querySelectorAll('*')) {
    if (!TEXT_TAGS.includes(el.tagName)) continue;
    const text = (el.innerText || "").trim();
    if (!text) continue;
    // Skip if any descendant has visible text — only leaf text containers count
    let hasTextChild = false;
    for (const c of el.children) {
      if ((c.innerText || "").trim()) { hasTextChild = true; break; }
    }
    if (hasTextChild) continue;
    const rect = el.getBoundingClientRect();
    const cs = window.getComputedStyle(el);
    elements.push({
      tag: el.tagName.toLowerCase(),
      classes: Array.from(el.classList),
      text: text.slice(0, 80),
      outer_html: el.outerHTML.slice(0, 200),
      rect: { top: rect.top, left: rect.left, right: rect.right, bottom: rect.bottom,
              width: rect.width, height: rect.height },
      font_size_px: parseFloat(cs.fontSize),
    });
  }
  return elements;
}
"""


def _is_headline(el: dict) -> bool:
    """Returns True if the element is a PRIMARY headline (h1, h2, t-display, t-h1, t-h2).

    Excludes t-h3 and smaller — those are subheadings/labels and aren't subject
    to the headline-min-size or hero-ratio rules.
    """
    if el["tag"] in {"h1", "h2"}:
        # If h1/h2 has a smaller-class override (t-h3, t-label, etc.), exempt it
        classes = set(el.get("classes") or [])
        if any(c in classes for c in {"t-h3", "t-label", "t-handle", "t-caption"}):
            return False
        return True
    classes = set(el.get("classes") or [])
    if any(c in classes for c in {"t-display", "t-h1", "t-h2"}):
        return True
    return False


def _is_label_or_caption(el: dict) -> bool:
    """Small Zone-3 / kicker elements that may live in the bottom safe zone."""
    classes = set(el.get("classes") or [])
    return any(c in classes for c in {"t-label", "t-handle", "t-caption"})


def _is_body_text(el: dict) -> bool:
    if el["tag"] == "p":
        return True
    classes = set(el.get("classes") or [])
    return "t-body" in classes


def _render_dom(slide_body_html, brand_css_path, slide_shell_path, pairing_font_faces) -> list[dict]:
    template = Template(Path(slide_shell_path).read_text())
    html = template.render(
        brand_css_path=str(brand_css_path),
        slide_body=slide_body_html,
        pairing_font_faces=pairing_font_faces or "",
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": CANVAS_W, "height": CANVAS_H})
            page = ctx.new_page()
            page.goto(f"file://{tmp_path}")
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            elements = page.evaluate(EXTRACT_JS)
            browser.close()
            return elements
    finally:
        tmp_path.unlink(missing_ok=True)


def check_fit(
    *,
    slide_body_html: str,
    brand_css_path: Path,
    slide_shell_path: Path,
    pairing_font_faces: Optional[str] = None,
    slide_type: Optional[str] = None,
) -> LayoutFitResult:
    elements = _render_dom(slide_body_html, brand_css_path, slide_shell_path, pairing_font_faces)
    violations: list[LayoutViolation] = []

    for el in elements:
        rect = el["rect"]
        oh = el.get("outer_html", "")
        # Rule 1 — top safe zone
        if rect["top"] < TOP_SAFE:
            violations.append(LayoutViolation(
                "top-safe-zone",
                f"text top {rect['top']:.0f}px is inside top safe zone (< {TOP_SAFE}px). Element text: {el['text'][:60]!r}",
                oh,
            ))
        # Rule 2 — bottom safe zone (skip small labels/handles that live in Zone 3 by design)
        if rect["bottom"] > BOTTOM_SAFE and not _is_label_or_caption(el):
            violations.append(LayoutViolation(
                "bottom-safe-zone",
                f"text bottom {rect['bottom']:.0f}px overlaps bottom safe zone (> {BOTTOM_SAFE}px). Element text: {el['text'][:60]!r}",
                oh,
            ))
        # Rule 3 — left/right safe zones
        if rect["left"] < LEFT_SAFE:
            violations.append(LayoutViolation(
                "left-safe-zone",
                f"text left {rect['left']:.0f}px is inside left safe zone (< {LEFT_SAFE}px). Element text: {el['text'][:60]!r}",
                oh,
            ))
        if rect["right"] > RIGHT_SAFE:
            violations.append(LayoutViolation(
                "right-safe-zone",
                f"text right {rect['right']:.0f}px exceeds right safe zone (> {RIGHT_SAFE}px). Element text: {el['text'][:60]!r}",
                oh,
            ))
        # Rule 4 — canvas overflow (hard reject; broader than safe-zone)
        if rect["top"] < 0 or rect["left"] < 0 or rect["right"] > CANVAS_W or rect["bottom"] > CANVAS_H:
            violations.append(LayoutViolation(
                "canvas-overflow",
                f"text rect ({rect['left']:.0f}, {rect['top']:.0f}) -> ({rect['right']:.0f}, {rect['bottom']:.0f}) exceeds canvas {CANVAS_W}x{CANVAS_H}",
                oh,
            ))
        # Rule 5 — grid-crop (hook only)
        if slide_type == "hook":
            if rect["top"] < GRID_CROP_TOP or rect["bottom"] > GRID_CROP_BOTTOM:
                violations.append(LayoutViolation(
                    "grid-crop",
                    f"hook text outside central 1080x1080 grid-crop region (must be {GRID_CROP_TOP}<=y<={GRID_CROP_BOTTOM}). Element text: {el['text'][:60]!r}",
                    oh,
                ))

    # Rule 8 — body minimum
    for el in elements:
        if _is_body_text(el) and el["font_size_px"] < MIN_BODY_PX:
            violations.append(LayoutViolation(
                "body-min-size",
                f"body element font-size {el['font_size_px']:.0f}px < {MIN_BODY_PX}px minimum. Element text: {el['text'][:60]!r}",
                el.get("outer_html", ""),
            ))
    # Rule 9 — headline minimum
    for el in elements:
        if _is_headline(el) and el["font_size_px"] < MIN_HEADLINE_PX:
            violations.append(LayoutViolation(
                "headline-min-size",
                f"headline element font-size {el['font_size_px']:.0f}px < {MIN_HEADLINE_PX}px minimum. Element text: {el['text'][:60]!r}",
                el.get("outer_html", ""),
            ))

    # Rule 7 — hero ratio: max(headline) / max(body) >= 3
    headlines = [el["font_size_px"] for el in elements if _is_headline(el)]
    bodies = [el["font_size_px"] for el in elements if _is_body_text(el)]
    if headlines and bodies:
        ratio = max(headlines) / max(bodies)
        if ratio < HERO_RATIO_MIN:
            violations.append(LayoutViolation(
                "hero-ratio",
                f"max headline ({max(headlines):.0f}px) / max body ({max(bodies):.0f}px) = {ratio:.2f}; minimum is {HERO_RATIO_MIN}",
            ))

    # Rule 6 — cramming: vertical gap between stacked text blocks >= 16px when they overlap horizontally
    sorted_els = sorted(
        [el for el in elements if (_is_headline(el) or _is_body_text(el))],
        key=lambda e: e["rect"]["top"],
    )
    for i in range(len(sorted_els) - 1):
        a = sorted_els[i]
        b = sorted_els[i + 1]
        # horizontal overlap?
        if a["rect"]["right"] >= b["rect"]["left"] and b["rect"]["right"] >= a["rect"]["left"]:
            gap = b["rect"]["top"] - a["rect"]["bottom"]
            if gap < CRAMMING_MIN_GAP_PX and gap >= 0:
                violations.append(LayoutViolation(
                    "cramming",
                    f"vertical gap {gap:.0f}px between stacked text blocks (< {CRAMMING_MIN_GAP_PX}px minimum)",
                ))

    return LayoutFitResult(ok=(len(violations) == 0), violations=violations)
