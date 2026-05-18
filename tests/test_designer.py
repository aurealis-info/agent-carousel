from unittest.mock import patch

import pytest

from aurealis_carousel.designer import DesignerResult, SlideContent, compile_slide

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def blueprint():
    return {
        "i": 3,
        "type": "body",
        "headline": "Build the wall",
        "body": "Brick by brick. Day by day.",
        "label": "MOVE 01",
        "hero_word": "wall",
        "layout_move": "MEGA-WORD REST",
        "hero_word_treatment": {"italic": True, "color_shift": "accent"},
        "color_role": "primary",
        "inverted": False,
    }


@pytest.fixture
def palette():
    return {
        "bg": "#0A0A0A",
        "text": "#F0E6D6",
        "text_muted": "#6B6B6B",
        "accent": "#A67C2E",
    }


@pytest.fixture
def pairing():
    return {
        "id": "source-serif-source-sans",
        "heading": {"family": "Source Serif Pro"},
        "body": {"family": "Source Sans Pro"},
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_compile_returns_html_on_first_pass(blueprint, palette, pairing):
    valid_html = '<h2 class="t-h1">Build the <span style="color: var(--color-accent);">wall</span></h2><p class="t-body">Brick by brick. Day by day.</p>'
    with patch("aurealis_carousel.designer.query_json", return_value={"html": valid_html}) as mock:
        r = compile_slide(
            slide_blueprint=blueprint,
            palette=palette,
            pairing_id=pairing["id"],
            pairing=pairing,
            n_total=7,
            previous_html=None,
        )
    assert mock.call_count == 1
    assert r.html == valid_html
    assert r.retries == 0
    assert r.fallback is False


def test_compile_retries_on_validator_rejection(blueprint, palette, pairing):
    bad = {"html": '<h2 style="color: #ff00ff;">bad palette</h2>'}
    good = {"html": '<h2 class="t-h1">Build the wall</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=[bad, good]) as mock:
        r = compile_slide(
            slide_blueprint=blueprint,
            palette=palette,
            pairing_id=pairing["id"],
            pairing=pairing,
            n_total=7,
            previous_html=None,
        )
    assert mock.call_count == 2
    assert r.retries == 1
    assert r.fallback is False
    assert r.html == good["html"]


def test_compile_falls_back_after_two_failures(blueprint, palette, pairing):
    bad = {"html": '<h2 style="color: #ff00ff;">bad</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=[bad, bad]) as mock:
        r = compile_slide(
            slide_blueprint=blueprint,
            palette=palette,
            pairing_id=pairing["id"],
            pairing=pairing,
            n_total=7,
            previous_html=None,
        )
    assert mock.call_count == 2
    assert r.fallback is True
    assert r.retries == 2
    # Fallback HTML must contain the slide's headline + body
    assert "Build the wall" in r.html
    assert "Brick by brick" in r.html


def test_compile_treats_empty_html_as_violation(blueprint, palette, pairing):
    good = {"html": '<h2 class="t-h1">Build the wall</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=[{"html": ""}, good]) as mock:
        r = compile_slide(
            slide_blueprint=blueprint,
            palette=palette,
            pairing_id=pairing["id"],
            pairing=pairing,
            n_total=7,
            previous_html=None,
        )
    assert mock.call_count == 2
    assert r.retries == 1
    assert r.fallback is False


def test_retry_prompt_includes_violations(blueprint, palette, pairing):
    captured = []

    def capture(prompt, **kwargs):
        captured.append(prompt)
        if len(captured) == 1:
            return {"html": '<h2 style="color: #ff00ff;">bad</h2>'}
        return {"html": '<h2 class="t-h1">recovered</h2>'}

    with patch("aurealis_carousel.designer.query_json", side_effect=capture):
        compile_slide(
            slide_blueprint=blueprint,
            palette=palette,
            pairing_id=pairing["id"],
            pairing=pairing,
            n_total=7,
            previous_html=None,
        )
    assert "Previous attempt failed validation" in captured[1]
    assert "#ff00ff" in captured[1]


def test_prompt_includes_pairing_and_palette(blueprint, palette, pairing):
    captured = []

    def capture(prompt, **kwargs):
        captured.append(prompt)
        return {"html": '<h2 class="t-h1">ok</h2>'}

    with patch("aurealis_carousel.designer.query_json", side_effect=capture):
        compile_slide(
            slide_blueprint=blueprint,
            palette=palette,
            pairing_id=pairing["id"],
            pairing=pairing,
            n_total=7,
            previous_html=None,
        )
    assert "source-serif-source-sans" in captured[0]
    assert "#0A0A0A" in captured[0]  # palette values injected


def test_prompt_includes_layout_move(blueprint, palette, pairing):
    captured = []

    def capture(prompt, **kwargs):
        captured.append(prompt)
        return {"html": '<h2 class="t-h1">ok</h2>'}

    with patch("aurealis_carousel.designer.query_json", side_effect=capture):
        compile_slide(
            slide_blueprint=blueprint,
            palette=palette,
            pairing_id=pairing["id"],
            pairing=pairing,
            n_total=7,
            previous_html=None,
        )
    assert "MEGA-WORD REST" in captured[0]
    assert "layout_move" in captured[0]
