from pathlib import Path

import pytest

from aurealis_carousel.token_validate import ValidationResult, check

CASES = Path(__file__).parent / "validator" / "cases"


@pytest.fixture
def test_palette():
    """Minimal writer-style palette dict for token_validate tests."""
    return {
        "bg": "#0a0a0a",
        "text": "#f0e6d6",
        "text_muted": "#6b6b6b",
        "accent": "#a67c2e",
    }


def _load(name):
    return (CASES / name).read_text()


def test_valid_minimal_passes(test_palette):
    assert check(_load("valid_minimal.html"), test_palette).ok


def test_valid_complex_passes(test_palette):
    assert check(_load("valid_complex.html"), test_palette).ok


def test_invalid_color_literal_rejected(test_palette):
    r = check(_load("invalid_color_literal.html"), test_palette)
    assert not r.ok
    assert any("color" in v.rule and "#ff00ff" in v.detail for v in r.violations)


def test_invalid_font_family_rejected(test_palette):
    r = check(_load("invalid_font_family.html"), test_palette)
    assert not r.ok
    assert any("font-family" in v.rule for v in r.violations)


def test_invalid_font_size_rejected(test_palette):
    r = check(_load("invalid_font_size.html"), test_palette)
    assert not r.ok
    assert any("font-size" in v.rule and "47px" in v.detail for v in r.violations)


def test_invalid_script_tag_rejected(test_palette):
    r = check(_load("invalid_script_tag.html"), test_palette)
    assert not r.ok
    assert any("disallowed-element" in v.rule and "script" in v.detail for v in r.violations)


def test_invalid_external_url_rejected(test_palette):
    r = check(_load("invalid_external_url.html"), test_palette)
    assert not r.ok
    assert any("external-resource" in v.rule for v in r.violations)


def test_invalid_banned_class_rejected(test_palette):
    r = check(_load("invalid_banned_class.html"), test_palette)
    assert not r.ok
    assert any("banned-class" in v.rule and "tw-" in v.detail for v in r.violations)


def test_invalid_named_color_rejected(test_palette):
    r = check(_load("invalid_named_color.html"), test_palette)
    assert not r.ok
    assert any("color" in v.rule for v in r.violations)


def test_invalid_color_in_style_block_rejected(test_palette):
    r = check(_load("invalid_color_in_style_block.html"), test_palette)
    assert not r.ok
    assert any("color" in v.rule and "#ff00ff" in v.detail for v in r.violations)


def test_invalid_color_in_media_query_rejected(test_palette):
    r = check(_load("invalid_color_in_media_query.html"), test_palette)
    assert not r.ok
    assert any("color" in v.rule for v in r.violations)


def test_multi_violation_returns_all(test_palette):
    r = check(_load("multi_violation.html"), test_palette)
    assert not r.ok
    rules = {v.rule for v in r.violations}
    assert any("color" in x for x in rules)
    assert any("font-size" in x for x in rules)
    assert any("disallowed-element" in x for x in rules)
    assert any("banned-class" in x for x in rules)


def test_validation_result_format_violations_for_retry(test_palette):
    r = check(_load("invalid_color_literal.html"), test_palette)
    f = r.format_for_retry()
    assert f.startswith("Previous attempt failed validation")
    assert "color-literal:color" in f
    assert "#ff00ff" in f
    assert "Regenerate strictly using brand tokens" in f


def test_check_accepts_writer_palette_dict():
    from aurealis_carousel.token_validate import check

    palette = {
        "bg": "#0A0A0A",
        "text": "#F0E6D6",
        "text_muted": "#6B6B6B",
        "accent": "#A67C2E",
    }
    html = '<div style="background: #0A0A0A; color: #F0E6D6;"></div>'
    assert check(html, palette).ok


def test_check_rejects_hex_outside_writer_palette():
    from aurealis_carousel.token_validate import check

    palette = {"bg": "#0A0A0A", "text": "#F0E6D6", "text_muted": "#6B6B6B", "accent": "#A67C2E"}
    html = '<div style="background: #FF00FF;"></div>'  # neon pink not in palette
    result = check(html, palette)
    assert not result.ok
    assert any("color-literal" in v.rule for v in result.violations)
