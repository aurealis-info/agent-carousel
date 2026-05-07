from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from aurealis_carousel.critique import CritiqueResult, critique_carousel

REPO = Path(__file__).parent.parent
ETHOS_BRIEF = REPO / "brands" / "ethos" / "brief.yaml"


@pytest.fixture
def ethos_brand():
    return yaml.safe_load(ETHOS_BRIEF.read_text())


@pytest.fixture
def slide_paths(tmp_path):
    """3 fake PNG paths — content doesn't matter since query is mocked."""
    paths = []
    for i in range(1, 4):
        p = tmp_path / f"slide-{i:02d}.png"
        p.write_bytes(b"fake png bytes")
        paths.append(p)
    return paths


@pytest.fixture
def strategist_spec():
    return {
        "topic": "test topic",
        "topic_slug": "test-topic",
        "frame": "PAS",
        "voice_mode": "guide",
        "type_pairing_id": "recoleta-berthold",
        "narrative_arc": {
            "thesis": "from x to y",
            "motif": None,
            "slides": [
                {"i": 1, "type": "hook", "headline": "Hook"},
                {"i": 2, "type": "body", "headline": "Body"},
                {"i": 3, "type": "cta", "headline": "Download ETHOS"},
            ],
        },
    }


def _well_formed_critic():
    return {
        "carousel_assessment": {
            "cohesion": "PASS",
            "motif_consistency": "PASS",
            "narrative_arc_clarity": "PASS",
            "cta_bridge_effectiveness": "PASS",
            "type_pairing_appropriateness": "PASS",
        },
        "subtraction_test_findings": "All slides survive subtraction.",
        "peer_test_verdict": "PASS",
        "algorithm_test_verdict": "PASS",
        "per_slide": [
            {"i": 1, "verdict": "PASS", "violations": []},
            {"i": 2, "verdict": "PASS", "violations": []},
            {"i": 3, "verdict": "PASS", "violations": []},
        ],
        "must_revise_slides": [],
        "overall_recommendation": "SHIP",
    }


def test_critique_returns_well_formed_result(ethos_brand, slide_paths, strategist_spec):
    with patch("aurealis_carousel.critique.query_json", return_value=_well_formed_critic()):
        r = critique_carousel(
            brand=ethos_brand, strategist_spec=strategist_spec,
            rendered_pngs=slide_paths,
            playbook_voice="", playbook_typography="",
            playbook_layout="", playbook_conversion="",
        )
    assert isinstance(r, CritiqueResult)
    assert r.must_revise_slides == []
    assert r.overall_recommendation == "SHIP"
    assert r.carousel_assessment["cohesion"] == "PASS"


def test_critique_returns_revise_for_problem_slide(ethos_brand, slide_paths, strategist_spec):
    bad = _well_formed_critic()
    bad["per_slide"][1]["verdict"] = "REVISE"
    bad["per_slide"][1]["violations"] = [{
        "category": "hierarchy", "severity": "blocking",
        "specifics": "Body text overpowers headline",
        "fix_direction": "Increase headline weight to 900",
    }]
    bad["must_revise_slides"] = [2]
    bad["overall_recommendation"] = "REVISE"
    with patch("aurealis_carousel.critique.query_json", return_value=bad):
        r = critique_carousel(
            brand=ethos_brand, strategist_spec=strategist_spec,
            rendered_pngs=slide_paths,
            playbook_voice="", playbook_typography="",
            playbook_layout="", playbook_conversion="",
        )
    assert r.must_revise_slides == [2]
    assert r.overall_recommendation == "REVISE"
    assert r.per_slide[1]["violations"][0]["category"] == "hierarchy"


def test_critique_prompt_lists_all_png_paths(ethos_brand, slide_paths, strategist_spec):
    captured = []
    def capture(prompt, **kwargs):
        captured.append((prompt, kwargs))
        return _well_formed_critic()
    with patch("aurealis_carousel.critique.query_json", side_effect=capture):
        critique_carousel(
            brand=ethos_brand, strategist_spec=strategist_spec,
            rendered_pngs=slide_paths,
            playbook_voice="", playbook_typography="",
            playbook_layout="", playbook_conversion="",
        )
    prompt = captured[0][0]
    for p in slide_paths:
        assert str(p) in prompt


def test_critique_call_grants_read_tool(ethos_brand, slide_paths, strategist_spec):
    captured = []
    def capture(prompt, **kwargs):
        captured.append((prompt, kwargs))
        return _well_formed_critic()
    with patch("aurealis_carousel.critique.query_json", side_effect=capture):
        critique_carousel(
            brand=ethos_brand, strategist_spec=strategist_spec,
            rendered_pngs=slide_paths,
            playbook_voice="", playbook_typography="",
            playbook_layout="", playbook_conversion="",
        )
    kwargs = captured[0][1]
    assert "allowed_tools" in kwargs
    assert "Read" in kwargs["allowed_tools"]


def test_critique_prompt_carries_adversarial_framing(ethos_brand, slide_paths, strategist_spec):
    captured = []
    def capture(prompt, **kwargs):
        captured.append(prompt)
        return _well_formed_critic()
    with patch("aurealis_carousel.critique.query_json", side_effect=capture):
        critique_carousel(
            brand=ethos_brand, strategist_spec=strategist_spec,
            rendered_pngs=slide_paths,
            playbook_voice="", playbook_typography="",
            playbook_layout="", playbook_conversion="",
        )
    prompt = captured[0]
    # Adversarial cues must be present
    assert any(phrase in prompt for phrase in [
        "rejected", "mediocrity", "NOT a helpful assistant",
        "Subtraction Test", "Peer Test", "Algorithm Test",
    ])


def test_critique_passes_through_strategist_spec_to_prompt(ethos_brand, slide_paths, strategist_spec):
    captured = []
    def capture(prompt, **kwargs):
        captured.append(prompt)
        return _well_formed_critic()
    with patch("aurealis_carousel.critique.query_json", side_effect=capture):
        critique_carousel(
            brand=ethos_brand, strategist_spec=strategist_spec,
            rendered_pngs=slide_paths,
            playbook_voice="", playbook_typography="",
            playbook_layout="", playbook_conversion="",
        )
    prompt = captured[0]
    assert "test topic" in prompt or "PAS" in prompt
    assert "guide" in prompt or "recoleta-berthold" in prompt
