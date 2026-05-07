from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from aurealis_carousel.designer import DesignerResult, SlideContent, generate_slide

REPO = Path(__file__).parent.parent
ETHOS_BRIEF = REPO / "brands" / "ethos" / "brief.yaml"
ETHOS_CSS = REPO / "brands" / "ethos" / "brand.css"
LIBRARY = REPO / "fonts" / "library.yaml"


@pytest.fixture
def ethos_brand():
    return yaml.safe_load(ETHOS_BRIEF.read_text())


@pytest.fixture
def brand_css():
    return ETHOS_CSS.read_text()


@pytest.fixture
def recoleta_pairing():
    lib = yaml.safe_load(LIBRARY.read_text())
    return next(p for p in lib["pairings"] if p["id"] == "recoleta-berthold")


@pytest.fixture
def slide():
    return SlideContent(
        i=3, type="body", headline="Build the wall",
        body="Brick by brick. Day by day.",
        label="MOVE 01", composition="monolith", density="loud",
        hero_word="wall",
    )


def test_generate_returns_html_on_first_pass(ethos_brand, brand_css, recoleta_pairing, slide):
    valid_html = '<h2 class="t-h1">Build the <span class="c-secondary">wall</span></h2><p class="t-body">Brick by brick. Day by day.</p>'
    with patch("aurealis_carousel.designer.query_json", return_value={"html": valid_html}) as mock:
        r = generate_slide(
            brand=ethos_brand, brand_css=brand_css, pairing=recoleta_pairing,
            emphasis_font=None, slide=slide, n_total=7, previous_html=None,
            playbook_typography="", playbook_layout="",
        )
    assert mock.call_count == 1
    assert r.html == valid_html
    assert r.retries == 0
    assert r.fallback is False


def test_generate_retries_on_validator_rejection(ethos_brand, brand_css, recoleta_pairing, slide):
    bad = {"html": '<h2 style="color: #ff00ff;">bad palette</h2>'}
    good = {"html": '<h2 class="t-h1">Build the wall</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=[bad, good]) as mock:
        r = generate_slide(
            brand=ethos_brand, brand_css=brand_css, pairing=recoleta_pairing,
            emphasis_font=None, slide=slide, n_total=7, previous_html=None,
            playbook_typography="", playbook_layout="",
        )
    assert mock.call_count == 2
    assert r.retries == 1
    assert r.fallback is False
    assert r.html == good["html"]


def test_generate_falls_back_after_two_failures(ethos_brand, brand_css, recoleta_pairing, slide):
    bad = {"html": '<h2 style="color: #ff00ff;">bad</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=[bad, bad]) as mock:
        r = generate_slide(
            brand=ethos_brand, brand_css=brand_css, pairing=recoleta_pairing,
            emphasis_font=None, slide=slide, n_total=7, previous_html=None,
            playbook_typography="", playbook_layout="",
        )
    assert mock.call_count == 2
    assert r.fallback is True
    assert r.retries == 2
    # Fallback HTML must contain the slide's headline + body and pass token validator
    assert "Build the wall" in r.html
    assert "Brick by brick" in r.html


def test_generate_treats_empty_html_as_violation(ethos_brand, brand_css, recoleta_pairing, slide):
    good = {"html": '<h2 class="t-h1">Build the wall</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=[{"html": ""}, good]) as mock:
        r = generate_slide(
            brand=ethos_brand, brand_css=brand_css, pairing=recoleta_pairing,
            emphasis_font=None, slide=slide, n_total=7, previous_html=None,
            playbook_typography="", playbook_layout="",
        )
    assert mock.call_count == 2
    assert r.retries == 1
    assert r.fallback is False


def test_retry_prompt_includes_violations(ethos_brand, brand_css, recoleta_pairing, slide):
    captured = []
    def capture(prompt, **kwargs):
        captured.append(prompt)
        if len(captured) == 1:
            return {"html": '<h2 style="color: #ff00ff;">bad</h2>'}
        return {"html": '<h2 class="t-h1">recovered</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=capture):
        generate_slide(
            brand=ethos_brand, brand_css=brand_css, pairing=recoleta_pairing,
            emphasis_font=None, slide=slide, n_total=7, previous_html=None,
            playbook_typography="", playbook_layout="",
        )
    assert "Previous attempt failed validation" in captured[1]
    assert "#ff00ff" in captured[1]


def test_prompt_includes_pairing_and_brand_css(ethos_brand, brand_css, recoleta_pairing, slide):
    captured = []
    def capture(prompt, **kwargs):
        captured.append(prompt)
        return {"html": '<h2 class="t-h1">ok</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=capture):
        generate_slide(
            brand=ethos_brand, brand_css=brand_css, pairing=recoleta_pairing,
            emphasis_font=None, slide=slide, n_total=7, previous_html=None,
            playbook_typography="", playbook_layout="",
        )
    assert "recoleta-berthold" in captured[0]
    assert "--type-h1" in captured[0]  # brand css tokens injected


def test_emphasis_font_appears_in_prompt(ethos_brand, brand_css, recoleta_pairing, slide):
    emphasis = {"from_pairing": "citadel-helvetica", "family": "Citadel Script Std", "role": "hero-word-only"}
    captured = []
    def capture(prompt, **kwargs):
        captured.append(prompt)
        return {"html": '<h2 class="t-h1">ok</h2>'}
    with patch("aurealis_carousel.designer.query_json", side_effect=capture):
        generate_slide(
            brand=ethos_brand, brand_css=brand_css, pairing=recoleta_pairing,
            emphasis_font=emphasis, slide=slide, n_total=7, previous_html=None,
            playbook_typography="", playbook_layout="",
        )
    assert "Citadel Script Std" in captured[0]
    assert "hero" in captured[0].lower()
