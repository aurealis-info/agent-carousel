from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from aurealis_carousel.cli import main


REPO = Path(__file__).parent.parent


def test_list_brands_prints_known_brands(capsys):
    with patch("sys.argv", ["aurealis-carousel", "list-brands"]):
        rc = main()
    captured = capsys.readouterr()
    assert rc == 0
    # All three brand dirs that exist
    assert "_test" in captured.out
    assert "ethos" in captured.out
    assert "lokin" in captured.out


def test_generate_command_invokes_orchestrator_with_brand(tmp_path):
    fake_run = MagicMock(return_value=[Path("slide-01.png"), Path("slide-02.png")])
    with patch("sys.argv", ["aurealis-carousel", "generate", "_test"]):
        with patch("aurealis_carousel.cli.run", fake_run):
            rc = main()
    assert rc == 0
    args, kwargs = fake_run.call_args
    assert kwargs["brand_name"] == "_test"
    assert kwargs["auto_commit"] is False
    assert kwargs["user_topic_hint"] is None


def test_generate_command_with_topic_and_auto_commit(tmp_path):
    fake_run = MagicMock(return_value=[])
    with patch("sys.argv", ["aurealis-carousel", "generate", "ethos",
                            "--topic", "Decisiveness",
                            "--auto-commit"]):
        with patch("aurealis_carousel.cli.run", fake_run):
            rc = main()
    assert rc == 0
    _, kwargs = fake_run.call_args
    assert kwargs["brand_name"] == "ethos"
    assert kwargs["user_topic_hint"] == "Decisiveness"
    assert kwargs["auto_commit"] is True


def test_doctor_unknown_brand_exits_nonzero(capsys):
    with patch("sys.argv", ["aurealis-carousel", "doctor", "nonexistent_brand"]):
        rc = main()
    captured = capsys.readouterr()
    assert rc != 0
    assert "not found" in captured.out.lower() or "not found" in captured.err.lower()


def test_doctor_known_brand_succeeds(capsys):
    with patch("sys.argv", ["aurealis-carousel", "doctor", "_test"]):
        rc = main()
    captured = capsys.readouterr()
    assert rc == 0
    assert "_test" in captured.out


def test_no_args_prints_help(capsys):
    with patch("sys.argv", ["aurealis-carousel"]):
        rc = main()
    captured = capsys.readouterr()
    assert rc != 0
    # argparse default help mentions the program
    assert "generate" in captured.out or "generate" in captured.err
