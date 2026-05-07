from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from aurealis_carousel.strategist import StrategistResult, generate_strategy, ValidationError

REPO = Path(__file__).parent.parent
ETHOS_BRIEF = REPO / "brands" / "ethos" / "brief.yaml"


@pytest.fixture
def ethos_brand():
    return yaml.safe_load(ETHOS_BRIEF.read_text())


@pytest.fixture
def font_library():
    return yaml.safe_load((REPO / "fonts" / "library.yaml").read_text())


def _well_formed_response():
    return {
        "topic": "Five questions a decisive man asks before action",
        "topic_slug": "five-questions-decisive-man-asks",
        "frame": "PAS",
        "voice_mode": "guide",
        "type_pairing_id": "recoleta-berthold",
        "emphasis_font": None,
        "creative_strategy_notes": "PAS frame because audience is problem-aware about indecision.",
        "narrative_arc": {
            "thesis": "From overwhelm to one concrete action",
            "motif": "gold underline beneath every climactic word",
            "climax_position": "N-1",
            "slides": [
                {"i": 1, "type": "hook", "headline": "Stop deciding twice.", "body": "",
                 "label": None, "composition": "billboard", "density": "loud", "hero_word": None},
                {"i": 2, "type": "context", "headline": "Indecision compounds.", "body": "Each undecided choice taxes your day.",
                 "label": None, "composition": "monolith", "density": "quiet", "hero_word": "compounds"},
                {"i": 3, "type": "body", "headline": "Ask: what am I avoiding?", "body": "Name the avoidance.",
                 "label": "MOVE 01", "composition": "monolith", "density": "loud", "hero_word": "avoiding"},
                {"i": 4, "type": "body", "headline": "Ask: smallest next step?", "body": "Reduce to one move.",
                 "label": "MOVE 02", "composition": "monolith", "density": "quiet", "hero_word": None},
                {"i": 5, "type": "body", "headline": "Ask: when, exactly?", "body": "Time-box the decision.",
                 "label": "MOVE 03", "composition": "monolith", "density": "quiet", "hero_word": "exactly"},
                {"i": 6, "type": "climax", "headline": "Decisiveness is a habit.", "body": "Repeat the loop.",
                 "label": None, "composition": "bullseye", "density": "loud", "hero_word": "habit"},
                {"i": 7, "type": "cta", "headline": "Download ETHOS", "body": "Theory without execution stays theory. ETHOS automates the protocol.",
                 "label": None, "composition": "bullseye", "density": "loud", "color_inverted": True, "hero_word": None}
            ]
        },
        "caption": {
            "first_125_chars": "Stop deciding twice. Five questions a decisive man asks before action — comment DECIDE for the protocol.",
            "full": "Stop deciding twice. Five questions a decisive man asks before action — comment DECIDE for the protocol. Save this thread.",
            "hashtags": ["#christianmen", "#discipleship", "#youngchristian",
                         "#manhood", "#wisdom", "#discipline", "#decisions",
                         "#bibledaily", "#christianidentity", "#fyp"]
        }
    }


def _empty_playbook():
    return {"01-hooks.md": "", "02-narrative.md": "",
            "03-conversion.md": "", "06-voice.md": ""}


def test_generate_returns_well_formed(ethos_brand, font_library):
    with patch("aurealis_carousel.strategist.query_json", return_value=_well_formed_response()):
        r = generate_strategy(brand=ethos_brand, font_library=font_library,
                              history=[], user_topic_hint=None,
                              playbook=_empty_playbook())
    assert isinstance(r, StrategistResult)
    assert r.voice_mode == "guide"
    assert r.type_pairing_id == "recoleta-berthold"
    assert r.slide_count == 7


def test_generate_rejects_hook_over_6_words(ethos_brand, font_library):
    bad = _well_formed_response()
    bad["narrative_arc"]["slides"][0]["headline"] = "This hook has way too many words to count"
    with patch("aurealis_carousel.strategist.query_json", return_value=bad):
        with pytest.raises(ValidationError, match="hook|6 words"):
            generate_strategy(brand=ethos_brand, font_library=font_library,
                              history=[], user_topic_hint=None,
                              playbook=_empty_playbook())


def test_generate_rejects_brand_banned_word(ethos_brand, font_library):
    bad = _well_formed_response()
    bad["narrative_arc"]["slides"][1]["body"] = "Manifest your day in alignment with what you want"  # ETHOS bans "manifest" + "alignment"
    with patch("aurealis_carousel.strategist.query_json", return_value=bad):
        with pytest.raises(ValidationError, match="banned"):
            generate_strategy(brand=ethos_brand, font_library=font_library,
                              history=[], user_topic_hint=None,
                              playbook=_empty_playbook())


def test_generate_rejects_voice_mode_outside_enum(ethos_brand, font_library):
    bad = _well_formed_response()
    bad["voice_mode"] = "narrator"
    with patch("aurealis_carousel.strategist.query_json", return_value=bad):
        with pytest.raises(ValidationError, match="voice_mode"):
            generate_strategy(brand=ethos_brand, font_library=font_library,
                              history=[], user_topic_hint=None,
                              playbook=_empty_playbook())


def test_generate_rejects_type_pairing_outside_library(ethos_brand, font_library):
    bad = _well_formed_response()
    bad["type_pairing_id"] = "made-up-pairing"
    with patch("aurealis_carousel.strategist.query_json", return_value=bad):
        with pytest.raises(ValidationError, match="type_pairing"):
            generate_strategy(brand=ethos_brand, font_library=font_library,
                              history=[], user_topic_hint=None,
                              playbook=_empty_playbook())


def test_generate_rejects_topic_in_recent_history(ethos_brand, font_library):
    history = [{"date": "2026-05-06", "slug": "five-questions-decisive-man-asks", "topic": "Five questions"}]
    with patch("aurealis_carousel.strategist.query_json", return_value=_well_formed_response()):
        with pytest.raises(ValidationError, match="recent history"):
            generate_strategy(brand=ethos_brand, font_library=font_library,
                              history=history, user_topic_hint=None,
                              playbook=_empty_playbook())


def test_user_topic_hint_used_verbatim(ethos_brand, font_library):
    captured = {}
    def capture(prompt, **kwargs):
        captured["prompt"] = prompt
        return _well_formed_response()
    with patch("aurealis_carousel.strategist.query_json", side_effect=capture):
        generate_strategy(brand=ethos_brand, font_library=font_library,
                          history=[], user_topic_hint="The Cost of Avoidance",
                          playbook=_empty_playbook())
    assert "The Cost of Avoidance" in captured["prompt"]
