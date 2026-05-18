"""tests/test_writer.py"""
from unittest.mock import patch

import pytest

from aurealis_carousel import writer


SAMPLE_BLUEPRINT = {
    "topic": "The discipline of silence",
    "topic_slug": "discipline-of-silence",
    "frame": "principle-stack",
    "voice_mode": "guide",
    "pairing_id": "source-serif-source-sans",
    "palette": {
        "bg": "#0A0A0A",
        "text": "#F0E6D6",
        "text_muted": "#6B6B6B",
        "accent": "#A67C2E",
    },
    "slides": [
        {
            "i": 1, "type": "hook", "headline": "Silence builds the man",
            "body": "", "label": None, "hero_word": "Silence",
            "layout_move": "MEGA-WORD REST",
            "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                    "scale_shift": "mega", "weight_shift": None,
                                    "family_shift": None},
            "color_role": "bg=palette.bg, accent_on=hero_word",
            "inverted": False,
        },
        {"i": 2, "type": "body", "headline": "Why noise hides you",
         "body": "...", "label": None, "hero_word": None,
         "layout_move": "EYEBROW / HERO / TAGLINE STACK",
         "hero_word_treatment": None,
         "color_role": "bg=palette.bg", "inverted": False},
        {"i": 3, "type": "body", "headline": "Three windows of silence",
         "body": "...", "label": None, "hero_word": None,
         "layout_move": "ROMAN NUMERAL CHAPTER MARKER",
         "hero_word_treatment": None,
         "color_role": "bg=palette.bg", "inverted": False},
        {"i": 4, "type": "climax", "headline": "Governed.",
         "body": "", "label": None, "hero_word": "Governed",
         "layout_move": "MEGA-WORD REST",
         "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                 "scale_shift": "mega", "weight_shift": None,
                                 "family_shift": None},
         "color_role": "bg=palette.bg, accent_on=hero_word",
         "inverted": False},
        {"i": 5, "type": "cta", "headline": "ETHOS builds that man",
         "body": "One verse, one anchor, one rep per morning.",
         "label": None, "hero_word": None,
         "layout_move": "ALL-CAPS HERO + LOWERCASE TAGLINE",
         "hero_word_treatment": None,
         "color_role": "bg=palette.bg", "inverted": False},
    ],
    "caption": {
        "first_125_chars": "Silence builds the man you keep auditioning to become. Stop performing. Sit with it.",
        "full": "Silence builds the man you keep auditioning to become. Stop performing. Sit with it. Three windows. Governed. ETHOS builds that man one morning at a time.",
        "hashtags": ["#christianmen", "#manhood", "#discipleship", "#bible",
                     "#faith", "#integrity", "#wisdom", "#character",
                     "#ethosapp", "#governedman"],
    },
    "creative_notes": "Source Serif Pro pairing because the topic is instructional and protocol-tier; warm gold accent only on hook + climax because the topic asks for restraint, not exuberance."
}

SAMPLE_BRAND = {
    "brand_name": "ETHOS",
    "app_name": "ETHOS",
    "brief": "ETHOS is an iOS app for young Christian men ...",
    "slide_count_range": [5, 6],
    "hashtag_count_range": [8, 12],
}

SAMPLE_LIBRARY = {
    "pairings": [
        {"id": "source-serif-source-sans", "emotional_register": "instructional",
         "heading": {"family": "Source Serif Pro"}, "body": {"family": "Source Sans Pro"}},
        {"id": "cinzel-josefin", "emotional_register": "monumental",
         "heading": {"family": "Cinzel"}, "body": {"family": "Josefin Sans"}},
    ],
}


def test_validate_blueprint_happy_path():
    writer.validate_blueprint(SAMPLE_BLUEPRINT, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                              recent_slugs=[])


def test_validate_blueprint_rejects_hook_over_six_words():
    bp = _copy_with_slide_change(SAMPLE_BLUEPRINT, 0,
                                 headline="One two three four five six seven eight")
    with pytest.raises(writer.BlueprintValidationError, match="hook"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_bad_pairing_id():
    bp = dict(SAMPLE_BLUEPRINT, pairing_id="does-not-exist")
    with pytest.raises(writer.BlueprintValidationError, match="pairing_id"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_low_contrast_palette():
    bp = dict(SAMPLE_BLUEPRINT, palette={
        "bg": "#FFFFFF", "text": "#EEEEEE", "text_muted": "#DDDDDD", "accent": "#A67C2E"
    })
    with pytest.raises(writer.BlueprintValidationError, match="contrast"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_hashtag_outside_range():
    bp = dict(SAMPLE_BLUEPRINT)
    bp["caption"] = dict(bp["caption"], hashtags=["#one", "#two"])
    with pytest.raises(writer.BlueprintValidationError, match="hashtag"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_recent_slug():
    with pytest.raises(writer.BlueprintValidationError, match="topic_slug"):
        writer.validate_blueprint(SAMPLE_BLUEPRINT, brand=SAMPLE_BRAND,
                                  library=SAMPLE_LIBRARY,
                                  recent_slugs=["discipline-of-silence"])


def test_validate_blueprint_rejects_missing_hook_trigram_in_caption():
    bp = dict(SAMPLE_BLUEPRINT)
    bp["caption"] = dict(bp["caption"],
                         first_125_chars="An entirely different sentence about something else.")
    with pytest.raises(writer.BlueprintValidationError, match="trigram"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_validate_blueprint_rejects_cta_missing_app_name():
    bp = _copy_with_slide_change(SAMPLE_BLUEPRINT, 4,
                                 headline="Download today")
    with pytest.raises(writer.BlueprintValidationError, match="app name"):
        writer.validate_blueprint(bp, brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY,
                                  recent_slugs=[])


def test_generate_happy_path():
    with patch("aurealis_carousel.writer.query_json", return_value=SAMPLE_BLUEPRINT):
        result = writer.generate(
            winning_angle={"topic": "...", "voice_mode": "guide"},
            brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY, playbook={},
            visual_ref_paths=[], recent_slugs=[],
        )
    assert result["topic_slug"] == "discipline-of-silence"
    assert result["pairing_id"] == "source-serif-source-sans"


def test_generate_retries_on_validation_failure():
    bad = dict(SAMPLE_BLUEPRINT, pairing_id="does-not-exist")
    with patch("aurealis_carousel.writer.query_json",
               side_effect=[bad, SAMPLE_BLUEPRINT]) as mock:
        result = writer.generate(
            winning_angle={"topic": "...", "voice_mode": "guide"},
            brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY, playbook={},
            visual_ref_paths=[], recent_slugs=[],
        )
    assert mock.call_count == 2
    assert result["pairing_id"] == "source-serif-source-sans"


def test_generate_raises_after_retry_fails():
    bad = dict(SAMPLE_BLUEPRINT, pairing_id="does-not-exist")
    with patch("aurealis_carousel.writer.query_json", return_value=bad):
        with pytest.raises(writer.BlueprintValidationError):
            writer.generate(
                winning_angle={"topic": "...", "voice_mode": "guide"},
                brand=SAMPLE_BRAND, library=SAMPLE_LIBRARY, playbook={},
                visual_ref_paths=[], recent_slugs=[],
            )


def _copy_with_slide_change(blueprint: dict, slide_idx: int, **changes) -> dict:
    """Helper: deep-copy blueprint and update one slide's fields."""
    import copy
    bp = copy.deepcopy(blueprint)
    for k, v in changes.items():
        bp["slides"][slide_idx][k] = v
    return bp
