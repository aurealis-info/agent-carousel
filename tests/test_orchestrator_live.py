"""End-to-end test that hits the real `claude` binary and renders real PNGs.

Run with: .venv/bin/pytest tests/test_orchestrator_live.py -xvs --run-live
"""
import datetime as dt
from pathlib import Path

import pytest

from aurealis_carousel.orchestrator import run

REPO = Path(__file__).parent.parent


@pytest.mark.live
def test_orchestrator_runs_end_to_end_against_test_brand(tmp_path):
    output_root = tmp_path / "output"
    history_path = tmp_path / "history" / "_test.yaml"
    slide_paths = run(
        brand_name="_test",
        user_topic_hint=None,
        output_root=output_root,
        history_path=history_path,
        auto_commit=False,
    )
    assert len(slide_paths) >= 3
    for p in slide_paths:
        assert p.exists() and p.stat().st_size > 0
    metadata_files = list(output_root.rglob("metadata.yaml"))
    assert len(metadata_files) == 1
