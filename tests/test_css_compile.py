from pathlib import Path

import pytest

from aurealis_carousel.css_compile import compile_carousel_css

SAMPLE_PALETTE = {
    "bg": "#0A0A0A",
    "text": "#F0E6D6",
    "text_muted": "#6B6B6B",
    "accent": "#A67C2E",
    "accent_alt": "#C4501A",
}


def test_emits_color_vars_in_root():
    css = compile_carousel_css(SAMPLE_PALETTE)
    assert "--color-bg: #0A0A0A" in css
    assert "--color-text: #F0E6D6" in css
    assert "--color-text-muted: #6B6B6B" in css
    assert "--color-primary: #A67C2E" in css
    assert "--color-secondary: #A67C2E" in css  # accent maps to BOTH primary and secondary
    assert "--color-accent: #C4501A" in css     # accent_alt maps to --color-accent


def test_accent_alt_falls_back_to_accent_when_missing():
    palette = dict(SAMPLE_PALETTE)
    palette.pop("accent_alt")
    css = compile_carousel_css(palette)
    assert "--color-accent: #A67C2E" in css


def test_includes_base_css_role_classes():
    css = compile_carousel_css(SAMPLE_PALETTE)
    assert ".t-display" in css
    assert ".t-mega" in css
    assert ".u-italic" in css


def test_rejects_invalid_hex():
    with pytest.raises(ValueError, match="invalid hex"):
        compile_carousel_css({**SAMPLE_PALETTE, "bg": "not-a-color"})
