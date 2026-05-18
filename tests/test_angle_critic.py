"""tests/test_angle_critic.py"""
from unittest.mock import patch

from aurealis_carousel import angle_critic


SAMPLE_ANGLES = [{"topic": f"T{i}", "topic_slug": f"t-{i}"} for i in range(10)]


def test_picks_valid_index():
    with patch(
        "aurealis_carousel.angle_critic.query_json",
        return_value={"winning_index": 3, "reasoning": "best hook"},
    ):
        idx = angle_critic.pick_winner(angles_list=SAMPLE_ANGLES, brand={"brief": ""}, playbook={})
    assert idx == 3


def test_falls_back_to_zero_on_out_of_range():
    with patch(
        "aurealis_carousel.angle_critic.query_json",
        return_value={"winning_index": 99, "reasoning": "wat"},
    ):
        idx = angle_critic.pick_winner(angles_list=SAMPLE_ANGLES, brand={"brief": ""}, playbook={})
    assert idx == 0


def test_falls_back_to_zero_on_missing_index():
    with patch(
        "aurealis_carousel.angle_critic.query_json",
        return_value={"reasoning": "no index"},
    ):
        idx = angle_critic.pick_winner(angles_list=SAMPLE_ANGLES, brand={"brief": ""}, playbook={})
    assert idx == 0
