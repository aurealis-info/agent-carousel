from pathlib import Path

import pytest

from aurealis_carousel.layout_check import LayoutFitResult, check_fit

REPO = Path(__file__).parent.parent
SHELL = REPO / "templates" / "slide-shell.html"
ETHOS_CSS = REPO / "brands" / "ethos" / "brand.css"

# A clean, all-rules-passing slide body for ETHOS.
# Geometry: top >= 135px (top-safe), left >= 86px (left-safe), bottom <= 1080px,
# right <= 994px. Typography: headline (t-display = 120px) / body (32px) = 3.75x
# (meets >= 3 hero ratio); body >= 30px; headline >= 88px.
GOOD_BODY = """
<div style="position: absolute; top: 200px; left: 100px; width: 800px;">
  <span class="t-label c-secondary" style="margin-bottom: var(--sp-3); display: block;">MOVE 01</span>
  <h1 class="t-display" style="margin-bottom: var(--sp-4);">Build</h1>
  <p class="t-body" style="max-width: 720px;">Brick by brick.</p>
</div>
"""


def test_check_fit_passes_well_formed_slide():
    r = check_fit(slide_body_html=GOOD_BODY, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    assert isinstance(r, LayoutFitResult)
    assert r.ok, f"unexpected violations: {r.violations}"


def test_check_fit_rejects_text_in_top_safe_zone():
    bad = """
    <div style="position: absolute; top: 50px; left: var(--sp-6);">
      <h2 class="t-h1">Too high</h2>
    </div>
    """
    r = check_fit(slide_body_html=bad, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    assert not r.ok
    assert any("top-safe-zone" in v.rule for v in r.violations)


def test_check_fit_rejects_text_in_bottom_safe_zone():
    bad = """
    <div style="position: absolute; bottom: 50px; left: var(--sp-6);">
      <h2 class="t-h1">Too low</h2>
    </div>
    """
    r = check_fit(slide_body_html=bad, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    assert not r.ok
    assert any("bottom-safe-zone" in v.rule for v in r.violations)


def test_check_fit_rejects_text_overflowing_canvas_right():
    bad = """
    <div style="position: absolute; top: 200px; left: 1100px;">
      <h2 class="t-h1">Off canvas right</h2>
    </div>
    """
    r = check_fit(slide_body_html=bad, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    assert not r.ok
    assert any(v.rule in {"right-safe-zone", "canvas-overflow"} for v in r.violations)


def test_check_fit_rejects_hero_ratio_under_3x():
    """Headline at ~64px against body at ~32px = 2x ratio (< 3x) -> reject."""
    bad = """
    <div style="position: absolute; top: 300px; left: var(--sp-6); width: 800px;">
      <h2 style="font-size: var(--type-h2); font-family: var(--font-heading);">Small headline</h2>
      <p style="font-size: var(--type-body);">Body that's only half the headline.</p>
    </div>
    """
    r = check_fit(slide_body_html=bad, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    assert not r.ok
    assert any("hero-ratio" in v.rule for v in r.violations)


def test_check_fit_rejects_grid_crop_violation_for_hook():
    """Hook text near top of canvas (y < 135) gets decapitated on profile grid (1080x1080 center)."""
    bad = """
    <div style="position: absolute; top: 1250px; left: var(--sp-6);">
      <h2 class="t-h1">Hook below grid crop</h2>
    </div>
    """
    r = check_fit(slide_body_html=bad, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL,
                  slide_type="hook")
    assert not r.ok
    assert any("grid-crop" in v.rule or "bottom-safe-zone" in v.rule for v in r.violations)


def test_check_fit_skips_grid_crop_for_non_hook_slides():
    """The grid crop rule is hook-only; for body slides, text in y=200 is fine."""
    body = """
    <div style="position: absolute; top: 200px; left: var(--sp-6); width: 800px;">
      <h2 class="t-h1">Body slide title</h2>
      <p class="t-body">Body text here.</p>
    </div>
    """
    r = check_fit(slide_body_html=body, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL,
                  slide_type="body")
    # No grid-crop violation expected
    assert not any("grid-crop" in v.rule for v in r.violations)


def test_layout_fit_result_format_for_retry():
    bad = """
    <div style="position: absolute; top: 50px; left: var(--sp-6);">
      <h2 class="t-h1">Too high</h2>
    </div>
    """
    r = check_fit(slide_body_html=bad, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    formatted = r.format_for_retry()
    assert "top-safe-zone" in formatted.lower() or "top safe" in formatted.lower()
    assert "Previous attempt" in formatted or "did not fit" in formatted.lower()


def test_check_fit_allows_page_number_in_bottom_safe_zone():
    """Page numbers / handles in Zone 3 (bottom-right) should NOT trigger bottom-safe-zone."""
    body = """
    <div style="position: absolute; top: 200px; left: var(--sp-6); width: 800px;">
      <h2 class="t-display">Big headline</h2>
      <p class="t-body">Body content here.</p>
    </div>
    <span class="t-label" style="position: absolute; bottom: var(--sp-5); left: var(--sp-6);">04 / 04</span>
    <span class="t-label" style="position: absolute; bottom: var(--sp-5); right: var(--sp-6);">SWIPE</span>
    """
    r = check_fit(slide_body_html=body, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    bottom_violations = [v for v in r.violations if "bottom-safe-zone" in v.rule]
    # No bottom-safe-zone violations from the t-label spans
    assert not bottom_violations, f"unexpected bottom-safe-zone violations: {bottom_violations}"


def test_check_fit_allows_t_h3_subheadings_below_88px():
    """Small numbered subheadings rendered as t-h3 (44px) should NOT trigger headline-min-size."""
    body = """
    <div style="position: absolute; top: 200px; left: var(--sp-6); width: 800px;">
      <h2 class="t-display">Daniel kept a schedule</h2>
      <div style="display: flex; gap: var(--sp-6); margin-top: var(--sp-5);">
        <h3 class="t-h3">Three times daily.</h3>
        <h3 class="t-h3">By the open window.</h3>
        <h3 class="t-h3">On the clock.</h3>
      </div>
      <p class="t-body" style="margin-top: var(--sp-4);">Body text here.</p>
    </div>
    """
    r = check_fit(slide_body_html=body, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    headline_min_violations = [v for v in r.violations if v.rule == "headline-min-size"]
    assert not headline_min_violations, f"unexpected headline-min-size violations: {headline_min_violations}"


def test_check_fit_hero_ratio_uses_largest_headline_only():
    """Hero ratio should compare max headline to max body, ignoring t-h3 subheadings."""
    body = """
    <div style="position: absolute; top: 200px; left: var(--sp-6); width: 800px;">
      <h2 class="t-display">Big headline at 120px</h2>
      <h3 class="t-h3">Subheading at 44px (should be ignored for hero-ratio)</h3>
      <p class="t-body">Body at 32px.</p>
    </div>
    """
    r = check_fit(slide_body_html=body, brand_css_path=ETHOS_CSS, slide_shell_path=SHELL)
    # 120 / 32 = 3.75; should pass
    hero_violations = [v for v in r.violations if v.rule == "hero-ratio"]
    assert not hero_violations, f"unexpected hero-ratio violations: {hero_violations}"
