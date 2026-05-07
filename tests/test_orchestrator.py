"""End-to-end orchestrator test with all Claude calls mocked.

The mocked `query_json` is dispatched per-phase by inspecting the prompt content,
so a single side_effect can serve strategist, designer, and critique calls.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from aurealis_carousel.orchestrator import run

REPO = Path(__file__).parent.parent
FIXTURE = Path(__file__).parent / "fixtures" / "runs" / "happy_path" / "responses.yaml"


@pytest.fixture
def fixture_responses():
    return yaml.safe_load(FIXTURE.read_text())


def _make_query_json_side_effect(responses):
    """Returns a side-effect callable that dispatches by content of the prompt."""
    designer_calls = {"count": 0}

    def side_effect(prompt, **kwargs):
        # Strategist — its prompt is a creative-director frame with brand-context
        # tokens unique to that phase.
        if "TYPE PAIRINGS AVAILABLE" in prompt and "VOICE PRINCIPLES:" in prompt:
            return responses["strategist"]
        # Critique — its prompt feeds rendered PNG paths and asks for a verdict
        if "rejected 80%" in prompt or "PNG paths" in prompt.lower():
            return responses["critique"]
        # Designer — falls through here. Dispatch by call order so each slide
        # gets its corresponding fixture HTML.
        idx = designer_calls["count"]
        designer_calls["count"] += 1
        html_list = responses["designer"]
        # Cycle in case revision passes also dispatch here
        html = html_list[min(idx, len(html_list) - 1)]
        return {"html": html}

    return side_effect


def test_orchestrator_happy_path(tmp_path, fixture_responses):
    output_root = tmp_path / "output"
    history_path = tmp_path / "history" / "_test.yaml"
    side = _make_query_json_side_effect(fixture_responses)

    with patch("aurealis_carousel.strategist.query_json", side_effect=side), \
         patch("aurealis_carousel.designer.query_json", side_effect=side), \
         patch("aurealis_carousel.critique.query_json", side_effect=side), \
         patch("aurealis_carousel.persist.subprocess.run", MagicMock(returncode=0)):

        slide_paths = run(
            brand_name="_test",
            user_topic_hint=None,
            output_root=output_root,
            history_path=history_path,
            auto_commit=False,
        )

    # 4 PNGs rendered to disk
    assert len(slide_paths) == 4
    for p in slide_paths:
        assert p.exists()
        assert p.suffix == ".png"

    # metadata.yaml + caption.txt landed under output_root
    metadata_files = list(output_root.rglob("metadata.yaml"))
    assert len(metadata_files) == 1
    caption_files = list(output_root.rglob("caption.txt"))
    assert len(caption_files) == 1

    # caption content matches the strategist fixture
    caption_text = caption_files[0].read_text()
    assert "Stop overthinking" in caption_text

    # history was appended
    assert history_path.exists()
    history = yaml.safe_load(history_path.read_text())
    assert len(history) == 1
    assert history[0]["slug"] == "three-questions-for-clarity"
