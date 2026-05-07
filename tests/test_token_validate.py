from pathlib import Path

import pytest
import yaml

from aurealis_carousel.token_validate import ValidationResult, check

CASES = Path(__file__).parent / "validator" / "cases"
BRAND_YAML = Path(__file__).parent.parent / "brands" / "_test" / "brief.yaml"


@pytest.fixture
def test_brand():
    """Use _test brand if available; else fall back to a minimal stub."""
    if BRAND_YAML.exists():
        return yaml.safe_load(BRAND_YAML.read_text())
    return {
        "design": {
            "colors": {
                "primary": "#a67c2e", "secondary": "#c8973e", "accent": "#c4501a",
                "background": "#0a0a0a", "text": "#f0e6d6", "text_muted": "#6b6b6b",
            }
        }
    }


def _load(name):
    return (CASES / name).read_text()


def test_valid_minimal_passes(test_brand):
    assert check(_load("valid_minimal.html"), test_brand).ok


def test_valid_complex_passes(test_brand):
    assert check(_load("valid_complex.html"), test_brand).ok


def test_invalid_color_literal_rejected(test_brand):
    r = check(_load("invalid_color_literal.html"), test_brand)
    assert not r.ok
    assert any("color" in v.rule and "#ff00ff" in v.detail for v in r.violations)


def test_invalid_font_family_rejected(test_brand):
    r = check(_load("invalid_font_family.html"), test_brand)
    assert not r.ok
    assert any("font-family" in v.rule for v in r.violations)


def test_invalid_font_size_rejected(test_brand):
    r = check(_load("invalid_font_size.html"), test_brand)
    assert not r.ok
    assert any("font-size" in v.rule and "47px" in v.detail for v in r.violations)


def test_invalid_script_tag_rejected(test_brand):
    r = check(_load("invalid_script_tag.html"), test_brand)
    assert not r.ok
    assert any("disallowed-element" in v.rule and "script" in v.detail for v in r.violations)


def test_invalid_external_url_rejected(test_brand):
    r = check(_load("invalid_external_url.html"), test_brand)
    assert not r.ok
    assert any("external-resource" in v.rule for v in r.violations)


def test_invalid_banned_class_rejected(test_brand):
    r = check(_load("invalid_banned_class.html"), test_brand)
    assert not r.ok
    assert any("banned-class" in v.rule and "tw-" in v.detail for v in r.violations)


def test_invalid_named_color_rejected(test_brand):
    r = check(_load("invalid_named_color.html"), test_brand)
    assert not r.ok
    assert any("color" in v.rule for v in r.violations)


def test_invalid_color_in_style_block_rejected(test_brand):
    r = check(_load("invalid_color_in_style_block.html"), test_brand)
    assert not r.ok
    assert any("color" in v.rule and "#ff00ff" in v.detail for v in r.violations)


def test_invalid_color_in_media_query_rejected(test_brand):
    r = check(_load("invalid_color_in_media_query.html"), test_brand)
    assert not r.ok
    assert any("color" in v.rule for v in r.violations)


def test_multi_violation_returns_all(test_brand):
    r = check(_load("multi_violation.html"), test_brand)
    assert not r.ok
    rules = {v.rule for v in r.violations}
    assert any("color" in x for x in rules)
    assert any("font-size" in x for x in rules)
    assert any("disallowed-element" in x for x in rules)
    assert any("banned-class" in x for x in rules)


def test_validation_result_format_violations_for_retry(test_brand):
    r = check(_load("invalid_color_literal.html"), test_brand)
    f = r.format_for_retry()
    assert f.startswith("Previous attempt failed validation")
    assert "color-literal:color" in f
    assert "#ff00ff" in f
    assert "Regenerate strictly using brand tokens" in f
