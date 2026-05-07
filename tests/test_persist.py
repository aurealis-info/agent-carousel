from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from aurealis_carousel.persist import PersistInputs, finalize


def _inputs(tmp_path, auto_commit=False):
    return PersistInputs(
        brand_name="ethos", topic="test topic", topic_slug="test-slug",
        scripture_lane="A", verse="Ps 1:1", frame="PAS",
        voice_mode="guide", type_pairing_id="recoleta-berthold",
        emphasis_font=None, arc_thesis="from x to y", motif=None,
        composition_pattern=["billboard", "monolith", "bullseye"],
        slide_count=3,
        slide_paths=[Path("slide-01.png"), Path("slide-02.png"), Path("slide-03.png")],
        caption="hi caption", hashtags=["#a", "#b"],
        warnings={}, retries={"layout_check_slide_2": 1},
        output_dir=tmp_path / "outputs" / "ethos" / "test-slug",
        history_path=tmp_path / "history" / "ethos.yaml",
        repo_root=tmp_path, auto_commit=auto_commit,
    )


def test_finalize_writes_caption_txt(tmp_path):
    inp = _inputs(tmp_path)
    finalize(inp)
    assert (inp.output_dir / "caption.txt").read_text() == "hi caption"


def test_finalize_writes_metadata_yaml(tmp_path):
    inp = _inputs(tmp_path)
    finalize(inp)
    meta = yaml.safe_load((inp.output_dir / "metadata.yaml").read_text())
    assert meta["topic"] == "test topic"
    assert meta["voice_mode"] == "guide"
    assert meta["type_pairing_id"] == "recoleta-berthold"


def test_finalize_appends_to_history(tmp_path):
    inp = _inputs(tmp_path)
    finalize(inp)
    h = yaml.safe_load(inp.history_path.read_text())
    assert len(h) == 1
    assert h[0]["topic"] == "test topic"


def test_finalize_appends_to_existing_history(tmp_path):
    inp = _inputs(tmp_path)
    inp.history_path.parent.mkdir(parents=True, exist_ok=True)
    inp.history_path.write_text(yaml.safe_dump([{"date": "2026-04-01", "topic": "old"}]))
    finalize(inp)
    h = yaml.safe_load(inp.history_path.read_text())
    assert len(h) == 2 and h[0]["topic"] == "old" and h[1]["topic"] == "test topic"


def test_finalize_skips_git_when_auto_commit_false(tmp_path):
    fake = MagicMock(return_value=MagicMock(returncode=0))
    with patch("aurealis_carousel.persist.subprocess.run", fake):
        finalize(_inputs(tmp_path, auto_commit=False))
    assert fake.call_count == 0


def test_finalize_runs_git_add_commit_push_when_auto_commit_true(tmp_path):
    fake = MagicMock(return_value=MagicMock(returncode=0))
    with patch("aurealis_carousel.persist.subprocess.run", fake):
        finalize(_inputs(tmp_path, auto_commit=True))
    git_calls = [c for c in fake.call_args_list if c.args[0][0] == "git"]
    assert any("add" in c.args[0] for c in git_calls)
    assert any("commit" in c.args[0] for c in git_calls)
    assert any("push" in c.args[0] for c in git_calls)
