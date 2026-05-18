"""tests/test_angles.py"""
from unittest.mock import patch

import pytest

from aurealis_carousel import angles


MOCK_RESPONSE = {
    "angles": [
        {
            "topic": f"Topic {i}",
            "topic_slug": f"topic-{i}",
            "hook_intent": f"Hook intent {i}",
            "arc_thesis": f"Thesis {i}",
            "frame": "PAS",
            "voice_mode": "guide",
            "emotional_register": "monumental",
        }
        for i in range(10)
    ]
}


def test_generate_angles_returns_10():
    with patch("aurealis_carousel.angles.query_json", return_value=MOCK_RESPONSE):
        result = angles.generate_angles(
            brand={"brand_name": "TEST", "brief": "prose"},
            playbook={},
            history=[],
            user_topic_hint=None,
        )
    assert len(result) == 10
    assert all("topic" in a for a in result)


def test_generate_angles_accepts_5_minimum():
    short = {"angles": MOCK_RESPONSE["angles"][:5]}
    with patch("aurealis_carousel.angles.query_json", return_value=short):
        result = angles.generate_angles(
            brand={"brand_name": "TEST", "brief": "prose"},
            playbook={},
            history=[],
            user_topic_hint=None,
        )
    assert len(result) == 5


def test_generate_angles_retries_on_too_few():
    too_few = {"angles": MOCK_RESPONSE["angles"][:3]}
    with patch(
        "aurealis_carousel.angles.query_json",
        side_effect=[too_few, MOCK_RESPONSE],
    ) as mock:
        result = angles.generate_angles(
            brand={"brand_name": "TEST", "brief": "prose"},
            playbook={},
            history=[],
            user_topic_hint=None,
        )
    assert len(result) == 10
    assert mock.call_count == 2


def test_generate_angles_raises_after_retry():
    too_few = {"angles": MOCK_RESPONSE["angles"][:2]}
    with patch("aurealis_carousel.angles.query_json", return_value=too_few):
        with pytest.raises(angles.AngleGenerationError):
            angles.generate_angles(
                brand={"brand_name": "TEST", "brief": "prose"},
                playbook={},
                history=[],
                user_topic_hint=None,
            )
